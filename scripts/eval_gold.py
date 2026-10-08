"""정답 세트: 고르기, 태깅 화면, 형식 검사, 채점, 표본 감사.

사용:
  python scripts/eval_gold.py pick [회차] [--per-asin 5] [--min-chars 40] [--sample-per-asin 25]
    정답 세트: ASIN마다 per-asin개. language가 빈 값(영어)이고 본문이 min-chars자 이상인 리뷰만.
      ASIN 안에서는 표본이 있는 별점 묶음(config/pipeline.yaml의 weighting.groups)을 고르게, 부정과 긍정은 있으면 1개 이상.
      모자라면 다른 ASIN에서 채우고 gold/gold_pick_log.json에 남긴다.
    스키마 표본: 정답 세트를 뺀 리뷰에서 ASIN마다 sample-per-asin개, ASIN 안에서는 표본이 있는 별점마다 고르게.
      언어는 거르지 않는다. schema-drafter가 읽는 파일.
    시드는 회차 이름으로 정해서 다시 돌려도 같은 결과가 나온다.
    결과: gold/gold_reviews.csv, gold/gold_pick_log.json, 03_schema_sample.csv(02_reviews.csv와 같은 칸),
          03_schema_input.csv(정답 세트를 뺀 전부).
    정답 세트 리뷰는 스키마 예시로 쓰지 않는다(쓰면 점수가 부풀려진다).

  python scripts/eval_gold.py sheet [회차]
    스키마 승인 뒤, 민재님이 정답 세트를 태깅하는 화면 gold/gold_tagging.html을 만든다(한 파일, 외부 라이브러리 없음).
    고른 값은 브라우저 localStorage에 저장되고, "gold_tags.jsonl 내보내기"로 내려받아 gold/gold_tags.jsonl로 저장한다.
    태거 결과는 화면에 넣지 않는다.

  python scripts/eval_gold.py gold [회차]
    민재님이 쓴 gold/gold_tags.jsonl의 형식을 본다: 정답 세트 리뷰인지, 승인 스키마의 주제인지,
    감성 네 값 중 하나인지, 같은 리뷰 같은 주제가 두 번인지, 태그가 하나도 없는 정답 세트 리뷰가 있는지.
    오류가 있으면 종료 코드 1.

  python scripts/eval_gold.py score [회차] [--f1 0.80] [--sentiment 0.90]
    정답 세트 기준으로 sonnet(04_tags.jsonl의 정답 세트 리뷰, 리포트가 쓰는 태그. 아직 없으면 시험 태깅의
    04_tags_sonnet_gold.jsonl)과
    top(04_tags_top_gold.jsonl, 있으면)을 채점한다.
    주제: (review_id, topic) 쌍의 정밀도, 재현율, F1. 감성: 주제가 맞은 쌍 중 감성이 같은 비율.
    결과: 04_gold_eval.json(모델별 summary_ko 포함), 04_gold_eval.md(불일치 목록). sonnet이 기준 미달이면 종료 코드 1.

  python scripts/eval_gold.py audit-sample [회차] [--n 150]
    04_tags.jsonl에서 감사할 표본을 고른다: ASIN마다 n / ASIN 수개, ASIN 안에서는 감성 비율대로,
    부정 태그가 있으면 최소 3개. 정답 세트 리뷰(gold/gold_reviews.csv)의 태그는 뺀다(검증 표본과 겹치지 않게).
    시드 고정. 결과: 04_audit_sample.jsonl(evidence-auditor가 판정할 태그).

  python scripts/eval_gold.py audit [회차] [--max-fail 0.05]
    evidence-auditor의 태그 검수(04_tag_audit.yaml)를 04_audit_sample.jsonl과 맞춰 센다.
    FAIL 비율 = FAIL 태그 수 / 표본 태그 수(전체와 ASIN별). 정답 세트 리뷰의 태그는 표본에서 빼고 센다(옛 표본에 섞여 있어도).
    보수적 비율 = (FAIL + UNVERIFIED + 빠진 태그 missed) / (표본 태그 + missed): 판정을 받지 못한 것을 모두 FAIL로 센 값.
    다시 태깅할 묶음(batches_with_findings)도 뽑는다.
    결과: 04_tag_audit_summary.json. 전체 FAIL 비율이 기준을 넘으면 종료 코드 1.
"""
import argparse
import csv
import hashlib
import json
import random
import sys
from collections import Counter, defaultdict
from pathlib import Path

