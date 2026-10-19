"""리뷰 리포트를 장 묶음으로 나눠 쓴 파일을 틀 순서로 합치고 표를 끼운다. 모델을 부르지 않는다(2026-10-16).

사용:
  python scripts/report_parts.py assemble [회차]
    report-writer가 장 묶음마다 쓴 06_report_part_<묶음>.md(묶음 이름 1-7, 8, 9, 10, 11, 12, appendix)를 틀 순서로 이어 붙이고,
    '{{표: 이름}}' 줄 자리에 05_tables.md의 같은 이름 블록(여는 주석 줄부터 닫는 주석 줄까지)을 글자 그대로 넣어 06_report.md를 쓴다.
    묶음 파일 빠짐, 다른 묶음의 장 제목, 표를 직접 붙임, 틀 중괄호 남음, 05_tables.md에 없는 표 이름, 자리가 없는 표 블록은 FAIL
    (06_report.md를 쓰지 않음). 05_metrics_early.json(라벨 전 미리 쓰기용)이 있으면 두 가지를 대조한다: 미리 쓴 묶음(1-7, 9)이 쓰는 표 블록이
    05_tables_early.md와 05_tables.md에서 글자 그대로 같은지, 라벨에 기대는 값(세부 이슈, 안전, 견고성, 변형 신호)을 뺀 숫자가 같은지.
    다르면 FAIL이고 다른 표와 키를 보여 준다(미리 쓴 장을 `입력: final`로 다시 써야 함). 결과는 06_report_parts_check.json.
    11장은 변형 신호의 방향 지수와 합친 방향 표가 세부 이슈 라벨로 계산되므로 미리 쓰지 않는다(2026-10-16 스피커 회차로 확인).
  python scripts/report_parts.py check [회차] --part <묶음>
    묶음 파일 하나만 본다(제 장 제목만 있는지, 표를 직접 붙이지 않았는지, 틀 중괄호가 남지 않았는지, 표 이름이 05_tables(_early).md에 있는지).
"""
import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from pipeline_io import resolve_run, write_json  # noqa: E402

for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass

# 묶음 이름 -> 그 묶음이 담는 장(틀 순서). appendix는 '## 부록'. 1-7은 리포트 제목(# ...)과 머리말도 담는다.
PARTS = [("1-7", [1, 2, 3, 4, 5, 6, 7]), ("8", [8]), ("9", [9]), ("10", [10]), ("11", [11]), ("12", [12]), ("appendix", ["부록"])]
EARLY = ("1-7", "9")             # 세부 이슈 라벨이 필요 없어 태깅 검사 뒤 바로 쓰는 묶음
LATE = ("8", "10", "11", "12", "appendix")
# early와 final 05_metrics.json을 대조할 때 빼는 키(라벨 뒤에만 생기거나 라벨로 바뀌는 값, 매번 바뀌는 값).
# 스피커 회차(2026-10-16)에서 라벨 전후로 달라진 것은 이 키들뿐이었다. 쓰는 장(8, 10, 11, 12, 부록)은 모두 라벨 뒤에 쓴다.
LABEL_KEYS = {"issues", "issue_overlap", "safety_check", "robustness", "generated_at", "top_issues", "variant_signal", "variant_signals",
              "top_rank_text", "top_tie", "safety_action"}   # 2026-10-17 E2: 견고성과 07b 라벨로 정하는 표기
PLACEHOLDER = re.compile(r"^\{\{표:\s*(.+?)\s*\}\}[ \t]*$", re.M)
BLOCK = re.compile(r"<!-- 표:(.+?) -->.*?<!-- /표:\1 -->", re.S)
CHAPTER = re.compile(r"^## (\d+)\. ", re.M)


def part_path(run, name):
    return run / f"06_report_part_{name}.md"


def chapters_in(text):
    got = {int(m.group(1)) for m in CHAPTER.finditer(text)}
    if re.search(r"^## 부록", text, re.M):
        got.add("부록")
    return got


def table_blocks(path):
    if not path.exists():
        return {}
    return {m.group(1).strip(): m.group(0) for m in BLOCK.finditer(path.read_text(encoding="utf-8"))}


def check_part(name, text, table_names=None):
    """묶음 파일 하나의 오류 목록."""
    want = dict(PARTS).get(name)
    errors = []
    if want is None:
        return [f"{name}: 모르는 묶음 이름(1-7, 8, 9, 10, 11, 12, appendix 중 하나)"]
    got = chapters_in(text)
    if got != set(want):
        errors.append(f"{name}: 장 제목이 맞지 않음(있음 {sorted(map(str, got))}, 있어야 함 {sorted(map(str, want))})")
    if name == "1-7" and not re.search(r"^# ", text, re.M):
        errors.append("1-7: 리포트 제목(# ...)과 머리말이 없음")
    if "<!-- 표:" in text:
        errors.append(f"{name}: 표를 직접 붙였음(<!-- 표: 가 있음). {{{{표: 이름}}}} 줄을 그대로 두어야 함")
    rest = PLACEHOLDER.sub("", text)
    for i, line in enumerate(rest.splitlines(), 1):
        if "{" in line or "}" in line:
            errors.append(f"{name}: {i}번째 줄에 틀 중괄호가 남음: {line.strip()[:60]}")
            break
    if table_names is not None:
        for m in PLACEHOLDER.finditer(text):
            if m.group(1).strip() not in table_names:
                errors.append(f"{name}: 표 '{m.group(1).strip()}'이(가) 표 파일에 없음")
    return errors


