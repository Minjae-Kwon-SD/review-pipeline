"""회차 입력 파일과 스키마 검사.

사용: python scripts/check_inputs.py [회차]
  1단계. 회차를 빼면 runs/CURRENT의 회차를 본다.
  검사: 01_asins.csv, 02_reviews.csv, 02_star_distribution.csv의 칸과 값,
        ASIN마다 별점 묶음(config/pipeline.yaml의 weighting.groups) 표본.
          오류: 표본이 있는 묶음이 2개 미만, 또는 실제 비율 50% 이상인 묶음에 표본이 없음.
          경고: 묶음 표본이 min_group_sample보다 적음, 표본이 없는 묶음(그 실제 비율과 함께).
        분포: s1~s5 합이 98~102인지(아니면 오류), 분포로 계산한 평균과 average_rating 차이가
          dist_mean_tolerance를 넘는지(경고).
  결과: 00_input_check.json(ASIN별 group_coverage, missing_real_pct, 언어별 건수 포함). 오류가 있으면 종료 코드 1.

사용: python scripts/check_inputs.py [회차] --schema [파일 이름]
  2단계 뒤(03_schema_draft.yaml)와 3단계 승인 뒤(기본값 03_schema_approved.yaml)에 스키마를 본다.
  검사: id와 side, 정의, 예시 인용이 그 리뷰 원문에 있는지, 예시가 정답 세트 리뷰가 아닌지, 주제 수 16개 이내.
  주의: 공통 주제(config/topics_common.yaml) 11개가 id나 common_id로 남았는지, 예시가 03_schema_sample.csv에서 왔는지.
  결과: 03_schema_check.json. 오류가 있으면 종료 코드 1.
"""
import argparse
import csv
import re
import sys
from collections import Counter, defaultdict

from pipeline_io import (ASIN_COLS, DIST_COLS, REVIEW_COLS, ROOT, STARS, load_config, load_csv_or_die, load_schema,
                         load_yaml, norm_text, now_iso, read_csv, real_shares, resolve_run, star_groups, write_json)

MAX_TOPICS = 16
AMAZON_ID = re.compile(r"R[0-9A-Z]{6,}")


def check_reviews(rows, errors, warns):
    seen = set()
    for i, r in enumerate(rows, 2):
        rid, asin = r["review_id"], r["asin"]
        where = f"02_reviews.csv {i}번째 줄({rid or '빈 review_id'})"
        if not rid:
            errors.append(f"{where}: review_id가 비었습니다.")
        elif rid in seen:
            errors.append(f"{where}: review_id가 겹칩니다.")
        seen.add(rid)
        if not asin:
            errors.append(f"{where}: asin이 비었습니다.")
        elif rid and not rid.startswith(asin) and not AMAZON_ID.fullmatch(rid):
            warns.append(f"{where}: review_id가 asin으로 시작하지 않습니다.")
        if r["star"] not in ("1", "2", "3", "4", "5"):
            errors.append(f"{where}: star는 1~5 정수여야 합니다(지금 '{r['star']}').")
        if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", r["date"]):
            warns.append(f"{where}: date가 YYYY-MM-DD 형식이 아닙니다.")
        if not r["body"].strip():
            errors.append(f"{where}: body가 비었습니다.")
        for col in ("verified", "vine"):
            if r[col].lower() not in ("true", "false"):
                errors.append(f"{where}: {col}는 true 또는 false여야 합니다.")


def check_dist(rows, errors, warns, tolerance):
    out = {}
    for i, r in enumerate(rows, 2):
        asin = r["asin"]
        where = f"02_star_distribution.csv {i}번째 줄({asin})"
        if asin in out:
            errors.append(f"{where}: asin이 겹칩니다.")
            continue
        vals = {}
        for s in (5, 4, 3, 2, 1):
            try:
                v = float(r[f"s{s}"])
                if not 0 <= v <= 100:
                    raise ValueError
            except ValueError:
                errors.append(f"{where}: s{s}는 0~100 숫자(퍼센트)여야 합니다.")
                break
            vals[s] = v
        else:
            total = sum(vals.values())
            if not 98 <= total <= 102:
                errors.append(f"{where}: 별점 비율 합이 {total:g}%입니다(반올림 고려해 98~102이어야 함).")
            else:
                out[asin] = r
                if r.get("average_rating"):
                    mean = sum(s * v for s, v in real_shares(r).items())
                    try:
                        avg = float(r["average_rating"])
                        if abs(mean - avg) > tolerance:
                            warns.append(f"{where}: 분포로 계산한 평균 {mean:.2f}과 average_rating {avg:g}의 차이가 "
                                         f"{abs(mean - avg):.2f}입니다(기준 {tolerance}).")
                    except ValueError:
                        warns.append(f"{where}: average_rating이 숫자가 아닙니다.")
        if not r["total_ratings"].replace(",", "").isdigit():
            warns.append(f"{where}: total_ratings가 정수가 아닙니다.")
    return out


