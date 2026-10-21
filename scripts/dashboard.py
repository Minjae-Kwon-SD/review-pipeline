"""파이프라인을 돌리는 사람이 보는 대시보드(2026-10-19 담당자 결정). 모델을 부르지 않고, 회차 폴더의 기록 파일을 읽기만 한다.

사용:
  python scripts/dashboard.py [회차] [--port 8765] [--no-open]
    이 PC에서만 열리는 작은 화면(http://127.0.0.1:8765)을 띄우고 브라우저를 연다. 회차를 주지 않으면 runs/CURRENT를 따라간다
    (회차가 바뀌면 화면도 따라 바뀜). 화면은 5초마다 /api/state를 다시 읽고, 바뀐 것이 있으면 알림음과 윈도우 알림을 낸다.
    끄려면 이 창에서 Ctrl+C.
  python scripts/dashboard.py snapshot [회차]
    화면이 읽는 값을 JSON으로 찍기만 한다(시험과 점검용).

읽는 파일(회차 폴더 기준): state.json, timing.jsonl, 00_auto_decisions.md, guard_log.jsonl(.claude/hooks/guard_runs.py가 막은 기록),
  *_check.json, *_summary.json, 07_audit*.yaml, 18_guide_audit*.yaml, 06_report_part_*.md, 17_guide_part_*.md, raw/paid_calls.jsonl 줄 수,
  00_collect_plan.yaml, 08_timing.md, 00_input_check.json, 01_asins.csv, 04_gold_eval.json의 sonnet 요약 숫자 세 개.
읽지 않는 것: gold/, gold_score/ 안의 파일(바로가기는 있는지만 봄), 04_gold_eval_score*(채점용 세트), 리뷰 원문.
남은 시간 예상은 다른 회차(시험 사본 *-rt* 제외)의 timing.jsonl에서, 지금 회차가 마지막으로 끝낸 단계부터 리포트와 가이드 HTML이 끝날 때까지
  걸린 시간(관문 기다림과 멈춤 뺌)의 가운데 값이다. 처음 하는 품목도 단계 구성은 같아 쓸 수 있지만 리뷰 수가 크게 다르면 어긋난다.
"""
import argparse
import csv
import json
import os
import re
import statistics
import subprocess
import sys
import threading
import webbrowser
from datetime import datetime
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from pipeline_io import ROOT, die, now_iso  # noqa: E402

for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass

RUNS = ROOT / "runs"
PAGE = Path(__file__).resolve().parent / "dashboard.html"

# 진행판에 보이는 순서와 이름. stages.yaml에 없는 단계(수집, 정답지, 자동 관문, 시간 표)도 넣는다.
STEPS = [
    ("00_collect", "리뷰 모으기", "script"), ("00_asin_review", "상품 확인", "auto"), ("01_inputs", "입력 검사", "script"),
    ("12_market", "시장 데이터", "script"), ("23_specs", "상품 사양", "agents"), ("02_schema_draft", "주제 초안", "agents"),
    ("03_schema_approval", "주제 확인", "human"), ("04_gold_tagging", "정답지 달기", "human"), ("05a_pilot", "시험 태깅 확인", "auto"),
    ("05_tagging", "태깅", "agents"), ("06_tag_check", "태그 감사", "agents"), ("06_gold_review", "정답지 점수 확인", "auto"),
    ("13_detail_schema_draft", "설계 정보 항목 초안", "agents"), ("13a_detail_schema_approval", "설계 정보 항목 승인", "auto"),
    ("15_research", "웹 조사", "agents"), ("07a_issue_draft", "세부 이슈 초안", "agents"), ("07a_issue_approval", "세부 이슈 승인", "auto"),
    ("08a_report_early", "리포트 미리 쓰기", "agents"), ("16a_guide_metrics_early", "가이드 미리 계산", "script"),
    ("17a_guide_early", "가이드 미리 쓰기", "agents"), ("07b_issue_labeling", "세부 이슈 라벨", "agents"),
    ("07c_issue_check", "라벨 검사", "agents"), ("14_detail_extract", "설계 정보 뽑기", "agents"), ("14b_detail_check", "설계 정보 감사", "agents"),
    ("22_robustness", "견고성 계산", "script"), ("07_weight", "가중 집계", "script"), ("08_report", "리포트 쓰기", "agents"),
    ("09_report_check", "리포트 감사", "agents"), ("11_html", "리포트 HTML", "script"), ("16_guide_metrics", "가이드 계산", "script"),
    ("17_guide_write", "가이드 쓰기", "agents"), ("18_guide_check", "가이드 감사", "agents"), ("19_guide_html", "가이드 HTML", "script"),
    ("10_timing", "시간 표", "script"),
]
STEP_NAME = {s: n for s, n, _ in STEPS}
ALIAS = {"05_weight": "07_weight", "13_detail_schema_approval": "13a_detail_schema_approval", "14b_detail_audit": "14b_detail_check"}
END_STEPS = ("11_html", "19_guide_html")       # 둘 다 끝나면 회차 끝
GOLD_STEP = "04_gold_tagging"

