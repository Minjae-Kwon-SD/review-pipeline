"""스크립트들이 같이 쓰는 입출력 도우미. 단독으로 실행하지 않는다."""
import csv
import json
import re
import sys
import unicodedata
from datetime import datetime
from pathlib import Path

# Windows에서 출력이 파이프로 넘어가면 cp949가 되어 한글이 깨지므로 UTF-8로 고정한다.
for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass

ROOT = Path(__file__).resolve().parent.parent

REVIEW_COLS = ["review_id", "asin", "star", "date", "title", "body", "verified", "vine"]
DIST_COLS = ["asin", "s5", "s4", "s3", "s2", "s1", "total_ratings"]
ASIN_COLS = ["asin", "title", "brand", "price_usd", "price_band", "amazon_rating", "status", "reason"]
# v1에서 더한 칸. 필수 칸 뒤에 오는 선택 칸이라 손으로 만든 v0 파일(8칸, 7칸, 8칸)도 그대로 읽힌다.
REVIEW_OPT = ["helpful_votes", "variant_asin", "variant_text", "brand", "language", "country"]
DIST_OPT = ["average_rating", "source", "captured_at"]
ASIN_OPT = ["parent_asin"]
OPTIONAL_COLS = {tuple(REVIEW_COLS): REVIEW_OPT, tuple(DIST_COLS): DIST_OPT, tuple(ASIN_COLS): ASIN_OPT}
STARS = (1, 2, 3, 4, 5)
SENTIMENTS = ("positive", "negative", "mixed", "neutral")
SIDE_KO = {"P": "제품", "B": "브랜드"}


def die(msg):
    print(f"[중단] {msg}", file=sys.stderr)
    sys.exit(2)


def now_iso():
    return datetime.now().astimezone().isoformat(timespec="seconds")


def resolve_run(arg=None):
    """회차 이름이나 경로를 받아 회차 폴더를 돌려준다. 없으면 runs/CURRENT를 읽는다."""
    if not arg:
        current = ROOT / "runs" / "CURRENT"
        if not current.exists():
            die("회차를 주지 않았고 runs/CURRENT도 없습니다.")
        arg = current.read_text(encoding="utf-8").strip()
    p = Path(arg)
    if not p.is_absolute() and not p.exists():
        p = ROOT / "runs" / arg
    if not p.is_dir():
        die(f"회차 폴더가 없습니다: {p}")
    return p


def read_csv(path, cols, errors):
    """머리줄이 cols로 시작하는 CSV를 dict 목록으로 읽는다. 문제는 errors에 적고 None을 돌려준다.

    cols 뒤에는 그 파일의 선택 칸(OPTIONAL_COLS)만 올 수 있다. 없는 선택 칸은 빈 문자열로 채운다.
    """
    if not path.exists():
        errors.append(f"{path.name}이(가) 없습니다.")
        return None
    try:
        with open(path, encoding="utf-8-sig", newline="") as f:
            reader = csv.reader(f)
            header = [h.strip() for h in next(reader, [])]
            raw = [(reader.line_num, r) for r in reader if any(c.strip() for c in r)]
    except UnicodeDecodeError:
        errors.append(f"{path.name}이(가) UTF-8이 아닙니다. Excel이면 'CSV UTF-8'로 다시 저장해 주세요.")
        return None
    optional = OPTIONAL_COLS.get(tuple(cols), [])
    extra = header[len(cols):]
    if header[:len(cols)] != cols or len(set(extra)) != len(extra) or any(c not in optional for c in extra):
        opt = f" (뒤에 선택 칸 {','.join(optional)} 가능)" if optional else ""
        errors.append(f"{path.name} 머리줄이 다릅니다. 기대: {','.join(cols)}{opt} / 실제: {','.join(header)}")
        return None
    rows, ok = [], True
    for line_no, r in raw:
        if len(r) != len(header):
            errors.append(f"{path.name} {line_no}번째 줄의 칸 수가 {len(r)}개입니다({len(header)}개여야 함). "
                          "본문에 쉼표나 따옴표가 있으면 칸 전체를 큰따옴표로 감싸고, 안의 큰따옴표는 두 번 씁니다.")
            ok = False
            continue
        row = {k: "" for k in optional}
        row.update({k: (v if k in ("title", "body") else v.strip()) for k, v in zip(header, r)})
        rows.append(row)
    return rows if ok else None


def load_csv_or_die(path, cols):
    errors = []
    rows = read_csv(path, cols, errors)
    if rows is None:
        die(" ".join(errors) + " 먼저 check_inputs.py를 돌려 주세요.")
    return rows


def load_yaml(path):
    try:
        import yaml
    except ImportError:
        die("PyYAML이 필요합니다. 한 번만 설치해 주세요: python -m pip install pyyaml")
    if not path.exists():
        die(f"{path.name}이(가) 없습니다.")
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f)


