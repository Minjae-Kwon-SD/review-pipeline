"""weight.py가 쓰는 정답지 장 4개(시간 추이, 공출현, 신뢰 신호, 브랜드 심층)의 계산과 표. 단독으로 실행하지 않는다.

모든 비교에서 전체 만족도(COMPARE_EXCLUDE)는 뺀다. 숫자는 여기서만 만들고 report-writer는 옮기기만 한다.
"""
import re
from collections import Counter, defaultdict
from datetime import date
from itertools import combinations

from pipeline_io import SENTIMENTS, STARS, fmt_pct, pct

GROUP_OF_STAR = {1: "negative", 2: "negative", 3: "neutral", 4: "positive", 5: "positive"}
GROUP_KO = {"negative": "부정(1,2★)", "neutral": "중립(3★)", "positive": "긍정(4,5★)"}


def as_of_date(run_name, override=None):
    """기준 날짜: --as-of, 아니면 회차 이름 끝의 YYYY-MM-DD, 아니면 오늘."""
    if override:
        return date.fromisoformat(override)
    m = re.search(r"(\d{4}-\d{2}-\d{2})$", run_name)
    return date.fromisoformat(m.group(1)) if m else date.today()


def periods_for(as_of):
    """기간 4개. 최근 분기는 기준 날짜가 든 분기가 아니라 그 직전에 끝난 분기다(진행 중인 분기는 리뷰가 덜 모여서 뺀다).
    예: 기준 2026-10-07 → 끝난 분기 2026년 7~9월. 기간: ~2024년, 2025년, 2026년 1~6월, 2026년 7~9월.
    끝난 분기가 그해 1분기면 올해 앞부분 기간은 비어서 빠진다. 끝난 분기가 작년이면(기준이 1분기) 작년을 그 분기 앞까지로 줄인다.
    돌려주는 값: [(이름, 시작일, 끝일)], 진행 중 분기 시작일"""
    q = (as_of.month - 1) // 3                      # 0~3, 기준 날짜가 든 분기
    cur_start = date(as_of.year, 3 * q + 1, 1)
    if q == 0:
        ly, lq = as_of.year - 1, 3
    else:
        ly, lq = as_of.year, q - 1
    last_start = date(ly, 3 * lq + 1, 1)
    last_end = date(ly, 3 * lq + 3, 30 if 3 * lq + 3 in (6, 9) else 31)
    y = ly
    out = [(f"~{y - 2}년", date(1900, 1, 1), date(y - 2, 12, 31)),
           (f"{y - 1}년", date(y - 1, 1, 1), date(y - 1, 12, 31))]
    if last_start.month > 1:
        out.append((f"{y}년 1~{last_start.month - 1}월", date(y, 1, 1), date(y, last_start.month - 1, 30 if last_start.month - 1 in (6, 9) else 31)))
    out.append((f"{y}년 {last_start.month}~{last_end.month}월", last_start, last_end))
    return out, cur_start


def time_trend(reviews, tags, weight, exclude, as_of):
    pers, cur_start = periods_for(as_of)
    rows = []
    neg_tags_by_review = defaultdict(list)
    for t in tags:
        if t["sentiment"] == "negative" and t["topic"] not in exclude:
            neg_tags_by_review[t["review_id"]].append(t["topic"])
    for name, start, end in pers:
        rs = [r for r in reviews if r["date"] and start.isoformat() <= r["date"] <= end.isoformat()]
        n = len(rs)
        stars = Counter(int(r["star"]) for r in rs)
        wsum = sum(weight[r["review_id"]] for r in rs)
        wgroup = {g: pct(sum(weight[r["review_id"]] for r in rs if GROUP_OF_STAR[int(r["star"])] == g), wsum)
                  for g in ("negative", "neutral", "positive")}
        neg = Counter(tp for r in rs for tp in neg_tags_by_review.get(r["review_id"], []))
        total_neg = sum(neg.values())
        rows.append({"period": name, "start": start.isoformat(), "end": end.isoformat(), "reviews": n,
                     "star_counts": {str(s): stars[s] for s in STARS},
                     "sample_mean_star": round(sum(int(r["star"]) for r in rs) / n, 2) if n else None,
                     "weighted_group_pct": wgroup, "negative_tags": total_neg,
                     "neg_topic_share": {tp: pct(c, total_neg) for tp, c in neg.most_common()}})
    in_progress = sum(1 for r in reviews if r["date"] and r["date"] >= cur_start.isoformat())
    return {"as_of": as_of.isoformat(), "rule": "최근 분기는 기준 날짜가 든 분기가 아니라 그 직전에 끝난 분기. 진행 중인 분기의 리뷰는 기간에서 뺌",
            "in_progress_from": cur_start.isoformat(), "in_progress_reviews": in_progress, "periods": rows}


