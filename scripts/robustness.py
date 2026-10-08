"""견고성 점검: 머리 결론이 표본의 우연이나 상품 하나에 기대고 있지 않은지 본다. 모델을 부르지 않는다.

사용:
  python scripts/robustness.py [회차] [--n 2000] [--seed 7]
    (1) 다시 뽑기: ASIN마다 그 ASIN의 리뷰를 같은 수만큼 복원 추출해 n번 다시 계산한다(난수 씨앗 고정).
        - 머리 주제(config guide.head_topic)가 부정 언급 리뷰어(가중) 1위로 남는 비율
        - 머리 주제 부정 언급 리뷰어(가중)의 95% 구간(2.5%, 97.5% 백분위)
        - 머리 주제가 가장 큰 약점인 ASIN 수의 분포와, 다시 뽑기의 95% 이상을 덮는 가장 좁은 범위
    (2) 상품 하나씩 빼기: ASIN마다 그 ASIN을 빼고 머리 주제 부정 리뷰어 비율, 불만 1위와 2위, 최대 약점 상품 수,
        약한 쪽 대 센 쪽 라벨 리뷰 수(config guide.direction_index), 불만 지도 상위 3개를 다시 계산한다.
        뒤집힘: 머리 주제가 1위가 아님, 약한 쪽이 절반 이하, 최대 약점 상품이 남은 상품의 과반이 아님.
    가중치는 리뷰마다 원래 표본에서 정한 값을 그대로 쓴다(가중치는 ASIN 안에서 정해지므로 상품을 빼도 다른 ASIN의 값은 같고,
    다시 뽑기에서는 근사). 계산 규칙은 weight.py와 같다(주제 비교에서 전체 만족도 제외, 최대 약점은 언급 --strength-min개 이상인 주제 중
    부정 언급 리뷰어 비율이 가장 높은 주제, 같으면 부정 언급 수). '빼지 않음'과 '다시 뽑지 않음' 값이 05_metrics.json과 같은지 스스로 확인한다.
    출력: 05_robustness.json. weight.py가 metrics의 robustness로, guide_metrics.py가 가이드 A장 표로 쓴다.
"""
import argparse
import json
import random
import sys
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from issues import review_weights  # noqa: E402
from pipeline_io import ROOT, die, load_schema, load_yaml, now_iso, read_jsonl, resolve_run, write_json  # noqa: E402

for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass

EXCLUDE = ("overall",)


def r1(x):
    return round(x, 1)


class Data:
    def __init__(self, run, strength_min):
        self.run = run
        cat = run.name.split("-")[0]
        self.conf = (load_yaml(ROOT / "config" / "categories" / f"{cat}.yaml") or {})["guide"]
        self.schema = load_schema(run)
        self.reviews, self.weight = review_weights(run)
        tags = [t for t in read_jsonl(run / "04_tags.jsonl")]
        off = {t["review_id"] for t in tags if t["topic"] == "off_category"}
        self.reviews = [r for r in self.reviews if r["review_id"] not in off]
        self.asin_of = {r["review_id"]: r["asin"] for r in self.reviews}
        self.tags = [t for t in tags if t["review_id"] in self.asin_of and t["topic"] != "off_category"]
        self.topics = [t for t in self.schema if t not in EXCLUDE]
        self.name = {t: self.schema[t]["name_ko"] for t in self.schema}
        self.neg = defaultdict(set)           # 리뷰 -> 부정으로 언급한 주제
        self.ment = defaultdict(Counter)      # 리뷰 -> 주제 언급 수
        for t in self.tags:
            self.ment[t["review_id"]][t["topic"]] += 1
            if t["sentiment"] == "negative":
                self.neg[t["review_id"]].add(t["topic"])
        self.by_asin = defaultdict(list)
        for r in self.reviews:
            self.by_asin[r["asin"]].append(r["review_id"])
        self.strength_min = strength_min
        di = self.conf["direction_index"]
        labs = read_jsonl(run / "07b_issue_labels.jsonl")
        self.low = {x["review_id"] for x in labs if set(x["labels"]) & set(di["low"]["labels"])}
        self.high = {x["review_id"] for x in labs if set(x["labels"]) & set(di["high"]["labels"])}
        self.di = di
        self.head = self.conf["head_topic"]

    def neg_pct(self, ids):
        """주제마다 부정 언급 리뷰어(가중) %. ids는 중복을 허용한다(다시 뽑기)."""
        tw = sum(self.weight[i] for i in ids)
        acc = defaultdict(float)
        for i in ids:
            for t in self.neg[i]:
                acc[t] += self.weight[i]
        return {t: 100.0 * acc[t] / tw if tw else 0.0 for t in self.topics}

    def worst(self, ids):
        """한 ASIN의 가장 큰 약점(weight.py 7장과 같은 규칙)"""
        tw = sum(self.weight[i] for i in ids)
        ment, negw, negn = Counter(), defaultdict(float), Counter()
        for i in ids:
            for t, n in self.ment[i].items():
                ment[t] += n
            for t in self.neg[i]:
                negw[t] += self.weight[i]
                negn[t] += 1
        cand = [t for t in self.topics if ment[t] >= self.strength_min]
        if not cand:
            return None
        best = max(cand, key=lambda t: (round(100.0 * negw[t] / tw, 1) if tw else 0.0, negn[t]))
        return best if negw[best] > 0 else None


