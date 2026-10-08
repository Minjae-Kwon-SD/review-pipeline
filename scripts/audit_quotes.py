"""태그와 리포트의 기계 검사.

사용:
  python scripts/audit_quotes.py tags [회차] [--model sonnet|top] [--batches id1,id2]
    04_batches.json의 묶음마다 태그 파일(04_tags_{model}_{batch_id}.jsonl)을 검사한다.
    sonnet: sonnet 묶음(ASIN 묶음과 gold 묶음)을 모두 검사하고, 모두 통과하면 ASIN 묶음만 04_tags.jsonl(리포트가 쓰는 태그)로
      합친다(gold 묶음은 merge false라 합치지 않음).
    top: gold 묶음(04_tags_top_gold.jsonl)만 검사한다(정답 세트 비교용, 합치지 않음).
    --batches를 주면 그 묶음만 검사하고 합치지 않는다(시험 태깅용).
    검사: 칸, 승인 스키마 안의 주제, 감성 네 값, 같은 리뷰 같은 주제 중복, 그 묶음에 없는 리뷰,
          인용이 그 리뷰의 제목이나 본문에 그대로 있는지(공백과 따옴표 모양만 허용).
    결과: 04_quote_check_{model}.json(failed_batches 포함). 실패한 묶음이 있으면 합치지 않고 종료 코드 1.

  python scripts/audit_quotes.py negation [회차] [--tags-file 04_tags.jsonl]
    인용 바로 앞 세 단어 안에 부정어(not, no longer, didn't 등)가 있는 태그를 센다(경고만, 04_negation_check.json).
    tags 검사도 같은 경고를 묶음마다 warnings에 넣는다. off_category(카테고리 밖 리뷰 표시)는 그 리뷰의 유일한 태그여야 한다.

  python scripts/audit_quotes.py report [회차]
    06_report.md 검사: 05_tables.md의 표가 글자 그대로 들어갔는지, 인용 뒤 (브랜드, 별점★, review_id)가
    실제 리뷰와 맞는지, 모르는 review_id가 없는지, 12개 장과 부록이 있는지.
    07b_issue_counts.json이 있으면: 표 밖 문장의 "<라벨 이름> 리뷰 n개"가 07b 개수와 같은지(8장은 전체, 10장은 그 브랜드
    ASIN의 by_asin 합), "이상 반응 n개, 나머지 m개"가 07c_safety_summary.json과, "함께 붙은 리뷰 n개"가 overlap과 같은지,
    반품이나 환불 불가 라벨이 있으면 12장에 "샘플"이 있는지, "안전 부정 리뷰 n개:" 문장이 07c negative_text와 같은지.
    리포트 어디든 가운뎃점(·)이 있으면 FAIL.
    결과: 07_quote_check.json. 오류가 있으면 종료 코드 1.
"""
import argparse
import json
import re
import sys
from collections import Counter, defaultdict

from pipeline_io import (ASIN_COLS, REVIEW_COLS, SENTIMENTS, die, load_csv_or_die, load_schema, load_yaml,
                         norm_text, now_iso, read_jsonl, resolve_run, write_json, write_jsonl)

TAG_KEYS = ("review_id", "topic", "sentiment", "quote")
OFF_CATEGORY = "off_category"   # 카테고리 밖 리뷰 표시. 그 리뷰의 유일한 태그여야 하고 감성은 neutral
OVERALL = "overall"             # 전체 만족도. 승인 스키마에 있으면 off_category가 아닌 리뷰마다 하나(overall_required: false면 검사 안 함)
NEGATIONS = {"not", "no", "never", "nothing", "nor", "without", "cannot", "hardly", "barely", "longer"}   # longer는 no longer
WORD = re.compile(r"[a-z’']+")


def negation_before(quote, r, k=3):
    """원문에서 인용 바로 앞 k단어 안(같은 문장)의 부정어(not, no longer, didn't 등). 찾으면 그 낱말, 없거나 인용을 못 찾으면 None."""
    q = norm_text(quote).lower()
    for field in ("title", "body"):
        text = norm_text(r[field]).lower()
        i = text.find(q)
        if i < 0:
            continue
        head = re.split(r"[.!?;:]", text[:i])[-1]          # 같은 문장 안에서만 본다
        before = WORD.findall(head)[-k:]
        for w in reversed(before):
            if w in NEGATIONS or w.endswith("n't") or w.endswith("n’t"):
                return w
        return None
    return None


