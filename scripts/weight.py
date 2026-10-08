"""5단계: 별점 가중 보정과 집계.

사용: python scripts/weight.py [회차] [--tags 04_tags.jsonl] [--impact-min 3] [--strength-min 2]
입력: 01_asins.csv, 02_reviews.csv, 02_star_distribution.csv, 03_schema_approved.yaml,
      04_tags.jsonl(sonnet 묶음 태그를 합친 것, 리포트가 쓰는 태그),
      config/pipeline.yaml(별점 묶음과 경고 기준),
      04_gold_eval.json(있으면 부록의 정확도 숫자를 리포트 표기로 옮겨 accuracy에 넣는다)
출력: 05_metrics.json(리포트 문장에 쓰는 모든 숫자), 05_tables.md(리포트에 그대로 붙일 표)

사용: python scripts/weight.py [회차] --weights-only
  태그와 스키마 없이 가중치만 계산해 05_weights_preview.md(ASIN별 묶음, 표본 수, 실제 %, 방식, 가중치, 경고)를 쓴다.

계산 규칙(별점 묶음 보정, 묶음은 config/pipeline.yaml의 weighting.groups)
- ASIN마다 n = 표본 수, real[s] = 실제 비율(합 1). covered = 표본이 있는 묶음, R = covered 묶음의 실제 비율 합.
- 묶음 안 별점이 모두 표본을 가지면 w(s) = (real[s] / R) / (표본 수(s) / n).
  하나라도 비면 w_g = (real_g / R) / (표본 수(g) / n)을 묶음 안 표본이 있는 별점에 똑같이 준다.
  표본이 없는 묶음의 실제 비율은 missing_real_pct로 남긴다. 모든 묶음이 차 있고 별점마다 표본이 있으면 v0 규칙과 같다.
- 가중 부정 비율 = 그 주제 부정 태그의 가중치 합 / 그 주제 태그 전체의 가중치 합.
- 부정 언급 리뷰어(가중) = 그 주제를 부정으로 언급한 리뷰의 가중치 합 / 전체 리뷰의 가중치 합.
- 별점 격차 = 그 주제 부정 언급 리뷰의 가중 평균 별점 - 나머지 모든 리뷰의 가중 평균 별점.
자체 검사: ASIN마다 가중치 합 = n, covered 묶음의 가중 비중 = real_g / R(오차 1e-9).
- 유효 별점: 평균 별점(가중 평균, 영향 분석의 별점 격차, ASIN 비교)에는 리뷰마다 유효 별점을 쓴다.
  별점마다 보정한 리뷰는 실제 별점, 묶음 단위로 보정한 리뷰는 그 묶음의 실제 평균 별점(묶음 안 s x real[s] 합 / real_g).
  리뷰의 원래 별점 칸은 바꾸지 않는다.
자체 검사(추가): ASIN마다 유효 별점 가중 평균 = 표본이 있는 묶음만으로 다시 나눈 분포 평균(오차 0.005).
  모든 묶음이 별점마다 보정된 ASIN은 이 값이 원래 분포 평균과 같다(v0 검사).
1장 실제 별점 분포: 가중치에서 거꾸로 만들지 않고 02_star_distribution.csv에서 바로 모은다.
  별점 s의 실제 비율 = Σ_ASIN n × real[s] / R(표본이 있는 묶음의 별점만) ÷ Σ n. 비어 있는 묶음의 별점은 0%이고,
  빠진 실제 비율(Σ n × missing_real_pct ÷ Σ n)을 따로 적는다.
경고(멈추지 않음): 묶음 표본이 min_group_sample보다 적음,
  리뷰 한 개의 비중 w(s) / n이 max_review_share보다 큼(적은 리뷰가 큰 비중을 대표함).
"""
import argparse
import json
import sys
from collections import Counter, defaultdict
from itertools import combinations

import sections
from pipeline_io import (ASIN_COLS, DIST_COLS, REVIEW_COLS, SENTIMENTS, SIDE_KO, STARS, category_conf, die,
                         fmt_pct, fmt_star, load_config, load_csv_or_die, load_schema, now_iso, pct,
                         read_jsonl, real_shares, resolve_run, star_groups, write_json)


# 리뷰마다 하나씩 붙는 주제(전체 만족도)는 1~3장 분포에만 보이고, 주제끼리 비교하는 곳
# (ASIN별 강점과 약점, 영향 분석, 공출현)에서는 뺀다. 리뷰 단위 총평이라 별점과 같은 뜻이 되기 때문이다.
COMPARE_EXCLUDE = ("overall",)


OFF_CATEGORY = "off_category"   # review-tagger가 카테고리 밖 리뷰에 다는 표시(주제가 아님)


def compare_topics(schema):
    return [t for t in schema if t not in COMPARE_EXCLUDE]


