"""개발 가이드 장 묶음(17_guide_part_<묶음>.md)을 17_guide.md 하나로 합치고 검사한다. 모델을 부르지 않는다(2026-10-17 안 B).

사용: python scripts/guide_parts.py assemble [회차]
      python scripts/guide_parts.py check [회차] --part <묶음> [--early]
      (--early는 01-02-A 미리 쓴 판 17_guide_part_01-02-A_early.md를 검사. assemble은 미리 쓴 판을 읽지 않는다)

묶음(틀 순서와 따로): 01-02-A(라벨 전 미리 씀(_early.md), 라벨 뒤 보강. 미리 쓰지 못하면 라벨 뒤 1차에 final로), 03, 04(라벨 뒤 1차, 같은 때), head-05(라벨 뒤 2차, 제목 줄 # 포함).
합친 순서는 guide-writer.md 장 순서 그대로: # 제목, ## 머리 숫자, ## 01, ## 02, ## 03, ## 04, ## 05, ## A. 표는 가이드에 없으므로(HTML이 소제목 아래 그림) 이어 붙이기만 한다.
FAIL: 묶음 빠짐, 묶음에 맡지 않은 장 제목, 맡은 장 제목 빠짐이나 두 번, 제목 줄(#) 수, 틀 중괄호 남음,
      03 원인 줄과 04 기준 제목이 16_guide_metrics.json의 원인 번호 표(p.causes, std.board[].causes)와 다름,
      방향 지수 [m:키] 문장이 부호와 반대쪽 이름만 씀(예: +0.09인데 '저음 과다 쪽').
경고: 머리 숫자 주제(guide.head_topic)를 1위로 쓰면서 다시 뽑기에서 1위로 남은 비율이 60% 미만인데 '비슷', '같은 수준' 같은 단서가 없는 줄.
결과: 17_guide.md, 17_guide_parts_check.json. 숫자와 출처 검사는 guide_check.py(18)가 한다.
"""
import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from pipeline_io import ROOT, category_conf, load_schema, load_yaml, now_iso, resolve_run, write_json  # noqa: E402

for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass

ORDER = ["머리 숫자", "01", "02", "03", "04", "05", "A"]          # 합친 장 순서
PARTS = {"01-02-A": ["01", "02", "A"], "03": ["03"], "04": ["04"], "head-05": ["머리 숫자", "05"]}
HEDGE = ("비슷", "같은 수준", "사실상", "순위는 정하지", "순위를 정하지", "나란히", "차이가 작", "함께 관문")
MARK = re.compile(r"\[m:([^\]]+)\]")


def part_path(run, name, early=False):
    return run / f"17_guide_part_{name}{'_early' if early else ''}.md"


def chapter_of(line):
    """'## 01 시장 개요' -> '01', '## 머리 숫자' -> '머리 숫자', 장 제목 줄이 아니면 None"""
    if not line.startswith("## "):
        return None
    t = line[3:].strip()
    return "머리 숫자" if t.startswith("머리 숫자") else t.split()[0] if t else ""


def split_chapters(text):
    """[(장, 줄 목록)], 제목 줄(#) 목록, 첫 장 앞의 다른 줄"""
    chs, titles, pre, cur = [], [], [], None
    for line in text.splitlines():
        c = chapter_of(line)
        if c is not None:
            cur = (c, [line])
            chs.append(cur)
        elif line.startswith("# "):
            titles.append(line)
        elif cur:
            cur[1].append(line)
        elif line.strip():
            pre.append(line)
    return chs, titles, pre


def check_part(run, name, early=False):
    p = part_path(run, name, early)
    if not p.exists():
        return [f"묶음 {name}: {p.name} 없음"], [], []
    chs, titles, pre = split_chapters(p.read_text(encoding="utf-8"))
    want, errors = PARTS[name], []
    got = [c for c, _ in chs]
    for c in got:
        if c not in want:
            errors.append(f"묶음 {name}: 맡지 않은 장 '## {c}'")
    for c in want:
        if got.count(c) != 1:
            errors.append(f"묶음 {name}: 장 '## {c}'이 {got.count(c)}번")
    if len(titles) != (1 if name == "head-05" else 0):
        errors.append(f"묶음 {name}: 제목 줄(# ...) {len(titles)}개(head-05에만 하나)")
    if pre and name != "head-05":           # head-05는 제목 줄 뒤 부제(> ...)를 첫 장 앞에 둔다
        errors.append(f"묶음 {name}: 첫 장 제목 앞에 다른 줄: {pre[0][:60]}")
    titles = titles + pre
    for c, lines in chs:
        for ln in lines:
            if re.search(r"\{[^{}\s]{1,20}\}", ln):
                errors.append(f"묶음 {name}: 틀 중괄호가 남음: {ln.strip()[:60]}")
    return errors, chs, titles