def negation_check(run, tags_file):
    """태그 인용마다 바로 앞 세 단어 안에 부정어가 있는지(인용이 부정어를 잘라 감성이 반대로 읽힐 수 있음). 경고만, 합치지 않음."""
    by_id = {r["review_id"]: r for r in load_csv_or_die(run / "02_reviews.csv", REVIEW_COLS)}
    hits = []
    for t in read_jsonl(run / tags_file):
        r = by_id.get(t["review_id"])
        w = negation_before(t["quote"], r) if r else None
        if w:
            hits.append({"review_id": t["review_id"], "topic": t["topic"], "sentiment": t["sentiment"], "quote": t["quote"],
                         "negation": w})
    write_json(run / "04_negation_check.json", {"checked_at": now_iso(), "tags_file": tags_file, "warnings": len(hits),
                                                "by_sentiment": dict(Counter(h["sentiment"] for h in hits)), "items": hits})
    print(f"부정어 경고: {len(hits)}개({tags_file}, 인용 바로 앞 세 단어 안에 부정어) → 04_negation_check.json")
    return 0


def load_batches(run, model):
    path = run / "04_batches.json"
    if not path.exists():
        die("04_batches.json이 없습니다. tag_batches.py plan을 먼저 돌려 주세요.")
    return [b for b in json.loads(path.read_text(encoding="utf-8"))["batches"] if model in b.get("models", [])]


def check_file(path, batch_ids, by_id, schema):
    """태그 파일 하나를 검사한다. (태그 목록, 오류, 주의, 그대로 맞은 인용 수, 정규화로 맞은 인용 수, 태깅된 리뷰)"""
    issues, warns, exact, normalized = [], [], 0, 0
    tags = read_jsonl(path, issues)
    seen, ok = set(), []
    for n, t in enumerate(tags, 1):
        where = f"{n}번째 태그"
        missing = [k for k in TAG_KEYS if not str(t.get(k) or "").strip()]
        if missing:
            issues.append(f"{where}: 빈 칸 {', '.join(missing)}")
            continue
        extra = sorted(set(t) - set(TAG_KEYS))
        if extra:
            warns.append(f"{where}: 쓰지 않는 칸 {', '.join(extra)}")
        rid, topic, sent, quote = (t[k] for k in TAG_KEYS)
        r = by_id.get(rid)
        if r is None:
            issues.append(f"{where}: 없는 review_id {rid}")
            continue
        if rid not in batch_ids:
            issues.append(f"{where}: {rid}는 이 묶음의 리뷰가 아닙니다.")
        if topic == OFF_CATEGORY:
            if sent != "neutral":
                issues.append(f"{where}: {rid} off_category의 감성은 neutral이어야 합니다.")
        elif topic not in schema:
            issues.append(f"{where}: 승인 스키마에 없는 주제 {topic}")
        if sent not in SENTIMENTS:
            issues.append(f"{where}: 감성 값 {sent}(positive, negative, mixed, neutral 중 하나여야 함)")
        if (rid, topic) in seen:
            issues.append(f"{where}: {rid}에 {topic} 태그가 두 번 있습니다.")
        seen.add((rid, topic))
        if quote in r["body"] or quote in r["title"]:
            exact += 1
        elif norm_text(quote) in norm_text(r["body"]) or norm_text(quote) in norm_text(r["title"]):
            normalized += 1
        else:
            issues.append(f"{where}: {rid} 인용이 원문에 없습니다: \"{quote[:80]}\"")
        w = negation_before(quote, r)
        if w:
            warns.append(f"{where}: {rid} {topic} 인용 바로 앞에 부정어 '{w}'(인용에 부정어까지 넣어야 하는지 확인)")
        ok.append({k: t[k] for k in TAG_KEYS})
    offs = {rid for rid, tp in seen if tp == OFF_CATEGORY}
    for rid in sorted(offs):
        if any(r_ == rid and tp != OFF_CATEGORY for r_, tp in seen):
            issues.append(f"{rid}: off_category 리뷰에 다른 태그가 있습니다(off_category 한 줄만).")
    return tags, ok, issues, warns, exact, normalized, {rid for rid, _ in seen}


