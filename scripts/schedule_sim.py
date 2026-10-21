"""회차 시간 기록으로 단계 순서만 바꿨을 때 회차 길이를 계산한다(2026-10-21 담당자 결정: 순서와 동시 수를 바꾼 고침은 다시 돌리지 않고 셈). 모델을 부르지 않는다.

사용: python scripts/schedule_sim.py <회차> [--pred 단계=앞단계1+앞단계2 ...] [--dur 단계=분 ...]
  timing.jsonl에서 단계마다 처음 시작과 마지막 끝을 읽어 걸린 분을 얻는다. config/stages.yaml의 after를 뒤집어 앞 단계를 만든다.
  모형: 단계는 앞 단계가 모두 끝나면 시작한다(앞 단계가 없으면 실제 시작 시각). 실제 회차에서 앞 단계가 끝난 뒤 늦게 시작한
  만큼(메인 세션이 띄우기까지의 틈)은 그대로 더한다. --pred로 앞 단계를 바꾸고(예: 13_detail_schema_draft=02_schema_draft),
  --dur로 걸린 분을 바꿔 다시 계산한다. 앞 단계를 바꾼 단계의 틈은 LAG_NEW(0.3분)로 둔다. 결과: 실제 끝, 모형 끝(바꾸기 전), 바꾼 뒤 끝, 회차 길이를 정한 줄.
  사람 단계의 기다림도 걸린 분에 들어 있다(AI 작업 시간과 다른 셈이니 차이만 읽는다).
  주의: 실제 틈에는 stages.yaml에 없는 기다림(예: 지시문에만 적힌 순서)도 들어 있다. --tight는 모든 틈을 짧게 둔 이상적인 길이다.
"""
import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from pipeline_io import ROOT, die, load_yaml, resolve_run  # noqa: E402

for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass


LAG_NEW = 0.3   # 분. 앞 단계가 끝나고 메인 세션이 다음을 띄우기까지의 보통 틈(yogamatx5 중간값 근처)


def windows(run):
    ev = [json.loads(l) for l in (run / "timing.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()]
    w = {}
    for e in ev:
        if e.get("event") not in ("step_start", "step_end"):
            continue
        t = datetime.fromisoformat(e["ts"])
        s, x = w.setdefault(e["step"], [None, None])
        if e["event"] == "step_start" and (s is None or t < s):
            w[e["step"]][0] = t
        if e["event"] == "step_end" and (x is None or t > x):
            w[e["step"]][1] = t
    return {k: v for k, v in w.items() if v[0] and v[1]}


def simulate(w, preds, dur, lag, t0):
    """단계마다 (시작, 끝) 분(t0 기준). 앞 단계가 없거나 기록이 없으면 실제 시작."""
    out, order = {}, list(w)

    def go(s, seen=()):
        if s in out:
            return out[s]
        if s in seen:
            die(f"앞 단계가 돌고 돕니다: {s}")
        ps = [p for p in preds.get(s, []) if p in w]
        if ps:
            st = max(go(p, seen + (s,))[1] for p in ps) + lag.get(s, 0.0)
        else:
            st = (w[s][0] - t0).total_seconds() / 60
        out[s] = (st, st + dur[s])
        return out[s]
    for s in order:
        go(s)
    return out


def critical(res, preds):
    end = max(res, key=lambda s: res[s][1])
    line = [end]
    while True:
        ps = [p for p in preds.get(line[-1], []) if p in res]
        if not ps:
            break
        line.append(max(ps, key=lambda p: res[p][1]))
    return list(reversed(line))


def main():
    ap = argparse.ArgumentParser(description="단계 순서만 바꿨을 때 회차 길이")
    ap.add_argument("run", nargs="?")
    ap.add_argument("--pred", action="append", default=[], help="단계=앞단계1+앞단계2(빈 값이면 앞 단계 없음)")
    ap.add_argument("--dur", action="append", default=[], help="단계=분")
    ap.add_argument("--tight", action="store_true", help="모든 단계의 틈을 LAG_NEW로(메인 세션이 바로 띄운다고 칠 때의 회차 길이)")
    a = ap.parse_args()
    run = resolve_run(a.run)
    w = windows(run)
    if not w:
        die("timing.jsonl에 단계 기록이 없습니다.")
    stages = (load_yaml(ROOT / "config" / "stages.yaml") or {}).get("stages") or []
    preds = {}
    for s in stages:
        for nxt in s.get("after") or []:
            preds.setdefault(nxt, []).append(s["id"])
    ids = {s["id"] for s in stages}
    t0 = min(v[0] for v in w.values())
    w = {k: v for k, v in w.items() if k in ids}      # stages.yaml에 없는 기록(10_timing 등)은 회차 끝에 묶여 있어 뺀다
    dur = {s: (v[1] - v[0]).total_seconds() / 60 for s, v in w.items()}
    lag = {}
    for s, v in w.items():
        ps = [p for p in preds.get(s, []) if p in w]
        if ps:
            lag[s] = max(0.0, (v[0] - max(w[p][1] for p in ps)).total_seconds() / 60)
    real_end = (max(v[1] for v in w.values()) - t0).total_seconds() / 60   # stages.yaml 단계의 마지막 끝
    base = simulate(w, preds, dur, lag, t0)
    p2, d2 = {k: list(v) for k, v in preds.items()}, dict(dur)
    lag2 = {k: LAG_NEW for k in lag} if a.tight else dict(lag)
    for x in a.pred:
        k, _, v = x.partition("=")
        p2[k.strip()] = [p for p in v.split("+") if p.strip()]
        lag2[k.strip()] = LAG_NEW      # 실제 틈은 옛 앞 단계에 맞춘 것이라, 앞 단계를 바꾼 단계는 짧은 띄우기 틈만 둔다
    for x in a.dur:
        k, _, v = x.partition("=")
        d2[k.strip()] = float(v)
    new = simulate(w, p2, d2, lag2, t0)
    b_end, n_end = max(e for _, e in base.values()), max(e for _, e in new.values())
    print(f"{run.name}: 실제 끝 {real_end:.1f}분, 모형 끝(바꾸기 전) {b_end:.1f}분, 바꾼 뒤 {n_end:.1f}분(차이 {n_end - b_end:+.1f}분)")
    print("  바꾸기 전 회차 길이를 정한 줄: " + " → ".join(f"{s}({dur[s]:.1f})" for s in critical(base, preds)))
    if a.pred or a.dur or a.tight:
        print("  바꾼 뒤 회차 길이를 정한 줄: " + " → ".join(f"{s}({d2[s]:.1f})" for s in critical(new, p2)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