# 점검 신호등: (이름, 파일 글롭, 무엇을 보는지). 같은 글롭에 파일이 여럿이면 가장 늦게 바뀐 것.
CHECKS = [
    ("입력 검사", "00_input_check.json", "리뷰 파일 형식과 개수"),
    ("주제 스키마 검사", "03_schema_check.json", "승인한 주제 목록 형식"),
    ("태그 인용 확인", "04_quote_check_sonnet.json", "태그의 인용이 리뷰 원문에 있는지"),
    ("태그 감사", "04_tag_audit_summary.json", "표본 태그를 감사자가 다시 본 실패 비율(기준 5%)"),
    ("세부 이슈 라벨 검사", "07b_issue_check.json", "라벨 묶음 형식과 빠진 리뷰"),
    ("세부 이슈 라벨 감사", "07b_issue_audit_summary.json", "표본 라벨 실패 비율(기준 5%)"),
    ("설계 정보 항목 검사", "13_detail_schema_check.json", "설계 정보 항목 형식과 인용"),
    ("설계 정보 검사", "14_detail_check.json", "뽑은 값 형식과 빠진 리뷰"),
    ("설계 정보 감사", "14b_detail_audit_summary.json", "표본 값 실패 비율(기준 5%)"),
    ("상품 사양 확인", "23_specs_check.json", "사양 값이 상품 페이지에 있는지"),
    ("리포트 합치기", "06_report_parts_check.json", "장 묶음이 빠짐없이 합쳐졌는지"),
    ("리포트 감사", "07_audit*.yaml", "리포트 숫자와 인용을 감사자가 대조"),
    ("리포트 인용 확인", "07_quote_check.json", "리포트 인용 리뷰 id가 맞는지"),
    ("리포트 HTML 검사", "06_report_html_check.json", "HTML 숫자와 깨진 곳"),
    ("가이드 합치기", "17_guide_parts_check.json", "가이드 장 묶음이 빠짐없이 합쳐졌는지"),
    ("가이드 감사", "18_guide_audit*.yaml", "가이드 숫자와 출처를 감사자가 대조"),
    ("가이드 인용 확인", "18_guide_quote_check.json", "가이드 숫자, 인용, 출처 대조"),
    ("가이드 HTML 검사", "07_guide_html_check.json", "HTML 숫자와 깨진 곳"),
    ("베끼기 검사", "19_copy_check.json", "형식 견본과 문장이 겹치는 비율"),
]

REPORT_PARTS = ["1-7", "8", "9", "10", "11", "12", "appendix"]       # scripts/report_parts.py PARTS
GUIDE_PARTS = ["01-02-A", "03", "04", "head-05"]                       # scripts/guide_parts.py PARTS
EARLY_REPORT = ("1-7", "9")                                            # 08a_report_early가 쓰는 묶음
EARLY_GUIDE = ("01-02-A",)                                             # 17a_guide_early가 쓰는 묶음


def ts(s):
    try:
        return datetime.fromisoformat(s)
    except (TypeError, ValueError):
        return None


def read_json(p):
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None


def read_events(run):
    out = []
    p = run / "timing.jsonl"
    if not p.exists():
        return out
    for line in p.read_text(encoding="utf-8", errors="replace").splitlines():
        try:
            out.append(json.loads(line))
        except ValueError:
            continue                         # 여러 에이전트가 같이 써 깨진 줄은 건너뜀
    return out