def bootstrap(D, n, seed):
    rng = random.Random(seed)
    first, vals, weak = 0, [], Counter()
    for _ in range(n):
        samp = {a: [rng.choice(ids) for _ in ids] for a, ids in D.by_asin.items()}
        ids = [i for v in samp.values() for i in v]
        p = D.neg_pct(ids)
        order = sorted(D.topics, key=lambda t: (-p[t], t))
        first += order[0] == D.head
        vals.append(p[D.head])
        weak[sum(D.worst(v) == D.head for v in samp.values())] += 1
    vals.sort()
    lo, hi = vals[int(n * 0.025)], vals[min(n - 1, int(n * 0.975))]
    # 95% 이상을 덮는 가장 좁은 연속 범위(같은 폭이면 더 많이 덮는 쪽)
    ks = sorted(weak)
    best = None
    for i, a in enumerate(range(min(ks), max(ks) + 1)):
        for b in range(a, max(ks) + 1):
            cover = sum(weak[k] for k in range(a, b + 1)) / n
            if cover >= 0.95:
                cand = (b - a, -cover, a, b, cover)
                best = cand if best is None or cand < best else best
                break
    return {"n": n, "seed": seed, "head_first_pct": r1(100.0 * first / n), "head_neg_ci": [r1(lo), r1(hi)],
            "weakest_dist": {str(k): r1(100.0 * weak[k] / n) for k in sorted(weak)},
            "weakest_range": [best[2], best[3]], "weakest_range_cover": r1(100.0 * best[4])}


def leave_one_out(D):
    rows = []
    weak_of = {a: D.worst(ids) for a, ids in D.by_asin.items()}
    for out in [None] + sorted(D.by_asin):
        ids = [i for a, v in D.by_asin.items() if a != out for i in v]
        idset = set(ids)
        p = D.neg_pct(ids)
        order = sorted(D.topics, key=lambda t: (-p[t], t))
        remain = len(D.by_asin) - (out is not None)
        weakest = sum(1 for a, w in weak_of.items() if a != out and w == D.head)
        low, high = len(D.low & idset), len(D.high & idset)
        share = r1(100.0 * low / (low + high)) if low + high else None
        flips = []
        if order[0] != D.head:
            flips.append(f"불만 1위가 {D.name[order[0]]}로 바뀜")
        if share is not None and share <= 50:
            flips.append(f"{D.di['low']['name']} 쪽이 절반 이하")
        if weakest * 2 <= remain:
            flips.append("최대 약점 상품이 과반 아님")
        rows.append({"out": out, "reviews": len(ids), "head_neg": r1(p[D.head]), "first": order[0], "first_pct": r1(p[order[0]]),
                     "second": order[1], "second_pct": r1(p[order[1]]), "weakest": weakest, "remain": remain,
                     "low": low, "high": high, "low_share": share, "top3": order[:3], "flips": flips})
    base = rows[0]["top3"]
    for r in rows[1:]:
        r["top3_changed"] = r["top3"] != base
    return rows, weak_of