def check_tags(run, model, only=None):
    reviews = load_csv_or_die(run / "02_reviews.csv", REVIEW_COLS)
    schema = load_schema(run)
    by_id = {r["review_id"]: r for r in reviews}
    order = {r["review_id"]: i for i, r in enumerate(reviews)}
    batches = load_batches(run, model)
    overall_required = (load_yaml(run / "03_schema_approved.yaml") or {}).get("overall_required", True) is not False
    if only:
        unknown = sorted(set(only) - {b["batch_id"] for b in batches})
        if unknown:
            die(f"04_batches.json에 {model} 묶음으로 없는 id: {', '.join(unknown)}")
        batches = [b for b in batches if b["batch_id"] in only]
    result = {"checked_at": now_iso(), "model": model, "only": only or None, "batches": {}}
    merged, failed = [], []

    for b in batches:
        bid = b["batch_id"]
        path = run / f"04_tags_{model}_{bid}.jsonl"
        if not path.exists():
            result["batches"][bid] = {"status": "FAIL", "issues": [f"{path.name}이(가) 없습니다."]}
            failed.append(bid)
            continue
        tags, ok, issues, warns, exact, normalized, tagged = check_file(path, set(b["review_ids"]), by_id, schema)
        pairs = {(t["review_id"], t["topic"]) for t in ok}
        untagged = [rid for rid in b["review_ids"] if rid not in tagged]
        if untagged:      # 리뷰를 빠뜨린 것이므로 묶음 실패
            issues.append(f"태그가 하나도 없는 리뷰 {len(untagged)}개: {', '.join(untagged[:10])}"
                          + (" 등" if len(untagged) > 10 else ""))
        if OVERALL in schema and overall_required:   # 스키마에 전체 만족도가 있으면 off_category가 아닌 리뷰마다 하나씩 있어야 함
            no_ov = [rid for rid in b["review_ids"] if rid in tagged and (rid, OVERALL) not in pairs and (rid, OFF_CATEGORY) not in pairs]
            if no_ov:
                issues.append(f"overall이 없는 리뷰 {len(no_ov)}개: {', '.join(no_ov[:10])}" + (" 등" if len(no_ov) > 10 else ""))
        if issues:
            failed.append(bid)
        if b.get("merge", True):
            merged += ok
        result["batches"][bid] = {"status": "FAIL" if issues else "PASS", "asin": b.get("asin"),
                                  "reviews": len(b["review_ids"]), "tags": len(tags), "quote_exact": exact,
                                  "quote_whitespace_or_quote_marks": normalized, "untagged_reviews": len(untagged),
                                  "issues": issues, "warnings": warns}

    result["status"] = "FAIL" if failed else "PASS"
    result["failed_batches"] = failed
    if model == "sonnet" and not only and not failed:
        merged.sort(key=lambda t: (order[t["review_id"]], t["topic"]))
        write_jsonl(run / "04_tags.jsonl", merged)
        result["merged_into"] = "04_tags.jsonl"
    write_json(run / f"04_quote_check_{model}.json", result)

    print(f"태그 검사({model}{', ' + ','.join(only) if only else ''}): {result['status']}  (묶음 {len(batches)}개)")
    for bid, a in result["batches"].items():
        print(f"  {bid}: {a['status']}  리뷰 {a.get('reviews', '-')}개, 태그 {a.get('tags', 0)}개")
        for i in a["issues"]:
            print(f"    오류: {i}")
        for w in a.get("warnings", []):
            print(f"    주의: {w}")
    if result.get("merged_into"):
        print(f"  {len(merged)}개를 04_tags.jsonl로 합쳤습니다(리포트가 쓰는 태그).")
    return 1 if failed else 0