def strip_label_keys(o):
    if isinstance(o, dict):
        return {k: strip_label_keys(v) for k, v in o.items() if k not in LABEL_KEYS}
    if isinstance(o, list):
        return [strip_label_keys(v) for v in o]
    return o


def compare_tables(run, texts):
    """미리 쓴 묶음이 쓰는 표 블록이 05_tables_early.md와 05_tables.md에서 같은지. 다른 표 이름 목록(early 파일이 없으면 빈 목록)."""
    early = table_blocks(run / "05_tables_early.md")
    if not early:
        return []
    final = table_blocks(run / "05_tables.md")
    used = {m.group(1).strip() for n in EARLY if n in texts for m in PLACEHOLDER.finditer(texts[n])}
    return sorted(nm for nm in used if early.get(nm) != final.get(nm))


def compare_metrics(run):
    """05_metrics_early.json이 있으면 라벨에 기대지 않는 값이 05_metrics.json과 같은지. (대조했는지, 다른 최상위 키들)"""
    early, final = run / "05_metrics_early.json", run / "05_metrics.json"
    if not early.exists() or not final.exists():
        return False, []
    a = strip_label_keys(json.loads(early.read_text(encoding="utf-8")))
    b = strip_label_keys(json.loads(final.read_text(encoding="utf-8")))
    return True, sorted(k for k in set(a) | set(b) if a.get(k) != b.get(k))


def assemble(run):
    errors, texts = [], {}
    blocks = table_blocks(run / "05_tables.md")
    if not blocks:
        errors.append("05_tables.md가 없거나 표 블록이 없음")
    for name, _ in PARTS:
        p = part_path(run, name)
        if not p.exists():
            errors.append(f"묶음 파일 없음: {p.name}")
            continue
        texts[name] = p.read_text(encoding="utf-8")
        errors += check_part(name, texts[name], set(blocks) if blocks else None)
    compared, diffs = compare_metrics(run)
    if diffs:
        errors.append("05_metrics_early.json과 05_metrics.json의 라벨에 기대지 않는 값이 다름: " + ", ".join(diffs)
                      + " (이 값을 쓴 미리 쓴 장을 `입력: final`로 다시 써 주세요)")
    tdiff = compare_tables(run, texts)
    if tdiff:
        errors.append("미리 쓴 장이 쓰는 표가 라벨 전후로 다름: " + ", ".join(tdiff) + " (그 장을 `입력: final`로 다시 써 주세요)")
    body = "\n\n".join(texts[n].rstrip("\n") for n, _ in PARTS if n in texts) + "\n"
    used = set()

    def put(m):
        nm = m.group(1).strip()
        if nm in blocks:
            used.add(nm)
            return blocks[nm]
        return m.group(0)

    out = PLACEHOLDER.sub(put, body)
    left = [m.group(1).strip() for m in PLACEHOLDER.finditer(out)]
    if left:
        errors.append("표 자리가 남음: " + ", ".join(left))
    for nm in blocks:
        if nm not in used:
            errors.append(f"표 블록 '{nm}'의 자리({{{{표: {nm}}}}})가 묶음 파일에 없음")
    result = {"status": "FAIL" if errors else "PASS", "parts": [n for n, _ in PARTS if n in texts],
              "tables_inserted": sorted(used), "metrics_compared": compared, "metrics_diff_keys": diffs,
              "early_table_diff": tdiff, "errors": errors}
    write_json(run / "06_report_parts_check.json", result)
    if errors:
        print(f"리포트 합치기: FAIL ({len(errors)}개)")
        for e in errors:
            print(f"  오류: {e}")
        return 1
    (run / "06_report.md").write_text(out, encoding="utf-8")
    print(f"리포트 합치기: PASS. 묶음 {len(texts)}개, 표 {len(used)}개 끼움"
          + (", early와 final 숫자 같음" if compared else "") + " → 06_report.md")
    return 0


def check(run, name):
    p = part_path(run, name)
    if not p.exists():
        print(f"묶음 파일 없음: {p.name}")
        return 1
    names = set(table_blocks(run / "05_tables.md")) | set(table_blocks(run / "05_tables_early.md"))
    errors = check_part(name, p.read_text(encoding="utf-8"), names or None)
    if errors:
        print(f"{p.name}: FAIL")
        for e in errors:
            print(f"  오류: {e}")
        return 1
    print(f"{p.name}: PASS")
    return 0


def main():
    ap = argparse.ArgumentParser(description="리포트 장 묶음 합치기와 검사")
    ap.add_argument("mode", choices=["assemble", "check"])
    ap.add_argument("run", nargs="?")
    ap.add_argument("--part", help="check: 묶음 이름(1-7, 8, 9, 10, 11, 12, appendix)")
    a = ap.parse_args()
    run = resolve_run(a.run)
    if a.mode == "check":
        if not a.part:
            ap.error("check에는 --part <묶음>을 주세요.")
        sys.exit(check(run, a.part))
    sys.exit(assemble(run))


if __name__ == "__main__":
    main()