from pipeline_io import (ASIN_COLS, REVIEW_COLS, SENTIMENTS, STARS, die, load_config, load_csv_or_die,
                         load_schema, load_yaml, now_iso, read_jsonl, resolve_run, write_json, write_jsonl)

SHEET_TEMPLATE = Path(__file__).resolve().parent / "gold_sheet.html"
GOLD_COLS = ["review_id", "asin", "star", "title", "body"]


def seeded(run, salt):
    """회차 이름과 용도로 정한 난수. 같은 회차면 늘 같은 결과."""
    return random.Random(int(hashlib.sha256(f"{run.name}:{salt}".encode("utf-8")).hexdigest()[:12], 16))


def shuffled(items, rng):
    items = sorted(items, key=lambda r: r["review_id"])
    rng.shuffle(items)
    return items


def csv_header(path):
    with open(path, encoding="utf-8-sig", newline="") as f:
        return [h.strip() for h in next(csv.reader(f), [])]


def write_rows(path, cols, rows):
    with open(path, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f)
        w.writerow(cols)
        for r in rows:
            w.writerow([r.get(c, "") for c in cols])


def star_table(rows, asins):
    c = defaultdict(Counter)
    for r in rows:
        c[r["asin"]][int(r["star"])] += 1
    lines = ["  ASIN         합계  1★  2★  3★  4★  5★"]
    for a in asins:
        lines.append(f"  {a}  {sum(c[a].values()):>4} " + " ".join(f"{c[a][s]:>3}" for s in STARS))
    lines.append(f"  합계        {len(rows):>4} " + " ".join(f"{sum(c[a][s] for a in asins):>3}" for s in STARS))
    return "\n".join(lines)


# ---------------------------------------------------------------- pick

def pick_group_round(pools, order, k, chosen):
    """묶음 순서 order대로 돌아가며 pools에서 하나씩 꺼내 chosen에 k개가 될 때까지 더한다."""
    while len(chosen) < k and any(pools[g] for g in order):
        for g in order:
            if len(chosen) >= k:
                break
            if pools[g]:
                chosen.append(pools[g].pop())
    return chosen