def gold_accuracy(g):
    """04_gold_eval.json의 정확도를 리포트 표기로 옮긴다(F1 소수 둘째 자리, 감성 일치 % 소수 첫째 자리).

    topic_f1_text("0.90"), sentiment_text("88.6%")는 리포트에 글자 그대로 쓰는 표기다.
    """
    out = {"gold_reviews": g.get("gold_reviews"), "status": g.get("status")}
    for label, m in g.get("models", {}).items():
        f1, sp = round(m["topic_f1"], 2), pct(m["sentiment_agreement"], 1)
        out[label] = {"topic_f1": f1, "sentiment_pct": sp,
                      "topic_f1_text": f"{f1:.2f}", "sentiment_text": fmt_pct(sp)}
    return out


def data_notes(run, dist, asin_info, summary, weighting):
    """리포트 머리말과 7장에 쓰는 고정 문구 대신 데이터로 만든 문장."""
    if (run / "raw" / "paid_calls.jsonl").exists():
        source = "아마존에서 새로 수집한 뒤 공유 리뷰 DB에서 받음"
    elif any(d.get("source") for d in dist.values()):
        source = "공유 리뷰 DB에서 받음"
    else:
        source = "브라우저로 직접 모음"
    log = run / "02_collect_log.json"
    if log.exists():
        dropped = json.loads(log.read_text(encoding="utf-8")).get("dropped_count", 0)
        if dropped:
            source += f", 본문 없는 리뷰 {dropped}개 제외"
    sm, wm = summary["sample_mean_star"], summary["weighted_mean_star"]
    if sm < wm:
        notice = (f"표본에는 낮은 별점이 실제보다 많습니다(표본 평균 {fmt_star(sm)}, 실제 분포로 되돌린 가중 평균 "
                  f"{fmt_star(wm)}).")
    elif sm > wm:
        notice = (f"표본에는 높은 별점이 실제보다 많습니다(표본 평균 {fmt_star(sm)}, 실제 분포로 되돌린 가중 평균 "
                  f"{fmt_star(wm)}).")
    else:
        notice = f"표본 평균과 가중 평균이 {fmt_star(sm)}로 같습니다."
    empty = [a for a, x in weighting["per_asin"].items() if x["missing_real_pct"] > 0]
    if empty:
        notice += (f" ASIN {len(empty)}개는 표본이 없는 별점 묶음이 있어, 그 묶음의 실제 비율은 가중 결과에서 빠졌습니다"
                   f"(ASIN별 비율은 1장 분포 표).")
    ns = sorted(a["sample_reviews"] for a in asin_info.values())
    per_asin = f"ASIN당 표본 리뷰 {ns[0]}개" if ns[0] == ns[-1] else f"ASIN당 표본 리뷰 {ns[0]}~{ns[-1]}개"
    return {"data_source": source, "sample_notice": notice, "asin_sample_text": per_asin}


def weights_preview(run, reviews, dist, asins, conf):
    """--weights-only: 태그 없이 가중치만 계산해 05_weights_preview.md를 쓴다."""
    _, asin_info, weighting, _ = build_weights(reviews, dist, conf)
    wc = conf["weighting"]
    lines = ["# 가중치 미리보기", "",
             f"회차 {run.name}. 만든 때 {now_iso()}. 묶음 기준과 경고 기준은 config/pipeline.yaml"
             f"(묶음 표본 {wc['min_group_sample']}개 미만, 리뷰 한 개 비중 {fmt_pct(100 * wc['max_review_share'])} 초과면 경고).",
             "", *weights_table(weighting), "",
             "| ASIN | 브랜드 | 표본 리뷰 | 표본 평균 | 보정 평균(유효 별점) | 분포 평균(덮인 묶음 기준) | 분포 평균(전체) | 빠진 실제 비율 |",
             "|---|---|---|---|---|---|---|---|"]
    for a, x in asin_info.items():
        lines.append(f"| {a} | {asins.get(a, {}).get('brand', '')} | {x['sample_reviews']} | {fmt_star(x['sample_mean_star'])} | "
                     f"{fmt_star(x['weighted_mean_star'])} | {fmt_star(x['covered_hist_mean_star'])} | "
                     f"{fmt_star(x['hist_mean_star'])} | {fmt_pct(x['missing_real_pct'])} |")
    lines += ["", disclosure(weighting), "", "## 경고", ""]
    lines += [f"- {w}" for w in weighting["warnings"]] or ["- 없음"]
    (run / "05_weights_preview.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"가중치 미리보기: ASIN {len(asin_info)}개, 리뷰 {sum(x['sample_reviews'] for x in asin_info.values())}개, "
          f"경고 {len(weighting['warnings'])}개. 자체 검사 통과. 05_weights_preview.md")
    for w in weighting["warnings"]:
        print(f"  주의: {w}")


def real_star_dist(dist, weighting):
    """1장 실제 별점 분포(%)와 빠진 실제 비율(%). ASIN마다 표본 수 n으로 가중한다."""
    acc, total_n, missing = {s: 0.0 for s in STARS}, 0, 0.0
    for asin, x in weighting["per_asin"].items():
        n = x["sample_reviews"]
        real = real_shares(dist[asin])
        covered = [s for g in x["groups"].values() if g["mode"] != "empty" for s in g["stars"]]
        R = sum(real[s] for s in covered)
        for s in covered:
            acc[s] += n * real[s] / R if R else 0.0
        missing += n * x["missing_real_pct"]
        total_n += n
    if not total_n:
        return {str(s): 0.0 for s in STARS}, 0.0
    return {str(s): round(100 * acc[s] / total_n, 1) for s in STARS}, round(missing / total_n, 1)


