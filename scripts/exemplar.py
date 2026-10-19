"""형식 견본 만들기(2026-10-17 담당자 결정): 완성도 높은 회차의 리포트와 가이드에서 내용을 자리표로 바꿔
작성자가 형식과 문체만 따르게 한다. 작성자는 이 견본만 읽고, 원본 회차 폴더는 Hook(guard_runs.py)으로 막는다.

python scripts/exemplar.py build <원본 회차>   → config/exemplars/<원본 품목>/report_exemplar.md, guide_exemplar.md, exemplar_check.json
  - 시험 회차에는 그 회차와 다른 품목의 견본을 준다(같은 품목 견본은 남긴 예시 줄로 결론이 샐 수 있음).
  - 바꾸는 것: 리뷰 인용 → {인용}, 따옴표 안 글 → {인용}, [m:키] → [m:{키}], [r:id] → [r:{출처}], 리뷰 id → {id}, ASIN → {ASIN},
    주제, 세부 이슈 라벨, 증상, 방향 이름 → {주제} {라벨} {방향}, 브랜드 → {브랜드}, 그 밖의 영문 낱말 묶음(상품, 표준 이름) → {영문},
    숫자 → {수}. 표 블록은 {{표: 이름}} 한 줄.
  - 남기는 것: 제목(장 번호 그대로), 소제목 순서, 목록 모양, 문장 틀. 절마다 내용 줄은 앞의 두 줄만 남기고 나머지는 "(같은 꼴 n줄)".
  - 스스로 검사: 제목 밖 줄에 숫자, 리뷰 id, 브랜드, 주제와 라벨 이름이 남으면 FAIL(종료 코드 1, 견본을 쓰지 않음).
"""
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from pipeline_io import ASIN_COLS, die, load_csv_or_die, load_yaml, now_iso, write_json  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "config" / "exemplars"
KEEP_PER_SECTION = 2
TITLE_FIX = {"영향 분석: 별점을 가장 많이 깎는 불만": "영향 분석: 낮은 별점과 함께 나오는 불만"}   # 틀 제목이 바뀐 것(2026-10-17)
WHITELIST = {"TL;DR", "P1", "P2", "HTML", "ASIN", "SKU"}
LATIN = re.compile(r"(?<![{\w\[])[A-Za-z][A-Za-z0-9&'’.+/-]*(?:[ \t]+[A-Za-z0-9][A-Za-z0-9&'’.+/-]*)*")
NUM = re.compile(r"(?<![{\w])[+-]?\d[\d,]*(?:\.\d+)?")


def names(run):
    """(주제와 라벨 이름 목록(긴 것부터), 브랜드 목록)"""
    topic, label = set(), set()
    s = load_yaml(run / "03_schema_approved.yaml") or {}
    for t in s.get("topics", []):
        topic.add(t.get("name_ko"))
    a = load_yaml(run / "07a_issues_approved.yaml") or {}
    for t in a.get("topics", []):
        topic.add(t.get("name_ko"))
        for d in (t.get("directions") or {}).values():
            for l in d.get("labels", []):
                label.add(l.get("name_ko"))
    cat = run.name.split("-")[0]
    conf = load_yaml(ROOT / "config" / "categories" / f"{cat}.yaml") or {}
    di = (conf.get("guide") or {}).get("direction_index") or {}
    direction = {(di.get(k) or {}).get("name") for k in ("high", "low")}
    brands = {r["brand"] for r in load_csv_or_die(run / "01_asins.csv", ASIN_COLS) if r.get("brand")}
    clean = lambda xs: sorted({x for x in xs if x and len(x) > 1}, key=len, reverse=True)
    return clean(topic), clean(label), clean(direction), clean(brands)


def mask_line(line, N, heading=False):
    topic, label, direction, brands = N
    s = line
    if not heading:
        if s.lstrip().startswith(">"):
            return re.sub(r">.*", '> "{인용}" ({브랜드}, {수}★, {id})', s, count=1)
        s = re.sub(r'"[^"\n]{1,400}"|“[^”\n]{1,400}”', '"{인용}"', s)
        s = re.sub(r"\[m:[^\]]+\]", "[m:{키}]", s)
        s = re.sub(r"\[r:[^\]]+\]", "[r:{출처}]", s)
        s = re.sub(r"\[(?:head|std|p|a|m|s)\.[^\]]+\]", "[{키}]", s)
        s = re.sub(r"\bR[0-9A-Z]{9,}\b", "{id}", s)
        s = re.sub(r"\bB0[0-9A-Z]{8}\b", "{ASIN}", s)
    for x in label:
        s = s.replace(x, "{라벨}")
    for x in topic:
        s = s.replace(x, "{주제}")
    for x in direction:
        s = s.replace(x, "{방향}")
    for b in brands:
        s = re.sub(re.escape(b), "{브랜드}", s, flags=re.I)
    s = s.replace("TL;DR", "①")
    s = LATIN.sub(lambda m: m.group(0) if m.group(0) in WHITELIST else "{영문}", s)
    s = s.replace("①", "TL;DR")
    if not heading:
        s = NUM.sub("{수}", s)
    return s