def pick(run, per_asin, min_chars, sample_per_asin):
    reviews = load_csv_or_die(run / "02_reviews.csv", REVIEW_COLS)
    groups = load_config()["weighting"]["groups"]
    group_of = {s: g for g, stars in groups.items() for s in stars}
    asins = sorted({r["asin"] for r in reviews})
    rng = seeded(run, "gold")

    # 정답 세트
    pools, gold, short = {}, {}, {}
    for a in asins:
        eligible = [r for r in reviews if r["asin"] == a and not r.get("language")
                    and len(r["body"].strip()) >= min_chars]
        pools[a] = {g: shuffled([r for r in eligible if group_of[int(r["star"])] == g], rng) for g in groups}
        chosen = []
        for g in ("negative", "positive"):          # 부정과 긍정은 있으면 먼저 하나씩
            if g in pools[a] and pools[a][g] and len(chosen) < per_asin:
                chosen.append(pools[a][g].pop())
        gold[a] = pick_group_round(pools[a], list(groups), per_asin, chosen)
        if len(gold[a]) < per_asin:
            short[a] = per_asin - len(gold[a])
    need = sum(short.values())
    filled = Counter()
    while need:
        donors = sorted((a for a in asins if any(pools[a].values())),
                        key=lambda a: (-sum(len(p) for p in pools[a].values()), a))
        if not donors:
            break
        for a in donors:
            if not need:
                break
            pick_group_round(pools[a], list(groups), len(gold[a]) + 1, gold[a])
            filled[a] += 1
            need -= 1
    gold_rows = [r for a in asins for r in gold[a]]
    (run / "gold").mkdir(exist_ok=True)
    write_rows(run / "gold" / "gold_reviews.csv", GOLD_COLS, gold_rows)
    gold_ids = {r["review_id"] for r in gold_rows}

    # 스키마 표본
    rng2 = seeded(run, "schema_sample")
    rest = [r for r in reviews if r["review_id"] not in gold_ids]
    sample = []
    for a in asins:
        by_star = {s: shuffled([r for r in rest if r["asin"] == a and int(r["star"]) == s], rng2) for s in STARS}
        sample += pick_group_round(by_star, list(STARS), sample_per_asin, [])
    order = {r["review_id"]: i for i, r in enumerate(reviews)}
    sample.sort(key=lambda r: order[r["review_id"]])
    write_rows(run / "03_schema_sample.csv", csv_header(run / "02_reviews.csv"), sample)
    write_rows(run / "03_schema_input.csv", REVIEW_COLS, rest)

    log = {"picked_at": now_iso(), "seed": f"{run.name}:gold / {run.name}:schema_sample",
           "criteria": {"per_asin": per_asin, "min_chars": min_chars, "language": "빈 값(영어)만",
                        "groups": groups, "sample_per_asin": sample_per_asin},
           "gold_reviews": len(gold_rows), "short": short, "filled_from": dict(filled),
           "unfilled": need, "schema_sample": len(sample), "schema_input": len(rest)}
    write_json(run / "gold" / "gold_pick_log.json", log)

    print(f"정답 세트 {len(gold_rows)}개를 gold/gold_reviews.csv에 적었습니다"
          f"(ASIN마다 {per_asin}개, 영어, 본문 {min_chars}자 이상).")
    print(star_table(gold_rows, asins))
    if short:
        print("  주의: 조건에 맞는 리뷰가 모자란 ASIN " + ", ".join(f"{a} {n}개" for a, n in short.items())
              + " → 다른 ASIN에서 채움: " + (", ".join(f"{a} {n}개" for a, n in filled.items()) or "없음")
              + (f", 그래도 {need}개 모자람" if need else ""))
    print(f"스키마 표본 {len(sample)}개를 03_schema_sample.csv에 적었습니다(ASIN마다 {sample_per_asin}개, 별점마다 고르게).")
    print(star_table(sample, asins))
    print(f"정답 세트를 뺀 리뷰 {len(rest)}개를 03_schema_input.csv에 적었습니다.")
    return 0


# ---------------------------------------------------------------- sheet

def sheet(run, translations=None):
    schema = load_schema(run)
    picked = run / "gold" / "gold_reviews.csv"
    if not picked.exists():
        die("gold/gold_reviews.csv가 없습니다. eval_gold.py pick을 먼저 돌려 주세요.")
    with open(picked, encoding="utf-8-sig", newline="") as f:
        gold = list(csv.DictReader(f))
    reviews = {r["review_id"]: r for r in load_csv_or_die(run / "02_reviews.csv", REVIEW_COLS)}
    brands = {r["asin"]: r["brand"] for r in load_csv_or_die(run / "01_asins.csv", ASIN_COLS)}
    # 있으면 원문 아래에 한국어 번역을 참고용으로 보여 준다(태깅은 원문 기준, 리포트와 인용 검사에는 쓰지 않음)
    # 번역 파일은 gold 폴더(기본)나 --translations로 준 경로(gold 폴더 쓰기가 막힌 세션에서 메인 세션이 쓴 파일)
    tr_path = Path(translations) if translations else run / "gold" / "gold_translations_ko.json"
    tr = json.loads(tr_path.read_text(encoding="utf-8")) if tr_path.exists() else {}
    data = {
        "run": run.name,
        "reviews": [{"review_id": g["review_id"], "asin": g["asin"], "star": int(g["star"]),
                     "brand": brands.get(g["asin"]) or reviews.get(g["review_id"], {}).get("brand", ""),
                     "date": reviews.get(g["review_id"], {}).get("date", ""),
                     "title": g["title"], "body": g["body"],
                     "title_ko": (tr.get(g["review_id"]) or {}).get("title_ko", ""),
                     "body_ko": (tr.get(g["review_id"]) or {}).get("body_ko", "")} for g in gold],
        "topics": [{"id": t["id"], "name_ko": t["name_ko"], "side": t["side"],
                    "definition": str(t.get("definition") or ""),
                    "include": [str(x) for x in (t.get("include") or [])],
                    "exclude": [str(x) for x in (t.get("exclude") or [])],
                    "confusions": str(t.get("confusions") or "").strip(),
                    "sentiment_notes": str(t.get("sentiment_notes") or "").strip(),
                    "examples": [str(e.get("quote") or "") for e in t["examples"] if isinstance(e, dict)]}
                   for t in schema.values()],
        # 스키마 안 영어, 외국어 표현의 한국어 번역(화면 보기용). terms는 모든 주제에 공통
        "gloss": {"terms": tr.get("terms") or {}, "topics": tr.get("topics") or {}},
    }
    payload = json.dumps(data, ensure_ascii=False).replace("</", "<\\/")
    html = SHEET_TEMPLATE.read_text(encoding="utf-8").replace("__RUN__", run.name).replace("__DATA__", payload)
    out = run / "gold" / "gold_tagging.html"
    out.write_text(html, encoding="utf-8")
    n_tr = sum(1 for r in data["reviews"] if r["title_ko"] or r["body_ko"])
    print(f"정답 세트 태깅 화면을 만들었습니다: {out} (리뷰 {len(gold)}개, 주제 {len(schema)}개, 한국어 번역 {n_tr}개)")
    print("  브라우저로 열어 태깅하고, 'gold_tags.jsonl 내보내기'로 받은 파일을 gold/gold_tags.jsonl로 저장해 주세요.")
    return 0


