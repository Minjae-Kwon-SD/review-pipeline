"""단계별 시간 기록, 단계 상태(state.json), 시간 표.

사용:
  python scripts/timing_report.py mark [회차] start|end|stop <단계 이름> [--kind script|agents|human]
    /review-run이 단계마다 시작과 끝을 timing.jsonl에 적고, 같은 때 state.json의 상태를 바꾼다.
    start: running(사람 대기면 needs_human), end: done, stop: 재시도를 다 써서 멈춤(needs_human).
    --kind는 스크립트 단계 script, 에이전트를 부르는 단계 agents, 사람 대기(⏸) human.
    --calls(에이전트 호출 수), --retries(재시도 호출 수), --workers(동시 실행 수)를 주면 그 줄에 함께 적는다.
    end에서 그 단계가 config/stages.yaml에 있으면 입력 해시(stage_plan.input_hash)를 state.json에 적는다(다음에 같은 입력이면 건너뜀).
    에이전트 하나하나의 시작과 끝은 .claude/hooks/timing.py가 같은 파일에 적는다.
  python scripts/timing_report.py report [회차]
    timing.jsonl을 짝지어 08_timing.md를 만든다. 기계 시간 = 전체 경과 - 사람 대기.
    같은 단계를 두 번 이상 시작했으면(중간에 멈춘 뒤 이어 돌리기 등) 이전 시도도 표와 기계 시간에 들어가므로,
    단계마다 마지막 시도만 더한 값을 따로 적는다.
"""
import argparse
import json
import sys
from datetime import datetime

from pipeline_io import now_iso, read_jsonl, resolve_run, write_json

STATUS = {"start": "running", "end": "done", "stop": "needs_human"}


def stage_hash(run, step):
    """config/stages.yaml에 있는 단계면 (지금 입력 해시, 지시문과 코드 해시), 없으면 (None, None)"""
    try:
        import stage_plan
        conf = stage_plan.load_conf()
    except SystemExit:
        return None, None
    st = stage_plan.stage_by_id(conf).get(step)
    return (stage_plan.input_hash(run, st), stage_plan.code_hash(st)) if st else (None, None)


def stage_files(run, step):
    """시작 때 있던 입력 파일마다 해시(단계가 도는 동안 바뀌었는지 보는 데 씀)"""
    try:
        import stage_plan
        st = stage_plan.stage_by_id(stage_plan.load_conf()).get(step)
    except SystemExit:
        return None
    return stage_plan.input_files(run, st) if st else None


def mark(run, edge, step, kind, calls=None, retries=None, workers=None):
    ts = now_iso()
    status = "needs_human" if edge == "start" and kind == "human" else STATUS[edge]
    ev = {"ts": ts, "event": "step_start" if edge == "start" else "step_end", "step": step, "kind": kind, "status": status}
    for k, v in (("calls", calls), ("retries", retries), ("workers", workers)):
        if v is not None:
            ev[k] = v
    ih, ch = stage_hash(run, step) if edge in ("start", "end") else (None, None)
    path = run / "state.json"
    state = json.loads(path.read_text(encoding="utf-8")) if path.exists() else {"run": run.name, "steps": {}}
    prev = state["steps"].get(step) or {}
    if edge == "end" and prev.get("input_files_start") is not None:
        # 시작 때 있던 입력 파일이 단계가 도는 동안 바뀌거나 없어졌으면 완료로 적지 않는다(새 결과가 어느 입력 기준인지 모름).
        # 단계가 스스로 만든 입력(시작 때 없던 파일, 예: 12_market의 market/raw)은 보지 않는다.
        now = stage_files(run, step) or {}
        changed = sorted(f for f, h in prev["input_files_start"].items() if now.get(f) != h)
        if changed:
            status = "needs_human"
            ev["status"] = status
            ev["input_changed"] = changed[:20]
            print(f"{step}: 단계가 도는 동안 입력 파일 {len(changed)}개가 바뀌었습니다(예: {changed[0]}). 완료로 적지 않습니다.")
    if edge == "end" and ih:
        ev["input_hash"] = ih
        if ch:
            ev["code_hash"] = ch
    with open(run / "timing.jsonl", "a", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps(ev, ensure_ascii=False) + "\n")
    rec = {"status": status, "kind": kind, "updated": ts, **{k: ev[k] for k in ("calls", "retries", "workers") if k in ev}}
    if edge == "start" and ih:
        rec["input_files_start"] = stage_files(run, step) or {}
    if edge == "end" and status == "done" and ih:
        rec["input_hash"] = ih
        if ch:
            rec["code_hash"] = ch
    state["steps"][step] = rec
    write_json(path, state)
    print(f"{step}: {status}")
    return 0