def wavg(pairs):
    """(가중치, 별점) 목록의 가중 평균."""
    tw = sum(w for w, _ in pairs)
    return sum(w * s for w, s in pairs) / tw if tw else 0.0


def star_weights(counts, real, groups):
    """ASIN 하나의 별점 묶음 보정. counts[s] = 표본 수, real[s] = 합 1인 실제 비율.

    covered = 표본이 있는 묶음, R = covered 묶음의 실제 비율 합.
    묶음 안 별점이 모두 표본을 가지면 w(s) = (real[s] / R) / (counts[s] / n),
    하나라도 비면 w_g = (real_g / R) / (sample_g / n)을 묶음 안 표본이 있는 별점에 똑같이 준다.
    돌려주는 값: ({별점: 가중치}, 묶음 현황, R)
    """
    n = sum(counts.get(s, 0) for s in STARS)
    info = star_groups(counts, real, groups)
    R = sum(g["real"] for g in info.values() if g["mode"] != "empty")
    w = {}
    for g in info.values():
        if g["mode"] == "per_star":
            for s in g["stars"]:
                w[s] = (real[s] / R) / (counts[s] / n) if R else 0.0
        elif g["mode"] == "group":
            wg = (g["real"] / R) / (g["sample"] / n) if R else 0.0
            for s in g["stars"]:
                if counts.get(s, 0):
                    w[s] = wg
    return w, info, R


def build_weights(reviews, dist, conf):
    """리뷰마다 가중치를 만들고 ASIN마다 자체 검사를 한다. 검사에 실패하면 멈춘다."""
    wc = conf["weighting"]
    groups = wc["groups"]
    by_asin = defaultdict(list)
    for r in reviews:
        by_asin[r["asin"]].append(r)
    weight, eff, asin_info, per_asin, warnings = {}, {}, {}, {}, []
    for asin in sorted(by_asin):
        rs = by_asin[asin]
        if asin not in dist:
            die(f"{asin}: 02_star_distribution.csv에 별점 비율이 없습니다. check_inputs.py를 먼저 통과시켜 주세요.")
        n = len(rs)
        counts = Counter(int(r["star"]) for r in rs)
        real = real_shares(dist[asin])
        w, info, R = star_weights(counts, real, groups)
        if R <= 0:
            die(f"{asin}: 표본이 있는 별점 묶음의 실제 비율 합이 0입니다. check_inputs.py를 먼저 통과시켜 주세요.")
        # 유효 별점: 별점마다 보정한 별점은 그대로, 묶음 단위로 보정한 별점은 그 묶음의 실제 평균 별점
        es = {}
        for gi in info.values():
            for s in gi["stars"]:
                if gi["mode"] == "group":
                    es[s] = (sum(x * real[x] for x in gi["stars"]) / gi["real"] if gi["real"]
                             else sum(gi["stars"]) / len(gi["stars"]))
                else:
                    es[s] = float(s)
        for r in rs:
            weight[r["review_id"]] = w[int(r["star"])]
            eff[r["review_id"]] = es[int(r["star"])]

        # 자체 검사: 가중치 합 = n, covered 묶음의 가중 비중 = real_g / R
        wsum = sum(w[int(r["star"])] for r in rs)
        if abs(wsum - n) > 1e-9 * max(1, n):
            die(f"자체 검사 실패 {asin}: 가중치 합 {wsum:.10f} != 표본 수 {n}")
        for g, gi in info.items():
            if gi["mode"] == "empty":
                continue
            share = sum(w[int(r["star"])] for r in rs if int(r["star"]) in gi["stars"]) / n
            if abs(share - gi["real"] / R) > 1e-9:
                die(f"자체 검사 실패 {asin} {g}: 가중 비중 {share:.10f} != {gi['real'] / R:.10f}")
        weighted_mean = wavg([(w[int(r["star"])], es[int(r["star"])]) for r in rs])
        hist_mean = sum(real[s] * s for s in STARS)
        covered_mean = sum(real[s] * s for gi in info.values() if gi["mode"] != "empty" for s in gi["stars"]) / R
        all_per_star = all(gi["mode"] == "per_star" for gi in info.values())
        if abs(weighted_mean - covered_mean) >= 0.005:
            die(f"자체 검사 실패 {asin}: 유효 별점 가중 평균 {weighted_mean:.4f} != 덮인 묶음 분포 평균 {covered_mean:.4f}")

        missing = round(100 * sum(gi["real"] for gi in info.values() if gi["mode"] == "empty"), 1)
        groups_out = {}
        for g, gi in info.items():
            gw = [w[s] for s in gi["stars"] if s in w]
            max_w = max(gw) if gw else None
            groups_out[g] = {"stars": gi["stars"], "sample": gi["sample"], "real_pct": round(100 * gi["real"], 1),
                             "mode": gi["mode"], "weights": {str(s): round(w[s], 6) for s in gi["stars"] if s in w},
                             "effective_star": round(es[gi["stars"][0]], 6) if gi["mode"] == "group" else None,
                             "max_weight": None if max_w is None else round(max_w, 6),
                             "max_review_share_pct": None if max_w is None else round(100 * max_w / n, 2)}
            if gi["mode"] != "empty" and gi["sample"] < wc["min_group_sample"]:
                warnings.append(f"{asin} {g}: 묶음 표본 {gi['sample']}개(기준 {wc['min_group_sample']}개 미만)")
            if max_w is not None and max_w / n > wc["max_review_share"]:
                warnings.append(f"{asin} {g}: 리뷰 한 개 비중 {fmt_pct(100 * max_w / n)}(가중치 {max_w:.3f} / 표본 {n}개, "
                                f"기준 {fmt_pct(100 * wc['max_review_share'])} 초과)")
        per_asin[asin] = {"sample_reviews": n, "covered_real_pct": round(100 * R, 1),
                          "missing_real_pct": missing, "all_per_star": all_per_star, "groups": groups_out}
        asin_info[asin] = {
            "sample_reviews": n,
            "sample_counts": {str(s): counts[s] for s in STARS},
            "real_pct": {str(s): round(100 * real[s], 1) for s in STARS},
            "weights": {str(s): round(w[s], 4) for s in sorted(w)},
            "sample_mean_star": round(sum(int(r["star"]) for r in rs) / n, 2),
            "weighted_mean_star": round(weighted_mean, 2),
            "hist_mean_star": round(hist_mean, 2),
            "covered_hist_mean_star": round(covered_mean, 2),
            "missing_real_pct": missing,
        }
    weighting = {"method": "star_groups", "groups": groups, "per_asin": per_asin, "warnings": warnings}
    return weight, asin_info, weighting, eff