# ---------------------------------------------------------------- score

def score_one(gold, pred, gold_ids):
    g = {(t["review_id"], t["topic"]): t["sentiment"] for t in gold}
    p = {(t["review_id"], t["topic"]): t for t in pred if t["review_id"] in gold_ids}
    tp = set(g) & set(p)
    precision = len(tp) / len(p) if p else 0.0
    recall = len(tp) / len(g) if g else 0.0
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
    same = [k for k in tp if p[k]["sentiment"] == g[k]]
    return {
        "gold_pairs": len(g), "pred_pairs": len(p), "matched_pairs": len(tp),
        "precision": round(precision, 3), "recall": round(recall, 3), "topic_f1": round(f1, 3),
        "sentiment_agreement": round(len(same) / len(tp), 3) if tp else 0.0,
        "missed": [{"review_id": r, "topic": t, "gold_sentiment": g[(r, t)]} for r, t in sorted(set(g) - tp)],
        "extra": [{"review_id": r, "topic": t, "sentiment": p[(r, t)]["sentiment"], "quote": p[(r, t)].get("quote", "")}
                  for r, t in sorted(set(p) - tp)],
        "sentiment_diff": [{"review_id": r, "topic": t, "gold": g[(r, t)], "pred": p[(r, t)]["sentiment"],
                            "quote": p[(r, t)].get("quote", "")} for r, t in sorted(tp) if p[(r, t)]["sentiment"] != g[(r, t)]],
    }


def summary_ko(model, r, f1_min, sent_min):
    """한 줄 요약. 예: sonnet: 주제 F1 0.90(기준 0.80, 통과), 감성 일치 88.6%(기준 90.0%, 1.4%p 모자람)
    모자란 양은 표기한 값끼리 뺀다(리포트에 적힌 숫자와 어긋나지 않게)."""
    f1, f1_min_r = round(r["topic_f1"], 2), round(f1_min, 2)
    sp, smin = round(100 * r["sentiment_agreement"], 1), round(100 * sent_min, 1)
    f1_judge = "통과" if r["topic_f1"] >= f1_min else f"{f1_min_r - f1:.2f} 모자람"
    s_judge = "통과" if r["sentiment_agreement"] >= sent_min else f"{smin - sp:.1f}%p 모자람"
    return (f"{model}: 주제 F1 {f1:.2f}(기준 {f1_min_r:.2f}, {f1_judge}), "
            f"감성 일치 {sp:.1f}%(기준 {smin:.1f}%, {s_judge})")


