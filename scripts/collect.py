"""0단계: 리뷰 수집(공유 리뷰 DB에서 받기, 유료 수집은 설정으로 막아 둠).

사용: python scripts/collect.py candidates <회차> --category perfume
  공유 DB에서 카테고리 키워드로 리뷰를 검색해 서로 다른 ASIN을 모으고, 상품 제목 규칙
  (config/categories/<카테고리>.yaml의 title_include, title_exclude)으로 거른다.
  후보마다 get_review_stats(asin 전체 값)와 search_reviews(asin, limit 1)의 rating_summary를 받는다.
  결과: 00_candidates.csv(DB 리뷰 수 많은 순), 원문 응답은 raw/candidates/.

사용: python scripts/collect.py rank <회차> --category hairremovalcream [--max-product-calls 25]
  (2026-10-10, H2부터) 검색 순위와 매출로 후보를 고른다. DB에 있는 상품으로 고르던 candidates의 약점을 고친 방식.
  config/categories/<카테고리>.yaml의 selection.seeds 검색어마다 spd-amz-market search_terms_trends_top_products(무료)로
  상위 상품을 받고, 제목 규칙으로 거른 뒤 평균 순위 앞쪽부터 products_byasin(무료)으로 월 매출 추정, 리뷰 수, 평점, 부모 ASIN을 붙인다.
  같은 부모는 매출이 큰 하나만 남기고, 후보마다 공유 DB 통계(get_review_stats, search_reviews limit 1, 무료)를 붙인다.
  매출 순으로 selection.pick(기본 10)개에 rank_pick 번호를 주고, DB 리뷰가 selection.min_db_reviews(기본 100)보다 적으면
  need_paid=yes로 적는다. 결과: 00_candidates.csv(candidates와 같은 칸 뒤에 순위, 매출 칸), 00_candidates_log.json(뺀 것과 이유).
  응답 원문은 raw/candidates/top_<검색어>.json, raw/product_<ASIN>.json(pull이 다시 쓰고, market.py가 복사해 씀).

사용: python scripts/collect.py pull <회차> [--mode db|paid] [--offline] [--confirm-paid] [--paid-asins A,B] [--paid-test]
  01_asins.csv에서 status가 selected인 ASIN만 받는다.
  db 모드: search_reviews(asin 전체 값, limit 200, offset 끝까지). asin은 부분일치(ILIKE)라
    응답의 asin이 정확히 같은 행만 남긴다. 원문은 raw/reviews_<ASIN>.json.
    --offline이면 raw 파일이 있는 ASIN은 다시 받지 않고 그 파일로 변환만 한다.
  products_byasin(marketplace US)으로 brandName, parentAsin, title, reviewRating을 받아 raw/product_<ASIN>.json에
    저장하고 01_asins.csv의 brand, title, amazon_rating, parent_asin 빈칸을 채운다(값이 있으면 그대로).
  paid 모드: config/pipeline.yaml의 paid.enabled가 true이고 --confirm-paid가 있을 때만
    scrape_reviews(regions com, sort recent, 별점마다 paid.max_pages_per_star 페이지)를 먼저 부르고 db 모드처럼 받는다.
    유료로 받는 ASIN: --paid-asins로 준 것, 없으면 selected 중 공유 DB 리뷰가 paid.scrape_below_db_reviews보다 적은 것만
    (get_review_stats, 무료로 확인). paid.max_asins를 넘으면 부르지 않고 멈춘다.
    paid.split_by_star가 true면 ASIN x 별점마다 한 번씩 부른다(한 번에 다섯 별점을 부르면 시간 초과 위험, 문서 경고).
    호출마다 raw/paid_calls.jsonl에 적고(걸린 초 포함), 이미 성공한 (ASIN, 별점) 호출은 다시 부르지 않는다(다시 돌려도 돈이 두 번 들지 않음).
    paid.max_scrape_calls는 이 로그의 전체 호출 수 한도다.
    --paid-test: 첫 대상 ASIN 하나, 1★ 하나, 1페이지만 부르고 걸린 시간, 받은 수, DB에 rating_summary가 붙는지 찍고 끝낸다(수집 안 함).
    응답에 비용 칸은 없다. 실제 금액은 Apify 계정에서만 보인다.
  본문이 공백뿐인 리뷰는 02_reviews.csv에서 뺀다(인용을 본문에서 확인하므로). 뺀 목록은 02_collect_log.json.
  결과: 02_reviews.csv, 02_star_distribution.csv, 02_collect_log.json.
    끝에 ASIN별 리뷰 수, 별점별 건수, 언어별 건수를 찍는다.

사용: python scripts/collect.py prices <회차> [--offline]
  selected ASIN마다 부모 ASIN의 변형(spd-amz-market products_variations, 무료)을 받아 01_asins.csv의 price_band
  (변형 가격 범위와 용량 범위, 예 36.00~115.54달러(0.33~3.3 fl oz))와 price_usd(이 ASIN 가격)를 채운다.
  원문은 raw/variations_<부모>.json, 조회 날짜와 변형 목록은 01_prices.json.

토큰은 .mcp.json의 ${AMZ_REVIEW_TOKEN}처럼 환경 변수에서만 읽고 출력하거나 파일에 쓰지 않는다.
"""
import argparse
import csv
import html
import json
import re
import sys
import threading
import time
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from mcp_http import MCPError, Session, call_tool
from pipeline_io import (ASIN_COLS, ASIN_OPT, DIST_COLS, DIST_OPT, REVIEW_COLS, REVIEW_OPT, ROOT, STARS, die,
                         load_config, load_yaml, now_iso, read_csv, write_json)

