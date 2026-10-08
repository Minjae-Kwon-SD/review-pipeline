"""제품 개발 가이드의 숫자와 표, 근거 리뷰 묶음(16_guide_metrics.json)을 만든다. 모델을 부르지 않는다.

사용: python scripts/guide_metrics.py [회차]

입력: 05_metrics.json, 04_tags.jsonl, 07b_issue_labels.jsonl, 07b_issue_counts.json, 07c_safety_summary.json,
      07c_safety_verdicts.yaml, 14_details.jsonl, 14_detail_counts.json, market/market.json, 02_reviews.csv,
      02_star_distribution.csv, 01_asins.csv, config/categories/<카테고리>.yaml의 guide 절.
카테고리마다 다른 것(시장 노드, 방향 지수 라벨, 기준표 후보, 검색어 성별 낱말 등)은 guide 절에서만 읽는다.

출력 16_guide_metrics.json:
  values: {키: {value, text, ev(근거 묶음 키), note}}   guide-writer는 [m:키]로 인용하고 검사는 text와 대조한다.
  tables: 장마다 표(행마다 값과 표기, 근거 묶음 키)
  ev: {키: {t 제목, s 설명, i 리뷰 id(관련 높은 순, 최대 80개), q {리뷰 id: 노랗게 표시할 인용}}}
  quotes: 근거 묶음마다 인용 후보(리뷰 id, 별점, 브랜드, 원문)
  caveats: A장에 적을 한계
가중은 리뷰 리포트와 같은 별점 묶음 가중(weight.build_weights).
"""
import argparse
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from issues import review_weights  # noqa: E402
from pipeline_io import (ASIN_COLS, ROOT, die, split_tags, category_conf, load_csv_or_die, load_schema, load_yaml, now_iso, pct, read_jsonl,  # noqa: E402
                         resolve_run, write_json)

for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass

EV_MAX = 80
EXCLUDE = ("overall",)


def f_int(v):
    return f"{int(round(v)):,}"


def f_pct(v):
    v = float(v)
    return "0.1% 미만" if 0 < v < 0.05 else f"{v:.1f}%"      # 0이 아닌데 0.0%로 보이지 않게


def f_star(v):
    return f"{float(v):.2f}★"


def f_num(v, d=2):
    return f"{float(v):,.{d}f}"