def score(run, f1_min, sent_min):
    schema = load_schema(run)
    gold_path = run / "gold" / "gold_tags.jsonl"
    if not gold_path.exists():
        die("gold/gold_tags.jsonl이 없습니다. 정답 세트 태깅을 먼저 해 주세요.")
    gold = read_jsonl(gold_path)
    for n, t in enumerate(gold, 1):
        if t.get("topic") not in schema:
            die(f"정답 세트 {n}번째 줄: 승인 스키마에 없는 주제 {t.get('topic')}")
        if t.get("sentiment") not in SENTIMENTS:
            die(f"정답 세트 {n}번째 줄: 감성 값 {t.get('sentiment')}")
    picked_path = run / "gold" / "gold_reviews.csv"
    gold_ids = {t["review_id"] for t in gold}
    if picked_path.exists():
        with open(picked_path, encoding="utf-8-sig", newline="") as f:
            gold_ids |= {r["review_id"] for r in csv.DictReader(f)}
    example_ids = {str(e.get("review_id")) for t in schema.values() for e in t["examples"] if isinstance(e, dict)}
    leaked = sorted(gold_ids & example_ids)

    result = {"scored_at": now_iso(), "gold_reviews": len(gold_ids), "thresholds": {"topic_f1": f1_min, "sentiment": sent_min},
              "judged_model": "sonnet", "gold_used_as_schema_example": leaked, "models": {}}
    # sonnet: 전체 태깅 뒤에는 04_tags.jsonl(리포트가 쓰는 태그), 시험 태깅 때는 gold 묶음 태그(04_tags_sonnet_gold.jsonl)
    sonnet_file = next((n for n in ("04_tags.jsonl", "04_tags_sonnet_gold.jsonl") if (run / n).exists()), None)
    if sonnet_file is None:
        die("04_tags.jsonl도 04_tags_sonnet_gold.jsonl도 없습니다. audit_quotes.py tags --model sonnet을 먼저 통과시켜 주세요.")
    result["sonnet_source"] = sonnet_file
    for model, name in (("sonnet", sonnet_file), ("top", "04_tags_top_gold.jsonl")):
        if (run / name).exists():
            result["models"][model] = score_one(gold, read_jsonl(run / name), gold_ids)
    judged = result["models"]["sonnet"]
    result["status"] = "PASS" if judged["topic_f1"] >= f1_min and judged["sentiment_agreement"] >= sent_min else "FAIL"
    for model, r in result["models"].items():
        r["summary_ko"] = summary_ko(model, r, f1_min, sent_min)
    result["summary_ko"] = [r["summary_ko"] for r in result["models"].values()]
    write_json(run / "04_gold_eval.json", result)
    (run / "04_gold_eval.md").write_text(render(result, schema), encoding="utf-8")

    print(f"정답 세트 채점: {result['status']}  (판정은 리포트에 쓰는 sonnet 기준, sonnet 태그 {sonnet_file}. "
          f"리뷰 {len(gold_ids)}개, 정답 태그 {judged['gold_pairs']}개)")
    for model, r in result["models"].items():
        print(f"  {r['summary_ko']}")
        print(f"    정밀도 {r['precision']:.2f}, 재현율 {r['recall']:.2f}, "
              f"빠짐 {len(r['missed'])}, 더함 {len(r['extra'])}, 감성 다름 {len(r['sentiment_diff'])}")
    if leaked:
        print(f"  주의: 정답 세트 리뷰가 스키마 예시로 쓰였습니다: {', '.join(leaked)}")
    print("  불일치 목록: 04_gold_eval.md")
    return 0 if result["status"] == "PASS" else 1


def render(result, schema):
    name = {k: v["name_ko"] for k, v in schema.items()}
    lines = ["# 정답 세트 불일치 목록", "",
             f"정답 세트 리뷰 {result['gold_reviews']}개. 기준: 주제 F1 {result['thresholds']['topic_f1']}, "
             f"감성 일치 {result['thresholds']['sentiment']:.0%}. 판정(sonnet, 리포트가 쓰는 태그): {result['status']}", ""]
    for model, r in result["models"].items():
        lines += [f"## {model}", "", r["summary_ko"], "",
                  f"정밀도 {r['precision']:.2f}, 재현율 {r['recall']:.2f}", "",
                  "| 종류 | review_id | 주제 | 정답 | 기계 | 기계 인용 |", "|---|---|---|---|---|---|"]
        lines += [f"| 빠짐 | {x['review_id']} | {name.get(x['topic'], x['topic'])} | {x['gold_sentiment']} | - | - |" for x in r["missed"]]
        lines += [f"| 더함 | {x['review_id']} | {name.get(x['topic'], x['topic'])} | - | {x['sentiment']} | {x['quote'][:60]} |" for x in r["extra"]]
        lines += [f"| 감성 다름 | {x['review_id']} | {name.get(x['topic'], x['topic'])} | {x['gold']} | {x['pred']} | {x['quote'][:60]} |"
                  for x in r["sentiment_diff"]]
        lines.append("")
    lines.append("줄마다 기계가 틀렸는지, 정답 태깅이 틀렸는지, 스키마 정의가 애매한지 적어 두면 스키마를 고칠 때 씁니다.")
    return "\n".join(lines) + "\n"