def cooccurrence(tags, exclude, top_neg=8, top_pos=5):
    by = defaultdict(lambda: defaultdict(set))
    for t in tags:
        if t["topic"] not in exclude:
            by[t["sentiment"]][t["review_id"]].add(t["topic"])
    out = {}
    for sent, k in (("negative", top_neg), ("positive", top_pos)):
        c = Counter()
        for ts in by[sent].values():
            for a, b in combinations(sorted(ts), 2):
                c[(a, b)] += 1
        out[sent] = [{"a": a, "b": b, "reviews": n} for (a, b), n in sorted(c.items(), key=lambda x: (-x[1], x[0]))[:k]]
    return out


def _hv(r):
    try:
        return int(r.get("helpful_votes") or 0)
    except ValueError:
        return 0


def trust_signals(reviews, tags, exclude, top=8, min_voted=None):
    """min_voted: 도움돼요를 1표 이상 받은 리뷰가 이 수보다 적으면 도움돼요 순위를 잠정(helpful_provisional)으로 표시"""
    def block(rs):
        n = len(rs)
        return {"reviews": n, "mean_star": round(sum(int(r["star"]) for r in rs) / n, 2) if n else None,
                "negative_pct": pct(sum(1 for r in rs if int(r["star"]) <= 2), n)}
    ver = [r for r in reviews if r["verified"] == "true"]
    unver = [r for r in reviews if r["verified"] != "true"]
    vine = [r for r in reviews if r["vine"] == "true"]
    total_hv = sum(_hv(r) for r in reviews)
    neg_hv = sum(_hv(r) for r in reviews if int(r["star"]) <= 2)
    pos_hv = sum(_hv(r) for r in reviews if int(r["star"]) >= 4)
    hv_of = {r["review_id"]: _hv(r) for r in reviews}
    topic_hv = Counter()
    for t in tags:
        if t["sentiment"] == "negative" and t["topic"] not in exclude:
            topic_hv[t["topic"]] += hv_of.get(t["review_id"], 0)
    neg_tag_hv = sum(topic_hv.values())
    top_reviews = sorted(reviews, key=lambda r: (-_hv(r), r["review_id"]))[:top]
    return {"verified": block(ver), "unverified": block(unver), "vine": block(vine),
            "helpful_total": total_hv, "helpful_reviews": sum(1 for r in reviews if _hv(r) > 0),
            "helpful_min_voted": min_voted,
            "helpful_provisional": min_voted is not None and sum(1 for r in reviews if _hv(r) > 0) < min_voted,
            "helpful_negative_reviews": neg_hv, "helpful_positive_reviews": pos_hv,
            "helpful_negative_pct": pct(neg_hv, neg_hv + pos_hv), "helpful_positive_pct": pct(pos_hv, neg_hv + pos_hv),
            "helpful_weighted_complaints": [{"topic": tp, "votes": v, "share_pct": pct(v, neg_tag_hv)}
                                            for tp, v in sorted(topic_hv.items(), key=lambda x: (-x[1], x[0])) if v > 0],
            "top_helpful": [{"review_id": r["review_id"], "asin": r["asin"], "star": int(r["star"]), "title": r["title"],
                             "votes": _hv(r)} for r in top_reviews if _hv(r) > 0]}


