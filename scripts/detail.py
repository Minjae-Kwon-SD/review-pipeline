"""개발 가이드용 설계 정보(리뷰마다 뽑을 항목) 준비.

사용:
  python scripts/detail.py sample [회차] [--n 150]
    02_reviews.csv에서 ASIN과 별점 묶음(1~2, 3, 4~5)이 고르게 섞이게 n개를 뽑아 13_detail_sample.csv로 쓴다(시드 고정).
    정답 세트 리뷰(gold/gold_reviews.csv의 review_id)는 여기서 뺀다. detail-schema-drafter는 이 파일만 읽는다.
  python scripts/detail.py check [회차]
    13_detail_schema_draft.yaml 검사: 항목 15개 이하, 칸(id, name_ko, format, definition, fill_rule, quote_required,
    sample_count, examples, guide_use), 표본 5개 이상, 형식 값, 예시 인용이 표본의 그 리뷰 원문에 그대로 있는지,
    정답 세트 리뷰 id가 없는지. 결과: 13_detail_schema_check.json. 오류가 있으면 종료 코드 1.
  python scripts/detail.py approve [회차] --approved-at <UTC> --approved-by "<누가, 어떻게>"
    13_detail_schema_draft.yaml에 13_detail_schema_edits.yaml(고친 곳: 값 나누기 split_values, 덧붙일 칸 extra)을 적용해
    13_detail_schema_approved.yaml로 저장한다.
  python scripts/detail.py plan [회차] [--size 50]
    02_reviews.csv 전체를 ASIN마다 묶음으로 나눠 14_detail_input/<묶음>.jsonl과 14_detail_batches.json을 쓴다.
  python scripts/detail.py extract-check [회차]
    detail-extractor 출력(14_details_<묶음>.jsonl) 검사: 승인 항목과 허용 값만, 숫자, extra 조건, 입력 리뷰마다 한 줄 이상.
    인용이 그 리뷰 제목이나 본문에 글자 그대로(공백과 따옴표 모양만 허용) 없으면 그 값은 버리고 센다.
    형식 오류나 빠진 리뷰가 있는 묶음은 failed_batches. 모두 통과하면 14_details.jsonl과 14_detail_counts.json(항목과 값마다
    리뷰 수, 가중 비율, ASIN별 수, 숫자 항목은 ASIN별 값과 중앙값). 결과: 14_detail_check.json
  python scripts/detail.py rejudge-plan [회차] --items a,b [--size 50]
    이미 값이 있는 리뷰만 골라 정한 항목만 다시 판정할 묶음(14_rejudge_batches.json, 14_rejudge_input/)을 만든다.
  python scripts/detail.py rejudge-merge [회차]
    다시 판정 결과(14_rejudge_<묶음>.jsonl)를 검사하고 그 리뷰들의 그 항목 값만 14_details.jsonl에서 바꾼다(백업 14_details_before_rejudge.jsonl).
    항목별 전후 수는 14_rejudge_check.json, 새로 생긴 값은 감사 표본 14b_rejudge_audit_sample.jsonl.
    감사 집계는 audit --sample-file 14b_rejudge_audit_sample.jsonl --audit-file 14b_rejudge_audit.yaml.
  python scripts/detail.py audit-sample [회차] [--n 150]   /   python scripts/detail.py audit [회차]
    항목과 ASIN이 고르게 섞이게 값 n개를 뽑고(14b_detail_audit_sample.jsonl), evidence-auditor 판정(14b_detail_audit.yaml)의
    FAIL 비율을 센다(14b_detail_audit_summary.json, 5%를 넘으면 종료 코드 1).
"""
import argparse
import csv
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from issues import GROUP, review_weights, seeded  # noqa: E402
from pipeline_io import (REVIEW_COLS, die, load_csv_or_die, load_yaml, norm_text, now_iso, pct, read_jsonl,  # noqa: E402
                         resolve_run, write_json, write_jsonl)

for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass

SAMPLE_COLS = ["review_id", "asin", "brand", "star", "title", "body"]
FORMATS = ("number", "choice", "text")
GUIDE_USES = ("시장 진입 조건", "경쟁사 점수표", "집중 분석", "소비자 기준표", "상세페이지 문구")
FIELDS = ("id", "name_ko", "format", "definition", "fill_rule", "quote_required", "sample_count", "examples", "guide_use")
MAX_ITEMS, MIN_COUNT = 15, 5


