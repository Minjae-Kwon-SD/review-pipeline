"""market.py build: market/raw/의 spd-amz-market 응답으로 market/market.json과 market/market_summary.md를 만든다.
숫자는 응답 값 그대로 옮기고(비율과 합만 계산), 행마다 원본 파일을 적는다. 칸의 뜻이나 단위가 문서에 없으면 "단위 미확인"."""
import json
import re
from datetime import datetime, timezone
from pathlib import Path

from pipeline_io import ASIN_COLS, category_conf, die, load_csv_or_die, now_iso, write_json

# 카테고리마다 다른 값은 config/categories/<카테고리>.yaml의 market 절에서 읽는다(use_conf)
PARENT_NODE, CONTEXT_NODES, TERM_WORDS, NODES, SEED, MAX_NODES = None, (), (), {}, "", 15
TERMS_TOP = 50
NOTE_UNIT = "단위 미확인"


def load(raw, name):
    p = raw / name
    return (json.loads(p.read_text(encoding="utf-8")), f"market/raw/{name}") if p.exists() else (None, None)


def safe(s):
    return re.sub(r"[^0-9A-Za-z가-힣]+", "_", str(s)).strip("_")[:60]


def payload(d):
    if isinstance(d, dict) and isinstance(d.get("payload"), list):
        return d["payload"]
    return d if isinstance(d, list) else []


def keys_of(rows):
    ks = []
    for r in rows[:50]:
        for k in r:
            if k not in ks:
                ks.append(k)
    return ks


def day(ts):
    return datetime.fromtimestamp(ts, timezone.utc).strftime("%Y-%m-%d")


def market_conf(run):
    c = category_conf(run).get("market") or {}
    if not c:
        die("config/categories/<카테고리>.yaml에 market 절(seed, parent_node, nodes, term_words)이 없습니다.")
    return c


def use_conf(run):
    """market 절을 이 모듈 값으로 쓴다."""
    global PARENT_NODE, CONTEXT_NODES, TERM_WORDS, NODES, SEED, MAX_NODES
    c = market_conf(run)
    PARENT_NODE = int(c["parent_node"])
    CONTEXT_NODES = tuple(int(x) for x in c.get("context_nodes") or ())
    TERM_WORDS = tuple(str(w).lower() for w in c.get("term_words") or ())
    NODES = dict(c["nodes"])
    SEED = c["seed"]
    MAX_NODES = int(c.get("max_nodes", 15))
    return c


def term_rule(term, brands, words=None):
    """카테고리 검색어: config market.term_words의 낱말이나 브랜드 이름이 들어 있음"""
    t = term.lower()
    return any(w in t for w in (TERM_WORDS if words is None else words)) or any(b and b.lower() in t for b in brands)