def brand_deep(reviews, tags, weight, schema, brand_of_asin, topic_stats, exclude, strength_min, top=8):
    """브랜드마다 상위 주제(언급 순, 전체 만족도 제외), 강점 2와 약점 2(그 브랜드 언급 strength_min개 이상),
    그리고 강점과 약점마다 인용 후보(도움돼요 많은 순, 같은 감성 태그)."""
    asin_of = {r["review_id"]: r["asin"] for r in reviews}
    star = {r["review_id"]: int(r["star"]) for r in reviews}
    hv = {r["review_id"]: _hv(r) for r in reviews}
    topics = [t for t in schema if t not in exclude]
    out = []
    for brand in sorted({b for b in brand_of_asin.values() if b}):
        asins = {a for a, b in brand_of_asin.items() if b == brand}
        ids = [r["review_id"] for r in reviews if r["asin"] in asins]
        bts = [t for t in tags if asin_of[t["review_id"]] in asins]
        stats = [s for s in topic_stats(bts, topics, weight, ids) if s["mentions"] > 0]
        for s in stats:
            s.pop("_neg_reviews", None)
            s["name_ko"] = schema[s["id"]]["name_ko"]
        top_rows = sorted(stats, key=lambda s: (-s["mentions"], s["id"]))[:top]
        eligible = [s for s in stats if s["mentions"] >= strength_min]
        strengths = sorted([s for s in eligible if s["pos_reviewer_pct"] > 0],
                           key=lambda s: (-s["pos_reviewer_pct"], -s["positive"], s["id"]))[:2]
        weaknesses = sorted([s for s in eligible if s["neg_reviewer_pct"] > 0],
                            key=lambda s: (-s["neg_reviewer_pct"], -s["negative"], s["id"]))[:2]

        def quotes(topic, sent, k=3):
            cand = [t for t in bts if t["topic"] == topic and t["sentiment"] == sent]
            cand.sort(key=lambda t: (-hv[t["review_id"]], t["review_id"]))
            return [{"review_id": t["review_id"], "star": star[t["review_id"]], "quote": t["quote"],
                     "helpful_votes": hv[t["review_id"]]} for t in cand[:k]]
        out.append({"brand": brand, "asins": sorted(asins), "reviews": len(ids),
                    "top_topics": [{k: s[k] for k in ("id", "name_ko", "mentions", "positive", "negative", "mixed", "neutral", "neg_pct",
                                                      "weighted_neg_pct", "pos_reviewer_pct", "neg_reviewer_pct")}
                                   for s in top_rows],
                    "strengths": [{"id": s["id"], "name_ko": s["name_ko"], "mentions": s["mentions"],
                                   "pos_reviewer_pct": s["pos_reviewer_pct"], "quote_candidates": quotes(s["id"], "positive")}
                                  for s in strengths],
                    "weaknesses": [{"id": s["id"], "name_ko": s["name_ko"], "mentions": s["mentions"],
                                    "neg_reviewer_pct": s["neg_reviewer_pct"], "quote_candidates": quotes(s["id"], "negative")}
                                   for s in weaknesses]})
    return out


# ---------------------------------------------------------------- 변형(용량) 신호

ML_PER_OZ = 29.5735


def variant_parts(text):
    """'Size: 1 Fl Oz (Pack of 1); Scent: Rose' → {'Size': '1 Fl Oz (Pack of 1)', 'Scent': 'Rose'}"""
    out = {}
    for part in str(text or "").split(";"):
        if ":" in part:
            k, v = part.split(":", 1)
            out[k.strip()] = v.strip()
    return out