GROUP_KO = {"negative": "부정", "neutral": "중립", "positive": "긍정"}
MODE_KO = {"per_star": "별점마다", "group": "묶음 단위", "empty": "표본 없음"}


def group_label(g, stars):
    return f"{GROUP_KO.get(g, g)}({','.join(str(s) for s in stars)}★)"


def weights_table(weighting):
    """ASIN별 묶음 표(마크다운 줄 목록)."""
    lines = ["| ASIN | 묶음 | 표본 수 | 실제 % | 방식 | 가중치 | 최대 가중치 | 리뷰 한 개 비중 |",
             "|---|---|---|---|---|---|---|---|"]
    for asin, a in weighting["per_asin"].items():
        for g, gi in a["groups"].items():
            ws = ", ".join(f"{s}★ {v:.3f}" for s, v in gi["weights"].items()) or "-"
            if gi["mode"] == "group":
                ws = f"{next(iter(gi['weights'].values())):.3f}(묶음 공통, 유효 별점 {gi['effective_star']:.2f}★)"
            mx = "-" if gi["max_weight"] is None else f"{gi['max_weight']:.3f}"
            sh = "-" if gi["max_review_share_pct"] is None else f"{gi['max_review_share_pct']:.2f}%"
            lines.append(f"| {asin} | {group_label(g, gi['stars'])} | {gi['sample']} | {fmt_pct(gi['real_pct'])} | "
                         f"{MODE_KO[gi['mode']]} | {ws} | {mx} | {sh} |")
    return lines


def disclosure(weighting):
    """데이터로 만든 보정 공개 문장."""
    pa = weighting["per_asin"]
    full = [a for a, x in pa.items() if x["all_per_star"]]
    part = [a for a in pa if a not in full]
    text = (f"별점 보정: ASIN {len(pa)}개 중 {len(full)}개는 별점마다, {len(part)}개는 일부 묶음을 묶음 단위로 "
            f"보정했습니다(묶음: " + ", ".join(group_label(g, s) for g, s in weighting["groups"].items()) + ").")
    empty = [f"{a} {group_label(g, gi['stars'])} {fmt_pct(gi['real_pct'])}"
             for a, x in pa.items() for g, gi in x["groups"].items() if gi["mode"] == "empty"]
    if empty:
        text += (" 표본이 없는 묶음은 가중 결과에서 빠졌고, 나머지 묶음의 비율을 그만큼 키워 맞췄습니다: "
                 + "; ".join(empty) + ".")
    return text