def newest(run, pattern):
    files = [p for p in run.glob(pattern) if p.is_file()]
    return max(files, key=lambda p: (p.stat().st_mtime, p.name)) if files else None


def current_name():
    c = RUNS / "CURRENT"
    return c.read_text(encoding="utf-8").strip() if c.exists() else None


def is_test_copy(name):
    return bool(re.search(r"-rt\d*(-|$)", name))


def step_rows(run, events):
    state = read_json(run / "state.json") or {}
    steps = {ALIAS.get(k, k): v for k, v in (state.get("steps") or {}).items()}
    open_waits = {}
    for e in events:
        if e.get("event") == "wait_start":
            open_waits[e.get("gate")] = e.get("ts")
        elif e.get("event") == "wait_end":
            open_waits.pop(e.get("gate"), None)
    starts = {}
    for e in events:
        if e.get("event") == "step_start":
            starts[ALIAS.get(e.get("step"), e.get("step"))] = e.get("ts")
    known = [s for s, _, _ in STEPS]
    extra = sorted(k for k in steps if k not in known)
    ended = all((steps.get(s) or {}).get("status") == "done" for s in END_STEPS)
    rows = []
    for sid in known + extra:
        rec = steps.get(sid) or {}
        status = rec.get("status") or ("none" if ended else "waiting")   # 끝난 회차에서 기록이 없으면 돌지 않은 단계
        kind = next((k for s, _, k in STEPS if s == sid), rec.get("kind") or "script")
        if sid in open_waits and status != "done":
            status = "needs_human"
        if not rec and sid not in open_waits and kind == "auto":
            continue                         # 자동 관문은 기록이 생길 때만 보임
        rows.append({"id": sid, "name": STEP_NAME.get(sid, sid), "kind": kind, "status": status,
                     "since": starts.get(sid) if status in ("running", "needs_human") else rec.get("updated"),
                     "updated": rec.get("updated"), "calls": rec.get("calls"), "retries": rec.get("retries")})
    for gate, t in open_waits.items():       # 단계 목록에 없는 관문 기다림(예: 18_guide_fix2_decision)
        g = ALIAS.get(gate, gate)
        if not any(r["id"] == g for r in rows):
            rows.append({"id": g, "name": STEP_NAME.get(g, g), "kind": "human", "status": "needs_human", "since": t, "updated": t})
    return rows


def agents_running(events):
    open_ = {}
    for e in events:
        if e.get("event") == "SubagentStart":
            open_[e.get("agent_id")] = {"agent_type": e.get("agent_type"), "since": e.get("ts")}
        elif e.get("event") == "SubagentStop":
            open_.pop(e.get("agent_id"), None)
    return sorted(open_.values(), key=lambda a: a["since"] or "")


def last_activity(run, events):
    """마지막 기록 시각(timing.jsonl 마지막 줄과 회차 폴더에서 가장 늦게 바뀐 파일 가운데 늦은 것)"""
    best = None
    for e in events[-50:]:
        t = ts(e.get("ts"))
        if t and (best is None or t > best):
            best = t
    try:
        for p in list(run.iterdir()) + list((run / "market").glob("*")):
            if p.is_file():
                t = datetime.fromtimestamp(p.stat().st_mtime).astimezone()
                if best is None or t > best:
                    best = t
    except OSError:
        pass
    return best.isoformat(timespec="seconds") if best else None


def auto_decisions(run):
    p = run / "00_auto_decisions.md"
    if not p.exists():
        return []
    out, group = [], None
    for line in p.read_text(encoding="utf-8", errors="replace").splitlines():
        s = line.strip()
        if s.startswith("#"):
            group = s.lstrip("#").strip()
        elif s.startswith(("- ", "* ")):
            out.append({"group": group, "text": s[2:].strip()})
        elif s.startswith("|") and not re.match(r"^\|[\s:|-]+\|?$", s):
            cells = [c.strip() for c in s.strip("|").split("|")]
            if cells and cells[0] not in ("관문", "단계"):     # 머리줄은 뺌
                out.append({"group": group, "text": " / ".join(c for c in cells if c)})
    return out