def parse_size(value):
    """용량 문자열에서 (fl oz, 묶음 수). 못 읽으면 (None, 1). ml은 fl oz로 바꾼다."""
    s = str(value or "")
    pack = re.search(r"pack\s+of\s+(\d+)", s, re.I)
    pack = int(pack.group(1)) if pack else 1
    m = re.search(r"([\d.]+)\s*(?:fl\.?\s*oz|fluid\s+ounces?|ounces?|oz)\b", s, re.I)
    if m:
        return float(m.group(1)), pack
    m = re.search(r"([\d.]+)\s*ml\b", s, re.I)
    if m:
        return round(float(m.group(1)) / ML_PER_OZ, 2), pack
    return None, pack


def size_label(oz, pack):
    return f"{oz:g} fl oz" + (f" x{pack}" if pack > 1 else "")


def is_size_key(key):
    return str(key).lower() in ("size", "volume", "capacity")


def norm_variant(key, value):
    """변형 값을 비교용 이름으로. 용량 키면 같은 용량의 다른 표기를 합친다. (이름, fl oz, 묶음 수)"""
    if is_size_key(key):
        oz, pack = parse_size(value)
        if oz:
            return size_label(oz, pack), oz, pack
    return value, None, 1


def choose_variant_key(reviews, min_reviews):
    """변형 텍스트의 키마다 '리뷰 min_reviews개 이상인 변형이 2개 이상인 ASIN 수'를 세어 가장 많은 키를 고른다.
    카테고리와 상관없이 동작한다(향수면 Size, 옷이면 Size나 Color 등). 돌려주는 값: (키, {키: ASIN 수})"""
    counts = defaultdict(lambda: defaultdict(Counter))
    for r in reviews:
        for k, v in variant_parts(r.get("variant_text")).items():
            counts[k][r["asin"]][norm_variant(k, v)[0]] += 1
    score = {k: sum(1 for c in by_asin.values() if sum(1 for n in c.values() if n >= min_reviews) >= 2)
             for k, by_asin in counts.items()}
    if not score or max(score.values()) == 0:
        return None, score
    return sorted(score, key=lambda k: (-score[k], k))[0], score


def variant_signal(reviews, tags, weight, schema, prices, exclude, min_reviews=15, min_tags=12, topic_min=10):
    key, score = choose_variant_key(reviews, min_reviews)
    out = {"key": key, "key_scores": score, "rules": {"min_reviews": min_reviews, "min_tags": min_tags, "topic_min": topic_min},
           "checked_on": (prices or {}).get("checked_on"), "asins": []}
    if not key:
        return out
    price_by_variant = {}
    for a, p in ((prices or {}).get("asins") or {}).items():
        for v in p.get("variants") or []:
            if v.get("asin") and v.get("buyBoxPrice"):
                price_by_variant[v["asin"]] = float(v["buyBoxPrice"])
    tags_by_review = defaultdict(list)
    for t in tags:
        tags_by_review[t["review_id"]].append(t)
    for asin in sorted({r["asin"] for r in reviews}):
        rs = [r for r in reviews if r["asin"] == asin]
        groups = defaultdict(list)
        for r in rs:
            v = variant_parts(r.get("variant_text")).get(key)
            if not v:
                continue
            label, oz, pack = norm_variant(key, v)
            groups[label].append((r, oz, pack))
        kept = {lab: g for lab, g in groups.items() if len(g) >= min_reviews}
        if len(kept) < 2:
            continue
        mentions = Counter(t["topic"] for r in rs for t in tags_by_review[r["review_id"]] if t["topic"] not in exclude)
        topics = [tp for tp, n in sorted(mentions.items(), key=lambda x: (-x[1], x[0])) if n >= topic_min]
        rows, hidden = [], []
        for lab, g in kept.items():
            ids = [r["review_id"] for r, _, _ in g]
            n_tags = sum(len(tags_by_review[i]) for i in ids)
            if n_tags < min_tags:
                hidden.append(lab)
                continue
            oz, pack = g[0][1], g[0][2]
            vasin = Counter(r.get("variant_asin") for r, _, _ in g).most_common(1)[0][0]
            price = price_by_variant.get(vasin)
            wsum = sum(weight[i] for i in ids)
            neg = {}
            for tp in topics:
                negw = sum(weight[i] for i in ids if any(t["topic"] == tp and t["sentiment"] == "negative"
                                                         for t in tags_by_review[i]))
                neg[tp] = pct(negw, wsum)
            rows.append({"variant": lab, "variant_asin": vasin, "oz": oz, "pack": pack, "reviews": len(ids), "tags": n_tags,
                         "price": price, "price_per_oz": round(price / (oz * pack), 2) if price and oz else None,
                         "neg_reviewer_pct": neg})
        rows.sort(key=lambda x: (x["oz"] is None, x["oz"] or 0, x["variant"]))
        out["asins"].append({"asin": asin, "variants_total": len(groups), "variants_shown": len(rows),
                             "hidden_low_tags": hidden, "topics": topics, "rows": rows})
    return out


