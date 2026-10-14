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

  python scripts/eval_gold.py sheet [회차] [--schema 03_schema_draft.yaml]
    담당자가 정답 세트를 태깅하는 화면 gold/gold_tagging.html을 만든다(한 파일, 외부 라이브러리 없음).
    2026-10-10부터: 승인본(03_schema_approved.yaml)이 없으면 초안(03_schema_draft.yaml)으로 만들고, 화면 맨 위에
    "스키마 확인"(주제마다 승인, 고침, 빼기와 메모)을 함께 넣는다. 스키마 승인과 정답 세트 태깅을 한 화면에서 한다.
    "스키마 확인 내보내기"로 받은 파일은 runs/<회차>/03_schema_review.json으로 저장한다.
    필수 주제(id나 common_id가 overall, performance인 주제)는 리뷰마다 값을 골라야 "다 봤음"이 체크된다
    (overall은 감성 넷 중 하나, 효과 주제는 감성 또는 "언급 없음"). H1에서 이 칸을 비워 다시 본 시간(29분)을 없앤다.
    고른 값은 브라우저 localStorage에 저장되고, "gold_tags.jsonl 내보내기"로 내려받아 gold/gold_tags.jsonl로 저장한다.
    태거 결과는 화면에 넣지 않는다.

  python scripts/eval_gold.py schema-approve [회차] [--review 03_schema_review.json] --approved-at <UTC> --approved-by "<누가, 어떻게>"
    한 화면에서 받은 스키마 확인 파일을 읽는다. 모든 주제가 승인이면 03_schema_draft.yaml을 03_schema_approved.yaml로 복사하고
    승인 시각과 승인자를 적는다. 고침이나 빼기가 하나라도 있으면 그 주제와 메모를 찍고 종료 코드 1(메인 세션이 초안을 고쳐 승인본으로 저장).

  python scripts/eval_gold.py gold [회차] [--rename old:new,...] [--drop-unknown]
    --rename: 승인 때 id가 바뀐 주제의 정답 태그 주제를 바꾼다. --drop-unknown: 승인 스키마에 없는 주제(뺀 주제)의 정답 태그를 뺀다.
    둘 다 원래 파일을 gold/gold_tags.before_fix.jsonl로 남기고 바꾼 개수를 찍는다(초안 화면에서 태깅했을 때만 쓴다).
    담당자가 쓴 gold/gold_tags.jsonl의 형식을 본다: 정답 세트 리뷰인지, 승인 스키마의 주제인지,
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

from pipeline_io import (ASIN_COLS, REVIEW_COLS, ROOT, SENTIMENTS, STARS, die, load_config, load_csv_or_die,
                         load_schema, load_yaml, now_iso, read_jsonl, resolve_run, write_json, write_jsonl)

SHEET_TEMPLATE = Path(__file__).resolve().parent / "gold_sheet.html"
GOLD_COLS = ["review_id", "asin", "star", "title", "body"]
# 정답 세트 두 벌(2026-10-13): rules = 규칙을 다듬는 데 쓴 세트(gold/), score = 채점만 하는 세트(gold_score/, 규칙을 만들 때 보지 않음)
GOLD_DIRS = {"rules": "gold", "score": "gold_score"}
GOLD_DIR = "gold"


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