def gold_ids(run):
    p = run / "gold" / "gold_reviews.csv"
    if not p.exists():
        return set()
    with p.open(encoding="utf-8-sig") as f:
        return {r["review_id"] for r in csv.DictReader(f)}


def sample(run, n):
    reviews = load_csv_or_die(run / "02_reviews.csv", REVIEW_COLS)
    gold = gold_ids(run)
    brands = {}
    asins_csv = run / "01_asins.csv"
    if asins_csv.exists():
        with asins_csv.open(encoding="utf-8-sig") as f:
            brands = {r["asin"]: r.get("brand", "") for r in csv.DictReader(f)}
    pool = [r for r in reviews if r["review_id"] not in gold]
    rng = seeded(run, "detail_sample")
    cells = defaultdict(list)
    for r in sorted(pool, key=lambda r: r["review_id"]):
        cells[(r["asin"], GROUP[int(r["star"])])].append(r)
    for v in cells.values():
        rng.shuffle(v)
    keys, out = sorted(cells), []
    while len(out) < n and any(cells[c] for c in keys):
        for c in keys:
            if len(out) >= n:
                break
            if cells[c]:
                out.append(cells[c].pop())
    out.sort(key=lambda r: (r["asin"], int(r["star"]), r["review_id"]))
    with (run / "13_detail_sample.csv").open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(SAMPLE_COLS)
        for r in out:
            w.writerow([r["review_id"], r["asin"], brands.get(r["asin"], ""), r["star"], r["title"], r["body"]])
    by = Counter((r["asin"], GROUP[int(r["star"])]) for r in out)
    print(f"설계 정보 표본 {len(out)}개(정답 세트 {len(gold)}개 제외) → 13_detail_sample.csv")
    for a in sorted({k[0] for k in by}):
        print(f"  {a}: " + ", ".join(f"{g} {by[(a, g)]}" for g in ("neg", "neu", "pos")))
    return 0


def check(run):
    draft = load_yaml(run / "13_detail_schema_draft.yaml") or {}
    with (run / "13_detail_sample.csv").open(encoding="utf-8-sig") as f:
        smp = {r["review_id"]: r for r in csv.DictReader(f)}
    gold = gold_ids(run)
    items = draft.get("items") or []
    errors = []
    if not items:
        errors.append("items가 비어 있습니다.")
    if len(items) > MAX_ITEMS:
        errors.append(f"항목이 {len(items)}개입니다(최대 {MAX_ITEMS}개).")
    ids = Counter(str(it.get("id")) for it in items)
    for i, c in ids.items():
        if c > 1:
            errors.append(f"id {i}가 {c}번 나옵니다.")
    quotes = 0
    for it in items:
        where = f"항목 {it.get('id')}"
        miss = [k for k in FIELDS if it.get(k) in (None, "", [])]
        if miss:
            errors.append(f"{where}: 빈 칸 {', '.join(miss)}")
        if it.get("format") not in FORMATS:
            errors.append(f"{where}: format은 {', '.join(FORMATS)} 중 하나여야 합니다({it.get('format')}).")
        if it.get("format") == "choice" and not it.get("allowed_values"):
            errors.append(f"{where}: choice 형식이면 allowed_values가 있어야 합니다.")
        if it.get("format") == "number" and not it.get("unit"):
            errors.append(f"{where}: number 형식이면 unit이 있어야 합니다.")
        try:
            cnt = int(it.get("sample_count") or 0)
        except (TypeError, ValueError):
            cnt = 0
        if cnt < MIN_COUNT:
            errors.append(f"{where}: 표본 리뷰 {cnt}개(최소 {MIN_COUNT}개).")
        uses = it.get("guide_use") or []
        uses = uses if isinstance(uses, list) else [uses]
        bad = [u for u in uses if u not in GUIDE_USES]
        if bad:
            errors.append(f"{where}: guide_use 값 {bad}(허용: {', '.join(GUIDE_USES)})")
        for ex in it.get("examples") or []:
            rid, q = str(ex.get("review_id")), str(ex.get("quote") or "")
            quotes += 1
            if rid in gold:
                errors.append(f"{where}: 정답 세트 리뷰 {rid}를 예시로 썼습니다.")
            r = smp.get(rid)
            if r is None:
                errors.append(f"{where}: 예시 {rid}는 표본에 없습니다.")
            elif norm_text(q) not in norm_text(r["title"]) and norm_text(q) not in norm_text(r["body"]):
                errors.append(f"{where}: 예시 {rid} 인용이 원문에 없습니다: \"{q[:60]}\"")
        if len(it.get("examples") or []) != 2:
            errors.append(f"{where}: 예시 인용은 2개여야 합니다({len(it.get('examples') or [])}개).")
    status = "FAIL" if errors else "PASS"
    write_json(run / "13_detail_schema_check.json", {"checked_at": now_iso(), "status": status, "items": len(items),
                                                      "quotes_checked": quotes, "errors": errors})
    print(f"설계 정보 초안 검사: {status}  (항목 {len(items)}개, 인용 {quotes}개)")
    for e in errors:
        print(f"  오류: {e}")
    return 1 if errors else 0