def render_variant(vs, schema, brand_of_asin):
    if not vs["key"]:
        return ["변형으로 나눌 수 있는 상품이 없습니다(리뷰 15개 이상인 변형이 2개 이상인 ASIN 없음)."]
    lines = []
    for a in vs["asins"]:
        if not a["rows"]:
            continue
        names = [schema[tp]["name_ko"] for tp in a["topics"]]
        lines += [f"**{brand_of_asin.get(a['asin'], '')}** ({a['asin']}, {vs['key']} 변형 {a['variants_total']}개 중 {a['variants_shown']}개)", "",
                  "| 변형 | 리뷰 | 태그 | 현재 가격 | 온스당 가격 | " + " | ".join(names) + " |",
                  "|---|---|---|---|---|" + "---|" * len(names)]
        for r in a["rows"]:
            price = f"{r['price']:.2f}달러" if r["price"] else "가격 없음"
            per = f"{r['price_per_oz']:.2f}달러" if r["price_per_oz"] else "-"
            lines.append(f"| {r['variant']} | {r['reviews']} | {r['tags']} | {price} | {per} | "
                         + " | ".join(fmt_pct(r["neg_reviewer_pct"][tp]) for tp in a["topics"]) + " |")
        lines.append("")
    rl = vs["rules"]
    lines.append(f"변형 키는 {vs['key']}(리뷰 {rl['min_reviews']}개 이상인 변형이 2개 이상인 ASIN 수가 가장 많은 키). "
                 f"리뷰 {rl['min_reviews']}개 이상인 변형만, 태그 {rl['min_tags']}개 미만인 변형은 숨김. 주제는 그 ASIN에서 언급 {rl['topic_min']}개 이상"
                 "(전체 만족도 제외)이고, 값은 그 변형 리뷰 중 그 주제를 부정으로 말한 리뷰의 비율(가중)입니다. "
                 f"가격은 현재 바이박스 가격(spd-amz-market, {vs['checked_on'] or '날짜 없음'} 조회)이라 리뷰 시점 가격과 다를 수 있습니다. "
                 "같은 ASIN 안에서만 비교하고, 리뷰 수가 적은 변형은 순위로 읽지 않습니다.")
    return lines


# ---------------------------------------------------------------- 세부 이슈(07b_issue_counts.json)

