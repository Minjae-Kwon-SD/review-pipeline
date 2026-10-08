"""README와 설명서(docs/walkthrough.md)에 쓰는 숫자를 실제 회차 파일에서 모으고, 문서 속 숫자를 대조한다. 모델을 부르지 않는다.

사용:
  python scripts/doc_facts.py build [회차]
    검사 결과, 05_metrics.json, timing.jsonl, costs.jsonl 등에서 숫자를 모아 docs/doc_facts.json(키와 표기)과
    docs/doc_facts.md(사람이 보는 표)를 쓴다. 문서에는 이 표기를 그대로 옮긴다.
  python scripts/doc_facts.py check [회차] [--docs README.md docs/walkthrough.md]
    문서마다 (1) 코드 표시(`...`)와 코드 블록 밖의 숫자가 doc_facts.json 표기에 있는 숫자인지(목록 번호, 단계 번호 같은
    구조 숫자는 ALLOW), (2) 코드 표시 안의 경로가 실제로 있는지(<회차>, <카테고리> 같은 자리 표시는 빼고),
    (3) 가운뎃점이 없는지 본다. 결과: docs/doc_check.json
"""
import argparse
import json
import re
import sys
from collections import OrderedDict
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from pipeline_io import ROOT, load_yaml, now_iso, resolve_run, write_json  # noqa: E402

for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass

# 고치기 단계: 이번 회차에서 지시나 코드를 고치느라 생긴 단계라, 처음부터 바른 지시로 다시 돌리면 필요 없다
FIXUP = {"11_report_polish", "11b_polish_audit", "18b_guide_fix", "20_head_growth", "20b_head_text",
         "23c_specs_cleanup", "24_report_fix", "24b_report_en_fix", "25_guide_g5", "25b_guide_consistency",
         "26_claim_strength", "26b_source_drop", "27_rejudge", "27b_rejudge_audit", "27c_rejudge_guide"}
PHASES = OrderedDict([("review", "리뷰 리포트"), ("guide", "개발 가이드"), ("en", "영어판과 보강(G3 이후)")])


def phase_of(step):
    n = int(re.match(r"\d+", step).group(0))
    return "guide" if 12 <= n <= 19 else ("en" if n >= 20 else "review")


def j(run, name):
    return json.loads((run / name).read_text(encoding="utf-8"))


def ts(s):
    return datetime.fromisoformat(s)