def build(run):
    use_conf(run)
    raw = run / "market" / "raw"
    calls = [json.loads(l) for l in (run / "market" / "calls.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()]
    asins = [r for r in load_csv_or_die(run / "01_asins.csv", ASIN_COLS) if r["status"] == "selected"]
    out = {"made_at": now_iso(), "run": run.name, "marketplace": "US", "tables": {}, "fields": {}, "not_obtained": [], "notes": []}
    T = out["tables"]

    # 1. 하위 카테고리(카테고리 노드의 자식 + 위 노드)
    subs, src = load(raw, "subcategories_search_all.json")
    by_id = {int(x["id"]): x for x in subs or []}
    cols = ["id", "subcategoryName", "subcategoryContextName", "parentId", "level", "totalMonthlyRevenue", "totalNumberUnitsSold",
            "totalBrands", "totalAsins", "avgPrice", "avgRating", "avgReviews", "momGrowth", "momGrowth12", "azRevenuePct", "sellerRevenuePct"]
    rows = [x for x in subs or [] if x.get("parentId") == PARENT_NODE and int(x["id"]) > 0]
    rows.sort(key=lambda x: -(x.get("totalMonthlyRevenue") or 0))
    ctx = [by_id[i] for i in CONTEXT_NODES if i in by_id]
    T["subcategories"] = [{**{c: x.get(c) for c in cols}, "source": src} for x in (ctx + rows)[:MAX_NODES]]
    out["fields"]["subcategories_search"] = keys_of(subs or [])
    our_nodes = {}
    for a in asins:
        p, _ = load(raw, f"products_byasin_{a['asin']}.json")
        p = p[0] if isinstance(p, list) and p else p
        if p and p.get("subcategoryId") in by_id:
            our_nodes[a["asin"]] = by_id[p["subcategoryId"]].get("subcategoryContextName")

    # 2. 브랜드 상위 20(EDP, EDT)
    bcols = ["brandName", "revenue", "marketshare", "moMMktShareChange", "numberASINs", "totalNumberUnitsSold", "avgPrice",
             "reviewRating", "totalReviews", "avgReviews", "adSpendShare"]
    for k, node in NODES.items():
        d, src = load(raw, f"subcategories_category_competitors_{safe(node)}.json")
        rows = payload(d)
        T[f"brands_{k}"] = [{**{c: r.get(c) for c in bcols}, "source": src} for r in rows[:20]]
        out["fields"]["subcategories_category_competitors"] = keys_of(rows)
    bad, _ = load(raw, "subcategories_category_competitors_Eau_de_Parfum.json")
    if bad is not None:
        top = (payload(bad) or [{}])[0].get("brandName")
        out["notes"].append(f"subcategories_category_competitors를 노드 이름만(\"Eau de Parfum\", \"Eau de Toilette\")으로 부르면 두 결과가 같고 1위가 {top}"
                            "(평균 가격 1,364)라 향수 카테고리가 아님. 버리고 subcategoryContextName(\"Women's Eau de Parfum\")으로 다시 부른 결과만 씀.")

    # 3. 검색어 상위 50(EDP, EDT): 규칙(향수 낱말이나 브랜드 이름이 든 검색어)으로 거른 뒤 30일 검색량 순
    brands = sorted({r["brandName"] for k in NODES for r in T[f"brands_{k}"] if r.get("brandName")} | {a["brand"] for a in asins})
    tcols = ["searchTermValue", "volume30Day", "current4WkVolume", "priorYear4WkVolume", "yoYChange", "yoYChangePct", "relevancy", "numRelatedProducts"]
    for k, node in NODES.items():
        d, src = load(raw, f"subcategories_relevant_search_terms_{safe(node)}.json")
        rows = payload(d)
        kept = [r for r in rows if term_rule(str(r.get("searchTermValue", "")), brands)]
        kept.sort(key=lambda r: -(r.get("volume30Day") or 0))
        T[f"terms_{k}"] = [{**{c: r.get(c) for c in tcols}, "source": src} for r in kept[:TERMS_TOP]]
        out["fields"]["subcategories_relevant_search_terms"] = keys_of(rows)
        out["notes"].append(f"{node} 관련 검색어 {len(rows):,}개 중 카테고리 낱말({', '.join(TERM_WORDS)})이나 브랜드 이름(상위 20 브랜드와 우리 6개)이 든 것 "
                            f"{len(kept):,}개를 30일 검색량 순으로 50개. 응답의 relevancy만으로는 \"now\", \"yellowstone\" 같은 검색어가 남아 이 규칙을 씀.")

    # 4. 검색어 추이(search_terms_trends): 응답 안에서 그 검색어 자신의 행
    trend_rows, used = [], set()
    for c in calls:
        if c.get("tool") != "search_terms_trends" or not c.get("ok"):
            continue
        kw = c["args"]["keyword"]
        if kw in used:
            continue
        used.add(kw)
        d, src = load(raw, f"search_terms_trends_{safe(kw)}.json")
        rows = payload(d)
        me = next((r for r in rows if str(r.get("searchTerm", "")).lower() == kw.lower()), None)
        rel = term_rule(kw, brands)
        if me is None:
            trend_rows.append({"keyword": kw, "found": False, "fragrance_term": rel, "source": src})
            continue
        h = me.get("history") or []
        trend_rows.append({"keyword": kw, "found": True, "fragrance_term": rel, "estimateSearches": me.get("estimateSearches"),
                           "growth1m": me.get("estimateSearchesGrowth1Month"), "growth3m": me.get("estimateSearchesGrowth3Months"),
                           "growth6m": me.get("estimateSearchesGrowth6Months"), "growth12m": me.get("estimateSearchesGrowth12Months"),
                           "history_from": h[0]["date"][:10] if h else None, "history_to": h[-1]["date"][:10] if h else None,
                           "history_weeks": len(h), "first_week": h[0].get("estimateSearches") if h else None,
                           "last_week": h[-1].get("estimateSearches") if h else None, "source": src})
        out["fields"]["search_terms_trends"] = keys_of(rows)
    T["trends"] = trend_rows

    # 5. 우리 상품 6개(products_byasin + products_history)
    pcols = ["asin", "brandName", "title", "size", "unitValue", "unitType", "buyBoxPrice", "averageBuyBoxPrice", "monthlyRevenueEstimate",
             "monthlyUnitsSold", "amzMonthlySold", "reviewRating", "reviewCount", "rank", "subcategoryRank", "subcategoryId",
             "numberOfSellers", "listedSince", "hasAPlus", "itemHighlights"]
    prod = []
    for a in asins:
        p, src = load(raw, f"products_byasin_{a['asin']}.json")
        p = p[0] if isinstance(p, list) and p else (p or {})
        out["fields"]["products_byasin"] = list(p.keys())
        row = {c: p.get(c) for c in pcols}
        row["subcategory"] = our_nodes.get(a["asin"])
        row["source"] = src
        h, hsrc = load(raw, f"products_history_{a['asin']}.json")
        if isinstance(h, dict):
            out["fields"]["products_history"] = list(h.keys())
            for series in ("amazon", "buyBoxShipping", "salesRank", "reviewCount"):
                pts = [x for x in h.get(series) or [] if x.get("value") is not None]
                if pts:
                    vals = [x["value"] for x in pts]
                    row[f"hist_{series}"] = {"points": len(pts), "from": day(pts[0]["unixTimeStampSeconds"]),
                                             "to": day(pts[-1]["unixTimeStampSeconds"]), "first": vals[0], "last": vals[-1],
                                             "min": min(vals), "max": max(vals)}
            row["history_source"] = hsrc
        prod.append(row)
    T["our_products"] = prod

    # 6. 광고와 상위 상품
    d, src = load(raw, f"search_terms_advertised_brands_{safe(SEED)}.json")
    T["advertised_brands"] = [{**r, "source": src} for r in payload(d)]
    out["fields"]["search_terms_advertised_brands"] = keys_of(payload(d))
    ad_files = sorted(raw.glob("search_terms_ad_spy_*.json"))
    T["ad_spy"] = []
    for f in ad_files:
        rows = payload(json.loads(f.read_text(encoding="utf-8")))
        out["fields"]["search_terms_ad_spy"] = keys_of(rows)
        brand = f.stem.replace("search_terms_ad_spy_", "").replace("_", " ")
        T["ad_spy"] += [{"brand": brand, **{k: r.get(k) for k in ("searchTermValue", "estimateSearches", "estimatedCpc", "totalAdSpend",
                                                                  "sponsoredProducts", "topGroupWinRate", "topSpotWinRate")},
                         "source": f"market/raw/{f.name}"} for r in rows]
    d, src = load(raw, f"search_terms_trends_top_products_{safe(SEED)}.json")
    tp = payload(d)
    out["fields"]["search_terms_trends_top_products"] = keys_of(tp)
    T["top_products"] = [{"brandName": r.get("brandName"), "asin": r.get("asin"), "title": r.get("title"), "avgRank": r.get("avgRank"),
                          "latestRank": r.get("latestRank"), "days": len(r.get("searchTermProductRanksDailies") or []), "source": src} for r in tp]
    T["calls"] = calls

    out["not_obtained"] = [
        "검색어별 CPC: 카테고리 검색어에는 없음. search_terms_ad_spy(브랜드 하나의 광고 검색어)에만 estimatedCpc가 있어, 이번에는 " + (", ".join(sorted({r["brand"] for r in T["ad_spy"]})) or "아무 브랜드도") + f" 광고 검색어 {len(T['ad_spy'])}개만 받음(단위 미확인).",
        "광고비 비중(검색 결과 중 스폰서 비율): 없음. 브랜드별 adSpendShare(경쟁 브랜드 표)와 검색어별 광고 승률만 있음(뜻과 단위 미확인).",
        "전체 시장 규모: 아마존 US 노드 월매출(totalMonthlyRevenue)만 있음. 아마존 밖 시장이나 연간 공식 수치는 없음(웹 조사 단계).",
        "아마존 직판(1P) 비중: azRevenuePct, sellerRevenuePct 칸은 있으나 뜻을 설명한 문서가 없음(단위 미확인).",
        "상품 bullet 전체와 성분표: 칸이 없음. itemHighlights(한 줄 요약)만 " f"{len(prod)}개 중 "
        f"{sum(1 for r in prod if r.get('itemHighlights'))}개에 있고, 비어 있는 것은 "
        f"{', '.join(r['asin'] for r in prod if not r.get('itemHighlights')) or '없음'}.",
    ]
    failed = [c for c in calls if not c.get("ok")]     # 받지 못한 호출(회차마다 다름)
    if failed:
        out["not_obtained"].append("실패한 호출: " + ", ".join(f"{c.get('tool')} {c.get('args', {}).get('keyword') or c.get('args', {}).get('subcategoryContextName') or ''}".strip() for c in failed[:10]))
    write_json(run / "market" / "market.json", out)
    (run / "market" / "market_summary.md").write_text(render(out), encoding="utf-8")
    per = ", ".join(f"{k} 브랜드 {len(T.get(f'brands_{k}', []))}, 검색어 {len(T.get(f'terms_{k}', []))}" for k in NODES)   # 노드 키는 카테고리 설정에서
    print(f"market.json, market_summary.md를 만들었습니다(하위 카테고리 {len(T['subcategories'])}행, {per}, "
          f"추이 {len(T['trends'])}, 우리 상품 {len(T['our_products'])}).")
    return 0


def n(v, d=0):
    if v is None:
        return "-"
    if isinstance(v, bool):
        return "예" if v else "아니오"
    if isinstance(v, (int, float)):
        return f"{v:,.{d}f}"
    return str(v)


def p(v):
    return "-" if v is None else f"{100 * v:.1f}%"


def render(o):
    T = o["tables"]
    L = [f"# 시장 데이터 요약: {o.get('run', '')}", "",
         f"spd-amz-market(무료)만 썼습니다. 마켓 US, 만든 때 {o['made_at']}. 숫자는 응답 값 그대로이고, 칸의 뜻이나 단위가 문서에 없으면 \"단위 미확인\"으로 적었습니다. "
         "행마다 원본 파일은 market.json의 source에 있습니다.", "", "## 1. 호출 목록", "",
         "| # | 도구 | 입력 | 결과 | 행 수 | 비고 |", "|---|---|---|---|---|---|"]
    for i, c in enumerate(T["calls"], 1):
        res = "성공" if c.get("ok") else "실패"
        note = "회차 raw/의 같은 날 응답을 복사(호출 없음)" if c.get("reused_from") else (c.get("error", "")[:70] if not c.get("ok") else "")
        if c.get("ok") and c.get("attempt") == 2:
            note = "두 번째 시도에 성공"
        L.append(f"| {i} | {c['tool']} | {json.dumps(c['args'], ensure_ascii=False)} | {res} | {n(c.get('rows'))} | {note} |")
    called = sum(1 for c in T["calls"] if c.get("called"))
    L += ["", f"실제 호출 {called}번(한도 40번), 실패 {sum(1 for c in T['calls'] if c.get('called') and not c.get('ok'))}번.", ""]

    L += ["## 2. 하위 카테고리(카테고리 노드와 위 노드)", "", "월 매출, 판매량은 칸 이름(totalMonthlyRevenue, totalNumberUnitsSold) 그대로이고 통화와 기간은 문서에 없어 단위 미확인. "
          "증감(momGrowth, momGrowth12), azRevenuePct, sellerRevenuePct도 단위 미확인.", "",
          "| 노드 id | 이름 | 월 매출 | 판매량 | 브랜드 수 | ASIN 수 | 평균 가격 | 평균 별점 | momGrowth | momGrowth12 | azRevenuePct | sellerRevenuePct |",
          "|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for r in T["subcategories"]:
        L.append(f"| {r['id']} | {r['subcategoryContextName'] or r['subcategoryName']} | {n(r['totalMonthlyRevenue'])} | {n(r['totalNumberUnitsSold'])} | "
                 f"{n(r['totalBrands'])} | {n(r['totalAsins'])} | {n(r['avgPrice'], 2)} | {n(r['avgRating'], 2)} | {n(r['momGrowth'], 2)} | "
                 f"{n(r['momGrowth12'], 2)} | {n(r['azRevenuePct'], 4)} | {n(r['sellerRevenuePct'], 4)} |")
    L.append("")
    for k, node in NODES.items():
        L += [f"## 3. 브랜드 상위 20: {node}", "", "marketshare, moMMktShareChange, adSpendShare는 응답 값 그대로(단위 미확인). revenue는 칸 이름 그대로(기간과 통화 단위 미확인).", "",
              "| 순위 | 브랜드 | revenue | marketshare | moMMktShareChange | ASIN 수 | 판매량 | 평균 가격 | 평균 별점 | 리뷰 수 | adSpendShare |",
              "|---|---|---|---|---|---|---|---|---|---|---|"]
        for i, r in enumerate(T[f"brands_{k}"], 1):
            L.append(f"| {i} | {r['brandName']} | {n(r['revenue'])} | {n(r['marketshare'], 4)} | {n(r['moMMktShareChange'], 4)} | {n(r['numberASINs'])} | "
                     f"{n(r['totalNumberUnitsSold'])} | {n(r['avgPrice'], 2)} | {n(r['reviewRating'], 2)} | {n(r['totalReviews'])} | {n(r['adSpendShare'], 3)} |")
        L.append("")
    for k, node in NODES.items():
        L += [f"## 4. 검색어 상위 50: {node}", "", "| 순위 | 검색어 | 30일 검색량 | 최근 4주 | 작년 같은 4주 | yoYChange | yoYChangePct | relevancy |", "|---|---|---|---|---|---|---|---|"]
        for i, r in enumerate(T[f"terms_{k}"], 1):
            L.append(f"| {i} | {r['searchTermValue']} | {n(r['volume30Day'])} | {n(r['current4WkVolume'])} | {n(r['priorYear4WkVolume'])} | "
                     f"{n(r['yoYChange'])} | {n(r['yoYChangePct'], 4)} | {n(r['relevancy'])} |")
        L.append("")
    L += ["## 5. 검색어 추이(search_terms_trends, 12개월)", "", "growth 칸은 응답 값 그대로(estimateSearchesGrowth1Month 등, 단위 미확인). "
          "카테고리 검색어 표시가 아니오인 것은 처음 고른 규칙(relevancy만)으로 잘못 고른 검색어라 해석에 쓰지 않습니다.", "",
          "| 검색어 | 카테고리 검색어 | 추정 검색 수 | 1개월 | 3개월 | 6개월 | 12개월 | 이력 기간 | 주 수 | 첫 주 | 마지막 주 |", "|---|---|---|---|---|---|---|---|---|---|---|"]
    for r in T["trends"]:
        if not r["found"]:
            L.append(f"| {r['keyword']} | {n(r['fragrance_term'])} | 응답에 그 검색어 행 없음 | | | | | | | | |")
            continue
        L.append(f"| {r['keyword']} | {n(r['fragrance_term'])} | {n(r['estimateSearches'])} | {n(r['growth1m'])} | {n(r['growth3m'])} | {n(r['growth6m'])} | "
                 f"{n(r['growth12m'])} | {r['history_from']} ~ {r['history_to']} | {r['history_weeks']} | {n(r['first_week'])} | {n(r['last_week'])} |")
    L += ["", "## 6. 우리 상품 6개(products_byasin, products_history)", "", "monthlyRevenueEstimate, monthlyUnitsSold, amzMonthlySold는 칸 이름 그대로(단위 미확인). "
          "가격 이력(amazon, buyBoxShipping)과 순위 이력(salesRank)의 값 단위는 문서에 없어 단위 미확인이고, 같은 날의 buyBoxPrice와 나란히 적었습니다.", "",
          "| ASIN | 브랜드 | 용량 | buyBoxPrice | 월 매출 추정 | 월 판매량 | amzMonthlySold | 별점 | 리뷰 수 | 하위 카테고리 | 카테고리 순위 | 판매자 수 | 등록일 | A+ | itemHighlights |",
          "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for r in T["our_products"]:
        L.append(f"| {r['asin']} | {r['brandName']} | {r['size']} | {n(r['buyBoxPrice'], 2)} | {n(r['monthlyRevenueEstimate'])} | {n(r['monthlyUnitsSold'])} | "
                 f"{n(r['amzMonthlySold'])} | {n(r['reviewRating'], 1)} | {n(r['reviewCount'])} | {r['subcategory']} | {n(r['subcategoryRank'])} | "
                 f"{n(r['numberOfSellers'])} | {str(r['listedSince'] or '-')[:10]} | {n(r['hasAPlus'])} | {'비어 있음' if not r['itemHighlights'] else '있음'} |")
    L += ["", "itemHighlights(응답 원문 그대로, 한 줄 요약):", ""]
    for r in T["our_products"]:
        L.append(f"- {r['asin']} {r['brandName']}: {r['itemHighlights'] or '비어 있음'}")
    L += ["", "| ASIN | 이력 | 점 수 | 기간 | 처음 값 | 마지막 값 | 최소 | 최대 |", "|---|---|---|---|---|---|---|---|"]
    for r in T["our_products"]:
        for s in ("amazon", "buyBoxShipping", "salesRank", "reviewCount"):
            h = r.get(f"hist_{s}")
            if h:
                L.append(f"| {r['asin']} | {s} | {n(h['points'])} | {h['from']} ~ {h['to']} | {n(h['first'], 2)} | {n(h['last'], 2)} | {n(h['min'], 2)} | {n(h['max'], 2)} |")
    L += ["", f"## 7. 광고와 상위 상품(\"{SEED}\")", "", "### 이 검색어에 광고하는 브랜드(search_terms_advertised_brands)", "",
          "| 브랜드 | sponsoredProducts | sponsoredBrandWinRate | topGroupWinRate | topSpotWinRate |", "|---|---|---|---|---|"]
    for r in T["advertised_brands"]:
        L.append(f"| {r.get('name')} | {n(r.get('sponsoredProducts'))} | {n(r.get('sponsoredBrandWinRate'), 3)} | {n(r.get('topGroupWinRate'), 3)} | {n(r.get('topSpotWinRate'), 3)} |")
    L += ["", "승률 칸은 응답 값 그대로(단위 미확인).", "", "### 브랜드 광고 검색어(search_terms_ad_spy)", "",
          "search_terms_ad_spy는 입력이 브랜드 이름이라 검색어로는 부를 수 없어, 우리 상품의 첫 브랜드("
          + (", ".join(sorted({r["brand"] for r in T.get("ad_spy", [])})) or "없음") + ")로 한 번 불렀습니다. estimatedCpc, totalAdSpend는 단위 미확인.", "",
          "| 브랜드 | 검색어 | 추정 검색 수 | estimatedCpc | totalAdSpend | sponsoredProducts | topGroupWinRate | topSpotWinRate |", "|---|---|---|---|---|---|---|---|"]
    for r in T["ad_spy"]:
        L.append(f"| {r['brand']} | {r['searchTermValue']} | {n(r['estimateSearches'])} | {n(r['estimatedCpc'], 2)} | {n(r['totalAdSpend'], 2)} | "
                 f"{n(r['sponsoredProducts'])} | {n(r['topGroupWinRate'], 3)} | {n(r['topSpotWinRate'], 3)} |")
    L += ["", "### 이 검색어의 상위 상품(search_terms_trends_top_products)", "", "| 브랜드 | ASIN | 제목 | avgRank | latestRank | 일별 기록 수 |", "|---|---|---|---|---|---|"]
    for r in T["top_products"]:
        L.append(f"| {r['brandName']} | {r['asin']} | {str(r['title'])[:70]} | {n(r['avgRank'], 1)} | {n(r['latestRank'])} | {r['days']} |")
    L += ["", "## 8. 받지 못한 것", ""] + [f"- {x}" for x in o["not_obtained"]]
    L += ["", "## 9. 메모", ""] + [f"- {x}" for x in o["notes"]]
    L += ["", "## 10. 도구마다 응답 칸 이름", ""]
    for tool, ks in o["fields"].items():
        L.append(f"- {tool}: {', '.join(ks)}")
    return "\n".join(L) + "\n"