# ---------------------------------------------------------------- gold 형식

def check_gold(run):
    schema = load_schema(run)
    picked_path = run / "gold" / "gold_reviews.csv"
    gold_path = run / "gold" / "gold_tags.jsonl"
    if not picked_path.exists():
        die("gold/gold_reviews.csv가 없습니다. eval_gold.py pick을 먼저 돌려 주세요.")
    if not gold_path.exists():
        die("gold/gold_tags.jsonl이 없습니다.")
    with open(picked_path, encoding="utf-8-sig", newline="") as f:
        picked = [r["review_id"] for r in csv.DictReader(f)]
    errors, seen = [], set()
    tags = read_jsonl(gold_path, errors)
    for n, t in enumerate(tags, 1):
        rid, topic, sent = t.get("review_id"), t.get("topic"), t.get("sentiment")
        if rid not in picked:
            errors.append(f"{n}번째 줄: {rid}는 정답 세트 리뷰가 아닙니다.")
        if topic not in schema:
            errors.append(f"{n}번째 줄: 승인 스키마에 없는 주제 {topic}")
        if sent not in SENTIMENTS:
            errors.append(f"{n}번째 줄: 감성 값 {sent}(positive, negative, mixed, neutral 중 하나)")
        if (rid, topic) in seen:
            errors.append(f"{n}번째 줄: {rid}에 {topic}가 두 번 있습니다.")
        seen.add((rid, topic))
    empty = [rid for rid in picked if rid not in {k[0] for k in seen}]
    print(f"정답 세트 형식 검사: {'FAIL' if errors else 'PASS'}  (리뷰 {len(picked)}개, 태그 {len(tags)}개)")
    for e in errors:
        print(f"  오류: {e}")
    if empty:
        print(f"  주의: 태그가 없는 정답 세트 리뷰 {', '.join(empty)}. 정말 해당 주제가 없으면 그대로 둡니다.")
    return 1 if errors else 0


# ---------------------------------------------------------------- 표본 감사

def sentiment_quotas(counts, k, neg_min):
    """감성별 개수 counts에서 k개를 비율대로 나눈다(큰 나머지 방식). 부정은 neg_min개 이상."""
    total = sum(counts.values())
    raw = {s: k * c / total for s, c in counts.items()}
    q = {s: int(v) for s, v in raw.items()}
    for s in sorted(raw, key=lambda s: (-(raw[s] - q[s]), s))[:k - sum(q.values())]:
        q[s] += 1
    need = min(neg_min, counts.get("negative", 0)) - q.get("negative", 0)
    while need > 0:
        donor = max((s for s in q if s != "negative" and q[s] > 0), key=lambda s: (q[s], s), default=None)
        if donor is None:
            break
        q[donor] -= 1
        q["negative"] += 1
        need -= 1
    return q


def gold_ids_of(run):
    """정답 세트 리뷰 id(스크립트만 읽는다)"""
    p = run / "gold" / "gold_reviews.csv"
    if not p.exists():
        return set()
    with open(p, encoding="utf-8-sig", newline="") as f:
        return {r["review_id"] for r in csv.DictReader(f)}