def pick_score(run, per_asin, min_chars):
    """채점용 정답 세트(gold_score/)를 스크립트가 상품과 별점으로 고르게 뽑는다(2026-10-13 담당자 지정).
    - 02_reviews.csv에서 규칙용 정답 세트(gold/), 스키마 표본(03_schema_sample.csv), 스키마 예시 리뷰를 뺀 나머지에서 뽑는다
      (2026-10-14: 스키마를 만든 에이전트가 본 리뷰로 채점하면 점수가 부푼다). 본문 min_chars자 미만은 뺀다.
    - per_asin이 4보다 적으면 남은 별점 4개 중 쓰는 별점도 상품마다 돌린다(앞 별점에 몰리지 않게).
    - 상품마다 per_asin개(기본 4개), 한 상품 안에서는 별점이 겹치지 않게. 상품마다 빠지는 별점을 돌려
      (상품 i는 별점 (i mod 5)+1을 뺌, 상품은 ASIN 순서) 전체로 별점마다 고르게 나오게 한다.
    - 시드는 회차 이름과 "gold_score"로 고정. 시드와 뽑은 목록을 gold_pick_log.json에 남긴다."""
    reviews = load_csv_or_die(run / "02_reviews.csv", REVIEW_COLS)
    asins = sorted({r["asin"] for r in reviews})
    rules = set()
    p = run / GOLD_DIRS["rules"] / "gold_reviews.csv"
    if p.exists():
        with open(p, encoding="utf-8-sig", newline="") as f:
            rules = {r["review_id"] for r in csv.DictReader(f)}
    seen_by_drafter = set()
    sp = run / "03_schema_sample.csv"
    if sp.exists():
        with open(sp, encoding="utf-8-sig", newline="") as f:
            seen_by_drafter = {r["review_id"] for r in csv.DictReader(f)}
    for name in ("03_schema_approved.yaml", "03_schema_draft.yaml"):
        if (run / name).exists():
            seen_by_drafter |= {str(e.get("review_id")) for t in load_schema(run, name).values() for e in t["examples"] if isinstance(e, dict)}
            break
    rules |= seen_by_drafter
    rng = seeded(run, "gold_score")
    chosen_all, short, plan = [], {}, {}
    for i, a in enumerate(asins):
        skip = STARS[i % len(STARS)]
        rest = [s for s in STARS if s != skip]
        stars = sorted((rest[i % len(rest):] + rest[:i % len(rest)])[:per_asin]) if per_asin < len(rest) else rest
        plan[a] = {"skipped_star": skip, "stars": stars}
        for s in stars:
            pool = shuffled([r for r in reviews if r["asin"] == a and int(r["star"]) == s and r["review_id"] not in rules
                             and len(r["body"].strip()) >= min_chars], rng)
            if pool:
                chosen_all.append(pool[0])
            else:
                short.setdefault(a, []).append(s)
        for s in [x for x in STARS if x not in stars]:      # 모자란 만큼 그 상품의 안 쓴 별점에서 채운다(2026-10-14)
            if len(short.get(a, [])) <= sum(1 for r in chosen_all if r["asin"] == a and int(r["star"]) not in stars):
                break
            pool = shuffled([r for r in reviews if r["asin"] == a and int(r["star"]) == s and r["review_id"] not in rules
                             and len(r["body"].strip()) >= min_chars], rng)
            if pool:
                chosen_all.append(pool[0])
                plan[a].setdefault("filled_from", []).append(s)
    out = run / GOLD_DIRS["score"]
    out.mkdir(exist_ok=True)
    write_rows(out / "gold_reviews.csv", GOLD_COLS, chosen_all)
    star_count = Counter(int(r["star"]) for r in chosen_all)
    write_json(out / "gold_pick_log.json", {
        "picked_at": now_iso(), "seed": f"{run.name}:gold_score", "purpose": "채점만(틀린 것을 보고 규칙을 고치지 않음)",
        "method": f"스크립트가 상품과 별점으로 고르게 뽑았다(상품마다 {per_asin}개, 한 상품 안 별점 겹치지 않음, 빠지는 별점을 상품마다 돌림)",
        "criteria": {"per_asin": per_asin, "min_body_chars": min_chars,
                     "excluded": f"규칙용 정답 세트와 스키마 표본과 예시 리뷰 {len(rules)}개(스키마 쪽 {len(seen_by_drafter)}개)"},
        "plan": plan, "star_counts": {str(s): star_count[s] for s in STARS}, "short": short,
        "picked": [{"review_id": r["review_id"], "asin": r["asin"], "star": int(r["star"])} for r in chosen_all]})
    print(f"채점용 정답 세트 {len(chosen_all)}개를 {GOLD_DIRS['score']}/gold_reviews.csv에 적었습니다. "
          f"스크립트가 상품과 별점으로 고르게 뽑았습니다(상품마다 {per_asin}개, 한 상품 안 별점 겹치지 않음, 본문 {min_chars}자 이상, "
          f"규칙용 정답 세트와 스키마 표본과 예시 {len(rules)}개 뺌, 시드 {run.name}:gold_score).")
    print(star_table(chosen_all, asins))
    if short:
        print("  주의: 그 별점에 뽑을 리뷰가 없음 " + ", ".join(f"{a} {v}" for a, v in short.items()))
    return 0


# ---------------------------------------------------------------- sheet

REQUIRED_COMMON = ("overall", "performance")    # 정답 세트 화면에서 리뷰마다 꼭 고르는 주제(id나 common_id)


def required_topics(schema):
    return [tid for tid, t in schema.items() if tid in REQUIRED_COMMON or str(t.get("common_id") or "") in REQUIRED_COMMON]


def sheet_order(schema, required):
    """정답 화면의 주제 칸 순서(2026-10-14 담당자 결정, 품목과 상관없음): 필수 주제를 맨 앞에, 그다음 제품 주제, 브랜드 주제.
    같은 묶음 안에서는 스키마 표본에서 근거가 많은 주제(evidence_count)부터, 같으면 스키마 순서."""
    idx = {tid: i for i, tid in enumerate(schema)}
    return sorted(schema.values(), key=lambda t: (t["id"] not in required, t.get("side") != "P",
                                                  -(t.get("evidence_count") or 0), idx[t["id"]]))


