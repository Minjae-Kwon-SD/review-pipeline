"""PreToolUse Hook(2026-10-17 담당자 결정): 하위 에이전트가 지금 회차(runs/CURRENT) 밖의 회차 폴더와
시험 기록(docs/experiments_*.md, docs/decisions_log.md, _experiments/)을 열지 못하게 막는다.

- 메인 세션의 호출(agent_id 없음)은 막지 않는다(회차 비교를 메인 세션이 함).
- Read: file_path, Grep/Glob: path와 pattern, Bash: command 문자열을 본다.
- Grep/Glob에서 path가 없거나 저장소 맨 위, runs/ 자체면 다른 회차까지 훑으므로 막고 path를 지금 회차로 주라고 알린다.
- 막을 때는 permissionDecision deny와 이유를 돌려준다. 그 밖의 오류는 막지 않고 넘긴다(종료 코드 0).
- 막은 기록은 runs/<CURRENT>/guard_log.jsonl에 한 줄씩 남긴다(2026-10-19, 대시보드의 금지 파일 감시가 읽음).
"""
import json
import re
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BLOCK_DOCS = (re.compile(r"(^|/)docs/experiments_[^/]*\.md$"), re.compile(r"(^|/)docs/decisions_log\.md$"),
              re.compile(r"(^|/)_experiments(/|$)"))
RUN_RE = re.compile(r"(?:^|/)runs/([^/*?\[\]]+)")


def norm(p):
    return str(p).replace("\\", "/")


def current_run():
    c = ROOT / "runs" / "CURRENT"
    return c.read_text(encoding="utf-8").strip() if c.exists() else None


def rel(p):
    s = norm(p)
    r = norm(ROOT)
    if s.lower().startswith(r.lower()):
        s = s[len(r):].lstrip("/")
    return s


def bad_path(p, cur):
    """막을 이유 문자열, 괜찮으면 None"""
    s = rel(p)
    for rx in BLOCK_DOCS:
        if rx.search(s):
            return f"시험 기록 파일({s})은 하위 에이전트가 열지 않는다"
    for m in RUN_RE.finditer(s):
        name = m.group(1)
        if name not in (cur, "CURRENT"):
            return f"다른 회차 폴더(runs/{name})는 열지 않는다. 지금 회차는 runs/{cur}"
    return None


def decide(data):
    if not data.get("agent_id"):          # 메인 세션
        return None
    cur = current_run()
    if not cur:
        return None
    tool, inp = data.get("tool_name"), data.get("tool_input") or {}
    if tool == "Read":
        return bad_path(inp.get("file_path", ""), cur)
    if tool in ("Grep", "Glob"):
        for k in ("path", "pattern", "glob"):
            if inp.get(k):
                why = bad_path(inp[k], cur)
                if why:
                    return why
        path = (inp.get("path") or "").strip()
        base = rel(path).rstrip("/") if path else ""
        if not path or base in ("", ".", "runs"):
            return f"{tool}는 path를 지금 회차(runs/{cur}/)나 config/, .claude/, scripts/로 좁혀 부른다(저장소 전체를 훑으면 다른 회차가 섞임)"
        return None
    if tool == "Bash":
        cmd = norm(inp.get("command", ""))
        for name in re.findall(r"runs/([A-Za-z0-9_.-]+)", cmd):
            if name not in (cur, "CURRENT"):
                return f"다른 회차 폴더(runs/{name})는 열지 않는다"
        if re.search(r"experiments_|decisions_log|_experiments", cmd):
            return "시험 기록 파일은 하위 에이전트가 열지 않는다"
    return None


def log_hit(data, why):
    """막은 호출을 지금 회차의 guard_log.jsonl에 적는다. 실패해도 막는 것은 그대로 한다."""
    try:
        cur = current_run()
        run = ROOT / "runs" / cur if cur else None
        if not run or not run.is_dir():
            return
        inp = data.get("tool_input") or {}
        target = inp.get("file_path") or inp.get("path") or inp.get("pattern") or inp.get("command") or ""
        row = {"ts": datetime.now().astimezone().isoformat(timespec="seconds"), "agent_type": data.get("agent_type"),
               "agent_id": data.get("agent_id"), "tool": data.get("tool_name"), "target": rel(target)[:300], "reason": why}
        with open(run / "guard_log.jsonl", "a", encoding="utf-8", newline="\n") as f:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")
    except Exception as e:
        print(f"guard hook log: {e}", file=sys.stderr)


def main():
    try:
        data = json.loads(sys.stdin.buffer.read().decode("utf-8") or "{}")
        why = decide(data)
        if why:
            log_hit(data, why)
            out = json.dumps({"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": "deny",
                                                     "permissionDecisionReason": why}}, ensure_ascii=False)
            sys.stdout.buffer.write((out + "\n").encode("utf-8"))   # Windows 파이프 기본 인코딩(cp949)을 피함
    except Exception as e:
        print(f"guard hook: {e}", file=sys.stderr)


if __name__ == "__main__":
    main()
    sys.exit(0)