REVIEW_SERVER, MARKET_SERVER = "amz-review", "spd-amz-market"
PAGE = 200
SUMMARY_KEYS = {5: "fiveStar", 4: "fourStar", 3: "threeStar", 2: "twoStar", 1: "oneStar"}


def run_dir(name, create=False):
    p = Path(name)
    if not p.is_absolute() and not p.is_dir():
        p = ROOT / "runs" / name
    if create:
        p.mkdir(parents=True, exist_ok=True)
    elif not p.is_dir():
        die(f"회차 폴더가 없습니다: {p}")
    return p


def call(server, tool, args):
    try:
        return call_tool(server, tool, args)
    except MCPError as e:
        die(str(e))


def call_fresh(server, tool, args):
    """동시 호출용: 호출마다 세션을 새로 연다(세션 하나를 여러 스레드가 함께 쓰지 않게)."""
    try:
        return Session(server).call(tool, args)
    except MCPError as e:
        die(str(e))


def search_all(args, save_prefix=None):
    """search_reviews를 offset을 늘려 끝까지 부른다. (응답 원문 목록, 리뷰 목록)"""
    pages, reviews, off = [], [], 0
    while True:
        text, d = call(REVIEW_SERVER, "search_reviews", {**args, "limit": PAGE, "offset": off})
        if save_prefix:
            save_prefix.parent.mkdir(parents=True, exist_ok=True)
            (save_prefix.parent / f"{save_prefix.name}_{off:06d}.json").write_text(text, encoding="utf-8")
        pages.append(d)
        got = d.get("reviews") or []
        reviews += got
        if len(got) < PAGE:
            return pages, reviews
        off += PAGE


def real_from_summary(rs):
    """rating_summary를 {별점: 퍼센트}로. 없으면 None."""
    if not isinstance(rs, dict):
        return None
    out = {}
    for s, k in SUMMARY_KEYS.items():
        v = (rs.get(k) or {}).get("percentage")
        if v is None:
            return None
        out[s] = v
    return out


def has_any(title, words):
    t = (title or "").lower()
    return any(w.lower() in t for w in words)


def kind_hint(title, rules):
    for kind, words in (rules or {}).items():
        if has_any(title, words):
            return kind
    return "other"


def records(data):
    """응답에서 행(사전) 목록을 꺼낸다(market.py records와 같은 규칙)."""
    if isinstance(data, list):
        return [x for x in data if isinstance(x, dict)]
    if isinstance(data, dict):
        best = [v for v in data.values() if isinstance(v, list) and v and isinstance(v[0], dict)]
        return max(best, key=len) if best else [data]
    return []


def safe_name(s):
    return re.sub(r"[^0-9A-Za-z]+", "_", str(s)).strip("_")[:60]


def num(v):
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


# ---------------------------------------------------------------- candidates