def load_config():
    """config/pipeline.yaml. 묶음은 {이름: [별점...]}."""
    conf = load_yaml(ROOT / "config" / "pipeline.yaml") or {}
    w = conf.get("weighting") or {}
    groups = {str(k): [int(s) for s in v] for k, v in (w.get("groups") or {}).items()}
    if sorted(s for v in groups.values() for s in v) != list(STARS):
        die("config/pipeline.yaml의 weighting.groups가 1~5★를 한 번씩 덮어야 합니다.")
    conf["weighting"] = {"groups": groups, "min_group_sample": int(w.get("min_group_sample", 30)),
                         "max_review_share": float(w.get("max_review_share", 0.02)),
                         "dist_mean_tolerance": float(w.get("dist_mean_tolerance", 0.15))}
    conf["paid"] = conf.get("paid") or {}
    return conf


def real_shares(dist_row):
    """02_star_distribution.csv 한 줄의 s1~s5 퍼센트를 합 1로 맞춘 비율로."""
    vals = {s: float(dist_row[f"s{s}"]) for s in STARS}
    total = sum(vals.values())
    return {s: vals[s] / total for s in STARS} if total else {s: 0.0 for s in STARS}


def star_groups(counts, real, groups):
    """ASIN 하나의 별점 묶음 현황. counts[s] = 표본 수, real[s] = 합 1인 실제 비율.

    mode: per_star(묶음 안 별점이 모두 표본을 가짐), group(일부만 가짐), empty(표본 없음).
    """
    out = {}
    for g, stars in groups.items():
        sample = sum(counts.get(s, 0) for s in stars)
        mode = "empty" if sample == 0 else ("per_star" if all(counts.get(s, 0) for s in stars) else "group")
        out[g] = {"stars": list(stars), "sample": sample, "real": sum(real[s] for s in stars), "mode": mode}
    return out


def load_schema(run, name="03_schema_approved.yaml"):
    """스키마(기본은 승인본)를 읽어 {topic id: 주제 정보}로 돌려준다."""
    data = load_yaml(run / name)
    topics = (data or {}).get("topics") or []
    if not topics:
        die(f"{name}에 topics가 없습니다.")
    out = {}
    for t in topics:
        tid = str(t.get("id", "")).strip()
        if not tid:
            die(f"{name}에 id가 없는 주제가 있습니다.")
        if tid in out:
            die(f"{name}에 같은 id가 두 번 있습니다: {tid}")
        side = str(t.get("side", "")).strip()
        if side not in SIDE_KO:
            die(f"{name}의 주제 {tid}: side는 P(제품) 또는 B(브랜드)여야 합니다.")
        out[tid] = {**t, "id": tid, "name_ko": str(t.get("name_ko") or tid), "side": side,
                    "examples": t.get("examples") or []}
    return out


def read_jsonl(path, errors=None):
    """JSON 한 줄에 하나씩 읽는다. 빈 줄은 건너뛴다."""
    out = []
    with open(path, encoding="utf-8-sig") as f:
        for i, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            try:
                out.append(json.loads(line))
            except json.JSONDecodeError as e:
                msg = f"{path.name} {i}번째 줄이 JSON이 아닙니다: {e.msg}"
                if errors is None:
                    die(msg)
                errors.append(msg)
    return out


def write_json(path, data):
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def write_jsonl(path, rows):
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")


_QUOTE_MAP = str.maketrans({"‘": "'", "’": "'", "“": '"', "”": '"', " ": " "})


def norm_text(s):
    """인용 대조용 정규화: 유니코드 NFC, 따옴표 모양 통일, 공백 묶기. 글자 자체는 바꾸지 않는다."""
    s = unicodedata.normalize("NFC", s or "").translate(_QUOTE_MAP)
    return re.sub(r"\s+", " ", s).strip()


def pct(num, den, digits=1):
    return round(100.0 * num / den, digits) if den else 0.0


def fmt_pct(x):
    return f"{x:.1f}%"


def fmt_star(x):
    return f"{x:.2f}★"


OFF_CATEGORY = "off_category"   # review-tagger가 카테고리 밖 리뷰에 다는 표시(주제가 아님)


def split_tags(reviews, tags, schema=None):
    """집계 전에 태그를 거른다(weight.py와 같은 규칙).
    off_category가 붙은 리뷰는 리뷰와 태그 모두에서 빼고, 승인 스키마에 없는 주제의 태그도 뺀다.
    돌려주는 것: (리뷰, 태그, {"off_category_reviews": [...], "unknown_topic_tags": n})"""
    off = {t["review_id"] for t in tags if t.get("topic") == OFF_CATEGORY}
    reviews = [r for r in reviews if r["review_id"] not in off]
    kept = [t for t in tags if t["review_id"] not in off]
    unknown = 0
    if schema is not None:
        unknown = sum(1 for t in kept if t.get("topic") not in schema)
        kept = [t for t in kept if t.get("topic") in schema]
    return reviews, kept, {"off_category_reviews": sorted(off), "unknown_topic_tags": unknown}


def category_conf(run):
    """회차 이름의 첫 부분(perfume-db-... -> perfume)으로 config/categories/<카테고리>.yaml을 읽는다. 없으면 빈 dict."""
    cat = Path(run).name.split("-")[0]
    p = ROOT / "config" / "categories" / f"{cat}.yaml"
    return (load_yaml(p) or {}) if p.exists() else {}
