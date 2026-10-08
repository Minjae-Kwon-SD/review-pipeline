"""무료 시장 데이터(spd-amz-market)를 받아 개발 가이드용 표를 만든다. 모델을 부르지 않는다.

사용:
  python scripts/market.py fetch [회차] [--max-calls 40]
    spd-amz-market만 부른다(amz-review, 유료 수집은 부르지 않음). 응답 원문은 market/raw/<도구>_<입력>.json에 저장하고,
    이미 저장된 파일이 있으면 다시 부르지 않는다(다시 돌려도 호출이 늘지 않음). 오류는 한 번만 다시 부르고 기록한 뒤 넘어간다.
    호출 기록: market/calls.jsonl(도구, 입력, 성공 여부, 행 수, 파일). 회차의 raw/에 이미 받은 products_byasin,
    products_variations 응답은 다시 부르지 않고 market/raw/로 복사해 쓴다(같은 날 받은 응답).
  python scripts/market.py fetch-trends [회차] --months 24 --seeds "perfume,cologne" [--max-calls 20]
    search_terms_trends를 씨앗 검색어마다 한 번(months 기간) 부른다. 응답에는 씨앗과 관련 검색어 100개 안팎의 주간 이력이 들어 있어,
    머리 숫자의 성장 배수(최근 4주 ÷ 1년 전 같은 4주)를 계산할 이력을 모은다. 파일은 search_terms_trends_<씨앗>_m<months>.json.
    --max-calls는 이 명령에서 새로 부르는 호출 수의 한도(calls.jsonl의 이 명령 기록 기준).
  python scripts/market.py build [회차]
    market/raw/의 응답으로 market/market.json(표의 숫자와 행마다 원본 파일)과 market/market_summary.md를 만든다.
    칸의 뜻이나 단위가 문서에 없으면 "단위 미확인"으로 적고 추측하지 않는다.
"""
import argparse
import json
import re
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from mcp_http import MCPError, call_tool  # noqa: E402
from pipeline_io import ASIN_COLS, load_csv_or_die, now_iso, resolve_run, write_json  # noqa: E402

for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass

SERVER = "spd-amz-market"
MP = "US"
# 첫 검색어, 노드, 카테고리 낱말은 config/categories/<카테고리>.yaml의 market 절(market_build.use_conf)


def safe(s):
    return re.sub(r"[^0-9A-Za-z가-힣]+", "_", str(s)).strip("_")[:60]


class Fetcher:
    def __init__(self, run, max_calls):
        self.dir = run / "market" / "raw"
        self.dir.mkdir(parents=True, exist_ok=True)
        self.log = run / "market" / "calls.jsonl"
        self.max = max_calls
        self.calls = sum(1 for l in self.log.read_text(encoding="utf-8").splitlines() if '"called": true' in l) if self.log.exists() else 0

    def record(self, row):
        with self.log.open("a", encoding="utf-8") as f:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")

    def get(self, tool, args, key):
        path = self.dir / f"{tool}_{safe(key)}.json"
        if path.exists():
            return json.loads(path.read_text(encoding="utf-8"))
        if self.calls >= self.max:
            print(f"  호출 한도 {self.max}번에 닿아 부르지 않음: {tool} {key}")
            self.record({"at": now_iso(), "tool": tool, "args": args, "called": False, "ok": False, "error": "호출 한도"})
            return None
        err = None
        for attempt in (1, 2):
            self.calls += 1
            try:
                text, data = call_tool(SERVER, tool, {**args, "marketplace": MP})
                path.write_text(text, encoding="utf-8")
                n = rows(data)
                self.record({"at": now_iso(), "tool": tool, "args": args, "called": True, "ok": True, "attempt": attempt,
                             "rows": n, "file": str(path.relative_to(self.dir.parent.parent))})
                print(f"  {tool} {key}: 성공, 행 {n}")
                return data
            except MCPError as e:
                err = str(e)[:300]
                self.record({"at": now_iso(), "tool": tool, "args": args, "called": True, "ok": False, "attempt": attempt, "error": err})
                print(f"  {tool} {key}: 실패({attempt}번째) {err[:120]}")
        return None


def rows(data):
    """응답의 행 수: 목록이면 길이, 사전이면 그 안의 가장 긴 목록 길이."""
    if isinstance(data, list):
        return len(data)
    if isinstance(data, dict):
        ls = [len(v) for v in data.values() if isinstance(v, list)]
        return max(ls) if ls else 1
    return 0


def records(data):
    """응답에서 행(사전) 목록을 꺼낸다."""
    if isinstance(data, list):
        return [x for x in data if isinstance(x, dict)]
    if isinstance(data, dict):
        best = [v for v in data.values() if isinstance(v, list) and v and isinstance(v[0], dict)]
        if best:
            return max(best, key=len)
        return [data]
    return []


def our_asins(run):
    return [r for r in load_csv_or_die(run / "01_asins.csv", ASIN_COLS) if r["status"] == "selected"]