def check_groups(asin, counts, dist_row, wc, errors, warns):
    """ASIN 하나의 별점 묶음 표본을 보고 group_coverage를 돌려준다."""
    real = real_shares(dist_row)
    info = star_groups(counts, real, wc["groups"])
    covered = [g for g, x in info.items() if x["mode"] != "empty"]
    if len(covered) < 2:
        errors.append(f"{asin}: 표본이 있는 별점 묶음이 {len(covered)}개입니다(2개 이상이어야 가중치를 만들 수 있음).")
    for g, x in info.items():
        stars = ",".join(str(s) for s in x["stars"])
        if x["mode"] == "empty":
            msg = f"{asin}: {g} 묶음({stars}★)에 표본이 없습니다(실제 비율 {100 * x['real']:.1f}%)."
            if x["real"] >= 0.5:
                errors.append(msg + " 실제 비율이 50% 이상인 묶음이라 리뷰를 더 모아야 합니다.")
            else:
                warns.append(msg + " 이 비율은 가중 결과에서 빠집니다.")
        elif x["sample"] < wc["min_group_sample"]:
            warns.append(f"{asin}: {g} 묶음({stars}★) 표본이 {x['sample']}개입니다(기준 {wc['min_group_sample']}개).")
    for s in STARS:
        if real[s] == 0 and counts[s] > 0:
            warns.append(f"{asin}: 실제 {s}★ 비율이 0%라 {s}★ 표본 리뷰는 가중치 0이 됩니다.")
    coverage = {g: {"sample": x["sample"], "real_pct": round(100 * x["real"], 1), "mode": x["mode"]}
                for g, x in info.items()}
    missing = round(100 * sum(x["real"] for x in info.values() if x["mode"] == "empty"), 1)
    return coverage, missing


def check_asins(rows, errors, warns):
    out = {}
    for i, r in enumerate(rows, 2):
        where = f"01_asins.csv {i}번째 줄({r['asin']})"
        if r["status"] not in ("selected", "excluded"):
            errors.append(f"{where}: status는 selected 또는 excluded여야 합니다.")
        if r["status"] != "selected":
            continue
        if not r["brand"]:
            errors.append(f"{where}: brand가 비었습니다.")
        try:
            if r["amazon_rating"] and not 1 <= float(r["amazon_rating"]) <= 5:
                raise ValueError
        except ValueError:
            warns.append(f"{where}: amazon_rating은 1~5 숫자여야 합니다.")
        out[r["asin"]] = r
    return out