def run_all(run, n, seed, strength_min):
    D = Data(run, strength_min)
    loo, weak_of = leave_one_out(D)
    m = json.loads((run / "05_metrics.json").read_text(encoding="utf-8")) if (run / "05_metrics.json").exists() else None
    if m:   # 자체 검사: 다시 뽑지 않은 값이 metrics와 같아야 한다
        t = next(x for x in m["topics"] if x["id"] == D.head)
        mw = {a["asin"]: (a.get("weakness") or {}).get("id") for a in m["asins"]}
        if loo[0]["head_neg"] != t["neg_reviewer_pct"]:
            die(f"머리 주제 부정 리뷰어 비율이 metrics와 다릅니다: {loo[0]['head_neg']} 대 {t['neg_reviewer_pct']}")
        if mw != weak_of:
            die(f"ASIN별 최대 약점이 metrics와 다릅니다: {weak_of} 대 {mw}")
    bs = bootstrap(D, n, seed)
    weakest = loo[0]["weakest"]
    lo, hi = bs["weakest_range"]
    total = len(D.by_asin)
    texts = {
        "weakest": f"{total}개 중 {weakest}개" + (f"(리뷰를 다시 뽑아 보면 {lo}~{hi}개)" if (lo, hi) != (weakest, weakest) else ""),
        "head_first": f"{bs['head_first_pct']:.1f}%",
        "head_neg_ci": f"{bs['head_neg_ci'][0]:.1f}%~{bs['head_neg_ci'][1]:.1f}%",
        "weakest_dist": ", ".join(f"{k}개 {v:.1f}%" for k, v in bs["weakest_dist"].items()),
        "loo_flips": f"{len(loo) - 1}번 중 {sum(1 for r in loo[1:] if r['flips'])}번",
    }
    out = {"made_at": now_iso(), "run": run.name, "head_topic": D.head, "head_name": D.name[D.head],
           "rules": {"strength_min_mentions": strength_min, "exclude": list(EXCLUDE), "direction_index": D.di},
           "base": {"head_neg": loo[0]["head_neg"], "weakest": weakest, "asins": total, "weakest_by_asin": weak_of},
           "bootstrap": bs, "leave_one_out": loo, "texts": texts, "names": D.name}
    write_json(run / "05_robustness.json", out)
    print(f"견고성 점검: 다시 뽑기 {n}번(씨앗 {seed}) {D.name[D.head]} 1위 유지 {texts['head_first']}, 부정 리뷰어 95% 구간 {texts['head_neg_ci']}, "
          f"최대 약점 상품 {texts['weakest']} [{texts['weakest_dist']}]")
    print(f"상품 하나씩 빼기: 뒤집힘 {texts['loo_flips']}")
    for r in loo:
        print(f"  {r['out'] or '빼지 않음'}: {D.name[D.head]} {r['head_neg']:.1f}%, 1위 {D.name[r['first']]} {r['first_pct']:.1f}%, "
              f"2위 {D.name[r['second']]} {r['second_pct']:.1f}%, 최대 약점 {r['remain']}개 중 {r['weakest']}개, "
              f"약함 {r['low']} 대 셈 {r['high']}({r['low_share']}%), 상위 3 {', '.join(D.name[t] for t in r['top3'])}"
              + (f"  뒤집힘: {', '.join(r['flips'])}" if r["flips"] else ""))
    return 0


def main():
    ap = argparse.ArgumentParser(description="견고성 점검(다시 뽑기, 상품 하나씩 빼기)")
    ap.add_argument("run", nargs="?")
    ap.add_argument("--n", type=int, default=2000)
    ap.add_argument("--seed", type=int, default=7)
    ap.add_argument("--strength-min", type=int, default=10, help="weight.py --strength-min과 같은 값")
    a = ap.parse_args()
    sys.exit(run_all(resolve_run(a.run), a.n, a.seed, a.strength_min))


if __name__ == "__main__":
    main()