def topic_stats(tags, topic_ids, weight, review_ids):
    total_w = sum(weight[r] for r in review_ids)
    out = []
    for tid in topic_ids:
        ts = [t for t in tags if t["topic"] == tid]
        c = Counter(t["sentiment"] for t in ts)
        tag_w = sum(weight[t["review_id"]] for t in ts)
        neg_w = sum(weight[t["review_id"]] for t in ts if t["sentiment"] == "negative")
        neg_reviews = {t["review_id"] for t in ts if t["sentiment"] == "negative"}
        pos_reviews = {t["review_id"] for t in ts if t["sentiment"] == "positive"}
        out.append({
            "id": tid, "mentions": len(ts),
            **{s: c[s] for s in SENTIMENTS},
            "neg_pct": pct(c["negative"], len(ts)),
            "weighted_neg_pct": pct(neg_w, tag_w),
            "neg_reviewer_pct": pct(sum(weight[r] for r in neg_reviews), total_w),
            "pos_reviewer_pct": pct(sum(weight[r] for r in pos_reviews), total_w),
            "_neg_reviews": neg_reviews,
        })
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("run", nargs="?")
    ap.add_argument("--tags", default="04_tags.jsonl")
    ap.add_argument("--impact-min", type=int, default=20, help="영향 분석에 넣을 최소 부정 언급 리뷰 수(정답지 기준 20)")
    ap.add_argument("--strength-min", type=int, default=10,
                    help="ASIN별 강점과 약점 후보의 최소 언급 수(그 ASIN 안에서, 정답지 기준 10)")
    ap.add_argument("--weights-only", action="store_true", help="태그 없이 05_weights_preview.md만 만든다")
    ap.add_argument("--as-of", default=None, help="시간 추이 기준 날짜 YYYY-MM-DD(기본: 회차 이름의 날짜, 없으면 오늘)")
    args = ap.parse_args()
    run = resolve_run(args.run)
    conf = load_config()

    asins = {r["asin"]: r for r in load_csv_or_die(run / "01_asins.csv", ASIN_COLS) if r["status"] == "selected"}
    reviews = load_csv_or_die(run / "02_reviews.csv", REVIEW_COLS)
    dist = {r["asin"]: r for r in load_csv_or_die(run / "02_star_distribution.csv", DIST_COLS)}
    if args.weights_only:
        weights_preview(run, reviews, dist, asins, conf)
        return
    schema = load_schema(run)
    tags = read_jsonl(run / args.tags)
    # 카테고리와 무관한 리뷰(review-tagger가 off_category 한 줄만 단 리뷰)는 집계에서 빼고 개수만 부록에 적는다
    off = sorted({t["review_id"] for t in tags if t.get("topic") == OFF_CATEGORY})
    if off:
        asin_by_id = {r["review_id"]: r["asin"] for r in reviews}
        off_by_asin = dict(sorted(Counter(asin_by_id.get(r, "?") for r in off).items()))
        reviews = [r for r in reviews if r["review_id"] not in set(off)]
        tags = [t for t in tags if t["review_id"] not in set(off)]
    star = {r["review_id"]: int(r["star"]) for r in reviews}
    asin_of = {r["review_id"]: r["asin"] for r in reviews}
    for t in tags:
        if t.get("review_id") not in star:
            die(f"태그의 review_id가 리뷰 파일에 없습니다: {t.get('review_id')}. audit_quotes.py tags를 먼저 통과시켜 주세요.")
        if t.get("topic") not in schema:
            die(f"승인 스키마에 없는 주제입니다: {t.get('topic')}")
        if t.get("sentiment") not in SENTIMENTS:
            die(f"감성 값이 잘못됐습니다: {t.get('sentiment')}")

    weight, asin_info, weighting, eff = build_weights(reviews, dist, conf)
    all_ids = [r["review_id"] for r in reviews]

    # 1장: 분포
    sent_raw = Counter(t["sentiment"] for t in tags)
    tag_w_total = sum(weight[t["review_id"]] for t in tags)
    sent_w = {s: sum(weight[t["review_id"]] for t in tags if t["sentiment"] == s) for s in SENTIMENTS}
    side_raw = Counter(schema[t["topic"]]["side"] for t in tags)
    sample_counts = Counter(star.values())
    real_pct, missing_pct = real_star_dist(dist, weighting)

    # 2~3장: 주제
    topics = topic_stats(tags, list(schema), weight, all_ids)
    for t in topics:
        t["name_ko"], t["side"] = schema[t["id"]]["name_ko"], schema[t["id"]]["side"]

    # 4장: 영향 분석
    impact = []
    for t in topics:
        neg = t["_neg_reviews"]
        if t["id"] in COMPARE_EXCLUDE or len(neg) < args.impact_min:
            continue
        neg_avg = wavg([(weight[r], eff[r]) for r in neg])
        other_avg = wavg([(weight[r], eff[r]) for r in all_ids if r not in neg])
        impact.append({"id": t["id"], "name_ko": t["name_ko"], "neg_reviews": len(neg),
                       "neg_avg_star": round(neg_avg, 2), "other_avg_star": round(other_avg, 2),
                       "gap": round(neg_avg - other_avg, 2)})
    impact.sort(key=lambda x: x["gap"])

    # 7장: ASIN별 비교
    asin_rows = []
    for asin in sorted(asin_info):
        ids = [r for r in all_ids if asin_of[r] == asin]
        ats = [t for t in tags if asin_of[t["review_id"]] == asin]
        aw = sum(weight[t["review_id"]] for t in ats)
        stats = [s for s in topic_stats(ats, compare_topics(schema), weight, ids) if s["mentions"] >= args.strength_min]
        best = max(stats, key=lambda s: (s["pos_reviewer_pct"], s["positive"]), default=None)
        worst = max(stats, key=lambda s: (s["neg_reviewer_pct"], s["negative"]), default=None)
        info = asins.get(asin, {})
        asin_rows.append({
            "asin": asin, "brand": info.get("brand", ""), "price_band": info.get("price_band", ""),
            "amazon_rating": info.get("amazon_rating", ""), "tags": len(ats),
            "weighted_pos_pct": pct(sum(weight[t["review_id"]] for t in ats if t["sentiment"] == "positive"), aw),
            "weighted_neg_pct": pct(sum(weight[t["review_id"]] for t in ats if t["sentiment"] == "negative"), aw),
            "strength": best and best["pos_reviewer_pct"] > 0 and
            {"id": best["id"], "name_ko": schema[best["id"]]["name_ko"], "pos_reviewer_pct": best["pos_reviewer_pct"]} or None,
            "weakness": worst and worst["neg_reviewer_pct"] > 0 and
            {"id": worst["id"], "name_ko": schema[worst["id"]]["name_ko"], "neg_reviewer_pct": worst["neg_reviewer_pct"]} or None,
            **asin_info[asin],
        })

    # 공출현(부정 x 부정): v0 리포트에는 안 쓰지만 남겨 둔다
    neg_by_review = defaultdict(set)
    for t in tags:
        if t["sentiment"] == "negative" and t["topic"] not in COMPARE_EXCLUDE:
            neg_by_review[t["review_id"]].add(t["topic"])
    co = Counter()
    for ts in neg_by_review.values():
        for a, b in combinations(sorted(ts), 2):
            co[(a, b)] += 1

    # 5~7장, 10장: 시간 추이, 공출현, 신뢰 신호, 브랜드 심층(전체 만족도는 비교에서 뺌)
    time_trend = sections.time_trend(reviews, tags, weight, COMPARE_EXCLUDE, sections.as_of_date(run.name, args.as_of))
    cooc = sections.cooccurrence(tags, COMPARE_EXCLUDE)
    min_voted = (category_conf(run).get("report") or {}).get("helpful_min_voted_reviews")
    if min_voted is None:
        print("  주의: config/categories/<카테고리>.yaml에 report.helpful_min_voted_reviews가 없어 도움돼요 순위 잠정 표시를 하지 않습니다.")
    trust = sections.trust_signals(reviews, tags, COMPARE_EXCLUDE, min_voted=min_voted)
    brand_of_asin = {a: (asins.get(a, {}).get("brand") or "") for a in asin_info}
    brand_deep = sections.brand_deep(reviews, tags, weight, schema, brand_of_asin, topic_stats, COMPARE_EXCLUDE,
                                     args.strength_min)

    for t in topics:
        del t["_neg_reviews"]
    metrics = {
        "generated_at": now_iso(), "run": run.name, "tags_file": args.tags,
        "rules": {"impact_min_neg_reviews": args.impact_min, "strength_min_mentions": args.strength_min,
                  "compare_exclude_topics": list(COMPARE_EXCLUDE),
                  "rounding": "비율은 소수 첫째 자리 %, 별점은 소수 둘째 자리"},
        "summary": {"asins": len(asin_info), "reviews": len(all_ids), "tags": len(tags),
                    "brands": len({a["brand"] for a in asin_rows if a["brand"]}),
                    "tags_per_review": round(len(tags) / len(all_ids), 2) if all_ids else 0,
                    "sample_mean_star": round(sum(star.values()) / len(all_ids), 2),
                    "weighted_mean_star": round(wavg([(weight[r], eff[r]) for r in all_ids]), 2),
                    "date_min": min((r["date"] for r in reviews if r["date"]), default=""),
                    "date_max": max((r["date"] for r in reviews if r["date"]), default="")},
        "sentiment": {"raw": {s: sent_raw[s] for s in SENTIMENTS},
                      "raw_pct": {s: pct(sent_raw[s], len(tags)) for s in SENTIMENTS},
                      "weighted_pct": {s: pct(sent_w[s], tag_w_total) for s in SENTIMENTS}},
        "side": {"raw": {k: side_raw[k] for k in SIDE_KO}, "raw_pct": {k: pct(side_raw[k], len(tags)) for k in SIDE_KO}},
        "stars": {"sample_counts": {str(s): sample_counts[s] for s in STARS},
                  "real_pct": real_pct, "missing_real_pct": missing_pct},
        "topics": sorted(topics, key=lambda t: (-t["mentions"], t["id"])),
        "impact": impact,
        "asins": asin_rows,
        "cooccurrence_neg": [{"a": a, "b": b, "count": n} for (a, b), n in co.most_common()],
        "weighting": weighting,
        "time_trend": time_trend,
        "cooccurrence": cooc,
        "trust_signals": trust,
        "brand_deep": brand_deep,
    }
    metrics["notes"] = data_notes(run, dist, asin_info, metrics["summary"], weighting)
    if off:
        metrics["off_category"] = {"reviews": len(off), "by_asin": off_by_asin, "review_ids": off}
        metrics["notes"]["off_category_text"] = (
            f"이 카테고리와 무관한 리뷰 {len(off)}개(" + ", ".join(f"{a} {n}개" for a, n in off_by_asin.items())
            + ")는 태거가 off_category로 표시해 모든 집계에서 뺐습니다.")
    prices = run / "01_prices.json"
    if prices.exists():
        metrics["prices"] = json.loads(prices.read_text(encoding="utf-8"))
    # 11장: 변형(용량) 신호. 변형 키는 데이터로 고른다(카테고리와 상관없음)
    metrics["variant_signal"] = sections.variant_signal(reviews, tags, weight, schema, metrics.get("prices"), COMPARE_EXCLUDE)
    metrics["brand_of_asin"] = brand_of_asin
    # 8장과 10장: 세부 이슈 개수(있으면). 숫자는 issues.py label-check가 만든 07b_issue_counts.json 그대로 옮긴다
    counts_path = run / "07b_issue_counts.json"
    if counts_path.exists():
        counts = json.loads(counts_path.read_text(encoding="utf-8"))
        labels_path = run / "07b_issue_labels.jsonl"
        labels = [json.loads(x) for x in labels_path.read_text(encoding="utf-8").splitlines() if x.strip()]             if labels_path.exists() else []
        metrics["issues"] = sections.issue_summary(counts, labels, tags, reviews)
        metrics["issue_overlap"] = counts.get("overlap")
        for b in brand_deep:
            for s_ in b["strengths"]:
                s_["top_issues"] = sections.brand_issues(counts, b["asins"], s_["id"], "positive")
            for s_ in b["weaknesses"]:
                s_["top_issues"] = sections.brand_issues(counts, b["asins"], s_["id"], "negative")
    safety_path = run / "07c_safety_summary.json"
    if safety_path.exists():
        metrics["safety_check"] = json.loads(safety_path.read_text(encoding="utf-8"))
    gold = run / "04_gold_eval.json"
    if gold.exists():
        metrics["accuracy"] = gold_accuracy(json.loads(gold.read_text(encoding="utf-8")))
    rob = run / "05_robustness.json"
    if rob.exists():          # robustness.py가 만든 견고성 점검(부록 문장용 표기와 요약)
        r = json.loads(rob.read_text(encoding="utf-8"))
        metrics["robustness"] = {"texts": r["texts"], "bootstrap": r["bootstrap"], "base": r["base"],
                                 "leave_one_out_flips": sum(1 for x in r["leave_one_out"][1:] if x["flips"]),
                                 "leave_one_out_runs": len(r["leave_one_out"]) - 1,
                                 "leave_one_out_head_neg": [x["head_neg"] for x in r["leave_one_out"][1:]],
                                 "leave_one_out_head_neg_text": f"{min(x['head_neg'] for x in r['leave_one_out'][1:]):.1f}%~"
                                                                f"{max(x['head_neg'] for x in r['leave_one_out'][1:]):.1f}%"}
    write_json(run / "05_metrics.json", metrics)
    (run / "05_tables.md").write_text(render_tables({**metrics, "_schema_names": schema}), encoding="utf-8")
    s = metrics["summary"]
    print(f"집계 완료: 리뷰 {s['reviews']}개, 태그 {s['tags']}개, 표본 평균 {s['sample_mean_star']}★, "
          f"가중 평균 {s['weighted_mean_star']}★. 자체 검사 통과(ASIN {s['asins']}개).")
    for w in weighting["warnings"]:
        print(f"  주의: {w}")