# review_id는 v0 꼴(B0XXXXXXX1-03)과 아마존 리뷰 ID(R로 시작하는 대문자 영숫자, 숫자 포함) 둘 다 받는다
AMAZON_RID = r"R(?=[0-9A-Z]*\d)[0-9A-Z]{9,}"
QUOTE_TAIL = re.compile(r"\(([^()]+?),\s*([1-5])★,\s*([A-Za-z0-9]+-\d+|" + AMAZON_RID + r")\)")
ID_LIKE = re.compile(r"\b(?:[A-Z0-9]{10}-\d{1,3}|" + AMAZON_RID + r")\b")
CHAPTERS = [f"## {i}." for i in range(1, 13)] + ["## 부록"]   # 정답지 순서 12개 장과 부록


SAMPLE_LABEL = ("customer_service", "negative", "not_returnable")   # 12장 샘플(시향) 제공 권고의 근거 라벨


def chapter(text, n):
    m = re.search(rf"^## {n}\..*?(?=^## |\Z)", text, re.M | re.S)
    return m.group(0) if m else ""


def check_issue_counts(run, report, brands):
    """리포트 문장 속 세부 이슈 개수를 07b_issue_counts.json(과 07c_safety_summary.json)에 대조한다."""
    path = run / "07b_issue_counts.json"
    if not path.exists():
        return []
    counts = json.loads(path.read_text(encoding="utf-8"))
    text = re.sub(r"<!-- 표:(.+?) -->.*?<!-- /표: -->", "", report, flags=re.S)   # 표 블록은 따로 검사함
    labels = defaultdict(list)                       # name_ko -> [(전체 리뷰 수, by_asin)]
    for v in counts["topics"].values():
        for l in v["labels"]:
            if l["id"] != "other":
                labels[l["name_ko"]].append((l["reviews"], l["by_asin"]))
    errors = []

    def found(part):
        taken = []
        for name in sorted(labels, key=len, reverse=True):
            for m in re.finditer(re.escape(name) + r"\s*\)?\s*\"?\s*리뷰\s*([\d,]+)개", part):
                if any(a <= m.start() < b for a, b in taken):
                    continue
                taken.append(m.span())
                yield name, int(m.group(1).replace(",", ""))

    ch10 = chapter(text, 10)
    rest = text.replace(ch10, "") if ch10 else text
    for name, n in found(rest):
        if n not in {r for r, _ in labels[name]}:
            errors.append(f"세부 이슈 '{name} 리뷰 {n}개': 07b_issue_counts.json은 {sorted({r for r, _ in labels[name]})}")
    asins_of = defaultdict(set)
    for a, b in brands.items():
        asins_of[b].add(a)
    for m in re.finditer(r"^### (.+?)\s*$(.*?)(?=^### |\Z)", ch10, re.M | re.S):
        brand = m.group(1).strip()
        if brand not in asins_of:
            continue
        for name, n in found(m.group(2)):
            ok = {sum(by.get(a, 0) for a in asins_of[brand]) for _, by in labels[name]}
            if n not in ok:
                errors.append(f"10장 {brand} 세부 이슈 '{name} 리뷰 {n}개': 07b_issue_counts.json의 그 브랜드 값은 {sorted(ok)}")
    ov = counts.get("overlap")
    for m in re.finditer(r"함께 붙은 리뷰\s*([\d,]+)개", text):
        if not ov or int(m.group(1).replace(",", "")) != ov["reviews"]:
            errors.append(f"'함께 붙은 리뷰 {m.group(1)}개': overlap은 {ov and ov['reviews']}")
    sp = run / "07c_safety_summary.json"
    if sp.exists():
        s = json.loads(sp.read_text(encoding="utf-8"))
        if s.get("negative_text"):
            for m in re.finditer(r"안전 부정 리뷰 \d+개:", text):
                if not text[m.start():].startswith(s["negative_text"]):
                    errors.append(f"안전 부정 문장이 07c_safety_summary.json의 negative_text와 다릅니다: "
                                  f"{text[m.start():m.start() + 80]}")
        for m in re.finditer(r"(?:이상 반응|몸 증상)\s*(\d+)개,\s*나머지\s*(\d+)개", text):
            if (int(m.group(1)), int(m.group(2))) != (s["negative_symptom"], s["negative_no_symptom"]):
                errors.append(f"'이상 반응 {m.group(1)}개, 나머지 {m.group(2)}개': 07c_safety_summary.json은 "
                              f"{s['negative_symptom']}개, {s['negative_no_symptom']}개")
    t, d, lid = SAMPLE_LABEL
    lab = next((l for l in counts["topics"].get(f"{t}.{d}", {}).get("labels", []) if l["id"] == lid), None)
    if lab and lab["reviews"] > 0 and "샘플" not in chapter(text, 12):
        errors.append(f"12장에 샘플(시향) 제공이 없습니다(근거 라벨 {lab['name_ko']} 리뷰 {lab['reviews']}개).")
    return errors