def check_status(p):
    if p.suffix == ".yaml":
        txt = p.read_text(encoding="utf-8", errors="replace")
        m = re.search(r"overall_status:\s*([A-Z_]+)", txt)
        n_fail = len(re.findall(r"status:\s*FAIL", txt)) - (1 if m and m.group(1) == "FAIL" else 0)
        return (m.group(1) if m else "UNKNOWN"), (f"지적 FAIL {n_fail}개" if n_fail else "")
    d = read_json(p) or {}
    st = d.get("status") or ("PASS" if d.get("errors") == [] else "UNKNOWN")
    bits = []
    if isinstance(d.get("fail_rate"), (int, float)):
        bits.append(f"실패 {100 * d['fail_rate']:.1f}%")
    if d.get("errors"):
        bits.append(f"오류 {len(d['errors'])}개")
    if d.get("failed_batches"):
        bits.append(f"실패 묶음 {len(d['failed_batches'])}개")
    if isinstance(d.get("warnings"), list) and d["warnings"]:
        bits.append(f"경고 {len(d['warnings'])}개")
    return st, ", ".join(bits)


def checks(run):
    out = []
    for name, pat, what in CHECKS:
        p = newest(run, pat)
        if not p:
            out.append({"name": name, "status": "NONE", "file": None, "detail": "", "what": what})
            continue
        st, detail = check_status(p)
        out.append({"name": name, "status": st, "file": rel(p), "detail": detail, "what": what,
                    "updated": datetime.fromtimestamp(p.stat().st_mtime).astimezone().isoformat(timespec="seconds")})
    return out


def paid_calls(run):
    log = run / "raw" / "paid_calls.jsonl"
    n = sum(1 for line in log.read_text(encoding="utf-8", errors="replace").splitlines() if line.strip()) if log.exists() else 0
    limit = None
    plan = run / "00_collect_plan.yaml"
    if plan.exists():
        try:
            import yaml
            limit = int((yaml.safe_load(plan.read_text(encoding="utf-8")) or {}).get("max_paid_calls") or 0)
        except Exception:
            limit = None
    return {"calls": n, "limit": limit}


def guard_hits(run):
    out = []
    p = run / "guard_log.jsonl"
    if p.exists():
        for line in p.read_text(encoding="utf-8", errors="replace").splitlines():
            try:
                out.append(json.loads(line))
            except ValueError:
                continue
    return out


def part_state(run, prefix, part):
    final = run / f"{prefix}{part}.md"
    early = run / f"{prefix}{part}_early.md"
    if final.exists():
        return "done"
    if early.exists():
        return "early"
    return "none"


def chapters(run, steps):
    st = {r["id"]: r["status"] for r in steps}
    rep = [{"part": p, "state": part_state(run, "06_report_part_", p), "early_planned": p in EARLY_REPORT}
           for p in REPORT_PARTS]
    gui = [{"part": p, "state": part_state(run, "17_guide_part_", p), "early_planned": p in EARLY_GUIDE}
           for p in GUIDE_PARTS]
    # 08a_report_early는 미리 쓴 묶음을 최종 이름(06_report_part_1-7.md)으로 쓴다. 미리 쓰기가 돌았는지는 단계 기록으로 본다.
    rp = (run / "06_report_parts_check.json").exists()
    gp = (run / "17_guide_parts_check.json").exists()
    return {"report": rep, "guide": gui, "report_merged": rp, "guide_merged": gp,
            "report_early_ran": st.get("08a_report_early"), "guide_early_ran": st.get("17a_guide_early"),
            "report_done": (run / "06_report.html").exists(), "guide_done": (run / "07_guide.html").exists()}


def human_gaps(events, open_until=None):
    """관문 기다림, 사람 단계, 멈춤 구간 목록 [(시작, 끝)]. open_until을 주면 아직 안 끝난 기다림을 그 시각까지로 셈."""
    gaps, waits, hs = [], {}, {}
    for e in events:
        t, ev = ts(e.get("ts")), e.get("event")
        if not t:
            continue
        if ev == "wait_start":
            waits[e.get("gate")] = t
        elif ev == "wait_end" and e.get("gate") in waits:
            gaps.append((waits.pop(e.get("gate")), t))
        elif ev == "step_start" and e.get("kind") == "human":
            hs[e.get("step")] = t
        elif ev == "step_end" and e.get("kind") == "human" and e.get("step") in hs:
            gaps.append((hs.pop(e.get("step")), t))
        elif ev == "pause" and ts(e.get("from")):
            gaps.append((ts(e.get("from")), t))
    if open_until:
        gaps += [(t, open_until) for t in list(waits.values()) + list(hs.values())]
    return gaps


