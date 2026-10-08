"""개발 가이드 문장(17_guide.md) 기계 검사. 모델을 부르지 않는다.

사용: python scripts/guide_check.py [회차]
  1. 문장 속 숫자: [m:키]마다 그 키가 16_guide_metrics.json에 있고, 표시 바로 앞(같은 줄)에 그 키의 표기(text)가 그대로 있는지.
  2. [m:키] 없이 쓴 숫자: 숫자가 든 줄인데 [m:키]가 하나도 없으면 경고(연도, 장 번호, 순서 번호, 표준 번호는 셈하지 않음).
  3. 출처: [r:id]마다 15_research_check.json에서 verified인지.
  4. 인용: > "번역" (브랜드, 별점★, review_id)마다 리뷰가 있고, 별점과 브랜드가 맞고, metrics의 인용 후보(quotes)에 있는 리뷰인지.
  5. 장 제목 줄(## 머리 숫자, ## 01 ~ ## 05, ## A)과 소비자 기준표 기준마다 네 칸(벌주는 선, 만족 기준, 개발 기준, 상세페이지 문구).
  6. 가운뎃점 0.
결과: 18_guide_quote_check.json. 오류가 있으면 종료 코드 1.
"""
import argparse
import csv
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from pipeline_io import REVIEW_COLS, load_csv_or_die, now_iso, resolve_run, write_json  # noqa: E402

for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass

MARK = re.compile(r"\[m:([^\]]+)\]")
RMARK = re.compile(r"\[r:([^\]\s]+)\]")
QUOTE = re.compile(r'"(.+?)"\s*\(([^()]+?),\s*([1-5])★,\s*(R[0-9A-Z]+)\)')
HEADS = ["## 머리 숫자", "## 01 ", "## 02 ", "## 03 ", "## 04 ", "## 05 ", "## A "]
STD_CELLS = ("벌주는 선", "만족 기준", "개발 기준", "상세페이지 문구")


def check(run):
    text = (run / "17_guide.md").read_text(encoding="utf-8")
    M = json.loads((run / "16_guide_metrics.json").read_text(encoding="utf-8"))
    rc = json.loads((run / "15_research_check.json").read_text(encoding="utf-8"))
    verified = {x["id"] for x in rc["items"] if x["status"] == "verified"}
    reviews = {r["review_id"]: r for r in load_csv_or_die(run / "02_reviews.csv", REVIEW_COLS)}
    with (run / "01_asins.csv").open(encoding="utf-8-sig") as f:
        brands = {r["asin"]: r.get("brand", "") for r in csv.DictReader(f)}
    cand = {q["review_id"] for qs in M["quotes"].values() for q in qs}
    errors, warns = [], []
    nums = refs = quotes = 0
    for ln, line in enumerate(text.splitlines(), 1):
        pos = 0
        for m in MARK.finditer(line):
            nums += 1
            key = m.group(1)
            v = M["values"].get(key)
            if v is None:
                errors.append(f"{ln}번째 줄: 없는 metrics 키 [m:{key}]")
            elif str(v["text"]) not in line[pos:m.start()]:
                errors.append(f"{ln}번째 줄: [m:{key}] 앞에 표기 '{v['text']}'가 없음")
            pos = m.end()
        for m in RMARK.finditer(line):
            refs += 1
            if m.group(1) not in verified:
                errors.append(f"{ln}번째 줄: 확인되지 않은 출처 [r:{m.group(1)}]")
        stripped = re.sub(r"\[(?:m|r):[^\]]+\]", "", line)
        stripped = re.sub(r"\b(19|20)\d{2}\b|^#+.*$|^\s*\d+\.\s|\bR[0-9A-Z]{9,}\b|[A-Z]{2,}[ -]?\d+|\d+★|B0[0-9A-Z]{8}", "", stripped)
        if re.search(r"\d", stripped) and not MARK.search(line) and not line.lstrip().startswith(">"):
            warns.append(f"{ln}번째 줄: [m:키] 없는 숫자: {line.strip()[:70]}")
        for q in QUOTE.finditer(line):
            quotes += 1
            _, brand, star, rid = q.groups()
            r = reviews.get(rid)
            if r is None:
                errors.append(f"{ln}번째 줄: 없는 리뷰 {rid}")
                continue
            if int(r["star"]) != int(star):
                errors.append(f"{ln}번째 줄: {rid} 별점 {star}★, 실제 {r['star']}★")
            if brands.get(r["asin"]) and brands[r["asin"]] != brand.strip():
                errors.append(f"{ln}번째 줄: {rid} 브랜드 '{brand}', 01_asins.csv '{brands[r['asin']]}'")
            if rid not in cand:
                errors.append(f"{ln}번째 줄: {rid}는 metrics 인용 후보가 아님")
        if "·" in line:
            errors.append(f"{ln}번째 줄에 가운뎃점(·)")
    for h in HEADS:
        if not re.search(rf"^{re.escape(h)}", text, re.M):
            errors.append(f"장 제목 줄 '{h.strip()}'이 없음")
    stds = re.split(r"^#### ", text, flags=re.M)[1:]
    for s in stds:
        if not s.startswith("기준"):
            continue
        title = s.splitlines()[0]
        for c in STD_CELLS:
            if f"- {c}" not in s:
                errors.append(f"기준표 '{title}'에 '{c}' 칸이 없음")
    status = "FAIL" if errors else "PASS"
    write_json(run / "18_guide_quote_check.json", {"checked_at": now_iso(), "status": status, "numbers": nums, "research_refs": refs,
                                                    "quotes": quotes, "standards": sum(1 for s in stds if s.startswith('기준')),
                                                    "errors": errors, "warnings": warns[:80]})
    print(f"가이드 문장 기계 검사: {status}  (숫자 {nums}개, 출처 {refs}개, 인용 {quotes}개, 기준 {sum(1 for s in stds if s.startswith('기준'))}개, "
          f"경고 {len(warns)}개)")
    for e in errors[:30]:
        print(f"  오류: {e}")
    return 1 if errors else 0


def main():
    ap = argparse.ArgumentParser(description="개발 가이드 문장 기계 검사")
    ap.add_argument("run", nargs="?")
    args = ap.parse_args()
    sys.exit(check(resolve_run(args.run)))


if __name__ == "__main__":
    main()
