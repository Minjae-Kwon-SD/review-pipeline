"""베낌 재기(2026-10-17 담당자 결정): 시험 회차의 리포트와 가이드가 다른 회차(원본) 문서의 문장을 얼마나 그대로 가져왔는지 센다.

python scripts/copy_check.py <회차> --source <원본 회차> [--n 8] [--warn 5.0] [--out 파일]  → runs/<회차>/19_copy_check.json
  - 문서마다 낱말 n개(기본 8)씩 이어 붙인 조각 가운데 원본 문서에도 있는 조각의 비율(%)과 가장 긴 같은 구간 10개.
  - 빼는 것: 표 블록과 표 줄, 제목 줄, 인용 줄(>), 그리고 이 회차 스크립트 출력(05_metrics.json, 05_tables.md, 16_guide_metrics.json의
    글자 값)에 있는 조각. 스크립트가 만든 문장을 작성자가 글자 그대로 옮기는 것은 규칙이라 베낌으로 세지 않는다.
  - 숫자는 '#'로 바꿔 센다(같은 데이터면 숫자가 같아 숫자만으로 겹치는 것을 줄임).
  - 비율이 --warn(기본 5%)을 넘으면 WARN. 판정이 아니라 기록이다(원본을 본 rt7, rt2와 다른 품목끼리의 값을 기준선으로 함께 적음).
"""
import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from pipeline_io import die, now_iso, write_json  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
DOCS = (("report", "06_report.md", ("05_metrics.json", "05_tables.md")), ("guide", "17_guide.md", ("16_guide_metrics.json",)))


def tokens(text):
    text = re.sub(r"<!-- 표:(.+?) -->.*?<!-- /표:\1 -->", " ", text, flags=re.S)
    keep = []
    for line in text.splitlines():
        t = line.strip()
        if not t or t.startswith(("#", "|", ">", "<!--", "{{표")):
            continue
        keep.append(t)
    s = " ".join(keep)
    s = re.sub(r"\[(?:m|r):[^\]]*\]", " ", s)
    s = re.sub(r"\bR[0-9A-Z]{9,}\b|\bB0[0-9A-Z]{8}\b", "ID", s)
    s = re.sub(r"[+-]?\d[\d,]*(?:\.\d+)?", "#", s)
    s = re.sub(r"[*_`\"“”()\[\],.:;!?~·]", " ", s)
    return s.split()


def shingles(toks, n):
    return {tuple(toks[i:i + n]) for i in range(len(toks) - n + 1)}


def strings(obj, out):
    if isinstance(obj, str):
        out.append(obj)
    elif isinstance(obj, dict):
        for v in obj.values():
            strings(v, out)
    elif isinstance(obj, list):
        for v in obj:
            strings(v, out)


def script_shingles(run, files, n):
    texts = []
    for f in files:
        p = run / f
        if not p.exists():
            continue
        if p.suffix == ".json":
            strings(json.loads(p.read_text(encoding="utf-8")), texts)
        else:
            texts.append(p.read_text(encoding="utf-8").replace("|", " "))
    return shingles(tokens("\n".join(texts)), n)


def longest_spans(toks, src_sh, n, top=10):
    spans, i = [], 0
    while i <= len(toks) - n:
        if tuple(toks[i:i + n]) in src_sh:
            j = i
            while j <= len(toks) - n and tuple(toks[j:j + n]) in src_sh:
                j += 1
            spans.append(" ".join(toks[i:j + n - 1]))
            i = j + n - 1
        else:
            i += 1
    return sorted(spans, key=lambda s: -len(s.split()))[:top]


def check(run_name, source_name, n=8, warn=5.0, out=None):
    run, src = ROOT / "runs" / run_name, ROOT / "runs" / source_name
    for d in (run, src):
        if not d.is_dir():
            die(f"회차 폴더가 없습니다: {d}")
    res = {"checked_at": now_iso(), "run": run_name, "source": source_name, "n": n, "warn_pct": warn, "docs": {}}
    worst = 0.0
    for kind, fname, script_files in DOCS:
        a, b = run / fname, src / fname
        if not (a.exists() and b.exists()):
            continue
        ta, tb = tokens(a.read_text(encoding="utf-8")), tokens(b.read_text(encoding="utf-8"))
        own = script_shingles(run, script_files, n)
        sa = shingles(ta, n) - own
        sb = shingles(tb, n)
        both = sa & sb
        pct = round(100.0 * len(both) / len(sa), 1) if sa else 0.0
        worst = max(worst, pct)
        res["docs"][kind] = {"shingles": len(sa), "copied": len(both), "copied_pct": pct,
                             "longest": longest_spans(ta, both, n)}
        print(f"{kind}: 원본과 같은 {n}낱말 조각 {pct}% ({len(both)}/{len(sa)}, 스크립트 문장 뺌)")
    res["status"] = "WARN" if worst > warn else "OK"
    dst = Path(out) if out else run / "19_copy_check.json"   # 기준선을 잴 때는 --out(원본 회차 폴더에 쓰지 않음)
    write_json(dst, res)
    print(f"베낌 재기: {res['status']} (기준 {warn}%) → {dst}")
    return res


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("run")
    ap.add_argument("--source", required=True)
    ap.add_argument("--n", type=int, default=8)
    ap.add_argument("--warn", type=float, default=5.0)
    ap.add_argument("--out", help="결과 파일 경로(기본 runs/<회차>/19_copy_check.json)")
    a = ap.parse_args()
    check(a.run, a.source, a.n, a.warn, a.out)
