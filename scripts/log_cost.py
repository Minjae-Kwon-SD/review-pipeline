"""headless 실행 한 번의 시간과 비용을 회차의 costs.jsonl에 한 줄로 남긴다.

사용: python scripts/log_cost.py <회차> <claude -p --output-format json 결과 파일>
  결과 JSON에서 duration_ms, total_cost_usd, num_turns만 꺼내고, state.json에서 멈춘 단계
  (needs_human이나 running인 마지막 단계)를 함께 적는다. 결과 파일의 다른 내용은 옮기지 않는다.
"""
import json
import sys

from pipeline_io import die, now_iso, resolve_run


def stopped_step(run):
    path = run / "state.json"
    if not path.exists():
        return None
    steps = json.loads(path.read_text(encoding="utf-8")).get("steps", {})
    pending = [k for k, v in steps.items() if v.get("status") in ("needs_human", "running")]
    return pending[-1] if pending else (list(steps)[-1] if steps else None)


def main():
    if len(sys.argv) != 3:
        die("사용: python scripts/log_cost.py <회차> <결과 JSON 파일>")
    run = resolve_run(sys.argv[1])
    raw = open(sys.argv[2], encoding="utf-8-sig").read().strip()
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        data = json.loads(raw.splitlines()[-1])
    row = {"logged_at": now_iso(), "stopped_at": stopped_step(run),
           "duration_ms": data.get("duration_ms"), "total_cost_usd": data.get("total_cost_usd"),
           "num_turns": data.get("num_turns"), "is_error": data.get("is_error"), "subtype": data.get("subtype")}
    with open(run / "costs.jsonl", "a", encoding="utf-8") as f:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")
    print(json.dumps(row, ensure_ascii=False))


if __name__ == "__main__":
    main()
