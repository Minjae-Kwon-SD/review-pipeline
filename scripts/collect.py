"""0단계: 리뷰 수집(공유 리뷰 DB에서 받기, 유료 수집은 설정으로 막아 둠).

사용: python scripts/collect.py candidates <회차> --category perfume
  공유 DB에서 카테고리 키워드로 리뷰를 검색해 서로 다른 ASIN을 모으고, 상품 제목 규칙
  (config/categories/<카테고리>.yaml의 title_include, title_exclude)으로 거른다.
  후보마다 get_review_stats(asin 전체 값)와 search_reviews(asin, limit 1)의 rating_summary를 받는다.
  결과: 00_candidates.csv(DB 리뷰 수 많은 순), 원문 응답은 raw/candidates/.

사용: python scripts/collect.py pull <회차> [--mode db|paid] [--offline] [--confirm-paid]
  01_asins.csv에서 status가 selected인 ASIN만 받는다.
  db 모드: search_reviews(asin 전체 값, limit 200, offset 끝까지). asin은 부분일치(ILIKE)라
    응답의 asin이 정확히 같은 행만 남긴다. 원문은 raw/reviews_<ASIN>.json.
    --offline이면 raw 파일이 있는 ASIN은 다시 받지 않고 그 파일로 변환만 한다.
  products_byasin(marketplace US)으로 brandName, parentAsin, title, reviewRating을 받아 raw/product_<ASIN>.json에
    저장하고 01_asins.csv의 brand, title, amazon_rating, parent_asin 빈칸을 채운다(값이 있으면 그대로).
  paid 모드: config/pipeline.yaml의 paid.enabled가 true이고 --confirm-paid가 있을 때만 ASIN마다
    scrape_reviews(별점 1~5, regions com, sort recent)를 먼저 부르고 db 모드처럼 받는다.
    호출마다 raw/paid_calls.jsonl에 적고, paid.max_scrape_calls를 넘으면 멈춘다.
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
import time
from collections import Counter
from pathlib import Path

from mcp_http import MCPError, call_tool
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


def paid_scrape(run, asins, conf):
    paid = conf["paid"]
    log = run / "raw" / "paid_calls.jsonl"
    limit = int(paid.get("max_scrape_calls", 0))
    done = sum(1 for _ in open(log, encoding="utf-8")) if log.exists() else 0
    for a in asins:
        if done >= limit:
            die(f"유료 호출이 paid.max_scrape_calls({limit}번)에 닿아 멈춥니다. 남은 ASIN은 수집하지 않았습니다.")
        args = {"asins": [a], "ratings": list(STARS), "regions": ["com"],
                "max_pages": int(paid.get("max_pages_per_star", 1)), "sort": "recent", "limit": 1}
        _, res = call(REVIEW_SERVER, "scrape_reviews", args)
        done += 1
        with open(log, "a", encoding="utf-8") as f:
            f.write(json.dumps({"ts": now_iso(), "asin": a, "arguments": args,
                                **{k: res.get(k) for k in ("collected", "inserted", "skipped")}},
                               ensure_ascii=False) + "\n")
        print(f"  유료 수집 {a}: 수집 {res.get('collected')}, 새로 저장 {res.get('inserted')}, 중복 {res.get('skipped')}",
              flush=True)


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


def pull(run, mode, offline, confirm_paid):
    conf = load_config()
    if mode == "paid":
        if not conf["paid"].get("enabled"):
            die("유료 수집이 꺼져 있습니다(config/pipeline.yaml의 paid.enabled: false). 켜려면 담당자가 직접 바꿔 주세요.")
        if not confirm_paid:
            die("유료 수집은 --confirm-paid를 함께 줘야 합니다(Apify 크레딧이 실제로 듭니다).")
        if offline:
            die("유료 수집과 --offline은 함께 쓸 수 없습니다.")
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
        paid_scrape(run, selected, conf)
        offline = False

    reviews, dists, notes, stats, dropped = [], [], [], {}, []
    by_asin = {r["asin"]: r for r in asin_rows}
    for a in selected:
        revs, src = fetch_reviews(run, a, offline)
        exact = [r for r in revs if r.get("asin") == a]
        if len(exact) != len(revs):
            notes.append(f"{a}: asin 부분일치로 딸려 온 다른 ASIN 리뷰 {len(revs) - len(exact)}개를 뺐습니다.")
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
    ap.add_argument("action", choices=["candidates", "pull", "prices"])
    ap.add_argument("run")
    ap.add_argument("--category", default="perfume")
    ap.add_argument("--mode", choices=["db", "paid"], default="db")
    ap.add_argument("--offline", action="store_true", help="raw 파일이 있으면 다시 받지 않는다")
    ap.add_argument("--confirm-paid", action="store_true", help="유료 수집을 실제로 부른다는 확인")
    args = ap.parse_args()
    if args.action == "candidates":
        sys.exit(candidates(run_dir(args.run, create=True), args.category))
    if args.action == "prices":
        sys.exit(prices(run_dir(args.run), args.offline))
    sys.exit(pull(run_dir(args.run), args.mode, args.offline, args.confirm_paid))


if __name__ == "__main__":
    main()