def audit_sample(run, n_total, neg_min=3):
    gold = gold_ids_of(run)
    tags = [t for t in read_jsonl(run / "04_tags.jsonl") if t["review_id"] not in gold]
    reviews = load_csv_or_die(run / "02_reviews.csv", REVIEW_COLS)
    asin_of = {r["review_id"]: r["asin"] for r in reviews}
    order = {r["review_id"]: i for i, r in enumerate(reviews)}
    by_asin = defaultdict(list)
    for t in tags:
        by_asin[asin_of[t["review_id"]]].append(t)
    asins = sorted(by_asin)
    per_asin = n_total // len(asins) if asins else 0
    rng = seeded(run, "audit_sample")
    sample, report = [], {}
    for a in asins:
        ts = sorted(by_asin[a], key=lambda t: (order[t["review_id"]], t["topic"]))
        if len(ts) <= per_asin:
            chosen = ts
        else:
            counts = Counter(t["sentiment"] for t in ts)
            q = sentiment_quotas(counts, per_asin, neg_min)
            chosen = []
            for s in SENTIMENTS:
                pool = [t for t in ts if t["sentiment"] == s]
                chosen += rng.sample(pool, q.get(s, 0))
        sample += chosen
        report[a] = Counter(t["sentiment"] for t in chosen)
    sample.sort(key=lambda t: (order[t["review_id"]], t["topic"]))
    write_jsonl(run / "04_audit_sample.jsonl", sample)
    print(f"감사 표본 {len(sample)}개를 04_audit_sample.jsonl에 적었습니다(정답 세트를 뺀 태그 {len(tags)}개 중, ASIN마다 {per_asin}개).")
    for a in asins:
        print(f"  {a}: {sum(report[a].values())}개 (" + ", ".join(f"{s} {report[a][s]}" for s in SENTIMENTS) + ")")
    return 0