# ---------------------------------------------------------------- 승인, 묶음, 추출 검사, 감사

def approve(run, approved_at, approved_by):
    import copy
    import yaml
    draft = load_yaml(run / "13_detail_schema_draft.yaml") or {}
    edits = load_yaml(run / "13_detail_schema_edits.yaml") or {}
    out = copy.deepcopy(draft)
    items = {it["id"]: it for it in out.get("items") or []}
    for e in edits.get("split_values") or []:
        it = items[e["item"]]
        vals = it["allowed_values"]
        i = next(k for k, v in enumerate(vals) if v["value"] == e["value"])
        vals[i:i + 1] = e["into"]
        if e.get("rule"):
            it["fill_rule"] = f"{it['fill_rule']} {e['rule']}"
    for e in edits.get("extra") or []:
        it = items[e["item"]]
        it.setdefault("extra", {})[e["field"]] = {"when_value": e["when_value"], "format": e["format"], "rule": e["rule"]}
        it["fill_rule"] = f"{it['fill_rule']} {e['rule']}"
    out.update({"version": "approved", "approved_at": approved_at, "approved_by": approved_by, "edits": edits})
    (run / "13_detail_schema_approved.yaml").write_text(yaml.safe_dump(out, allow_unicode=True, sort_keys=False, width=1000),
                                                         encoding="utf-8")
    print(f"승인본을 13_detail_schema_approved.yaml로 저장했습니다(항목 {len(items)}개, 고친 곳 "
          f"{len(edits.get('split_values') or []) + len(edits.get('extra') or [])}개, {approved_at}, {approved_by}).")
    return 0


def approved_items(run):
    d = load_yaml(run / "13_detail_schema_approved.yaml") or {}
    if d.get("version") != "approved":
        die("13_detail_schema_approved.yaml이 없거나 승인본이 아닙니다.")
    return {it["id"]: it for it in d["items"]}


def plan(run, size):
    approved_items(run)
    reviews = load_csv_or_die(run / "02_reviews.csv", REVIEW_COLS)
    outdir = run / "14_detail_input"
    outdir.mkdir(exist_ok=True)
    by_asin = defaultdict(list)
    for r in reviews:
        by_asin[r["asin"]].append(r)
    batches = []
    for a in sorted(by_asin):
        rs = sorted(by_asin[a], key=lambda r: r["review_id"])
        for k in range(0, len(rs), size):
            bid = f"{a}_{k // size + 1:02d}"
            chunk = rs[k:k + size]
            write_jsonl(outdir / f"{bid}.jsonl", [{"review_id": r["review_id"], "title": r["title"], "body": r["body"]} for r in chunk])
            batches.append({"batch_id": bid, "asin": a, "reviews": len(chunk), "input": f"14_detail_input/{bid}.jsonl",
                            "output": f"14_details_{bid}.jsonl"})
    write_json(run / "14_detail_batches.json", {"made_at": now_iso(), "size": size, "reviews": len(reviews), "batches": batches})
    print(f"설계 정보 추출 묶음 {len(batches)}개(리뷰 {len(reviews)}개, 묶음 최대 {size}개) → 14_detail_batches.json")
    return 0


