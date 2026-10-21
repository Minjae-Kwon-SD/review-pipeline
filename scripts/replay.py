"""끝난 회차를 복사해 고른 단계만 다시 돌릴 준비를 한다(2026-10-21 담당자 결정: 고친 단계만 다시 돌려 토큰을 아낌). 모델을 부르지 않는다.

사용: python scripts/replay.py <원본 회차 폴더> <새 회차 이름> --from <단계[,단계]> [--only] [--set-current]
  원본 회차를 runs/<새 회차 이름>/으로 복사하고, 고른 단계(--only가 없으면 config/stages.yaml의 after를 따라 그 뒤 단계 전부)의
  출력 파일만 지운다. state.json에서 그 단계들을 지워 stage_plan.py plan이 다시 할 단계로 고르게 한다.
  새 회차 이름의 첫 부분(카테고리)은 원본과 같아야 한다. 원본 저장소의 config/categories/<카테고리>.yaml이 이 저장소에 없으면 복사한다.
  복사하지 않는 것: gold/, gold_score/(정답지는 담당자가 복사), timing.jsonl, 08_timing.md, guard_log.jsonl(다시 돌린 시간만 새로 잼).
  --set-current: runs/CURRENT를 새 회차로 바꾼다(guard_runs.py가 하위 에이전트를 CURRENT 회차로만 묶으므로). 이전 값을 알린다.
  결과 기록: runs/<새 회차>/replay_info.json(원본, 다시 할 단계, 지운 파일).
"""
import argparse
import fnmatch
import json
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from pipeline_io import ROOT, die, load_yaml, now_iso, write_json  # noqa: E402

for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass

SKIP_TOP = {"gold", "gold_score", "timing.jsonl", "timing.jsonl.lock", "08_timing.md", "guard_log.jsonl", "replay_info.json"}
# stages.yaml outputs에 없는 판(v1, 고치기, 반쪽)도 그 단계와 함께 지운다
EXTRA = {
    "05_tagging": ["04_tags_*_*.jsonl"],
    "06_tag_check": ["04_tag_audit_*.yaml", "04_audit_sample*.jsonl", "04_quote_check_*.json", "04_negation_check.json", "04_gold_eval.*"],
    "08_report": ["06_report_part_*.md", "06_report_conclusions.yaml", "06_report_concl_packet.md"],
    "09_report_check": ["07_audit*.yaml", "06_report_v*.md", "06_report_changed.md", "07_quote_check.json"],
    "17_guide_write": ["17_guide_v*.md", "17_guide_part_*.md"],
    "18_guide_check": ["18_guide_audit*.yaml", "18_guide_changed.md", "18_guide_quote_check.json"],
}


def downstream(stages, start):
    after = {s["id"]: s.get("after") or [] for s in stages}
    out, todo = [], list(start)
    while todo:
        s = todo.pop(0)
        if s in out:
            continue
        out.append(s)
        todo += after.get(s, [])
    return out


def main():
    ap = argparse.ArgumentParser(description="끝난 회차를 복사해 고른 단계만 다시")
    ap.add_argument("source")
    ap.add_argument("name")
    ap.add_argument("--from", dest="start", required=True, help="다시 할 첫 단계(쉼표로 여럿)")
    ap.add_argument("--only", action="store_true", help="뒤 단계는 두고 고른 단계만 다시")
    ap.add_argument("--set-current", action="store_true")
    ap.add_argument("--dest", help="새 회차를 만들 runs 폴더(기본 이 저장소의 runs, 시험용)")
    a = ap.parse_args()
    src = Path(a.source).resolve()
    if not (src / "state.json").exists():
        die(f"끝난 회차 폴더가 아닙니다(state.json 없음): {src}")
    cat = src.name.split("-")[0]
    if a.name.split("-")[0] != cat:
        die(f"새 회차 이름의 첫 부분이 원본 카테고리({cat})와 같아야 합니다: {a.name}")
    dst = (Path(a.dest) if a.dest else ROOT / "runs") / a.name
    if dst.exists():
        die(f"이미 있는 회차입니다: {dst}")
    stages = (load_yaml(ROOT / "config" / "stages.yaml") or {}).get("stages") or []
    ids = {s["id"] for s in stages}
    start = [x.strip() for x in a.start.split(",") if x.strip()]
    bad = [x for x in start if x not in ids]
    if bad:
        die(f"stages.yaml에 없는 단계: {bad}")
    redo = start if a.only else downstream(stages, start)
    pats = []
    for s in stages:
        if s["id"] in redo:
            pats += list(s.get("outputs") or []) + EXTRA.get(s["id"], [])

    def skip(d, names):
        return [n for n in names if Path(d) == src and n in SKIP_TOP]
    shutil.copytree(src, dst, ignore=skip)
    removed = []
    for p in sorted(dst.rglob("*")):
        if p.is_file():
            rel = p.relative_to(dst).as_posix()
            if any(fnmatch.fnmatch(rel, pt) for pt in pats):
                p.unlink()
                removed.append(rel)
    st = json.loads((dst / "state.json").read_text(encoding="utf-8"))
    st["run"] = a.name
    for s in redo:
        (st.get("steps") or {}).pop(s, None)
    write_json(dst / "state.json", st)
    (dst / "gold").mkdir(exist_ok=True)
    cfg_src = src.parents[1] / "config" / "categories" / f"{cat}.yaml"
    cfg_dst = ROOT / "config" / "categories" / f"{cat}.yaml"
    copied_cfg = False
    if not a.dest and not cfg_dst.exists() and cfg_src.exists():
        shutil.copyfile(cfg_src, cfg_dst)
        copied_cfg = True
    write_json(dst / "replay_info.json", {"made_at": now_iso(), "source": str(src), "start": start, "only": a.only,
                                          "redo": redo, "removed": removed, "copied_category_config": copied_cfg})
    print(f"{src.name} → runs/{a.name}: 다시 할 단계 {len(redo)}개({', '.join(redo)}), 지운 파일 {len(removed)}개"
          + (f", 품목 설정 config/categories/{cat}.yaml 복사" if copied_cfg else ""))
    print("  정답지(gold/)는 복사하지 않았습니다. 채점이 필요하면 담당자가 복사합니다.")
    if a.set_current:
        cur = ROOT / "runs" / "CURRENT"
        old = cur.read_text(encoding="utf-8").strip() if cur.exists() else ""
        cur.write_text(a.name + "\n", encoding="utf-8")
        print(f"  runs/CURRENT: {old} → {a.name}(끝나면 되돌릴 것)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