def ai_seconds(a, b, gaps):
    """a~b 사이에서 기다림과 멈춤을 뺀 초(겹친 기다림은 한 번만 뺌)"""
    cut = sorted((max(a, s), min(b, e)) for s, e in gaps if e > a and s < b)
    merged = []
    for s, e in cut:
        if merged and s <= merged[-1][1]:
            merged[-1] = (merged[-1][0], max(merged[-1][1], e))
        else:
            merged.append((s, e))
    return max(0.0, (b - a).total_seconds() - sum((e - s).total_seconds() for s, e in merged))


def step_ends(events):
    out = {}
    for e in events:
        if e.get("event") == "step_end" and ts(e.get("ts")):
            out[ALIAS.get(e.get("step"), e.get("step"))] = ts(e["ts"])
    return out


def step_starts(events):
    out = {}
    for e in events:
        if e.get("event") == "step_start" and ts(e.get("ts")):
            out[ALIAS.get(e.get("step"), e.get("step"))] = ts(e["ts"])
    return out


def history_runs(exclude):
    """다른 회차를 시작 시각 순으로(시험 사본 제외)"""
    out = []
    for d in sorted(RUNS.iterdir()) if RUNS.exists() else []:
        if d.is_dir() and d.name != exclude and not is_test_copy(d.name) and (d / "timing.jsonl").exists():
            first = next((ts(e.get("ts")) for e in read_events(d) if ts(e.get("ts"))), None)
            if first:
                out.append((first, d))
    return [d for _, d in sorted(out)]


ETA_RUNS = 3       # 남은 시간은 같은 단계 기록이 있는 가장 최근 회차 3개로 셈(옛 회차는 단계 구성이 달라 어긋남)


def eta(run, events, steps):
    """남은 시간 예상(분)과 정답지 차례까지(분). 지난 회차가 같은 단계를 끝낸 뒤 끝까지 걸린 AI 시간의 가운데 값."""
    st = {r["id"]: r["status"] for r in steps}
    if all(st.get(s) == "done" for s in END_STEPS):
        return {"state": "finished"}
    mine = step_ends(events)
    done = [(t, s) for s, t in mine.items() if st.get(s) == "done"]
    if not done:
        return {"state": "no_basis", "why": "지금 회차에 끝난 단계가 아직 없음"}
    t_last, milestone = max(done)
    rest, to_gold, used = [], [], []
    for d in reversed(history_runs(run.name)):
        if len(used) >= ETA_RUNS:
            break
        ev = read_events(d)
        ends, starts, gaps = step_ends(ev), step_starts(ev), human_gaps(ev)
        if milestone not in ends or not all(s in ends for s in END_STEPS):
            continue
        fin = max(ends[s] for s in END_STEPS)
        if fin <= ends[milestone]:
            continue
        rest.append(ai_seconds(ends[milestone], fin, gaps) / 60)
        used.append(d.name)
        if st.get(GOLD_STEP) in (None, "waiting") and GOLD_STEP in starts and starts[GOLD_STEP] > ends[milestone]:
            to_gold.append(ai_seconds(ends[milestone], starts[GOLD_STEP], gaps) / 60)
    if not rest:
        return {"state": "no_basis", "why": f"지난 회차 가운데 '{STEP_NAME.get(milestone, milestone)}' 뒤 기록이 있는 회차가 없음"}
    now = datetime.now().astimezone()
    since = ai_seconds(t_last, now, human_gaps(events, open_until=now)) / 60
    left = max(0.0, statistics.median(rest) - since)
    return {"state": "ok", "milestone": milestone, "milestone_name": STEP_NAME.get(milestone, milestone),
            "milestone_at": t_last.isoformat(timespec="seconds"), "minutes_left": round(left, 1),
            "spread": [round(min(rest), 1), round(max(rest), 1)], "runs": used,
            "gold_minutes": round(max(0.0, statistics.median(to_gold) - since), 1) if to_gold else None}


def asin_count(run):
    p = run / "01_asins.csv"
    if not p.exists():
        return None
    with open(p, encoding="utf-8-sig", newline="") as f:
        return sum(1 for r in csv.DictReader(f) if (r.get("status") or "selected") == "selected")


