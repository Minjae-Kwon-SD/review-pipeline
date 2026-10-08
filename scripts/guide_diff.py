"""두 판의 가이드 문장(Markdown)에서 바뀐 줄만 18_guide_changed.md로 쓴다(감사가 바뀐 문장만 보게). 모델을 부르지 않는다.

사용: python scripts/guide_diff.py [회차] <옛 파일> <새 파일> [--out 18_guide_changed.md]
    리포트 문장을 고칠 때는 --out 06_report_changed.md처럼 다른 이름으로 쓴다.
"""
import argparse
import difflib
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from pipeline_io import resolve_run  # noqa: E402

for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass


def main():
    ap = argparse.ArgumentParser(description="가이드 문장 바뀐 줄")
    ap.add_argument("run", nargs="?")
    ap.add_argument("old")
    ap.add_argument("new")
    ap.add_argument("--out", default="18_guide_changed.md")
    a = ap.parse_args()
    run = resolve_run(a.run)
    old = (run / a.old).read_text(encoding="utf-8").splitlines()
    new = (run / a.new).read_text(encoding="utf-8").splitlines()
    out = [f"# 바뀐 줄 ({a.old} → {a.new})", ""]
    n = 0
    for tag, i1, i2, j1, j2 in difflib.SequenceMatcher(a=old, b=new, autojunk=False).get_opcodes():
        if tag == "equal":
            continue
        for k in range(i1, i2):
            out.append(f"- 옛 {k + 1}행: {old[k]}")
        for k in range(j1, j2):
            out.append(f"- 새 {k + 1}행: {new[k]}")
            n += 1
    (run / a.out).write_text("\n".join(out) + "\n", encoding="utf-8")
    print(f"바뀐 줄 {n}개 → {a.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
