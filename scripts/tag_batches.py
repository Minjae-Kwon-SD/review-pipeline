"""5단계: 태깅 묶음 나누기.

사용: python scripts/tag_batches.py plan [회차] [--size 50]
  ASIN마다 리뷰를 date, review_id 순으로 size개씩 나눠 04_batches.json에 쓴다.
  묶음 id는 <ASIN>_<두 자리 번호>(예: B0GFGL26JD_01). ASIN 묶음은 sonnet이 태깅한다(04_tags_sonnet_<묶음>.jsonl).
  정답 세트 리뷰(gold/gold_reviews.csv)만 담은 gold 묶음을 따로 하나 두고, sonnet(04_tags_sonnet_gold.jsonl, 시험 태깅
  점수용)과 상위 모델(04_tags_top_gold.jsonl, 비교용)이 태깅한다. gold 묶음은 04_tags.jsonl에 합치지 않는다.
  정답 세트 리뷰도 ASIN 묶음에 그대로 들어 있어 전체 태깅 뒤에는 04_tags.jsonl에도 있다.
  시험 태깅(pilot)은 리뷰가 가장 적은 ASIN의 묶음과 gold 묶음이다(pilot_batches).
  묶음마다 그 묶음 리뷰만 담은 입력 파일 04_tag_input/<묶음>.csv(02_reviews.csv와 같은 칸, 같은 순서)를 쓴다.
  review-tagger는 02_reviews.csv 전체 대신 이 파일만 읽는다(2026-10-11, 결정 기록 F11 태그 입력 파일 나누기).
"""
import argparse
import csv
import sys
from collections import defaultdict

from pipeline_io import REVIEW_COLS, load_csv_or_die, now_iso, resolve_run, write_json


def write_inputs(run, reviews, batches):
    """묶음마다 04_tag_input/<묶음>.csv. 이전 계획의 파일은 지우고 다시 쓴다."""
    out = run / "04_tag_input"
    out.mkdir(exist_ok=True)
    for old in out.glob("*.csv"):
        old.unlink()
    by_id = {r["review_id"]: r for r in reviews}
    cols = list(reviews[0].keys()) if reviews else list(REVIEW_COLS)
    for b in batches:
        missing = [x for x in b["review_ids"] if x not in by_id]
        if missing:
            sys.exit(f"묶음 {b['batch_id']}의 리뷰 {len(missing)}개가 02_reviews.csv에 없습니다: {', '.join(missing[:5])}")
        with open(out / f"{b['batch_id']}.csv", "w", encoding="utf-8-sig", newline="") as f:
            w = csv.DictWriter(f, fieldnames=cols)
            w.writeheader()
            w.writerows(by_id[x] for x in b["review_ids"])


def plan(run, size):
    reviews = load_csv_or_die(run / "02_reviews.csv", REVIEW_COLS)
    by_asin = defaultdict(list)
    for r in reviews:
        by_asin[r["asin"]].append(r)
    batches = []
    for asin in sorted(by_asin):
        rs = sorted(by_asin[asin], key=lambda r: (r["date"], r["review_id"]))
        for k in range(0, len(rs), size):
            batches.append({"batch_id": f"{asin}_{k // size + 1:02d}", "asin": asin, "models": ["sonnet"],
                            "review_ids": [r["review_id"] for r in rs[k:k + size]]})
    gold_path = run / "gold" / "gold_reviews.csv"
    gold_ids = []
    if gold_path.exists():
        with open(gold_path, encoding="utf-8-sig", newline="") as f:
            gold_ids = [r["review_id"] for r in csv.DictReader(f)]
        # gold 묶음은 시험 태깅에서 sonnet 점수를 바로 내려고 sonnet도 태깅한다. 04_tags.jsonl에는 합치지 않는다(merge false).
        batches.append({"batch_id": "gold", "asin": None, "models": ["sonnet", "top"], "merge": False,
                        "review_ids": gold_ids})
    else:
        print("  주의: gold/gold_reviews.csv가 없어 gold 묶음을 만들지 않았습니다(eval_gold.py pick 먼저).")
    write_inputs(run, reviews, batches)
    pilot_asin = min(by_asin, key=lambda a: (len(by_asin[a]), a)) if by_asin else None
    pilot = [b["batch_id"] for b in batches if b["asin"] == pilot_asin] + (["gold"] if gold_ids else [])
    write_json(run / "04_batches.json", {"planned_at": now_iso(), "size": size, "reviews": len(reviews),
                                         "pilot_asin": pilot_asin, "pilot_batches": pilot, "batches": batches})
    sonnet = [b for b in batches if "sonnet" in b["models"]]
    print(f"묶음 {len(batches)}개를 04_batches.json에 적었습니다(sonnet {len(sonnet)}개, 크기 {size}, "
          f"gold {'1개, 리뷰 ' + str(len(gold_ids)) + '개' if gold_ids else '없음'}).")
    for asin in sorted(by_asin):
        bs = [b for b in sonnet if b["asin"] == asin]
        print(f"  {asin}: 리뷰 {len(by_asin[asin])}개, 묶음 {len(bs)}개 ({', '.join(str(len(b['review_ids'])) for b in bs)})")
    print(f"  시험 태깅: {', '.join(pilot)} (리뷰가 가장 적은 ASIN {pilot_asin})")
    print(f"  묶음 입력 파일 {len(batches)}개를 04_tag_input/에 적었습니다(묶음 리뷰만, 02_reviews.csv와 같은 칸).")
    return 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("mode", choices=["plan"])
    ap.add_argument("run", nargs="?")
    ap.add_argument("--size", type=int, default=50)
    args = ap.parse_args()
    sys.exit(plan(resolve_run(args.run), args.size))


if __name__ == "__main__":
    main()