def sheet(run, translations=None, schema_name=None):
    if schema_name is None:
        schema_name = "03_schema_approved.yaml" if (run / "03_schema_approved.yaml").exists() else "03_schema_draft.yaml"
    if not (run / schema_name).exists():
        die(f"{schema_name}이(가) 없습니다. 스키마 초안이나 승인본이 있어야 화면을 만듭니다.")
    schema = load_schema(run, schema_name)
    draft_mode = schema_name != "03_schema_approved.yaml"
    required = required_topics(schema)
    picked = run / GOLD_DIR / "gold_reviews.csv"
    if not picked.exists():
        die("gold/gold_reviews.csv가 없습니다. eval_gold.py pick을 먼저 돌려 주세요.")
    with open(picked, encoding="utf-8-sig", newline="") as f:
        gold = list(csv.DictReader(f))
    reviews = {r["review_id"]: r for r in load_csv_or_die(run / "02_reviews.csv", REVIEW_COLS)}
    brands = {r["asin"]: r["brand"] for r in load_csv_or_die(run / "01_asins.csv", ASIN_COLS)}
    # 있으면 원문 아래에 한국어 번역을 참고용으로 보여 준다(태깅은 원문 기준, 리포트와 인용 검사에는 쓰지 않음)
    # 번역 파일은 gold 폴더(기본)나 --translations로 준 경로(gold 폴더 쓰기가 막힌 세션에서 메인 세션이 쓴 파일)
    tr_path = Path(translations) if translations else run / GOLD_DIR / "gold_translations_ko.json"
    tr = json.loads(tr_path.read_text(encoding="utf-8")) if tr_path.exists() else {}
    rules_tr = run / GOLD_DIRS["rules"] / "gold_translations_ko.json"
    if GOLD_DIR != GOLD_DIRS["rules"] and not (tr.get("terms") or tr.get("topics")) and rules_tr.exists():
        base = json.loads(rules_tr.read_text(encoding="utf-8"))      # 스키마 용어 번역은 규칙용 세트 것을 같이 씀(리뷰 번역은 섞지 않음)
        tr = {**tr, "terms": base.get("terms") or {}, "topics": base.get("topics") or {}}
    data = {
        "run": run.name,
        "store_key": run.name if GOLD_DIR == GOLD_DIRS["rules"] else f"{run.name}:{GOLD_DIR}:" + hashlib.sha256(
            ",".join(g["review_id"] for g in gold).encode("utf-8")).hexdigest()[:8],   # 뽑은 목록이 바뀌면 브라우저 저장도 새로
        "gold_dir": GOLD_DIR,
        # 화면 위에 늘 띄우는 것: 감성 판정 순서(config/topics_common.yaml tagging_rule)와 주제 설명
        "rules_panel": {"sentiment_order": [str(x) for x in (load_yaml(ROOT / "config" / "topics_common.yaml") or {}).get("tagging_rule") or []],
                        "topics": [{"name_ko": t["name_ko"], "definition": str(t.get("definition") or "")} for t in schema.values()]},
        "schema_file": schema_name,
        "schema_mode": "draft" if draft_mode else "approved",
        "required": required,
        "reviews": [{"review_id": g["review_id"], "asin": g["asin"], "star": int(g["star"]),
                     "brand": brands.get(g["asin"]) or reviews.get(g["review_id"], {}).get("brand", ""),
                     "date": reviews.get(g["review_id"], {}).get("date", ""),
                     "title": g["title"], "body": g["body"],
                     "title_ko": (tr.get(g["review_id"]) or {}).get("title_ko", ""),
                     "body_ko": (tr.get(g["review_id"]) or {}).get("body_ko", "")} for g in gold],
        "topics": [{"id": t["id"], "name_ko": t["name_ko"], "side": t["side"],
                    "common_id": str(t.get("common_id") or ""), "evidence_count": t.get("evidence_count"),
                    "definition": str(t.get("definition") or ""),
                    "include": [str(x) for x in (t.get("include") or [])],
                    "exclude": [str(x) for x in (t.get("exclude") or [])],
                    "confusions": str(t.get("confusions") or "").strip(),
                    "sentiment_notes": str(t.get("sentiment_notes") or "").strip(),
                    "examples": [str(e.get("quote") or "") for e in t["examples"] if isinstance(e, dict)]}
                   for t in sheet_order(schema, required)],
        # 스키마 안 영어, 외국어 표현의 한국어 번역(화면 보기용). terms는 모든 주제에 공통
        "gloss": {"terms": tr.get("terms") or {}, "topics": tr.get("topics") or {}},
    }
    payload = json.dumps(data, ensure_ascii=False).replace("</", "<\\/")
    html = SHEET_TEMPLATE.read_text(encoding="utf-8").replace("__RUN__", run.name).replace("__GOLDDIR__", GOLD_DIR)
    html = html.replace("__TITLE__", "정답 세트 태깅" if GOLD_DIR == GOLD_DIRS["rules"] else "채점용 정답 세트 태깅").replace("__DATA__", payload)
    out = run / GOLD_DIR / "gold_tagging.html"
    out.write_text(html, encoding="utf-8")
    n_tr = sum(1 for r in data["reviews"] if r["title_ko"] or r["body_ko"])
    print(f"정답 세트 태깅 화면을 만들었습니다: {out} (리뷰 {len(gold)}개, 주제 {len(schema)}개, 한국어 번역 {n_tr}개, "
          f"기준 {schema_name}, 필수 주제 {', '.join(required) or '없음'})")
    print(f"  브라우저로 열어 태깅하고, 'gold_tags.jsonl 내보내기'로 받은 파일을 {GOLD_DIR}/gold_tags.jsonl로 저장해 주세요.")
    if draft_mode:
        print("  초안 화면입니다. 맨 위 '스키마 확인'을 마치고 '스키마 확인 내보내기'로 받은 파일을 "
              f"runs/{run.name}/03_schema_review.json으로 저장해 주세요.")
    return 0