def check_schema(run, name):
    """스키마 파일 하나를 검사한다. id, side 오류는 load_schema가 바로 멈춘다."""
    schema = load_schema(run, name)
    reviews = {r["review_id"]: r for r in load_csv_or_die(run / "02_reviews.csv", REVIEW_COLS)}
    gold_ids = set()
    gold_path = run / "gold" / "gold_reviews.csv"
    if gold_path.exists():
        with open(gold_path, encoding="utf-8-sig", newline="") as f:
            gold_ids = {r["review_id"] for r in csv.DictReader(f)}
    else:
        print("  주의: gold/gold_reviews.csv가 없어 정답 세트와 겹치는지 보지 못했습니다(eval_gold.py pick 먼저).")
    errors, warns = [], []
    if len(schema) > MAX_TOPICS:
        warns.append(f"주제가 {len(schema)}개입니다(16개 이내로 정했음).")
    for tid, t in schema.items():
        if not re.fullmatch(r"[a-z][a-z0-9_]*", tid):
            warns.append(f"{tid}: id는 영어 소문자 snake_case로 씁니다.")
        if not str(t.get("definition") or "").strip():
            errors.append(f"{tid}: definition이 비었습니다.")
        for key in ("include", "exclude", "confusions"):
            if key not in t:
                warns.append(f"{tid}: {key} 칸이 없습니다.")
        for n, e in enumerate(t["examples"], 1):
            where = f"{tid} 예시 {n}"
            if not isinstance(e, dict):
                errors.append(f"{where}: review_id와 quote로 적어야 합니다.")
                continue
            rid, quote = str(e.get("review_id") or ""), str(e.get("quote") or "")
            r = reviews.get(rid)
            if r is None:
                errors.append(f"{where}: 없는 review_id {rid}")
                continue
            if rid in gold_ids:
                errors.append(f"{where}: {rid}는 정답 세트 리뷰라 예시로 쓰면 안 됩니다(채점이 부풀려짐).")
            text = r["title"] + "\n" + r["body"]
            if not quote or (quote not in text and norm_text(quote) not in norm_text(text)):
                errors.append(f"{where}: 인용이 {rid} 원문에 없습니다: \"{quote[:80]}\"")
    # v1: 공통 주제 11개가 id 그대로나 common_id로 남았는지, 예시가 스키마 표본에서 왔는지(주의만)
    common_path = ROOT / "config" / "topics_common.yaml"
    if common_path.exists():
        common = [str(t["id"]) for t in (load_yaml(common_path) or {}).get("topics", [])]
        kept = set(schema) | {str(t.get("common_id")) for t in schema.values() if t.get("common_id")}
        lost = [c for c in common if c not in kept]
        if lost:
            warns.append(f"공통 주제가 빠졌습니다(id나 common_id로 남겨야 함): {', '.join(lost)}")
    sample_path = run / "03_schema_sample.csv"
    if sample_path.exists():
        with open(sample_path, encoding="utf-8-sig", newline="") as f:
            sample_ids = {r["review_id"] for r in csv.DictReader(f)}
        outside = sorted({str(e.get("review_id")) for t in schema.values() for e in t["examples"]
                          if isinstance(e, dict) and str(e.get("review_id")) not in sample_ids})
        if outside:
            warns.append(f"스키마 표본(03_schema_sample.csv)에 없는 리뷰를 예시로 썼습니다: {', '.join(outside)}")
    status = "FAIL" if errors else "PASS"
    write_json(run / "03_schema_check.json", {"checked_at": now_iso(), "file": name, "status": status,
                                             "topics": len(schema), "errors": errors, "warnings": warns})
    print(f"스키마 검사({name}): {status}  (주제 {len(schema)}개: "
          f"제품 {sum(t['side'] == 'P' for t in schema.values())}, 브랜드 {sum(t['side'] == 'B' for t in schema.values())})")
    for e in errors:
        print(f"  오류: {e}")
    for w in warns:
        print(f"  주의: {w}")
    return 1 if errors else 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("run", nargs="?")
    ap.add_argument("--schema", nargs="?", const="03_schema_approved.yaml", default=None,
                    help="스키마 파일 이름(기본 03_schema_approved.yaml)")
    args = ap.parse_args()
    run = resolve_run(args.run)
    if args.schema:
        sys.exit(check_schema(run, args.schema))
    errors, warns = [], []
    wc = load_config()["weighting"]
    asins = read_csv(run / "01_asins.csv", ASIN_COLS, errors)
    reviews = read_csv(run / "02_reviews.csv", REVIEW_COLS, errors)
    dist_rows = read_csv(run / "02_star_distribution.csv", DIST_COLS, errors)

    selected = check_asins(asins, errors, warns) if asins is not None else {}
    dist = check_dist(dist_rows, errors, warns, wc["dist_mean_tolerance"]) if dist_rows is not None else {}
    counts = defaultdict(Counter)
    langs = defaultdict(Counter)
    if reviews is not None:
        check_reviews(reviews, errors, warns)
        for r in reviews:
            if r["star"] in ("1", "2", "3", "4", "5"):
                counts[r["asin"]][int(r["star"])] += 1
            langs[r["asin"]][r.get("language") or "blank"] += 1

    coverage, missing = {}, {}
    if reviews is not None and dist_rows is not None:
        for asin in sorted(counts):
            if asin not in dist:
                if not any(r["asin"] == asin for r in dist_rows):
                    errors.append(f"{asin}: 02_star_distribution.csv에 별점 비율이 없습니다.")
                continue
            coverage[asin], missing[asin] = check_groups(asin, counts[asin], dist[asin], wc, errors, warns)
        for asin in sorted(set(dist) - set(counts)):
            warns.append(f"{asin}: 별점 비율은 있는데 리뷰가 없습니다.")
    if reviews is not None and asins is not None:
        for asin in sorted(set(counts) - set(selected)):
            errors.append(f"{asin}: 01_asins.csv에 selected로 없습니다(브랜드와 가격대가 리포트에 필요).")
        for asin in sorted(set(selected) - set(counts)):
            warns.append(f"{asin}: selected인데 리뷰가 없습니다.")

    status = "FAIL" if errors else "PASS"
    write_json(run / "00_input_check.json", {
        "checked_at": now_iso(), "status": status, "errors": errors, "warnings": warns,
        "asins": len(counts), "reviews": sum(sum(c.values()) for c in counts.values()),
        "sample_counts": {a: {str(s): counts[a][s] for s in (1, 2, 3, 4, 5)} for a in sorted(counts)},
        "groups": wc["groups"],
        "group_coverage": coverage,
        "missing_real_pct": missing,
        "languages": {a: dict(langs[a].most_common()) for a in sorted(langs)},
        "languages_total": dict(sum(langs.values(), Counter()).most_common()),
    })

    print(f"입력 검사: {status}  (ASIN {len(counts)}개, 리뷰 {sum(sum(c.values()) for c in counts.values())}개)")
    if counts:
        print("ASIN별 표본 수: 1★ 2★ 3★ 4★ 5★ / 묶음 방식")
        for a in sorted(counts):
            modes = ", ".join(f"{g} {x['mode']}" for g, x in coverage.get(a, {}).items())
            print(f"  {a}: " + " ".join(f"{counts[a][s]:>3}" for s in (1, 2, 3, 4, 5)) + f" / {modes}")
    for e in errors:
        print(f"  오류: {e}")
    for w in warns:
        print(f"  주의: {w}")
    sys.exit(1 if errors else 0)


if __name__ == "__main__":
    main()