def check_value(it, row):
    """값 하나의 형식 오류(없으면 None)."""
    v = row.get("value")
    fmt = it.get("format")
    if fmt == "choice":
        if v not in {x["value"] for x in it.get("allowed_values") or []}:
            return f"허용 값이 아님: {v}"
    elif fmt == "number":
        if isinstance(v, bool) or not isinstance(v, (int, float)):
            return f"숫자가 아님: {v}"
    elif fmt == "text":
        if not isinstance(v, str) or not v.strip():
            return "빈 글"
    for field, rule in (it.get("extra") or {}).items():
        need = v == rule.get("when_value")
        has = bool(str((row.get("extra") or {}).get(field) or "").strip())
        if need and not has:
            return f"값이 {v}이면 extra.{field}가 있어야 함"
    return None


def quote_ok(q, r):
    if not q.strip():
        return False
    return (q in r["title"] or q in r["body"] or norm_text(q) in norm_text(r["title"]) or norm_text(q) in norm_text(r["body"]))


def known_exceptions(run):
    """이 회차의 알려진 예외(14_known_exceptions.yaml): {(review_id, item): 이유}. 파일은 회차 폴더마다 따로라 다른 회차에는 걸리지 않는다."""
    p = run / "14_known_exceptions.yaml"
    d = (load_yaml(p) or {}) if p.exists() else {}
    return {(str(e["review_id"]), str(e["item"])): str(e.get("reason") or "") for e in d.get("exceptions") or []}


def extract_check(run):
    items = approved_items(run)
    reviews = {r["review_id"]: r for r in load_csv_or_die(run / "02_reviews.csv", REVIEW_COLS)}
    plan_ = json.loads((run / "14_detail_batches.json").read_text(encoding="utf-8"))
    errors, failed, merged, dropped = [], [], [], []
    keys = set()
    known, known_hits = known_exceptions(run), []
    for b in plan_["batches"]:
        want = {x["review_id"] for x in read_jsonl(run / b["input"])}
        out_path = run / b["output"]
        if not out_path.exists():
            errors.append(f"{b['batch_id']}: {b['output']}이(가) 없습니다.")
            failed.append(b["batch_id"])
            continue
        n_err = len(errors)
        rows = read_jsonl(out_path, errors)
        seen, bad = set(), len(errors) > n_err      # JSON으로 읽지 못한 줄이 있으면 묶음 실패
        for n, row in enumerate(rows, 1):
            rid = row.get("review_id")
            if rid not in want:
                errors.append(f"{b['batch_id']} {n}번째: 이 묶음에 없는 리뷰 {rid}")
                bad = True
                continue
            seen.add(rid)
            if row.get("item") is None:
                continue
            it = items.get(row.get("item"))
            if it is None:
                errors.append(f"{b['batch_id']} {n}번째 {rid}: 승인 항목이 아님 {row.get('item')}")
                bad = True
                continue
            e = check_value(it, row)
            if e:
                errors.append(f"{b['batch_id']} {n}번째 {rid} {row['item']}: {e}")
                bad = True
                continue
            q = str(row.get("quote") or "")
            r = reviews[rid]
            if not quote_ok(q, r):     # 값만 버리고 합치면 그 리뷰의 값이 조용히 빠지므로 묶음을 실패로 돌린다
                if (rid, row["item"]) in known:     # 이 회차의 알려진 예외: 값은 버리고 KNOWN으로 따로 보인다(숨기지 않음)
                    known_hits.append({"batch": b["batch_id"], "review_id": rid, "item": row["item"], "value": row.get("value"), "quote": q,
                                       "reason": known[(rid, row["item"])]})
                    continue
                dropped.append({"batch": b["batch_id"], "review_id": rid, "item": row["item"], "value": row.get("value"), "quote": q})
                errors.append(f"{b['batch_id']} {n}번째 {rid} {row['item']}: 인용이 원문에 없음({q[:40]})")
                bad = True
                continue
            key = (rid, row["item"], json.dumps(row.get("value"), ensure_ascii=False))
            if key in keys:
                continue
            keys.add(key)
            m = {"review_id": rid, "asin": r["asin"], "item": row["item"], "value": row.get("value"), "quote": q}
            if row.get("extra"):
                m["extra"] = row["extra"]
            merged.append(m)
        missing = want - seen
        if missing:
            errors.append(f"{b['batch_id']}: 한 줄도 없는 리뷰 {len(missing)}개(예: {sorted(missing)[0]})")
            bad = True
        if bad:
            failed.append(b["batch_id"])
    status = "FAIL" if failed else "PASS"
    result = {"checked_at": now_iso(), "status": status, "failed_batches": failed, "errors": errors[:200],
              "values": len(merged), "dropped_quotes": len(dropped), "dropped": dropped[:100],
              "known_exceptions": known_hits}
    if not failed:
        write_jsonl(run / "14_details.jsonl", merged)
        result["counts"] = detail_counts(run, merged, items)
    write_json(run / "14_detail_check.json", result)
    print(f"설계 정보 추출 검사: {status}  (묶음 {len(plan_['batches'])}개, 실패 {len(failed)}개, 값 {len(merged)}개, "
          f"원문에 없어 버린 인용 {len(dropped)}개, KNOWN {len(known_hits)}개)")
    for k in known_hits:
        print(f"  KNOWN(14_known_exceptions.yaml): {k['batch']} {k['review_id']} {k['item']}: 인용이 원문에 없음({k['quote'][:40]}) - {k['reason']}")
    for e in errors[:30]:
        print(f"  오류: {e}")
    return 1 if failed else 0


