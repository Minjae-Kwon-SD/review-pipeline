"""5단계: 태깅 묶음 나누기.

사용: python scripts/tag_batches.py plan [회차] [--size 50]
  ASIN마다 리뷰를 date, review_id 순으로 size개씩 나눠 04_batches.json에 쓴다.
  묶음 id는 <ASIN>_<두 자리 번호>(예: B0GFGL26JD_01). ASIN 묶음은 sonnet이 태깅한다(04_tags_sonnet_<묶음>.jsonl).
  정답 세트 리뷰(gold/gold_reviews.csv)만 담은 gold 묶음을 따로 하나 두고, sonnet(04_tags_sonnet_gold.jsonl, 시험 태깅
  점수용)과 상위 모델(04_tags_top_gold.jsonl, 비교용)이 태깅한다. gold 묶음은 04_tags.jsonl에 합치지 않는다.
  정답 세트 리뷰도 ASIN 묶음에 그대로 들어 있어 전체 태깅 뒤에는 04_tags.jsonl에도 있다.
  시험 태깅(pilot)은 리뷰가 가장 적은 ASIN의 묶음과 gold 묶음이다(pilot_batches).
"""
import argparse
import csv
import sys
from collections import defaultdict

from pipeline_io import REVIEW_COLS, load_csv_or_die, now_iso, resolve_run, write_json


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