def render_tables(m):
    """리포트에 그대로 붙일 표. 블록 이름은 report_template_ko.md의 {{표: 이름}}과 같다."""
    blocks = []

    def block(name, lines):
        blocks.append(f"<!-- 표:{name} -->\n" + "\n".join(lines) + f"\n<!-- /표:{name} -->")

    s = m["summary"]
    period = f", 리뷰 기간 {s['date_min']} ~ {s['date_max']}" if s.get("date_min") else ""
    block("요약", [f"ASIN {s['asins']}개, 리뷰 {s['reviews']:,}개, 태그 {s['tags']:,}개, 가중 평균 {fmt_star(s['weighted_mean_star'])}, "
                 f"브랜드 {s['brands']}개{period}"])

    se, sd, st = m["sentiment"], m["side"], m["stars"]
    ko = {"positive": "긍정", "negative": "부정", "mixed": "혼합", "neutral": "중립"}
    block("분포", [
        "- 감성 구성: " + ", ".join(f"{ko[k]} {se['raw'][k]}({fmt_pct(se['raw_pct'][k])})" for k in SENTIMENTS)
        + f". 가중하면 긍정 {fmt_pct(se['weighted_pct']['positive'])}, 부정 {fmt_pct(se['weighted_pct']['negative'])}.",
        "- 제품 대 브랜드: " + ", ".join(f"{SIDE_KO[k]} {sd['raw'][k]}({fmt_pct(sd['raw_pct'][k])})" for k in SIDE_KO),
        "- 별점 분포: 표본 " + ", ".join(f"{k}★ {st['sample_counts'][str(k)]}개" for k in STARS)
        + f"(평균 {fmt_star(s['sample_mean_star'])}). 실제 " + ", ".join(f"{k}★ {fmt_pct(st['real_pct'][str(k)])}" for k in STARS)
        + f"(가중 평균 {fmt_star(s['weighted_mean_star'])})."
        + (f" 표본이 없는 묶음의 실제 비율 {fmt_pct(st['missing_real_pct'])}는 빠짐(ASIN 표본 수로 가중)."
           if st["missing_real_pct"] else ""),
        "",
        *weights_table(m["weighting"]),
        "",
        disclosure(m["weighting"]),
    ])

    shown = [t for t in m["topics"] if t["mentions"] > 0]
    block("주제별 언급", ["| 구분 | 주제 | 언급 수 | 부정 비율 |", "|---|---|---|---|"]
          + [f"| {SIDE_KO[t['side']]} | {t['name_ko']} | {t['mentions']} | {fmt_pct(t['neg_pct'])} |" for t in shown])
    block("주제 평가", ["| 구분 | 주제 | 언급 | 긍정 | 부정 | 혼합 | 중립 | 부정 비율 | 가중 부정 비율 | 부정 언급 리뷰어(가중) |",
                     "|---|---|---|---|---|---|---|---|---|---|"]
          + [f"| {SIDE_KO[t['side']]} | {t['name_ko']} | {t['mentions']} | {t['positive']} | {t['negative']} | {t['mixed']} | "
             f"{t['neutral']} | {fmt_pct(t['neg_pct'])} | {fmt_pct(t['weighted_neg_pct'])} | {fmt_pct(t['neg_reviewer_pct'])} |"
             for t in shown])

    n = m["rules"]["impact_min_neg_reviews"]
    impact_note = (f"부정 언급 리뷰 {n}개 이상인 주제만. 전체 만족도는 리뷰 단위 총평이라 별점과 같은 뜻이 되어 이 표에서 뺍니다.")
    if m["impact"]:
        block("영향 분석", ["| 주제 | 부정 언급 리뷰 | 그 리뷰의 가중 평균 | 나머지 리뷰의 가중 평균 | 격차 |", "|---|---|---|---|---|"]
              + [f"| {t['name_ko']} | {t['neg_reviews']} | {fmt_star(t['neg_avg_star'])} | {fmt_star(t['other_avg_star'])} | "
                 f"{t['gap']:+.2f} |" for t in m["impact"]] + ["", impact_note])
    else:
        block("영향 분석", [f"부정 언급 리뷰가 {n}개 이상인 주제가 없습니다(전체 만족도 제외)."])

    block("시간 추이", sections.render_time(m["time_trend"], m["_schema_names"]))
    block("공출현", sections.render_cooc(m["cooccurrence"], m["_schema_names"]))
    block("신뢰 신호", sections.render_trust(m["trust_signals"], m["_schema_names"]))
    block("브랜드 심층", sections.render_brand(m["brand_deep"]))
    block("세부 이슈", sections.render_issues(m["issues"], m["_schema_names"], m.get("issue_overlap"), m.get("safety_check"))
          if m.get("issues") else ["세부 이슈 라벨이 아직 없습니다(07b_issue_counts.json 없음)."])
    block("변형 신호", sections.render_variant(m["variant_signal"], m["_schema_names"], m.get("brand_of_asin", {})))

    def sw(x, key):
        return f"{x['name_ko']}({fmt_pct(x[key])})" if x else "없음"

    block("ASIN별 비교", ["| ASIN | 브랜드 | 가격대 | 표본 리뷰 | 아마존 평균 별점 | 태그 | 긍정/부정(가중) | 가장 큰 강점* | 가장 큰 약점* |",
                        "|---|---|---|---|---|---|---|---|---|"]
          + [f"| {a['asin']} | {a['brand']} | {a['price_band']} | {a['sample_reviews']} | {a['amazon_rating'] or '-'} | {a['tags']} | "
             f"{fmt_pct(a['weighted_pos_pct'])} / {fmt_pct(a['weighted_neg_pct'])} | {sw(a['strength'], 'pos_reviewer_pct')} | "
             f"{sw(a['weakness'], 'neg_reviewer_pct')} |" for a in m["asins"]]
          + ["", f"\\* 그 ASIN에서 언급 {m['rules']['strength_min_mentions']}개 이상인 주제(전체 만족도 제외) 중 그 ASIN 리뷰어가 "
                 "가장 많이 칭찬한 주제와 비판한 주제. 괄호는 그 ASIN 리뷰어 중 해당 주제를 칭찬 또는 비판한 비율(가중)."]
          + ([f"가격대는 그 상품의 용량별 변형의 현재 바이박스 가격 범위(spd-amz-market, {m['prices']['checked_on']} 조회)."]
             if m.get("prices") else []))
    return "\n\n".join(blocks) + "\n"


if __name__ == "__main__":
    main()