def check_report(run):
    reviews = {r["review_id"]: r for r in load_csv_or_die(run / "02_reviews.csv", REVIEW_COLS)}
    brands = {r["asin"]: r["brand"] for r in load_csv_or_die(run / "01_asins.csv", ASIN_COLS)}
    tagged = {t["review_id"] for t in read_jsonl(run / "04_tags.jsonl")}
    report = (run / "06_report.md").read_text(encoding="utf-8")
    tables = (run / "05_tables.md").read_text(encoding="utf-8")
    errors, warns = [], []

    for m in re.finditer(r"<!-- 표:(.+?) -->.*?<!-- /표:\1 -->", tables, re.S):
        if m.group(0) not in report:
            errors.append(f"표 '{m.group(1)}'이(가) 05_tables.md와 글자 그대로 같지 않거나 빠졌습니다.")

    cited = []
    for m in QUOTE_TAIL.finditer(report):
        brand, stars, rid = m.group(1).strip(), int(m.group(2)), m.group(3)
        cited.append(rid)
        r = reviews.get(rid)
        if r is None:
            errors.append(f"인용 출처 {rid}: 없는 review_id")
            continue
        if int(r["star"]) != stars:
            errors.append(f"인용 출처 {rid}: 별점이 {stars}★로 적혔는데 실제는 {r['star']}★")
        if brands.get(r["asin"]) and brands[r["asin"]] != brand:
            errors.append(f"인용 출처 {rid}: 브랜드가 '{brand}'로 적혔는데 01_asins.csv는 '{brands[r['asin']]}'")
        if rid not in tagged:
            warns.append(f"인용 출처 {rid}: 04_tags.jsonl에 태그가 없는 리뷰입니다.")
    for rid in sorted(set(ID_LIKE.findall(report)) - set(reviews)):
        errors.append(f"리포트에 모르는 review_id가 있습니다: {rid}")
    for ch in CHAPTERS:
        if not re.search(rf"^{re.escape(ch)}", report, re.M):
            errors.append(f"'{ch}'로 시작하는 장이 없습니다.")
    errors += check_issue_counts(run, report, brands)
    for n, line in enumerate(report.splitlines(), 1):
        if "·" in line:
            errors.append(f"{n}번째 줄에 가운뎃점(·)이 있습니다: {line.strip()[:60]}")
    readings = report.count("데이터 읽기")
    if readings < 8:
        warns.append(f"'데이터 읽기'가 {readings}번뿐입니다(1~7장, 9장에 하나씩과 10장 브랜드마다 기대).")
    if not cited:
        warns.append("인용이 하나도 없습니다.")

    status = "FAIL" if errors else "PASS"
    write_json(run / "07_quote_check.json", {"checked_at": now_iso(), "status": status, "cited_review_ids": cited,
                                             "errors": errors, "warnings": warns})
    print(f"리포트 기계 검사: {status}  (인용 {len(cited)}개)")
    for e in errors:
        print(f"  오류: {e}")
    for w in warns:
        print(f"  주의: {w}")
    return 1 if errors else 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("mode", choices=["tags", "report", "negation"])
    ap.add_argument("run", nargs="?")
    ap.add_argument("--model", default="sonnet", choices=["sonnet", "top"])
    ap.add_argument("--tags-file", default="04_tags.jsonl", help="negation: 볼 태그 파일")
    ap.add_argument("--batches", default=None, help="이 묶음만 검사(쉼표로 구분). 합치지 않는다")
    args = ap.parse_args()
    run = resolve_run(args.run)
    only = [x.strip() for x in args.batches.split(",") if x.strip()] if args.batches else None
    if args.mode == "negation":
        sys.exit(negation_check(run, args.tags_file))
    sys.exit(check_tags(run, args.model, only) if args.mode == "tags" else check_report(run))


if __name__ == "__main__":
    main()