def past_runs(cur):
    out = []
    for d in sorted(RUNS.iterdir()) if RUNS.exists() else []:
        if not d.is_dir() or is_test_copy(d.name):
            continue
        tm = d / "08_timing.md"
        ai = None
        if tm.exists():
            m = re.search(r"AI 작업\(벽시계[^)]*\):\s*([\d.]+)분", tm.read_text(encoding="utf-8", errors="replace"))
            ai = float(m.group(1)) if m else None
        gold = read_json(d / "04_gold_eval.json") or {}
        son = (gold.get("models") or {}).get("sonnet") or {}
        inp = read_json(d / "00_input_check.json") or {}
        aud = read_json(d / "04_tag_audit_summary.json") or {}
        m = re.match(r"(.+?)-(\d{4}-\d{2}-\d{2})(.*)$", d.name)
        if not any((d / f).exists() for f in ("state.json", "timing.jsonl", "06_report.html")):
            continue
        out.append({"run": d.name, "category": m.group(1) if m else d.name, "date": m.group(2) if m else "",
                    "current": d.name == cur, "products": asin_count(d), "reviews": inp.get("reviews"), "ai_minutes": ai,
                    "topic_f1": son.get("topic_f1"), "direction": son.get("direction_agreement"), "mixed": son.get("mixed_agreement"),
                    "tag_audit_fail": aud.get("fail_rate"),
                    "report": rel(d / "06_report.html") if (d / "06_report.html").exists() else None,
                    "guide": rel(d / "07_guide.html") if (d / "07_guide.html").exists() else None})
    return out


def rel(p):
    return str(Path(p).resolve().relative_to(ROOT)).replace("\\", "/")


def links(run):
    cand = [("정답지 화면", "gold/gold_tagging.html"), ("채점용 정답지 화면", "gold_score/gold_tagging.html"),
            ("리포트", "06_report.html"), ("가이드", "07_guide.html"), ("자동으로 정한 것", "00_auto_decisions.md"),
            ("시간 표", "08_timing.md"), ("단계 상태", "state.json"), ("시간 기록", "timing.jsonl"), ("막은 기록", "guard_log.jsonl")]
    out = [{"name": n, "path": rel(run / f)} for n, f in cand if (run / f).exists()]
    out.append({"name": "회차 폴더", "path": rel(run)})
    return out


def snapshot(run_arg=None):
    name = run_arg or current_name()
    run = RUNS / name if name else None
    if not run or not run.is_dir():
        return {"now": now_iso(), "run": name, "error": "회차 폴더가 없습니다. 회차 이름을 주거나 runs/CURRENT를 확인해 주세요."}
    events = read_events(run)
    steps = step_rows(run, events)
    st = {r["id"]: r["status"] for r in steps}
    human = [r for r in steps if r["status"] == "needs_human" and r["kind"] in ("human", "auto")]
    finished = all(st.get(s) == "done" for s in END_STEPS)
    # 끝난 회차에 남은 needs_human(예: 도는 동안 입력이 바뀌어 완료로 못 적은 단계)은 지난 일이라 멈춤으로 보지 않는다
    stuck = [] if finished else [r for r in steps if r["status"] == "needs_human" and r["kind"] not in ("human", "auto")]
    return {
        "now": now_iso(), "run": name, "following_current": run_arg is None, "current": current_name(),
        "steps": steps, "running": [r for r in steps if r["status"] == "running"],
        "human_turn": human, "stuck": stuck, "agents": agents_running(events),
        "last_activity": last_activity(run, events),
        "finished": finished,
        "decisions": auto_decisions(run), "checks": checks(run), "paid": paid_calls(run),
        "guard": guard_hits(run), "chapters": chapters(run, steps), "eta": eta(run, events, steps),
        "history": past_runs(name), "links": links(run),
        "retries": [e for e in events if e.get("event") == "retry"][-20:],
    }


# ---------- 화면 ----------

TESTS = {"state": "idle", "line": "", "at": None}