def pair_events(events):
    """시작과 끝을 짝지어 (이름, 종류, 시작, 끝) 목록으로 돌려준다."""
    open_, rows = {}, []
    for e in events:
        ts = datetime.fromisoformat(e["ts"])
        ev = e.get("event", "")
        if ev in ("SubagentStart", "SubagentStop"):
            key = ("agent", e.get("agent_id") or e.get("agent_type"))
            name, kind = e.get("agent_type") or "agent", "agent"  # Hook이 적은 에이전트 하나
        elif ev in ("step_start", "step_end"):
            key = ("step", e.get("step"))
            name, kind = e.get("step"), e.get("kind", "script")
        else:
            continue
        if ev in ("SubagentStart", "step_start"):
            open_[key] = (name, kind, ts)
        elif key in open_:
            n, k, start = open_.pop(key)
            rows.append((n, k, start, ts))
    rows += [(n, k, start, None) for n, k, start in open_.values()]
    return sorted(rows, key=lambda r: r[2])


def minutes(a, b):
    return (b - a).total_seconds() / 60


def report(run):
    path = run / "timing.jsonl"
    if not path.exists():
        print("timing.jsonl이 없습니다.")
        return 1
    rows = pair_events(read_jsonl(path))
    if not rows:
        print("짝지을 기록이 없습니다.")
        return 1
    done = [r for r in rows if r[3]]
    first, last = min(r[2] for r in rows), max(r[3] for r in done) if done else None
    human = sum(minutes(s, e) for _, k, s, e in done if k == "human")
    agents = sum(minutes(s, e) for _, k, s, e in done if k == "agent")
    total = minutes(first, last) if last else 0.0
    attempts, last_try = {}, {}
    for n, k, s, e in done:
        if k in ("script", "agents"):
            attempts[n] = attempts.get(n, 0) + 1
            last_try[n] = minutes(s, e)
    retried = {n: c for n, c in attempts.items() if c > 1}
    kind_ko = {"agent": "에이전트", "agents": "에이전트 단계", "script": "스크립트", "human": "사람 대기"}
    lines = [f"# 단계별 시간: {run.name}", "",
             "| 단계 | 종류 | 시작 | 끝 | 걸린 분 |", "|---|---|---|---|---|"]
    for n, k, s, e in rows:
        lines.append(f"| {n} | {kind_ko.get(k, k)} | {s:%H:%M:%S} | {e:%H:%M:%S} | {minutes(s, e):.1f} |" if e
                     else f"| {n} | {kind_ko.get(k, k)} | {s:%H:%M:%S} | 끝 기록 없음 | - |")
    notes = [f"- 전체 경과: {total:.1f}분",
             f"- 사람 대기: {human:.1f}분",
             f"- 기계 시간(전체 경과 - 사람 대기): {total - human:.1f}분. 원래 방식과 비교하는 값입니다.",
             f"- 에이전트 작업 시간 합: {agents:.1f}분. 기계 시간보다 크면 그만큼 병렬로 돌았다는 뜻입니다."]
    if retried:
        notes.append("- 두 번 이상 시작한 단계: " + ", ".join(f"{n} {c}번" for n, c in retried.items())
                     + f". 단계마다 마지막 시도만 더한 기계 시간은 {sum(last_try.values()):.1f}분입니다"
                     " (단계 사이의 짧은 틈은 빠짐).")
    (run / "08_timing.md").write_text("\n".join(lines + [""] + notes) + "\n", encoding="utf-8")
    print("\n".join(notes))
    return 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("mode", choices=["mark", "report"])
    ap.add_argument("args", nargs="*", help="mark: [회차] start|end|stop <단계 이름>, report: [회차]")
    ap.add_argument("--kind", default="script", choices=["script", "agents", "human"])
    ap.add_argument("--calls", type=int, default=None)
    ap.add_argument("--retries", type=int, default=None)
    ap.add_argument("--workers", type=int, default=None)
    a = ap.parse_args()
    if a.mode == "report":
        sys.exit(report(resolve_run(a.args[0] if a.args else None)))
    if len(a.args) == 2:
        run, (edge, step) = resolve_run(None), a.args
    elif len(a.args) == 3:
        run, edge, step = resolve_run(a.args[0]), a.args[1], a.args[2]
    else:
        ap.error("mark에는 [회차] start|end|stop <단계 이름>을 주세요.")
    if edge not in STATUS:
        ap.error("start, end, stop 중 하나여야 합니다.")
    sys.exit(mark(run, edge, step, a.kind, a.calls, a.retries, a.workers))


if __name__ == "__main__":
    main()