def issue_summary(counts, labels=None, tags=None, reviews=None, top=3, k=2):
    """주제와 방향마다 상위 라벨(기타 제외), 라벨 전체 개수, 기타 비율. 숫자는 07b_issue_counts.json 그대로.
    labels(07b_issue_labels.jsonl)와 태그가 있으면 라벨마다 인용 후보 k개(도움돼요 많은 순, 같은 주제 태그의 quote)."""
    quote = {(t["review_id"], t["topic"]): t["quote"] for t in (tags or [])}
    star = {r["review_id"]: int(r["star"]) for r in (reviews or [])}
    hv = {r["review_id"]: _hv(r) for r in (reviews or [])}
    by_label = defaultdict(list)
    for m in labels or []:
        for lab in m["labels"]:
            by_label[(m["topic"], m["direction"], lab)].append(m["review_id"])
    out = {}
    for key, v in (counts or {}).get("topics", {}).items():
        rows = []
        for l in v["labels"]:
            if l["id"] == "other" or l["reviews"] <= 0:
                continue
            ids = sorted(set(by_label[(v["topic"], v["direction"], l["id"])]), key=lambda r: (-hv.get(r, 0), r))
            rows.append({"id": l["id"], "name_ko": l["name_ko"], "reviews": l["reviews"], "weighted_pct": l["weighted_pct"],
                         "quote_candidates": [{"review_id": r, "star": star.get(r), "quote": quote.get((r, v["topic"]), "")}
                                              for r in ids[:k] if (r, v["topic"]) in quote]})
        out[key] = {"topic": v["topic"], "direction": v["direction"], "units": v["units"], "other_pct": v["other_pct"],
                    "top": [{x: r[x] for x in ("id", "name_ko", "reviews", "weighted_pct")} for r in rows[:top]],
                    "labels": rows}
    return out


def brand_issues(counts, asins, topic, direction, top=3):
    """브랜드(ASIN 집합) 안에서 그 주제와 방향의 라벨별 리뷰 수 상위(기타 제외)."""
    v = (counts or {}).get("topics", {}).get(f"{topic}.{direction}")
    if not v:
        return []
    rows = [{"id": l["id"], "name_ko": l["name_ko"], "reviews": sum(l["by_asin"].get(a, 0) for a in asins)}
            for l in v["labels"] if l["id"] != "other"]
    return sorted([r for r in rows if r["reviews"] > 0], key=lambda r: (-r["reviews"], r["id"]))[:top]


def render_issues(summary, schema, overlap, safety):
    ko = {"negative": "부정 이슈", "positive": "긍정 이슈"}
    lines = ["| 주제 | 방향 | 세부 이슈(리뷰 수, 가중 비율) | 기타 비율 |", "|---|---|---|---|"]
    for key in sorted(summary, key=lambda k: (summary[k]["direction"] != "negative", -summary[k]["units"])):
        s = summary[key]
        top = ", ".join(f"{l['name_ko']} 리뷰 {l['reviews']}개({fmt_pct(l['weighted_pct'])})" for l in s["top"]) or "기타만"
        other = fmt_pct(s["other_pct"])
        if key == "safety.negative" and safety and safety.get("by_symptom"):   # 안전 부정은 라벨 대신 증상별(07c)
            top = ", ".join(f"{x['name']} 리뷰 {x['reviews']}개({fmt_pct(x['weighted_pct'])})" for x in safety["by_symptom"])
            if safety.get("negative_no_symptom"):
                top += f", 이상 반응 없음 리뷰 {safety['negative_no_symptom']}개"
            other = "증상별 분류(07c)"
        lines.append(f"| {schema[s['topic']]['name_ko']} | {ko[s['direction']]} | {top} | {other} |")
    lines.append("")
    if overlap:
        na, nb = overlap.get("names") or ["원래 알던 향과 다름", "정품과 향이 다름"]
        lines.append(f"향 부정 \"{na}\"과 신뢰 부정 \"{nb}\"이 함께 붙은 리뷰 {overlap['reviews']}개"
                     f"({fmt_pct(overlap['weighted_pct'])}, 가중).")
    if safety and safety.get("negative_text"):
        lines.append(f"{safety['negative_text']}(07c_safety_check.md, 알레르기 언급은 본인 반응을 직접 묘사하지 않은 리뷰).")
    elif safety:
        lines.append(f"안전 부정 인용 {safety['negative_symptom'] + safety['negative_no_symptom']}개 중 이상 반응 {safety['negative_symptom']}개, "
                     f"나머지 {safety['negative_no_symptom']}개(07c_safety_check.md).")
    lines.append("주제와 방향마다 리뷰 수 상위 3개(기타 제외). 리뷰 하나는 라벨마다 한 번 셉니다. 가중 비율은 그 라벨이 붙은 리뷰의 가중치 합 ÷ 전체 리뷰 "
                 "가중치 합. 기타 비율은 그 주제와 방향의 인용 중 승인 라벨에 들지 않은 비율. 전체 만족도는 나누지 않습니다. "
                 "안전 부정은 라벨 대신 증상별 분류 전부(07c)를 적습니다.")
    return lines


