"""단계별 시간 기록, 단계 상태(state.json), 시간 표.

사용:
  python scripts/timing_report.py mark [회차] start|end|stop <단계 이름> [--kind script|agents|human] [--force]
    /review-run이 단계마다 시작과 끝을 timing.jsonl에 적고, 같은 때 state.json의 상태를 바꾼다.
    start: running(사람 쪽이면 needs_human), end: done, stop: 재시도를 다 써서 멈춤(needs_human).
    --kind는 스크립트 단계 script, 에이전트를 부르는 단계 agents, 관문(⏸) human.
    human의 end는 담당자 답을 받은 턴의 맨 처음에 찍는다. start 뒤 30초 안이면 거절한다(정말 그랬으면 --force).
    --calls(에이전트 호출 수), --retries(재시도 호출 수), --workers(동시 실행 수)를 주면 그 줄에 함께 적는다.
    end에서 그 단계가 config/stages.yaml에 있으면 입력 해시(stage_plan.input_hash)를 state.json에 적는다(다음에 같은 입력이면 건너뜀).
    에이전트 하나하나의 시작과 끝은 .claude/hooks/timing.py가 같은 파일에 적는다.
  python scripts/timing_report.py wait [회차] start|end <관문> [--force]
    관문 기다림. start는 질문을 보내고 턴을 끝내기 직전, end는 담당자 답을 받은 턴의 맨 처음. 30초 안 end는 거절(--force).
  python scripts/timing_report.py pause [회차] --reason limit|pc_off
    사용량 한도나 PC 꺼짐에서 다시 시작한 턴의 맨 처음에 부른다. 직전 기록 시각부터 지금까지를 멈춤으로 적는다.
  python scripts/timing_report.py report [회차]
    timing.jsonl을 짝지어 08_timing.md를 만든다. 시간 나눔(2026-10-13):
    AI 작업 = 에이전트와 스크립트, 에이전트 단계가 하나라도 돌던 벽시계 시간(겹친 시간은 한 번)에서 기다림, 라벨링, 멈춤을 뺀 것.
      관문 답(human 단계 end, wait end)이 안에 든 단계는 기다림이 섞였으므로 AI 작업에 넣지 않고 이름만 적는다.
    담당자 라벨링 = gold/, gold_score/의 gold_label_times.json에서 화면을 연 때부터 마지막 저장이나 제출까지(다시 열면 더함).
    담당자 기다림 = wait start~end(와 human 단계의 start~end)에서 라벨링과 멈춤을 뺀 것.
    멈춤 = pause 기록. 끝 기록 없는 에이전트 실행은 시간에 넣지 않고 개수만 센다. 기록이 없는 값은 "기록 없음".
    같은 단계를 두 번 이상 시작했으면 단계마다 마지막 시도만 더한 값을 따로 적는다.
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


HUMAN_KINDS = ("human",)


def mark(run, edge, step, kind, calls=None, retries=None, workers=None, force=False):
    ts = now_iso()
    if edge == "end" and kind in HUMAN_KINDS and not force and (run / "timing.jsonl").exists():
        starts = [e for e in read_jsonl(run / "timing.jsonl") if e.get("event") == "step_start" and e.get("step") == step]
        if starts and (datetime.fromisoformat(ts) - datetime.fromisoformat(starts[-1]["ts"])).total_seconds() < 30:
            print(f"{step}: 시작하고 30초 안에 끝을 찍으려 합니다. 사람 쪽 단계의 끝은 담당자 답을 받은 턴의 맨 처음에 찍습니다. "
                  "정말 그렇게 빨리 답했으면 --force를 붙이세요.")
            return 1
    status = "needs_human" if edge == "start" and kind in HUMAN_KINDS else STATUS[edge]
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
    append_event(run, ev)
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


def append_event(run, ev):
    with open(run / "timing.jsonl", "a", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps(ev, ensure_ascii=False) + "\n")


def wait(run, edge, gate, force=False):
    ts = now_iso()
    if edge == "end" and not force and (run / "timing.jsonl").exists():
        starts = [e for e in read_jsonl(run / "timing.jsonl") if e.get("event") == "wait_start" and e.get("gate") == gate]
        if starts and (datetime.fromisoformat(ts) - datetime.fromisoformat(starts[-1]["ts"])).total_seconds() < 30:
            print(f"{gate}: 기다림을 시작하고 30초 안에 끝을 찍으려 합니다. 끝은 담당자 답을 받은 턴의 맨 처음에 찍습니다. "
                  "정말 그렇게 빨리 답했으면 --force를 붙이세요.")
            return 1
    append_event(run, {"ts": ts, "event": "wait_" + edge, "gate": gate})
    print(f"{gate}: 기다림 {edge}")
    return 0


def pause(run, reason):
    path = run / "timing.jsonl"
    events = read_jsonl(path) if path.exists() else []
    if not events:
        print("timing.jsonl에 기록이 없어 멈춤의 시작을 알 수 없습니다.")
        return 1
    ts, frm = now_iso(), max(events, key=lambda e: datetime.fromisoformat(e["ts"]))["ts"]
    append_event(run, {"ts": ts, "event": "pause", "from": frm, "reason": reason})
    print(f"멈춤 {reason}: {frm} ~ {ts} ({minutes(datetime.fromisoformat(frm), datetime.fromisoformat(ts)):.1f}분)")
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


def union(iv):
    out = []
    for s, e in sorted(x for x in iv if x[1] > x[0]):
        if out and s <= out[-1][1]:
            out[-1] = (out[-1][0], max(out[-1][1], e))
        else:
            out.append((s, e))
    return out


def subtract(iv, cut):
    out, cut = [], union(cut)
    for s, e in union(iv):
        for cs, ce in cut:
            if ce <= s or cs >= e:
                continue
            if cs > s:
                out.append((s, cs))
            s = max(s, ce)
            if s >= e:
                break
        if s < e:
            out.append((s, e))
    return out


def total_min(iv):
    return sum(minutes(s, e) for s, e in union(iv))


def label_sessions(run):
    """정답 세트 화면이 적은 시각(open, save, submit)으로 라벨링 구간을 만든다. 파일이 하나도 없으면 None.
    구간은 open부터 다음 open 전의 마지막 save나 submit까지. 그 사이 저장이 없으면 끝을 모르는 구간으로 개수만 센다."""
    found, sessions, unknown = False, [], 0
    for d in ("gold", "gold_score"):
        p = run / d / "gold_label_times.json"
        if not p.exists():
            continue
        found = True
        evs = sorted(json.loads(p.read_text(encoding="utf-8")).get("events") or [], key=lambda e: e["ts"])
        start = end = None
        for e in evs + [{"event": "open", "ts": None}]:
            if e["event"] == "open":
                if start is not None:
                    if end is not None:
                        sessions.append((start, end))
                    else:
                        unknown += 1
                start = end = None
                if e["ts"]:
                    start = datetime.fromisoformat(e["ts"].replace("Z", "+00:00"))
            elif start is not None:
                end = datetime.fromisoformat(e["ts"].replace("Z", "+00:00"))
    return (sessions, unknown) if found else None


def split_section(run, events, rows):
    """AI 작업, 담당자 라벨링, 담당자 기다림, 멈춤, 끝 기록 없는 에이전트 실행 수"""
    done = [r for r in rows if r[3]]
    agents = [(s, e) for _, k, s, e in done if k == "agent"]
    no_end = sum(1 for _, k, _s, e in rows if k == "agent" and e is None)
    waits, open_w = [], {}
    for ev in events:
        if ev.get("event") == "wait_start":
            open_w[ev.get("gate")] = datetime.fromisoformat(ev["ts"])
        elif ev.get("event") == "wait_end" and ev.get("gate") in open_w:
            waits.append((open_w.pop(ev.get("gate")), datetime.fromisoformat(ev["ts"])))
    waits += [(s, e) for _, k, s, e in done if k == "human"]
    answers = [datetime.fromisoformat(ev["ts"]) for ev in events
               if ev.get("event") == "wait_end" or (ev.get("event") == "step_end" and ev.get("kind") == "human")]
    steps, mixed = [], []
    for n, k, s, e in done:
        if k in ("script", "agents"):
            if any(s < t < e for t in answers):
                mixed.append((n, minutes(s, e)))
            else:
                steps.append((s, e))
    pauses = [(datetime.fromisoformat(ev["from"]), datetime.fromisoformat(ev["ts"]), ev.get("reason"))
              for ev in events if ev.get("event") == "pause"]
    p_iv = [(s, e) for s, e, _ in pauses]
    lab = label_sessions(run)
    lab_iv = lab[0] if lab else []
    excl = waits + lab_iv + p_iv
    by_type = {}
    for n, k, s, e in done:
        if k == "agent":
            m, c = by_type.get(n, (0.0, 0))
            by_type[n] = (m + minutes(s, e), c + 1)
    out = ["", "## 시간 나눔(AI 작업, 담당자 라벨링, 담당자 기다림, 멈춤)",
           f"- AI 작업(벽시계, 겹친 시간은 한 번): {total_min(subtract(agents + steps, excl)):.1f}분. "
           f"그중 에이전트가 하나라도 돌던 시간 {total_min(subtract(agents, excl)):.1f}분"]
    if by_type:
        out.append("- 에이전트별 합(겹친 시간도 각각 셈): " + ", ".join(
            f"{n} {m:.1f}분({c}번)" for n, (m, c) in sorted(by_type.items(), key=lambda x: -x[1][0])))
    if lab is None:
        out.append("- 담당자 라벨링: 기록 없음(gold_label_times.json 없음)")
    else:
        out.append(f"- 담당자 라벨링: {total_min(lab_iv):.1f}분(화면을 연 구간 {len(lab_iv)}개"
                   + (f", 끝을 모르는 구간 {lab[1]}개는 시간에 넣지 않음" if lab[1] else "") + ")")
    if waits:
        out.append(f"- 담당자 기다림(라벨링과 멈춤 뺌): {total_min(subtract(waits, lab_iv + p_iv)):.1f}분(관문 {len(waits)}번)")
    else:
        out.append("- 담당자 기다림: 기록 없음(wait 기록 없음)")
    if pauses:
        kinds, ko = {}, {"limit": "사용량 한도", "pc_off": "PC 꺼짐"}
        for _s, _e, r in pauses:
            kinds[r] = kinds.get(r, 0) + 1
        out.append(f"- 멈춤: {total_min(p_iv):.1f}분(" + ", ".join(f"{ko.get(r, r)} {c}번" for r, c in kinds.items()) + ")")
    else:
        out.append("- 멈춤: 기록 없음(pause 기록 없음)")
    out.append(f"- 끝 기록 없는 에이전트 실행: {no_end}개(시간에 넣지 않음)")
    if mixed:
        out.append("- 관문 답이 안에 들어 있어 AI 작업에서 뺀 단계: " + ", ".join(f"{n} {m:.1f}분" for n, m in mixed))
    return out


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
    human = sum(minutes(s, e) for _, k, s, e in done if k in HUMAN_KINDS)
    agents = sum(minutes(s, e) for _, k, s, e in done if k == "agent")
    total = minutes(first, last) if last else 0.0
    attempts, last_try = {}, {}
    for n, k, s, e in done:
        if k in ("script", "agents"):
            attempts[n] = attempts.get(n, 0) + 1
            last_try[n] = minutes(s, e)
    retried = {n: c for n, c in attempts.items() if c > 1}
    kind_ko = {"agent": "에이전트", "agents": "에이전트 단계", "script": "스크립트", "human": "관문 응답 대기"}
    lines = [f"# 단계별 시간: {run.name}", "",
             "| 단계 | 종류 | 시작 | 끝 | 걸린 분 |", "|---|---|---|---|---|"]
    for n, k, s, e in rows:
        lines.append(f"| {n} | {kind_ko.get(k, k)} | {s:%H:%M:%S} | {e:%H:%M:%S} | {minutes(s, e):.1f} |" if e
                     else f"| {n} | {kind_ko.get(k, k)} | {s:%H:%M:%S} | 끝 기록 없음 | - |")
    notes = [f"- 전체 경과: {total:.1f}분",
             f"- 사람 대기: {human:.1f}분",
             f"- 기계 시간(전체 경과 - 사람 대기): {total - human:.1f}분. 사람 쪽 기록이 빠지면 커지므로, 원래 방식과 비교하는 값은 아래 시간 나눔의 AI 작업입니다.",
             f"- 에이전트 작업 시간 합: {agents:.1f}분. 기계 시간보다 크면 그만큼 병렬로 돌았다는 뜻입니다."]
    if retried:
        notes.append("- 두 번 이상 시작한 단계: " + ", ".join(f"{n} {c}번" for n, c in retried.items())
                     + f". 단계마다 마지막 시도만 더한 기계 시간은 {sum(last_try.values()):.1f}분입니다"
                     " (단계 사이의 짧은 틈은 빠짐).")
    notes += split_section(run, read_jsonl(path), rows)
    (run / "08_timing.md").write_text("\n".join(lines + [""] + notes) + "\n", encoding="utf-8")
    print("\n".join(notes))
    return 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("mode", choices=["mark", "wait", "pause", "report"])
    ap.add_argument("args", nargs="*", help="mark: [회차] start|end|stop <단계 이름>, wait: [회차] start|end <관문>, pause: [회차], report: [회차]")
    ap.add_argument("--kind", default="script", choices=["script", "agents", "human"])
    ap.add_argument("--force", action="store_true", help="사람 쪽 단계나 기다림을 시작 30초 안에 끝으로 찍어야 할 때")
    ap.add_argument("--reason", choices=["limit", "pc_off"], help="pause: 사용량 한도 limit, PC 꺼짐 pc_off")
    ap.add_argument("--calls", type=int, default=None)
    ap.add_argument("--retries", type=int, default=None)
    ap.add_argument("--workers", type=int, default=None)
    a = ap.parse_args()
    if a.mode == "report":
        sys.exit(report(resolve_run(a.args[0] if a.args else None)))
    if a.mode == "pause":
        if not a.reason:
            ap.error("pause에는 --reason limit|pc_off를 주세요.")
        sys.exit(pause(resolve_run(a.args[0] if a.args else None), a.reason))
    if len(a.args) == 2:
        run, (edge, step) = resolve_run(None), a.args
    elif len(a.args) == 3:
        run, edge, step = resolve_run(a.args[0]), a.args[1], a.args[2]
    else:
        ap.error(f"{a.mode}에는 [회차] start|end <이름>을 주세요.")
    if a.mode == "wait":
        if edge not in ("start", "end"):
            ap.error("wait는 start, end 중 하나여야 합니다.")
        sys.exit(wait(run, edge, step, a.force))
    if edge not in STATUS:
        ap.error("start, end, stop 중 하나여야 합니다.")
    sys.exit(mark(run, edge, step, a.kind, a.calls, a.retries, a.workers, a.force))


if __name__ == "__main__":
    main()
