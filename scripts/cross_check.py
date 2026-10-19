"""리포트(06_report.md)와 가이드(17_guide.md) 사이, 그리고 각 문서 장 사이의 표현 어긋남을 찾는다. 모델을 부르지 않는다(2026-10-17 E2).

사용: python scripts/cross_check.py [회차] [--report 06_report.md] [--guide 17_guide.md] [--out 19_cross_check.json]

1. 방향 부호: 같은 브랜드에 붙은 방향 지수(문장에 방향 이름이나 '방향'이 있을 때의 +0.xx, -0.xx)가 문서나 장마다 부호가 반대면 FAIL.
   0 근처(카테고리 설정 guide.direction_index 기준 |지수| < 1.96/sqrt(n), n을 모르면 0.20 미만)인데 '방향 불분명' 없이 한쪽 이름을 쓰면 경고.
2. 1위 단정: 머리 숫자 주제(guide.head_topic)를 '가장 많은', '가장 높', '1위', '단독'으로 쓰는 줄에 '비슷', '같은 수준', '사실상',
   '순위는 정하지', '거의 같' 같은 단서가 같은 문장에 없고, 다시 뽑기에서 1위로 남은 비율(05_robustness.json)이 60% 미만이면 FAIL.
3. 안전 라벨 구성: 안전 주제 부정 세부 이슈 라벨 이름을 둘 이상 늘어놓은 줄에 라벨(리뷰 1개 이상)이 하나라도 빠지면 FAIL.
결과: 19_cross_check.json(오류, 경고, 문서와 줄). 리포트나 가이드 한쪽만 있으면 있는 쪽만 본다.
"""
import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from pipeline_io import ROOT, category_conf, load_schema, load_yaml, now_iso, resolve_run, write_json, ASIN_COLS, load_csv_or_die, common_topic  # noqa: E402

for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass

HEDGE = ("비슷", "같은 수준", "사실상", "순위는 정하지", "순위를 정하지", "거의 같", "나란히", "차이가 작", "함께 관문")
SIGNED = re.compile(r"(?<![\d.])([+-−](?:0\.\d{2}|1\.00))(?!\d)")
CH = re.compile(r"^## (.+)$")


def sentences(text):
    """(장 제목, 줄 번호, 문장) 목록. 표 블록(<!-- 표: ... -->)과 인용 줄(>)은 뺀다."""
    out, ch, in_table = [], "", False
    for ln, line in enumerate(text.splitlines(), 1):
        if line.startswith("<!-- 표:"):
            in_table = True
        if in_table:
            if line.startswith("<!-- /표:"):
                in_table = False
            continue
        m = CH.match(line)
        if m:
            ch = m.group(1).split()[0]
            continue
        if line.lstrip().startswith(">") or line.lstrip().startswith("|"):
            continue
        for s in re.split(r"(?<=[.다])\s+", line):
            if s.strip():
                out.append((ch, ln, s.strip()))
    return out


def direction_claims(doc, sents, brands, hi, lo):
    """(브랜드, 지수, 문서, 장, 줄, 문장): 방향 이름이나 '방향'이 있는 문장에서 브랜드 뒤 40자 안의 첫 부호 숫자"""
    claims = []
    for ch, ln, s in sents:
        if not (hi in s or lo in s or "방향" in s):
            continue
        for b in brands:
            for m in re.finditer(re.escape(b), s):
                n = SIGNED.search(s, m.end(), m.end() + 60)
                if n and not any(o in s[m.end():n.start()] for o in brands if o != b):
                    # 2026-10-17 rt7: 브랜드 바로 뒤 ASIN이 있으면 그 상품 값(같은 브랜드의 다른 상품끼리는 견주지 않음),
                    # 방향 불분명은 문장 전체에서 봄(긴 문장에서 120자 뒤에 있던 '불분명'을 놓침)
                    asin = re.match(r"\s*(B0[0-9A-Z]{8})", s[m.end():n.start()])
                    claims.append({"brand": b + (" " + asin.group(1) if asin else ""), "index": float(n.group(1).replace("−", "-")),
                                   "doc": doc, "chapter": ch, "line": ln, "text": s[:120], "unclear": "불분명" in s})
    return claims