def build_one(src, N, kind):
    text = src.read_text(encoding="utf-8")
    text = re.sub(r"<!-- 표:(.+?) -->.*?<!-- /표:\1 -->", lambda m: "{{표: " + m.group(1).strip() + "}}", text, flags=re.S)
    out, kept, skipped = [], 0, 0

    def flush():
        nonlocal skipped
        if skipped:
            out.append(f"(같은 꼴 {skipped}줄)")
            skipped = 0
    for line in text.splitlines():
        if line.startswith("#"):
            flush()
            for old, new in TITLE_FIX.items():
                line = line.replace(old, new)
            out.append(mask_line(line, N, heading=True))
            kept = 0
            continue
        if not line.strip() or line.startswith("{{표:"):
            out.append(line)
            continue
        if line.lstrip().startswith("|"):          # 표 줄은 스크립트가 만든다
            continue
        if kept < KEEP_PER_SECTION:
            out.append(mask_line(line, N))
            kept += 1
        else:
            skipped += 1
    flush()
    head = (f"<!-- 형식 견본({kind}): {now_iso()}에 scripts/exemplar.py가 만듦. 내용은 자리표이고 형식과 문장 틀만 본다. "
            f"자리표 글자를 그대로 옮기지 않는다. 장 제목과 순서는 config/report_template_ko.md와 작성자 지시문이 이긴다. -->")
    return head + "\n" + "\n".join(re.sub(r"\n{3,}", "\n\n", "\n".join(out)).splitlines()) + "\n"


def check(text, N):
    topic, label, direction, brands = N
    bad = []
    for i, line in enumerate(text.splitlines(), 1):
        if line.startswith("#") or line.startswith("<!--") or line.startswith("(같은 꼴") or line.startswith("{{표:"):
            continue
        body = re.sub(r"\{[^{}]*\}", "", line)
        for w in WHITELIST:
            body = body.replace(w, "")
        if re.search(r"\d", body):
            bad.append(f"{i}줄 숫자: {line[:80]}")
        if re.search(r"\bR[0-9A-Z]{9,}\b|\bB0[0-9A-Z]{8}\b", body):
            bad.append(f"{i}줄 id: {line[:80]}")
        for x in list(brands) + list(topic) + list(label):
            if x.lower() in body.lower():
                bad.append(f"{i}줄 이름 '{x}': {line[:80]}")
                break
    return bad


def build(run_name):
    run = ROOT / "runs" / run_name
    if not run.is_dir():
        die(f"회차 폴더가 없습니다: {run}")
    N = names(run)
    out = OUT / run_name.split("-")[0]
    out.mkdir(parents=True, exist_ok=True)
    res = {"made_at": now_iso(), "source_run": run_name, "files": {}}
    ok = True
    for kind, src, dst in (("report", run / "06_report.md", out / "report_exemplar.md"), ("guide", run / "17_guide.md", out / "guide_exemplar.md")):
        if not src.exists():
            die(f"원본 문서가 없습니다: {src}")
        text = build_one(src, N, kind)
        bad = check(text, N)
        res["files"][dst.name] = {"lines": len(text.splitlines()), "leaks": bad[:50], "status": "FAIL" if bad else "PASS"}
        if bad:
            ok = False
        dst.write_text(text, encoding="utf-8", newline="\n")
        print(f"{dst.name}: {'FAIL' if bad else 'PASS'}  ({len(text.splitlines())}줄, 남은 내용 {len(bad)}개)")
        for b in bad[:10]:
            print(f"  {b}")
    res["status"] = "PASS" if ok else "FAIL"
    write_json(out / "exemplar_check.json", res)
    return 0 if ok else 1


if __name__ == "__main__":
    if len(sys.argv) != 3 or sys.argv[1] != "build":
        die("사용법: python scripts/exemplar.py build <원본 회차>")
    sys.exit(build(sys.argv[2]))