def consistency(text, M, conf, schema):
    """장 사이 어긋남: 원인 번호(03 원인 줄, 04 기준 제목)와 방향 지수 부호. 머리 숫자 주제 1위 단정은 경고."""
    errors, warns = [], []
    causes = {c["n"]: c for c in M["tables"].get("p.causes") or []}
    board = M["tables"].get("std.board") or []
    if causes:
        for m in re.finditer(r"원인 (\d+)\((설계 결함|선호 차이)\)", text):
            c = causes.get(int(m.group(1)))
            if not c:
                errors.append(f"03 원인 {m.group(1)}: 원인 번호 표(p.causes)에 없음")
            elif c["type"] != m.group(2):
                errors.append(f"03 원인 {m.group(1)}: '{m.group(2)}'로 씀, 원인 번호 표는 '{c['type']}'")
        for m in re.finditer(r"^#### 기준 (\d+):.*$", text, re.M):
            n = int(m.group(1))
            if not 1 <= n <= len(board):
                errors.append(f"04 기준 {n}: 기준표(std.board)에 없는 번호")
                continue
            want = board[n - 1].get("causes") or []
            got = [int(x) for x in re.findall(r"\d+", (re.search(r"\(원인 ([\d, ]+) 대응\)", m.group(0)) or [None, ""])[1])]
            if sorted(got) != sorted(want):
                errors.append(f"04 기준 {n} 제목의 원인 {got or '없음'}: 원인 번호 표는 {want or '없음(원인 밖)'}")
    di = conf.get("direction_index") or {}
    hi, lo = (di.get("high") or {}).get("name"), (di.get("low") or {}).get("name")
    if hi and lo:
        for line in text.splitlines():
            for seg in re.split(r"(?<=[.다])\s", line):
                for k in MARK.findall(seg):
                    if not (k.endswith(".dir_index") or ".vdir." in k):
                        continue
                    v = (M["values"].get(k) or {}).get("value")
                    if not isinstance(v, (int, float)) or v == 0:
                        continue
                    if "불분명" in str((M["values"].get(k) or {}).get("text", "")):   # 방향 불분명 값은 어느 쪽 방향도 아님(2026-10-17 E4)
                        continue
                    want, other = (hi, lo) if v > 0 else (lo, hi)
                    if other in seg and want not in seg:
                        errors.append(f"방향 [m:{k}] {v:+.2f}인데 '{other}' 쪽으로 씀: {seg.strip()[:70]}")
    hp = (M["values"].get("a.robust.head_first") or {}).get("value")
    tname = (schema.get(conf.get("head_topic")) or {}).get("name_ko")
    if tname and isinstance(hp, (int, float)) and hp < 60:
        for line in text.splitlines():
            if tname in line and re.search(r"단독 1위|가장 많은 약점|주제 중 가장 높", line) and not any(h in line for h in HEDGE):
                warns.append(f"'{tname}' 1위 단정(다시 뽑기 1위 유지 {hp}%): {line.strip()[:70]}")
    return errors, warns


def assemble(run):
    errors, chapters, title = [], {}, None
    for name in PARTS:
        e, chs, titles = check_part(run, name)
        errors += e
        for c, lines in chs:
            if c in PARTS[name]:          # 그 장을 맡은 묶음의 것만 씀(맡지 않은 장은 위에서 FAIL)
                chapters.setdefault(c, lines)
        if name == "head-05" and titles:
            title = titles          # 제목 줄과 부제
    missing = [c for c in ORDER if c not in chapters]
    body = (title or [""]) + [""] + sum(([*chapters[c], ""] if c in chapters else [] for c in ORDER), [])
    text = "\n".join(body).rstrip() + "\n"
    warns = []
    mp = run / "16_guide_metrics.json"
    if mp.exists() and not missing:
        M = json.loads(mp.read_text(encoding="utf-8"))
        cat = run.name.split("-")[0]
        conf = category_conf(run).get("guide") or {}
        e, warns = consistency(text, M, conf, load_schema(run))
        errors += e
    status = "FAIL" if errors or missing else "PASS"
    if not missing:
        (run / "17_guide.md").write_text(text, encoding="utf-8")
    write_json(run / "17_guide_parts_check.json", {"checked_at": now_iso(), "status": status, "parts": list(PARTS),
                                                    "chapters": [c for c in ORDER if c in chapters], "errors": errors, "warnings": warns})
    print(f"가이드 합치기: {status}. 묶음 {len(PARTS)}개, 장 {len(chapters)}개" + (" → 17_guide.md" if not missing else ", 17_guide.md를 쓰지 않음"))
    for e in errors[:30]:
        print(f"  오류: {e}")
    for w in warns[:10]:
        print(f"  경고: {w}")
    return 1 if status == "FAIL" else 0


def main():
    ap = argparse.ArgumentParser(description="개발 가이드 장 묶음 합치기")
    ap.add_argument("cmd", choices=["assemble", "check"])
    ap.add_argument("run", nargs="?")
    ap.add_argument("--part", choices=list(PARTS))
    ap.add_argument("--early", action="store_true", help="01-02-A 미리 쓴 판(_early.md)을 검사")
    a = ap.parse_args()
    run = resolve_run(a.run)
    if a.cmd == "check":
        if not a.part:
            sys.exit("check에는 --part가 필요합니다")
        if a.early and a.part != "01-02-A":
            sys.exit("--early는 --part 01-02-A에만 씁니다")
        errors, _, _ = check_part(run, a.part, a.early)
        print(f"가이드 묶음 검사 {a.part}{' (미리 쓴 판)' if a.early else ''}: {'FAIL' if errors else 'PASS'}")
        for e in errors:
            print(f"  오류: {e}")
        sys.exit(1 if errors else 0)
    sys.exit(assemble(run))


if __name__ == "__main__":
    main()