def median(v):
    v = sorted(v)
    if not v:
        return None
    n = len(v)
    return v[n // 2] if n % 2 else round((v[n // 2 - 1] + v[n // 2]) / 2, 3)


def detail_counts(run, merged, items):
    reviews, weight = review_weights(run)
    asin_of = {r["review_id"]: r["asin"] for r in reviews}
    total_w = sum(weight.values())
    out = {"total_reviews": len(reviews), "items": {}}
    for iid, it in items.items():
        rows = [m for m in merged if m["item"] == iid]
        rids = {m["review_id"] for m in rows}
        entry = {"name_ko": it["name_ko"], "format": it["format"], "reviews": len(rids),
                 "weighted_pct": pct(sum(weight[r] for r in rids), total_w),
                 "by_asin": dict(sorted(Counter(asin_of[r] for r in rids).items()))}
        if it["format"] == "choice":
            vals = []
            for v in it.get("allowed_values") or []:
                vr = {m["review_id"] for m in rows if m["value"] == v["value"]}
                vals.append({"value": v["value"], "ko": v.get("ko"), "reviews": len(vr),
                             "weighted_pct": pct(sum(weight[r] for r in vr), total_w),
                             "by_asin": dict(sorted(Counter(asin_of[r] for r in vr).items()))})
            entry["values"] = vals
        elif it["format"] == "number":
            per = defaultdict(list)
            for m in rows:
                per[asin_of[m["review_id"]]].append(float(m["value"]))
            entry["numbers_by_asin"] = {a: sorted(v) for a, v in sorted(per.items())}
            entry["median"] = median([float(m["value"]) for m in rows])
            entry["median_by_asin"] = {a: median(v) for a, v in sorted(per.items())}
        out["items"][iid] = entry
    write_json(run / "14_detail_counts.json", out)
    return {iid: e["reviews"] for iid, e in out["items"].items()}


def audit_sample(run, n):
    rows = read_jsonl(run / "14_details.jsonl")
    rng = seeded(run, "detail_audit")
    cells = defaultdict(list)
    for r in sorted(rows, key=lambda r: (r["review_id"], r["item"], json.dumps(r["value"], ensure_ascii=False))):
        cells[(r["item"], r["asin"])].append(r)
    for v in cells.values():
        rng.shuffle(v)
    keys, out = sorted(cells), []
    while len(out) < n and any(cells[k] for k in keys):
        for k in keys:
            if len(out) >= n:
                break
            if cells[k]:
                out.append(cells[k].pop())
    write_jsonl(run / "14b_detail_audit_sample.jsonl", out)
    print(f"설계 정보 감사 표본 {len(out)}개(항목 {len({r['item'] for r in out})}개, ASIN {len({r['asin'] for r in out})}개) "
          "→ 14b_detail_audit_sample.jsonl")
    return 0


def audit(run, max_fail, sample_file="14b_detail_audit_sample.jsonl", audit_file="14b_detail_audit.yaml"):
    data = load_yaml(run / audit_file) or {}
    a = data.get("audit") if isinstance(data, dict) else None
    if not isinstance(a, dict):
        die(f"{audit_file} 맨 위에 audit: 항목이 없습니다.")
    sample = read_jsonl(run / sample_file)
    # 다시 판정 표본은 행마다 change(added, removed, quote_changed)가 있다. 판정도 change별로 센다(없어짐 FAIL = 지우면 안 됐음).
    keys = {(s["review_id"], s["item"], json.dumps(s["value"], ensure_ascii=False), s.get("change", "")) for s in sample}
    fails, warns = [], []
    for f in a.get("findings") or []:
        if str(f.get("status", "")).upper() != "FAIL":
            continue
        k = (str(f.get("review_id")), str(f.get("item")), json.dumps(f.get("value"), ensure_ascii=False), str(f.get("change") or ""))
        if k not in keys:
            warns.append(f"표본에 없는 항목 {k}")
            continue
        fails.append(k)
    rate = len(fails) / len(sample) if sample else 0.0
    checked = a.get("checked")
    if not sample:
        status = "EMPTY"            # 빈 표본은 PASS가 아니라 따로 판정
    elif checked != len(sample) or warns:
        status = "INCOMPLETE"       # 감사자가 표본을 다 보지 않았거나, 표본에 없는 판정을 냈으면 PASS로 넘기지 않음
    else:
        status = "PASS" if rate <= max_fail else "FAIL"
    write_json(run / audit_file.replace(".yaml", "_summary.json"), {"checked_at": now_iso(), "status": status, "sample": len(sample),
                                                       "auditor_checked": checked,
                                                       "fail": len(fails), "fail_rate": round(rate, 3), "max_fail_rate": max_fail,
                                                       "by_item": dict(Counter(k[1] for k in fails)),
                                                       "by_change": dict(Counter(k[3] for k in fails if k[3])), "warnings": warns})
    print(f"설계 정보 감사 집계: {status}  (표본 {len(sample)}개 중 FAIL {len(fails)}개 = {rate:.1%}, 기준 {max_fail:.0%} 이하)"
          + ("  표본이 비어 판정하지 않음(메인 세션이 따로 정함)" if status == "EMPTY" else "")
          + (f"  감사가 끝나지 않음(checked {checked}, 표본 {len(sample)}개, 표본에 없는 판정 {len(warns)}개)" if status == "INCOMPLETE" else ""))
    return 0 if status == "PASS" else 1


def rejudge_plan(run, items_arg, size):
    """이미 뽑은 값이 있는 리뷰만 골라 정한 항목만 다시 판정하는 묶음(14_rejudge_batches.json, 14_rejudge_input/)."""
    items = approved_items(run)
    want = [x.strip() for x in items_arg.split(",") if x.strip()]
    bad = [x for x in want if x not in items]
    if bad:
        die(f"승인 항목이 아님: {bad}")
    reviews = {r["review_id"]: r for r in load_csv_or_die(run / "02_reviews.csv", REVIEW_COLS)}
    rows = read_jsonl(run / "14_details.jsonl")
    rids = sorted({r["review_id"] for r in rows if r["item"] in want})
    outdir = run / "14_rejudge_input"
    outdir.mkdir(exist_ok=True)
    batches = []
    for k in range(0, len(rids), size):
        bid = f"R{k // size + 1:02d}"
        chunk = rids[k:k + size]
        write_jsonl(outdir / f"{bid}.jsonl", [{"review_id": r, "title": reviews[r]["title"], "body": reviews[r]["body"]} for r in chunk])
        batches.append({"batch_id": bid, "reviews": len(chunk), "input": f"14_rejudge_input/{bid}.jsonl", "output": f"14_rejudge_{bid}.jsonl"})
    write_json(run / "14_rejudge_batches.json", {"made_at": now_iso(), "items": want, "size": size, "reviews": len(rids), "batches": batches})
    print(f"다시 판정 묶음 {len(batches)}개(항목 {', '.join(want)}, 값이 있던 리뷰 {len(rids)}개) → 14_rejudge_batches.json")
    return 0


def rejudge_merge(run):
    """다시 판정 결과를 검사하고, 그 리뷰들의 그 항목 값만 14_details.jsonl에서 바꾼다. 바뀐 행은 감사 표본으로 쓴다."""
    items = approved_items(run)
    plan_ = json.loads((run / "14_rejudge_batches.json").read_text(encoding="utf-8"))
    want = set(plan_["items"])
    reviews = {r["review_id"]: r for r in load_csv_or_die(run / "02_reviews.csv", REVIEW_COLS)}
    errors, failed, new, dropped, scope = [], [], [], [], set()
    for b in plan_["batches"]:
        ids = {x["review_id"] for x in read_jsonl(run / b["input"])}
        scope |= ids
        p = run / b["output"]
        if not p.exists():
            errors.append(f"{b['batch_id']}: {b['output']}이(가) 없습니다.")
            failed.append(b["batch_id"])
            continue
        n_err = len(errors)
        out_rows = read_jsonl(p, errors)
        seen, bad = set(), len(errors) > n_err      # JSON으로 읽지 못한 줄이 있으면 묶음 실패
        for n, row in enumerate(out_rows, 1):
            rid = row.get("review_id")
            if rid not in ids:
                errors.append(f"{b['batch_id']} {n}번째: 이 묶음에 없는 리뷰 {rid}")
                bad = True
                continue
            seen.add(rid)
            if row.get("item") is None:
                continue
            if row.get("item") not in want:
                errors.append(f"{b['batch_id']} {n}번째 {rid}: 다시 판정할 항목이 아님 {row.get('item')}")
                bad = True
                continue
            e = check_value(items[row["item"]], row)
            if e:
                errors.append(f"{b['batch_id']} {n}번째 {rid} {row['item']}: {e}")
                bad = True
                continue
            q = str(row.get("quote") or "")
            if not quote_ok(q, reviews[rid]):
                dropped.append({"review_id": rid, "item": row["item"], "value": row.get("value"), "quote": q})
                continue
            m = {"review_id": rid, "asin": reviews[rid]["asin"], "item": row["item"], "value": row.get("value"), "quote": q}
            if row.get("extra"):
                m["extra"] = row["extra"]
            new.append(m)
        if ids - seen:
            errors.append(f"{b['batch_id']}: 한 줄도 없는 리뷰 {len(ids - seen)}개")
            bad = True
        if bad:
            failed.append(b["batch_id"])
    if dropped:      # 인용이 원문에 없으면 교체하지 않는다(그 값만 버리고 합치면 바뀐 값이 조용히 빠짐)
        failed += sorted({b["batch_id"] for b in plan_["batches"]
                          if any(d["review_id"] in {x["review_id"] for x in read_jsonl(run / b["input"])} for d in dropped)} - set(failed))
        errors += [f"{d['review_id']} {d['item']}: 인용이 원문에 없음({d['quote'][:40]})" for d in dropped]
    if failed:
        write_json(run / "14_rejudge_check.json", {"checked_at": now_iso(), "status": "FAIL", "failed_batches": failed, "errors": errors[:200],
                                                   "dropped_quotes": dropped})
        print(f"다시 판정 검사: FAIL  (실패 묶음 {failed})")
        for e in errors[:30]:
            print(f"  오류: {e}")
        return 1
    old = read_jsonl(run / "14_details.jsonl")
    if not (run / "14_details_before_rejudge.jsonl").exists():
        write_jsonl(run / "14_details_before_rejudge.jsonl", old)
    key = lambda m: (m["review_id"], m["item"], json.dumps(m["value"], ensure_ascii=False))
    seen, uniq = set(), []
    for m in new:
        if key(m) not in seen:
            seen.add(key(m))
            uniq.append(m)
    before = [m for m in old if m["review_id"] in scope and m["item"] in want]
    keep = [m for m in old if not (m["review_id"] in scope and m["item"] in want)]
    merged = sorted(keep + uniq, key=lambda m: (m["review_id"], m["item"], json.dumps(m["value"], ensure_ascii=False)))
    write_jsonl(run / "14_details.jsonl", merged)
    detail_counts(run, merged, items)
    bk, ak = {key(m) for m in before}, {key(m) for m in uniq}
    added = [m for m in uniq if key(m) not in bk]
    removed = [m for m in before if key(m) not in ak]
    bq = {key(m): m["quote"] for m in before}
    requoted = [m for m in uniq if key(m) in bq and bq[key(m)] != m["quote"]]
    per = {}
    for it in sorted(want):
        cb = Counter(m["value"] for m in before if m["item"] == it)
        ca = Counter(m["value"] for m in uniq if m["item"] == it)
        per[it] = {"before": sum(cb.values()), "after": sum(ca.values()),
                   "added": sum(1 for m in added if m["item"] == it), "removed": sum(1 for m in removed if m["item"] == it),
                   "by_value": {v: [cb[v], ca[v]] for v in sorted(set(cb) | set(ca))}}
    # 감사 표본: 바뀐 행 전부(새로 생김, 없어짐, 인용만 바뀜)
    write_jsonl(run / "14b_rejudge_audit_sample.jsonl", [{**m, "change": "added"} for m in added] + [{**m, "change": "removed"} for m in removed]
                + [{**m, "change": "quote_changed", "old_quote": bq[key(m)]} for m in requoted])
    write_json(run / "14_rejudge_check.json", {"checked_at": now_iso(), "status": "PASS", "reviews": len(scope), "items": per,
                                               "added": added, "removed": removed, "quote_changed": requoted, "dropped_quotes": dropped})
    print(f"다시 판정 검사: PASS  (리뷰 {len(scope)}개, 원문에 없어 버린 인용 {len(dropped)}개)")
    for it, v in per.items():
        print(f"  {it}: 값 {v['before']}개 → {v['after']}개(새로 생김 {v['added']}, 없어짐 {v['removed']})")
    print(f"  바뀐 행 {len(added) + len(removed) + len(requoted)}개(새로 생김 {len(added)}, 없어짐 {len(removed)}, 인용만 바뀜 {len(requoted)}) "
          "→ 14b_rejudge_audit_sample.jsonl(감사 표본)")
    return 0


def main():
    ap = argparse.ArgumentParser(description="설계 정보 표본과 초안 검사")
    ap.add_argument("mode", choices=["sample", "check", "approve", "plan", "extract-check", "audit-sample", "audit",
                                     "rejudge-plan", "rejudge-merge"])
    ap.add_argument("--items", default="", help="rejudge-plan: 다시 판정할 항목 id(쉼표로)")
    ap.add_argument("--sample-file", default="14b_detail_audit_sample.jsonl", help="audit: 감사 표본 파일")
    ap.add_argument("--audit-file", default="14b_detail_audit.yaml", help="audit: 감사 결과 파일")
    ap.add_argument("run", nargs="?")
    ap.add_argument("--n", type=int, default=150)
    ap.add_argument("--size", type=int, default=50)
    ap.add_argument("--max-fail", type=float, default=0.05)
    ap.add_argument("--approved-at", default=None)
    ap.add_argument("--approved-by", default=None)
    args = ap.parse_args()
    run = resolve_run(args.run)
    if args.mode == "approve" and not (args.approved_at and args.approved_by):
        die("approve에는 --approved-at과 --approved-by가 필요합니다.")
    sys.exit({"sample": lambda: sample(run, args.n), "check": lambda: check(run),
              "approve": lambda: approve(run, args.approved_at, args.approved_by), "plan": lambda: plan(run, args.size),
              "extract-check": lambda: extract_check(run), "audit-sample": lambda: audit_sample(run, args.n),
              "audit": lambda: audit(run, args.max_fail, args.sample_file, args.audit_file),
              "rejudge-plan": lambda: rejudge_plan(run, args.items, args.size), "rejudge-merge": lambda: rejudge_merge(run)}[args.mode]())


if __name__ == "__main__":
    main()