def median(v):
    v = sorted(v)
    if not v:
        return None
    n = len(v)
    return v[n // 2] if n % 2 else round((v[n // 2 - 1] + v[n // 2]) / 2, 3)


class G:
    def unit(self, item):
        """숫자 항목의 단위(승인 스키마 unit). 없으면 향수 때의 기본값 시간"""
        return re.sub(r"\(.*?\)", "", self.detail_units.get(item) or "시간").strip() or "시간"

    def dur(self, v, item):
        """숫자 항목 표기. 단위가 시간이고 1시간 미만이면 분으로(0.292시간 -> 약 18분)"""
        u = self.unit(item)
        return f"약 {round(v * 60)}분" if u == "시간" and v < 1 else f"{v:g}{u}"

    def item_name(self, item):
        """숫자 항목의 짧은 이름(카테고리 설정 guide.number_names, 없으면 향수 때의 '말한 지속 시간')"""
        return (self.conf.get("number_names") or {}).get(item) or "말한 지속 시간"

    def __init__(self, run):
        self.run = run
        self.m = json.loads((run / "05_metrics.json").read_text(encoding="utf-8"))
        cat = run.name.split("-")[0]
        self.conf = (load_yaml(ROOT / "config" / "categories" / f"{cat}.yaml") or {})["guide"]
        self.schema = load_schema(run)
        self.reviews, self.weight = review_weights(run)
        self.rev = {r["review_id"]: r for r in self.reviews}
        self.total_w = sum(self.weight.values())
        _, self.tags, self.dropped = split_tags(self.reviews, read_jsonl(run / "04_tags.jsonl"), self.schema)
        self.tag = {(t["review_id"], t["topic"]): t for t in self.tags}
        self.labels = read_jsonl(run / "07b_issue_labels.jsonl")
        self.counts = json.loads((run / "07b_issue_counts.json").read_text(encoding="utf-8"))
        self.details = read_jsonl(run / "14_details.jsonl")
        self.dcounts = json.loads((run / "14_detail_counts.json").read_text(encoding="utf-8"))
        self.detail_units = {i["id"]: i.get("unit") for i in (load_yaml(run / "13_detail_schema_approved.yaml") or {}).get("items") or []}
        self.market = json.loads((run / "market" / "market.json").read_text(encoding="utf-8"))
        self.detail_names = {i["id"]: i.get("name_ko") for i in (load_yaml(run / "13_detail_schema_approved.yaml") or {}).get("items") or []}
        self.mkeys = list(((category_conf(run).get("market") or {}).get("nodes") or {}).keys())    # 시장 표 이름 키
        self.safety = json.loads((run / "07c_safety_summary.json").read_text(encoding="utf-8"))
        self.verdicts = ((load_yaml(run / "07c_safety_verdicts.yaml") or {}).get("audit") or {}).get("verdicts") or []
        self.asins = [r for r in load_csv_or_die(run / "01_asins.csv", ASIN_COLS) if r["status"] == "selected"]
        self.brand = {a["asin"]: a["brand"] for a in self.asins}
        self.label_reviews = defaultdict(set)          # 라벨 id -> 리뷰
        self.label_topic = {}
        for row in self.labels:
            for lab in row["labels"]:
                if lab != "other":
                    self.label_reviews[lab].add(row["review_id"])
                    self.label_topic[lab] = row["topic"]
        self.label_name = {l["id"]: l["name_ko"] for v in self.counts["topics"].values() for l in v["labels"]}
        self.values, self.tables, self.ev, self.quotes = {}, {}, {}, {}

    # ------------------------------------------------ 도우미
    def wpct(self, rids, base=None):
        base = self.rev.keys() if base is None else base
        bw = sum(self.weight[r] for r in base)
        return pct(sum(self.weight[r] for r in rids if r in self.weight), bw)

    def neg_reviews(self, topic):
        return {t["review_id"] for t in self.tags if t["topic"] == topic and t["sentiment"] == "negative"}

    def put(self, key, value, text, ev=None, note=None):
        self.values[key] = {"value": value, "text": text, "ev": ev, **({"note": note} if note else {})}
        return key

    def evidence(self, key, title, sub, rids, quote_of=None, sort_low_first=False):
        """근거 묶음: 도움돼요 많은 순(같으면 최신), 최대 80개. quote_of(리뷰 id) -> 노랗게 표시할 인용."""
        rids = [r for r in set(rids) if r in self.rev]
        def hv(r):
            try:
                return int(self.rev[r].get("helpful_votes") or 0)
            except ValueError:
                return 0
        rids = sorted(rids, key=lambda r: (-hv(r), -int(self.rev[r]["date"].replace("-", "") or 0), r))   # 같으면 리뷰 id 순(시드 없이 고정)
        top = rids[:EV_MAX]
        q = {r: quote_of(r) for r in top if quote_of and quote_of(r)}
        self.ev[key] = {"t": title, "s": f"{sub} 리뷰 {len(rids)}개 중 {len(top)}개(도움돼요 많은 순)", "n": len(rids), "i": top, "q": q}
        self.quotes[key] = [{"review_id": r, "star": int(self.rev[r]["star"]), "brand": self.brand.get(self.rev[r]["asin"], ""),
                             "quote": q[r]} for r in top if r in q][:5]
        return key

    def tag_quote(self, topic):
        return lambda r: (self.tag.get((r, topic)) or {}).get("quote")

    def label_quote(self, lab):
        return self.tag_quote(self.label_topic.get(lab))

    def detail_quote(self, item, value=None):
        idx = defaultdict(list)
        for d in self.details:
            if d["item"] == item and (value is None or d["value"] == value):
                idx[d["review_id"]].append(d["quote"])
        return lambda r: (idx.get(r) or [None])[0]

    def detail_reviews(self, item, value=None):
        return {d["review_id"] for d in self.details if d["item"] == item and (value is None or d["value"] == value)}

    # ------------------------------------------------ 머리
    def head(self):
        c = self.conf
        node = next(r for r in self.market["tables"]["subcategories"] if str(r["id"]) == str(c["market_node_head"]))
        mv = node["totalMonthlyRevenue"]
        self.put("head.market_month", mv, f"{f_int(mv)}(월 매출 칸, 단위 미확인)", note=f"{node['subcategoryContextName']} 노드, spd-amz-market")
        self.put("head.market_year", mv * 12, f"{f_int(mv * 12)}(월 매출을 달러로 읽을 때 연 환산)", note="월 매출 칸 x 12, 단위 미확인")
        tp = c["head_topic"]
        t = next(x for x in self.m["topics"] if x["id"] == tp)
        ev = self.evidence("ev.head_topic_neg", f"{t['name_ko']} 부정 리뷰", f"{t['name_ko']} 부정 언급", self.neg_reviews(tp),
                           self.tag_quote(tp))
        self.put("head.topic_neg", t["neg_reviewer_pct"], f_pct(t["neg_reviewer_pct"]), ev, note=f"{t['name_ko']} 부정 언급 리뷰어(가중)")
        weak = [a for a in self.m["asins"] if (a.get("weakness") or {}).get("id") == tp]
        rob = (self.m.get("robustness") or {}).get("texts", {}).get("weakest")      # 다시 뽑기 범위를 붙인 표기(robustness.py)
        self.put("head.topic_weakest", len(weak), rob or f"{len(self.m['asins'])}개 중 {len(weak)}개",
                 note="가장 큰 약점(부정 언급 리뷰어 가중 비율이 가장 높은 주제)이 이 주제인 상품 수. 괄호는 리뷰를 다시 뽑았을 때 95% 이상을 덮는 범위")
        di = c["direction_index"]
        low = set().union(*[self.label_reviews[l] for l in di["low"]["labels"]])
        high = set().union(*[self.label_reviews[l] for l in di["high"]["labels"]])
        evl = self.evidence("ev.dir_low", f"{di['low']['name']} 쪽 리뷰", di["low"]["name"] + " 쪽 라벨이 붙은", low,
                            self.tag_quote(di["topic"]))
        evh = self.evidence("ev.dir_high", f"{di['high']['name']} 쪽 리뷰", di["high"]["name"] + " 쪽 라벨이 붙은", high,
                            self.tag_quote(di["topic"]))
        self.put("head.dir_low", len(low), f"{f_int(len(low))}개", evl)
        self.put("head.dir_high", len(high), f"{f_int(len(high))}개", evh)
        ratio = round(len(low) / len(high), 2) if high else None
        self.put("head.dir_ratio", ratio, f"{di['low']['name']} {f_int(len(low))}개 대 {di['high']['name']} {f_int(len(high))}개"
                 + (f"({ratio:.2f}배)" if ratio else ""), evl)
        self.growth()

    def growth(self):
        """성장 배수 = 최근 w주 검색량 합 / 52주 전 같은 w주의 합(search_terms_trends 주간 이력). 두 기간 이력이 모두 있는 후보만 순위."""
        import glob
        from datetime import date, timedelta
        from market_build import market_conf, safe, term_rule
        mc = market_conf(self.run)
        words = tuple(str(w).lower() for w in mc.get("term_words") or ())
        g = self.conf["growth"]
        w = g["window_weeks"]
        brands = sorted({r["brandName"] for k in mc["nodes"] for r in self.market["tables"].get(f"brands_{k}", []) if r.get("brandName")}
                        | set(self.brand.values()))
        excl = [x.lower() for x in g.get("exclude_words") or []]
        cands = {}
        for f in [str(self.run / "market" / "raw" / f"subcategories_relevant_search_terms_{safe(x)}.json") for x in mc["nodes"].values()]:
            if not Path(f).exists():
                continue
            for r in json.loads(Path(f).read_text(encoding="utf-8")):
                t = r.get("searchTermValue") or ""
                if (r.get("volume30Day") or 0) >= g["min_volume"] and term_rule(t, brands, words) and not any(x in t.lower().split() for x in excl):
                    if t not in cands or (r.get("volume30Day") or 0) > (cands[t].get("volume30Day") or 0):
                        cands[t] = r
        hist, src = {}, {}
        for f in sorted(glob.glob(str(self.run / "market" / "raw" / "search_terms_trends_*.json"))):
            d = json.loads(Path(f).read_text(encoding="utf-8"))
            if not isinstance(d, list):
                continue
            for r in d:
                h = r.get("history") or []
                t = r.get("searchTerm")
                if t and (t not in hist or len(h) > len(hist[t])):
                    hist[t], src[t] = h, Path(f).name
        rows = []
        for t in cands:
            h = {x["date"][:10]: x.get("estimateSearches") for x in hist.get(t, [])}
            if not h:
                continue
            last = sorted(h)[-w:]
            prev = [(date.fromisoformat(d) - timedelta(weeks=52)).isoformat() for d in last]
            if len(last) < w or any(h.get(d) is None for d in last + prev):
                continue
            rec, pri = sum(h[d] for d in last), sum(h[d] for d in prev)
            if pri <= 0:
                continue
            rows.append({"term": t, "recent": rec, "prior": pri, "multiple": round(rec / pri, 2), "recent_weeks": f"{last[0]} ~ {last[-1]}",
                         "prior_weeks": f"{prev[0]} ~ {prev[-1]}", "volume30Day": cands[t].get("volume30Day"), "source": src[t]})
        rows.sort(key=lambda r: (-r["multiple"], r["term"]))
        self.tables["m.growth"] = rows[:15]
        self.put("m.growth_candidates", len(cands), f"{len(cands)}개")
        self.put("m.growth_ranked", len(rows), f"{len(rows)}개")
        if rows:
            b = rows[0]
            self.put("head.fastest_term", b["term"], f"\"{b['term']}\" 최근 {w}주 {f_int(b['recent'])}, 1년 전 같은 {w}주 {f_int(b['prior'])}, {b['multiple']:.2f}배",
                     note=f"30일 검색량 {g['min_volume']:,} 이상 카테고리 검색어 {len(cands)}개 중 두 기간 주간 이력이 있는 {len(rows)}개에서 성장 배수 1위")
            self.put("head.growth_multiple", b["multiple"], f"{b['multiple']:.2f}배")
            self.put("head.growth_recent", b["recent"], f_int(b["recent"]))
            self.put("head.growth_prior", b["prior"], f_int(b["prior"]))
            self.put("head.growth_weeks", b["recent_weeks"], f"{b['recent_weeks']}(1년 전 {b['prior_weeks']})")

    def all_terms(self):
        seen = {}
        for k in [f"terms_{x}" for x in self.mkeys]:
            for r in self.market["tables"].get(k) or []:
                t = r["searchTermValue"]
                if t not in seen or (r.get("volume30Day") or 0) > (seen[t].get("volume30Day") or 0):
                    seen[t] = r
        return list(seen.values())

    # ------------------------------------------------ 01 시장
    def market_ch(self):
        T = self.market["tables"]
        self.tables["m.subcategories"] = [{"id": r["id"], "name": r["subcategoryContextName"] or r["subcategoryName"],
                                           "revenue": r["totalMonthlyRevenue"], "revenue_text": f_int(r["totalMonthlyRevenue"]),
                                           "units": r["totalNumberUnitsSold"], "brands": r["totalBrands"], "asins": r["totalAsins"],
                                           "avg_price": r["avgPrice"], "avg_rating": r["avgRating"], "mom": r["momGrowth"],
                                           "mom12": r["momGrowth12"], "az": r["azRevenuePct"]} for r in T["subcategories"]]
        for k, node in zip(self.mkeys, self.conf["market_nodes_brand_share"]):
            rows = T[f"brands_{k}"][:10]
            top10 = sum(r["marketshare"] or 0 for r in rows)
            self.tables[f"m.brands_{k}"] = [{"rank": i + 1, "brand": r["brandName"], "share": r["marketshare"],
                                             "share_text": f_pct(100 * (r["marketshare"] or 0)), "revenue": r["revenue"],
                                             "avg_price": r["avgPrice"], "rating": r["reviewRating"]} for i, r in enumerate(rows)]
            self.put(f"m.top10_share_{k}", round(100 * top10, 1), f_pct(100 * top10), note=f"{node} 상위 10개 브랜드 marketshare 합(단위 미확인 값을 %로 읽음)")
            self.put(f"m.top1_{k}", rows[0]["brandName"], f"{rows[0]['brandName']} {f_pct(100 * rows[0]['marketshare'])}")
        gw = self.conf["gender_words"]
        def gender(t):
            tl = f" {t.lower()} "
            if any(f" {w} " in tl or tl.strip().startswith(w + " ") for w in gw["female"]):
                return "female"
            if any(f" {w} " in tl for w in gw["male"]):
                return "male"
            return "common"
        groups = defaultdict(list)
        for r in self.all_terms():
            groups[gender(r["searchTermValue"])].append(r)
        for g in ("female", "male", "common"):
            rows = sorted(groups[g], key=lambda r: -(r.get("volume30Day") or 0))[:10]
            self.tables[f"m.terms_{g}"] = [{"term": r["searchTermValue"], "volume": r["volume30Day"], "volume_text": f_int(r["volume30Day"] or 0),
                                            "yoy_pct": r.get("yoYChangePct"), "yoy_text": "-" if r.get("yoYChangePct") is None else f"{r['yoYChangePct'] * 100:+.1f}%"}   # 응답 값 0.0874를 +8.7%로(비율로 읽음)
                                           for r in rows]
            self.put(f"m.terms_{g}_n", len(groups[g]), f"{f_int(len(groups[g]))}개")
            self.put(f"m.terms_{g}_volume", sum(r.get("volume30Day") or 0 for r in groups[g]),
                     f_int(sum(r.get("volume30Day") or 0 for r in groups[g])))
        brands = [r for k in self.mkeys for r in T[f"brands_{k}"] if r.get("avgPrice")]
        prices = sorted(r["avgPrice"] for r in brands)
        nb = self.conf.get("price_bands", 3)
        cuts = [prices[int(len(prices) * i / nb)] for i in range(1, nb)]
        bands = defaultdict(list)
        for r in brands:
            i = sum(r["avgPrice"] >= c for c in cuts)
            bands[i].append(r)
        tot = sum(r["revenue"] or 0 for r in brands)
        rows = []
        for i in range(nb):
            rs = bands[i]
            lo = min(r["avgPrice"] for r in rs) if rs else None
            hi = max(r["avgPrice"] for r in rs) if rs else None
            rows.append({"band": i + 1, "price_range": f"{lo:.2f}~{hi:.2f}" if rs else "-", "brands": len(rs),
                         # 별점이 비어 있는 브랜드는 평균에서 뺀다(시장 도구 응답에 None이 있음)
                         "avg_rating": (round(sum(x) / len(x), 2) if (x := [r["reviewRating"] for r in rs if r.get("reviewRating") is not None]) else None),
                         "revenue_share": pct(sum(r["revenue"] or 0 for r in rs), tot)})
        self.tables["m.price_bands"] = rows
        for r in rows:
            self.put(f"m.price_band{r['band']}_rating", r["avg_rating"], f_star(r["avg_rating"]) if r["avg_rating"] else "-")
            self.put(f"m.price_band{r['band']}_share", r["revenue_share"], f_pct(r["revenue_share"]))
            self.put(f"m.price_band{r['band']}_range", r["price_range"], r["price_range"])

    # ------------------------------------------------ 02 경쟁사 점수표
    def scoreboard(self):
        c = self.conf
        di = c["direction_index"]
        prod = {p["asin"]: p for p in self.market["tables"]["our_products"]}
        dur = self.dcounts["items"].get(c["duration_item"], {})
        rows = []
        tp = c["head_topic"]
        neg_tp = self.neg_reviews(tp)
        for a in self.m["asins"]:
            asin = a["asin"]
            ids = [r["review_id"] for r in self.reviews if r["asin"] == asin]
            p = prod.get(asin, {})
            oz = p.get("unitValue")
            price = p.get("buyBoxPrice")
            neg = [r for r in ids if r in neg_tp]
            low = [r for r in ids if any(r in self.label_reviews[l] for l in di["low"]["labels"])]
            high = [r for r in ids if any(r in self.label_reviews[l] for l in di["high"]["labels"])]
            n_dir = len(set(low) | set(high))
            idx = round((len(high) - len(low)) / (len(high) + len(low)), 2) if n_dir >= di["min_reviews"] and (len(high) + len(low)) else None
            vals = (dur.get("numbers_by_asin") or {}).get(asin) or []
            med = median(vals) if len(vals) >= c["duration_min_values"] else None
            k = f"s.{asin}"
            evn = self.evidence(f"ev.{asin}.topic_neg", f"{a['brand']}: {self.schema[tp]['name_ko']} 부정", "이 상품의 " + self.schema[tp]["name_ko"]
                                + " 부정 언급", neg, self.tag_quote(tp))
            evl = self.evidence(f"ev.{asin}.dir_low", f"{a['brand']}: {di['low']['name']}", di["low"]["name"] + " 쪽 라벨이 붙은", low, self.tag_quote(tp))
            evh = self.evidence(f"ev.{asin}.dir_high", f"{a['brand']}: {di['high']['name']}", di["high"]["name"] + " 쪽 라벨이 붙은", high, self.tag_quote(tp))
            evd = self.evidence(f"ev.{asin}.duration", f"{a['brand']}: {self.item_name(c['duration_item'])}", f"{self.item_name(c['duration_item'])}(숫자)",
                                {d["review_id"] for d in self.details if d["item"] == c["duration_item"] and d["asin"] == asin},
                                self.detail_quote(c["duration_item"]))
            row = {"asin": asin, "brand": a["brand"], "subcategory": p.get("subcategory"), "price": price,
                   "size": p.get("size"), "oz": oz, "price_per_oz": round(price / oz, 2) if price and oz else None,
                   "weighted_star": a["weighted_mean_star"], "topic_neg_pct": self.wpct(neg, ids), "dir_low": len(low), "dir_high": len(high),
                   "dir_n": n_dir, "dir_index": idx, "duration_values": len(vals), "duration_median": med,
                   "strength": (a.get("strength") or {}).get("name_ko"), "weakness": (a.get("weakness") or {}).get("name_ko"),
                   "ev": {"topic_neg": evn, "dir_low": evl, "dir_high": evh, "duration": evd}}
            rows.append(row)
            self.put(f"{k}.price", price, f"{price:.2f}달러" if price else "-")
            self.put(f"{k}.price_per_oz", row["price_per_oz"], f"{row['price_per_oz']:.2f}달러" if row["price_per_oz"] else "-")
            self.put(f"{k}.star", row["weighted_star"], f_star(row["weighted_star"]))
            self.put(f"{k}.topic_neg", row["topic_neg_pct"], f_pct(row["topic_neg_pct"]), evn)
            self.put(f"{k}.dir_index", idx, "-" if idx is None else f"{idx:+.2f}", evl)
            self.put(f"{k}.duration_median", med, "-" if med is None else self.dur(med, c['duration_item']), evd)
        self.tables["s.scoreboard"] = rows

    # ------------------------------------------------ 03 문제
    def problems(self):
        rows = []
        for t in self.m["topics"]:
            if t["id"] in EXCLUDE:
                continue
            ev = self.evidence(f"ev.topic.{t['id']}", f"{t['name_ko']} 부정", t["name_ko"] + " 부정 언급", self.neg_reviews(t["id"]),
                               self.tag_quote(t["id"]))
            rows.append({"topic": t["id"], "name": t["name_ko"], "neg_reviewer_pct": t["neg_reviewer_pct"], "negative": t["negative"], "ev": ev})
            self.put(f"p.map.{t['id']}", t["neg_reviewer_pct"], f_pct(t["neg_reviewer_pct"]), ev)
        rows.sort(key=lambda r: -r["neg_reviewer_pct"])
        self.tables["p.complaint_map"] = rows
        gaps = sorted(self.m["impact"], key=lambda r: r["gap"])[:3]
        self.tables["p.gaps"] = []
        for i, g in enumerate(gaps, 1):
            ev = f"ev.topic.{g['id']}"
            self.tables["p.gaps"].append({**g, "ev": ev})
            self.put(f"p.gap{i}", g["gap"], f"{g['gap']:+.2f}", ev, note=f"{g['name_ko']}: 부정 {g['neg_avg_star']:.2f}★ 대 나머지 {g['other_avg_star']:.2f}★")
            self.put(f"p.gap{i}_neg", g["neg_avg_star"], f_star(g["neg_avg_star"]), ev)
            self.put(f"p.gap{i}_other", g["other_avg_star"], f_star(g["other_avg_star"]), ev)
        for f in self.conf["focus"]:
            self.focus(f)
        sc = self.safety
        # 07c_safety_summary와 같은 규칙: 부정 감성 인용 중 이상 반응으로 판정된 리뷰만 증상별로 묶는다
        neg_ids = {str(r["review_id"]) for r in read_jsonl(self.run / "07c_safety_input.jsonl") if r.get("sentiment") == "negative"}
        is_sym = lambda v: str(v.get("verdict")).lower() in ("symptom", "이상 반응 있음", "몸 증상 있음", "yes", "true")
        symp = {}
        for v in self.verdicts:
            if v.get("symptom_type") and is_sym(v) and str(v["review_id"]) in neg_ids:
                symp.setdefault(v["symptom_type"], []).append(str(v["review_id"]))
        st = []
        for x in sc.get("by_symptom") or []:
            ev = self.evidence(f"ev.safety.{x['name']}", f"안전 부정: {x['name']}", "07c에서 이 증상으로 판정한", symp.get(x["name"], []),
                               self.tag_quote("safety"))
            st.append({**x, "ev": ev})
            self.put(f"p.safety.{x['name']}", x["reviews"], f"{x['reviews']}개", ev)
        self.tables["p.safety"] = st
        self.put("p.safety_text", sc.get("negative_text"), sc.get("negative_text"))

    def value_table(self, item, key, quote=True):
        it = self.dcounts["items"].get(item)
        if not it:
            return []
        rows = []
        for v in it.get("values") or []:
            if not v["reviews"]:
                continue
            ev = self.evidence(f"ev.{key}.{item}.{v['value']}", f"{it['name_ko']}: {v['ko']}", f"{it['name_ko']} 값 {v['ko']}",
                               self.detail_reviews(item, v["value"]), self.detail_quote(item, v["value"]))
            rows.append({"value": v["value"], "ko": v["ko"], "reviews": v["reviews"], "weighted_pct": v["weighted_pct"], "ev": ev})
            self.put(f"{key}.{item}.{v['value']}", v["reviews"], f"{v['reviews']}개", ev)
        rows.sort(key=lambda r: -r["reviews"])
        self.tables[f"{key}.{item}"] = rows
        self.put(f"{key}.{item}.total", it["reviews"], f"{it['reviews']}개")
        return rows

    def focus(self, f):
        key = f"f.{f['id']}"
        c = self.conf
        for item in f.get("items") or []:
            fmt = (self.dcounts["items"].get(item) or {}).get("format")
            if fmt == "choice":
                self.value_table(item, key)
            elif fmt == "number":
                it = self.dcounts["items"][item]
                bins = c.get("duration_bins", [1, 3, 6, 12])
                allv = [(d["review_id"], float(d["value"])) for d in self.details if d["item"] == item]
                edges = [0] + bins + [float("inf")]
                rows = []
                for lo, hi in zip(edges, edges[1:]):
                    rids = {r for r, v in allv if lo <= v < hi}
                    u = self.unit(item)      # 숫자 항목의 단위(승인 스키마의 unit, 없으면 시간)
                    nm = self.item_name(item)
                    lab = f"{lo:g}~{hi:g}{u}" if hi != float("inf") else f"{lo:g}{u} 이상"
                    if lo == 0:
                        lab = f"{hi:g}{u} 미만"
                    ev = self.evidence(f"ev.{key}.{item}.bin{len(rows)}", f"{nm} {lab}", f"{nm} {lab}", rids,
                                       self.detail_quote(item))
                    rows.append({"bin": lab, "reviews": len(rids), "ev": ev})
                    self.put(f"{key}.{item}.bin{len(rows) - 1}", len(rids), f"{len(rids)}개", ev)
                self.tables[f"{key}.{item}.bins"] = rows
                self.put(f"{key}.{item}.median", it["median"], self.dur(it['median'], item) if it["median"] is not None else "-")
                self.put(f"{key}.{item}.n", len(allv), f"{len(allv)}개")
            elif fmt == "text":
                # 같은 이름의 다른 표기를 묶는다(카테고리 설정 guide.value_aliases, 대소문자 무시)
                al = {v.lower(): canon for canon, vs in ((self.conf.get("value_aliases") or {}).get(item) or {}).items() for v in [canon] + vs}
                vals = Counter(al.get(str(d["value"]).strip().lower(), str(d["value"]).strip()) for d in self.details if d["item"] == item)
                self.tables[f"{key}.{item}"] = [{"value": v, "reviews": n} for v, n in vals.most_common(15)]
                self.put(f"{key}.{item}.n", sum(vals.values()), f"{sum(vals.values())}개")
        if f.get("split_label") and f.get("items"):
            lab = f["split_label"]
            for item in f["items"]:
                it = self.dcounts["items"].get(item) or {}
                if it.get("format") != "choice" or item == "fake_suspicion_basis":
                    continue
                rows = []
                for v in it.get("values") or []:
                    rids = self.detail_reviews(item, v["value"])
                    if len(rids) < 3:
                        continue
                    hit = rids & self.label_reviews[lab]
                    rows.append({"value": v["value"], "ko": v["ko"], "reviews": len(rids), "with_label": len(hit),
                                 "share": pct(len(hit), len(rids))})
                    self.put(f"{key}.{item}.{v['value']}.{lab}", pct(len(hit), len(rids)), f"{len(rids)}개 중 {len(hit)}개({f_pct(pct(len(hit), len(rids)))})")
                self.tables[f"{key}.{item}.by_{lab}"] = rows
        if f.get("pair_items"):
            # 같은 인용(리뷰 id, 인용)의 노트와 방향을 짝짓는다. 한쪽이 하나뿐이면 짝이 분명하다.
            # 양쪽이 모두 둘 이상이면 어느 노트가 어느 방향인지 알 수 없으므로 짝을 만들지 않고 "짝 불명"으로 센다.
            pairs = Counter()
            pa, pb = f["pair_items"]
            notes, dirs = defaultdict(list), defaultdict(list)
            for d in self.details:
                if d["item"] == pa:
                    notes[(d["review_id"], d["quote"])].append(d["value"])
                elif d["item"] == pb:
                    dirs[(d["review_id"], d["quote"])].append(d["value"])
            unclear = []
            for k, dv in dirs.items():
                ns = notes.get(k, [])
                if len(ns) >= 2 and len(dv) >= 2:
                    unclear.append(k)
                    continue
                for n in ns:
                    for v in dv:
                        pairs[(n, v)] += 1
            self.tables[f"{key}.note_x_direction"] = [{"note": n, "direction": dv, "reviews": c_} for (n, dv), c_ in pairs.most_common()]
            self.put(f"{key}.note_pairs", sum(pairs.values()), f"{sum(pairs.values())}쌍", note="노트와 방향의 짝(한쪽이 하나뿐인 인용만)")
            self.put(f"{key}.note_pairs_unclear", len(unclear), f"{len(unclear)}개",
                     self.evidence(f"ev.{key}.note_pairs_unclear", "노트와 방향 짝 불명", "한 인용에 노트와 방향이 둘 이상씩 있는",
                                   {k[0] for k in unclear}, self.detail_quote(pb)),
                     note="한 인용에 노트와 방향이 모두 둘 이상이라 짝을 정하지 않은 인용 수")
        for lab in f.get("labels") or []:
            rids = self.label_reviews[lab]
            ev = self.evidence(f"ev.label.{lab}", self.label_name.get(lab, lab), self.label_name.get(lab, lab) + " 라벨이 붙은", rids, self.label_quote(lab))
            self.put(f"{key}.label.{lab}", len(rids), f"{len(rids)}개", ev)
        for tp in f.get("topics") or []:
            ent = self.counts["topics"].get(f"{tp}.negative")
            if ent:
                self.tables[f"{key}.labels.{tp}"] = [{"id": l["id"], "name": l["name_ko"], "reviews": l["reviews"], "weighted_pct": l["weighted_pct"]}
                                                     for l in ent["labels"] if l["id"] != "other" and l["reviews"]]

    # ------------------------------------------------ 04 기준표
    def standards(self):
        terms = self.all_terms()
        rows = []
        symp_ids = {str(v["review_id"]) for v in self.verdicts if v.get("symptom_type")}
        for s in self.conf["standards"]:
            neg = set().union(*[self.label_reviews[l] for l in s.get("neg_labels") or []]) if s.get("neg_labels") else set()
            if s.get("safety"):
                neg |= symp_ids
            pos = set().union(*[self.label_reviews[l] for l in s.get("pos_labels") or []]) if s.get("pos_labels") else set()
            qf = (lambda r: (self.tag.get((r, "safety")) or {}).get("quote")) if s.get("safety") else \
                (lambda r, s=s: next((self.label_quote(l)(r) for l in s.get("neg_labels") or [] if r in self.label_reviews[l]), None))
            evn = self.evidence(f"ev.std.{s['id']}.neg", f"{s['title']}: 불만 리뷰", s["title"] + " 부정 라벨이 붙은", neg, qf)
            qp = lambda r, s=s: next((self.label_quote(l)(r) for l in s.get("pos_labels") or [] if r in self.label_reviews[l]), None)
            evp = self.evidence(f"ev.std.{s['id']}.pos", f"{s['title']}: 만족한 리뷰", s["title"] + " 긍정 라벨이 붙은", pos, qp)
            by_asin = []
            for a in self.asins:
                ids = [r["review_id"] for r in self.reviews if r["asin"] == a["asin"]]
                by_asin.append({"asin": a["asin"], "brand": a["brand"], "neg_pct": self.wpct([r for r in ids if r in neg], ids),
                                "neg": sum(1 for r in ids if r in neg)})
            best = min(by_asin, key=lambda x: (x["neg_pct"], x["brand"]))
            neg_labels = [{"id": l, "name": self.label_name.get(l, l), "reviews": len(self.label_reviews[l])}
                          for l in s.get("neg_labels") or []]
            items = []
            for item in s.get("items") or []:
                it = self.dcounts["items"].get(item) or {}
                want = (s.get("item_values") or {}).get(item)
                for v in it.get("values") or []:
                    if v["reviews"] and (want is None or v["value"] in want):
                        items.append({"item": item, "value": v["value"], "ko": v["ko"], "reviews": v["reviews"],
                                      "text": f"{v['ko']} {v['reviews']}"})
                if it.get("format") == "number":
                    unit = str((self.detail_units.get(item) or "")).split("(")[0].strip()
                    med = it.get("median")
                    items.append({"item": item, "value": "median", "ko": "중앙값", "reviews": it.get("reviews"), "median": med,
                                  "text": f"{it.get('name_ko') or item} 중앙값 {'-' if med is None else f'{med:g}{unit}'}(값 {it.get('reviews')}개)"})
            words = [w.lower() for w in s.get("search_words") or []]
            rel = sorted([t for t in terms if any(w in t["searchTermValue"].lower() for w in words)],
                         key=lambda t: -(t.get("volume30Day") or 0))[:5]
            row = {"id": s["id"], "title": s["title"], "neg_reviews": len(neg), "neg_weighted_pct": self.wpct(neg),
                   "pos_reviews": len(pos), "best": best, "by_asin": by_asin, "neg_labels": neg_labels, "items": items,
                   "terms": [{"term": t["searchTermValue"], "volume": t["volume30Day"], "yoy_pct": t.get("yoYChangePct")} for t in rel],
                   "ev": {"neg": evn, "pos": evp}}
            rows.append(row)
            k = f"std.{s['id']}"
            self.put(f"{k}.neg", len(neg), f"{f_int(len(neg))}개", evn)
            self.put(f"{k}.neg_pct", row["neg_weighted_pct"], f_pct(row["neg_weighted_pct"]), evn)
            self.put(f"{k}.pos", len(pos), f"{f_int(len(pos))}개", evp)
            self.put(f"{k}.best", best["brand"], f"{best['brand']} {f_pct(best['neg_pct'])}")
            for x in neg_labels:
                self.put(f"{k}.label.{x['id']}", x["reviews"], f"{x['reviews']}개", self.evidence(
                    f"ev.label.{x['id']}", x["name"], x["name"] + " 라벨이 붙은", self.label_reviews[x["id"]], self.label_quote(x["id"])))
            for t in row["terms"]:
                self.put(f"{k}.term.{t['term']}", t["volume"], f"{f_int(t['volume'] or 0)}")
        self.tables["std.board"] = rows

    # ------------------------------------------------ 상품 사양과 기준 1, 2, 4, 6 연결
    def specs_link(self):
        """23_specs_verified.json(specs.py check가 확인한 값만)을 점수표와 기준 1, 2, 4, 6에 나란히 놓는다.
        상품이 적어 비율 비교나 원인 주장은 하지 않고 나열만 한다. 파일이 없으면 건너뛴다."""
        p = self.run / "23_specs_verified.json"
        if not p.exists():
            return
        S = json.loads(p.read_text(encoding="utf-8"))["products"]
        sc = category_conf(self.run).get("specs") or {}
        note_map = sc.get("note_map") or {}
        links = sc.get("links") or {}
        note_item, part_item = sc.get("note_item"), sc.get("part_item")
        self.tables["std.spec_kinds"] = {v: k for k, v in links.items()}
        board = {s["id"]: s for s in self.tables.get("std.board", [])}
        score = {r["asin"]: r for r in self.tables.get("s.scoreboard", [])}

        def vals(asin, item):
            out = []
            for v in (S.get(asin) or {}).get("values", {}).get(item, []):
                out += v["value"] if isinstance(v["value"], list) else [v["value"]]
            return out

        def src(asin, item):
            return [{"url": v["url"], "type": v["source_type"]} for v in (S.get(asin) or {}).get("values", {}).get(item, [])]

        def match(asin):
            return (S.get(asin) or {}).get("match") or "찾지 못함"

        def notes(asin):
            return [n for k in ("notes_top", "notes_middle", "notes_base", "notes_all") for n in vals(asin, k)]

        conc = {a["asin"]: ", ".join(vals(a["asin"], "concentration")) or "-" for a in self.asins}
        # 점수표 칸
        for a in self.asins:
            r = score.get(a["asin"])
            if r is not None:
                r["spec_concentration"] = conc[a["asin"]]
                r["spec_notes"] = ", ".join(notes(a["asin"])) or "-"
                r["spec_match"] = match(a["asin"])
                r["spec_src"] = src(a["asin"], "concentration") + src(a["asin"], "notes_top") + src(a["asin"], "notes_all")
            self.put(f"spec.{a['asin']}.concentration", conc[a["asin"]], conc[a["asin"]], note=f"상품 사양({match(a['asin'])})")
            self.put(f"spec.{a['asin']}.match", match(a["asin"]), match(a["asin"]))
        n_match = Counter(match(a["asin"]) for a in self.asins)
        self.put("spec.match_summary", dict(n_match), ", ".join(f"{k} {v}개" for k, v in sorted(n_match.items())))

        # 기준 1: 농도와 지속력 불만, 말한 지속 시간
        b1 = board.get(links.get("duration"))
        if b1:
            rows = []
            for x in b1["by_asin"]:
                sc = score.get(x["asin"], {})
                rows.append({"asin": x["asin"], "brand": x["brand"], "subcategory": sc.get("subcategory"), "concentration": conc[x["asin"]],
                             "match": match(x["asin"]), "neg_pct": x["neg_pct"], "duration_values": sc.get("duration_values"),
                             "duration_median": sc.get("duration_median"), "src": src(x["asin"], "concentration")})
            self.tables[f"std.spec.{b1['id']}"] = rows
            women = [r for r in rows if str(r["subcategory"] or "").startswith("Women")]
            if women:
                bw = min(women, key=lambda r: (r["neg_pct"], r["brand"]))
                self.put(f"std.{b1['id']}.best_women", bw["brand"], f"{bw['brand']} {f_pct(bw['neg_pct'])}",
                         note="여성 하위 카테고리 상품 가운데 지속력과 세기 부정(가중)이 가장 낮은 상품")
                self.put(f"std.{b1['id']}.best_women_median", bw["duration_median"],
                         "-" if bw["duration_median"] is None else self.dur(bw['duration_median'], self.conf['duration_item']))
            best = b1["best"]
            self.put(f"std.{b1['id']}.best_sub", score.get(best["asin"], {}).get("subcategory"),
                     score.get(best["asin"], {}).get("subcategory") or "-", note="부정이 가장 적은 상품의 하위 카테고리")
            for r in rows:
                k = f"std.spec.{b1['id']}.{r['asin']}"
                self.put(f"{k}.neg_pct", r["neg_pct"], f_pct(r["neg_pct"]))
                self.put(f"{k}.duration", r["duration_median"], f"값 {r['duration_values']}개" +
                         ("" if r["duration_median"] is None else f", 중앙값 {self.dur(r['duration_median'], self.conf['duration_item'])}"))

        # 기준 2: 공식 노트와 리뷰가 말한 노트
        b2 = board.get(links.get("notes"))
        if b2 and note_item:
            sn = defaultdict(set)          # 리뷰 -> scent_note 값
            nw = defaultdict(set)          # 리뷰 -> other의 원문 낱말
            for d in self.details:
                if d["item"] == note_item:
                    sn[d["review_id"]].add(d["value"])
                    w = (d.get("extra") or {}).get("note_word")
                    if w:
                        nw[d["review_id"]].add(str(w).lower())
            missing = self.label_reviews.get("missing_described_notes", set())
            rows = []
            for a in self.asins:
                asin = a["asin"]
                off = [n.lower() for n in notes(asin)]
                if not off:
                    rows.append({"asin": asin, "brand": a["brand"], "match": match(asin), "official": "-", "mention": None, "said": None,
                                 "missing": None, "missing_notes": "-", "src": []})
                    continue
                hit_cat = {c for c, kws in note_map.items() if any(any(k in n for k in kws) for n in off)}
                ids = [r["review_id"] for r in self.reviews if r["asin"] == asin]
                said = [r for r in ids if sn.get(r)]
                mention = [r for r in said if (sn[r] & hit_cat) or any(any(w in n or n in w for n in off) for w in nw.get(r, ()))]
                mis = [r for r in ids if r in missing]
                mis_notes = Counter(v for r in mis for v in sn.get(r, ()) if v != "other")
                ko = {v["value"]: v["ko"] for v in (self.dcounts["items"].get(note_item) or {}).get("values", [])}
                rows.append({"asin": asin, "brand": a["brand"], "match": match(asin), "official": ", ".join(notes(asin)),
                             "said": len(said), "mention": len(mention), "missing": len(mis),
                             "missing_notes": ", ".join(f"{ko.get(k, k)}{'(공식)' if k in hit_cat else ''} {v}" for k, v in sorted(mis_notes.items(), key=lambda kv: (-kv[1], kv[0]))[:4]) or "-",
                             "src": src(asin, "notes_top") + src(asin, "notes_middle") + src(asin, "notes_base") + src(asin, "notes_all")})
                ev = self.evidence(f"ev.spec.notes.{asin}", f"{a['brand']}: 공식 노트를 말한 리뷰", "공식 노트(또는 그 계열)를 말한", mention,
                                   self.detail_quote(note_item))
                k = f"std.spec.{b2['id']}.{asin}"
                self.put(f"{k}.mention", len(mention), f"{len(mention)}개", ev)
                self.put(f"{k}.said", len(said), f"{len(said)}개")
                self.put(f"{k}.missing", len(mis), f"{len(mis)}개")
            self.tables[f"std.spec.{b2['id']}"] = rows

        # 기준 4: 병과 분사기 사양과 망가진 부품
        b4 = board.get(links.get("parts"))
        if b4 and part_item:
            pf = defaultdict(Counter)
            ko = {v["value"]: v["ko"] for v in (self.dcounts["items"].get(part_item) or {}).get("values", [])}
            for d in self.details:
                if d["item"] == part_item:
                    pf[d["asin"]][d["value"]] += 1
            rows = []
            for a in self.asins:
                asin = a["asin"]
                ids = {d["review_id"] for d in self.details if d["item"] == part_item and d["asin"] == asin}
                ev = self.evidence(f"ev.spec.parts.{asin}", f"{a['brand']}: 망가진 부품", "망가진 부품을 말한", ids, self.detail_quote(part_item))
                rows.append({"asin": asin, "brand": a["brand"], "match": match(asin), "sprayer": "; ".join(vals(asin, "sprayer_bottle")) or "확인 못 함",
                             "parts": len(ids), "top": ", ".join(f"{ko.get(k, k)} {v}" for k, v in sorted(pf[asin].items(), key=lambda kv: (-kv[1], kv[0]))[:3]) or "-",
                             "ev": ev, "src": src(asin, "sprayer_bottle")})
                self.put(f"std.spec.{b4['id']}.{asin}.parts", len(ids), f"{len(ids)}개", ev)
            self.tables[f"std.spec.{b4['id']}"] = rows

        # 기준 6: 이상 반응 리뷰와 표시 알레르기 성분(나열만)
        b6 = board.get(links.get("body"))
        if b6:
            asin_of = {r["review_id"]: r["asin"] for r in self.reviews}
            sym = defaultdict(Counter)
            for v in self.verdicts:
                if v.get("symptom_type") and str(v["review_id"]) in asin_of:
                    sym[asin_of[str(v["review_id"])]][v["symptom_type"]] += 1
            rows = []
            for a in self.asins:
                asin = a["asin"]
                al = vals(asin, "allergens")
                rows.append({"asin": asin, "brand": a["brand"], "match": match(asin), "symptoms": sum(sym[asin].values()),
                             "by_type": ", ".join(f"{k} {v}" for k, v in sorted(sym[asin].items(), key=lambda kv: (-kv[1], kv[0]))) or "-",
                             "allergens": ", ".join(al) if al else "표시 확인 못 함",
                             "ingredients": "있음" if vals(asin, "ingredients") else "확인 못 함", "src": src(asin, "allergens") + src(asin, "ingredients")})
                self.put(f"std.spec.{b6['id']}.{asin}.symptoms", sum(sym[asin].values()), f"{sum(sym[asin].values())}개")
            self.tables[f"std.spec.{b6['id']}"] = rows
            pos = {t["review_id"] for t in self.tags if t["topic"] == "safety" and t["sentiment"] == "positive"}
            ev = self.evidence(f"ev.std.{b6['id']}.pos_tags", "몸 반응이 없었다는 리뷰", "안전 주제 긍정 태그가 붙은", pos, self.tag_quote("safety"))
            self.put(f"std.{b6['id']}.pos_tags", len(pos), f"{len(pos)}개" if pos else "근거 없음", ev if pos else None,
                     note="안전 주제 긍정 태그(몸 반응이 없었다는 말)가 붙은 리뷰")
            al_n = sum(1 for r in rows if r["allergens"] != "표시 확인 못 함")
            self.put(f"std.spec.{b6['id']}.allergen_products", al_n, f"{len(rows)}개 중 {al_n}개", note="표시 알레르기 성분을 확인한 상품 수")

    # ------------------------------------------------ A 견고성 점검
    def robustness(self):
        """robustness.py가 만든 05_robustness.json(다시 뽑기, 상품 하나씩 빼기)을 가이드 A장 값과 표로 옮긴다.
        '빼지 않음' 줄이 머리 숫자와 같은지 확인한다."""
        p = self.run / "05_robustness.json"
        if not p.exists():
            die("05_robustness.json이 없습니다. python scripts/robustness.py <회차>를 먼저 돌리세요.")
        R = json.loads(p.read_text(encoding="utf-8"))
        nm = R["names"]
        di = self.conf["direction_index"]
        loo = R["leave_one_out"]
        base = loo[0]
        if f_pct(base["head_neg"]) != self.values["head.topic_neg"]["text"] or base["weakest"] != self.values["head.topic_weakest"]["value"] \
                or base["low"] != self.values["head.dir_low"]["value"] or base["high"] != self.values["head.dir_high"]["value"]:
            die("견고성 점검의 '빼지 않음' 줄이 머리 숫자와 다릅니다.")
        rows = []
        for r in loo:
            flips = list(r["flips"]) + (["불만 지도 상위 3개 순서 바뀜"] if r.get("top3_changed") else [])
            rows.append({"out": r["out"], "brand": self.brand.get(r["out"], "") if r["out"] else "", "reviews": r["reviews"],
                         "head_neg_text": f_pct(r["head_neg"]),
                         "first_text": f"{nm[r['first']]} {f_pct(r['first_pct'])}", "second_text": f"{nm[r['second']]} {f_pct(r['second_pct'])}",
                         "weakest_text": f"{r['remain']}개 중 {r['weakest']}개",
                         "dir_text": f"{f_int(r['low'])}개 대 {f_int(r['high'])}개" + (f"({f_pct(r['low_share'])})" if r["low_share"] is not None else ""),
                         "top3_text": ", ".join(nm[t] for t in r["top3"]), "flips": flips, "flip_text": ", ".join(flips) if flips else "없음"})
        self.tables["a.robust"] = rows
        bs = R["bootstrap"]
        T = R["texts"]
        self.put("a.robust.n", bs["n"], f"{bs['n']:,}번", note=f"난수 씨앗 {bs['seed']}")
        # A장 정확도 두 줄: 설계 정보 추출 감사, 웹 조사 주장 확인
        da = self.run / "14b_detail_audit_summary.json"
        if da.exists():
            d = json.loads(da.read_text(encoding="utf-8"))
            self.put("a.detail_audit", d["fail_rate"], f"표본 {d['sample']}개 중 FAIL {d['fail']}개({d['fail_rate'] * 100:.1f}%)")
        rc = self.run / "15_research_check.json"
        if rc.exists():
            d = json.loads(rc.read_text(encoding="utf-8"))
            self.put("a.research_verified", d.get("verified"), f"{d.get('claims')}개 중 {d.get('verified')}개")
        self.put("a.robust.head_first", bs["head_first_pct"], T["head_first"],
                 note=f"다시 뽑기에서 {nm[R['head_topic']]}가 부정 언급 리뷰어(가중) 1위로 남은 비율")
        self.put("a.robust.head_neg_ci", bs["head_neg_ci"], T["head_neg_ci"], note="머리 숫자 2의 95% 구간(다시 뽑기)")
        self.put("a.robust.weakest", R["base"]["weakest"], T["weakest"], note="머리 숫자 3, 괄호는 다시 뽑기의 95% 이상을 덮는 범위")
        self.put("a.robust.weakest_dist", bs["weakest_dist"], T["weakest_dist"], note="머리 숫자 3의 다시 뽑기 분포")
        self.put("a.robust.loo_flips", sum(1 for r in rows[1:] if r["flips"]), T["loo_flips"],
                 note="상품 하나를 뺐을 때 결론(불만 1위, 약한 쪽 과반, 최대 약점 과반)이나 불만 지도 상위 3개 순서가 바뀐 경우 수")
        self.put("a.robust.loo_head_neg", None, f"{f_pct(min(r['head_neg'] for r in loo[1:]))}~{f_pct(max(r['head_neg'] for r in loo[1:]))}",
                 note="상품 하나씩 뺐을 때 머리 숫자 2의 범위")
        self.put("a.robust.loo_low_share", None,
                 f"{f_pct(min(r['low_share'] for r in loo[1:]))}~{f_pct(max(r['low_share'] for r in loo[1:]))}",
                 note=f"상품 하나씩 뺐을 때 {di['low']['name']} 쪽 비율의 범위")
        for r in loo[1:]:
            k = f"a.robust.{r['out']}"
            self.put(f"{k}.head_neg", r["head_neg"], f_pct(r["head_neg"]))
            self.put(f"{k}.weakest", r["weakest"], f"{r['remain']}개 중 {r['weakest']}개")
            self.put(f"{k}.low_share", r["low_share"], f_pct(r["low_share"]))

    def caveats(self):
        n = self.m["summary"]
        subs = [r.get("subcategory") for r in self.tables.get("s.scoreboard", [])]
        most = "모두" if subs and all(s == self.conf.get("caveat_subcategory") for s in subs) else "대부분"
        return [
            f"리뷰는 공유 리뷰 DB 표본(리뷰 {n['reviews']:,}개, ASIN {n['asins']}개)이라 낮은 별점이 실제보다 많다(표본 평균 {n['sample_mean_star']:.2f}★, "
            f"가중 평균 {n['weighted_mean_star']:.2f}★). 비율은 별점 묶음 가중으로 되돌렸다.",
            f"자유 서술에서 뽑은 수치({self.item_name(self.conf['duration_item'])} 등)는 리뷰어가 적은 값이라 측정값이 아니다. 방향과 분포로만 읽는다.",
            "개발 기준의 사양 숫자는 웹 조사 출처를 근거로 한 시작점이고 시험으로 확인해야 한다.",
            f"상품 {n['asins']}개, {most} 한 하위 카테고리({self.conf.get('caveat_subcategory', '-')})라 상품끼리, 하위 카테고리끼리의 비교가 약하다."
            if self.conf.get("caveat_subcategory") else f"상품 {n['asins']}개라 상품끼리, 하위 카테고리끼리의 비교가 약하다.",
            "시장 데이터(spd-amz-market)의 매출, 점유율, 증감, 승률 칸은 문서에 단위가 없어 단위 미확인으로 적었다.",
            f"ASIN은 매출 순위가 아니라 공유 DB에 리뷰가 많은 후보 가운데 고른 {len(self.asins) if hasattr(self, 'asins') else ''}개다(상품 확인 관문에서 사람이 확인).",
            f"머리 숫자 5번(성장 배수)은 30일 검색량 {self.conf['growth']['min_volume']:,} 이상 카테고리 검색어 "
            f"{self.values.get('m.growth_candidates', {}).get('value', '-')}개 중 2년 주간 이력을 받은 "
            f"{self.values.get('m.growth_ranked', {}).get('value', '-')}개에서 골랐다. 나머지는 이력이 없어 순위에서 빠졌다. "
            "시장 데이터의 yoYChangePct 칸은 뜻과 단위가 확인되지 않아 머리 숫자에 쓰지 않는다.",
        ] + list(self.conf.get("caveats_extra") or [])


def build(run):
    g = G(run)
    g.head()
    g.market_ch()
    g.scoreboard()
    g.problems()
    g.standards()
    g.specs_link()
    g.robustness()
    g.tables["meta.focus"] = [{"id": f["id"], "title": f.get("title"), "split_label": f.get("split_label"),
                               "split_label_name": g.label_name.get(f.get("split_label"), f.get("split_label"))} for f in g.conf.get("focus") or []]
    g.tables["meta.brand_nodes"] = list(g.conf.get("market_nodes_brand_share") or [])
    g.tables["meta.market_keys"] = g.mkeys
    # 점수표 머리와 각주에 쓸 카테고리 이름(없으면 렌더러가 향수 때의 문구를 씀)
    di = g.conf["direction_index"]
    g.tables["meta.scoreboard"] = {"topic_name": g.schema[g.conf["head_topic"]]["name_ko"], "dir_high": di["high"]["name"],
                                   "dir_low": di["low"]["name"], "dir_min": di["min_reviews"], "duration_name": g.item_name(g.conf["duration_item"]),
                                   "duration_unit": g.unit(g.conf["duration_item"]), "duration_min": g.conf["duration_min_values"]}
    # 화면 제목과 값 이름(영어 id 대신): 설계 정보 항목 이름, 값 이름, 주제 이름
    _items = (load_yaml(g.run / "13_detail_schema_approved.yaml") or {}).get("items") or []
    g.tables["meta.names"] = {"items": {i["id"]: i.get("name_ko") for i in _items},
                              "values": {i["id"]: {str(v.get("value")): v.get("ko") for v in i.get("allowed_values") or []} for i in _items},
                              "topics": {k: v["name_ko"] for k, v in g.schema.items()}}
    g.tables["meta.duration_name"] = (g.dcounts["items"].get(g.conf.get("duration_item")) or {}).get("name_ko")
    if g.conf.get("anatomy"):
        g.tables["meta.anatomy"] = g.conf["anatomy"]
    out = {"made_at": now_iso(), "run": run.name, "title": g.conf.get("title"), "values": g.values, "tables": g.tables, "ev": g.ev,
           "quotes": g.quotes, "caveats": g.caveats(),
           "sources": {"reviews": f"02_reviews.csv {len(g.reviews):,}개", "tags": f"04_tags.jsonl {len(g.tags):,}개",
                       "labels": f"07b_issue_labels.jsonl {len(g.labels):,}개", "details": f"14_details.jsonl {len(g.details):,}개",
                       "market": "market/market.json(spd-amz-market, 2026-10-07)", "research": "15_research.yaml",
                       **({"specs": "23_specs_verified.json(브랜드 사이트와 소매점 상품 페이지, 다시 열어 확인한 값만)"} if (run / "23_specs_verified.json").exists() else {})}}
    write_json(run / "16_guide_metrics.json", out)
    print(f"16_guide_metrics.json: 값 {len(g.values)}개, 표 {len(g.tables)}개, 근거 묶음 {len(g.ev)}개"
          f"(리뷰 id {sum(len(e['i']) for e in g.ev.values()):,}개)")
    return 0


def main():
    ap = argparse.ArgumentParser(description="개발 가이드 숫자")
    ap.add_argument("run", nargs="?")
    args = ap.parse_args()
    sys.exit(build(resolve_run(args.run)))


if __name__ == "__main__":
    main()
