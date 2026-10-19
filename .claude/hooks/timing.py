"""SubagentStart, SubagentStop Hook: 에이전트의 시작과 끝을 runs/<CURRENT>/timing.jsonl에 한 줄씩 적는다.

.claude/settings.json에 등록되어 있고, 이 파일을 직접 실행할 일은 없다.
시간 기록이 실패해도 파이프라인을 멈추지 않도록 늘 종료 코드 0으로 끝낸다
(SubagentStop에서 종료 코드 2는 에이전트를 멈추지 못하게 막는다).
"""
import json
import os
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def append_locked(path, line):
    """여러 에이전트가 같은 때 시작하면 Windows의 덧붙이기가 서로 덮어써 줄이 빠지거나 깨진다(2026-10-17 요가 매트 r2).
    옆 잠금 파일을 잡은 동안에만 쓴다. 잠금은 10초까지 기다린다."""
    import time
    lock = path.with_name(path.name + ".lock")
    fd = os.open(lock, os.O_RDWR | os.O_CREAT)
    try:
        if os.name == "nt":
            import msvcrt
            for _ in range(200):
                try:
                    msvcrt.locking(fd, msvcrt.LK_NBLCK, 1)
                    break
                except OSError:
                    time.sleep(0.05)
        else:
            import fcntl
            fcntl.flock(fd, fcntl.LOCK_EX)
        with open(path, "a", encoding="utf-8", newline="\n") as f:
            f.write(line)
            f.flush()
            os.fsync(f.fileno())
    finally:
        if os.name == "nt":
            import msvcrt
            try:
                os.lseek(fd, 0, 0)
                msvcrt.locking(fd, msvcrt.LK_UNLCK, 1)
            except OSError:
                pass
        os.close(fd)


def main():
    try:
        data = json.loads(sys.stdin.buffer.read().decode("utf-8") or "{}")
        current = ROOT / "runs" / "CURRENT"
        if not current.exists():
            return
        run = ROOT / "runs" / current.read_text(encoding="utf-8").strip()
        if not run.is_dir():
            return
        row = {
            "ts": datetime.now().astimezone().isoformat(timespec="seconds"),
            "event": data.get("hook_event_name"),
            "agent_type": data.get("agent_type"),
            "agent_id": data.get("agent_id"),
            "session_id": data.get("session_id"),
        }
        append_locked(run / "timing.jsonl", json.dumps(row, ensure_ascii=False) + "\n")
    except Exception as e:  # 기록 실패는 알리기만 한다
        print(f"timing hook: {e}", file=sys.stderr)


if __name__ == "__main__":
    main()
    sys.exit(0)