def fetch(run, max_calls):
    from market_build import use_conf
    c = use_conf(run)
    NODES, SEED = tuple(c["nodes"].values()), c["seed"]
    f = Fetcher(run, max_calls)
    asins = our_asins(run)
    # 1. 우리 상품과 변형(하위 카테고리): 회차 raw/에 이미 받은 응답을 복사해 쓴다
    for a in asins:
        for src, tool, key in ((run / "raw" / f"product_{a['asin']}.json", "products_byasin", a["asin"]),
                               (run / "raw" / f"variations_{a.get('parent_asin')}.json", "products_variations", a.get("parent_asin"))):
            dst = f.dir / f"{tool}_{safe(key)}.json"
            if src.exists() and not dst.exists():
                shutil.copy(src, dst)
                f.record({"at": now_iso(), "tool": tool, "args": {"asin": key}, "called": False, "ok": True,
                          "reused_from": str(src.relative_to(run)), "file": str(dst.relative_to(run))})
            elif not dst.exists():
                f.get(tool, {"asin": key}, key)
    # 2. 하위 카테고리 목록(한 번)
    f.get("subcategories_search", {}, "all")
    # 3. EDP, EDT 노드: 경쟁 브랜드, 관련 검색어
    # 노드 이름만("Eau de Parfum")으로 부르면 다른 카테고리(전자제품) 결과가 와서, 하위 카테고리 목록의 subcategoryContextName으로 부른다
    for node in NODES:
        d = f.get("subcategories_category_competitors", {"sub_category_name": node, "start_row": 0, "end_row": 20}, node)
        if d is None or not records(d):
            f.get("subcategories_brand_category_performance", {"brand_name": node}, node)
        f.get("subcategories_relevant_search_terms", {"subcategory_name": node}, node)
    # 4. 우리 상품 가격과 순위 이력
    for a in asins:
        f.get("products_history", {"asin": a["asin"]}, a["asin"])
    # 5. 광고와 상위 상품
    f.get("search_terms_advertised_brands", {"search_term": SEED, "start_row": 0, "end_row": 20}, SEED)
    f.get("search_terms_trends_top_products", {"search_term": SEED}, SEED)
    f.get("search_terms_ad_spy", {"brand_name": asins[0]["brand"], "start_row": 0, "end_row": 20}, asins[0]["brand"])
    # 6. 검색어 추이: 관련 검색어 검색량 상위 10개 + SEED
    terms = top_terms(f.dir, 10, NODES, tuple(str(w).lower() for w in c.get("term_words") or ()))
    for t in [SEED] + [t for t in terms if t.lower() != SEED]:
        f.get("search_terms_trends", {"keyword": t, "months": 12}, t)
    print(f"호출 {f.calls}번(한도 {max_calls}). 기록: market/calls.jsonl")
    return 0


VOLUME_KEYS = ("volume30Day", "searchVolume", "search_volume", "volume", "monthlySearchVolume", "currentVolume", "searchVolumeLatest")
TERM_KEYS = ("searchTerm", "search_term", "searchTermValue", "keyword", "term", "name")


def pick(d, keys):
    for k in keys:
        if k in d and d[k] not in (None, ""):
            return d[k]
    return None


def top_terms(raw_dir, n, nodes, words):
    """관련 검색어 중 향수 낱말이나 브랜드 이름이 든 것(market_build.term_rule)을 검색량 순으로 n개.
    응답의 relevancy만으로 고르면 "now", "yellowstone" 같은 검색어가 섞여 이 규칙을 쓴다."""
    from market_build import term_rule
    brands = set()
    for p in [raw_dir / f"subcategories_category_competitors_{safe(x)}.json" for x in nodes if (raw_dir / f"subcategories_category_competitors_{safe(x)}.json").exists()]:
        brands |= {r.get("brandName") for r in records(json.loads(p.read_text(encoding="utf-8"))) if r.get("brandName")}
    out = []
    for p in [raw_dir / f"subcategories_relevant_search_terms_{safe(x)}.json" for x in nodes if (raw_dir / f"subcategories_relevant_search_terms_{safe(x)}.json").exists()]:
        for r in records(json.loads(p.read_text(encoding="utf-8"))):
            t, v = pick(r, TERM_KEYS), pick(r, VOLUME_KEYS)
            if t is not None and isinstance(v, (int, float)) and term_rule(str(t), brands, words):
                out.append((v, str(t)))
    seen, res = set(), []
    for v, t in sorted(out, reverse=True):
        if t.lower() not in seen:
            seen.add(t.lower())
            res.append(t)
    return res[:n]


def fetch_trends(run, months, seeds, max_calls):
    f = Fetcher(run, 10 ** 6)
    start = f.calls
    for sd in seeds:
        if f.calls - start >= max_calls:
            print(f"  이 명령의 호출 한도 {max_calls}번에 닿아 멈춤")
            break
        f.get("search_terms_trends", {"keyword": sd, "months": months}, f"{sd}_m{months}")
    print(f"새 호출 {f.calls - start}번(한도 {max_calls})")
    return 0


def main():
    ap = argparse.ArgumentParser(description="무료 시장 데이터 받기와 표 만들기")
    ap.add_argument("mode", choices=["fetch", "build", "fetch-trends"])
    ap.add_argument("--months", type=int, default=24)
    ap.add_argument("--seeds", default="")
    ap.add_argument("run", nargs="?")
    ap.add_argument("--max-calls", type=int, default=40)
    args = ap.parse_args()
    run = resolve_run(args.run)
    if args.mode == "fetch":
        sys.exit(fetch(run, args.max_calls))
    if args.mode == "fetch-trends":
        sys.exit(fetch_trends(run, args.months, [x.strip() for x in args.seeds.split(",") if x.strip()], args.max_calls))
    import market_build
    sys.exit(market_build.build(run))


if __name__ == "__main__":
    main()