def candidates(run, category):
    cat_path = ROOT / "config" / "categories" / f"{category}.yaml"
    cat = load_yaml(cat_path) or {}
    raw = run / "raw" / "candidates"
    t0 = time.time()
    titles, seen = {}, set()
    for kw in cat.get("keywords") or []:
        _, revs = search_all({"keyword": kw}, raw / f"search_kw_{kw}")
        for r in revs:
            seen.add(r.get("id") or r.get("review_id"))
            titles.setdefault(r["asin"], r.get("product_title") or "")
        print(f"  키워드 {kw}: 리뷰 {len(revs)}개", flush=True)
    keep = sorted(a for a, t in titles.items()
                  if has_any(t, cat.get("title_include") or []) and not has_any(t, cat.get("title_exclude") or []))
    print(f"검색 리뷰 {len(seen)}개, ASIN {len(titles)}개 중 제목 규칙에 맞는 후보 {len(keep)}개", flush=True)

    rows = []
    for a in keep:
        st_text, st = call(REVIEW_SERVER, "get_review_stats", {"asin": a})
        (raw / f"stats_{a}.json").write_text(st_text, encoding="utf-8")
        one_text, one = call(REVIEW_SERVER, "search_reviews", {"asin": a, "limit": 1})
        (raw / f"one_{a}.json").write_text(one_text, encoding="utf-8")
        r1 = (one.get("reviews") or [{}])[0]
        real = real_from_summary(r1.get("rating_summary")) or {}
        dist = st.get("rating_distribution") or {}
        dr = st.get("date_range") or {}
        if st.get("asin_count") != 1:
            print(f"  주의: {a} get_review_stats의 asin_count가 {st.get('asin_count')}입니다(1이어야 단일 상품).")
        rows.append({
            "asin": a, "product_title": titles[a], "db_reviews": st.get("total_reviews"),
            **{f"db_s{s}": dist.get(str(s), 0) for s in STARS},
            **{f"real_s{s}": real.get(s, "") for s in STARS},
            "total_ratings": r1.get("total_ratings", ""), "average_rating": r1.get("average_rating", ""),
            "date_min": dr.get("earliest") or "", "date_max": dr.get("latest") or "",
            "kind_hint": kind_hint(titles[a], cat.get("kind_rules")), "asin_count": st.get("asin_count"),
        })
    rows.sort(key=lambda r: (-(r["db_reviews"] or 0), r["asin"]))
    cols = ["asin", "product_title", "db_reviews", *[f"db_s{s}" for s in STARS], *[f"real_s{s}" for s in STARS],
            "total_ratings", "average_rating", "date_min", "date_max", "kind_hint", "asin_count"]
    with open(run / "00_candidates.csv", "w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        w.writerows(rows)
    print(f"후보 {len(rows)}개를 00_candidates.csv에 적었습니다({time.time() - t0:.0f}초). DB 리뷰 수 많은 순:")
    for r in rows:
        print(f"  {r['asin']} {r['kind_hint']:<9} DB {r['db_reviews']:>4}개  "
              + " ".join(f"{s}★{r[f'db_s{s}']}" for s in STARS) + f"  {r['product_title'][:50]}")
    return 0


# ---------------------------------------------------------------- rank (검색 순위와 매출로 후보)

RANK_EXTRA = ["brand", "search_avg_rank", "search_latest_rank", "seeds", "monthly_revenue", "monthly_units", "price_usd",
              "amazon_reviews", "amazon_rating", "parent_asin", "rank_pick", "need_paid", "source"]


def rank_candidates(run, category, max_product_calls=None):
    cat = load_yaml(ROOT / "config" / "categories" / f"{category}.yaml") or {}
    sel = cat.get("selection") or {}
    seeds = [str(x) for x in sel.get("seeds") or []]
    if not seeds:
        die(f"config/categories/{category}.yaml에 selection.seeds(순위를 볼 검색어)가 없습니다.")
    limit = int(max_product_calls or sel.get("max_product_calls", 25))
    pick_n, enough = int(sel.get("pick", 10)), int(sel.get("min_db_reviews", 100))
    raw = run / "raw" / "candidates"
    raw.mkdir(parents=True, exist_ok=True)
    t0 = time.time()
    found = {}
    for seed in seeds:
        path = raw / f"top_{safe_name(seed)}.json"
        if path.exists():          # 이미 받은 응답은 다시 부르지 않는다
            d = json.loads(path.read_text(encoding="utf-8"))
        else:
            text, d = call(MARKET_SERVER, "search_terms_trends_top_products", {"search_term": seed, "marketplace": "US"})
            path.write_text(text, encoding="utf-8")
        got = records(d)
        for r in got:
            a = str(r.get("asin") or "").strip()
            if not a:
                continue
            rk, lr = num(r.get("avgRank")), num(r.get("latestRank"))
            f = found.setdefault(a, {"title": r.get("title") or "", "brand": r.get("brandName") or "", "avg_rank": rk,
                                     "latest_rank": lr, "seeds": []})
            f["seeds"].append(seed)
            if rk is not None and (f["avg_rank"] is None or rk < f["avg_rank"]):
                f["avg_rank"], f["latest_rank"] = rk, lr
        print(f"  검색어 '{seed}': 상위 상품 {len(got)}개", flush=True)
    inc, exc = cat.get("title_include") or [], cat.get("title_exclude") or []
    log = {"made_at": now_iso(), "category": category, "seeds": seeds, "title_rule_out": [], "over_call_limit": [],
           "same_parent": [], "no_product_data": []}
    keep = []
    for a, f in found.items():
        if has_any(f["title"], inc) and not has_any(f["title"], exc):
            keep.append(a)
        else:
            log["title_rule_out"].append({"asin": a, "title": f["title"]})
    keep.sort(key=lambda a: (found[a]["avg_rank"] is None, found[a]["avg_rank"] or 0, a))
    print(f"상위 상품 {len(found)}개 중 제목 규칙에 맞는 것 {len(keep)}개", flush=True)
    if len(keep) > limit:
        log["over_call_limit"] = keep[limit:]
        print(f"  products_byasin은 평균 순위 앞쪽 {limit}개만 부릅니다(나머지 {len(keep) - limit}개는 00_candidates_log.json).")
        keep = keep[:limit]

    rows = []
    for a in keep:
        path = run / "raw" / f"product_{a}.json"
        if not path.exists():
            text, _ = call(MARKET_SERVER, "products_byasin", {"asin": a, "marketplace": "US"})
            path.write_text(text, encoding="utf-8")
        d = json.loads(path.read_text(encoding="utf-8"))
        prod = (d[0] if isinstance(d, list) and d else d) or {}
        if not isinstance(prod, dict):
            prod = {}
        if not prod.get("asin") and prod.get("monthlyRevenueEstimate") is None:
            log["no_product_data"].append(a)
        f = found[a]
        rows.append({"asin": a, "product_title": prod.get("title") or f["title"], "brand": prod.get("brandName") or f["brand"],
                     "search_avg_rank": f["avg_rank"], "search_latest_rank": f["latest_rank"], "seeds": "; ".join(f["seeds"]),
                     "monthly_revenue": num(prod.get("monthlyRevenueEstimate")), "monthly_units": num(prod.get("monthlyUnitsSold")),
                     "price_usd": num(prod.get("buyBoxPrice")), "amazon_reviews": prod.get("reviewCount"),
                     "amazon_rating": prod.get("reviewRating"), "parent_asin": prod.get("parentAsin") or ""})
    best = {}
    for r in rows:                 # 같은 부모(용량, 묶음 차이)는 매출이 큰 하나
        k = r["parent_asin"] or r["asin"]
        if k not in best or (r["monthly_revenue"] or 0) > (best[k]["monthly_revenue"] or 0):
            if k in best:
                log["same_parent"].append({"asin": best[k]["asin"], "kept": r["asin"], "parent_asin": k})
            best[k] = r
        else:
            log["same_parent"].append({"asin": r["asin"], "kept": best[k]["asin"], "parent_asin": k})
    rows = sorted(best.values(), key=lambda r: (r["monthly_revenue"] is None, -(r["monthly_revenue"] or 0), r["asin"]))

    for i, r in enumerate(rows, 1):
        a = r["asin"]
        st_text, st = call(REVIEW_SERVER, "get_review_stats", {"asin": a})
        (raw / f"stats_{a}.json").write_text(st_text, encoding="utf-8")
        one_text, one = call(REVIEW_SERVER, "search_reviews", {"asin": a, "limit": 1})
        (raw / f"one_{a}.json").write_text(one_text, encoding="utf-8")
        r1 = next((x for x in one.get("reviews") or [] if x.get("asin") == a), {})
        real = real_from_summary(r1.get("rating_summary")) or {}
        dist = st.get("rating_distribution") or {}
        dr = st.get("date_range") or {}
        n_db = st.get("total_reviews") or 0
        r.update({"db_reviews": n_db, **{f"db_s{s}": dist.get(str(s), 0) for s in STARS},
                  **{f"real_s{s}": real.get(s, "") for s in STARS},
                  "total_ratings": r1.get("total_ratings", r["amazon_reviews"] if r["amazon_reviews"] is not None else ""),
                  "average_rating": r1.get("average_rating", r["amazon_rating"] if r["amazon_rating"] is not None else ""),
                  "date_min": dr.get("earliest") or "", "date_max": dr.get("latest") or "",
                  "kind_hint": kind_hint(r["product_title"], cat.get("kind_rules")), "asin_count": st.get("asin_count"),
                  "rank_pick": i if i <= pick_n else "", "need_paid": "yes" if n_db < enough else "no", "source": "rank"})
        for k in ("search_avg_rank", "search_latest_rank", "monthly_revenue", "monthly_units", "price_usd"):
            if isinstance(r[k], float):
                r[k] = f"{r[k]:g}"
            elif r[k] is None:
                r[k] = ""
    cols = ["asin", "product_title", "db_reviews", *[f"db_s{s}" for s in STARS], *[f"real_s{s}" for s in STARS],
            "total_ratings", "average_rating", "date_min", "date_max", "kind_hint", "asin_count"] + RANK_EXTRA
    with open(run / "00_candidates.csv", "w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)
    write_json(run / "00_candidates_log.json", log)
    picked = [r for r in rows if r["rank_pick"] != ""]
    paid_n = sum(r["need_paid"] == "yes" for r in picked)
    print(f"후보 {len(rows)}개를 00_candidates.csv에 적었습니다({time.time() - t0:.0f}초). 매출 순 앞 {pick_n}개에 rank_pick, "
          f"그중 DB 리뷰 {enough}개 미만(유료 수집 대상 후보) {paid_n}개. 칸 뜻(월 매출 추정 등)은 응답 칸 이름 그대로, 단위 미확인.")
    for r in rows:
        print(f"  {str(r['rank_pick'] or '-'):>2} {r['asin']} 매출 {r['monthly_revenue'] or '-':>10} 순위 {r['search_avg_rank'] or '-':>5} "
              f"DB {r['db_reviews']:>4}개 유료 {r['need_paid']:<3} {r['kind_hint']:<11} {str(r['product_title'])[:48]}")
    return 0


# ---------------------------------------------------------------- pull

def load_raw_reviews(path):
    d = json.loads(path.read_text(encoding="utf-8"))
    return [r for p in d.get("pages", []) for r in (p.get("reviews") or [])]


def fetch_reviews(run, asin, offline):
    path = run / "raw" / f"reviews_{asin}.json"
    if offline and path.exists():
        return load_raw_reviews(path), "raw"
    pages, _ = search_all({"asin": asin})
    path.write_text(json.dumps({"_note": "search_reviews responses, unmodified, in offset order (limit 200)",
                                "asin": asin, "fetched_at": now_iso(), "pages": pages},
                               ensure_ascii=False, indent=1), encoding="utf-8")
    return load_raw_reviews(path), "db"


def fetch_product(run, asin, offline):
    path = run / "raw" / f"product_{asin}.json"
    if not (offline and path.exists()):
        text, _ = call(MARKET_SERVER, "products_byasin", {"asin": asin, "marketplace": "US"})
        path.write_text(text, encoding="utf-8")
    d = json.loads(path.read_text(encoding="utf-8"))
    return (d[0] if isinstance(d, list) and d else d) or {}


def paid_targets(run, selected, conf, explicit):
    """유료로 받을 ASIN. --paid-asins가 있으면 그것, 없으면 공유 DB 리뷰가 scrape_below_db_reviews보다 적은 selected만."""
    if explicit:
        unknown = [a for a in explicit if a not in selected]
        if unknown:
            die(f"--paid-asins에 01_asins.csv의 selected가 아닌 ASIN이 있습니다: {', '.join(unknown)}")
        return list(explicit)
    below = int(conf["paid"].get("scrape_below_db_reviews", 0) or 0)
    if below <= 0:
        return list(selected)
    targets = []
    for a in selected:
        _, st = call(REVIEW_SERVER, "get_review_stats", {"asin": a})
        n = st.get("total_reviews") or 0
        mark = "유료 대상" if n < below else "DB로 충분"
        print(f"  {a}: 공유 DB 리뷰 {n}개 → {mark}(기준 {below}개 미만)", flush=True)
        if n < below:
            targets.append(a)
    return targets


def paid_scrape(run, asins, conf, test=False):
    paid = conf["paid"]
    log = run / "raw" / "paid_calls.jsonl"
    limit = int(paid.get("max_scrape_calls", 0))
    max_asins = int(paid.get("max_asins", 10))
    pages = 1 if test else int(paid.get("max_pages_per_star", 1))
    past = [json.loads(l) for l in open(log, encoding="utf-8") if l.strip()] if log.exists() else []
    done = len(past)
    ok_pairs = {(p["asin"], tuple(p["arguments"]["ratings"]), p["arguments"].get("max_pages"))
                for p in past if p.get("collected") is not None}
    if not asins:
        print("  유료로 받을 ASIN이 없습니다.")
        return
    if len(asins) > max_asins:
        die(f"유료 수집 대상 {len(asins)}개가 paid.max_asins({max_asins}개)를 넘어 부르지 않았습니다: {', '.join(asins)}")
    if test:
        plan = [(asins[0], [STARS[0]])]
    elif paid.get("split_by_star", True):
        plan = [(a, [s]) for a in asins for s in STARS]
    else:
        plan = [(a, list(STARS)) for a in asins]
    todo = []
    for a, ratings in plan:
        if not test and (a, tuple(ratings), pages) in ok_pairs:
            print(f"  유료 수집 {a} {ratings}: 이미 받음(raw/paid_calls.jsonl), 건너뜀", flush=True)
            continue
        todo.append((a, ratings))
    over = len(todo) > limit - done          # 상한을 넘는 호출은 처음부터 부르지 않는다(동시에 불러도 상한은 그대로)
    todo = todo[:max(0, limit - done)]
    # 동시 호출 수(paid.concurrency, 기본 1). 호출 수와 비용은 같고 걸리는 시간만 준다. 동시에 부를 때는 호출마다 세션을 따로 연다
    workers = 1 if test else max(1, int(paid.get("concurrency", 1)))
    lock = threading.Lock()

    def one(job):
        a, ratings = job
        args = {"asins": [a], "ratings": ratings, "regions": ["com"], "max_pages": pages, "sort": "recent", "limit": 1}
        t = time.time()
        _, res = (call if workers == 1 else call_fresh)(REVIEW_SERVER, "scrape_reviews", args)
        sec = round(time.time() - t, 1)
        with lock:
            with open(log, "a", encoding="utf-8") as f:
                f.write(json.dumps({"ts": now_iso(), "asin": a, "arguments": args, "seconds": sec, "test": test,
                                    **{k: res.get(k) for k in ("collected", "inserted", "skipped")}},
                                   ensure_ascii=False) + "\n")
            print(f"  유료 수집 {a} {ratings}: 수집 {res.get('collected')}, 새로 저장 {res.get('inserted')}, 중복 {res.get('skipped')}, "
                  f"{sec}초", flush=True)

    # 한 호출이 실패하면 멈춘다. 이미 받은 호출은 raw/paid_calls.jsonl에 남아 다시 돌리면 건너뛴다
    with ThreadPoolExecutor(max_workers=workers) as ex:
        list(ex.map(one, todo))
    if over:
        die(f"유료 호출이 paid.max_scrape_calls({limit}번)에 닿아 멈춥니다. 남은 호출은 부르지 않았습니다.")
    if test:
        _, one = call(REVIEW_SERVER, "search_reviews", {"asin": asins[0], "ratings": [STARS[0]], "limit": 1})
        r1 = next((x for x in one.get("reviews") or [] if x.get("asin") == asins[0]), {})
        has = real_from_summary(r1.get("rating_summary")) is not None
        print(f"시험 호출 끝: {asins[0]} 1★ 1페이지. DB의 이 ASIN 리뷰에 rating_summary(실제 별점 분포)가 "
              f"{'붙어 있음' if has else '없음(02_star_distribution.csv를 만들 수 없음, 담당자 확인 필요)'}. "
              "응답에 비용 칸은 없습니다(금액은 Apify 계정에서만 보임).")


def norm_date(s):
    s = str(s or "")
    return s[:10] if re.match(r"\d{4}-\d{2}-\d{2}", s) else s


def tf(v):
    return "true" if v else "false"


def review_row(r, brand):
    specs = r.get("variant_specs") or []
    hv = r.get("helpful_vote_count")
    return {
        "review_id": r.get("review_id") or "", "asin": r["asin"], "star": str(int(float(r["rating"]))),
        "date": norm_date(r.get("review_date")),
        "title": html.unescape(r.get("title") or ""), "body": html.unescape(r.get("review_text") or ""),
        "verified": tf(r.get("verified_purchase")), "vine": tf(r.get("vine_review")),
        "helpful_votes": "" if hv is None else str(hv), "variant_asin": r.get("variant_asin") or "",
        "variant_text": "; ".join(str(x) for x in specs) if isinstance(specs, list) else str(specs),
        "brand": brand, "language": r.get("language") or "", "country": r.get("country") or "",
    }


def dist_row(asin, revs):
    """리뷰에 붙은 rating_summary(상품 페이지 별점 막대)로 02_star_distribution.csv 한 줄을 만든다."""
    combos = Counter()
    latest = {}
    for r in revs:
        real = real_from_summary(r.get("rating_summary"))
        if real is None:
            continue
        key = (tuple(real[s] for s in STARS), r.get("total_ratings"), r.get("average_rating"))
        combos[key] += 1
        stamp = r.get("scraped_at") or r.get("created_at") or ""
        if stamp > latest.get(key, ("", None))[0]:
            latest[key] = (stamp, r)
    if not combos:
        return None, f"{asin}: rating_summary가 붙은 리뷰가 없어 실제 별점 분포를 만들지 못했습니다."
    note = None
    if len(combos) > 1:
        note = f"{asin}: rating_summary 값이 {len(combos)}가지라 가장 나중에 받은 값을 씁니다."
    key = max(latest, key=lambda k: latest[k][0])
    stamp, r = latest[key]
    pcts, total, avg = key
    row = {"asin": asin, **{f"s{s}": f"{pcts[s - 1]:g}" for s in (5, 4, 3, 2, 1)},
           "total_ratings": "" if total is None else str(total), "average_rating": "" if avg is None else f"{avg:g}",
           "source": "rating_summary", "captured_at": r.get("scraped_at") or r.get("created_at") or ""}
    return row, note


def write_csv(path, cols, rows):
    with open(path, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)


def pull(run, mode, offline, confirm_paid, paid_asins=None, paid_test=False):
    conf = load_config()
    if mode == "paid":
        if not conf["paid"].get("enabled"):
            die("유료 수집이 꺼져 있습니다(config/pipeline.yaml의 paid.enabled: false). 켜려면 담당자가 직접 바꿔 주세요.")
        if not confirm_paid:
            die("유료 수집은 --confirm-paid를 함께 줘야 합니다(Apify 크레딧이 실제로 듭니다).")
        if offline:
            die("유료 수집과 --offline은 함께 쓸 수 없습니다.")
    elif paid_asins or paid_test:
        die("--paid-asins와 --paid-test는 --mode paid --confirm-paid와 함께만 씁니다.")
    errors = []
    asin_rows = read_csv(run / "01_asins.csv", ASIN_COLS, errors)
    if asin_rows is None:
        die(" ".join(errors))
    selected = [r["asin"] for r in asin_rows if r["status"] == "selected"]
    if not selected:
        die("01_asins.csv에 status가 selected인 ASIN이 없습니다.")
    (run / "raw").mkdir(exist_ok=True)
    t0 = time.time()
    if mode == "paid":
        targets = paid_targets(run, selected, conf, paid_asins)
        paid_scrape(run, targets, conf, test=paid_test)
        if paid_test:
            return 0
        offline = False

    reviews, dists, notes, stats, dropped = [], [], [], {}, []
    by_asin = {r["asin"]: r for r in asin_rows}
    for a in selected:
        revs, src = fetch_reviews(run, a, offline)
        exact = [r for r in revs if r.get("asin") == a]
        if len(exact) != len(revs):
            notes.append(f"{a}: asin 부분일치로 딸려 온 다른 ASIN 리뷰 {len(revs) - len(exact)}개를 뺐습니다.")
        # 같은 ASIN 안에서 review_id가 같은 줄은 하나만 둔다(2026-10-14: offset으로 나눠 받을 때 페이지 경계에서 같은 리뷰가 두 번 온 일이 있음)
        uniq, seen_ids = [], set()
        for r in exact:
            rid = r.get("review_id")
            if rid in seen_ids:
                dropped.append({"review_id": rid, "asin": a, "star": int(float(r.get("rating") or 0)), "reason": "같은 ASIN 안 중복(같은 리뷰가 두 번 옴)"})
                continue
            seen_ids.add(rid)
            uniq.append(r)
        exact = uniq
        product = fetch_product(run, a, offline)
        row = by_asin[a]
        filled = {"brand": product.get("brandName"), "title": product.get("title"),
                  "amazon_rating": product.get("reviewRating"), "parent_asin": product.get("parentAsin")}
        for k, v in filled.items():
            if not row.get(k) and v not in (None, ""):
                row[k] = f"{v:g}" if isinstance(v, float) else str(v)
        brand = row.get("brand") or ""
        for r in exact:
            rr = review_row(r, brand)
            if rr["body"].strip():
                reviews.append(rr)
            else:
                dropped.append({"review_id": rr["review_id"], "asin": a, "star": int(rr["star"]), "reason": "본문 없음"})
        d, note = dist_row(a, exact)
        if d:
            dists.append(d)
        if note:
            notes.append(note)
        stats[a] = (src, exact)

    ids = Counter(r["review_id"] for r in reviews)
    dup = [k for k, n in ids.items() if n > 1]
    if dup:
        notes.append(f"review_id가 겹치는 리뷰 {len(dup)}개: {', '.join(dup[:5])}")
    write_csv(run / "01_asins.csv", ASIN_COLS + ASIN_OPT, asin_rows)
    write_csv(run / "02_reviews.csv", REVIEW_COLS + REVIEW_OPT, reviews)
    write_csv(run / "02_star_distribution.csv", DIST_COLS + DIST_OPT, dists)
    write_json(run / "02_collect_log.json", {
        "collected_at": now_iso(), "mode": mode, "offline": offline, "asins": selected,
        "kept_reviews": len(reviews), "dropped_count": len(dropped), "dropped": dropped, "notes": notes})

    print(f"수집 완료({mode}{', offline' if offline else ''}): ASIN {len(selected)}개, 리뷰 {len(reviews)}개"
          f"(본문 없는 리뷰 {len(dropped)}개 뺌), {time.time() - t0:.0f}초. "
          "02_reviews.csv, 02_star_distribution.csv, 02_collect_log.json, 01_asins.csv 빈칸 채움")
    print("ASIN별(02_reviews.csv에 남은 리뷰): 리뷰 수 / 1★ 2★ 3★ 4★ 5★ / 언어(빈 값은 영어) / 받은 곳")
    for a, (src, _) in stats.items():
        kept = [r for r in reviews if r["asin"] == a]
        c = Counter(int(r["star"]) for r in kept)
        lang = Counter(r["language"] or "blank" for r in kept)
        print(f"  {a}: {len(kept):>4} / " + " ".join(f"{c[s]:>3}" for s in STARS)
              + " / " + ", ".join(f"{k} {n}" for k, n in lang.most_common()) + f" / {src}")
    for d in dropped:
        print(f"  뺀 리뷰: {d['review_id']} ({d['asin']}, {d['star']}★, {d['reason']})")
    total_lang = Counter(r["language"] or "blank" for r in reviews)
    print("언어 합계: " + ", ".join(f"{k} {n}" for k, n in total_lang.most_common()))
    for n in notes:
        print(f"  주의: {n}")
    return 0


# ---------------------------------------------------------------- prices

def size_oz(v):
    """변형 하나의 용량(fl oz). unitType이 Fl Oz일 때 unitValue, 아니면 size 문자열에서 읽는다."""
    if str(v.get("unitType") or "").lower().startswith("fl") and v.get("unitValue"):
        return float(v["unitValue"])
    m = re.search(r"([\d.]+)\s*Fl\s*Oz", str(v.get("size") or ""), re.I)
    return float(m.group(1)) if m else None


def price_band(variants):
    """변형 목록에서 '최저~최고달러(용량 범위)' 문자열을 만든다."""
    prices = [float(v["buyBoxPrice"]) for v in variants if v.get("buyBoxPrice")]
    sizes = [x for x in (size_oz(v) for v in variants) if x]
    if not prices:
        return ""
    p = f"{min(prices):.2f}달러" if min(prices) == max(prices) else f"{min(prices):.2f}~{max(prices):.2f}달러"
    if sizes:
        z = f"{min(sizes):g} fl oz" if min(sizes) == max(sizes) else f"{min(sizes):g}~{max(sizes):g} fl oz"
        p += f"({z})"
    return p


def prices(run, offline):
    """01_asins.csv의 selected ASIN마다 부모 ASIN의 변형(spd-amz-market products_variations)을 받아
    price_band(변형 가격 범위와 용량 범위)와 price_usd(이 ASIN의 바이박스 가격)를 채운다. 결과 기록은 01_prices.json."""
    errors = []
    asin_rows = read_csv(run / "01_asins.csv", ASIN_COLS, errors)
    if asin_rows is None:
        die(" ".join(errors))
    (run / "raw").mkdir(exist_ok=True)
    out = {"checked_on": now_iso()[:10], "source": "spd-amz-market products_variations (marketplace US)", "asins": {}}
    for row in asin_rows:
        if row["status"] != "selected":
            continue
        a, parent = row["asin"], row.get("parent_asin") or row["asin"]
        path = run / "raw" / f"variations_{parent}.json"
        if not (offline and path.exists()):
            text, _ = call(MARKET_SERVER, "products_variations", {"asin": parent, "marketplace": "US"})
            path.write_text(text, encoding="utf-8")
        variants = json.loads(path.read_text(encoding="utf-8")) or []
        if not any(v.get("asin") == a for v in variants):
            product = fetch_product(run, a, True)
            variants = variants + ([product] if product else [])
        own = next((v for v in variants if v.get("asin") == a), {})
        row["price_band"] = price_band(variants)
        if own.get("buyBoxPrice"):
            row["price_usd"] = f"{float(own['buyBoxPrice']):.2f}"
        out["asins"][a] = {"parent_asin": parent, "price_band": row["price_band"], "price_usd": row.get("price_usd", ""),
                           "variants": [{"asin": v.get("asin"), "size": v.get("size"), "buyBoxPrice": v.get("buyBoxPrice")}
                                        for v in variants]}
        print(f"  {a}: {row['price_band'] or '가격 없음'} (이 ASIN {row.get('price_usd') or '-'}달러, 변형 {len(variants)}개)")
    write_csv(run / "01_asins.csv", ASIN_COLS + ASIN_OPT, asin_rows)
    write_json(run / "01_prices.json", out)
    print(f"가격대를 01_asins.csv와 01_prices.json에 적었습니다({out['checked_on']} 조회).")
    return 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("action", choices=["candidates", "rank", "pull", "prices"])
    ap.add_argument("run")
    ap.add_argument("--category", default="perfume")
    ap.add_argument("--mode", choices=["db", "paid"], default="db")
    ap.add_argument("--offline", action="store_true", help="raw 파일이 있으면 다시 받지 않는다")
    ap.add_argument("--confirm-paid", action="store_true", help="유료 수집을 실제로 부른다는 확인")
    ap.add_argument("--paid-asins", default="", help="유료로 받을 ASIN(쉼표). 없으면 DB 리뷰가 적은 selected만")
    ap.add_argument("--paid-test", action="store_true", help="유료 시험 호출 한 번(ASIN 하나, 1★, 1페이지)만 하고 끝냄")
    ap.add_argument("--max-product-calls", type=int, default=None, help="rank: products_byasin 호출 상한")
    args = ap.parse_args()
    if args.action == "candidates":
        sys.exit(candidates(run_dir(args.run, create=True), args.category))
    if args.action == "rank":
        sys.exit(rank_candidates(run_dir(args.run, create=True), args.category, args.max_product_calls))
    if args.action == "prices":
        sys.exit(prices(run_dir(args.run), args.offline))
    paid_asins = [a.strip() for a in args.paid_asins.split(",") if a.strip()]
    sys.exit(pull(run_dir(args.run), args.mode, args.offline, args.confirm_paid, paid_asins, args.paid_test))


if __name__ == "__main__":
    main()