def audit(run, max_fail):
    data = load_yaml(run / "04_tag_audit.yaml") or {}
    a = data.get("audit") if isinstance(data, dict) else None
    if not isinstance(a, dict):
        die("04_tag_audit.yaml 맨 위에 audit: 항목이 없습니다. evidence-auditor가 돌려준 YAML을 그대로 저장해 주세요.")
    warns = []
    sample_path = run / "04_audit_sample.jsonl"
    if sample_path.exists():
        tags = read_jsonl(sample_path)
    else:
        tags = read_jsonl(run / "04_tags.jsonl")
        warns.append("04_audit_sample.jsonl이 없어 04_tags.jsonl 전부를 표본으로 셉니다(audit-sample 먼저).")
    gold = gold_ids_of(run)
    gold_tags = [t for t in tags if t["review_id"] in gold]
    if gold_tags:
        warns.append(f"감사 표본에 정답 세트 리뷰의 태그 {len(gold_tags)}개(리뷰 {len({t['review_id'] for t in gold_tags})}개)가 있어 빼고 셉니다.")
        tags = [t for t in tags if t["review_id"] not in gold]
    asin_of = {r["review_id"]: r["asin"] for r in load_csv_or_die(run / "02_reviews.csv", REVIEW_COLS)}
    batch_of = {}
    if (run / "04_batches.json").exists():
        for b in json.loads((run / "04_batches.json").read_text(encoding="utf-8"))["batches"]:
            if "sonnet" in b.get("models", []) and b.get("merge", True):
                for rid in b["review_ids"]:
                    batch_of[rid] = b["batch_id"]
    tag_keys = {(t["review_id"], t["topic"]) for t in tags}
    sample_ids = {t["review_id"] for t in tags}
    counts, fail_by_asin, retry, batches = Counter(), Counter(), set(), set()
    for n, f in enumerate(a.get("findings") or [], 1):
        f = f if isinstance(f, dict) else {}
        st = str(f.get("status", "")).upper()
        key = (str(f.get("review_id", "")), str(f.get("topic", "")))
        if st not in ("FAIL", "UNVERIFIED", "PASS"):
            warns.append(f"findings {n}번째: status가 {st or '빈 값'}입니다.")
            continue
        if key[0] in gold:
            continue
        if key not in tag_keys:
            warns.append(f"findings {n}번째: 감사 표본에 없는 태그 {key[0]} / {key[1]}")
            continue
        counts[st] += 1
        if st == "FAIL":
            fail_by_asin[asin_of.get(key[0], "?")] += 1
            retry.add(asin_of.get(key[0], "?"))
            batches.add(batch_of.get(key[0], "?"))
    missed = []
    for m in (a.get("missed") or []):
        if not isinstance(m, dict):
            continue
        rid = str(m.get("review_id"))
        if rid in gold:
            continue
        if rid not in sample_ids:
            warns.append(f"missed {rid}: 감사 표본에 없는 리뷰라 세지 않습니다.")
            continue
        missed.append(m)
        retry.add(asin_of.get(rid, "?"))
        batches.add(batch_of.get(rid, "?"))
    checked = a.get("checked")
    if checked != len(tags) + len(gold_tags):
        warns.append(f"감사관이 읽은 태그 수(checked {checked})가 감사 표본 {len(tags)}개와 다릅니다.")
    rate = counts["FAIL"] / len(tags) if tags else 0.0
    cons_n = len(tags) + len(missed)
    cons = (counts["FAIL"] + counts["UNVERIFIED"] + len(missed)) / cons_n if cons_n else 0.0
    per_asin_n = Counter(asin_of[t["review_id"]] for t in tags)
    by_asin = {x: {"sample": per_asin_n[x], "fail": fail_by_asin[x],
                   "fail_rate": round(fail_by_asin[x] / per_asin_n[x], 3) if per_asin_n[x] else 0.0}
               for x in sorted(per_asin_n)}
    if not tags:
        status = "EMPTY"
    elif checked != len(tags) + len(gold_tags):
        status = "INCOMPLETE"       # 감사자가 표본을 다 보지 않았으면 PASS로 넘기지 않음
    else:
        status = "PASS" if rate <= max_fail else "FAIL"
    out = {"checked_at": now_iso(), "status": status, "sample_tags": len(tags), "auditor_checked": checked,
           "excluded_gold_tags": len(gold_tags),
           "fail": counts["FAIL"], "unverified": counts["UNVERIFIED"], "missed": len(missed),
           "fail_rate": round(rate, 3), "conservative_rate": round(cons, 3),
           "conservative_rule": "(FAIL + UNVERIFIED + missed) / (표본 태그 + missed)", "max_fail_rate": max_fail, "by_asin": by_asin,
           "asins_with_findings": sorted(retry - {"?"}), "batches_with_findings": sorted(batches - {"?"}),
           "warnings": warns}
    write_json(run / "04_tag_audit_summary.json", out)
    print(f"태그 검수 집계: {status}  (감사 표본 {len(tags)}개 중 FAIL {counts['FAIL']}개 = {rate:.1%}, "
          f"기준 {max_fail:.0%} 이하. UNVERIFIED {counts['UNVERIFIED']}개, 빠진 태그 {len(missed)}개, "
          f"판정 못 받은 것을 FAIL로 센 보수적 비율 {cons:.1%})")
    for x, v in by_asin.items():
        print(f"  {x}: 표본 {v['sample']}개, FAIL {v['fail']}개({v['fail_rate']:.1%})")
    if out["batches_with_findings"]:
        print(f"  다시 태깅할 묶음: {', '.join(out['batches_with_findings'])}")
    for w in warns:
        print(f"  주의: {w}")
    return 0 if status == "PASS" else 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("mode", choices=["pick", "sheet", "gold", "score", "audit-sample", "audit"])
    ap.add_argument("run", nargs="?")
    ap.add_argument("--per-asin", type=int, default=5)
    ap.add_argument("--min-chars", type=int, default=40)
    ap.add_argument("--sample-per-asin", type=int, default=25)
    ap.add_argument("--f1", type=float, default=0.80)
    ap.add_argument("--sentiment", type=float, default=0.90)
    ap.add_argument("--n", type=int, default=150, help="audit-sample 전체 표본 태그 수(ASIN마다 n / ASIN 수)")
    ap.add_argument("--max-fail", type=float, default=0.05)
    ap.add_argument("--translations", default=None, help="sheet: 한국어 번역 JSON 경로(기본 gold/gold_translations_ko.json)")
    args = ap.parse_args()
    run = resolve_run(args.run)
    if args.mode == "pick":
        sys.exit(pick(run, args.per_asin, args.min_chars, args.sample_per_asin))
    if args.mode == "sheet":
        sys.exit(sheet(run, args.translations))
    if args.mode == "gold":
        sys.exit(check_gold(run))
    if args.mode == "score":
        sys.exit(score(run, args.f1, args.sentiment))
    if args.mode == "audit-sample":
        sys.exit(audit_sample(run, args.n))
    sys.exit(audit(run, args.max_fail))


if __name__ == "__main__":
    main()
