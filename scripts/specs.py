"""상품 사양(브랜드 사이트, 소매점 상품 페이지) 준비와 확인. 모델을 부르지 않는다.

사용:
  python scripts/specs.py prep [회차]
    선택된 ASIN마다 아마존 상품 정보(raw/product_<ASIN>.json: 브랜드, 상품명, 용량)와 모을 항목
    (config/categories/<카테고리>.yaml의 specs.items)을 23_spec_input.json에 쓴다. product-spec-collector가 읽는다.
  python scripts/specs.py check [회차]
    23_specs.yaml의 값마다 url을 다시 열어(amazon 주소는 열지 않음) 페이지 글자에 quote가 있는지, 값(목록이면 원소마다)이
    quote 안에 있는지, 항목이 목록 안에 있는지, source_type과 match가 정한 값인지 본다(research.py와 같은 글자 맞추기).
    결과: 23_specs_check.json(값마다 상태와 이유, 상품별 확인과 버림 수), 23_specs_verified.json(확인된 값만, 가이드가 쓰는 파일).
"""
import argparse
import json
import sys
import urllib.error
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from pipeline_io import ASIN_COLS, ROOT, die, load_csv_or_die, load_yaml, now_iso, resolve_run, write_json  # noqa: E402
from research import BLOCKED_HOSTS, found, norm, page_text  # noqa: E402

for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass

MATCH = ("일치 확인", "이름만 일치", "찾지 못함")
SOURCE = ("official", "retailer", "community")


def conf(run):
    cat = run.name.split("-")[0]
    c = (load_yaml(ROOT / "config" / "categories" / f"{cat}.yaml") or {}).get("specs")
    if not c:
        die(f"config/categories/{cat}.yaml에 specs 절이 없습니다.")
    return c


def product(run, asin):
    p = run / "raw" / f"product_{asin}.json"
    if not p.exists():
        return {}
    d = json.loads(p.read_text(encoding="utf-8"))
    x = d[0] if isinstance(d, list) and d else d
    if isinstance(x, dict) and "data" in x:
        x = x["data"]
    if isinstance(x, list):
        x = x[0] if x else {}
    return x if isinstance(x, dict) else {}


def prep(run):
    c = conf(run)
    asins = [r for r in load_csv_or_die(run / "01_asins.csv", ASIN_COLS) if r["status"] == "selected"]
    out = []
    for a in asins:
        p = product(run, a["asin"])
        out.append({"asin": a["asin"], "brand": p.get("brandName") or a.get("brand"), "amazon_title": p.get("title") or a.get("title"),
                    "size": p.get("size"), "unit_value": p.get("unitValue"), "unit_type": p.get("unitType")})
    write_json(run / "23_spec_input.json", {"made_at": now_iso(), "run": run.name, "products": out,
                                            "items": [{k: i.get(k) for k in ("id", "name_ko", "ask", "format")} for i in c["items"]]})
    print(f"상품 {len(out)}개, 항목 {len(c['items'])}개 → 23_spec_input.json")
    return 0


def values_in_quote(value, quote):
    q = norm(quote)
    vals = value if isinstance(value, list) else [value]
    miss = [str(v) for v in vals if norm(v) and norm(v) not in q]
    return not miss and bool(vals), miss


def check(run):
    c = conf(run)
    items = {i["id"]: i for i in c["items"]}
    data = (load_yaml(run / "23_specs.yaml") or {}).get("specs") or {}
    prods = data.get("products") or []
    if not prods:
        die("23_specs.yaml에 products가 없습니다.")
    cache, rows, verified, per = {}, [], {}, {}
    for p in prods:
        asin = p.get("asin")
        match = p.get("match")
        per[asin] = Counter()
        verified[asin] = {"match": match, "match_reason": p.get("match_reason"), "amazon_title": p.get("amazon_title"),
                          "missing": p.get("missing") or [], "values": {}}
        if match not in MATCH:
            rows.append({"asin": asin, "item": "-", "status": "error", "reason": f"match 값이 목록 밖: {match}"})
        for v in p.get("values") or []:
            row = {"asin": asin, "item": v.get("item"), "url": v.get("url"), "source_type": v.get("source_type")}
            url = str(v.get("url") or "")
            reason = None
            if v.get("item") not in items:
                reason = "항목이 목록 밖"
            elif v.get("source_type") not in SOURCE:
                reason = "source_type이 목록 밖"
            elif not url.startswith("http"):
                reason = "url 없음"
            elif any(h in url.lower() for h in BLOCKED_HOSTS):
                reason = "amazon 주소라 쓰지 않음"
            else:
                ok, miss = values_in_quote(v.get("value"), v.get("quote") or "")
                if not ok:
                    reason = f"값이 quote 안에 없음: {miss[:3]}"
                else:
                    if url not in cache:
                        try:
                            cache[url] = page_text(url)
                        except urllib.error.HTTPError as e:
                            cache[url] = (None, f"HTTP {e.code}")
                        except Exception as e:  # noqa: BLE001
                            cache[url] = (None, f"열지 못함 {type(e).__name__}")
                    text, err = cache[url]
                    if text is None:
                        reason = err
                    elif not found(v.get("quote") or "", text):
                        reason = "페이지에 원문 문장이 없음"
            row["status"] = "verified" if reason is None else "dropped"
            if reason:
                row["reason"] = reason
            rows.append(row)
            per[asin][row["status"]] += 1
            if reason is None:
                verified[asin]["values"].setdefault(v["item"], []).append(
                    {"value": v["value"], "url": url, "source_type": v["source_type"], "quote": v.get("quote")})
    st = {a: {"verified": n["verified"], "dropped": n["dropped"]} for a, n in per.items()}
    status = "FAIL" if any(r["status"] == "error" for r in rows) else "PASS"
    write_json(run / "23_specs_check.json", {"checked_at": now_iso(), "status": status, "by_asin": st,
                                             "verified": sum(n["verified"] for n in per.values()),
                                             "dropped": sum(n["dropped"] for n in per.values()), "items": rows})
    write_json(run / "23_specs_verified.json", {"checked_at": now_iso(), "products": verified,
                                                "items": [{k: i.get(k) for k in ("id", "name_ko", "format")} for i in c["items"]]})
    print(f"상품 사양 확인: {status}  (확인 {sum(n['verified'] for n in per.values())}개, 버림 {sum(n['dropped'] for n in per.values())}개)")
    for a, n in st.items():
        vv = verified[a]
        print(f"  {a}: {vv['match']}, 확인 {n['verified']}개, 버림 {n['dropped']}개, 확인된 항목 {sorted(vv['values'])}")
    for r in rows:
        if r["status"] != "verified":
            print(f"  버림: {r['asin']} {r['item']} {r.get('reason')} {str(r.get('url'))[:80]}")
    return 1 if status == "FAIL" else 0


def main():
    ap = argparse.ArgumentParser(description="상품 사양 준비와 확인")
    ap.add_argument("mode", choices=["prep", "check"])
    ap.add_argument("run", nargs="?")
    a = ap.parse_args()
    run = resolve_run(a.run)
    sys.exit(prep(run) if a.mode == "prep" else check(run))


if __name__ == "__main__":
    main()