# ---------------------------------------------------------------- 표

def render_time(tt, schema):
    pers = tt["periods"]
    name = lambda tp: schema[tp]["name_ko"] if tp in schema else tp
    head = "| 구분 | " + " | ".join(p["period"] for p in pers) + " |"
    sep = "|---|" + "---|" * len(pers)
    lines = [head, sep,
             "| 리뷰 수 | " + " | ".join(str(p["reviews"]) for p in pers) + " |",
             "| 표본 1~5★ | " + " | ".join("/".join(str(p["star_counts"][str(s)]) for s in STARS) for p in pers) + " |",
             "| 표본 평균 별점 | " + " | ".join(f"{p['sample_mean_star']:.2f}★" if p["sample_mean_star"] is not None else "-"
                                          for p in pers) + " |"]
    for g in ("negative", "neutral", "positive"):
        lines.append(f"| 가중 {GROUP_KO[g]} | " + " | ".join(fmt_pct(p["weighted_group_pct"][g]) if p["reviews"] else "-"
                                                      for p in pers) + " |")
    lines.append("| 부정 태그 수 | " + " | ".join(str(p["negative_tags"]) for p in pers) + " |")
    topics = []
    for p in pers:
        for tp in p["neg_topic_share"]:
            if tp not in topics:
                topics.append(tp)
    total = Counter()
    for p in pers:
        for tp, v in p["neg_topic_share"].items():
            total[tp] += v
    topics.sort(key=lambda tp: -total[tp])
    lines.append("")
    lines.append("| 부정 태그 중 주제 비중 | " + " | ".join(p["period"] for p in pers) + " |")
    lines.append(sep)
    for tp in topics:
        lines.append(f"| {name(tp)} | " + " | ".join(fmt_pct(p["neg_topic_share"].get(tp, 0.0)) if p["negative_tags"] else "-"
                                                for p in pers) + " |")
    lines += ["", f"기간은 {tt['as_of']} 기준. 최근 분기는 끝난 분기({pers[-1]['period']})이고, 진행 중인 분기({tt['in_progress_from']}부터)의 "
                  f"리뷰 {tt['in_progress_reviews']}개는 뺐습니다. 리뷰는 공유 DB에 모인 표본이라, 오래된 기간일수록 별점을 골라 모은 "
                  "리뷰(낮은 별점 위주)만 남았을 수 있어 기간 사이 비교는 참고용입니다. 가중 비율은 각 ASIN의 실제 별점 분포로 되돌린 값입니다."]
    return lines


def render_cooc(co, schema):
    name = lambda tp: schema[tp]["name_ko"]
    lines = ["| 구분 | 주제 쌍 | 함께 나온 리뷰 수 |", "|---|---|---|"]
    for sent, label in (("negative", "부정 x 부정"), ("positive", "긍정 x 긍정")):
        for x in co[sent]:
            lines.append(f"| {label} | {name(x['a'])} + {name(x['b'])} | {x['reviews']} |")
        if not co[sent]:
            lines.append(f"| {label} | 없음 | 0 |")
    lines += ["", "같은 리뷰 안에서 두 주제가 같은 감성으로 함께 태깅된 리뷰 수(원본). 부정 x 부정 상위 8개, 긍정 x 긍정 상위 5개. "
                  "전체 만족도는 뺍니다. 함께 나온다는 뜻이며 원인 관계가 아닙니다."]
    return lines