def run_tests():
    TESTS.update(state="running", line="", at=now_iso())
    try:
        p = subprocess.run([sys.executable, str(ROOT / "tests" / "test_scripts.py")], cwd=ROOT, capture_output=True, timeout=900)
        out = p.stdout.decode("utf-8", errors="replace").strip().splitlines()
        err = p.stderr.decode("utf-8", errors="replace").strip().splitlines()
        if p.returncode == 0:
            m = re.search(r"(\d+)개 확인", out[-1] if out else "")
            TESTS.update(state="pass", line=f"통과 {m.group(1)}개" if m else "통과")
        else:
            fails = [l.strip(" -") for l in out if l.startswith(" -")]
            TESTS.update(state="fail", line=(f"실패 {len(fails)}개: " + "; ".join(fails[:3])) if fails else (err or out or ["실패"])[-1])
    except subprocess.TimeoutExpired:
        TESTS.update(state="fail", line="15분 안에 끝나지 않음")
    TESTS["at"] = now_iso()


def open_path(path):
    """저장소 안의 파일이나 폴더만 그 PC의 기본 프로그램으로 연다."""
    p = (ROOT / path).resolve()
    try:
        p.relative_to(ROOT)
    except ValueError:
        return False, "저장소 밖 경로는 열지 않습니다."
    if not p.exists():
        return False, "파일이 없습니다."
    if os.name == "nt":
        os.startfile(str(p))  # noqa: S606
    elif sys.platform == "darwin":
        subprocess.Popen(["open", str(p)])
    else:
        subprocess.Popen(["xdg-open", str(p)])
    return True, ""


def make_handler(run_arg):
    class H(BaseHTTPRequestHandler):
        def log_message(self, *a):
            pass

        def send(self, code, body, ctype="application/json; charset=utf-8"):
            data = body if isinstance(body, bytes) else body.encode("utf-8")
            self.send_response(code)
            self.send_header("Content-Type", ctype)
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(data)

        def do_GET(self):
            path = self.path.split("?")[0]
            if path in ("/", "/index.html"):
                self.send(200, PAGE.read_bytes(), "text/html; charset=utf-8")
            elif path == "/api/state":
                snap = snapshot(run_arg)
                snap["tests"] = TESTS
                self.send(200, json.dumps(snap, ensure_ascii=False))
            else:
                self.send(404, json.dumps({"error": "없음"}))

        def do_POST(self):
            n = int(self.headers.get("Content-Length") or 0)
            try:
                body = json.loads(self.rfile.read(n).decode("utf-8") or "{}")
            except ValueError:
                body = {}
            if self.headers.get("Origin") not in (None, f"http://{self.headers.get('Host')}"):
                self.send(403, json.dumps({"error": "다른 사이트에서 온 요청"}))       # 다른 웹 페이지가 이 PC 파일을 열지 못하게
            elif self.path == "/api/open":
                ok, why = open_path(str(body.get("path") or ""))
                self.send(200 if ok else 400, json.dumps({"ok": ok, "error": why}, ensure_ascii=False))
            elif self.path == "/api/tests":
                if TESTS["state"] != "running":
                    threading.Thread(target=run_tests, daemon=True).start()
                self.send(200, json.dumps({"ok": True}))
            else:
                self.send(404, json.dumps({"error": "없음"}))
    return H


def serve(run_arg, port, no_open):
    srv = ThreadingHTTPServer(("127.0.0.1", port), make_handler(run_arg))
    url = f"http://127.0.0.1:{port}"
    print(f"대시보드: {url}  (회차: {run_arg or 'runs/CURRENT를 따라감'}, 끄려면 Ctrl+C)")
    if not no_open:
        threading.Timer(0.5, lambda: webbrowser.open(url)).start()
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        print("대시보드를 껐습니다.")


def main():
    ap = argparse.ArgumentParser(description="파이프라인 대시보드")
    ap.add_argument("args", nargs="*", help="[snapshot] [회차]")
    ap.add_argument("--port", type=int, default=8765)
    ap.add_argument("--no-open", action="store_true", help="브라우저를 열지 않음")
    a = ap.parse_args()
    args = list(a.args)
    if args and args[0] == "snapshot":
        print(json.dumps(snapshot(args[1] if len(args) > 1 else None), ensure_ascii=False, indent=2))
        return 0
    run_arg = args[0] if args else None
    if run_arg and not (RUNS / run_arg).is_dir():
        die(f"회차 폴더가 없습니다: runs/{run_arg}")
    serve(run_arg, a.port, a.no_open)
    return 0


if __name__ == "__main__":
    sys.exit(main())
