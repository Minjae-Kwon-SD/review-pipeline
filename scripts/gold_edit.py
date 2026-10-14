"""담당자가 정한 정답 세트 고침 목록을 정답 파일에 그대로 적용한다. 모델을 부르지 않는다.

정답 폴더는 메인 세션과 에이전트가 읽지 못하게 막혀 있어서, 고침은 이 스크립트만 한다. 리뷰 내용은 찍지 않고 개수와 id만 찍는다.

사용:
  python scripts/gold_edit.py <회차> <고침 목록 yaml> [--set rules|score]

고침 목록(yaml):
  sentiment:            # 감성만 바꾸기: [review_id, 주제 id, 원래 감성, 새 감성]
    - [R..., removal_effect, negative, mixed]
  topics:               # 주제 고침. 항목 하나에 ops 여러 개(담당자 목록 한 줄 = 항목 하나)
    - id: R...
      ops:
        - {op: remove, topic: brand_experience, sentiment: positive}
        - {op: ensure, topic: removal_effect, sentiment: positive}        # 없으면 더하기(있으면 그대로)
        - {op: replace, topic: application, sentiment: negative, to_topic: wait_time, to_sentiment: negative}
        - {op: add, topic: scent, sentiment: negative}                     # 같은 주제가 있으면 충돌로 알림
- 원래 값이 목록과 다르면 바꾸지 않고 "맞지 않음"으로 알린다(지어내지 않음).
- 고치기 전 파일을 같은 폴더에 gold_tags.before_<날짜>.jsonl로 남긴다(이미 있으면 덮지 않음).
"""
import argparse
import json
import shutil
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from pipeline_io import SENTIMENTS, die, load_schema, load_yaml, resolve_run  # noqa: E402

for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass

DIRS = {"rules": "gold", "score": "gold_score"}


def main():
    ap = argparse.ArgumentParser(description="정답 세트 고침 목록 적용")
    ap.add_argument("run")
    ap.add_argument("edits")
    ap.add_argument("--set", default="rules", choices=list(DIRS))
    ap.add_argument("--from-backup", action="store_true", help="오늘 만든 고치기 전 사본에서 다시 시작(다시 적용할 때)")
    a = ap.parse_args()
    run = resolve_run(a.run)
    path = run / DIRS[a.set] / "gold_tags.jsonl"
    if not path.exists():
        die(f"{DIRS[a.set]}/gold_tags.jsonl이 없습니다.")
    schema = load_schema(run)
    edits = load_yaml(Path(a.edits))
    backup = path.with_name(f"gold_tags.before_{date.today():%Y-%m-%d}.jsonl")
    src = backup if a.from_backup and backup.exists() else path
    tags = [json.loads(l) for l in src.read_text(encoding="utf-8").splitlines() if l.strip()]
    idx = {(t["review_id"], t["topic"]): t for t in tags}
    problems, applied = [], {"sentiment": 0, "topics": 0, "ops": 0, "no_change": 0}

    def check(topic, sent):
        if topic not in schema:
            die(f"승인 스키마에 없는 주제 {topic}")
        if sent not in SENTIMENTS:
            die(f"감성 값이 아님: {sent}")

    for rid, topic, old, new in edits.get("sentiment") or []:
        check(topic, old)
        check(topic, new)
        t = idx.get((rid, topic))
        if not t:
            problems.append(f"감성 {rid} {topic}: 정답에 이 태그가 없음")
        elif t["sentiment"] != old:
            problems.append(f"감성 {rid} {topic}: 원래 값이 {old}가 아니라 {t['sentiment']}")
        else:
            t["sentiment"] = new
            applied["sentiment"] += 1

    for item in edits.get("topics") or []:
        rid, ok = item["id"], True
        for op in item["ops"]:
            topic, sent = op["topic"], op["sentiment"]
            check(topic, sent)
            cur = idx.get((rid, topic))
            kind = op["op"]
            if kind == "remove":
                if not cur or cur["sentiment"] != sent:
                    problems.append(f"주제 {rid} {topic} {sent} 빼기: " + ("태그가 없음" if not cur else f"감성이 {cur['sentiment']}"))
                    ok = False
                    continue
                tags.remove(cur)
                del idx[(rid, topic)]
            elif kind in ("add", "ensure"):
                if cur:
                    if kind == "ensure" or cur["sentiment"] == sent:
                        applied["no_change"] += 1
                        continue
                    problems.append(f"주제 {rid} {topic} {sent} 더하기: 이미 {cur['sentiment']}로 있음")
                    ok = False
                    continue
                t = {"review_id": rid, "topic": topic, "sentiment": sent}
                tags.append(t)
                idx[(rid, topic)] = t
            elif kind == "replace":
                to_t, to_s = op["to_topic"], op["to_sentiment"]
                check(to_t, to_s)
                if not cur or cur["sentiment"] != sent:
                    problems.append(f"주제 {rid} {topic}->{to_t}: " + ("태그가 없음" if not cur else f"감성이 {cur['sentiment']}"))
                    ok = False
                    continue
                if (rid, to_t) in idx:
                    have = idx[(rid, to_t)]["sentiment"]
                    if have == to_s:                 # 바꿀 자리에 같은 감성으로 이미 있으면, 옮기는 대신 원래 태그만 뺀다(결과가 같음)
                        tags.remove(cur)
                        del idx[(rid, topic)]
                        applied["ops"] += 1
                        applied["merged"] = applied.get("merged", 0) + 1
                        continue
                    problems.append(f"주제 {rid} {topic}->{to_t}: {to_t} 태그가 이미 {have}로 있음")
                    ok = False
                    continue
                del idx[(rid, topic)]
                cur["topic"], cur["sentiment"] = to_t, to_s
                idx[(rid, to_t)] = cur
            else:
                die(f"모르는 op: {kind}")
            applied["ops"] += 1
        applied["topics"] += 1 if ok else 0

    if not backup.exists():
        shutil.copyfile(path, backup)
    order = {}
    for i, t in enumerate(tags):
        order.setdefault(t["review_id"], i)
    tags.sort(key=lambda t: (order[t["review_id"]], t["topic"]))
    path.write_text("".join(json.dumps(t, ensure_ascii=False) + "\n" for t in tags), encoding="utf-8")
    n_s, n_t = len(edits.get("sentiment") or []), len(edits.get("topics") or [])
    print(f"정답 고침: 감성 {applied['sentiment']}/{n_s}개, 주제 항목 {applied['topics']}/{n_t}개(작업 {applied['ops']}개, "
          f"이미 그대로라 안 바꾼 것 {applied['no_change']}개, 바꿀 자리에 같은 값이 있어 원래 태그만 뺀 것 {applied.get('merged', 0)}개). 고치기 전 사본: {DIRS[a.set]}/{backup.name}")
    for p in problems:
        print(f"  맞지 않음(바꾸지 않음): {p}")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