def steps(run):
    """단계마다 시도 목록(시작, 끝, 분)과 종류"""
    ev = [json.loads(l) for l in (run / "timing.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()]
    open_, out = {}, OrderedDict()
    for e in ev:
        if e["event"] == "step_start":
            open_[e["step"]] = e
        elif e["event"] == "step_end" and e["step"] in open_:
            s = open_.pop(e["step"])
            d = out.setdefault(e["step"], {"kind": e["kind"], "tries": []})
            d["tries"].append((s["ts"], e["ts"], (ts(e["ts"]) - ts(s["ts"])).total_seconds() / 60))
    return ev, out


def fmt(x, nd=1):
    return f"{x:,.{nd}f}"


def build(run):
    F = OrderedDict()

    def put(key, text, src):
        F[key] = {"text": str(text), "source": src}

    m = j(run, "05_metrics.json")
    acc = m["accuracy"]
    put("gold.reviews", f"{acc['gold_reviews']}개", "05_metrics.json accuracy.gold_reviews")
    put("gold.f1", acc["sonnet"]["topic_f1_text"], "05_metrics.json accuracy.sonnet.topic_f1_text")
    put("gold.sent", acc["sonnet"]["sentiment_text"], "05_metrics.json accuracy.sonnet.sentiment_text")
    put("gold.top_sent", acc["top"]["sentiment_text"], "05_metrics.json accuracy.top.sentiment_text")
    asins = [r for r in (run / "01_asins.csv").read_text(encoding="utf-8").splitlines()[1:] if ",selected," in r]
    put("data.asins", f"{len(asins)}개", "01_asins.csv status=selected")
    reviews = sum(1 for _ in open(run / "04_tags.jsonl", encoding="utf-8"))
    put("data.tags", f"{reviews:,}개", "04_tags.jsonl 줄 수")
    rv = j(run, "06_report_html_numbers.json")
    import csv
    with open(run / "02_reviews.csv", encoding="utf-8", newline="") as f:
        nrev = sum(1 for _ in csv.DictReader(f))
    put("data.reviews", f"{nrev:,}개", "02_reviews.csv 행 수")
    col = j(run, "02_collect_log.json")
    put("data.dropped", f"{col.get('dropped_count', 0)}개", "02_collect_log.json dropped_count")
    sch = load_yaml(run / "03_schema_approved.yaml")
    put("data.topics", f"{len(sch['topics'])}개", "03_schema_approved.yaml topics")
    iss = load_yaml(run / "07a_issues_approved.yaml")
    nlab = sum(1 for t in iss["topics"] for v in t["directions"].values() for l in (v.get("labels") or []) if l.get("id") != "other")
    put("data.labels", f"{nlab}개", "07a_issues_approved.yaml 라벨 수(other 빼고)")
    gold_tags = sum(1 for l in (run / "gold" / "gold_tags.jsonl").read_text(encoding="utf-8").splitlines() if l.strip())
    put("gold.tags", f"{gold_tags}개", "gold/gold_tags.jsonl 줄 수(내용은 읽지 않고 줄만 셈)")

    a = j(run, "04_tag_audit_summary.json")
    put("audit.tags", f"{a['sample_tags']}개 중 FAIL {a['fail']}개({a['fail_rate'] * 100:.1f}%)", "04_tag_audit_summary.json")
    if "conservative_rate" in a:
        put("audit.tags_cons", f"{a['conservative_rate'] * 100:.1f}%", "04_tag_audit_summary.json conservative_rate(FAIL + UNVERIFIED + missed)")
        put("audit.tags_parts", f"UNVERIFIED {a['unverified']}개, 빠진 태그 {a['missed']}개, 뺀 정답 세트 태그 {a.get('excluded_gold_tags', 0)}개",
            "04_tag_audit_summary.json")
    a = j(run, "07b_issue_audit_summary.json")
    put("audit.labels", f"{a['sample']}개 중 FAIL {a['fail']}개({a['fail_rate'] * 100:.1f}%)", "07b_issue_audit_summary.json")
    a = j(run, "14b_detail_audit_summary.json")
    put("audit.details", f"{a['sample']}개 중 FAIL {a['fail']}개({a['fail_rate'] * 100:.1f}%)", "14b_detail_audit_summary.json")
    tr = load_yaml(run / "06_report_en_audit.yaml")["audit"]
    nf = sum(1 for x in tr.get("findings") or [] if x.get("status") == "FAIL")
    put("audit.translation", f"{tr['checked']}쌍 중 FAIL {nf}개({nf / tr['checked'] * 100:.1f}%)", "06_report_en_audit.yaml")
    h = j(run, "06_report_html_check.json")
    put("html.report_numbers", f"{h['numbers_checked']}개", "06_report_html_check.json numbers_checked")
    put("html.report_drill", f"{h['drilldowns_checked']}개", "06_report_html_check.json drilldowns_checked")
    put("html.report_kb", f"{h['size_kb']}KB", "06_report_html_check.json size_kb")
    h = j(run, "06_report_en_html_check.json")
    put("html.en_numbers", f"{h['numbers_checked']}개", "06_report_en_html_check.json")
    put("html.en_drill", f"{h['drilldowns_checked']}개", "06_report_en_html_check.json")
    put("html.en_kb", f"{h['size_kb']}KB", "06_report_en_html_check.json size_kb")
    h = j(run, "07_guide_html_check.json")
    put("html.guide_numbers", f"{h['numbers_checked']}개", "07_guide_html_check.json numbers_checked")
    put("html.guide_bundles", f"{h['evidence_bundles']}개", "07_guide_html_check.json evidence_bundles")
    put("html.guide_links", f"{h['source_links']}개", "07_guide_html_check.json source_links")
    put("html.guide_kb", f"{h['size_kb']}KB", "07_guide_html_check.json size_kb")
    d = j(run, "14_detail_check.json")
    put("detail.values", f"{d['values']:,}개", "14_detail_check.json values")
    ds = load_yaml(run / "13_detail_schema_approved.yaml")
    put("detail.items", f"{len(ds.get('items') or [])}개", "13_detail_schema_approved.yaml items")
    r = j(run, "15_research_check.json")
    put("research", f"{r['claims']}개 중 {r['verified']}개", "15_research_check.json claims, verified")
    calls = sum(1 for _ in open(run / "market" / "calls.jsonl", encoding="utf-8"))
    put("market.calls", f"{calls}번", "market/calls.jsonl 줄 수")
    if (run / "23_specs_check.json").exists():
        sc = j(run, "23_specs_check.json")
        put("specs.verified", f"{sc['verified']}개", "23_specs_check.json verified")
        put("specs.products", f"{len(sc['by_asin'])}개", "23_specs_check.json by_asin")
    if (run / "05_robustness.json").exists():
        rb = j(run, "05_robustness.json")
        put("robust.n", f"{rb['bootstrap']['n']:,}번", "05_robustness.json bootstrap.n")
        for k in ("head_first", "head_neg_ci", "loo_flips", "weakest"):
            put(f"robust.{k}", rb["texts"][k], f"05_robustness.json texts.{k}")
    g = j(run, "16_guide_metrics.json")["values"]
    put("guide.growth", g["head.fastest_term"]["text"], "16_guide_metrics.json values.head.fastest_term")

    # 시간
    ev, st = steps(run)
    for p, name in PHASES.items():
        mach_all = mach_last = human = 0.0
        for s, d in st.items():
            if phase_of(s) != p:
                continue
            last = d["tries"][-1][2]
            if d["kind"] == "human":
                human += last
                continue
            mach_all += sum(t[2] for t in d["tries"])
            if s not in FIXUP:
                mach_last += last
        put(f"time.{p}.first", f"{fmt(mach_all)}분", f"timing.jsonl {name} 단계 모든 시도 합(사람 대기 빼고)")
        put(f"time.{p}.rerun", f"{fmt(mach_last)}분", f"timing.jsonl {name} 단계 마지막 시도 합(고치기 단계 {', '.join(sorted(FIXUP))} 빼고)")
        put(f"time.{p}.human", f"{fmt(human)}분", f"timing.jsonl {name} 사람 대기(⏸) 단계")
    for kind in ("first", "rerun", "human"):
        tot_t = sum(float(F[f"time.{p}.{kind}"]["text"].rstrip("분").replace(",", "")) for p in PHASES)
        put(f"time.total.{kind}", f"{fmt(tot_t)}분", f"time.<영역>.{kind} 세 영역 합")
    import render_html
    put("html.report_chapters", f"{len(render_html.CHAPTERS)}개 장", "scripts/render_html.py CHAPTERS")
    put("topics.common", f"{len(load_yaml(ROOT / 'config' / 'topics_common.yaml')['topics'])}개", "config/topics_common.yaml topics")
    for s, d in st.items():
        put(f"step.{s}", f"{fmt(d['tries'][-1][2])}분", f"timing.jsonl {s} 마지막 시도")
    # 비용: 실행 기록을 그 직전에 끝난 단계의 영역으로 나눈다
    ends = [(ts(e["ts"]), e["step"]) for e in ev if e["event"] == "step_end"]
    costs = [json.loads(l) for l in (run / "costs.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()]
    tot = OrderedDict((p, [0, 0.0, 0.0]) for p in PHASES)
    for c in costs:
        t = ts(c["logged_at"])
        prev = [s for e, s in ends if e <= t]
        p = phase_of(prev[-1]) if prev else "review"
        tot[p][0] += 1
        tot[p][1] += c["total_cost_usd"]
        tot[p][2] += c["duration_ms"] / 60000
    for p, (n, usd, mins) in tot.items():
        put(f"cost.{p}", f"${usd:.2f}", f"costs.jsonl {PHASES[p]} 실행 {n}번 합")
        put(f"cost.{p}.runs", f"{n}번", "costs.jsonl")
    put("cost.total", f"${sum(v[1] for v in tot.values()):.2f}", "costs.jsonl 전체 합")
    put("cost.runs", f"{len(costs)}번", "costs.jsonl 줄 수")
    put("tests", f"{count_tests()}개", "tests/test_scripts.py 실행 결과의 확인 개수")
    ref_facts(put)

    out = ROOT / "docs" / "doc_facts.json"
    write_json(out, {"made_at": now_iso(), "run": run.name, "facts": F})
    md = ["# 문서 숫자 출처", "", f"회차 {run.name}, {now_iso()[:16]} 기준. `python scripts/doc_facts.py build`가 만든다.", "",
          "| 키 | 표기 | 출처 |", "|---|---|---|"]
    md += [f"| {k} | {v['text']} | {v['source']} |" for k, v in F.items()]
    (ROOT / "docs" / "doc_facts.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    print(f"문서 숫자 {len(F)}개 → docs/doc_facts.json, docs/doc_facts.md")
    return 0


REF_DIR = Path.home() / "Downloads"
REF = [  # (키, 파일, 찾을 정규식, 표기 틀) 정답지 HTML의 머리 문장에서 데이터 크기를 읽는다(구조 비교용, 데이터는 가져오지 않음)
    ("ref.report.reviews", "review_analysis_report_en.html", r"Data: ([\d,]+) Amazon reviews of the top (\d+) revenue ASINs", "{0}개, ASIN {1}개"),
    ("ref.report.tags", "review_analysis_report_en.html", r"\(([\d,]+) tags\)", "{0}개"),
    ("ref.guide.reviews", "Coolmate_Scrubs_Product_Dev_Guide_v1.html", r"Sources: ([\d,]+) Amazon reviews across (\d+) listings and (\d+) categories",
     "{0}개, 리스팅 {1}개, 카테고리 {2}개"),
    ("ref.guide.specs", "Coolmate_Scrubs_Product_Dev_Guide_v1.html", r"(\d+) listing specs and (\d+) size charts", "리스팅 사양 {0}개, 사이즈표 {1}개"),
    ("ref.guide.terms", "Coolmate_Scrubs_Product_Dev_Guide_v1.html", r"([\d,]+) search terms", "{0}개"),
]


def ref_facts(put):
    import html as H
    cache = {}
    for key, fn, pat, tmpl in REF:
        p = REF_DIR / fn
        if not p.exists():
            continue
        if fn not in cache:
            t = re.sub(r"<script.*?</script>|<style.*?</style>", "", p.read_text(encoding="utf-8"), flags=re.S)
            cache[fn] = re.sub(r"\s+", " ", H.unescape(re.sub(r"<[^>]+>", " ", t)))
        mm = re.search(pat, cache[fn])
        if mm:
            put(key, tmpl.format(*mm.groups()), f"정답지 {fn} 머리 문장")


def count_tests():
    import subprocess
    p = subprocess.run([sys.executable, str(ROOT / "tests" / "test_scripts.py")], capture_output=True, text=True, encoding="utf-8",
                       env={**__import__("os").environ, "PYTHONIOENCODING": "utf-8"})
    mm = re.search(r"통과\((\d+)개 확인\)", p.stdout + p.stderr)
    if not mm:
        sys.exit("시험이 통과하지 않아 개수를 적을 수 없습니다.")
    return int(mm.group(1))


NUM = re.compile(r"\$?\d(?:\d|,(?=\d))*(?:\.\d+)?")
PLACEHOLDER = re.compile(r"<[^>]+>|\*|\{[^}]+\}")


def check(run, docs):
    facts = j(ROOT / "docs", "doc_facts.json")["facts"]
    known = set()
    for v in facts.values():
        known.update(NUM.findall(v["text"]))
    al = load_yaml(ROOT / "docs" / "doc_numbers_allow.yaml") or {}
    allow = {str(x) for g in (al.get("allow") or {}).values() for x in g}
    example_paths = set(al.get("example_paths") or [])
    errors, report = [], {}
    for d in docs:
        p = ROOT / d
        text = p.read_text(encoding="utf-8")
        body = re.sub(r"```.*?```", "", text, flags=re.S)
        codes = re.findall(r"`([^`\n]+)`", body)
        prose = re.sub(r"`[^`\n]+`", "", body)
        prose = re.sub(r"\]\([^)]*\)", "]", prose)                                  # 링크 주소
        bad = []
        for line_no, line in enumerate(prose.splitlines(), 1):
            l2 = re.sub(r"^\s*(#+\s*\d+\.|>?\s*\d+\.|[-*]|#+|\|)\s*", "", line)            # 목록 번호, 장 번호
            l2 = re.sub(r"[a-z_-]+-\d{4}-\d{2}-\d{2}|\b\d{4}-\d{2}-\d{2}\b", "", l2)        # 회차 이름과 날짜
            l2 = re.sub(r"\b\d{2}[a-z]?_[A-Za-z0-9_]+", "", l2)                      # 단계와 파일 이름(05_metrics 등)
            l2 = re.sub(r"\bB0[A-Z0-9]{8}\b|\bR[0-9A-Z]{9,}\b", "", l2)              # ASIN, 리뷰 id
            for n in NUM.findall(l2):
                if n not in known and n not in allow:
                    bad.append(f"{line_no}행 '{n}': {line.strip()[:80]}")
        missing = []
        for c in codes:
            c = c.strip()
            if " " in c and not c.startswith(("scripts/", "runs/", "config/", "docs/", ".claude/", "tests/")):
                continue                                                               # 명령이나 값
            path = c.split(" ")[0]
            if PLACEHOLDER.search(path) or path.startswith(("http", "$", "-")) or path in example_paths:
                continue
            if "/" not in path and not re.search(r"\.(py|md|ya?ml|jsonl?|html|csv|txt)$", path):
                continue                                                               # 설정 키(paid.enabled 등)
            cand = [ROOT / path, run / path, ROOT / "scripts" / path, ROOT / "docs" / path, ROOT / "config" / path]
            if not any(x.exists() for x in cand):
                missing.append(path)
        dots = text.count("·")
        report[d] = {"unknown_numbers": bad, "missing_paths": sorted(set(missing)), "middle_dots": dots}
        errors += [f"{d} 숫자 출처 없음 {x}" for x in bad] + [f"{d} 없는 경로 {x}" for x in sorted(set(missing))]
        if dots:
            errors.append(f"{d} 가운뎃점 {dots}개")
    status = "FAIL" if errors else "PASS"
    write_json(ROOT / "docs" / "doc_check.json", {"checked_at": now_iso(), "status": status, "docs": report, "errors": errors})
    print(f"문서 검사: {status}  (" + ", ".join(f"{d}: 숫자 출처 없음 {len(r['unknown_numbers'])}, 없는 경로 {len(r['missing_paths'])}, "
                                           f"가운뎃점 {r['middle_dots']}" for d, r in report.items()) + ")")
    for e in errors[:40]:
        print(f"  오류: {e}")
    return 1 if errors else 0


def main():
    ap = argparse.ArgumentParser(description="문서 숫자 모으기와 대조")
    ap.add_argument("mode", choices=["build", "check"])
    ap.add_argument("run", nargs="?")
    ap.add_argument("--docs", nargs="+", default=["README.md", "docs/walkthrough.md"])
    a = ap.parse_args()
    run = resolve_run(a.run)
    sys.exit(build(run) if a.mode == "build" else check(run, a.docs))


if __name__ == "__main__":
    main()