def schema_approve(run, review_name, approved_at, approved_by):
    """한 화면의 스키마 확인 파일로 승인본을 만든다. 고침이나 빼기가 있으면 만들지 않고 목록을 찍는다."""
    draft_path, review_path = run / "03_schema_draft.yaml", run / review_name
    if not draft_path.exists():
        die("03_schema_draft.yaml이 없습니다.")
    if not review_path.exists():
        die(f"{review_name}이(가) 없습니다. 화면의 '스키마 확인 내보내기'로 받은 파일을 저장해 주세요.")
    if not approved_at or not approved_by:
        die("--approved-at과 --approved-by를 함께 주세요.")
    draft = load_schema(run, "03_schema_draft.yaml")
    rv = json.loads(review_path.read_text(encoding="utf-8"))
    dec = {str(x.get("id")): x for x in rv.get("topics") or []}
    missing = [t for t in draft if t not in dec]
    unknown = [t for t in dec if t not in draft]
    if missing or unknown:
        die(f"스키마 확인 파일이 초안과 맞지 않습니다. 결정이 없는 주제: {', '.join(missing) or '없음'}, "
            f"초안에 없는 주제: {', '.join(unknown) or '없음'}(다른 초안으로 만든 화면일 수 있음).")
    changes = [(t, dec[t].get("decision"), str(dec[t].get("note") or "").strip()) for t in draft
               if dec[t].get("decision") != "approve" or str(dec[t].get("note") or "").strip()]
    if changes:
        print(f"스키마 확인: 고칠 곳 {len(changes)}개. 승인본을 만들지 않았습니다(초안을 고쳐 03_schema_approved.yaml로 저장).")
        for t, d, note in changes:
            print(f"  {t}: {({'edit': '고침', 'drop': '빼기', 'approve': '승인(메모 있음)'}).get(d, d)} {note}")
        return 1
    text = draft_path.read_text(encoding="utf-8")
    head = (f"# 담당자 승인: {approved_at}, {approved_by}. 한 화면 스키마 확인({review_name})에서 모든 주제 승인, 초안 그대로.\n"
            f"approved_at: \"{approved_at}\"\napproved_by: \"{approved_by}\"\n")
    (run / "03_schema_approved.yaml").write_text(head + text, encoding="utf-8")
    print(f"모든 주제 {len(draft)}개 승인: 03_schema_draft.yaml을 03_schema_approved.yaml로 복사했습니다. "
          "다음: check_inputs.py --schema, eval_gold.py gold")
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
    # 방향 일치: 정답과 모델 어느 쪽도 mixed가 아닌 짝에서 감성이 같은 비율(긍정, 부정, 중립의 방향)
    # mixed 일치: 어느 한쪽이라도 mixed인 짝에서 둘 다 mixed인 비율(엇갈림 경계)
    plain = [k for k in tp if "mixed" not in (g[k], p[k]["sentiment"])]
    mixed = [k for k in tp if "mixed" in (g[k], p[k]["sentiment"])]
    both_mixed = [k for k in mixed if g[k] == p[k]["sentiment"]]
    return {
        "gold_pairs": len(g), "pred_pairs": len(p), "matched_pairs": len(tp),
        "precision": round(precision, 3), "recall": round(recall, 3), "topic_f1": round(f1, 3),
        "sentiment_agreement": round(len(same) / len(tp), 3) if tp else 0.0,
        "direction_pairs": len(plain), "direction_same": sum(1 for k in plain if p[k]["sentiment"] == g[k]),
        "direction_agreement": round(sum(1 for k in plain if p[k]["sentiment"] == g[k]) / len(plain), 3) if plain else 0.0,
        "mixed_pairs": len(mixed), "mixed_same": len(both_mixed),
        "mixed_agreement": round(len(both_mixed) / len(mixed), 3) if mixed else None,
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
    dp = round(100 * r["direction_agreement"], 1)
    d_judge = "통과" if r["direction_agreement"] >= sent_min else f"{smin - dp:.1f}%p 모자람"
    mx = "-" if r["mixed_agreement"] is None else f"{100 * r['mixed_agreement']:.1f}%"
    return (f"{model}: 주제 F1 {f1:.2f}(기준 {f1_min_r:.2f}, {f1_judge}), "
            f"감성 방향 일치 {dp:.1f}%(기준 {smin:.1f}%, {d_judge}), "
            f"mixed 일치 {mx}(짝 {r['mixed_pairs']}개, 기준 없음), 감성 전체 일치 {sp:.1f}%")


def score(run, f1_min, sent_min, tags=None):
    schema = load_schema(run)
    gold_path = run / GOLD_DIR / "gold_tags.jsonl"
    if not gold_path.exists():
        die("gold/gold_tags.jsonl이 없습니다. 정답 세트 태깅을 먼저 해 주세요.")
    gold = read_jsonl(gold_path)
    for n, t in enumerate(gold, 1):
        if t.get("topic") not in schema:
            die(f"정답 세트 {n}번째 줄: 승인 스키마에 없는 주제 {t.get('topic')}")
        if t.get("sentiment") not in SENTIMENTS:
            die(f"정답 세트 {n}번째 줄: 감성 값 {t.get('sentiment')}")
    picked_path = run / GOLD_DIR / "gold_reviews.csv"
    gold_ids = {t["review_id"] for t in gold}
    if picked_path.exists():
        with open(picked_path, encoding="utf-8-sig", newline="") as f:
            gold_ids |= {r["review_id"] for r in csv.DictReader(f)}
    example_ids = {str(e.get("review_id")) for t in schema.values() for e in t["examples"] if isinstance(e, dict)}
    leaked = sorted(gold_ids & example_ids)

    result = {"scored_at": now_iso(), "gold_reviews": len(gold_ids), "thresholds": {"topic_f1": f1_min, "sentiment": sent_min},
              "judged_model": "sonnet", "gold_used_as_schema_example": leaked, "models": {}}
    # sonnet: 전체 태깅 뒤에는 04_tags.jsonl(리포트가 쓰는 태그), 시험 태깅 때는 gold 묶음 태그(04_tags_sonnet_gold.jsonl)
    sonnet_file = tags or next((n for n in ("04_tags.jsonl", "04_tags_sonnet_gold.jsonl") if (run / n).exists()), None)
    if sonnet_file is None:
        die("04_tags.jsonl도 04_tags_sonnet_gold.jsonl도 없습니다. audit_quotes.py tags --model sonnet을 먼저 통과시켜 주세요.")
    result["sonnet_source"] = sonnet_file
    # --tags로 다시 태깅한 파일을 주면 그 파일로 판정하고, 리포트 태그(04_tags.jsonl)는 before로 나란히 적는다
    for model, name in (("sonnet", sonnet_file), ("before", "04_tags.jsonl" if tags else None), ("top", "04_tags_top_gold.jsonl")):
        if name is None:
            continue
        if model == "top" and GOLD_DIR != "gold":
            continue                                            # 상위 모델 비교 태그는 규칙용 세트에만 있음
        if (run / name).exists():
            result["models"][model] = score_one(gold, read_jsonl(run / name), gold_ids)
    judged = result["models"]["sonnet"]
    result["status"] = "PASS" if judged["topic_f1"] >= f1_min and judged["direction_agreement"] >= sent_min else "FAIL"
    for model, r in result["models"].items():
        r["summary_ko"] = summary_ko(model, r, f1_min, sent_min)
    result["summary_ko"] = [r["summary_ko"] for r in result["models"].values()]
    out_name = "04_gold_eval" if GOLD_DIR == "gold" else "04_gold_eval_score"   # 채점용 세트는 리포트 숫자(04_gold_eval.json)를 바꾸지 않음
    result["gold_set"] = GOLD_DIR
    write_json(run / f"{out_name}.json", result)
    (run / f"{out_name}.md").write_text(render(result, schema), encoding="utf-8")

    print(f"정답 세트 채점: {result['status']}  (판정은 리포트에 쓰는 sonnet 기준, sonnet 태그 {sonnet_file}. "
          f"리뷰 {len(gold_ids)}개, 정답 태그 {judged['gold_pairs']}개)")
    for model, r in result["models"].items():
        print(f"  {r['summary_ko']}")
        print(f"    정밀도 {r['precision']:.2f}, 재현율 {r['recall']:.2f}, "
              f"빠짐 {len(r['missed'])}, 더함 {len(r['extra'])}, 감성 다름 {len(r['sentiment_diff'])}")
    if leaked:
        print(f"  주의: 정답 세트 리뷰가 스키마 예시로 쓰였습니다: {', '.join(leaked)}")
    print(f"  불일치 목록: {out_name}.md")
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

def fix_gold_topics(gold_path, schema, rename, drop_unknown):
    """초안 화면으로 태깅한 정답 태그를 승인 스키마에 맞춘다(id 바꾸기, 뺀 주제 지우기). 원래 파일은 남긴다."""
    errors = []
    tags = read_jsonl(gold_path, errors)
    if errors:
        die("gold_tags.jsonl을 읽지 못했습니다: " + "; ".join(errors[:3]))
    bad = [f"{o}->{n}" for o, n in rename.items() if n not in schema]
    if bad:
        die(f"--rename의 새 주제가 승인 스키마에 없습니다: {', '.join(bad)}")
    out, renamed, dropped = [], 0, Counter()
    for t in tags:
        if t.get("topic") in rename:
            t = {**t, "topic": rename[t["topic"]]}
            renamed += 1
        if drop_unknown and t.get("topic") not in schema:
            dropped[t.get("topic")] += 1
            continue
        out.append(t)
    backup = gold_path.with_name("gold_tags.before_fix.jsonl")
    if not backup.exists():
        backup.write_text(gold_path.read_text(encoding="utf-8"), encoding="utf-8")
    write_jsonl(gold_path, out)
    print(f"정답 태그를 승인 스키마에 맞췄습니다: 주제 이름 바꿈 {renamed}개, 뺀 주제의 태그 지움 "
          f"{sum(dropped.values())}개({', '.join(f'{k} {v}' for k, v in dropped.items()) or '없음'}). 원래 파일: {backup.name}")


def check_gold(run, rename=None, drop_unknown=False):
    schema = load_schema(run)
    picked_path = run / GOLD_DIR / "gold_reviews.csv"
    gold_path = run / GOLD_DIR / "gold_tags.jsonl"
    if not picked_path.exists():
        die("gold/gold_reviews.csv가 없습니다. eval_gold.py pick을 먼저 돌려 주세요.")
    if not gold_path.exists():
        die("gold/gold_tags.jsonl이 없습니다.")
    if rename or drop_unknown:
        fix_gold_topics(gold_path, schema, rename or {}, drop_unknown)
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
    ov_ids = [t for t in schema if t == "overall" or schema[t].get("common_id") == "overall"]
    no_ov = [rid for rid in picked if ov_ids and not any((rid, t) in seen for t in ov_ids)]
    if no_ov:
        print(f"  주의: 전체 만족도 태그가 없는 정답 세트 리뷰 {len(no_ov)}개: {', '.join(no_ov[:10])}(태거는 모든 리뷰에 단다)")
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
    """정답 세트 리뷰 id, 두 벌 모두(스크립트만 읽는다)"""
    ids = set()
    for d in GOLD_DIRS.values():
        p = run / d / "gold_reviews.csv"
        if p.exists():
            with open(p, encoding="utf-8-sig", newline="") as f:
                ids |= {r["review_id"] for r in csv.DictReader(f)}
    return ids


def audit_sample(run, n_total, neg_min=3, parts=2):
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
    for old in list(run.glob("04_audit_sample_p*.jsonl")) + list(run.glob("04_tag_audit_p*.yaml")):
        old.unlink()                    # 옛 반쪽 판정이 새 표본과 섞이지 않게
    if parts > 1:
        # 감사자마다 반쪽(2026-10-14 담당자 결정). 빠진 태그(missed)를 리뷰 단위로 보므로 한 리뷰의 태그는 한 반쪽에만 넣는다.
        # 리뷰를 표본 순서(ASIN 순)대로 태그가 적은 반쪽에 넣어 수와 ASIN이 고르게 한다.
        halves = [[] for _ in range(parts)]
        by_review = defaultdict(list)
        for t in sample:
            by_review[t["review_id"]].append(t)
        for rid in sorted(by_review, key=lambda r: order[r]):
            min(halves, key=len).extend(by_review[rid])
        for k, h in enumerate(halves, 1):
            write_jsonl(run / f"04_audit_sample_p{k}.jsonl", h)
        print(f"  감사자 {parts}명 몫(리뷰 단위로 나눔): " + ", ".join(f"p{k} {len(h)}개" for k, h in enumerate(halves, 1)))
    return 0


def merge_tag_audit_parts(run, sample):
    """반쪽 판정을 04_tag_audit.yaml로 합친다. 반쪽 표본을 합치면 전체 표본과 정확히 같아야 하고(빠짐, 겹침 없음),
    반쪽마다 checked가 그 반쪽 수와 같고, 판정과 빠진 태그는 자기 반쪽 것이어야 한다. 반쪽 파일이 없으면 None."""
    part_files = sorted(run.glob("04_audit_sample_p*.jsonl"))
    if not part_files:
        return None
    key = lambda t: (str(t.get("review_id", "")), str(t.get("topic", "")))  # noqa: E731
    seen, problems, parts, findings, missed = {}, [], [], [], []
    for pf in part_files:
        tag = pf.stem.rsplit("_", 1)[1]
        half = read_jsonl(pf)
        for t in half:
            seen.setdefault(key(t), []).append(tag)
        yp = run / f"04_tag_audit_{tag}.yaml"
        if not yp.exists():
            die(f"{yp.name}이 없습니다. 반쪽 감사가 다 끝난 뒤 합칩니다.")
        a = ((load_yaml(yp) or {}).get("audit") or {})
        keys, rids = {key(t) for t in half}, {t["review_id"] for t in half}
        if a.get("checked") != len(half):
            problems.append(f"{tag}: 감사자가 {a.get('checked')}개를 봤다고 적었지만 반쪽 표본은 {len(half)}개")
        fs = [f for f in a.get("findings") or [] if isinstance(f, dict)]
        own = [f for f in fs if key(f) in keys]
        if len(own) != len(fs):
            problems.append(f"{tag}: 자기 반쪽에 없는 태그를 판정함 {len(fs) - len(own)}개")
        ms = [m for m in a.get("missed") or [] if isinstance(m, dict)]
        own_m = [m for m in ms if str(m.get("review_id")) in rids]
        if len(own_m) != len(ms):
            problems.append(f"{tag}: 자기 반쪽에 없는 리뷰의 빠진 태그를 적음 {len(ms) - len(own_m)}개")
        fail = sum(1 for f in own if str(f.get("status", "")).upper() == "FAIL")
        parts.append({"part": tag, "sample": len(half), "auditor_checked": a.get("checked"), "fail": fail,
                      "fail_rate": round(fail / len(half), 3) if half else 0.0, "missed": len(own_m)})
        findings += own
        missed += own_m
    all_keys = {key(t) for t in sample}
    lost = sorted(all_keys - set(seen))
    dup = sorted(k for k, v in seen.items() if len(v) > 1)
    extra = sorted(set(seen) - all_keys)
    if lost:
        problems.append(f"반쪽 어디에도 없는 표본 {len(lost)}개(예: {lost[0]})")
    if dup:
        problems.append(f"두 반쪽에 겹친 표본 {len(dup)}개(예: {dup[0]})")
    if extra:
        problems.append(f"전체 표본에 없는 반쪽 항목 {len(extra)}개(예: {extra[0]})")
    checked = len(sample) if not problems else sum(p_["auditor_checked"] or 0 for p_ in parts)
    import yaml
    (run / "04_tag_audit.yaml").write_text(yaml.safe_dump(
        {"audit": {"stage": "tags", "run": run.name, "checked": checked, "merged_from": [p_["part"] for p_ in parts],
                   "findings": findings, "missed": missed}}, allow_unicode=True, sort_keys=False), encoding="utf-8")
    return {"parts": parts, "problems": problems}


def audit(run, max_fail):
    merged = merge_tag_audit_parts(run, read_jsonl(run / "04_audit_sample.jsonl")) if (run / "04_audit_sample.jsonl").exists() else None
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
    elif checked != len(tags) + len(gold_tags) or (merged and merged["problems"]):
        status = "INCOMPLETE"       # 감사자가 표본을 다 보지 않았거나 반쪽을 합치다 문제가 있으면 PASS로 넘기지 않음
    else:
        status = "PASS" if rate <= max_fail else "FAIL"
    out = {"checked_at": now_iso(), "status": status, "sample_tags": len(tags), "auditor_checked": checked,
           "excluded_gold_tags": len(gold_tags),
           "fail": counts["FAIL"], "unverified": counts["UNVERIFIED"], "missed": len(missed),
           "fail_rate": round(rate, 3), "conservative_rate": round(cons, 3),
           "conservative_rule": "(FAIL + UNVERIFIED + missed) / (표본 태그 + missed)", "max_fail_rate": max_fail, "by_asin": by_asin,
           "asins_with_findings": sorted(retry - {"?"}), "batches_with_findings": sorted(batches - {"?"}),
           "warnings": warns}
    if merged:
        out["parts"], out["merge_problems"] = merged["parts"], merged["problems"]
    write_json(run / "04_tag_audit_summary.json", out)
    print(f"태그 검수 집계: {status}  (감사 표본 {len(tags)}개 중 FAIL {counts['FAIL']}개 = {rate:.1%}, "
          f"기준 {max_fail:.0%} 이하. UNVERIFIED {counts['UNVERIFIED']}개, 빠진 태그 {len(missed)}개, "
          f"판정 못 받은 것을 FAIL로 센 보수적 비율 {cons:.1%})")
    if merged:
        print("  반쪽마다: " + ", ".join(f"{p_['part']} {p_['fail']}/{p_['sample']}개 = {p_['fail_rate']:.1%}" for p_ in merged["parts"])
              + (". 합치기 확인: 표본 빠짐과 겹침 없음" if not merged["problems"] else ""))
        for pr in merged["problems"]:
            print(f"  합치기 문제: {pr}")
    for x, v in by_asin.items():
        print(f"  {x}: 표본 {v['sample']}개, FAIL {v['fail']}개({v['fail_rate']:.1%})")
    if out["batches_with_findings"]:
        print(f"  다시 태깅할 묶음: {', '.join(out['batches_with_findings'])}")
    for w in warns:
        print(f"  주의: {w}")
    return 0 if status == "PASS" else 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("mode", choices=["pick", "pick-score", "sheet", "schema-approve", "gold", "score", "audit-sample", "audit"])
    ap.add_argument("--set", default="rules", choices=list(GOLD_DIRS),
                    help="sheet, gold, score: rules(규칙을 다듬는 정답 세트, gold/) 또는 score(채점만 하는 정답 세트, gold_score/)")
    ap.add_argument("run", nargs="?")
    ap.add_argument("--per-asin", type=int, default=5)
    ap.add_argument("--min-chars", type=int, default=40)
    ap.add_argument("--sample-per-asin", type=int, default=25)
    ap.add_argument("--f1", type=float, default=0.80)
    ap.add_argument("--tags", default=None, help="score: 판정할 sonnet 태그 파일(회차 폴더 기준, 기본 04_tags.jsonl)")
    ap.add_argument("--sentiment", type=float, default=0.90)
    ap.add_argument("--n", type=int, default=150, help="audit-sample 전체 표본 태그 수(ASIN마다 n / ASIN 수)")
    ap.add_argument("--max-fail", type=float, default=0.05)
    ap.add_argument("--parts", type=int, default=2, help="audit-sample: 감사자 수만큼 표본을 리뷰 단위로 나눔(1이면 나누지 않음)")
    ap.add_argument("--translations", default=None, help="sheet: 한국어 번역 JSON 경로(기본 gold/gold_translations_ko.json)")
    ap.add_argument("--schema", default=None, help="sheet: 화면 기준 스키마 파일(기본: 승인본, 없으면 초안)")
    ap.add_argument("--review", default="03_schema_review.json", help="schema-approve: 스키마 확인 파일")
    ap.add_argument("--approved-at", default=None)
    ap.add_argument("--approved-by", default=None)
    ap.add_argument("--rename", default="", help="gold: 승인 때 바뀐 주제 id, old:new를 쉼표로")
    ap.add_argument("--drop-unknown", action="store_true", help="gold: 승인 스키마에 없는 주제의 정답 태그를 뺀다")
    args = ap.parse_args()
    run = resolve_run(args.run)
    global GOLD_DIR
    GOLD_DIR = GOLD_DIRS["score" if args.mode == "pick-score" else args.set]
    if args.mode == "pick-score":
        sys.exit(pick_score(run, 4 if args.per_asin == 5 else args.per_asin, 20 if args.min_chars == 40 else args.min_chars))
    if args.mode == "pick":
        sys.exit(pick(run, args.per_asin, args.min_chars, args.sample_per_asin))
    if args.mode == "sheet":
        sys.exit(sheet(run, args.translations, args.schema))
    if args.mode == "schema-approve":
        sys.exit(schema_approve(run, args.review, args.approved_at, args.approved_by))
    if args.mode == "gold":
        rename = dict(x.split(":", 1) for x in args.rename.split(",") if ":" in x)
        sys.exit(check_gold(run, rename, args.drop_unknown))
    if args.mode == "score":
        sys.exit(score(run, args.f1, args.sentiment, args.tags))
    if args.mode == "audit-sample":
        sys.exit(audit_sample(run, args.n, parts=args.parts))
    sys.exit(audit(run, args.max_fail))


if __name__ == "__main__":
    main()