def check(run, report="06_report.md", guide="17_guide.md"):
    cat = run.name.split("-")[0]
    conf = category_conf(run).get("guide") or {}
    schema = load_schema(run)
    brands = sorted({r["brand"] for r in load_csv_or_die(run / "01_asins.csv", ASIN_COLS) if r["status"] == "selected" and r.get("brand")},
                    key=len, reverse=True)
    di = conf.get("direction_index") or {}
    hi, lo = (di.get("high") or {}).get("name", "-"), (di.get("low") or {}).get("name", "-")
    docs = {d: (run / f).read_text(encoding="utf-8") for d, f in (("report", report), ("guide", guide)) if (run / f).exists()}
    errors, warns = [], []
    # 1. 방향 부호
    claims = []
    for d, t in docs.items():
        claims += direction_claims(d, sentences(t), brands, hi, lo)
    for b in sorted({c["brand"] for c in claims}):
        cs = [c for c in claims if c["brand"] == b and c["index"] != 0 and not c["unclear"]]   # 방향 불분명으로 적은 값은 부호를 견주지 않음
        if any(c["index"] > 0 for c in cs) and any(c["index"] < 0 for c in cs):
            pos = next(c for c in cs if c["index"] > 0)
            neg = next(c for c in cs if c["index"] < 0)
            errors.append(f"방향 부호 반대: {b} {pos['doc']} {pos['chapter']}장 {pos['line']}줄 {pos['index']:+.2f} 대 "
                          f"{neg['doc']} {neg['chapter']}장 {neg['line']}줄 {neg['index']:+.2f}")
    for c in claims:
        if abs(c["index"]) < 0.20 and not c["unclear"] and (hi in c["text"] or lo in c["text"]):
            warns.append(f"0 근처 방향({c['brand']} {c['index']:+.2f})에 한쪽 이름: {c['doc']} {c['chapter']}장 {c['line']}줄")
    # 2. 1위 단정
    rob = run / "05_robustness.json"
    hp = json.loads(rob.read_text(encoding="utf-8"))["bootstrap"].get("head_first_pct") if rob.exists() else None
    tname = (schema.get(conf.get("head_topic")) or {}).get("name_ko")
    if tname and isinstance(hp, (int, float)) and hp < 60:
        t1 = re.escape(tname)
        top = re.compile(rf"{t1}[^.]{{0,40}}?(주제 중 가장 높|가장 (많은|흔한|큰) (약점|불만)|불만 1위|단독 1위|1위 약점)|(불만|약점) 1위[^.]{{0,6}}{t1}")
        for d, t in docs.items():
            for ch, ln, s in sentences(t):
                if top.search(s) and "다시 뽑" not in s and not any(h in s for h in HEDGE):
                    errors.append(f"1위 단정({tname}, 다시 뽑기 1위 유지 {hp}%): {d} {ch}장 {ln}줄: {s[:80]}")
    # 3. 안전 라벨 구성
    cnt = run / "07b_issue_counts.json"
    sid = common_topic(schema, "safety")
    if cnt.exists() and sid:
        ent = json.loads(cnt.read_text(encoding="utf-8"))["topics"].get(f"{sid}.negative") or {}
        # 몸 반응 라벨(그 라벨 리뷰가 모두 07c에서 이상 반응으로 판정된 것)은 '이상 반응 있음' 수로 따로 적으므로 제품 위험 라벨 목록에서 뺀다
        sym = {str(v["review_id"]) for v in ((load_yaml(run / "07c_safety_verdicts.yaml") or {}).get("audit") or {}).get("verdicts") or []
               if v.get("symptom_type")}
        lab = {}
        lp = run / "07b_issue_labels.jsonl"
        for row in ([json.loads(x) for x in lp.read_text(encoding="utf-8").splitlines() if x.strip()] if lp.exists() else []):
            for l in row.get("labels") or []:
                lab.setdefault(l, set()).add(str(row["review_id"]))
        alln = [l for l in ent.get("labels") or [] if l["id"] != "other" and l.get("reviews")]
        names = [l["name_ko"] for l in alln if not (lab.get(l["id"]) and lab[l["id"]] <= sym)]     # 제품 위험 라벨(빠지면 안 됨)
        listed = [l["name_ko"] for l in alln]
        for d, t in docs.items():
            for ln, line in enumerate(t.splitlines(), 1):
                if line.startswith("|") or line.startswith("<!--") or not re.search(r"안전|제품 위험|이상 반응", line):
                    continue
                hit = [n for n in names if n in line]
                if sum(n in line for n in listed) >= 2 and len(hit) < len(names):
                    errors.append(f"안전 라벨 구성 빠짐: {d} {ln}줄에 {len(hit)}개, 빠진 것 {[n for n in names if n not in hit]}")
    status = "FAIL" if errors else "PASS"
    out = {"checked_at": now_iso(), "status": status, "docs": list(docs), "direction_claims": len(claims), "errors": errors, "warnings": warns}
    return out


def main():
    ap = argparse.ArgumentParser(description="리포트와 가이드 표현 대조")
    ap.add_argument("run", nargs="?")
    ap.add_argument("--report", default="06_report.md")
    ap.add_argument("--guide", default="17_guide.md")
    ap.add_argument("--out", default="19_cross_check.json")
    a = ap.parse_args()
    run = resolve_run(a.run)
    out = check(run, a.report, a.guide)
    write_json(run / a.out, out)
    print(f"리포트와 가이드 대조: {out['status']}  (문서 {', '.join(out['docs'])}, 방향 주장 {out['direction_claims']}개, "
          f"오류 {len(out['errors'])}개, 경고 {len(out['warnings'])}개)")
    for e in out["errors"][:30]:
        print(f"  오류: {e}")
    for w in out["warnings"][:10]:
        print(f"  경고: {w}")
    sys.exit(1 if out["errors"] else 0)


if __name__ == "__main__":
    main()
