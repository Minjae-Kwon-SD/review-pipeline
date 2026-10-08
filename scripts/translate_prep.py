"""리포트 번역 준비와 검사. 모델을 부르지 않는다.

사용:
  python scripts/translate_prep.py prep [회차] [--src 06_report.md]
    표 블록을 뺀 번역 원문(06_report_for_translation.md)과, 리포트가 인용한 리뷰마다 태그 인용 원문 목록
    (06_report_quote_sources.json)을 쓴다.
  python scripts/translate_prep.py check [회차] [--lang en]
    번역본(06_report_<lang>.md) 검사: 줄 수가 원문과 같은지, 줄마다 숫자 표기(숫자, %, ★)와 리뷰 id가 같은지
    (기간 이름은 i18n_names_<lang>.yaml의 periods로 바꿔 견주고, 순위 N위는 서수 낱말이나 숫자 서수로 있는지 따로 봄),
    인용 따옴표 안이 그 리뷰 원문에 글자 그대로 있는지, 한글이 남지 않았는지(인용 안 제외), 가운뎃점이 없는지.
    짝 파일(06_report_<lang>_pairs.jsonl: 줄 번호, 한국어, 번역)을 쓴다(뜻 감사용). 결과: 06_report_<lang>_check.json
"""
import argparse
import json

import yaml
import re
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from pipeline_io import REVIEW_COLS, load_csv_or_die, norm_text, now_iso, read_jsonl, resolve_run, write_json, write_jsonl  # noqa: E402

for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass

QUOTE = re.compile(r'"(.+?)"\s*\(([^()]+?),\s*([1-5])★,\s*(R[0-9A-Z]+)\)')
RID = re.compile(r"\bR[0-9A-Z]{9,}\b")


def strip_tables(text):
    return re.sub(r"<!-- 표:(.+?) -->.*?<!-- /표:\1 -->\n?", "", text, flags=re.S)


def prep(run, src):
    text = strip_tables((run / src).read_text(encoding="utf-8"))
    (run / "06_report_for_translation.md").write_text(text, encoding="utf-8")
    tags = read_jsonl(run / "04_tags.jsonl")
    by = defaultdict(list)
    for t in tags:
        by[t["review_id"]].append({"topic": t["topic"], "sentiment": t["sentiment"], "quote": t["quote"]})
    cited = sorted({m.group(4) for m in QUOTE.finditer(text)})
    write_json(run / "06_report_quote_sources.json", {r: by.get(r, []) for r in cited})
    print(f"번역 원문 {len(text.splitlines())}줄(표 블록 뺌), 인용 리뷰 {len(cited)}개 → 06_report_for_translation.md, 06_report_quote_sources.json")
    return 0


def numbers(s):
    s = QUOTE.sub(lambda m: f"({m.group(3)}★, {m.group(4)})", s)          # 인용 따옴표 안의 숫자는 원문 언어마다 달라 뺀다
    return sorted(re.findall(r"-?\d(?:\d|,(?=\d))*(?:\.\d+)?%?★?", s))      # 숫자 뒤 문장 쉼표는 숫자에 넣지 않는다


RANK = re.compile(r"(\d+)위")
ORDINAL_EN = ["first", "second", "third", "fourth", "fifth", "sixth", "seventh", "eighth", "ninth", "tenth"]


def localize_src(a, periods):
    """원문 줄을 번역과 견줄 꼴로: 기간 이름은 이름표의 번역으로 바꾸고, 순위(N위)는 숫자 목록에서 빼서 따로 본다."""
    for k in sorted(periods, key=len, reverse=True):
        a = a.replace(k, periods[k])
    ranks = [int(x) for x in RANK.findall(a)]
    return RANK.sub("위", a), ranks


def rank_ok(n, b):
    """순위 N이 번역 줄에 서수 낱말(first...)이나 숫자 서수(1st, No. 1, #1)로 있는가"""
    word = ORDINAL_EN[n - 1] if 0 < n <= len(ORDINAL_EN) else None
    return bool((word and re.search(rf"\b{word}\b", b, re.I)) or re.search(rf"(\b{n}(st|nd|rd|th)\b|No\. ?{n}\b|#{n}\b)", b))


def check(run, lang):
    src = (run / "06_report_for_translation.md").read_text(encoding="utf-8").splitlines()
    names = run / f"i18n_names_{lang}.yaml"
    periods = (yaml.safe_load(names.read_text(encoding="utf-8")) or {}).get("periods", {}) if names.exists() else {}
    out = (run / f"06_report_{lang}.md").read_text(encoding="utf-8").splitlines()
    reviews = {r["review_id"]: r for r in load_csv_or_die(run / "02_reviews.csv", REVIEW_COLS)}
    errors, pairs = [], []
    if len(src) != len(out):
        errors.append(f"줄 수가 다름: 원문 {len(src)}, 번역 {len(out)}")
    for i, (a, b) in enumerate(zip(src, out), 1):
        if not a.strip() and not b.strip():
            continue
        if bool(a.strip()) != bool(b.strip()):
            errors.append(f"{i}번째 줄: 한쪽만 빈 줄")
            continue
        la, ranks = localize_src(a, periods)
        na, nb = numbers(la), numbers(b)
        for n in ranks:
            if not rank_ok(n, b):
                errors.append(f"{i}번째 줄 순위 {n}위가 번역에 없음")
            elif str(n) in nb and nb.count(str(n)) > na.count(str(n)):
                nb.remove(str(n))                                          # 숫자 서수(No. 1)로 쓴 순위
        if na != nb:
            errors.append(f"{i}번째 줄 숫자 표기가 다름: 원문 {na[:8]}, 번역 {nb[:8]}")
        if sorted(RID.findall(a)) != sorted(RID.findall(b)):
            errors.append(f"{i}번째 줄 리뷰 id가 다름")
        for q in QUOTE.finditer(b):
            r = reviews.get(q.group(4))
            if r is None or (norm_text(q.group(1)) not in norm_text(r["title"]) and norm_text(q.group(1)) not in norm_text(r["body"])):
                errors.append(f"{i}번째 줄 인용이 {q.group(4)} 원문에 없음: \"{q.group(1)[:60]}\"")
        outside = QUOTE.sub("", b)
        if re.search(r"[가-힣]", outside):
            errors.append(f"{i}번째 줄에 한글이 남음: {outside[:60]}")
        if "·" in b:
            errors.append(f"{i}번째 줄에 가운뎃점")
        pairs.append({"line": i, "ko": a, lang: b})
    write_jsonl(run / f"06_report_{lang}_pairs.jsonl", pairs)
    status = "FAIL" if errors else "PASS"
    write_json(run / f"06_report_{lang}_check.json", {"checked_at": now_iso(), "status": status, "lines": len(src), "pairs": len(pairs),
                                                      "errors": errors[:100]})
    print(f"번역 검사: {status}  (줄 {len(src)}개, 짝 {len(pairs)}개, 오류 {len(errors)}개)")
    for e in errors[:30]:
        print(f"  오류: {e}")
    return 1 if errors else 0


def main():
    ap = argparse.ArgumentParser(description="리포트 번역 준비와 검사")
    ap.add_argument("mode", choices=["prep", "check"])
    ap.add_argument("run", nargs="?")
    ap.add_argument("--src", default="06_report.md")
    ap.add_argument("--lang", default="en")
    a = ap.parse_args()
    run = resolve_run(a.run)
    sys.exit(prep(run, a.src) if a.mode == "prep" else check(run, a.lang))


if __name__ == "__main__":
    main()
