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
  python scripts/research.py followup-plan [회차] [--max 15]
    보충 조사(2026-10-20 담당자 결정) 입력: 15_research.yaml의 not_found와 15_research_check.json에서 verified가 아닌 주장을
    15_research_followup_input.json에 모은다(kind: not_found 또는 unverified). 0개면 보충 조사를 하지 않는다.
    대상은 max개까지(찾지 못한 것 먼저, 2026-10-20 담당자 결정: 보충이 가이드를 늦추지 않게). 남은 것은 skipped 개수로 적는다.
  python scripts/research.py merge [회차]
    보충 조사 결과(15_research_followup.yaml, id는 fu_로 시작)를 합친다. 처음 한 번 15_research.yaml을 15_research_first.yaml로 남기고,
    언제나 첫 조사(15_research_first.yaml) + 보충 주장으로 15_research.yaml을 다시 쓴다. not_found는 보충 조사의 것으로 바꾼다.
    id가 fu_로 시작하지 않거나 첫 조사 id와 겹치면 합치지 않고 종료 코드 1. 합친 뒤 check를 다시 돌린다.
"""
import argparse
import html
import json
import re
import shutil
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
    if "pdf" in ctype.lower() or raw[:5] == b"%PDF-":
        return pdf_text(raw)
    text = raw.decode("utf-8", errors="replace")
    text = re.sub(r"<(script|style|noscript)[^>]*>.*?</\1>", " ", text, flags=re.S | re.I)
    text = re.sub(r"<[^>]+>", " ", text)
    return text, None


def pdf_text(raw):
    """PDF 글자(2026-10-20). pypdf가 있으면 쪽마다 글자를 뽑는다. 없거나 글자가 없으면(그림만 있는 PDF) 읽지 못함."""
    try:
        import io
        import logging
        from pypdf import PdfReader
        logging.getLogger("pypdf").setLevel(logging.ERROR)   # 글꼴 경고(fontTools 없음)는 글자 뽑기와 무관
    except ImportError:
        return None, "PDF라 글자를 읽지 못함(pypdf 없음)"
    try:
        text = "\n".join((pg.extract_text() or "") for pg in PdfReader(io.BytesIO(raw)).pages)
    except Exception as e:  # noqa: BLE001
        return None, f"PDF를 열지 못함 {type(e).__name__}"
    if not text.strip():
        return None, "PDF에 글자가 없음"
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


def followup_plan(run, max_items=15):
    data = load_yaml(run / "15_research.yaml") or {}
    cp = run / "15_research_check.json"
    if not cp.exists():
        print("15_research_check.json이 없습니다. research.py check를 먼저 돌리세요.")
        return 1
    chk = json.loads(cp.read_text(encoding="utf-8"))
    claims = {c.get("id"): c for c in data.get("claims") or []}
    items = [{"kind": "not_found", "area": x.get("area"), "what": x.get("what"), "tried": x.get("tried") or []}
             for x in data.get("not_found") or []]
    for r in chk.get("items") or []:
        if r.get("status") == "verified":
            continue
        c = claims.get(r.get("id")) or {}
        items.append({"kind": "unverified", "id": r.get("id"), "area": r.get("area"), "claim_ko": c.get("claim_ko"),
                      "subject": c.get("subject"), "url": r.get("url"), "reason": r.get("reason")})
    skipped = max(0, len(items) - max_items)
    items = items[:max_items]
    n = Counter(x["kind"] for x in items)
    write_json(run / "15_research_followup_input.json", {"made_at": now_iso(), "count": len(items),
                                                         "not_found": n["not_found"], "unverified": n["unverified"],
                                                         "max": max_items, "skipped": skipped, "items": items})
    print(f"보충 조사 대상: 찾지 못한 것 {n['not_found']}개, 확인 안 된 주장 {n['unverified']}개 → 15_research_followup_input.json"
          + (f", 상한 {max_items}개라 {skipped}개는 뺌" if skipped else "") + ("(0개라 보충 조사 안 함)" if not items else ""))
    return 0


def merge(run):
    import yaml
    cur, first, fu = run / "15_research.yaml", run / "15_research_first.yaml", run / "15_research_followup.yaml"
    if not fu.exists():
        print("15_research_followup.yaml이 없습니다.")
        return 1
    if not first.exists():
        shutil.copyfile(cur, first)
    base = load_yaml(first) or {}
    add = load_yaml(fu) or {}
    ids = {c.get("id") for c in base.get("claims") or []}
    errs, new = [], []
    for c in add.get("claims") or []:
        cid = str(c.get("id") or "")
        if not cid.startswith("fu_"):
            errs.append(f"{cid or '(id 없음)'}: id가 fu_로 시작하지 않음")
        elif cid in ids:
            errs.append(f"{cid}: id가 겹침")
        else:
            ids.add(cid)
            new.append(c)
    if errs:
        print("보충 조사를 합치지 않음:\n  " + "\n  ".join(errs))
        return 1
    out = dict(base)
    out["claims"] = list(base.get("claims") or []) + new
    out["not_found"] = add.get("not_found") or []
    out["followup"] = {"merged_at": now_iso(), "added": len(new), "first_file": first.name, "followup_file": fu.name}
    with open(cur, "w", encoding="utf-8") as f:
        yaml.safe_dump(out, f, allow_unicode=True, sort_keys=False, width=1000)
    print(f"보충 조사 합침: 첫 조사 {len(base.get('claims') or [])}개 + 보충 {len(new)}개 → 15_research.yaml"
          f"(첫 조사는 {first.name}), 남은 찾지 못한 것 {len(out['not_found'])}개. research.py check를 다시 돌리세요.")
    return 0


def main():
    ap = argparse.ArgumentParser(description="웹 조사 주장 확인")
    ap.add_argument("mode", choices=["check", "followup-plan", "merge"])
    ap.add_argument("run", nargs="?")
    ap.add_argument("--max", type=int, default=15)
    args = ap.parse_args()
    run = resolve_run(args.run)
    if args.mode == "followup-plan":
        sys.exit(followup_plan(run, args.max))
    sys.exit({"check": check, "merge": merge}[args.mode](run))


if __name__ == "__main__":
    main()
