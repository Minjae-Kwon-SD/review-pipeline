"""작성자 출력 파일이 다 생길 때까지 기다린다(2026-10-20). 모델을 부르지 않는다.

사용: python scripts/wait_files.py <회차> <파일> [<파일> ...] [--settle 15] [--timeout 1800] [--poll 5]
      python scripts/wait_files.py <회차> --batches 04_batches.json --name "04_tags_sonnet_{batch_id}.jsonl"
  --batches: 묶음 계획 파일의 batches마다 --name 틀로 파일 이름을 만든다(sonnet 묶음만, models에 sonnet이 있는 것). 2026-10-21: 태그 검사가 태거가 아직 쓰는 파일을 검사함
  파일은 회차 폴더 기준 경로. 모두 있고 크기가 settle초 동안 바뀌지 않으면 종료 코드 0, timeout초가 지나면 1(빠진 파일을 적음).
  메인 세션이 작성자들을 띄운 직후 Bash 백그라운드(run_in_background)로 부른다. 끝 알림이 오면 작성자의 끝 보고를
  기다리지 않고 다음 검사(report_parts.py, guide_parts.py)로 간다. yogamatx3-2026-10-20에서 12장 작성자가 12:17에
  파일을 다 쓰고도 끝 보고에 16분을 써, 가이드 감사까지 함께 밀렸다.
"""
import argparse
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from pipeline_io import resolve_run  # noqa: E402

for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass


def sizes(run, files):
    return {f: (run / f).stat().st_size if (run / f).exists() else None for f in files}


def main():
    ap = argparse.ArgumentParser(description="작성자 출력 파일 기다리기")
    ap.add_argument("run")
    ap.add_argument("files", nargs="*")
    ap.add_argument("--batches")
    ap.add_argument("--name", default="04_tags_sonnet_{batch_id}.jsonl")
    ap.add_argument("--settle", type=float, default=15)
    ap.add_argument("--timeout", type=float, default=1800)
    ap.add_argument("--poll", type=float, default=5)
    a = ap.parse_args()
    run = resolve_run(a.run)
    if a.batches:
        import json
        plan = json.loads((run / a.batches).read_text(encoding="utf-8"))
        a.files += [a.name.format(batch_id=b["batch_id"]) for b in plan.get("batches") or [] if "sonnet" in (b.get("models") or ["sonnet"])]
    if not a.files:
        print("기다릴 파일이 없습니다.")
        return 2
    start = time.time()
    last, since = None, None
    while True:
        now = sizes(run, a.files)
        missing = [f for f, s in now.items() if s is None]
        if not missing:
            if now != last:
                last, since = now, time.time()
            if time.time() - since >= a.settle:
                print(f"파일 {len(a.files)}개가 모두 생김({time.time() - start:.0f}초): " + ", ".join(a.files))
                return 0
        else:
            last, since = None, None
        if time.time() - start >= a.timeout:
            print(f"{a.timeout:.0f}초 안에 다 생기지 않음. 빠진 파일: " + (", ".join(missing) or "없음(크기가 계속 바뀜)"))
            return 1
        time.sleep(a.poll)


if __name__ == "__main__":
    sys.exit(main())