def render_trust(ts, schema):
    name = lambda tp: schema[tp]["name_ko"]

    def row(label, b):
        if not b["reviews"]:
            return f"| {label} | 0 | - | - |"
        return f"| {label} | {b['reviews']} | {b['mean_star']:.2f}★ | {fmt_pct(b['negative_pct'])} |"
    lines = ["| 구분 | 리뷰 수 | 평균 별점(원본) | 1~2★ 비율(원본) |", "|---|---|---|---|",
             row("확인된 구매", ts["verified"]), row("확인 안 된 구매", ts["unverified"]), row("Vine", ts["vine"]),
             "",
             f"도움돼요: 합계 {ts['helpful_total']}표(1표 이상 받은 리뷰 {ts['helpful_reviews']}개). "
             f"1~2★ 리뷰가 {ts['helpful_negative_reviews']}표({fmt_pct(ts['helpful_negative_pct'])}), "
             f"4~5★ 리뷰가 {ts['helpful_positive_reviews']}표({fmt_pct(ts['helpful_positive_pct'])})를 받았습니다(3★ 제외).",
             "", "| 순위 | 불만 주제(도움돼요 가중)" + (" (잠정)" if ts.get("helpful_provisional") else "") + " | 도움돼요 표 | 비중 |", "|---|---|---|---|"]
    lines += [f"| {i} | {name(x['topic'])} | {x['votes']} | {fmt_pct(x['share_pct'])} |"
              for i, x in enumerate(ts["helpful_weighted_complaints"][:8], 1)]
    lines += ["", "| 순위 | 별점 | 제목(원문) | 도움돼요 | review_id |", "|---|---|---|---|---|"]
    lines += [f"| {i} | {x['star']}★ | {x['title'].replace('|', '/')} | {x['votes']} | {x['review_id']} |"
              for i, x in enumerate(ts["top_helpful"], 1)]
    lines += ["", f"표본은 별점을 골라 모은 것이라 이 장의 숫자는 원본(가중 안 함)입니다. Vine 리뷰는 {ts['vine']['reviews']}개뿐이라 참고용입니다. "
                  "불만 주제 순위는 그 주제를 부정으로 말한 리뷰가 받은 도움돼요 표의 합입니다(전체 만족도 제외)."
              + (f" 표를 받은 리뷰가 {ts['helpful_reviews']}개로 기준 {ts['helpful_min_voted']}개보다 적어 순위는 잠정이고 해석하지 않습니다."
                 if ts.get("helpful_provisional") else "")]
    return lines


def render_brand(bd):
    lines = []
    for b in bd:
        lines += [f"**{b['brand']}** (ASIN {', '.join(b['asins'])}, 리뷰 {b['reviews']}개)", "",
                  "| 주제 | 언급 | 부정 비율 | 가중 부정 비율 |", "|---|---|---|---|"]
        lines += [f"| {t['name_ko']} | {t['mentions']} | {fmt_pct(t['neg_pct'])} | {fmt_pct(t['weighted_neg_pct'])} |"
                  for t in b["top_topics"]]
        def iss(s):
            xs = s.get("top_issues") or []
            return ("; 세부: " + ", ".join(f"{x['name_ko']} 리뷰 {x['reviews']}개" for x in xs)) if xs else ""
        st = ", ".join(f"{s['name_ko']}(긍정 언급 리뷰어 {fmt_pct(s['pos_reviewer_pct'])}{iss(s)})" for s in b["strengths"]) or "없음"
        wk = ", ".join(f"{s['name_ko']}(부정 언급 리뷰어 {fmt_pct(s['neg_reviewer_pct'])}{iss(s)})" for s in b["weaknesses"]) or "없음"
        lines += ["", f"강점 후보: {st}. 약점 후보: {wk}.", ""]
    lines.append("주제는 그 브랜드의 언급 수 상위 8개(전체 만족도 제외). 강점과 약점 후보는 그 브랜드 언급 10개 이상인 주제 중 "
                 "긍정 또는 부정 언급 리뷰어 비율(가중)이 가장 높은 2개씩입니다.")
    return lines
