"""웹 조사 주장 확인(15_research.yaml). 모델을 부르지 않는다.

사용:
  python scripts/research.py check [회차]
    주장마다 url을 다시 열어(amazon 주소는 열지 않고 뺌) 페이지 글자에 원문 문장(quote)이 있는지 본다.
    대소문자, 공백, 따옴표 모양, 문장부호 차이는 무시한다. 있으면 verified, 없거나 열지 못하면 unverified(이유와 함께).
    결과: 15_research_check.json(주장마다 상태, 분야별 확인 수). 가이드는 verified인 주장만 쓴다.
    열기에 잠깐 실패하면(HTTP 429, 5xx, 시간 초과) 2, 4, 8, 16초 쉬며 4번까지 다시 연다. 원문 문장을 찾은 페이지 글자는
    research_cache/<주소 해시>.json에 남긴다(열어 본 때 포함). 다음 확인에서 잠깐 실패로 열지 못하면 남긴 글자로 확인하고
    source를 cache(열어 본 때)로 적는다. 남긴 글자가 없으면 회차 안의 이전 확인 기록(15_research_check*.json)에서 그 주장이
    live로 확인된 가장 최근 기록을 찾아 source를 previous_check(확인한 때)로 적는다. 페이지가 없어졌거나(404) 원문 문장이 사라졌으면 unverified다.
"""
import argparse
import html
import json
import re
import sys
import urllib.error
import urllib.request
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from pipeline_io import load_yaml, now_iso, resolve_run, write_json  # noqa: E402

for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36"
BLOCKED_HOSTS = ("amazon.",)


def norm(s):
    s = html.unescape(str(s)).lower()
    s = s.replace("’", "'").replace("‘", "'").replace("“", '"').replace("”", '"').replace("–", "-").replace("—", "-")
    s = re.sub(r"[^0-9a-z가-힣%$.]+", " ", s)
    return re.sub(r"\s+", " ", s).strip()


def page_text(url, timeout=30):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "text/html,application/xhtml+xml,application/pdf;q=0.9,*/*;q=0.8",
                                               "Accept-Language": "en-US,en;q=0.9"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        raw = r.read()
        ctype = r.headers.get("Content-Type", "")
    if "pdf" in ctype.lower():
        return None, "PDF라 글자를 읽지 못함"
    text = raw.decode("utf-8", errors="replace")
    text = re.sub(r"<(script|style|noscript)[^>]*>.*?</\1>", " ", text, flags=re.S | re.I)
    text = re.sub(r"<[^>]+>", " ", text)
    return text, None


def found(quote, text):
    q, t = norm(quote), norm(re.sub(r"<[^>]+>", " ", text))
    if not q:
        return False
    if q in t:
        return True
    words = q.split()
    if len(words) >= 8:                      # 긴 문장은 앞 절반과 뒤 절반이 모두 있으면 인정(페이지가 줄을 나눈 경우)
        h = len(words) // 2
        return " ".join(words[:h]) in t and " ".join(words[h:]) in t
    return False


TRANSIENT = (429, 500, 502, 503, 504)


def fetch(url):
    """(글자, 오류, 잠깐 실패 여부). 잠깐 실패는 쉬었다가 4번까지 다시."""
    import time
    err = None
    for k, wait in enumerate((0, 2, 4, 8, 16)):
        if wait:
            time.sleep(wait)
        try:
            text, e = page_text(url)
            return text, e, False
        except urllib.error.HTTPError as e:
            err = f"HTTP {e.code}"
            if e.code not in TRANSIENT:
                return None, err, False
            ra = e.headers.get("Retry-After") if e.headers else None
            if ra and ra.isdigit() and int(ra) <= 30:
                time.sleep(int(ra))
        except Exception as e:  # noqa: BLE001
            err = f"열지 못함 {type(e).__name__}"
    return None, err, True


def cache_path(run, url):
    import hashlib
    return run / "research_cache" / (hashlib.sha1(url.encode("utf-8")).hexdigest()[:16] + ".json")


def previous_verified(run):
    """주장 id -> 이전 확인 기록에서 열어서 확인한(live 또는 source 없음) 가장 최근 때"""
    import glob
    best = {}
    for f in glob.glob(str(run / "15_research_check*.json")):
        try:
            d = json.loads(Path(f).read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue
        for x in d.get("items") or []:
            if x.get("status") == "verified" and x.get("source", "live") == "live":
                t = d.get("checked_at", "")
                if t > best.get(x["id"], ("", ""))[0]:
                    best[x["id"]] = (t, x.get("url"))
    return best


def check(run):
    prev = previous_verified(run)
    data = load_yaml(run / "15_research.yaml") or {}
    claims = data.get("claims") or []
    cache, out = {}, []
    for c in claims:
        url = str(c.get("url") or "")
        row = {"id": c.get("id"), "area": c.get("area"), "url": url}
        if not url.startswith("http"):
            row.update(status="unverified", reason="url 없음")
        elif any(h in url.lower() for h in BLOCKED_HOSTS):
            row.update(status="unverified", reason="amazon 주소라 열지 않음")
        else:
            if url not in cache:
                cache[url] = fetch(url)
            text, err, transient = cache[url]
            cp = cache_path(run, url)
            if text is None and transient and cp.exists():
                snap = json.loads(cp.read_text(encoding="utf-8"))
                if found(c.get("quote", ""), snap["text"]):
                    row.update(status="verified", source=f"cache({snap['fetched_at']})", reason=f"이번에 열지 못함({err}), 남긴 글자로 확인")
                else:
                    row.update(status="unverified", reason=err)
            elif text is None and transient and prev.get(row["id"], ("", None))[1] == url:
                row.update(status="verified", source=f"previous_check({prev[row['id']][0]})", reason=f"이번에 열지 못함({err}), 이전 확인 기록")
            elif text is None:
                row.update(status="unverified", reason=err)
            elif found(c.get("quote", ""), text):
                row.update(status="verified", source="live")
                cp.parent.mkdir(exist_ok=True)
                cp.write_text(json.dumps({"url": url, "fetched_at": now_iso(), "text": re.sub(r"\s+", " ", text)}, ensure_ascii=False),
                              encoding="utf-8")
            else:
                row.update(status="unverified", reason="페이지에 원문 문장이 없음")
        out.append(row)
    by = Counter((r["area"], r["status"]) for r in out)
    areas = sorted({r["area"] for r in out})
    res = {"checked_at": now_iso(), "claims": len(out), "verified": sum(r["status"] == "verified" for r in out),
           "verified_from_cache": sum(1 for r in out if str(r.get("source", "")).startswith("cache")),
           "verified_from_previous_check": sum(1 for r in out if str(r.get("source", "")).startswith("previous_check")),
           "by_area": {a: {"verified": by[(a, "verified")], "unverified": by[(a, "unverified")]} for a in areas}, "items": out}
    write_json(run / "15_research_check.json", res)
    print(f"웹 조사 확인: 주장 {len(out)}개 중 확인 {res['verified']}개, 빠짐 {len(out) - res['verified']}개 → 15_research_check.json")
    for a in areas:
        print(f"  {a}: 확인 {by[(a, 'verified')]}개, 빠짐 {by[(a, 'unverified')]}개")
    return 0


def main():
    ap = argparse.ArgumentParser(description="웹 조사 주장 확인")
    ap.add_argument("mode", choices=["check"])
    ap.add_argument("run", nargs="?")
    args = ap.parse_args()
    sys.exit(check(resolve_run(args.run)))


if __name__ == "__main__":
    main()
