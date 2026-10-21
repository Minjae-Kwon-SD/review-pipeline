"""스크립트 자체 시험: 가짜 회차(tests/fixture)로 돌려 손계산 값과 맞는지 본다.

사용: python tests/test_scripts.py
손계산(가중치 = 실제 비율 / 표본 비율)
- B0TESTAAA1: 분포 5★60 4★20 3★10 2★5 1★5, 표본 별점마다 1개(5개)
  가중치 5★3.0 4★1.0 3★0.5 2★0.25 1★0.25, 가중 평균 4.25 = 분포 평균 4.25
- B0TESTBBB2: 분포 5★40 4★20 3★10 2★10 1★20, 표본 1★ 2개와 나머지 1개씩(6개)
  가중치 5★2.4 4★1.2 3★0.6 2★0.6 1★0.6, 가중 평균 3.50 = 분포 평균 3.50
- 전체 가중 평균 (4.25*5 + 3.5*6) / 11 = 3.84, 표본 평균 31 / 11 = 2.82
- 지속력: 태그 7개(부정 4, 긍정 2, 혼합 1). 부정 비율 4/7 = 57.1%
  가중 부정 비율 1.7 / 7.7 = 22.1%, 부정 언급 리뷰어 1.7 / 11 = 15.5%
  영향: 부정 언급 리뷰 가중 평균 1.95 / 1.7 = 1.15, 나머지 40.3 / 9.3 = 4.33, 격차 -3.19
- 정답 세트: 상위 모델 F1 24/25 = 0.96, sonnet F1 22/25 = 0.88
별점 묶음 보정(v1, 묶음 부정 1,2★ / 중립 3★ / 긍정 4,5★, test_star_groups)
- 2★ 60, 5★ 80, 실제 61/8/8/5/18: R 0.92, w(2) 0.583333, w(5) 1.3125, 가중치 합 140, 빠진 비율 8.0
- 별점마다 80개, 실제 60/15/10/5/10: w 3.0/0.75/0.5/0.25/0.5(5★부터), 3.0은 경고 아님
- 1★ 60, 2★ 70, 3★ 70, 5★ 70, 실제 50/10/10/10/20: w1 0.9, w2 w3 0.385714, w5 2.314286(긍정 묶음 단위)
- 유효 별점: 경우1 부정 1.217391, 긍정 4.884058, 가중 평균 3.967391(= 3.65 / 0.92). 경우3 긍정 4.833333, 가중 평균 3.6
- 리뷰 한 개 비중 경고: 18개 중 1★ 1개 가중치 3.41 → 18.9%(기준 2%). 경우2의 w5 3.0 / 400 = 0.75%는 경고 아님
"""
import csv
import json
from collections import Counter
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass

HERE = Path(__file__).resolve().parent
SCRIPTS = HERE.parent / "scripts"
FAILS = []
CHECKS = [0]


def run(script, *args, expect=0):
    CHECKS[0] += 1
    p = subprocess.run([sys.executable, str(SCRIPTS / script), *map(str, args)],
                       capture_output=True, text=True, encoding="utf-8",
                       env=dict(os.environ, PYTHONIOENCODING="utf-8"))
    if p.returncode != expect:
        FAILS.append(f"{script} {' '.join(map(str, args))}: 종료 코드 {p.returncode}(기대 {expect})\n{p.stdout}{p.stderr}")
    return p.stdout + p.stderr


def eq(name, got, want):
    CHECKS[0] += 1
    if got != want:
        FAILS.append(f"{name}: {got!r} != {want!r}")


def fresh(tmp, name):
    dst = Path(tmp) / name
    shutil.copytree(HERE / "fixture" / "runs" / "fixture", dst)
    return dst


def fake_reviews(asin, counts):
    return [{"review_id": f"{asin}-{s}-{i}", "asin": asin, "star": str(s)}
            for s, n in counts.items() for i in range(n)]


def fake_dist(asin, s5, s4, s3, s2, s1):
    return {"asin": asin, "s5": str(s5), "s4": str(s4), "s3": str(s3), "s2": str(s2), "s1": str(s1)}


def test_star_groups():
    """별점 묶음 보정 손계산(브리프의 세 경우). 묶음: 부정 1,2★ / 중립 3★ / 긍정 4,5★"""
    sys.path.insert(0, str(SCRIPTS))
    from pipeline_io import load_config
    from weight import build_weights
    conf = load_config()

    def run_case(asin, counts, dist):
        reviews = fake_reviews(asin, counts)
        weight, info, wt, eff = build_weights(reviews, {asin: dist}, conf)
        pa = wt["per_asin"][asin]
        ws = {int(s): v for g in pa["groups"].values() for s, v in g["weights"].items()}
        pa["_eff"] = {int(r["star"]): round(eff[r["review_id"]], 6) for r in reviews}
        pa["_wmean"] = round(sum(weight[r["review_id"]] * eff[r["review_id"]] for r in reviews) / len(reviews), 6)
        pa["_info"] = info[asin]
        return ws, pa, wt["warnings"], round(sum(weight.values()), 9)

    # 1. 2★ 60, 5★ 80, 실제 61/8/8/5/18: 부정 0.23, 긍정 0.69, R 0.92
    ws, pa, warns, total = run_case("B0CASE0001", {2: 60, 5: 80}, fake_dist("B0CASE0001", 61, 8, 8, 5, 18))
    eq("경우1 가중치", ws, {2: 0.583333, 5: 1.3125})
    eq("경우1 R, 빠진 비율, 방식", (pa["covered_real_pct"], pa["missing_real_pct"],
                              [g["mode"] for g in pa["groups"].values()]), (92.0, 8.0, ["group", "empty", "group"]))
    eq("경우1 가중치 합", total, 140.0)
    # 유효 별점: 부정 (1x0.18 + 2x0.05) / 0.23, 긍정 (4x0.08 + 5x0.61) / 0.69, 가중 평균 3.65 / 0.92
    eq("경우1 유효 별점", pa["_eff"], {2: 1.217391, 5: 4.884058})
    eq("경우1 가중 평균(유효 별점)", pa["_wmean"], 3.967391)
    eq("경우1 덮인 묶음 분포 평균, 전체 분포 평균", (pa["_info"]["covered_hist_mean_star"], pa["_info"]["hist_mean_star"]),
       (3.97, 3.89))
    # 1장 실제 별점 분포: 02_star_distribution.csv에서 바로, 표본이 있는 묶음의 별점만 R(0.92)로 다시 나눔
    from weight import real_star_dist
    d1 = fake_dist("B0CASE0001", 61, 8, 8, 5, 18)
    _, _, wt1, _ = build_weights(fake_reviews("B0CASE0001", {2: 60, 5: 80}), {"B0CASE0001": d1}, conf)
    eq("경우1 실제 별점 분포", real_star_dist({"B0CASE0001": d1}, wt1),
       ({"1": 19.6, "2": 5.4, "3": 0.0, "4": 8.7, "5": 66.3}, 8.0))
    # 2. 별점마다 80개(n 400), 실제 60/15/10/5/10: 가중치 3.0은 경고 아님(초과만 경고)
    ws, pa, warns, total = run_case("B0CASE0002", {s: 80 for s in (1, 2, 3, 4, 5)},
                                    fake_dist("B0CASE0002", 60, 15, 10, 5, 10))
    eq("경우2 가중치", ws, {1: 0.5, 2: 0.25, 3: 0.5, 4: 0.75, 5: 3.0})
    eq("경우2 비중 경고(w5 3.0 / n 400 = 0.75%는 경고 아님)", [w for w in warns if "비중" in w], [])
    eq("경우2 가중 평균 = 분포 평균", (pa["_wmean"], pa["_info"]["hist_mean_star"]), (4.1, 4.1))
    eq("경우2 방식, 가중치 합", (pa["all_per_star"], total), (True, 400.0))
    # 3. 1★ 60, 2★ 70, 3★ 70, 5★ 70(n 270), 실제 50/10/10/10/20: 긍정 묶음 단위
    ws, pa, warns, total = run_case("B0CASE0003", {1: 60, 2: 70, 3: 70, 5: 70},
                                    fake_dist("B0CASE0003", 50, 10, 10, 10, 20))
    eq("경우3 가중치", ws, {1: 0.9, 2: 0.385714, 3: 0.385714, 5: 2.314286})
    eq("경우3 방식, 가중치 합", ([g["mode"] for g in pa["groups"].values()], total),
       (["per_star", "per_star", "group"], 270.0))
    eq("경우3 비중 경고", [w for w in warns if "비중" in w], [])
    # 긍정 유효 별점 (4x0.1 + 5x0.5) / 0.6, 가중 평균 0.2x1 + 0.1x2 + 0.1x3 + 0.6x4.833333 = 3.6
    eq("경우3 유효 별점", pa["_eff"], {1: 1.0, 2: 2.0, 3: 3.0, 5: 4.833333})
    eq("경우3 가중 평균(유효 별점)", pa["_wmean"], 3.6)
    # 리뷰 한 개 비중 경고: 18개 중 1★ 1개의 가중치 3.41 → 3.41 / 18 = 18.9% > 2.0%
    _, pa, warns, _ = run_case("B0CASE0005", {1: 1, 5: 17}, fake_dist("B0CASE0005", 81.055556, 0, 0, 0, 18.944444))
    eq("경우5 1★ 가중치", pa["groups"]["negative"]["weights"], {"1": 3.41})
    eq("리뷰 한 개 비중 경고", [w for w in warns if "비중" in w and "negative" in w],
       ["B0CASE0005 negative: 리뷰 한 개 비중 18.9%(가중치 3.410 / 표본 18개, 기준 2.0% 초과)"])


def test_sections():
    """시간 추이 기간 규칙, 공출현, 신뢰 신호(sections.py)"""
    sys.path.insert(0, str(SCRIPTS))
    from datetime import date
    import sections
    pers, cur = sections.periods_for(date(2026, 10, 7))
    eq("기간(10월 기준)", ([p[0] for p in pers], str(pers[-1][1]), str(pers[-1][2]), str(cur)),
       (["~2024년", "2025년", "2026년 1~6월", "2026년 7~9월"], "2026-07-01", "2026-09-30", "2026-10-01"))
    pers, cur = sections.periods_for(date(2026, 2, 10))   # 1분기 기준: 끝난 분기는 작년 10~12월
    eq("기간(2월 기준)", [p[0] for p in pers], ["~2023년", "2024년", "2025년 1~9월", "2025년 10~12월"])
    pers, _ = sections.periods_for(date(2026, 5, 1))      # 2분기 기준: 끝난 분기가 1분기라 올해 앞 기간 없음
    eq("기간(5월 기준)", [p[0] for p in pers], ["~2024년", "2025년", "2026년 1~3월"])
    tags = [{"review_id": "r1", "topic": "scent", "sentiment": "negative"},
            {"review_id": "r1", "topic": "longevity_projection", "sentiment": "negative"},
            {"review_id": "r1", "topic": "overall", "sentiment": "negative"},
            {"review_id": "r2", "topic": "scent", "sentiment": "negative"},
            {"review_id": "r2", "topic": "longevity_projection", "sentiment": "negative"},
            {"review_id": "r3", "topic": "scent", "sentiment": "positive"},
            {"review_id": "r3", "topic": "bottle_design", "sentiment": "positive"}]
    co = sections.cooccurrence(tags, ("overall",))
    eq("공출현", co, {"negative": [{"a": "longevity_projection", "b": "scent", "reviews": 2}],
                      "positive": [{"a": "bottle_design", "b": "scent", "reviews": 1}]})
    reviews = [{"review_id": "r1", "asin": "A", "star": "1", "title": "Bad", "verified": "true", "vine": "false", "helpful_votes": "5"},
               {"review_id": "r2", "asin": "A", "star": "2", "title": "Meh", "verified": "false", "vine": "false", "helpful_votes": ""},
               {"review_id": "r3", "asin": "A", "star": "5", "title": "Good", "verified": "true", "vine": "true", "helpful_votes": "3"}]
    ts = sections.trust_signals(reviews, tags, ("overall",))
    eq("신뢰 신호", (ts["verified"], ts["unverified"], ts["vine"]["reviews"], ts["helpful_total"],
                    ts["helpful_negative_pct"], ts["helpful_weighted_complaints"], [x["review_id"] for x in ts["top_helpful"]]),
       ({"reviews": 2, "mean_star": 3.0, "negative_pct": 50.0}, {"reviews": 1, "mean_star": 2.0, "negative_pct": 100.0}, 1, 8,
        62.5, [{"topic": "longevity_projection", "votes": 5, "share_pct": 100.0}, {"topic": "scent", "votes": 5, "share_pct": 100.0}],
        ["r1", "r3"]))


def test_variant():
    """변형 신호: 키 자동 선택, 용량 정규화, 온스당 가격, 숨김 규칙"""
    sys.path.insert(0, str(SCRIPTS))
    import sections
    eq("용량 읽기", (sections.parse_size("1 Fl Oz (Pack of 1)"), sections.parse_size("3.4 fl oz (Pack of 2)"),
                    sections.parse_size("100 ml"), sections.parse_size("Rose")), ((1.0, 1), (3.4, 2), (3.38, 1), (None, 1)))
    reviews, tags, weight = [], [], {}
    for i in range(20):        # A: 1 fl oz 20개, 3.3 fl oz 20개(표기가 둘로 갈려도 합침), 향은 하나뿐
        for size, va in (("1 Fl Oz (Pack of 1)", "A1"), ("3.3 Fl Oz (Pack of 1)" if i % 2 else "3.3 fl oz", "A3")):
            rid = f"{va}-{i}"
            reviews.append({"review_id": rid, "asin": "A", "variant_asin": va, "variant_text": f"Size: {size}; Scent: Rose"})
            weight[rid] = 1.0
            tags.append({"review_id": rid, "topic": "price_value", "sentiment": "negative" if va == "A1" and i < 10 else "positive"})
    for i in range(16):        # B: 변형 하나뿐이라 표에 안 나옴
        rid = f"B-{i}"
        reviews.append({"review_id": rid, "asin": "B", "variant_asin": "B1", "variant_text": "Size: 2 Fl Oz"})
        weight[rid] = 1.0
    eq("변형 키", sections.choose_variant_key(reviews, 15), ("Size", {"Size": 1, "Scent": 0}))
    prices = {"checked_on": "2026-10-07", "asins": {"A": {"variants": [{"asin": "A1", "buyBoxPrice": 30.0},
                                                                         {"asin": "A3", "buyBoxPrice": 66.0}]}}}
    schema = {"price_value": {"name_ko": "가격 대비 가치"}}
    vs = sections.variant_signal(reviews, tags, weight, schema, prices, ("overall",))
    rows = vs["asins"][0]["rows"]
    eq("변형 표", [(r["variant"], r["reviews"], r["price_per_oz"], r["neg_reviewer_pct"]["price_value"]) for r in rows],
       [("1 fl oz", 20, 30.0, 50.0), ("3.3 fl oz", 20, 20.0, 0.0)])
    eq("변형이 하나인 ASIN은 빠짐", [a["asin"] for a in vs["asins"]], ["A"])
    vs = sections.variant_signal(reviews, tags, weight, schema, prices, ("overall",), min_tags=21)
    eq("태그 적은 변형 숨김", vs["asins"][0]["hidden_low_tags"], ["1 fl oz", "3.3 fl oz"])
    # 옷 글자 사이즈: 꼬리(Tall, Petite, Plus)를 떼고 기본 사이즈와 순서로. 글자 사이즈가 아니면 None
    eq("옷 사이즈 읽기", [sections.letter_size(v) for v in ("XX-Large Plus", "Medium-Tall", "X-Small Petite", "3X-Large", "2XL", "Rose", "mens")],
       [("XXL", 6), ("M", 3), ("XS", 1), ("3XL", 7), ("XXL", 6), (None, None), (None, None)])
    # 키 점수가 같으면 사이즈 키를 먼저, 방향 라벨(작게, 크게)로 변형마다 수와 지수, 상품을 합친 표
    reviews, tags, weight, labels = [], [], {}, []
    for asin in ("A", "B"):
        for size, color, small in (("Small", "Red", 0), ("Small-Tall", "Blue", 0), ("X-Large", "Red", 1), ("X-Large Plus", "Blue", 1)):
            for i in range(8):
                rid = f"{asin}{size}{color}{i}"
                reviews.append({"review_id": rid, "asin": asin, "variant_asin": asin + size, "variant_text": f"Size: {size}; Color: {color}"})
                weight[rid] = 1.0
                tags.append({"review_id": rid, "topic": "fit_sizing", "sentiment": "negative"})
                if i < 3:
                    labels.append({"review_id": rid, "labels": ["runs_small" if small else "runs_large"]})
    eq("같은 점수면 사이즈 키 먼저", sections.rank_variant_keys({"Color": 2, "Size": 2, "Style": 0}), ["Size", "Color"])
    di = {"topic": "fit_sizing", "high": {"name": "작게", "labels": ["runs_small"]}, "low": {"name": "크게", "labels": ["runs_large"]}}
    sigs = sections.variant_signals(reviews, tags, weight, {"fit_sizing": {"name_ko": "핏"}}, None, ("overall",), direction=di, labels=labels)
    eq("변형 키 둘(사이즈 먼저)", [x["key"] for x in sigs], ["Size", "Color"])
    eq("상품 합친 사이즈별 방향", [(r["variant"], r["reviews"], r["asins"], r["high"], r["low"], r["index"]) for r in sigs[0]["pooled"]],
       [("S", 32, 2, 0, 12, -1.0), ("XL", 32, 2, 12, 0, 1.0)])
    eq("ASIN 안 사이즈 행 방향", [(r["variant"], r["direction"]) for r in sigs[0]["asins"][0]["rows"]],
       [("S", {"high": 0, "low": 6, "index": -1.0, "unclear": False}), ("XL", {"high": 6, "low": 0, "index": 1.0, "unclear": False})])


def test_issues(tmp):
    """issues.py: 주제와 방향마다 표본(20개 미만은 기타만), merge 검사"""
    run_ = tmp / "issues-2026-10-07"
    run_.mkdir()
    shutil.copy(HERE / "fixture" / "runs" / "fixture" / "03_schema_approved.yaml", run_ / "03_schema_approved.yaml")
    lines = ["review_id,asin,star,date,title,body,verified,vine"]
    tags = []
    for i in range(30):
        a, st = ("B0ISSUE001", 1 + i % 5) if i % 2 else ("B0ISSUE002", 1 + (i * 3) % 5)
        rid = f"R{i:02d}ISSUEXYZ"
        lines.append(f"{rid},{a},{st},2026-09-01,T,Body {i},true,false")
        tags.append({"review_id": rid, "topic": "longevity_projection", "sentiment": "negative" if i < 25 else "mixed",
                     "quote": f"Body {i}"})
        if i < 5:
            tags.append({"review_id": rid, "topic": "scent", "sentiment": "positive", "quote": f"Body {i}"})
        tags.append({"review_id": rid, "topic": "overall", "sentiment": "negative", "quote": f"Body {i}"})
    (run_ / "02_reviews.csv").write_text("\n".join(lines) + "\n", encoding="utf-8")
    (run_ / "04_tags.jsonl").write_text("".join(json.dumps(t) + "\n" for t in tags), encoding="utf-8")
    run("issues.py", "sample", run_, "--per", "12")
    plan = json.loads((run_ / "07a_issue_plan.json").read_text(encoding="utf-8"))
    got = {(e["topic"], e["direction"]): (e["quotes"], e["sampled"], e["only_other"]) for e in plan["items"]}
    eq("세부 이슈 표본", (got[("longevity_projection", "negative")], got[("longevity_projection", "positive")],
                       got[("scent", "positive")], any(e["topic"] == "overall" for e in plan["items"])),
       ((30, 12, False), (5, 0, True), (5, 0, True), False))
    smp = [json.loads(l) for l in (run_ / "07a_issue_samples" / "longevity_projection_negative.jsonl").read_text(encoding="utf-8").splitlines()]
    eq("표본이 ASIN을 고르게 섞음", Counter(x["asin"] for x in smp), Counter({"B0ISSUE001": 6, "B0ISSUE002": 6}))
    first = (run_ / "07a_issue_samples" / "longevity_projection_negative.jsonl").read_text(encoding="utf-8")
    run("issues.py", "sample", run_, "--per", "12")
    eq("표본 시드 고정", (run_ / "07a_issue_samples" / "longevity_projection_negative.jsonl").read_text(encoding="utf-8"), first)
    ids = [x["review_id"] for x in smp]
    good = {"topic": "longevity_projection", "directions": {
        "negative": {"labels": [{"id": "fades_fast", "name_ko": "금방 날아감", "name_en": "Fades quickly",
                                 "include": "금방 사라짐", "exclude": "처음부터 약함",
                                 "examples": [{"review_id": ids[0], "quote": "x"}, {"review_id": ids[1], "quote": "y"}],
                                 "approx_count": 10}], "other_approx_count": 2},
        "positive": {"labels": [], "other_approx_count": 5}}}
    import yaml
    for tid in ("price_value", "scent"):
        (run_ / f"07a_issues_{tid}.yaml").write_text(yaml.safe_dump({"topic": tid, "directions": {
            "negative": {"labels": [], "other_approx_count": 0}, "positive": {"labels": [], "other_approx_count": 0}}}),
            encoding="utf-8")
    (run_ / "07a_issues_longevity_projection.yaml").write_text(yaml.safe_dump(good, allow_unicode=True), encoding="utf-8")
    run("issues.py", "merge", run_)
    md = (run_ / "07a_issues_draft.md").read_text(encoding="utf-8")
    eq("세부 이슈 초안 표", ("금방 날아감" in md, "fades_fast" in md), (True, True))
    bad = json.loads(json.dumps(good))
    bad["directions"]["negative"]["labels"][0]["approx_count"] = 0
    bad["directions"]["negative"]["labels"][0]["examples"][1]["review_id"] = "R99NOTINSAMPLE"
    bad["directions"]["positive"]["labels"] = [dict(good["directions"]["negative"]["labels"][0], id="x")]
    (run_ / "07a_issues_longevity_projection.yaml").write_text(yaml.safe_dump(bad, allow_unicode=True), encoding="utf-8")
    out = run("issues.py", "merge", run_, expect=1)
    for want in ("5% 미만", "표본에 없습니다", "기타만 둬야"):
        if want not in out:
            FAILS.append(f"세부 이슈 검사에서 '{want}'를 잡지 못함:\n{out}")

    # 승인 뒤: approve, label-plan, label-check(개수), audit, safety, 리포트 개수 대조
    (run_ / "07a_issues_longevity_projection.yaml").write_text(yaml.safe_dump(good, allow_unicode=True), encoding="utf-8")
    run("issues.py", "merge", run_)
    run("issues.py", "approve", run_, "--approved-at", "2026-10-07T09:09Z", "--approved-by", "시험")
    appr = yaml.safe_load((run_ / "07a_issues_approved.yaml").read_text(encoding="utf-8"))
    eq("승인 기록", (appr["version"], appr["approved_at"], appr["approved_by"]), ("approved", "2026-10-07T09:09Z", "시험"))
    # 별점 분포가 표본과 같아 가중치는 모두 1(리뷰 30개, 가중치 합 30)
    (run_ / "02_star_distribution.csv").write_text(
        "asin,s5,s4,s3,s2,s1,total_ratings\nB0ISSUE001,20,20,20,20,20,100\nB0ISSUE002,20,20,20,20,20,100\n", encoding="utf-8")
    run("issues.py", "label-plan", run_, "--size", "20")
    plan = json.loads((run_ / "07b_label_batches.json").read_text(encoding="utf-8"))
    # 지속력 부정 30개(부정 25 + 혼합 5)는 묶음 20, 10. 지속력 긍정(혼합 5)과 향 긍정 5는 라벨이 없어 기타로 자동
    eq("라벨 묶음", ([(b["batch_id"], b["items"]) for b in plan["batches"]], plan["auto_other"]),
       ([("longevity_projection_negative_01", 20), ("longevity_projection_negative_02", 10)], 10))

    def label_out(bad=False):
        for b in plan["batches"]:
            rows = [json.loads(l) for l in (run_ / b["input"]).read_text(encoding="utf-8").splitlines()]
            out = [{"review_id": r["review_id"], "quote": r["quote"],
                    "labels": ["fades_fast"] if int(r["review_id"][1:3]) < 10 else ["other"]} for r in rows]
            if bad and b["batch_id"].endswith("_01"):
                out[0]["labels"] = ["nope"]
                out.pop()
            (run_ / b["output"]).write_text("".join(json.dumps(o) + "\n" for o in out), encoding="utf-8")
    label_out(bad=True)
    out = run("issues.py", "label-check", run_, expect=1)
    chk = json.loads((run_ / "07b_issue_check.json").read_text(encoding="utf-8"))
    eq("라벨 검사 실패 묶음", chk["failed_batches"], ["longevity_projection_negative_01"])
    for want in ("nope", "라벨이 없는 인용 1개"):
        if want not in out:
            FAILS.append(f"라벨 검사에서 '{want}'를 잡지 못함:\n{out}")
    label_out()
    run("issues.py", "label-check", run_)
    counts = json.loads((run_ / "07b_issue_counts.json").read_text(encoding="utf-8"))
    ln = counts["topics"]["longevity_projection.negative"]
    # 금방 날아감: R00~R09 10개(홀수 5개 B0ISSUE001, 짝수 5개 B0ISSUE002), 가중 10 / 30 = 33.3%. 기타 20 / 30 = 66.7%
    eq("라벨 개수", [(l["id"], l["reviews"], l["weighted_pct"], l["by_asin"]) for l in ln["labels"]],
       [("fades_fast", 10, 33.3, {"B0ISSUE001": 5, "B0ISSUE002": 5}),
        ("other", 20, 66.7, {"B0ISSUE001": 10, "B0ISSUE002": 10})])
    eq("기타 비율", (ln["units"], ln["other_units"], ln["other_pct"]), (30, 20, 66.7))
    eq("라벨 없는 방향은 기타 100%", counts["topics"]["longevity_projection.positive"]["other_pct"], 100.0)
    sys.path.insert(0, str(SCRIPTS))
    import sections
    summ = sections.issue_summary(counts)
    eq("세부 이슈 요약", summ["longevity_projection.negative"]["top"],
       [{"id": "fades_fast", "name_ko": "금방 날아감", "reviews": 10, "weighted_pct": 33.3}])
    eq("브랜드 안 세부 이슈", sections.brand_issues(counts, ["B0ISSUE001"], "longevity_projection", "negative"),
       [{"id": "fades_fast", "name_ko": "금방 날아감", "reviews": 5}])
    # 감사: 표본 10개 중 FAIL 1개 = 10%(기준 5% 초과), 표본에 없는 FAIL은 세지 않고 경고
    run("issues.py", "audit-sample", run_, "--n", "10", "--parts", "1")
    smp = [json.loads(l) for l in (run_ / "07b_issue_audit_sample.jsonl").read_text(encoding="utf-8").splitlines()]
    eq("감사 표본 수", len(smp), 10)
    f0 = smp[0]
    (run_ / "07b_issue_audit.yaml").write_text(yaml.safe_dump({"audit": {"stage": "issues", "checked": 10, "findings": [
        {"review_id": f0["review_id"], "topic": f0["topic"], "direction": f0["direction"], "status": "FAIL"},
        {"review_id": "R99NOTINSAMPLE", "topic": "scent", "direction": "positive", "status": "FAIL"},
        {"review_id": f0["review_id"], "topic": f0["topic"], "direction": f0["direction"], "status": "UNVERIFIED"}]}}),
        encoding="utf-8")
    run("issues.py", "audit", run_, expect=1)
    au = json.loads((run_ / "07b_issue_audit_summary.json").read_text(encoding="utf-8"))
    eq("감사 집계", (au["status"], au["fail"], au["fail_rate"], len(au["warnings"])), ("FAIL", 1, 0.1, 1))
    run("issues.py", "audit", run_, "--max-fail", "0.2")
    # 감사자 둘로 나누기(2026-10-14): 반쪽 5개씩, 반쪽마다 FAIL 비율, 합칠 때 빠짐과 겹침 확인
    run("issues.py", "audit-sample", run_, "--n", "10")
    halves = [[json.loads(l) for l in (run_ / f"07b_issue_audit_sample_p{k}.jsonl").read_text(encoding="utf-8").splitlines()] for k in (1, 2)]
    eq("반쪽 표본 수와 합", (len(halves[0]), len(halves[1]), sorted(json.dumps(x, sort_keys=True) for x in halves[0] + halves[1]) ==
       sorted(json.dumps(x, sort_keys=True) for x in smp)), (5, 5, True))
    h0 = halves[0][0]
    (run_ / "07b_issue_audit_p1.yaml").write_text(yaml.safe_dump({"audit": {"stage": "issues", "checked": 5, "findings": [
        {"review_id": h0["review_id"], "topic": h0["topic"], "direction": h0["direction"], "status": "FAIL"}]}}), encoding="utf-8")
    run("issues.py", "audit", run_, expect=2)                      # p2 판정이 아직 없으면 합치지 않음(중단)
    (run_ / "07b_issue_audit_p2.yaml").write_text(yaml.safe_dump({"audit": {"stage": "issues", "checked": 5, "findings": []}}), encoding="utf-8")
    out = run("issues.py", "audit", run_, "--max-fail", "0.2")
    au = json.loads((run_ / "07b_issue_audit_summary.json").read_text(encoding="utf-8"))
    eq("반쪽 합친 집계", (au["status"], au["fail"], [(p_["part"], p_["fail"], p_["fail_rate"]) for p_ in au["parts"]], au["merge_problems"]),
       ("PASS", 1, [("p1", 1, 0.2), ("p2", 0, 0.0)], []))
    eq("합치기 확인 문구", "표본 빠짐과 겹침 없음" in out, True)
    p2 = run_ / "07b_issue_audit_sample_p2.jsonl"
    p2.write_text(chr(10).join(p2.read_text(encoding="utf-8").splitlines()[1:]) + chr(10), encoding="utf-8")
    (run_ / "07b_issue_audit_p2.yaml").write_text(yaml.safe_dump({"audit": {"stage": "issues", "checked": 4, "findings": []}}), encoding="utf-8")
    out = run("issues.py", "audit", run_, "--max-fail", "0.2", expect=1)
    eq("반쪽에서 빠진 표본을 잡음", ("INCOMPLETE" in out, "반쪽 어디에도 없는 표본 1개" in out), (True, True))
    # 안전: 부정 2(이상 반응 1, 없음 1), 긍정 1(없음)
    extra = [{"review_id": "R00ISSUEXYZ", "topic": "safety", "sentiment": "negative", "quote": "Body 0"},
             {"review_id": "R01ISSUEXYZ", "topic": "safety", "sentiment": "negative", "quote": "Body 1"},
             {"review_id": "R02ISSUEXYZ", "topic": "safety", "sentiment": "positive", "quote": "Body 2"}]
    (run_ / "04_tags.jsonl").write_text("".join(json.dumps(t) + "\n" for t in tags + extra), encoding="utf-8")
    run("issues.py", "safety-input", run_)
    (run_ / "07c_safety_verdicts.yaml").write_text(yaml.safe_dump({"audit": {"stage": "safety", "verdicts": [
        {"review_id": "R00ISSUEXYZ", "verdict": "symptom", "symptom_type": "두통", "reason": "두통"},
        {"review_id": "R01ISSUEXYZ", "verdict": "none", "reason": "향이 셈"}]}}, allow_unicode=True), encoding="utf-8")
    out = run("issues.py", "safety-render", run_, expect=2)
    if "R02ISSUEXYZ" not in out:
        FAILS.append(f"판정 없는 안전 인용을 잡지 못함:\n{out}")
    v = yaml.safe_load((run_ / "07c_safety_verdicts.yaml").read_text(encoding="utf-8"))
    v["audit"]["verdicts"].append({"review_id": "R02ISSUEXYZ", "verdict": "none", "reason": "반응 없음"})
    (run_ / "07c_safety_verdicts.yaml").write_text(yaml.safe_dump(v, allow_unicode=True), encoding="utf-8")
    run("issues.py", "safety-render", run_)
    ss = json.loads((run_ / "07c_safety_summary.json").read_text(encoding="utf-8"))
    eq("안전 판정 집계", (ss["negative_symptom"], ss["negative_no_symptom"], ss["positive_no_symptom"]), (1, 1, 1))
    # 증상별: 두통 1개(가중치 1 / 30 = 3.3%), 이상 반응 없음 1개
    eq("안전 증상별", (ss["by_symptom"], ss["negative_text"]),
       ([{"name": "두통", "reviews": 1, "weighted_pct": 3.3}], "안전 부정 리뷰 2개: 두통 1개(가중 3.3%), 이상 반응 없음 1개"))
    v["audit"]["verdicts"][0].pop("symptom_type")
    (run_ / "07c_safety_verdicts.yaml").write_text(yaml.safe_dump(v, allow_unicode=True), encoding="utf-8")
    out = run("issues.py", "safety-render", run_, expect=2)
    if "symptom_type" not in out:
        FAILS.append(f"증상 분류 없는 이상 반응을 잡지 못함:\n{out}")
    v["audit"]["verdicts"][0]["symptom_type"] = "두통"
    (run_ / "07c_safety_verdicts.yaml").write_text(yaml.safe_dump(v, allow_unicode=True), encoding="utf-8")
    run("issues.py", "safety-render", run_)
    rows = sections.render_issues({"safety.negative": {"topic": "safety", "direction": "negative", "units": 2, "other_pct": 100.0,
                                                       "top": []}}, {"safety": {"name_ko": "안전"}}, None, ss)
    eq("8장 표 안전 부정 칸", rows[2], "| 안전 | 부정 이슈 | 두통 리뷰 1개(3.3%), 이상 반응 없음 리뷰 1개 | 증상별 분류(07c) |")
    md = (run_ / "07c_safety_check.md").read_text(encoding="utf-8")
    eq("안전 확인표에 원문", ("Body 1" in md, "이상 반응 있음" in md), (True, True))
    # 리포트 문장 속 세부 이슈 개수 대조(표 블록 밖, 10장은 브랜드 ASIN 합)
    from audit_quotes import check_issue_counts
    brands = {"B0ISSUE001": "BrandA", "B0ISSUE002": "BrandB"}
    ok = ("## 8. 핵심 인사이트\n지속력 약점. 세부 이슈: 금방 날아감 리뷰 10개.\n안전 부정: 이상 반응 1개, 나머지 1개는 향의 세기 등.\n"
          "안전 부정 리뷰 2개: 두통 1개(가중 3.3%), 이상 반응 없음 1개입니다.\n"
          "## 10. 브랜드 심층\n### BrandA\n- 약점 1: 세부: 금방 날아감 리뷰 5개\n## 12. 전략 방향\n샘플\n")
    eq("리포트 개수 대조(맞음)", check_issue_counts(run_, ok, brands), [])
    bad = ok.replace("리뷰 10개", "리뷰 9개").replace("리뷰 5개", "리뷰 10개").replace("나머지 1개", "나머지 2개")
    eq("리포트 개수 대조(틀림)", len(check_issue_counts(run_, bad, brands)), 3)
    eq("안전 문장 대조(틀림)", len(check_issue_counts(run_, ok.replace("두통 1개(가중 3.3%)", "두통 2개(가중 3.3%)"), brands)), 1)
    # 2026-10-17 E2: 10장 밖이라도 같은 문장에 브랜드가 있고 그 브랜드 값이면 통과, 브랜드가 없거나 값이 다르면 오류
    in12 = ok.replace("## 12. 전략 방향\n샘플\n", "## 12. 전략 방향\nBrandA는 부정 24.9%이고 금방 날아감 리뷰 5개다. 샘플\n")   # E4: 소수점은 문장 끝 아님
    eq("12장 브랜드 안 수", (check_issue_counts(run_, in12, brands), len(check_issue_counts(run_, in12.replace("BrandA는", "그 브랜드는"), brands)),
                         len(check_issue_counts(run_, in12.replace("리뷰 5개다", "리뷰 4개다"), brands))), ([], 1, 1))
    # 부정어 경고: 같은 문장 안 인용 바로 앞 세 단어
    from audit_quotes import negation_before
    r = {"title": "T", "body": "It no longer smells the same or has staying power. Not bad. It stays with you"}
    eq("부정어 경고", (negation_before("smells the same", r), negation_before("It stays with you", r),
                     negation_before("has staying power", r)), ("longer", None, None))
    # 문장 숫자 대조(E3): metrics에 없는 단위 숫자는 오류, 계산 규칙 상수 1.96은 허용(2026-10-17 rt7)
    from audit_quotes import check_prose_numbers
    pn = Path(tmp) / "prose-2099-01-01"
    pn.mkdir()
    (pn / "05_metrics.json").write_text(json.dumps({"a": 3.2, "b": "12개"}), encoding="utf-8")
    eq("문장 숫자 대조", (check_prose_numbers(pn, "부정 3.2%, 리뷰 12개. 0에서 1.96 / sqrt(n)보다 가까우면 불분명.\n"),
                       len(check_prose_numbers(pn, "부정 4.4%다.\n"))), ([], 1))


def test_price_band():
    """collect.py price_band: 변형 가격 범위와 용량 범위"""
    sys.path.insert(0, str(SCRIPTS))
    from collect import price_band
    eq("가격대", price_band([{"buyBoxPrice": 36.0, "unitValue": 0.33, "unitType": "Fl Oz"},
                           {"buyBoxPrice": 115.54, "size": "3.3 Fl Oz (Pack of 1)"},
                           {"buyBoxPrice": 75.0, "unitValue": 1, "unitType": "Fl Oz"}]), "36.00~115.54달러(0.33~3.3 fl oz)")
    eq("가격대 한 값", price_band([{"buyBoxPrice": 20.99, "unitValue": 3.4, "unitType": "Fl Oz"}]), "20.99달러(3.4 fl oz)")
    eq("가격 없음", price_band([{"size": "1 Fl Oz"}]), "")


def test_collect_rank_paid(tmp):
    """collect.py rank(검색 순위와 매출로 후보)와 유료 수집 대상, 별점마다 호출, 다시 돌려도 두 번 부르지 않음(2026-10-10)."""
    sys.path.insert(0, str(SCRIPTS))
    import importlib
    import yaml
    collect = importlib.import_module("collect")
    cfg = HERE.parent / "config" / "categories" / "rankcat.yaml"
    cfg.write_text(yaml.safe_dump({"category": "rankcat", "name_ko": "순위 시험", "title_include": ["Cream"], "title_exclude": ["Wax"],
                                   "kind_rules": {"face": ["Face"]},
                                   "selection": {"seeds": ["hair cream", "depilatory"], "pick": 2, "min_db_reviews": 100,
                                                 "max_product_calls": 3}},
                                  allow_unicode=True), encoding="utf-8")
    calls = []
    top = {"hair cream": [{"asin": "B0R1", "title": "A Cream", "brandName": "A", "avgRank": 3.0, "latestRank": 2},
                          {"asin": "B0R2", "title": "B Wax Cream", "brandName": "B", "avgRank": 1.0, "latestRank": 1},
                          {"asin": "B0R3", "title": "C Face Cream", "brandName": "C", "avgRank": 5.0, "latestRank": 5}],
           "depilatory": {"payload": [{"asin": "B0R1", "title": "A Cream", "brandName": "A", "avgRank": 2.0, "latestRank": 4},
                                      {"asin": "B0R4", "title": "D Cream", "brandName": "D", "avgRank": 4.0, "latestRank": 4},
                                      {"asin": "B0R5", "title": "E Cream", "brandName": "E", "avgRank": 9.0, "latestRank": 9}]}}
    prod = {"B0R1": {"asin": "B0R1", "title": "A Cream 2 pack", "brandName": "A", "monthlyRevenueEstimate": 500.0, "parentAsin": "P1",
                     "reviewCount": 900, "reviewRating": 4.1, "buyBoxPrice": 9.5, "monthlyUnitsSold": 50},
            "B0R3": {"asin": "B0R3", "title": "C Face Cream", "brandName": "C", "monthlyRevenueEstimate": 800.0, "parentAsin": "P3",
                     "reviewCount": 50, "reviewRating": 3.9},
            "B0R4": {"asin": "B0R4", "title": "D Cream", "brandName": "D", "monthlyRevenueEstimate": 600.0, "parentAsin": "P1",
                     "reviewCount": 70, "reviewRating": 4.0}}
    stats = {"B0R1": 300, "B0R3": 0, "B0R4": 20}
    summary = {"fiveStar": {"percentage": 60}, "fourStar": {"percentage": 20}, "threeStar": {"percentage": 10},
               "twoStar": {"percentage": 5}, "oneStar": {"percentage": 5}}

    def fake(server, tool, args):
        calls.append((tool, json.dumps(args, sort_keys=True)))
        if tool == "search_terms_trends_top_products":
            d = top[args["search_term"]]
        elif tool == "products_byasin":
            d = [prod[args["asin"]]]
        elif tool == "get_review_stats":
            n = stats.get(args["asin"], 0)
            d = {"total_reviews": n, "rating_distribution": {"5": n}, "asin_count": 1 if n else 0, "date_range": {}}
        elif tool == "search_reviews":
            d = {"reviews": [{"asin": args["asin"], "rating_summary": summary, "total_ratings": 999, "average_rating": 4.2}]
                 if stats.get(args["asin"]) else []}
        elif tool == "scrape_reviews":
            d = {"collected": 10 * args["max_pages"], "inserted": 10, "skipped": 0}
        else:
            raise AssertionError(tool)
        return json.dumps(d), d
    collect.call = fake
    try:
        r = Path(tmp) / "rank-2026-10-10"
        collect.rank_candidates(r, "rankcat")
    finally:
        cfg.unlink()
    rows = list(__import__("csv").DictReader(open(r / "00_candidates.csv", encoding="utf-8-sig")))
    eq("rank: 제목 규칙, 같은 부모는 매출 큰 것, 매출 순", [(x["asin"], x["rank_pick"], x["need_paid"]) for x in rows],
       [("B0R3", "1", "yes"), ("B0R4", "2", "yes")])
    eq("rank: products_byasin은 평균 순위 앞쪽 3개만", sorted(json.loads(a)["asin"] for t, a in calls if t == "products_byasin"),
       ["B0R1", "B0R3", "B0R4"])
    log = json.loads((r / "00_candidates_log.json").read_text(encoding="utf-8"))
    eq("rank 기록: 제목 규칙으로 뺀 것, 상한 밖, 같은 부모", ([x["asin"] for x in log["title_rule_out"]], log["over_call_limit"],
                                                  log["same_parent"]), (["B0R2"], ["B0R5"], [{"asin": "B0R1", "kept": "B0R4", "parent_asin": "P1"}]))
    eq("rank 칸", (rows[0]["kind_hint"], rows[0]["total_ratings"], rows[0]["monthly_revenue"], rows[1]["search_avg_rank"]),
       ("face", "50", "800", "4"))


    # 유료 수집 대상: DB 리뷰 100개 미만만, 별점마다, 다시 돌리면 성공한 호출은 건너뜀
    (r / "raw").mkdir(exist_ok=True)
    conf = {"paid": {"enabled": True, "max_pages_per_star": 10, "max_scrape_calls": 11, "max_asins": 2, "split_by_star": True,
                     "scrape_below_db_reviews": 100}}
    eq("유료 대상", collect.paid_targets(r, ["B0R1", "B0R3", "B0R4"], conf, None), ["B0R3", "B0R4"])
    eq("--paid-asins가 먼저", collect.paid_targets(r, ["B0R1", "B0R3"], conf, ["B0R1"]), ["B0R1"])
    calls.clear()
    collect.paid_scrape(r, ["B0R3"], conf, test=True)
    eq("시험 호출: 하나, 1★, 1페이지", [json.loads(a)["ratings"] + [json.loads(a)["max_pages"]] for t, a in calls if t == "scrape_reviews"], [[1, 1]])
    calls.clear()
    collect.paid_scrape(r, ["B0R3", "B0R4"], conf)

    sc = [json.loads(a) for t, a in calls if t == "scrape_reviews"]
    eq("별점마다 10페이지", [(x["asins"][0], x["ratings"], x["max_pages"]) for x in sc][:2], [("B0R3", [1], 10), ("B0R3", [2], 10)])
    eq("호출 수(B0R3 5 + B0R4 5)", len(sc), 10)
    calls.clear()
    collect.paid_scrape(r, ["B0R3", "B0R4"], conf)
    eq("다시 돌리면 성공한 호출은 다시 부르지 않음", [t for t, a in calls if t == "scrape_reviews"], [])
    # 동시 호출(paid.concurrency 4): 호출 수와 상한은 같고 기록 줄도 호출마다 하나
    r2 = Path(tmp) / "rank-par"
    (r2 / "raw").mkdir(parents=True)
    collect.call_fresh = fake
    calls.clear()
    collect.paid_scrape(r2, ["B0R3", "B0R4"], {"paid": {**conf["paid"], "concurrency": 4}})
    lines = [json.loads(l) for l in open(r2 / "raw" / "paid_calls.jsonl", encoding="utf-8")]
    eq("동시 호출: 호출 10번, 기록 10줄, 같은 조합", (len([t for t, a in calls if t == "scrape_reviews"]), len(lines),
       sorted((x["asin"], x["arguments"]["ratings"][0]) for x in lines)), (10, 10, sorted((a, s) for a in ("B0R3", "B0R4") for s in range(1, 6))))
    calls.clear()
    (Path(tmp) / "rank-par2" / "raw").mkdir(parents=True)
    try:
        collect.paid_scrape(Path(tmp) / "rank-par2", ["B0R3", "B0R4"], {"paid": {**conf["paid"], "concurrency": 4, "max_scrape_calls": 3}})
        stopped = False
    except SystemExit:
        stopped = True
    eq("동시 호출도 상한(3번)을 넘겨 부르지 않음", (stopped, len([t for t, a in calls if t == "scrape_reviews"])), (True, 3))
    try:
        collect.paid_scrape(r, ["B0R1", "B0R3", "B0R4"], conf)
        stopped = False
    except SystemExit:
        stopped = True
    eq("max_asins를 넘으면 부르지 않고 멈춤", stopped, True)
    # 제모 크림 설정(H2): 제목 규칙과 채운 시장 노드
    cc = yaml.safe_load((HERE.parent / "config" / "categories" / "hairremovalcream.yaml").read_text(encoding="utf-8"))
    titles = ["Nair Hair Remover Lotion with Baby Oil", "Sally Hansen Cream Hair Remover Kit for Face", "Magic Razorless Shaving Cream for Men",
              "Veet Ready-to-Use Wax Strips", "Ulike Laser Hair Removal Device", "Gillette Venus Razors for Women"]
    eq("제모 크림 제목 규칙", [collect.has_any(t, cc["title_include"]) and not collect.has_any(t, cc["title_exclude"]) for t in titles],
       [True, True, True, False, False, False])
    eq("제모 크림 종류 힌트(women에 men이 걸리지 않음)", [collect.kind_hint(t, cc["kind_rules"]) for t in
       ("Flamingo Body Hair Removal Cream for Women", "Nair Men Hair Removal Body Cream", "Veet Facial Hair Removal Cream")],
       ["body_cream", "men", "face"])
    import market_build
    try:
        market_build.market_conf(Path(tmp) / "hairremovalcream-2026-10-10")
        stopped = False
    except SystemExit:
        stopped = True
    eq("시장 노드를 채운 뒤에는 시장 설정을 읽음(Depilatories 3779081)", (stopped, cc["market"]["parent_node"]), (False, 3779081))


def test_collect(tmp):
    """collect.py: 유료 모드는 꺼져 있으면 거부, pull --offline은 raw 파일로 02 파일을 만든다."""
    run_ = tmp / "collect"
    (run_ / "raw").mkdir(parents=True)
    (run_ / "01_asins.csv").write_text(
        "asin,title,brand,price_usd,price_band,amazon_rating,status,reason\n"
        "B0COLLECT1,,,,,,selected,시험\nB0COLLECT9,,,,,,excluded,시험\n", encoding="utf-8")
    out = run("collect.py", "pull", run_, "--mode", "paid", "--confirm-paid", expect=2)
    if "유료 수집이 꺼져 있습니다" not in out:
        FAILS.append(f"꺼진 유료 수집을 거부하지 않음:\n{out}")
    # 2026-10-19: 유료 수집은 회차 시작 때 담당자 답(00_collect_plan.yaml)이 숫자로 허용해야 하고, 상한, 정렬, 페이지는 그 파일 값
    sys.path.insert(0, str(SCRIPTS))
    import collect
    import contextlib
    import io
    base_paid = {"enabled": True, "max_pages_per_star": 1, "max_scrape_calls": 10, "scrape_below_db_reviews": 100}
    for plan, msg in [(None, "없이는 부르지 않습니다"), ("source: db\nmax_paid_calls: 0\n", "허용하지 않습니다"),
                      ("source: paid_below\nmax_paid_calls: 0\n", "허용하지 않습니다"), ("source: paid_all\nmax_paid_calls: 5\nsort: top\n", "recent나 helpful")]:
        pr = tmp / f"plan-{len(msg)}-{bool(plan)}"
        pr.mkdir(exist_ok=True)
        if plan:
            (pr / "00_collect_plan.yaml").write_text(plan, encoding="utf-8")
        err = io.StringIO()
        try:
            with contextlib.redirect_stderr(err):
                collect.collect_plan_paid(pr, base_paid)
            FAILS.append(f"수집 계획 거부 안 함: {plan}")
        except SystemExit:
            if msg not in err.getvalue():
                FAILS.append(f"수집 계획 거부 문구 다름({msg}): {err.getvalue()}")
    pr = tmp / "plan-ok"
    pr.mkdir(exist_ok=True)
    (pr / "00_collect_plan.yaml").write_text("source: paid_below\nmax_paid_calls: 30\nsort: helpful\npages_per_star: 2\npaid_below_db_reviews: 50\n", encoding="utf-8")
    got = collect.collect_plan_paid(pr, base_paid)
    eq("수집 계획 상한은 작은 쪽, 정렬과 페이지와 기준은 계획 값", (got["max_scrape_calls"], got["sort"], got["max_pages_per_star"], got["scrape_below_db_reviews"]),
       (10, "helpful", 2, 50))
    (pr / "00_collect_plan.yaml").write_text("source: paid_all\nmax_paid_calls: 5\n", encoding="utf-8")
    got = collect.collect_plan_paid(pr, base_paid)
    eq("paid_all은 selected 전부(기준 0), 정렬 기본 recent", (got["max_scrape_calls"], got["sort"], got["scrape_below_db_reviews"]), (5, "recent", 0))
    summary = {"fiveStar": {"percentage": 70}, "fourStar": {"percentage": 10}, "threeStar": {"percentage": 5},
               "twoStar": {"percentage": 5}, "oneStar": {"percentage": 10}}
    base = {"asin": "B0COLLECT1", "variant_asin": "B0COLLECT2", "verified_purchase": True, "vine_review": False,
            "helpful_vote_count": 3, "country": "US", "language": None, "rating_summary": summary,
            "total_ratings": 1234, "average_rating": 4.3, "scraped_at": None, "created_at": "2026-10-05T00:00:00"}
    revs = [
        {**base, "review_id": "R1TESTAAAA01", "rating": 1.0, "review_date": "2026-09-01", "title": "Rock &amp; roll",
         "review_text": "Smells like &quot;alcohol&quot;", "variant_specs": ["Size: 50 ml", "Scent: Rose"]},
        {**base, "review_id": "R1TESTAAAA02", "rating": 5.0, "review_date": "2026-09-02", "title": "Love",
         "review_text": "Lovely", "variant_specs": [], "language": "es"},
        {**base, "asin": "B0COLLECT1X", "review_id": "R1TESTXXXX01", "rating": 5.0, "review_date": "2026-09-03",
         "title": "Other", "review_text": "Other product", "variant_specs": []},
        {**base, "review_id": "R1TESTEMPTY1", "rating": 3.0, "review_date": "2026-09-04", "title": "Title only",
         "review_text": "  ", "variant_specs": []},
    ]
    (run_ / "raw" / "reviews_B0COLLECT1.json").write_text(json.dumps({"pages": [{"count": 3, "reviews": revs}]}),
                                                          encoding="utf-8")
    (run_ / "raw" / "product_B0COLLECT1.json").write_text(json.dumps([{
        "brandName": "BrandC", "parentAsin": "B0PARENT01", "title": "Test Eau de Parfum", "reviewRating": 4.4}]),
        encoding="utf-8")
    out = run("collect.py", "pull", run_, "--offline")
    sys.path.insert(0, str(SCRIPTS))
    from pipeline_io import ASIN_COLS, DIST_COLS, REVIEW_COLS, load_csv_or_die
    rv = load_csv_or_die(run_ / "02_reviews.csv", REVIEW_COLS)
    eq("수집 리뷰(부분일치로 딸려 온 ASIN과 본문 없는 리뷰 뺌)", [x["review_id"] for x in rv], ["R1TESTAAAA01", "R1TESTAAAA02"])
    log = json.loads((run_ / "02_collect_log.json").read_text(encoding="utf-8"))
    eq("본문 없는 리뷰 기록", (log["dropped_count"], log["dropped"]),
       (1, [{"review_id": "R1TESTEMPTY1", "asin": "B0COLLECT1", "star": 3, "reason": "본문 없음"}]))
    eq("수집 리뷰 칸", {k: rv[0][k] for k in ("star", "title", "body", "verified", "helpful_votes", "variant_asin",
                                          "variant_text", "brand", "language", "country")},
       {"star": "1", "title": "Rock & roll", "body": 'Smells like "alcohol"', "verified": "true", "helpful_votes": "3",
        "variant_asin": "B0COLLECT2", "variant_text": "Size: 50 ml; Scent: Rose", "brand": "BrandC", "language": "",
        "country": "US"})
    d = load_csv_or_die(run_ / "02_star_distribution.csv", DIST_COLS)[0]
    eq("수집 별점 분포", (d["s5"], d["s1"], d["total_ratings"], d["average_rating"], d["source"], d["captured_at"]),
       ("70", "10", "1234", "4.3", "rating_summary", "2026-10-05T00:00:00"))
    a = load_csv_or_die(run_ / "01_asins.csv", ASIN_COLS)
    eq("01_asins.csv 빈칸 채움", (a[0]["brand"], a[0]["title"], a[0]["amazon_rating"], a[0]["parent_asin"], a[1]["brand"]),
       ("BrandC", "Test Eau de Parfum", "4.4", "B0PARENT01", ""))
    if "es 1" not in out or "blank 1" not in out:
        FAILS.append(f"언어별 건수를 찍지 않음:\n{out}")
    # v1 파일(선택 칸 포함)도 입력 검사를 지나고, 아마존 review_id(R...)에는 asin 경고를 내지 않는다
    out = run("check_inputs.py", run_)
    if "asin으로 시작하지 않습니다" in out:
        FAILS.append("아마존 review_id에 asin 경고를 냄")
    # 본문 없는 리뷰 개수가 데이터 출처 문장에 들어간다
    sys.path.insert(0, str(SCRIPTS))
    from weight import data_notes
    notes = data_notes(run_, {"B0COLLECT1": d}, {"B0COLLECT1": {"sample_reviews": 2}},
                       {"sample_mean_star": 3.0, "weighted_mean_star": 3.0}, {"per_asin": {}})
    eq("데이터 출처 문장", notes["data_source"], "공유 리뷰 DB에서 받음, 본문 없는 리뷰 1개 제외")

    # 리포트 검사: 아마존 review_id(R...) 인용도 별점과 브랜드를 대조한다
    (run_ / "04_tags.jsonl").write_text(json.dumps({"review_id": "R1TESTAAAA01", "topic": "x", "sentiment": "negative",
                                                    "quote": "Smells like"}) + "\n", encoding="utf-8")
    (run_ / "05_tables.md").write_text("", encoding="utf-8")
    chapters = "\n\n".join(f"## {i}. 장\n\n**데이터 읽기** 내용" for i in range(1, 13)) + "\n\n## 부록: 방법과 한계\n"
    good = chapters + '\n> "알코올 냄새" (BrandC, 1★, R1TESTAAAA01)\n'
    (run_ / "06_report.md").write_text(good, encoding="utf-8")
    run("audit_quotes.py", "report", run_)
    q = json.loads((run_ / "07_quote_check.json").read_text(encoding="utf-8"))
    eq("아마존 ID 인용을 잡음", q["cited_review_ids"], ["R1TESTAAAA01"])
    (run_ / "06_report.md").write_text(good.replace("BrandC, 1★", "BrandD, 5★"), encoding="utf-8")
    out = run("audit_quotes.py", "report", run_, expect=1)
    if "실제는 1★" not in out or "01_asins.csv는 'BrandC'" not in out:
        FAILS.append(f"아마존 ID 인용의 별점과 브랜드 오류를 잡지 못함:\n{out}")
    (run_ / "06_report.md").write_text(good + "\n(BrandC, 2★, R9UNKNOWN0001)\n", encoding="utf-8")
    out = run("audit_quotes.py", "report", run_, expect=1)
    if "R9UNKNOWN0001: 없는 review_id" not in out:
        FAILS.append(f"없는 아마존 review_id를 잡지 못함:\n{out}")
    (run_ / "06_report.md").write_text(good + "\n반품·환불 불가\n", encoding="utf-8")
    out = run("audit_quotes.py", "report", run_, expect=1)
    if "가운뎃점" not in out:
        FAILS.append(f"리포트의 가운뎃점을 잡지 못함:\n{out}")


LANGS = ["", "", "", "es"]


def synth_run(root, name, asins):
    """정답 세트와 스키마 표본 시험용 가짜 회차. asins = {asin: [(별점, 개수), ...]}"""
    run_ = root / name
    (run_ / "gold").mkdir(parents=True)
    (run_ / "01_asins.csv").write_text("asin,title,brand,price_usd,price_band,amazon_rating,status,reason\n" + "".join(
        f"{a},T {a},Brand{i},,,,selected,시험\n" for i, a in enumerate(asins)), encoding="utf-8")
    lines = ["review_id,asin,star,date,title,body,verified,vine,helpful_votes,variant_asin,variant_text,brand,language,country"]
    dist = ["asin,s5,s4,s3,s2,s1,total_ratings"]
    for i, (a, spec) in enumerate(asins.items()):
        k = 0
        for star, n in spec:
            for _ in range(n):
                k += 1
                lang = LANGS[k % len(LANGS)] if not a.endswith("6") else ("" if k <= 3 else "es")
                body = "short" if k % 7 == 0 else f"Review {k} of {a} talks about the scent and how long it lasts."
                lines.append(f"R{a[-4:]}X{k:05d},{a},{star},2026-09-{1 + k % 28:02d},Title {k},\"{body}\",true,false,0,{a},,"
                             f"Brand{i},{lang},US")
        dist.append(f"{a},60,10,10,10,10,100")
    (run_ / "02_reviews.csv").write_text("\n".join(lines) + "\n", encoding="utf-8")
    (run_ / "02_star_distribution.csv").write_text("\n".join(dist) + "\n", encoding="utf-8")
    return run_


def test_pick_and_sheet(tmp):
    """eval_gold.py pick: 정답 세트 30개(ASIN마다 5개, 영어, 본문 40자 이상, 부정과 긍정 포함), 시드 고정,
    스키마 표본 ASIN마다 25개(별점마다 고르게). sheet: 리뷰 30개와 주제가 다 들어가고, 내보내기 형식이 맞다."""
    sys.path.insert(0, str(SCRIPTS))
    from pipeline_io import REVIEW_COLS, load_csv_or_die
    asins = {f"B0SYNTH00{i}": [(1, 12), (2, 10), (3, 8), (4, 10), (5, 14)] for i in range(1, 6)}
    asins["B0SYNTH006"] = [(1, 3), (5, 30)]   # 영어 리뷰가 1★ 3개뿐인 ASIN: 정답 세트 2개 모자람
    run_ = synth_run(tmp, "synth-2026-10-07", asins)
    run("eval_gold.py", "pick", run_)
    reviews = {x["review_id"]: x for x in load_csv_or_die(run_ / "02_reviews.csv", REVIEW_COLS)}
    gold_text = (run_ / "gold" / "gold_reviews.csv").read_text(encoding="utf-8-sig")
    import csv as _csv
    gold = list(_csv.DictReader(gold_text.splitlines()))
    eq("정답 세트 수", len(gold), 30)
    bad = [g["review_id"] for g in gold if reviews[g["review_id"]]["language"] or len(reviews[g["review_id"]]["body"].strip()) < 40]
    eq("정답 세트 조건(영어, 40자 이상)", bad, [])
    by = {}
    for g in gold:
        by.setdefault(g["asin"], []).append(int(g["star"]))
    eq("정답 세트 ASIN마다 부정과 긍정", [a for a, st in by.items() if a != "B0SYNTH006"
                                     and not (any(x <= 2 for x in st) and any(x >= 4 for x in st))], [])
    eq("ASIN마다 5개 이상, 모자란 ASIN은 조건 맞는 3개", (min(len(by[a]) for a in by if a != "B0SYNTH006"), len(by["B0SYNTH006"])),
       (5, 3))
    log = json.loads((run_ / "gold" / "gold_pick_log.json").read_text(encoding="utf-8"))
    eq("모자란 ASIN 기록", (log["short"], sum(log["filled_from"].values()), log["unfilled"]), ({"B0SYNTH006": 2}, 2, 0))
    run("eval_gold.py", "pick", run_)
    eq("시드 고정(다시 돌려도 같음)", (run_ / "gold" / "gold_reviews.csv").read_text(encoding="utf-8-sig"), gold_text)
    sample = load_csv_or_die(run_ / "03_schema_sample.csv", REVIEW_COLS)
    gold_ids = {g["review_id"] for g in gold}
    eq("스키마 표본 수와 정답 세트 제외", (len(sample), [x["review_id"] for x in sample if x["review_id"] in gold_ids]), (150, []))
    cnt = {}
    for x in sample:
        cnt.setdefault(x["asin"], {}).setdefault(x["star"], 0)
        cnt[x["asin"]][x["star"]] += 1
    eq("스키마 표본 ASIN마다 25개", sorted({sum(v.values()) for v in cnt.values()}), [25])
    st1 = cnt["B0SYNTH001"]
    eq("스키마 표본 별점마다 고르게(B0SYNTH001)", sorted(st1.items()), [("1", 5), ("2", 5), ("3", 5), ("4", 5), ("5", 5)])
    eq("스키마 표본에 영어 아닌 리뷰도 들어감", any(x["language"] for x in sample), True)
    eq("스키마 표본 칸이 02_reviews.csv와 같음",
       (run_ / "03_schema_sample.csv").read_text(encoding="utf-8-sig").splitlines()[0],
       (run_ / "02_reviews.csv").read_text(encoding="utf-8").splitlines()[0])

    # 태깅 화면
    (run_ / "03_schema_approved.yaml").write_text("""topics:
  - id: scent
    name_ko: 향
    side: P
    definition: 향 자체의 호불호
    include: [향 계열]
    exclude: [지속 시간]
  - id: longevity_projection
    name_ko: 지속력과 확산력
    side: P
    definition: 향이 몇 시간 가는지
  - id: price_value
    name_ko: 가격 대비 가치
    side: B
    definition: 가격
""", encoding="utf-8")
    run("eval_gold.py", "sheet", run_)
    html = (run_ / "gold" / "gold_tagging.html").read_text(encoding="utf-8")
    eq("화면에 정답 세트 리뷰 30개", [g["review_id"] for g in gold if g["review_id"] not in html], [])
    eq("화면에 주제 다 들어감", [t for t in ("scent", "longevity_projection", "price_value", "지속력과 확산력") if t not in html], [])
    eq("화면에 태거 결과 없음", ("04_tags" in html, "quote" in html), (False, False))
    js = html.split("// toJsonl:start")[1].split("// toJsonl:end")[0]
    node = shutil.which("node")
    if node:
        test_js = js + """
const out = toJsonl({"R2": {"scent": "negative", "price_value": "positive"}, "R1": {"longevity_projection": "mixed"}},
  [{review_id: "R1"}, {review_id: "R2"}, {review_id: "R3"}],
  [{id: "scent"}, {id: "longevity_projection"}, {id: "price_value"}]);
process.stdout.write(out);
"""
        p = subprocess.run([node, "-e", test_js], capture_output=True, text=True, encoding="utf-8")
        eq("내보내기 형식", [json.loads(l) for l in p.stdout.splitlines()], [
            {"review_id": "R1", "topic": "longevity_projection", "sentiment": "mixed"},
            {"review_id": "R2", "topic": "scent", "sentiment": "negative"},
            {"review_id": "R2", "topic": "price_value", "sentiment": "positive"}])
    else:
        FAILS.append("node가 없어 내보내기 형식을 시험하지 못함")

    # 한 화면(2026-10-10): 승인본이 없으면 초안으로 화면을 만들고 스키마 확인을 함께, 필수 주제(전체 만족도, 효과)
    one = synth_run(tmp, "one-2026-10-10", {"B0ONE00001": [(1, 12), (2, 10), (3, 8), (4, 10), (5, 14)]})
    run("eval_gold.py", "pick", one, "--per-asin", "5")
    (one / "03_schema_draft.yaml").write_text("""topics:
  - id: overall
    name_ko: 전체 만족도
    side: P
    definition: 총평
  - id: removal_effect
    name_ko: 제거 효과
    side: P
    common_id: performance
    definition: 털이 잘 지워지나
    evidence_count: 40
  - id: smell
    name_ko: 냄새
    side: P
    definition: 냄새
  - id: price_value
    name_ko: 가격 대비 가치
    side: B
    definition: 가격
""", encoding="utf-8")
    out = run("eval_gold.py", "sheet", one)
    h1 = (one / "gold" / "gold_tagging.html").read_text(encoding="utf-8")
    d1 = json.loads(h1.split('<script type="application/json" id="data">')[1].split("</script>")[0].replace("<\\/", "</"))
    eq("초안 화면: 기준 파일, 모드, 필수 주제", (d1["schema_file"], d1["schema_mode"], d1["required"]),
       ("03_schema_draft.yaml", "draft", ["overall", "removal_effect"]))
    node = shutil.which("node")
    if node:
        js1 = h1.split("// toJsonl:start")[1].split("// toJsonl:end")[0] + h1.split("// schemaReview:start")[1].split("// schemaReview:end")[0]
        test_js = js1 + """
const a = toJsonl({"R1": {"overall": "positive", "removal_effect": "none", "smell": "negative"}}, [{review_id: "R1"}],
  [{id: "overall"}, {id: "removal_effect"}, {id: "smell"}]);
const b = schemaReview({"smell": {decision: "edit", note: "냄새와 향을 나눔"}}, [{id: "overall"}, {id: "smell"}], "one", "03_schema_draft.yaml");
process.stdout.write(JSON.stringify([a, b.topics]));
"""
        p = subprocess.run([node, "-e", test_js], capture_output=True, text=True, encoding="utf-8")
        got = json.loads(p.stdout)
        eq("언급 없음(none)은 내보내지 않음", [json.loads(l) for l in got[0].splitlines()],
           [{"review_id": "R1", "topic": "overall", "sentiment": "positive"}, {"review_id": "R1", "topic": "smell", "sentiment": "negative"}])
        eq("스키마 확인 내보내기(기본값 승인)", got[1], [{"id": "overall", "decision": "approve", "note": ""},
                                                  {"id": "smell", "decision": "edit", "note": "냄새와 향을 나눔"}])
    rv = {"run": "one", "topics": [{"id": t, "decision": "approve", "note": ""} for t in ("overall", "removal_effect", "smell", "price_value")]}
    rv["topics"][2] = {"id": "smell", "decision": "drop", "note": "다른 주제와 겹침"}
    (one / "03_schema_review.json").write_text(json.dumps(rv, ensure_ascii=False), encoding="utf-8")
    out = run("eval_gold.py", "schema-approve", one, "--approved-at", "2026-10-10T10:00Z", "--approved-by", "시험", expect=1)
    eq("고칠 곳이 있으면 승인본을 만들지 않음", ((one / "03_schema_approved.yaml").exists(), "smell: 빼기" in out), (False, True))
    rv["topics"][2] = {"id": "smell", "decision": "approve", "note": ""}
    (one / "03_schema_review.json").write_text(json.dumps(rv, ensure_ascii=False), encoding="utf-8")
    run("eval_gold.py", "schema-approve", one, "--approved-at", "2026-10-10T10:00Z", "--approved-by", "시험")
    import yaml
    ap_ = yaml.safe_load((one / "03_schema_approved.yaml").read_text(encoding="utf-8"))
    eq("모두 승인이면 초안 그대로 승인본", (ap_["approved_by"], [t["id"] for t in ap_["topics"]]),
       ("시험", ["overall", "removal_effect", "smell", "price_value"]))
    # 승인 때 smell을 빼고 removal_effect를 effect로 바꿨다면: 정답 태그를 맞춤
    ap_["topics"] = [t for t in ap_["topics"] if t["id"] != "smell"]
    ap_["topics"][1]["id"] = "effect"
    (one / "03_schema_approved.yaml").write_text(yaml.safe_dump(ap_, allow_unicode=True, sort_keys=False), encoding="utf-8")
    gids = [g["review_id"] for g in _csv.DictReader((one / "gold" / "gold_reviews.csv").read_text(encoding="utf-8-sig").splitlines())]
    (one / "gold" / "gold_tags.jsonl").write_text("".join(json.dumps(x) + "\n" for x in (
        [{"review_id": g, "topic": "overall", "sentiment": "positive"} for g in gids]
        + [{"review_id": gids[0], "topic": "removal_effect", "sentiment": "negative"}, {"review_id": gids[1], "topic": "smell", "sentiment": "negative"}])),
        encoding="utf-8")
    run("eval_gold.py", "gold", one, expect=1)
    out = run("eval_gold.py", "gold", one, "--rename", "removal_effect:effect", "--drop-unknown")
    fixed = [json.loads(l) for l in (one / "gold" / "gold_tags.jsonl").read_text(encoding="utf-8").splitlines()]
    eq("정답 태그 맞춤(이름 바꿈 1, 뺀 주제 1)", (sorted({t["topic"] for t in fixed}), len(fixed), (one / "gold" / "gold_tags.before_fix.jsonl").exists()),
       (["effect", "overall"], len(gids) + 1, True))

    # 정답 세트 묶음과 묶음 크기
    run("tag_batches.py", "plan", run_, "--size", "20")
    bp = json.loads((run_ / "04_batches.json").read_text(encoding="utf-8"))
    sizes = [len(b["review_ids"]) for b in bp["batches"] if b["asin"] == "B0SYNTH001"]
    eq("묶음 크기(54개를 20개씩)", sizes, [20, 20, 14])
    eq("gold 묶음", (bp["batches"][-1]["batch_id"], sorted(bp["batches"][-1]["review_ids"]), bp["batches"][-1]["models"]),
       ("gold", sorted(gold_ids), ["sonnet", "top"]))
    eq("시험 태깅은 리뷰가 가장 적은 ASIN", (bp["pilot_asin"], bp["pilot_batches"]),
       ("B0SYNTH006", ["B0SYNTH006_01", "B0SYNTH006_02", "gold"]))
    first = [reviews[x] for x in bp["batches"][0]["review_ids"]]
    eq("묶음 안은 날짜, review_id 순", [(x["date"], x["review_id"]) for x in first],
       sorted((x["date"], x["review_id"]) for x in first))
    with open(run_ / "04_tag_input" / f"{bp['batches'][0]['batch_id']}.csv", encoding="utf-8-sig", newline="") as f:
        inp = list(csv.DictReader(f))
    with open(run_ / "04_tag_input" / "gold.csv", encoding="utf-8-sig", newline="") as f:
        ginp = list(csv.DictReader(f))
    eq("묶음 입력 파일은 그 묶음 리뷰만, 같은 순서, 같은 본문",
       ([x["review_id"] for x in inp], [x["body"] for x in inp], sorted(x["review_id"] for x in ginp),
        len(list((run_ / "04_tag_input").glob("*.csv")))),
       (bp["batches"][0]["review_ids"], [reviews[x]["body"] for x in bp["batches"][0]["review_ids"]], sorted(gold_ids),
        len(bp["batches"])))


def test_audit_sample(tmp):
    """eval_gold.py audit-sample: ASIN마다 25개, 감성 비율대로, 부정이 있으면 최소 3개, 시드 고정."""
    run_ = tmp / "audit-sample"
    run_.mkdir()
    lines = ["review_id,asin,star,date,title,body,verified,vine"]
    tags = []
    for a, (npos, nneg, nmix) in {"B0AUDIT001": (60, 2, 8), "B0AUDIT002": (20, 0, 0)}.items():
        k = 0
        for sent, n in (("positive", npos), ("negative", nneg), ("mixed", nmix)):
            for _ in range(n):
                k += 1
                rid = f"R{a[-3:]}AUD{k:04d}"
                lines.append(f"{rid},{a},4,2026-09-01,T,Body text,true,false")
                tags.append({"review_id": rid, "topic": "scent", "sentiment": sent, "quote": "Body"})
    (run_ / "02_reviews.csv").write_text("\n".join(lines) + "\n", encoding="utf-8")
    (run_ / "04_tags.jsonl").write_text("".join(json.dumps(t) + "\n" for t in tags), encoding="utf-8")
    run("eval_gold.py", "audit-sample", run_, "--n", "50")
    sample = [json.loads(l) for l in (run_ / "04_audit_sample.jsonl").read_text(encoding="utf-8").splitlines()]
    c1 = {}
    for t in sample:
        if t["review_id"].startswith("R001"):
            c1[t["sentiment"]] = c1.get(t["sentiment"], 0) + 1
    # B0AUDIT001: 70개 중 25개. 비율대로면 긍정 21.4, 부정 0.7, 혼합 2.9 → 21, 1, 3. 부정 최소 min(3, 2) = 2개
    eq("감사 표본 구성(부정 최소)", c1, {"positive": 20, "negative": 2, "mixed": 3})
    eq("감사 표본 ASIN 2는 20개 전부", sum(1 for t in sample if t["review_id"].startswith("R002")), 20)
    first = (run_ / "04_audit_sample.jsonl").read_text(encoding="utf-8")
    run("eval_gold.py", "audit-sample", run_, "--n", "50")
    eq("감사 표본 시드 고정", (run_ / "04_audit_sample.jsonl").read_text(encoding="utf-8"), first)
    # 감사자 둘로 나누기(2026-10-14): 리뷰 단위로 반쪽, 반쪽마다 FAIL 비율, 합칠 때 빠짐과 겹침, 자기 반쪽 밖 판정을 잡음
    halves = [[json.loads(l) for l in (run_ / f"04_audit_sample_p{k}.jsonl").read_text(encoding="utf-8").splitlines()] for k in (1, 2)]
    eq("태그 반쪽 수와 합", (len(halves[0]), len(halves[1]), sorted(json.dumps(x, sort_keys=True) for x in halves[0] + halves[1]) ==
       sorted(json.dumps(x, sort_keys=True) for x in sample)), (23, 22, True))
    eq("한 리뷰는 한 반쪽에만", {t["review_id"] for t in halves[0]} & {t["review_id"] for t in halves[1]}, set())
    import yaml
    h0, h1 = halves[0][0], halves[1][0]
    (run_ / "04_tag_audit_p1.yaml").write_text(yaml.safe_dump({"audit": {"stage": "tags", "checked": 23, "findings": [
        {"review_id": h0["review_id"], "topic": "scent", "status": "FAIL"}]}}), encoding="utf-8")
    run("eval_gold.py", "audit", run_, expect=2)                   # p2 판정이 아직 없으면 합치지 않음(중단)
    (run_ / "04_tag_audit_p2.yaml").write_text(yaml.safe_dump({"audit": {"stage": "tags", "checked": 22, "findings": [],
        "missed": [{"review_id": h1["review_id"], "topic": "price_value", "reason": "시험"}]}}), encoding="utf-8")
    out = run("eval_gold.py", "audit", run_, "--max-fail", "0.10")
    au = json.loads((run_ / "04_tag_audit_summary.json").read_text(encoding="utf-8"))
    eq("태그 반쪽 합친 집계", (au["status"], au["fail"], au["missed"], [(p_["part"], p_["fail"], p_["fail_rate"], p_["missed"]) for p_ in au["parts"]],
       au["merge_problems"]), ("PASS", 1, 1, [("p1", 1, 0.043, 0), ("p2", 0, 0.0, 1)], []))
    eq("태그 합치기 확인 문구", "표본 빠짐과 겹침 없음" in out, True)
    (run_ / "04_tag_audit_p2.yaml").write_text(yaml.safe_dump({"audit": {"stage": "tags", "checked": 22, "findings": [
        {"review_id": h0["review_id"], "topic": "scent", "status": "FAIL"}]}}), encoding="utf-8")
    out = run("eval_gold.py", "audit", run_, "--max-fail", "0.10", expect=1)
    eq("자기 반쪽 밖 판정을 잡음", ("INCOMPLETE" in out, "자기 반쪽에 없는 태그를 판정함 1개" in out), (True, True))


def test_render_html(tmp):
    """render_html.py: 필터(py_match), 문장 속 개수 연결(Linker), 06_report.md 읽기, 검사가 틀린 숫자와 드릴다운을 잡는지"""
    sys.path.insert(0, str(SCRIPTS))
    import render_html as rh
    eq("표기", (rh.f_int(1212), rh.f_pct(5.0), rh.f_star(4.476), rh.f_gap(-3.27), rh.f_usd(35.0)),
       ("1,212", "5.0%", "4.48★", "-3.27", "35.00달러"))
    # 리뷰 3개: [id, asin, 변형, 별점, 제목, 본문, 날짜, 확인, 도움돼요, 브랜드, 가중치, 변형 텍스트, Vine, 변형 키마다 변형 이름]
    D = {"R": [["R1", "A", "", 1, "t", "b", "2025-03-01", 1, 2, 0, 1.0, "", 0, ["1 fl oz"]],
               ["R2", "A", "", 5, "t", "b", "2026-08-01", 0, 0, 0, 1.0, "", 1, ["3.3 fl oz"]],
               ["R3", "B", "", 2, "t", "headache", "2026-09-01", 1, 0, 1, 1.0, "", 0, [""]]],
         "T": [[0, 0, 1, "q"], [0, 1, 1, "q"], [1, 0, 0, "q"], [2, 0, 2, "q"], [2, 1, 1, "q"]],
         "L": [[0, 0], [1, 1], [4, 1]], "labels": [[0, 1, "금방 날아감", "fades_fast"], [1, 1, "가짜", "fake"]],
         "sid": ["longevity_projection", "trust"]}
    cnt = lambda f: len(rh.py_match(D, f))
    eq("필터", [cnt({"sub": 0}), cnt({"sub": 0, "sent": 1}), cnt({"pair": [0, 1]}), cnt({"label": 1}), cnt({"labels": [0, 1]}),
                cnt({"brand": 0, "verified": 1}), cnt({"dfrom": "2026-01-01", "dto": "2026-08-31"}), cnt({"vine": 1}), cnt({"hv": 1}),
                cnt({"asin": "A", "vlabel": "3.3 fl oz"}), cnt({"rids": [0, 2], "star": 2}), cnt({"sent": 2})],
       [3, 1, 1, 2, 1, 1, 1, 1, 1, 1, 1, 1])
    # 문장 속 '<라벨> 리뷰 n개'는 07b 값과 같을 때만 연결하고, 다르면 misses에 남긴다
    counts = {"topics": {"longevity_projection.negative": {"topic": "longevity_projection", "direction": "negative", "labels": [
        {"id": "fades_fast", "name_ko": "금방 날아감", "reviews": 1, "by_asin": {"A": 1}}]}}}
    m = {"brand_deep": [{"brand": "BrandA", "asins": ["A"]}, {"brand": "BrandB", "asins": ["B"]}]}
    lk = rh.Linker({"sym": {"두통": [2]}}, counts, {("longevity_projection", "negative", "fades_fast"): 0}, None, {"BrandA": 0, "BrandB": 1}, m, {"두통": [2]})
    h = lk("세부: 금방 날아감 리뷰 1개, 금방 날아감 리뷰 7개. 두통 1개(가중 0.1%)")
    eq("문장 속 개수 연결", (h.count('data-n="1"'), "금방 날아감 리뷰 7개" in h, lk.misses), (2, True, ["전체: 금방 날아감 7(07b 값과 다름)"]))
    h = lk("세부: 금방 날아감 리뷰 1개", brand="BrandB")
    eq("브랜드 안 개수는 by_asin 합", lk.misses[-1], "BrandB: 금방 날아감 1(07b 값과 다름)")
    items = rh.numbered_items(["1. **주장 하나** 본문 숫자 3개.", '   > "인용" (BrandA, 2★, R1ABCDEFGH2)', "", "문단 하나"])
    eq("번호 목록과 인용", (items[0]["claim"], items[0]["body"], items[0]["quotes"], items[1]),
       ("주장 하나", "본문 숫자 3개.", [("인용", "BrandA", "2", "R1ABCDEFGH2")], {"para": "문단 하나"}))
    # 실제 회차가 있으면 그 HTML로 검사가 틀린 숫자와 드릴다운, 가운뎃점, 외부 참조를 잡는지 본다
    real = HERE.parent / "runs" / "perfume-db-2026-10-07"
    if not (real / "06_report.html").exists():
        print("  (render_html 검사 시험: 실제 회차 HTML이 없어 건너뜀)")
        return
    r = Path(tmp) / "html_check"
    r.mkdir()
    for n in ("06_report.html", "06_report_html_numbers.json", "05_metrics.json", "07b_issue_counts.json", "07c_safety_summary.json",
              "07c_safety_verdicts.yaml"):
        shutil.copy(real / n, r / n)
    run("render_html.py", "check", r)
    page = (r / "06_report.html").read_text(encoding="utf-8")
    k = json.loads((r / "06_report_html_numbers.json").read_text(encoding="utf-8"))["numbers"][0]
    bad = re.sub(rf'(<span data-k="{k["k"]}"[^>]*>)[^<]*', r"\g<1>999", page, count=1)
    bad = re.sub(r'data-n="(\d+)"', lambda mt: f'data-n="{int(mt.group(1)) + 1}"', bad, count=1)
    bad = bad.replace("</body>", '<p>반품·환불</p><img src="https://example.com/x.png"></body>')
    (r / "06_report.html").write_text(bad, encoding="utf-8")
    out = run("render_html.py", "check", r, expect=1)
    for want in (f"숫자 {k['k']}", "드릴다운", "가운뎃점", "외부 참조"):
        if want not in out:
            FAILS.append(f"HTML 검사가 '{want}'를 잡지 못함:\n{out}")


def test_market_detail(tmp):
    """market.py(검색어 규칙, 응답 행 꺼내기, 이미 받은 응답은 다시 부르지 않음)와 detail.py(표본, 초안 검사)"""
    sys.path.insert(0, str(SCRIPTS))
    import market
    import market_build
    import yaml
    W = tuple(yaml.safe_load((HERE.parent / "config" / "categories" / "perfume.yaml").read_text(encoding="utf-8"))["market"]["term_words"])
    eq("향수 검색어 규칙(config market.term_words)", [market_build.term_rule(t, ["Lattafa"], W) for t in ("perfume for women", "now", "lattafa khamrah", "Eau de Toilette men")],
       [True, False, True, True])
    eq("응답 행", (market.rows([1, 2]), market.rows({"pageInfo": {}, "payload": [{}, {}, {}]}), len(market.records({"payload": [{"a": 1}]}))),
       (2, 3, 1))
    raw = Path(tmp) / "mk" / "market" / "raw"
    raw.mkdir(parents=True)
    (raw / "subcategories_relevant_search_terms_Women_s_Eau_de_Parfum.json").write_text(json.dumps([
        {"searchTermValue": "now", "volume30Day": 900}, {"searchTermValue": "perfume", "volume30Day": 500},
        {"searchTermValue": "lattafa", "volume30Day": 400}, {"searchTermValue": "blue", "volume30Day": 300}]), encoding="utf-8")
    (raw / "subcategories_category_competitors_Women_s_Eau_de_Parfum.json").write_text(json.dumps({"payload": [{"brandName": "Lattafa"}]}),
                                                                                      encoding="utf-8")
    eq("검색량 상위(규칙 통과만)", market.top_terms(raw, 5, ("Women's Eau de Parfum",), W), ["perfume", "lattafa"])
    f = market.Fetcher(Path(tmp) / "mk", 1)
    (raw / "products_history_B0X.json").write_text(json.dumps({"salesRank": []}), encoding="utf-8")
    called = []
    market.call_tool = lambda *a, **k: called.append(a) or ("[]", [])
    got = f.get("products_history", {"asin": "B0X"}, "B0X")
    eq("이미 받은 응답은 다시 부르지 않음", (got, called, f.calls), ({"salesRank": []}, [], 0))
    f.get("products_history", {"asin": "B0Y"}, "B0Y")
    f.get("products_history", {"asin": "B0Z"}, "B0Z")
    log = [json.loads(l) for l in (Path(tmp) / "mk" / "market" / "calls.jsonl").read_text(encoding="utf-8").splitlines()]
    eq("호출 한도", (len(called), [x.get("error") for x in log]), (1, [None, "호출 한도"]))

    # detail.py sample: 정답 세트 제외, (ASIN, 별점 묶음) 고르게, 시드 고정
    r = Path(tmp) / "dt-2026-10-07"
    (r / "gold").mkdir(parents=True)
    lines = ["review_id,asin,star,date,title,body,verified,vine"]
    for i in range(60):
        a = "B0DT00001" + str(i % 2)
        lines.append(f"R{i:02d}DETAILXYZ,{a},{1 + i % 5},2026-09-01,T{i},Body {i} lasts 3 hours,true,false")
    (r / "02_reviews.csv").write_text("\n".join(lines) + "\n", encoding="utf-8")
    (r / "gold" / "gold_reviews.csv").write_text("review_id,asin,star,title,body\nR00DETAILXYZ,B0DT000010,1,T,B\n", encoding="utf-8")
    run("detail.py", "sample", r, "--n", "12")
    import csv as _csv
    with (r / "13_detail_sample.csv").open(encoding="utf-8") as fh:
        smp = list(_csv.DictReader(fh))
    first = (r / "13_detail_sample.csv").read_text(encoding="utf-8")
    run("detail.py", "sample", r, "--n", "12")
    eq("설계 표본", (len(smp), "R00DETAILXYZ" in {x["review_id"] for x in smp}, Counter(x["asin"] for x in smp),
                    (r / "13_detail_sample.csv").read_text(encoding="utf-8") == first),
       (12, False, Counter({"B0DT000010": 6, "B0DT000011": 6}), True))
    import yaml
    a, b = smp[0], smp[1]
    item = {"id": "duration_hours", "name_ko": "지속 시간", "format": "number", "unit": "시간", "definition": "d", "fill_rule": "f",
            "quote_required": True, "sample_count": 6, "guide_use": ["집중 분석"],
            "examples": [{"review_id": a["review_id"], "quote": "lasts 3 hours"}, {"review_id": b["review_id"], "quote": "lasts 3 hours"}]}
    (r / "13_detail_schema_draft.yaml").write_text(yaml.safe_dump({"items": [item]}, allow_unicode=True), encoding="utf-8")
    run("detail.py", "check", r)
    bad = dict(item, format="choice", sample_count=3, guide_use=["기타"],
               examples=[{"review_id": "R00DETAILXYZ", "quote": "x"}, {"review_id": a["review_id"], "quote": "not in text"}])
    (r / "13_detail_schema_draft.yaml").write_text(yaml.safe_dump({"items": [bad]}, allow_unicode=True), encoding="utf-8")
    out = run("detail.py", "check", r, expect=1)
    for want in ("allowed_values", "최소 5개", "guide_use", "정답 세트", "원문에 없습니다"):
        if want not in out:
            FAILS.append(f"설계 초안 검사가 '{want}'를 잡지 못함:\n{out}")


def test_guide_pipeline(tmp):
    """detail.py 승인(두 곳 고침), 묶음, 추출 검사(버린 인용, extra 조건), 개수와 중앙값, 감사 집계. research.py 원문 찾기.
    render_guide_html의 [m:키] 바꾸기."""
    import yaml
    r = Path(tmp) / "gd-2026-10-07"
    r.mkdir()
    lines = ["review_id,asin,star,date,title,body,verified,vine"]
    for i in range(6):
        lines.append(f"R{i:02d}GUIDEXYZ,B0GD000001,{1 + i % 5},2026-09-0{1 + i},T{i},Lasts {i + 1} hours on my wrist. vanilla is too much,true,false")
    (r / "02_reviews.csv").write_text("\n".join(lines) + "\n", encoding="utf-8")
    (r / "02_star_distribution.csv").write_text("asin,s5,s4,s3,s2,s1,total_ratings\nB0GD000001,20,20,20,20,20,100\n", encoding="utf-8")
    draft = {"items": [
        {"id": "hours", "name_ko": "시간", "format": "number", "unit": "시간", "fill_rule": "숫자", "allowed_values": None},
        {"id": "ctx", "name_ko": "맥락", "format": "choice", "fill_rule": "말할 때",
         "allowed_values": [{"value": "gift", "ko": "선물"}, {"value": "first_or_blind", "ko": "처음이나 블라인드"}]},
        {"id": "note", "name_ko": "노트", "format": "choice", "fill_rule": "낱말",
         "allowed_values": [{"value": "vanilla", "ko": "바닐라"}, {"value": "other", "ko": "그 밖"}]}]}
    (r / "13_detail_schema_draft.yaml").write_text(yaml.safe_dump(draft, allow_unicode=True), encoding="utf-8")
    (r / "13_detail_schema_edits.yaml").write_text(yaml.safe_dump({
        "split_values": [{"item": "ctx", "value": "first_or_blind", "into": [{"value": "first", "ko": "처음"}, {"value": "blind", "ko": "블라인드"}],
                          "rule": "둘 다면 둘 다"}],
        "extra": [{"item": "note", "field": "note_word", "when_value": "other", "format": "text", "rule": "other면 낱말"}]},
        allow_unicode=True), encoding="utf-8")
    run("detail.py", "approve", r, "--approved-at", "2026-10-07T12:27Z", "--approved-by", "시험")
    ap = yaml.safe_load((r / "13_detail_schema_approved.yaml").read_text(encoding="utf-8"))
    it = {x["id"]: x for x in ap["items"]}
    eq("승인 두 곳 고침", ([v["value"] for v in it["ctx"]["allowed_values"]], it["note"]["extra"]["note_word"]["when_value"], ap["version"]),
       (["gift", "first", "blind"], "other", "approved"))
    run("detail.py", "plan", r, "--size", "4")
    plan = json.loads((r / "14_detail_batches.json").read_text(encoding="utf-8"))
    eq("추출 묶음", [(b["batch_id"], b["reviews"]) for b in plan["batches"]], [("B0GD000001_01", 4), ("B0GD000001_02", 2)])
    b1 = [{"review_id": f"R0{i}GUIDEXYZ", "item": "hours", "value": i + 1, "quote": f"Lasts {i + 1} hours"} for i in range(4)]
    b1 += [{"review_id": "R00GUIDEXYZ", "item": "note", "value": "vanilla", "quote": "vanilla is too much"},
           {"review_id": "R01GUIDEXYZ", "item": "note", "value": "vanilla", "quote": "not in the text"}]
    b2 = [{"review_id": "R04GUIDEXYZ", "item": None}, {"review_id": "R05GUIDEXYZ", "item": "note", "value": "other", "quote": "vanilla"}]
    (r / "14_details_B0GD000001_01.jsonl").write_text("".join(json.dumps(x) + "\n" for x in b1), encoding="utf-8")
    (r / "14_details_B0GD000001_02.jsonl").write_text("".join(json.dumps(x) + "\n" for x in b2), encoding="utf-8")
    out = run("detail.py", "extract-check", r, expect=1)
    chk = json.loads((r / "14_detail_check.json").read_text(encoding="utf-8"))
    eq("추출 검사 실패 묶음(인용이 원문에 없음, extra 없음)", chk["failed_batches"], ["B0GD000001_01", "B0GD000001_02"])
    if "note_word" not in out:
        FAILS.append(f"extra 조건을 잡지 못함:\n{out}")
    b2[1]["extra"] = {"note_word": "vanilla"}
    b1 = [x for x in b1 if x["quote"] != "not in the text"]     # 다시 뽑은 묶음에서 원문에 없는 인용이 빠졌다고 봄
    (r / "14_details_B0GD000001_01.jsonl").write_text("".join(json.dumps(x) + "\n" for x in b1), encoding="utf-8")
    (r / "14_details_B0GD000001_02.jsonl").write_text("".join(json.dumps(x) + "\n" for x in b2), encoding="utf-8")
    run("detail.py", "extract-check", r)
    chk = json.loads((r / "14_detail_check.json").read_text(encoding="utf-8"))
    cnt = json.loads((r / "14_detail_counts.json").read_text(encoding="utf-8"))
    eq("추출 값과 버린 인용", (chk["values"], chk["dropped_quotes"]), (6, 0))
    eq("숫자 항목 중앙값", (cnt["items"]["hours"]["median"], cnt["items"]["hours"]["reviews"]), (2.5, 4))
    eq("값 개수", [(v["value"], v["reviews"]) for v in cnt["items"]["note"]["values"]], [("vanilla", 1), ("other", 1)])
    run("detail.py", "audit-sample", r, "--n", "4")
    smp = [json.loads(l) for l in (r / "14b_detail_audit_sample.jsonl").read_text(encoding="utf-8").splitlines()]
    s0 = smp[0]
    (r / "14b_detail_audit.yaml").write_text(yaml.safe_dump({"audit": {"stage": "details", "checked": 4, "findings": [
        {"review_id": s0["review_id"], "item": s0["item"], "value": s0["value"], "status": "FAIL"}]}}), encoding="utf-8")
    run("detail.py", "audit", r, expect=1)
    au = json.loads((r / "14b_detail_audit_summary.json").read_text(encoding="utf-8"))
    eq("추출 감사 집계", (au["sample"], au["fail"], au["status"]), (4, 1, "FAIL"))
    # research.py: 원문 문장 찾기(따옴표, 공백, 대소문자, 줄 나눔 무시)
    sys.path.insert(0, str(SCRIPTS))
    import research
    page = "<p>The U.S. perfume market was valued at USD 9.21 billion in 2024</p><p>and is expected to grow at a CAGR of 5.1%.</p>"
    eq("출처 원문 찾기", (research.found("The U.S. perfume market was valued at USD 9.21 billion in 2024 and is expected to grow at a CAGR of 5.1%.", page),
                       research.found("valued at USD 10 billion", page)), (True, False))
    # research.py 보충 조사(2026-10-20): not_found와 unverified를 모으고, fu_ 주장을 합치고, 다시 합쳐도 같음
    rr = Path(tmp) / "rs-2026-10-20"
    rr.mkdir()
    (rr / "15_research.yaml").write_text(yaml.safe_dump({"claims": [
        {"id": "mkt_01", "area": "market", "claim_ko": "가", "url": "https://example.org/a", "quote": "a"},
        {"id": "reg_01", "area": "regulation", "claim_ko": "나", "url": "https://example.org/b", "quote": "b"}],
        "not_found": [{"area": "market", "what": "미국만의 규모", "tried": ["us widget market"]}]}, allow_unicode=True), encoding="utf-8")
    (rr / "15_research_check.json").write_text(json.dumps({"items": [
        {"id": "mkt_01", "area": "market", "url": "https://example.org/a", "status": "verified"},
        {"id": "reg_01", "area": "regulation", "url": "https://example.org/b", "status": "unverified", "reason": "페이지에 원문 문장이 없음"}]}), encoding="utf-8")
    run("research.py", "followup-plan", rr)
    fi = json.loads((rr / "15_research_followup_input.json").read_text(encoding="utf-8"))
    eq("보충 조사 대상", (fi["count"], fi["not_found"], fi["unverified"], fi["items"][1]["id"]), (2, 1, 1, "reg_01"))
    run("research.py", "followup-plan", rr, "--max", "1")
    fi1 = json.loads((rr / "15_research_followup_input.json").read_text(encoding="utf-8"))
    eq("보충 조사 상한(찾지 못한 것 먼저)", (fi1["count"], fi1["skipped"], fi1["items"][0]["kind"]), (1, 1, "not_found"))
    run("research.py", "followup-plan", rr)
    run("research.py", "merge", rr, expect=1)
    (rr / "15_research_followup.yaml").write_text(yaml.safe_dump({"claims": [
        {"id": "fu_reg_01", "area": "regulation", "claim_ko": "나", "url": "https://example.org/c", "quote": "c", "replaces": "reg_01"}],
        "not_found": []}, allow_unicode=True), encoding="utf-8")
    run("research.py", "merge", rr)
    run("research.py", "merge", rr)
    mg = yaml.safe_load((rr / "15_research.yaml").read_text(encoding="utf-8"))
    first = yaml.safe_load((rr / "15_research_first.yaml").read_text(encoding="utf-8"))
    eq("보충 조사 합치기(두 번 해도 같음)", ([c["id"] for c in mg["claims"]], mg["not_found"], mg["followup"]["added"], len(first["claims"]), len(first["not_found"])),
       (["mkt_01", "reg_01", "fu_reg_01"], [], 1, 2, 1))
    (rr / "15_research_followup.yaml").write_text(yaml.safe_dump({"claims": [{"id": "reg_02", "area": "regulation"}, {"id": "mkt_01"}]}), encoding="utf-8")
    out = run("research.py", "merge", rr, expect=1)
    # replay.py: 고른 단계와 뒤 단계 출력만 지우고 정답지는 복사하지 않음(2026-10-21)
    src = Path(tmp) / "rp" / "runs" / "zz-2026-10-21"
    (src / "gold").mkdir(parents=True)
    (src / "gold" / "gold_tags.jsonl").write_text("x", encoding="utf-8")
    for f in ["16_guide_metrics.json", "17_guide.md", "17_guide_v1.md", "18_guide_audit.yaml", "07_guide.html", "05_metrics.json", "timing.jsonl"]:
        (src / f).write_text("x", encoding="utf-8")
    (src / "state.json").write_text(json.dumps({"run": src.name, "steps": {"16_guide_metrics": {"status": "done"}, "07_weight": {"status": "done"}}}), encoding="utf-8")
    dest = Path(tmp) / "rp_out"
    run("replay.py", src, "zz-2026-10-21-replay", "--from", "16_guide_metrics", "--dest", dest)
    nr = dest / "zz-2026-10-21-replay"
    st = json.loads((nr / "state.json").read_text(encoding="utf-8"))
    eq("다시 돌리기 복사", (sorted(p.name for p in nr.iterdir()), list(st["steps"]), list((nr / "gold").iterdir())),
       (["05_metrics.json", "gold", "replay_info.json", "state.json"], ["07_weight"], []))
    run("replay.py", src, "zz-2026-10-21-r2", "--from", "17_guide_write", "--only", "--dest", dest)
    eq("다시 돌리기 --only", sorted(p.name for p in (dest / "zz-2026-10-21-r2").iterdir()),
       ["05_metrics.json", "07_guide.html", "16_guide_metrics.json", "18_guide_audit.yaml", "gold", "replay_info.json", "state.json"])
    run("replay.py", src, "other-2026-10-21", "--from", "17_guide_write", "--dest", dest, expect=2)
    # schedule_sim.py: 앞 단계를 바꾸면 회차 길이가 바뀜
    sr = Path(tmp) / "sim-2026-10-21"
    sr.mkdir()
    evs = []
    for sid, a0, a1 in [("01_inputs", 0, 1), ("02_schema_draft", 1, 6), ("03_schema_approval", 6, 8), ("13_detail_schema_draft", 8, 20)]:
        evs += [{"ts": f"2026-10-21T10:{a0:02d}:00+09:00", "event": "step_start", "step": sid}, {"ts": f"2026-10-21T10:{a1:02d}:00+09:00", "event": "step_end", "step": sid}]
    (sr / "timing.jsonl").write_text("\n".join(json.dumps(e) for e in evs) + "\n", encoding="utf-8")
    sout = run("schedule_sim.py", sr, "--pred", "13_detail_schema_draft=03_schema_approval")
    eq("순서 시뮬레이션(앞 단계를 승인으로 되돌리면 늦어짐)", "차이 +" in sout, True)
    # guide_metrics 회차 사실: 수집 계획 pick에 따라 상품 고른 방식 문장(2026-10-21)
    import guide_metrics as gm0
    gg = object.__new__(gm0.G)
    gg.run = rr
    (rr / "00_collect_plan.yaml").write_text("pick: manual\n", encoding="utf-8")
    gg.m = {"summary": {"reviews": 10, "asins": 2, "sample_mean_star": 3.0, "weighted_mean_star": 4.0}}
    gg.tables, gg.values, gg.asins = {}, {}, [{}, {}]
    gg.conf = {"duration_item": "d", "growth": {"min_volume": 1}}
    gg.item_name = lambda k: k
    cv = gg.caveats()
    eq("가이드 회차 사실(담당자 지정)", any("담당자가 직접 지정한 2개" in c for c in cv) and not any("매출 상위" in c or "사람이 확인" in c for c in cv), True)
    # guide_metrics.plan_problems: 품목 가이드 계획과 guide 절 대조(2026-10-20)
    import guide_metrics as gm
    plan = {"head_topic": "a", "direction_index": {"topic": "c", "high": {"name": "두꺼움"}, "low": {"name": "얇음"}},
            "focus": [{"id": "f1", "title": "F", "topics": ["a", "b"]}], "standards": [{"id": "s1", "title": "S", "topics": ["a"]}]}
    ok = {"head_topic": "a", "direction_index": {"topic": "c", "high": {"name": "두꺼움", "labels": ["thick"]}, "low": {"name": "얇음", "labels": ["thin"]}},
          "focus": [{"id": "f1", "title": "F", "topics": ["a", "b"], "items": ["x"]}], "standards": [{"id": "s1", "title": "S", "neg_labels": ["la"]}]}
    lt = {"thick": "c", "thin": "c", "la": "a", "lg": "g"}
    eq("가이드 계획 같음", gm.plan_problems(ok, plan, lt), [])
    bad = json.loads(json.dumps(ok)); bad["direction_index"]["topic"] = "g"; bad["standards"][0]["neg_labels"] = ["lg"]
    eq("가이드 계획 다름(방향 주제, 기준 라벨 주제)", len(gm.plan_problems(bad, plan, lt)), 2)
    # research.py: PDF 글자 읽기(2026-10-20)
    stream = b"BT /F1 12 Tf 72 720 Td (Widgets must carry a warning label.) Tj ET"
    objs = [b"<< /Type /Catalog /Pages 2 0 R >>", b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
            b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Contents 4 0 R /Resources << /Font << /F1 5 0 R >> >> >>",
            b"<< /Length %d >>\nstream\n" % len(stream) + stream + b"\nendstream", b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>"]
    pdf, offs = b"%PDF-1.4\n", []
    for i, o in enumerate(objs, 1):
        offs.append(len(pdf)); pdf += b"%d 0 obj\n" % i + o + b"\nendobj\n"
    xref = len(pdf)
    pdf += b"xref\n0 6\n0000000000 65535 f \n" + b"".join(b"%010d 00000 n \n" % x for x in offs)
    pdf += b"trailer << /Size 6 /Root 1 0 R >>\nstartxref\n%d\n%%%%EOF" % xref
    pt, perr = research.pdf_text(pdf)
    eq("PDF 글자 읽기", (perr, research.found("must carry a warning label", pt or "")), (None, True))
    eq("글자 없는 PDF", research.pdf_text(b"%PDF-1.4 broken")[0], None)
    # wait_files.py: 다 있으면 0, 빠지면 timeout 뒤 1
    (rr / "a.md").write_text("x", encoding="utf-8")
    run("wait_files.py", rr, "a.md", "--settle", "0", "--timeout", "5", "--poll", "0.2")
    wout = run("wait_files.py", rr, "a.md", "b.md", "--settle", "0", "--timeout", "0.5", "--poll", "0.2", expect=1)
    eq("파일 기다리기 빠진 파일", "b.md" in wout, True)
    eq("보충 조사 id 검사", ("reg_02: id가 fu_로 시작하지 않음" in out, "mkt_01: id가 fu_로 시작하지 않음" in out), (True, True))
    # render_guide_html: [m:키]는 그 키의 표기를 찾아 링크로, 표기가 없거나 확인 안 된 출처는 기록
    import render_guide_html as rg
    g = object.__new__(rg.R)
    g.V = {"a.n": {"text": "10.0%", "ev": "ev.a"}, "b.n": {"text": "3개", "ev": None}}
    g.M = {"ev": {"ev.a": {"n": 4}, "ev.z": {"n": 0}}}
    g.claims = {"mkt_01": {"id": "mkt_01", "url": "https://example.org/x", "source_name": "x"}}
    g.nums, g.misses, g.rmisses, g.used_claims = [], [], [], set()
    h = g.inline("부정 10.0% [m:a.n], 모두 3개 [m:b.n], 틀린 5.0% [m:a.n], 시장 [r:mkt_01] [r:reg_99]")
    eq("가이드 표시 바꾸기", (h.count('data-drill="ev"'), len(g.nums), len(g.misses), g.rmisses, "[m:" in h, 'href="https://example.org/x"' in h),
       (1, 2, 1, ["reg_99"], False, True))
    eq("리뷰 0개 근거 묶음은 링크가 아님", ("data-drill" in g.tnum("0개", "ev.z"), "data-drill" in g.tnum("4개", "ev.a")), (False, True))


def test_speaker_review_fixes():
    """2026-10-15 스피커 06, 07 검토 다섯 가지(모든 품목 규칙): 도움돼요 분모(3★ 포함), 점유율 단위 확인, 안전 기준 범위,
    가정 값은 머리 숫자 금지, 성별 검색어가 없으면 성별 표와 문장 없음. 견고성 뒤집힘은 test_robustness_specs."""
    sys.path.insert(0, str(SCRIPTS))
    import sections
    import guide_metrics as gm
    import guide_check as gc
    import render_guide_html as rg
    # 1. 도움돼요: 1~2★ 6표, 3★ 2표, 4~5★ 2표 -> 합계 10표 대비 60.0%, 20.0%, 20.0%(3★를 빼고 나누면 75%, 25%가 됨)
    rv = [{"review_id": "h1", "asin": "A", "star": "1", "title": "t", "verified": "true", "vine": "false", "helpful_votes": "6"},
          {"review_id": "h2", "asin": "A", "star": "3", "title": "t", "verified": "true", "vine": "false", "helpful_votes": "2"},
          {"review_id": "h3", "asin": "A", "star": "5", "title": "t", "verified": "true", "vine": "false", "helpful_votes": "2"}]
    ts = sections.trust_signals(rv, [], ("overall",))
    eq("도움돼요 별점 쪽 비율은 합계 대비", (ts["helpful_total"], ts["helpful_negative_pct"], ts["helpful_mid_pct"], ts["helpful_positive_pct"]),
       (10, 60.0, 20.0, 20.0))
    # 3. 점유율: revenue ÷ marketshare가 모두 같고 노드 매출과도 같으면 매출 점유율로 확인, 하나라도 어긋나면 단위 미확인
    rows = [{"revenue": 400.0, "marketshare": 0.4}, {"revenue": 100.0, "marketshare": 0.1}]
    eq("점유율 단위 확인", (gm.share_basis(rows, 1000.0)[0], gm.share_basis(rows)[0], gm.share_basis(rows, 2000.0)[0],
                       gm.share_basis([{"revenue": 400.0, "marketshare": 0.4}, {"revenue": 100.0, "marketshare": 0.2}])[0],
                       gm.share_basis(rows[:1])[0]), (True, True, False, False, False))
    # 5. 안전 기준: 몸 반응 판정 리뷰 + 안전 주제 부정 태그 전부(제품 위험, 기타 포함). 긍정과 다른 주제는 아님
    tags = [{"review_id": "s1", "topic": "safety", "sentiment": "negative"}, {"review_id": "s2", "topic": "safety", "sentiment": "negative"},
            {"review_id": "s3", "topic": "safety", "sentiment": "positive"}, {"review_id": "s4", "topic": "quality", "sentiment": "negative"}]
    eq("안전 기준 불만 범위", sorted(gm.safety_complaints(tags, "safety", {"s1", "s9"})), ["s1", "s2", "s9"])
    # 3, 4. 가이드 검사: 가정 값을 머리 숫자로 쓰면 FAIL, 성별 표가 비었는데 성별 검색어 수를 쓰면 FAIL
    M = {"values": {"head.market_year": {"text": "1", "assumption": True}, "head.market_month": {"text": "2"}},
         "tables": {"m.terms_female": [], "m.terms_male": []}}
    nl = chr(10)
    bad = nl.join(["## 머리 숫자", "- [head.market_year] 연", "", "## 01 시장", "- 여성 0개 [m:m.terms_female_n]", ""])
    good = nl.join(["## 머리 숫자", "- [head.market_month] 월", "", "## 01 시장", "- 연 1 [m:head.market_year]은 가정", ""])
    eq("가정 값 머리 숫자와 성별 문장 검사", (len(gc.head_gender_problems(bad, M)), gc.head_gender_problems(good, M)), (2, []))
    M["tables"]["m.terms_female"] = [{"term": "x"}]
    eq("성별 표가 있으면 성별 문장 허용", gc.head_gender_problems("- 여성 1개 [m:m.terms_female_n]", M), [])
    # 4. 성별 검색어가 하나도 없으면 HTML에 성별 표 제목을 두지 않음
    g = object.__new__(rg.R)
    g.T = lambda s, **k: s.format(**k) if k else s
    g.M = {"tables": {"m.terms_female": [], "m.terms_male": [], "m.terms_common": [{"term": "speaker", "volume_text": "10", "yoy_text": "-"}]}}
    h = g.insert_for("검색 수요")
    eq("성별 없는 품목의 검색 수요 표", ("여성 검색어" in h, "남성 검색어" in h, "speaker" in h), (False, False, True))
    g.M["tables"]["m.terms_female"] = [{"term": "speaker for women", "volume_text": "5", "yoy_text": "-"}]
    eq("성별 검색어가 있으면 성별 표", "여성 검색어" in g.insert_for("검색 수요"), True)


def test_i18n(tmp):
    """render_html Lang(문구 파일과 이름표, 빠진 문구 기록, notes 틀)와 translate_prep check(줄 수, 숫자, 인용, 한글)"""
    sys.path.insert(0, str(SCRIPTS))
    import render_html as rh
    L = object.__new__(rh.Lang)
    L.code, L.missing = "en", set()
    L.cat = {"strings": {"리뷰 {n}개": "{n} reviews"}, "notes_patterns": [{"re": "ASIN당 표본 리뷰 (\\d+)~(\\d+)개", "en": "{0} to {1} per ASIN"}]}
    L.names = {"topics": {"scent": "Scent"}, "labels": {"scent.negative.x": {"en": "Smells off"}}, "symptoms": {"두통": "Headache"},
               "periods": {"2025년": "2025"}, "raw_replace": {"달러": " USD"}}
    eq("영어 문구와 이름", (L("리뷰 {n}개", n=3), L("없는 문구"), sorted(L.missing), L.topic("scent", "향"), L.label("scent", "negative", "x", "다름"),
                        L.sym("두통"), L.period("2025년"), L.raw("20.99달러"), L.note("ASIN당 표본 리뷰 114~399개")),
       ("3 reviews", "없는 문구", ["없는 문구"], "Scent", "Smells off", "Headache", "2025", "20.99 USD", "114 to 399 per ASIN"))
    r = Path(tmp) / "tr-2026-10-07"
    r.mkdir()
    (r / "02_reviews.csv").write_text("review_id,asin,star,date,title,body,verified,vine\nR1TRANSLATE1,B0TR000001,2,2026-09-01,T,It fades in an hour,true,false\n",
                                      encoding="utf-8")
    (r / "06_report_for_translation.md").write_text('## 1. 개요\n\n**데이터 읽기** 부정 10.0%, 리뷰 1,212개.\n> "한 시간이면 날아가요" (BrandA, 2★, R1TRANSLATE1)\n',
                                                    encoding="utf-8")
    good = '## 1. Overview\n\n**Data Reading** Negative 10.0%, 1,212 reviews.\n> "It fades in an hour" (BrandA, 2★, R1TRANSLATE1)\n'
    (r / "06_report_en.md").write_text(good, encoding="utf-8")
    run("translate_prep.py", "check", r, "--lang", "en")
    bad = good.replace("10.0%", "10%").replace("It fades in an hour", "It fades fast").replace("Overview", "개요")
    (r / "06_report_en.md").write_text(bad, encoding="utf-8")
    out = run("translate_prep.py", "check", r, "--lang", "en", expect=1)
    for want in ("숫자 표기가 다름", "원문에 없음", "한글이 남음"):
        if want not in out:
            FAILS.append(f"번역 검사가 '{want}'를 잡지 못함:\n{out}")
    # 숫자 뒤 문장 쉼표, 기간 이름(이름표), 순위(N위 → 서수)는 다르게 보지 않는다. 순위가 빠지면 잡는다.
    (r / "i18n_names_en.yaml").write_text("periods:\n  2026년 1~6월: 2026 Jan-Jun\n", encoding="utf-8")
    (r / "06_report_for_translation.md").write_text("2026년 1~6월 리뷰 171개, 순위 2위, 끝.\n", encoding="utf-8")
    (r / "06_report_en.md").write_text("2026 Jan-Jun has 171, ranking second, end.\n", encoding="utf-8")
    run("translate_prep.py", "check", r, "--lang", "en")
    (r / "06_report_en.md").write_text("2026 Jan-Jun has 171, ranking high, end.\n", encoding="utf-8")
    out = run("translate_prep.py", "check", r, "--lang", "en", expect=1)
    if "순위 2위가 번역에 없음" not in out:
        FAILS.append(f"번역 검사가 빠진 순위를 잡지 못함:\n{out}")


def test_robustness_specs(tmp):
    """robustness.py(다시 뽑기 씨앗 고정, 상품 하나씩 빼기 뒤집힘 표시, 95% 범위)와 specs.py(값이 인용 안에 있는지, 목록 밖 값 거르기)"""
    sys.path.insert(0, str(SCRIPTS))
    import robustness as rb
    D = object.__new__(rb.Data)
    # ASIN 셋, 리뷰 넷씩. 주제 a가 대부분의 부정, 상품 C만 b가 약점
    D.topics, D.head, D.strength_min = ["a", "b"], "a", 1
    D.name = {"a": "가", "b": "나"}
    D.di = {"low": {"name": "약함"}, "high": {"name": "너무 셈"}}
    D.by_asin = {"A": ["A1", "A2", "A3", "A4"], "B": ["B1", "B2", "B3", "B4"], "C": ["C1", "C2", "C3", "C4"]}
    D.weight = {r: 1.0 for v in D.by_asin.values() for r in v}
    D.neg = {"A1": {"a"}, "A2": {"a"}, "B1": {"a"}, "B2": {"a"}, "C1": {"b"}, "C2": {"a"}, "C3": {"b"}}
    D.neg = __import__("collections").defaultdict(set, D.neg)
    D.ment = __import__("collections").defaultdict(__import__("collections").Counter,
                                                   {r: __import__("collections").Counter({t: 1 for t in ts}) for r, ts in D.neg.items()})
    D.low, D.high = {"A1", "A2", "B1", "C2"}, {"B2"}
    rows, weak = rb.leave_one_out(D)
    eq("상품별 최대 약점", weak, {"A": "a", "B": "a", "C": "b"})
    eq("빼지 않음 줄", (rows[0]["head_neg"], rows[0]["weakest"], rows[0]["low"], rows[0]["high"], rows[0]["flips"]), (41.7, 2, 4, 1, []))
    eq("A를 빼면 최대 약점 과반 아님", rows[1]["flips"], ["최대 약점 상품이 과반이 아니게 됨"])
    D.head = "b"        # 처음부터 과반이 아닌 결론은 상품을 빼도 '바뀜'으로 세지 않는다
    rows_b, _ = rb.leave_one_out(D)
    eq("처음부터 성립하지 않던 결론은 뒤집힘 아님", [f for r in rows_b for f in r["flips"] if "최대 약점" in f], [])
    D.head = "a"
    b1, b2 = rb.bootstrap(D, 200, 7), rb.bootstrap(D, 200, 7)
    eq("다시 뽑기는 씨앗이 같으면 같음", b1, b2)
    eq("95% 범위가 분포를 덮음", sum(v for k, v in b1["weakest_dist"].items() if b1["weakest_range"][0] <= int(k) <= b1["weakest_range"][1]) >= 95, True)
    import specs
    eq("값이 인용 안에", [specs.values_in_quote(["Bergamot", "Pear"], "Top notes: Bergamot, Pear")[0],
                     specs.values_in_quote(["Bergamot", "Rose"], "Top notes: Bergamot, Pear")[0],
                     specs.values_in_quote("Eau de Parfum", "Eternity Eau de Parfum 3.4 oz")[0]], [True, False, True])
    r = Path(tmp) / "perfume-specs-2026-10-07"
    r.mkdir()
    (r / "23_specs.yaml").write_text(
        "specs:\n  products:\n"
        "    - asin: B0SPEC0001\n      match: 일치 확인\n      values:\n"
        "        - {item: concentration, value: EDP, url: 'https://www.amazon.com/x', source_type: official, quote: 'EDP'}\n"
        "        - {item: color, value: red, url: 'https://example.org', source_type: official, quote: 'red'}\n"
        "        - {item: concentration, value: EDT, url: 'no-url', source_type: official, quote: 'EDT'}\n"
        "    - asin: B0SPEC0002\n      match: 비슷함\n", encoding="utf-8")
    out = run("specs.py", "check", r, expect=1)
    for want in ("amazon 주소라 쓰지 않음", "항목이 목록 밖", "url 없음"):
        if want not in out:
            FAILS.append(f"사양 확인이 '{want}'를 거르지 못함:\n{out}")
    chk = json.loads((r / "23_specs_check.json").read_text(encoding="utf-8"))
    eq("match 값이 목록 밖이면 FAIL", (chk["status"], chk["verified"]), ("FAIL", 0))


def test_off_category(tmp):
    """off_category 리뷰가 하나 있어도 weight.py와 render_html.py build, check가 돌고, 그 리뷰는 집계와 화면에서 빠진다"""
    sys.path.insert(0, str(SCRIPTS))
    import pipeline_io as pio
    rv, tg, info = pio.split_tags([{"review_id": "A"}, {"review_id": "B"}],
                                  [{"review_id": "A", "topic": "off_category"}, {"review_id": "B", "topic": "scent"}, {"review_id": "B", "topic": "nope"}],
                                  {"scent": {}})
    eq("off_category와 스키마 밖 주제 거르기", ([r["review_id"] for r in rv], [t["topic"] for t in tg], info),
       (["B"], ["scent"], {"off_category_reviews": ["A"], "unknown_topic_tags": 1}))
    real = HERE.parent / "runs" / "perfume-db-2026-10-07"
    if not (real / "06_report.md").exists() or not (real / "02_reviews.csv").exists():
        print("  (off_category 시험: 실제 회차나 그 리뷰 원문(공개 저장소에서는 뺌)이 없어 건너뜀)")
        return
    r = Path(tmp) / "perfume-off-2026-10-07"
    r.mkdir()
    for n in ("01_asins.csv", "02_reviews.csv", "02_star_distribution.csv", "03_schema_approved.yaml", "04_tags.jsonl", "04_gold_eval.json",
              "07a_issues_approved.yaml", "07b_issue_labels.jsonl", "07b_issue_counts.json", "07c_safety_summary.json", "07c_safety_verdicts.yaml",
              "01_prices.json", "06_report.md", "05_robustness.json"):
        if (real / n).exists():
            shutil.copy(real / n, r / n)
    labeled = {json.loads(l)["review_id"] for l in (r / "07b_issue_labels.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()}
    tags = [json.loads(l) for l in (r / "04_tags.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()]
    off = next(t["review_id"] for t in tags if t["review_id"] not in labeled and t["topic"] != "safety")
    tags = [t for t in tags if t["review_id"] != off] + [{"review_id": off, "topic": "off_category", "sentiment": "neutral", "quote": "x"}]
    (r / "04_tags.jsonl").write_text("".join(json.dumps(t, ensure_ascii=False) + chr(10) for t in tags), encoding="utf-8")
    run("weight.py", r)
    # 2026-10-16 미리 쓰기: 라벨 전 상태(07a, 07b, 07c, 견고성 파일 없음)의 같은 이름 회차로 --early를 돌려 라벨 뒤 값과 대조
    pre = Path(tmp) / "pre" / r.name
    shutil.copytree(r, pre, ignore=lambda d, names: [n for n in names if n.startswith(("07a_", "07b_", "07c_", "05_"))])
    run("weight.py", pre, "--early")
    for n in ("05_metrics_early.json", "05_tables_early.md", "05_quote_pool_early.json"):
        shutil.copy(pre / n, r / n)
    if str(SCRIPTS) not in sys.path:
        sys.path.insert(0, str(SCRIPTS))
    import report_parts
    early_tables = {"1-7": chr(10).join("{{표: " + x + "}}" for x in ("요약", "분포", "주제별 언급", "주제 평가", "영향 분석", "시간 추이", "공출현", "신뢰 신호")),
                    "9": "{{표: 브랜드별 비교}}" + chr(10) + "{{표: ASIN별 비교}}"}
    eq("라벨 전 --early와 라벨 뒤 값이 1~7장과 9장 범위에서 같음(숫자와 표)",
       (report_parts.compare_metrics(r), report_parts.compare_tables(r, early_tables)), ((True, []), []))
    m = json.loads((r / "05_metrics.json").read_text(encoding="utf-8"))
    eq("weight.py가 off_category 리뷰를 뺌", (m["summary"]["reviews"], m["off_category"]["reviews"]), (1211, 1))
    out = run("render_html.py", "build", r)
    page = (r / "06_report.html").read_text(encoding="utf-8")
    eq("HTML이 off_category 리뷰를 빼고 안내에 적음", ("리뷰 1211개" in out, off in page, "off_category" in page), (True, False, True))


def test_fake_category(tmp):
    """카테고리 전용 설정(제목, 겹침 라벨, 짝 항목, 사양 연결, 해부도, 회차 주의 사항)이 없는 가짜 카테고리로도 두 HTML이 만들어진다"""
    real = HERE.parent / "runs" / "perfume-db-2026-10-07"
    if not (real / "17_guide.md").exists() or not (real / "02_reviews.csv").exists():
        print("  (가짜 카테고리 시험: 실제 회차나 그 리뷰 원문(공개 저장소에서는 뺌)이 없어 건너뜀)")
        return
    import yaml
    cfg = HERE.parent / "config" / "categories" / "fakecat.yaml"
    base = yaml.safe_load((HERE.parent / "config" / "categories" / "perfume.yaml").read_text(encoding="utf-8"))
    base["category"], base["name_ko"] = "fakecat", "가짜 카테고리"
    for k in ("report", "issues", "specs"):
        base.pop(k, None)
    for k in ("anatomy", "caveats_extra", "caveat_subcategory"):
        base["guide"].pop(k, None)
    for f in base["guide"]["focus"]:
        f.pop("pair_items", None)
    cfg.write_text(yaml.safe_dump(base, allow_unicode=True, sort_keys=False), encoding="utf-8")
    try:
        r = Path(tmp) / "fakecat-2026-10-07"
        skip = {"raw", "gold", "research_cache", "14_detail_input", "14_rejudge_input", "07a_issue_samples", "07b_label_input"}
        shutil.copytree(real, r, ignore=lambda d, names: [n for n in names if n in skip or (Path(d).name == "market" and n == "raw")])
        run("guide_metrics.py", r)
        M = json.loads((r / "16_guide_metrics.json").read_text(encoding="utf-8"))
        W = json.loads((r / "16_guide_writer_input.json").read_text(encoding="utf-8"))
        eq("작성자용 입력: 값, 표, 인용은 같고 ev의 리뷰 id 목록만 빠짐",
           (W["values"] == M["values"], W["tables"] == M["tables"], W["quotes"] == M["quotes"], sorted(W["ev"]) == sorted(M["ev"]),
            any("i" in e or "q" in e for e in W["ev"].values())), (True, True, True, True, False))
        sk = [k for k in M["values"] if k.startswith("std.") and k.count(".") == 2 and k.endswith((".neg_pct", ".best"))]
        eq("기준표 불만 비율과 최저 상품에 정의 문구(2026-10-21)", (len(sk) > 0, all("분모" in (M["values"][k].get("note") or "") for k in sk)), (True, True))
        eq("설정 없는 표는 만들지 않음", (any(k.startswith("std.spec.") for k in M["tables"]), "meta.anatomy" in M["tables"],
                                     "f.scent_accuracy.note_x_direction" in M["tables"]), (False, False, False))
        run("render_guide_html.py", "build", r)
        g = (r / "07_guide.html").read_text(encoding="utf-8")
        eq("가이드 HTML에 해부도 없음", 'class="anat"' in g, False)
        sys.path.insert(0, str(SCRIPTS))
        import market_build
        try:
            market_build.market_conf(Path(tmp) / "nocat-2026-10-07")
            stopped = False
        except SystemExit:
            stopped = True
        eq("market 절이 없는 카테고리는 시장 수집을 멈춤", stopped, True)
        run("render_html.py", "build", r)
        h = (r / "06_report.html").read_text(encoding="utf-8")
        eq("리포트 제목은 카테고리 이름에서", ("아마존 리뷰 분석: 가짜 카테고리" in h, "향수(EDP/EDT)" in h), (True, False))
        m5 = json.loads((r / "05_metrics.json").read_text(encoding="utf-8"))
        t0 = m5["brand_deep"][0]["top_topics"][0]
        eq("브랜드 표에 혼합과 중립 칸, 네 감성 합 = 언급", ("<th>혼합</th>" in h and "<th>중립</th>" in h,
                                                 t0["positive"] + t0["negative"] + t0["mixed"] + t0["neutral"] == t0["mentions"]), (True, True))
    finally:
        cfg.unlink(missing_ok=True)


def test_common_topic():
    """공통 주제를 다시 정의해 id가 바뀌어도(safety → skin_reaction) common_id로 같은 주제를 찾는다"""
    sys.path.insert(0, str(SCRIPTS))
    from pipeline_io import common_topic
    eq("공통 주제 id 찾기", (common_topic({"safety": {}}, "safety"), common_topic({"skin_reaction": {"common_id": "safety"}}, "safety"),
                          common_topic({"scent": {}}, "safety")), ("safety", "skin_reaction", "safety"))


def test_sentiment_split():
    """감성 일치를 방향(어느 쪽도 mixed가 아닌 짝)과 mixed(한쪽이라도 mixed인 짝)로 나눠 잰다. 판정은 방향 일치로"""
    sys.path.insert(0, str(SCRIPTS))
    from eval_gold import score_one
    gold = [{"review_id": f"r{i}", "topic": "t", "sentiment": s} for i, s in enumerate(
        ["positive", "negative", "neutral", "negative", "mixed", "mixed", "negative", "positive"])]
    pred = [{"review_id": f"r{i}", "topic": "t", "sentiment": s} for i, s in enumerate(
        ["positive", "negative", "neutral", "positive", "mixed", "negative", "mixed", "positive"])]
    r = score_one(gold, pred, {f"r{i}" for i in range(8)})
    # 방향 짝: r0~r3, r7(5개) 중 같음 4개(r3 부정→긍정만 다름). mixed 짝: r4~r6(3개) 중 둘 다 mixed 1개(r4)
    eq("방향과 mixed 일치", (r["direction_pairs"], r["direction_same"], r["direction_agreement"],
                           r["mixed_pairs"], r["mixed_same"], r["mixed_agreement"], r["sentiment_agreement"]),
       (5, 4, 0.8, 3, 1, 0.333, 0.625))
    eq("mixed 짝이 없으면 None", score_one(gold[:2], pred[:2], {"r0", "r1"})["mixed_agreement"], None)


def test_helpful_provisional():
    """도움돼요 순위: 표를 받은 리뷰가 기준보다 적으면 (잠정)과 해석하지 않는다는 문장, 기준 이상이면 그대로"""
    sys.path.insert(0, str(SCRIPTS))
    import sections
    rv = [{"review_id": f"R{i}", "asin": "A", "star": "1" if i % 2 else "5", "title": "t", "verified": "true", "vine": "false",
           "helpful_votes": "3" if i < 5 else "0"} for i in range(10)]
    tg = [{"review_id": f"R{i}", "topic": "scent", "sentiment": "negative"} for i in range(1, 10, 2)]
    few = sections.trust_signals(rv, tg, ("overall",), min_voted=30)
    many = sections.trust_signals(rv, tg, ("overall",), min_voted=5)
    off = sections.trust_signals(rv, tg, ("overall",))
    eq("잠정 판정", (few["helpful_provisional"], many["helpful_provisional"], off["helpful_provisional"]), (True, False, False))
    t_few = chr(10).join(sections.render_trust(few, {"scent": {"name_ko": "향"}}))
    t_many = chr(10).join(sections.render_trust(many, {"scent": {"name_ko": "향"}}))
    eq("잠정 표 제목과 해석하지 않는다는 문장", ("(잠정)" in t_few, "해석하지 않습니다" in t_few, "(잠정)" in t_many, "해석하지 않습니다" in t_many),
       (True, True, False, False))


def test_stage_plan_packet(tmp):
    """stage_plan(해시가 같으면 건너뜀, 바뀐 단계와 뒤 단계만, 출력 겹침과 상한 검사, 작업자 배정), stage_packet(필요한 기준 필드만 원문 그대로),
    detail.py audit(빈 표본은 PASS가 아니라 EMPTY)"""
    sys.path.insert(0, str(SCRIPTS))
    import stage_plan as sp
    import yaml
    r = Path(tmp) / "stg-2026-10-07"
    r.mkdir()
    for n in ("a.txt", "b_in.txt"):
        (r / n).write_text(n, encoding="utf-8")
    lim = {k: 2 for k in sp.LIMIT_KEYS}
    lim.update({"worker_max_batches": 4, "worker_max_reviews": 200, "bulk_concurrency": 4})
    conf = {"limits": lim, "stages": [
        {"id": "s1", "kind": "script", "inputs": ["a.txt"], "outputs": ["a_out.txt"], "after": ["s2"]},
        {"id": "s2", "kind": "agents", "inputs": ["a_out.txt", "b_in.txt"], "outputs": ["b_out.txt"], "after": ["s3"]},
        {"id": "s3", "kind": "script", "inputs": ["b_out.txt"], "outputs": ["c_out.txt"], "after": []}]}
    for n in ("a_out.txt", "b_out.txt", "c_out.txt"):
        (r / n).write_text(n, encoding="utf-8")
    (r / "state.json").write_text(json.dumps({"run": r.name, "steps": {x: {"status": "done"} for x in ("s1", "s2", "s3")}}), encoding="utf-8")
    eq("기준 해시 없으면 다시", sp.plan(r, conf)["redo"], ["s1", "s2", "s3"])
    sp.baseline(r, conf)
    eq("해시가 같으면 건너뜀", sp.plan(r, conf)["redo"], [])
    (r / "b_in.txt").write_text("changed", encoding="utf-8")
    eq("바뀐 단계와 뒤 단계만", sp.plan(r, conf)["redo"], ["s2", "s3"])
    bad = json.loads(json.dumps(conf))
    bad["stages"][2]["outputs"] = ["b_out.txt"]
    bad["limits"]["retry_per_stage"] = 0
    errs = sp.check(bad)
    eq("출력 겹침과 상한 오류를 잡음", (any("출력 겹침" in e for e in errs), any("retry_per_stage" in e for e in errs)), (True, True))
    eq("실제 단계 정의는 통과", sp.check(sp.load_conf()), [])
    a = sp.assign(sp.load_conf(), 28, 1242)
    eq("태깅 28묶음 배정(대량 작업 동시 8, 2026-10-12)", (a["workers"], a["concurrency"], max(len(g) for g in a["groups"])), (7, 7, 4))
    a = sp.assign(sp.load_conf(), 6, 276)
    eq("리뷰 상한으로 작업자당 묶음이 줄어듦", (a["per_worker"] * 276 / 6 <= 200, a["workers"]), (True, 2))
    real = HERE.parent / "runs" / "perfume-db-2026-10-07"
    if (real / "13_detail_schema_approved.yaml").exists():
        import stage_packet as pk
        crit = pk.criteria(real, "detail", ["purchase_context"])
        src = next(i for i in yaml.safe_load((real / "13_detail_schema_approved.yaml").read_text(encoding="utf-8"))["items"] if i["id"] == "purchase_context")
        eq("기준 필드 원문 그대로", crit, [{k: src[k] for k in pk.DETAIL_FIELDS if k in src}])
        eq("다른 항목은 없음", "longevity_hours" in pk.dump(crit), False)
        eq("예시는 원문 그대로 들어감", (crit[0].get("examples") == src.get("examples"), "examples" in src), (True, True))
        other = next(i for i in yaml.safe_load((real / "13_detail_schema_approved.yaml").read_text(encoding="utf-8"))["items"] if i["id"] == "comparison_reference")
        ex_other = [e.get("quote") for e in other.get("examples") or [] if isinstance(e, dict) and e.get("quote")]
        eq("다른 항목의 예시는 안 들어감", any(q in pk.dump(crit) for q in ex_other), False)
        nb = pk.dump(pk.neighbors(real, ["purchase_context"]))
        eq("다른 항목은 정의만(원문 그대로), 판정 항목은 빠짐", (other["definition"] in nb, "fill_rule" in nb, "id: purchase_context" in nb), (True, False, False))
    d = Path(tmp) / "emp-2026-10-07"
    d.mkdir()
    (d / "14b_detail_audit_sample.jsonl").write_text("", encoding="utf-8")
    (d / "14b_detail_audit.yaml").write_text(chr(10).join(["audit:", "  stage: details", "  checked: 0", "  findings: []"]) + chr(10), encoding="utf-8")
    run("detail.py", "audit", d, expect=1)
    eq("빈 표본은 EMPTY", json.loads((d / "14b_detail_audit_summary.json").read_text(encoding="utf-8"))["status"], "EMPTY")
    run("timing_report.py", "mark", d, "end", "22_robustness", "--kind", "script", "--calls", "0", "--retries", "1")
    st = json.loads((d / "state.json").read_text(encoding="utf-8"))["steps"]["22_robustness"]
    eq("mark end가 입력 해시와 호출, 재시도를 적음", (len(st.get("input_hash", "")), st.get("calls"), st.get("retries")), (16, 0, 1))


def _detail_run(tmp, name):
    """설계 정보 추출 시험용 작은 회차(리뷰 6개, 항목 하나, 묶음 2개)"""
    import yaml
    r = Path(tmp) / name
    r.mkdir()
    lines = ["review_id,asin,star,date,title,body,verified,vine"]
    for i in range(6):
        lines.append(f"R{i:02d}G9REVIEW,B0G9TEST01,{1 + i % 5},2026-09-01,T{i},I bought it for my mom {i},true,false")
    (r / "02_reviews.csv").write_text("\n".join(lines) + "\n", encoding="utf-8")
    (r / "02_star_distribution.csv").write_text("asin,s5,s4,s3,s2,s1,total_ratings\nB0G9TEST01,60,20,10,5,5,100\n", encoding="utf-8")
    item = {"id": "purchase_context", "name_ko": "구매 맥락", "format": "choice", "definition": "d", "fill_rule": "f",
            "allowed_values": [{"value": "gift"}, {"value": "repurchase"}], "quote_required": True}
    (r / "13_detail_schema_approved.yaml").write_text(yaml.safe_dump({"version": "approved", "items": [item]}, allow_unicode=True),
                                                       encoding="utf-8")
    run("detail.py", "plan", r, "--size", "3")
    for bid, ids in (("B0G9TEST01_01", range(0, 3)), ("B0G9TEST01_02", range(3, 6))):
        (r / f"14_details_{bid}.jsonl").write_text("".join(json.dumps(
            {"review_id": f"R{i:02d}G9REVIEW", "item": "purchase_context", "value": "gift", "quote": f"for my mom {i}"}) + "\n"
            for i in ids), encoding="utf-8")
    return r


def test_g9_review_fixes(tmp):
    """GPT 검토(2026-10-08)가 찾은 구멍마다 실패를 재현하는 시험. F01~F09, F12와 태그 작업 파일(F11 일부)."""
    sys.path.insert(0, str(SCRIPTS))
    import stage_plan as sp
    lim = {k: 2 for k in sp.LIMIT_KEYS}
    lim.update({"worker_max_batches": 4, "worker_max_reviews": 200, "bulk_concurrency": 4})
    conf = {"limits": lim}
    # F04: 평균이 아니라 실제 묶음 크기로 배정. 180,180,20,20이면 어느 작업자도 200개를 넘지 않음
    a = sp.assign(conf, 4, 400, [180, 180, 20, 20])
    eq("F04 실제 크기로 배정(작업자 리뷰 200 이하)", (max(a["worker_reviews"]), a["groups"]), (200, [[0], [1, 2], [3]]))
    try:
        sp.assign(conf, 1, 250, [250])
        stopped = False
    except SystemExit:
        stopped = True
    eq("F04 상한보다 큰 묶음 하나는 멈춤", stopped, True)

    # F06: 깨진 JSON 줄이 있으면 묶음 실패
    r = _detail_run(tmp, "g9-f06-2026-10-07")
    p = r / "14_details_B0G9TEST01_01.jsonl"
    p.write_text(p.read_text(encoding="utf-8") + '{"review_id":\n', encoding="utf-8")
    run("detail.py", "extract-check", r, expect=1)
    eq("F06 깨진 줄은 묶음 실패", json.loads((r / "14_detail_check.json").read_text(encoding="utf-8"))["failed_batches"], ["B0G9TEST01_01"])
    # F07: 첫 추출도 인용이 원문에 없으면 묶음 실패(값만 버리고 PASS하지 않음)
    r = _detail_run(tmp, "g9-f07-2026-10-07")
    p = r / "14_details_B0G9TEST01_02.jsonl"
    p.write_text(p.read_text(encoding="utf-8").replace("for my mom 4", "for my aunt 4"), encoding="utf-8")
    run("detail.py", "extract-check", r, expect=1)
    eq("F07 원문에 없는 인용은 묶음 실패", (json.loads((r / "14_detail_check.json").read_text(encoding="utf-8"))["failed_batches"],
                                     (r / "14_details.jsonl").exists()), (["B0G9TEST01_02"], False))
    # F05: --only에 모르는 묶음 id가 있으면 멈춤(오타를 조용히 버리지 않음)
    r = _detail_run(tmp, "g9-f05-2026-10-07")
    run("stage_packet.py", "detail", r, "--items", "purchase_context", "--only", "B0G9TEST01_01,B0G9TEST01_99", expect=2)
    # F02: 작업 파일 해시가 참조한 입력 파일 내용까지 덮음
    run("stage_packet.py", "detail", r, "--items", "purchase_context")
    h1 = json.loads((r / "packets" / "detail_plan.json").read_text(encoding="utf-8"))["workers"][0]["packet_hash"]
    inp = r / "14_detail_input" / "B0G9TEST01_01.jsonl"
    inp.write_text(inp.read_text(encoding="utf-8").replace("my mom 0", "my mum 0"), encoding="utf-8")
    run("stage_packet.py", "detail", r, "--items", "purchase_context")
    h2 = json.loads((r / "packets" / "detail_plan.json").read_text(encoding="utf-8"))["workers"][0]["packet_hash"]
    eq("F02 입력 내용이 바뀌면 작업 파일 해시가 바뀜", h1 != h2, True)

    # F09: 감사가 표본을 다 보지 않았으면 PASS가 아님
    d = Path(tmp) / "g9-f09-2026-10-07"
    d.mkdir()
    smp = [{"review_id": "R1", "asin": "A", "item": "purchase_context", "value": "gift", "quote": "q"},
           {"review_id": "R2", "asin": "A", "item": "purchase_context", "value": "gift", "quote": "q"}]
    (d / "14b_detail_audit_sample.jsonl").write_text("".join(json.dumps(x) + "\n" for x in smp), encoding="utf-8")
    (d / "14b_detail_audit.yaml").write_text("audit:\n  stage: details\n  checked: 0\n  findings: []\n", encoding="utf-8")
    run("detail.py", "audit", d, expect=1)
    eq("F09 checked가 표본 수와 다르면 INCOMPLETE", json.loads((d / "14b_detail_audit_summary.json").read_text(encoding="utf-8"))["status"],
       "INCOMPLETE")
    # F08: 다시 판정 감사는 바뀐 종류(change)별로 센다. 없어짐 FAIL은 '지우면 안 됐음'
    smp = [dict(smp[0], change="removed"), dict(smp[1], change="added")]
    (d / "14b_rejudge_audit_sample.jsonl").write_text("".join(json.dumps(x) + "\n" for x in smp), encoding="utf-8")
    (d / "14b_rejudge_audit.yaml").write_text("audit:\n  stage: details\n  checked: 2\n  findings:\n"
                                              "    - {review_id: R1, item: purchase_context, value: gift, change: removed, status: FAIL, finding: f}\n",
                                              encoding="utf-8")
    run("detail.py", "audit", d, "--sample-file", "14b_rejudge_audit_sample.jsonl", "--audit-file", "14b_rejudge_audit.yaml",
        "--max-fail", "0.6")
    s8 = json.loads((d / "14b_rejudge_audit_summary.json").read_text(encoding="utf-8"))
    eq("F08 없어짐 FAIL을 change별로 셈", (s8["status"], s8["fail"], s8.get("by_change")), ("PASS", 1, {"removed": 1}))

    # F12: 태그가 없는 리뷰와 overall이 없는 리뷰는 묶음 실패
    import yaml
    t = fresh(tmp, "g9_f12")
    sch = yaml.safe_load((t / "03_schema_approved.yaml").read_text(encoding="utf-8"))
    sch.pop("overall_required", None)
    (t / "03_schema_approved.yaml").write_text(yaml.safe_dump(sch, allow_unicode=True, sort_keys=False), encoding="utf-8")
    run("tag_batches.py", "plan", t)
    out = run("audit_quotes.py", "tags", t, "--model", "sonnet", "--batches", "B0TESTAAA1_01", expect=1)
    eq("F12 overall 없는 리뷰를 잡음", "overall이 없는 리뷰" in out, True)
    t = fresh(tmp, "g9_f12b")
    run("tag_batches.py", "plan", t)
    p = t / "04_tags_sonnet_B0TESTAAA1_01.jsonl"
    p.write_text("".join(l + "\n" for l in p.read_text(encoding="utf-8").splitlines() if "B0TESTAAA1-03" not in l), encoding="utf-8")
    out = run("audit_quotes.py", "tags", t, "--model", "sonnet", "--batches", "B0TESTAAA1_01", expect=1)
    eq("F12 태그가 하나도 없는 리뷰는 묶음 실패", "태그가 하나도 없는 리뷰 1개" in out, True)
    # 태그 작업 파일: 시험 태깅 묶음(gold 포함)은 빼고 남은 sonnet 묶음만
    t = fresh(tmp, "g9_tags_packet")
    run("tag_batches.py", "plan", t)
    run("stage_packet.py", "tags", t)
    tp = json.loads((t / "packets" / "tags_plan.json").read_text(encoding="utf-8"))
    eq("태그 작업 파일에 시험 묶음 없음", sorted(b for w in tp["workers"] for b in w["batches"]), ["B0TESTBBB2_01"])

    # F01, F03: 지시문과 코드 해시, 묶음 출력 하나하나
    root = Path(tmp) / "g9root"
    (root / "agents").mkdir(parents=True)
    (root / "agents" / "worker.md").write_text("v1", encoding="utf-8")
    old_root = sp.ROOT
    sp.ROOT = root
    try:
        r = Path(tmp) / "g9-f01-2026-10-07"
        r.mkdir()
        (r / "in.txt").write_text("x", encoding="utf-8")
        (r / "plan.json").write_text(json.dumps({"batches": [{"batch_id": "b1", "output": "out_b1.txt"},
                                                             {"batch_id": "b2", "output": "out_b2.txt"}]}), encoding="utf-8")
        for n in ("out_b1.txt", "out_b2.txt"):
            (r / n).write_text(n, encoding="utf-8")
        c2 = {"limits": lim, "stages": [{"id": "w", "kind": "agents", "inputs": ["in.txt", "plan.json"], "outputs": ["out_b*.txt"],
                                         "code": ["agents/worker.md"], "expect": {"batches": "plan.json"}, "after": []}]}
        (r / "state.json").write_text(json.dumps({"run": r.name, "steps": {"w": {"status": "done"}}}), encoding="utf-8")
        sp.baseline(r, c2)
        eq("F01 지시문 기준이 없으면 다시(baseline은 코드 해시를 따로 적어야)", sp.plan(r, c2)["redo"], ["w"])
        sp.baseline(r, c2, with_code=True)
        eq("F01 기준이 같으면 건너뜀", sp.plan(r, c2)["redo"], [])
        (root / "agents" / "worker.md").write_text("v2", encoding="utf-8")
        p1 = sp.plan(r, c2)
        eq("F01 지시문이 바뀌면 다시", (p1["redo"], "지시문" in p1["reasons"].get("w", "")), (["w"], True))
        (root / "agents" / "worker.md").write_text("v1", encoding="utf-8")
        (r / "out_b2.txt").unlink()
        p2 = sp.plan(r, c2)
        eq("F03 묶음 출력 하나가 없으면 다시", (p2["redo"], "out_b2.txt" in p2["reasons"].get("w", "")), (["w"], True))
        eq("F01 단계 정의 검사가 없는 지시문 파일을 잡음",
           any("worker_x.md" in e for e in sp.check(dict(c2, stages=[dict(c2["stages"][0], code=["agents/worker_x.md"])]))), True)
    finally:
        sp.ROOT = old_root
    # 단계가 도는 동안 입력이 바뀌면 완료로 적지 않음
    d = Path(tmp) / "g9-mark-2026-10-07"
    d.mkdir()
    (d / "04_tags.jsonl").write_text("a\n", encoding="utf-8")
    run("timing_report.py", "mark", d, "start", "22_robustness", "--kind", "script")
    (d / "04_tags.jsonl").write_text("b\n", encoding="utf-8")
    run("timing_report.py", "mark", d, "end", "22_robustness", "--kind", "script")
    st = json.loads((d / "state.json").read_text(encoding="utf-8"))["steps"]["22_robustness"]
    eq("입력이 도중에 바뀌면 needs_human", (st["status"], "input_hash" in st), ("needs_human", False))
    # 2026-10-17 E4: 고치기 고리가 바꾸는 입력(edits, 09의 06_report.md)은 완료를 막지 않음. 다른 입력이 바뀌면 그대로 needs_human
    for f in ("06_report.md", "05_metrics.json"):
        (d / f).write_text("a\n", encoding="utf-8")
    run("timing_report.py", "mark", d, "start", "09_report_check", "--kind", "agents")
    (d / "06_report.md").write_text("b\n", encoding="utf-8")
    run("timing_report.py", "mark", d, "end", "09_report_check", "--kind", "agents")
    st = json.loads((d / "state.json").read_text(encoding="utf-8"))["steps"]["09_report_check"]
    ev = [e for e in map(json.loads, (d / "timing.jsonl").read_text(encoding="utf-8").splitlines()) if e.get("step") == "09_report_check"][-1]
    eq("고치기 입력만 바뀌면 done", (st["status"], "input_hash" in st, ev.get("edited")), ("done", True, ["06_report.md"]))
    run("timing_report.py", "mark", d, "start", "09_report_check", "--kind", "agents")
    (d / "05_metrics.json").write_text("b\n", encoding="utf-8")
    run("timing_report.py", "mark", d, "end", "09_report_check", "--kind", "agents")
    eq("다른 입력이 바뀌면 needs_human", json.loads((d / "state.json").read_text(encoding="utf-8"))["steps"]["09_report_check"]["status"], "needs_human")
    # 2026-10-21: edits 글롭(06의 04_tags_sonnet_*.jsonl)
    for f in ("04_tags_sonnet_A_01.jsonl", "04_audit_sample.jsonl"):
        (d / f).write_text("a\n", encoding="utf-8")
    run("timing_report.py", "mark", d, "start", "06_tag_check", "--kind", "agents")
    (d / "04_tags_sonnet_A_01.jsonl").write_text("b\n", encoding="utf-8")
    run("timing_report.py", "mark", d, "end", "06_tag_check", "--kind", "agents")
    eq("다시 태깅이 바꾼 묶음 파일은 done(글롭 edits)", json.loads((d / "state.json").read_text(encoding="utf-8"))["steps"]["06_tag_check"]["status"], "done")
    # wait_files --batches: 묶음 계획의 sonnet 묶음 파일을 기다림
    (d / "04_batches.json").write_text(json.dumps({"batches": [{"batch_id": "A_01", "models": ["sonnet"]}, {"batch_id": "gold", "models": ["top"]}]}), encoding="utf-8")
    run("wait_files.py", d, "--batches", "04_batches.json", "--settle", "0", "--timeout", "5", "--poll", "0.2")
    (d / "04_batches.json").write_text(json.dumps({"batches": [{"batch_id": "A_02", "models": ["sonnet"]}]}), encoding="utf-8")
    wo = run("wait_files.py", d, "--batches", "04_batches.json", "--settle", "0", "--timeout", "0.5", "--poll", "0.2", expect=1)
    eq("묶음 파일이 빠지면 기다림이 끝나지 않음", "04_tags_sonnet_A_02.jsonl" in wo, True)


def test_g10_rules_known(tmp):
    """공통 경계 규칙(config/detail_rules.yaml)이 맡은 항목의 작업 파일에만 원문 그대로 들어가고,
    알려진 예외(14_known_exceptions.yaml)는 그 회차의 그 (리뷰, 항목)에만 KNOWN으로 걸린다."""
    sys.path.insert(0, str(SCRIPTS))
    import yaml
    import stage_packet as pk
    rules = yaml.safe_load((HERE.parent / "config" / "detail_rules.yaml").read_text(encoding="utf-8"))
    by = {r["id"]: r for r in rules["rules"]}
    r = _detail_run(tmp, "g10-rules-2026-10-07")
    run("stage_packet.py", "detail", r, "--items", "purchase_context")
    txt = (r / "packets" / "detail_w1.md").read_text(encoding="utf-8")
    eq("purchase_context 규칙이 작업 파일에 원문 그대로",
       all(by[k]["rule"] in txt for k in ("repurchase", "gift_direction", "first_purchase")), True)
    eq("comparison_reference 규칙과 값 보충은 안 들어감",
       any(by[k]["rule"] in txt for k in ("comparison_one_value_per_target", "dupe_target", "unclear_same_or_other", "mention_without_comparison"))
       or "store_purchase" in txt, False)
    cr = pk.common_rules(["comparison_reference"])
    eq("comparison_reference 규칙 4개와 store_purchase 값 보충", ([x["id"] for x in cr["rules"]], [n["value"] for n in cr["value_notes"]]),
       (["comparison_one_value_per_target", "dupe_target", "unclear_same_or_other", "mention_without_comparison"], ["store_purchase"]))
    eq("걸리는 항목이 없으면 절이 없음", pk.common_rules(["longevity_hours"]), None)
    # 알려진 예외: 원문에 없는 인용 두 개 가운데 예외 파일에 있는 하나만 KNOWN, 나머지는 묶음 실패
    r = _detail_run(tmp, "g10-known-2026-10-07")
    p = r / "14_details_B0G9TEST01_01.jsonl"
    p.write_text(p.read_text(encoding="utf-8").replace("for my mom 1", "for my aunt 1").replace("for my mom 2", "for my aunt 2"), encoding="utf-8")
    (r / "14_known_exceptions.yaml").write_text(yaml.safe_dump({"exceptions": [
        {"review_id": "R01G9REVIEW", "item": "purchase_context", "reason": "시험"},
        {"review_id": "R02G9REVIEW", "item": "comparison_reference", "reason": "항목이 다르면 안 걸림"}]}, allow_unicode=True), encoding="utf-8")
    out = run("detail.py", "extract-check", r, expect=1)
    ck = json.loads((r / "14_detail_check.json").read_text(encoding="utf-8"))
    eq("KNOWN은 그 리뷰와 항목에만", ([(k["review_id"], k["item"]) for k in ck["known_exceptions"]], ck["dropped_quotes"], ck["failed_batches"]),
       ([("R01G9REVIEW", "purchase_context")], 1, ["B0G9TEST01_01"]))
    eq("KNOWN을 숨기지 않고 보임", "KNOWN(14_known_exceptions.yaml)" in out, True)
    p.write_text(p.read_text(encoding="utf-8").replace("for my aunt 2", "for my mom 2"), encoding="utf-8")
    run("detail.py", "extract-check", r)
    ck = json.loads((r / "14_detail_check.json").read_text(encoding="utf-8"))
    eq("예외만 남으면 PASS(값은 합치지 않음)", (ck["status"], len(ck["known_exceptions"]), ck["values"]), ("PASS", 1, 5))
    r2 = _detail_run(tmp, "g10-other-2026-10-07")     # 예외 파일이 없는 다른 회차에는 걸리지 않음
    p = r2 / "14_details_B0G9TEST01_01.jsonl"
    p.write_text(p.read_text(encoding="utf-8").replace("for my mom 1", "for my aunt 1"), encoding="utf-8")
    run("detail.py", "extract-check", r2, expect=1)
    eq("다른 회차에는 예외가 없음", json.loads((r2 / "14_detail_check.json").read_text(encoding="utf-8"))["known_exceptions"], [])
    real = HERE.parent / "runs" / "perfume-db-2026-10-07" / "14_known_exceptions.yaml"
    if real.exists():
        eq("향수 회차 알려진 예외 두 칸", sorted((e["review_id"], e["item"]) for e in yaml.safe_load(real.read_text(encoding="utf-8"))["exceptions"]),
           [("RLI9E523HGVOC", "desired_state"), ("RW9B7F2AP5A3C", "comparison_reference")])


def test_brand_compare():
    """9장 브랜드 행(sections.brand_compare): 브랜드 X는 ASIN 둘(A1, A2), Y는 B1 하나. 가중치 r1 2, 나머지 1.
    X: 태그 가중치 합 8(전체 만족도 포함), 긍정 r1 향 2 + r2 향 1 + r2 전체 1 = 4 -> 50.0%, 부정 4 -> 50.0%.
    향 긍정 리뷰어 (2 + 1) / 4 = 75.0%, 지속력 부정 리뷰어 (2 + 1) / 4 = 75.0%, 향 부정 리뷰어 1 / 4 = 25.0%.
    강점 향, 2위 강점 없음(전체 만족도는 뺌), 약점 지속력. Y: 향 긍정 하나뿐 -> 긍정 100.0%, 약점 없음."""
    sys.path.insert(0, str(SCRIPTS))
    import sections
    from weight import topic_stats
    reviews = [{"review_id": "r1", "asin": "A1"}, {"review_id": "r2", "asin": "A1"}, {"review_id": "r3", "asin": "A2"},
               {"review_id": "r4", "asin": "B1"}]
    weight = {"r1": 2.0, "r2": 1.0, "r3": 1.0, "r4": 1.0}
    tags = [{"review_id": "r1", "topic": "scent", "sentiment": "positive"},
            {"review_id": "r1", "topic": "longevity_projection", "sentiment": "negative"},
            {"review_id": "r2", "topic": "scent", "sentiment": "positive"},
            {"review_id": "r2", "topic": "overall", "sentiment": "positive"},
            {"review_id": "r3", "topic": "longevity_projection", "sentiment": "negative"},
            {"review_id": "r3", "topic": "scent", "sentiment": "negative"},
            {"review_id": "r4", "topic": "scent", "sentiment": "positive"}]
    schema = {"scent": {"name_ko": "향"}, "longevity_projection": {"name_ko": "지속력"}, "overall": {"name_ko": "전체 만족도"}}
    bc = sections.brand_compare(reviews, tags, weight, schema, {"A1": "X", "A2": "X", "B1": "Y"}, topic_stats, ("overall",), 1)
    x, y = bc
    eq("브랜드 행 X", (x["brand"], x["asins"], x["asin_count"], x["sample_reviews"], x["tags"], x["weighted_pos_pct"], x["weighted_neg_pct"],
                     x["strength"]["id"], x["strength"]["pos_reviewer_pct"], x["strength2"], x["weakness"]["id"], x["weakness"]["neg_reviewer_pct"]),
       ("X", ["A1", "A2"], 2, 3, 6, 50.0, 50.0, "scent", 75.0, None, "longevity_projection", 75.0))
    eq("브랜드 행 Y", (y["asin_count"], y["weighted_pos_pct"], y["weighted_neg_pct"], y["strength"]["pos_reviewer_pct"], y["weakness"]),
       (1, 100.0, 0.0, 100.0, None))
    lines = sections.render_brand_compare(bc, 1)
    eq("브랜드 행 표 한 줄", lines[2], "| X | 2 | 3 | 6 | 50.0% / 50.0% | 향(75.0%) | 없음 | 지속력(75.0%) |")
    # 2위 강점: Y에 지속력 긍정을 더하면 향 100.0%, 지속력 100.0%(같으면 긍정 수, 다음 id 순)
    bc = sections.brand_compare(reviews, tags + [{"review_id": "r4", "topic": "longevity_projection", "sentiment": "positive"}], weight, schema,
                                {"A1": "X", "A2": "X", "B1": "Y"}, topic_stats, ("overall",), 1)
    eq("2위 강점", (bc[1]["strength"]["id"], bc[1]["strength2"]["id"], bc[1]["strength2"]["pos_reviewer_pct"]),
       ("longevity_projection", "scent", 100.0))


def test_leftover_and_unit(tmp):
    """다른 품목에서 남은 말 검사(leftover_problems)와 가이드 단위 가격 기준(unit_basis): 품목과 상관없는 규칙"""
    sys.path.insert(0, str(SCRIPTS))
    import pipeline_io as pio
    import guide_metrics as gm
    run_ = Path(tmp) / "leftover-2026-10-14"
    run_.mkdir()
    (run_ / "05_metrics.json").write_text(json.dumps({"variant_signals": [{"asins": [{"rows": [{"oz": None}]}]}]}), encoding="utf-8")
    text = chr(10).join(["## 11. 변형 신호", "<!-- 표:변형 신호 -->", "| 온스당 가격 | checked_on |", "<!-- /표:변형 신호 -->",
                      "가격은 checked_on 기준이고 온스당 가격은 없습니다.", "원단은 평방야드당 2.6온스 이상이면 면제된다 [r:tst_01].",
                      "CozyFit은 1위다 [m:m.top1_WSET]."])
    errs = pio.leftover_problems(run_, text)
    eq("남은 말 검사(표와 출처 줄은 뺌)", [e.split(":")[0] for e in errs], ["5번째 줄", "5번째 줄"])
    (run_ / "05_metrics.json").write_text(json.dumps({"variant_signals": [{"asins": [{"rows": [{"oz": 1.0}]}]}]}), encoding="utf-8")
    eq("온스 데이터가 있으면 온스는 통과", len(pio.leftover_problems(run_, text)), 1)
    g = gm.G.__new__(gm.G)
    basis = lambda types: g.unit_basis({str(i): {"buyBoxPrice": 10.0, "unitType": t} for i, t in enumerate(types)})["basis"]
    eq("단위 가격 기준", (basis(["Fl Oz", "Ounce"]), basis(["Count", "Count"]), basis(["Count", "Set"]), basis([None])),
       ("oz", "unit", "price", "price"))
    import eval_gold as eg      # 정답 화면 주제 순서: 필수 먼저, 제품, 브랜드, 근거 많은 순
    sc = {"price_value": {"id": "price_value", "side": "B", "evidence_count": 40}, "fit": {"id": "fit", "side": "P", "evidence_count": 10},
          "overall": {"id": "overall", "side": "P", "evidence_count": 5}, "fabric": {"id": "fabric", "side": "P", "evidence_count": 30}}
    eq("정답 화면 주제 순서", [t["id"] for t in eg.sheet_order(sc, ["overall"])], ["overall", "fabric", "fit", "price_value"])


def test_price_complaints():
    """guide_metrics.price_complaints: 온스당 가격 1.0, 1.5, 2.0, 3.0인 상품 넷과 가격 없는 상품 하나. 순위 i x 3 // 4 -> 묶음 0, 0, 1, 2.
    묶음 0(P1 a 2, b 1, P2 c 1): 피부 부정 a 2 / 4 = 50.0%, 효과 부정 c 1 / 4 = 25.0%, 별점 (3 x 4.0 + 1 x 3.0) / 4 = 3.75.
    묶음 1(P3 d, e): 피부 부정 d 1 / 2 = 50.0%, 효과 0.0%, 별점 4.50. 묶음 2(P4 f): 0.0%, 5.00. 가격 없는 상품 1개."""
    sys.path.insert(0, str(SCRIPTS))
    import guide_metrics as gm
    g = object.__new__(gm.G)
    g.conf = {"price_bands": 3, "head_topic": "skin", "direction_index": {"topic": "skin"}, "focus": [{"id": "efficacy", "topics": ["eff"]}]}
    g.schema = {"skin": {"name_ko": "피부 반응"}, "eff": {"name_ko": "털 제거 효과"}}
    asin_of = {"a": "P1", "b": "P1", "c": "P2", "d": "P3", "e": "P3", "f": "P4", "z": "P5"}
    g.reviews = [{"review_id": r, "asin": a, "star": "3", "date": "2026-09-01", "helpful_votes": "0"} for r, a in asin_of.items()]
    g.rev = {r["review_id"]: r for r in g.reviews}
    g.weight = {"a": 2.0, "b": 1.0, "c": 1.0, "d": 1.0, "e": 1.0, "f": 1.0, "z": 1.0}
    g.tags = [{"review_id": "a", "topic": "skin", "sentiment": "negative", "quote": "burned"},
              {"review_id": "b", "topic": "skin", "sentiment": "positive", "quote": "gentle"},
              {"review_id": "c", "topic": "eff", "sentiment": "negative", "quote": "did not work"},
              {"review_id": "d", "topic": "skin", "sentiment": "negative", "quote": "rash"}]
    g.tag = {(t["review_id"], t["topic"]): t for t in g.tags}
    g.brand = {"P1": "B1", "P2": "B2", "P3": "B3", "P4": "B4", "P5": "B5"}
    g.m = {"asins": [{"asin": "P1", "weighted_mean_star": 4.0}, {"asin": "P2", "weighted_mean_star": 3.0}, {"asin": "P3", "weighted_mean_star": 4.5},
                     {"asin": "P4", "weighted_mean_star": 5.0}, {"asin": "P5", "weighted_mean_star": 2.0}]}
    g.values, g.ev, g.quotes = {}, {}, {}
    g.tables = {"s.scoreboard": [{"asin": a, "brand": g.brand[a], "price_per_oz": p} for a, p in
                                 (("P4", 3.0), ("P1", 1.0), ("P5", None), ("P3", 2.0), ("P2", 1.5))]}
    g.price_complaints()
    V = g.values
    eq("가격 묶음 상품", [b["asins"] for b in g.tables["price.bands"]], [["P1", "P2"], ["P3"], ["P4"]])
    eq("가격 묶음 값", [(V[f"price.band{i}.n"]["value"], V[f"price.band{i}.skin_neg"]["value"], V[f"price.band{i}.eff_neg"]["value"],
                       V[f"price.band{i}.star"]["value"]) for i in range(3)],
       [(2, 50.0, 25.0, 3.75), (1, 50.0, 0.0, 4.5), (1, 0.0, 0.0, 5.0)])
    eq("가격 묶음 표기", (V["price.band0.range"]["text"], V["price.band0.skin_neg"]["text"], V["price.band0.star"]["text"],
                       V["price.band0.head_neg"]["value"], V["price.unpriced"]["value"], g.ev["ev.price.band0.skin_neg"]["n"]),
       ("1.00~1.50달러/oz", "50.0%", "3.75★", 50.0, 1, 1))


def test_guide_split_1017(tmp):
    """2026-10-17 가이드 장 묶음(안 B): guide_metrics.make_causes(원인 번호 규칙), early_filter(라벨에 기대는 값 빼기),
    guide_parts.py assemble(장 순서, 맡지 않은 장, 원인 번호 대조, 방향 부호, 1위 단정 경고)."""
    import yaml
    sys.path.insert(0, str(SCRIPTS))
    import guide_metrics as gm
    # 1. 원인 번호: 집중 분석 순서, 기준 순서, 설계 결함 다음 선호 차이, 리뷰 많은 순 2개씩, 리뷰 10개 미만 라벨은 뺌
    focus = [{"id": "snd", "title": "소리", "topics": ["sq"]}, {"id": "bat", "title": "배터리", "topics": ["bl"]}]
    stds = [{"id": "s1", "title": "음질", "neg_labels": ["a", "b", "c", "p", "tiny"]}, {"id": "s2", "title": "배터리", "neg_labels": ["d"]},
            {"id": "s3", "title": "가격", "neg_labels": ["x"]}]
    topic = {"a": "sq", "b": "sq", "c": "sq", "p": "sq", "tiny": "sq", "d": "bl", "x": "pv"}
    revs = {"a": set(range(50)), "b": set(range(30)), "c": set(range(40)), "p": set(range(20)), "tiny": set(range(3)), "d": set(range(12)),
            "x": set(range(99))}
    cs = gm.make_causes(focus, stds, topic, revs, {"a": "A불만"}, preference=["p"])
    eq("원인 번호 규칙", [(c["n"], c["focus"], c["standard_n"], c["type"], [l["id"] for l in c["labels"]]) for c in cs],
       [(1, "snd", 1, "설계 결함", ["a", "c"]), (2, "snd", 1, "설계 결함", ["b"]), (3, "snd", 1, "선호 차이", ["p"]),
        (4, "bat", 2, "설계 결함", ["d"])])
    eq("원인 라벨의 키와 이름", (cs[0]["labels"][0]["key"], cs[0]["labels"][0]["name"], cs[0]["labels"][1]["name"]), ("std.s1.label.a", "A불만", "c"))
    # 2. early_filter: 두 계산(라벨 없음, 모든 라벨)이 다른 값과 안전 기준, 머리 숫자 3은 late_keys로, 남은 값이 쓰는 근거 묶음만 남김
    a = {"values": {"m.x": {"value": 1, "text": "1", "ev": "ev.m"}, "std.s1.neg": {"value": 0, "text": "0개", "ev": "ev.s"},
                    "std.saf.neg": {"value": 5, "text": "5개", "ev": None}, "head.topic_weakest": {"value": 3, "text": "3개", "ev": None}},
         "tables": {"m.t": [1], "s.scoreboard": [{"dir": 0}]}, "ev": {"ev.m": {}, "ev.s": {}, "ev.z": {}}, "quotes": {"ev.m": [], "ev.s": []}}
    b = {**a, "values": {**a["values"], "std.s1.neg": {"value": 9, "text": "9개", "ev": "ev.s"}}, "tables": {"m.t": [1], "s.scoreboard": [{"dir": 1}]}}
    out = gm.early_filter(a, b, {"standards": [{"id": "saf", "safety": True}]})
    eq("미리 쓰기 값 고르기", (sorted(out["values"]), out["late_keys"], sorted(out["tables"]), sorted(out["ev"]), out["mode"]),
       (["m.x"], ["head.topic_weakest", "std.s1.neg", "std.saf.neg"], ["m.t"], ["ev.m"], "early"))
    # 3. guide_parts.py assemble: 묶음 넷을 장 순서로 잇고, 원인 번호와 방향 부호를 대조
    r = Path(tmp) / "bluetoothspeaker-2099-01-01"
    r.mkdir()
    (r / "03_schema_approved.yaml").write_text(yaml.safe_dump({"topics": [{"id": "battery_life", "name_ko": "배터리와 충전", "side": "P"}]},
                                                              allow_unicode=True), encoding="utf-8")
    M = {"values": {"s.B1.dir_index": {"value": 0.09, "text": "+0.09"}, "a.robust.head_first": {"value": 51.6, "text": "51.6%"},
                    "s.B2.dir_index": {"value": -0.1, "text": "-0.10(방향 불분명)"}},
         "tables": {"p.causes": [{"n": 1, "type": "설계 결함", "standard": "sound"}, {"n": 2, "type": "선호 차이", "standard": "sound"}],
                    "std.board": [{"id": "sound", "causes": [1, 2]}, {"id": "value", "causes": []}]}}
    (r / "16_guide_metrics.json").write_text(json.dumps(M, ensure_ascii=False), encoding="utf-8")
    parts = {"01-02-A": "## 01 시장 개요\n시장.\n## 02 경쟁사\nAnker +0.09 [m:s.B1.dir_index]로 저음 부족 쪽이다. Boom -0.10(방향 불분명) [m:s.B2.dir_index]은 저음 부족 쪽으로 읽지 않는다.\n## A 데이터와 방법\n방법.\n",
             "03": "## 03 문제\n- 원인 1(설계 결함), 저음: 근거\n- 원인 2(선호 차이), 취향: 근거\n",
             "04": "## 04 포지셔닝\n#### 기준 1: 음질(원인 1, 2 대응)\n#### 기준 2: 가격(03 원인 밖)\n",
             "head-05": "# 가이드\n> 부제\n## 머리 숫자\n- 배터리와 충전은 비슷한 수준이다.\n## 05 한 장 요약\n요약.\n"}
    for k, v in parts.items():
        (r / f"17_guide_part_{k}.md").write_text(v, encoding="utf-8")
    run("guide_parts.py", "assemble", r)
    g = (r / "17_guide.md").read_text(encoding="utf-8")
    eq("가이드 합치기 순서", [l for l in g.splitlines() if l.startswith("#") and not l.startswith("####")],
       ["# 가이드", "## 머리 숫자", "## 01 시장 개요", "## 02 경쟁사", "## 03 문제", "## 04 포지셔닝", "## 05 한 장 요약", "## A 데이터와 방법"])
    eq("부제는 제목 뒤", g.splitlines()[1], "> 부제")
    bad = {**parts, "03": "## 03 문제\n- 원인 1(선호 차이), 저음: 근거\n## 04 포지셔닝\n",
           "04": "## 04 포지셔닝\n#### 기준 1: 음질(원인 1 대응)\n#### 기준 2: 가격(03 원인 밖)\n",
           "01-02-A": parts["01-02-A"].replace("저음 부족 쪽", "저음 과다 쪽"),
           "head-05": parts["head-05"].replace("비슷한 수준이다", "주제 중 가장 높고 단독 1위다")}
    for k, v in bad.items():
        (r / f"17_guide_part_{k}.md").write_text(v, encoding="utf-8")
    out = run("guide_parts.py", "assemble", r, expect=1)
    chk = json.loads((r / "17_guide_parts_check.json").read_text(encoding="utf-8"))
    eq("가이드 합치기 FAIL 종류", (any("맡지 않은 장 '## 04'" in e for e in chk["errors"]), any("원인 1: '선호 차이'" in e for e in chk["errors"]),
                               any("기준 1 제목의 원인 [1]" in e for e in chk["errors"]), any("'저음 과다' 쪽으로 씀" in e for e in chk["errors"]),
                               len(chk["warnings"])), (True, True, True, True, 1))
    (r / "17_guide_part_04.md").unlink()
    run("guide_parts.py", "assemble", r, expect=1)
    eq("묶음 빠짐", any("17_guide_part_04.md 없음" in e for e in json.loads((r / "17_guide_parts_check.json").read_text(encoding="utf-8"))["errors"]), True)
    run("guide_parts.py", "check", r, "--part", "03", expect=1)
    # 2026-10-19: 미리 쓴 판은 _early.md로 따로 두고 --early로 검사, assemble은 미리 쓴 판을 읽지 않음.
    # 가이드 기계 검사는 합치기 기록이 없거나 FAIL이면 오류(한 명이 전체를 쓴 가이드를 막음)
    (r / "17_guide_part_01-02-A_early.md").write_text(parts["01-02-A"], encoding="utf-8")
    run("guide_parts.py", "check", r, "--part", "01-02-A", "--early")
    run("guide_parts.py", "check", r, "--part", "03", "--early", expect=1)
    sys.path.insert(0, str(SCRIPTS))
    import guide_check as gc
    eq("합치기 FAIL이면 가이드 검사 오류", len(gc.parts_problems(r)), 1)
    (r / "17_guide_parts_check.json").unlink()
    eq("합치기 기록 없으면 가이드 검사 오류", "없음" in gc.parts_problems(r)[0], True)
    for k, v in parts.items():
        (r / f"17_guide_part_{k}.md").write_text(v, encoding="utf-8")
    run("guide_parts.py", "assemble", r)
    eq("합치기 PASS면 오류 없음", gc.parts_problems(r), [])


def test_e2_1017(tmp):
    """2026-10-17 E2: 방향 불분명 규칙(sections.direction_unclear), cross_check.py(방향 부호, 1위 단정, 안전 라벨 구성)"""
    import yaml
    sys.path.insert(0, str(SCRIPTS))
    import sections as sec
    eq("방향 불분명 규칙", (sec.direction_unclear(-0.14, 28), sec.direction_unclear(0.88, 16), sec.direction_unclear(None, 3),
                       sec.fmt_index(-0.14, True), sec.fmt_index(0.88, False)), (True, False, None, "-0.14(방향 불분명)", "+0.88"))
    r = Path(tmp) / "bluetoothspeaker-2098-01-01"
    r.mkdir()
    (r / "01_asins.csv").write_text("asin,title,brand,price_usd,price_band,amazon_rating,status,reason\n"
                                    "B1,t,Anker,1,low,4.5,selected,x\nB2,t,JBL,1,low,4.5,selected,x\n", encoding="utf-8")
    (r / "03_schema_approved.yaml").write_text(yaml.safe_dump({"topics": [
        {"id": "battery_life", "name_ko": "배터리와 충전", "side": "P"}, {"id": "safety", "name_ko": "안전", "side": "P"}]},
        allow_unicode=True), encoding="utf-8")
    (r / "05_robustness.json").write_text(json.dumps({"bootstrap": {"head_first_pct": 51.6}}), encoding="utf-8")
    (r / "07b_issue_counts.json").write_text(json.dumps({"topics": {"safety.negative": {"labels": [
        {"id": "hot", "name_ko": "뜨거워짐", "reviews": 7}, {"id": "smoke", "name_ko": "연기나 불", "reviews": 4},
        {"id": "ear", "name_ko": "귀 통증", "reviews": 3}, {"id": "other", "name_ko": "기타", "reviews": 1}]}}}, ensure_ascii=False), encoding="utf-8")
    (r / "07b_issue_labels.jsonl").write_text(json.dumps({"review_id": "R1", "labels": ["ear"]}) + "\n", encoding="utf-8")
    (r / "07c_safety_verdicts.yaml").write_text(yaml.safe_dump({"audit": {"verdicts": [{"review_id": "R1", "verdict": "symptom", "symptom_type": "귀"}]}},
                                                              allow_unicode=True), encoding="utf-8")
    (r / "06_report.md").write_text("## 8. 핵심\n배터리와 충전은 주제 중 가장 높은 약점이다.\nAnker Black -0.20로 저음 과다 쪽이다.\n"
                                    "안전 부정 라벨: 뜨거워짐 7개만 적고 연기나 불은 뺀 줄은 없음.\n", encoding="utf-8")
    (r / "17_guide.md").write_text("## 02 경쟁사\nAnker +0.30 방향은 저음 부족 쪽이다.\n## 03 문제\n안전 부정에서 제품 위험은 뜨거워짐, 연기나 불이다.\n"
                                   "JBL +0.05(방향 불분명), 배터리와 충전은 품질과 비슷한 수준으로 불만 1위다.\n", encoding="utf-8")
    run("cross_check.py", r, expect=1)
    ck = json.loads((r / "19_cross_check.json").read_text(encoding="utf-8"))
    eq("대조 오류 종류", (sum("방향 부호 반대: Anker" in e for e in ck["errors"]), sum("1위 단정" in e for e in ck["errors"]),
                     sum("안전 라벨 구성" in e for e in ck["errors"])), (1, 1, 0))
    (r / "17_guide.md").write_text("## 03 문제\n안전 부정에서 제품 위험은 뜨거워짐만이고 연기나 불은 없다고 적음, 귀 통증 따로.\n", encoding="utf-8")
    (r / "06_report.md").write_text("## 8. 핵심\n안전 부정 라벨: 뜨거워짐 7개, 귀 통증 3개.\n", encoding="utf-8")
    run("cross_check.py", r, expect=1)
    ck = json.loads((r / "19_cross_check.json").read_text(encoding="utf-8"))
    eq("안전 라벨 빠짐(몸 반응 라벨은 세지 않음)", [e.split(":")[0] for e in ck["errors"]], ["안전 라벨 구성 빠짐"])


def test_speedup_1016(tmp):
    """2026-10-16 속도 개선: report_parts.py(장 묶음 합치기와 표 끼우기, 라벨 전과 뒤 숫자와 표 대조), timing_report.py retry 기록,
    market.Fetcher 동시 호출에서도 호출 한도를 지킴, mcp_http는 HTTP 429를 다시 부름"""
    nl = chr(10)
    if str(SCRIPTS) not in sys.path:
        sys.path.insert(0, str(SCRIPTS))
    # 1. report_parts.py assemble: 묶음 7개를 틀 순서로 잇고 {{표: 이름}} 자리에 05_tables.md 블록을 끼운다
    r = Path(tmp) / "parts-2026-10-16"
    r.mkdir()
    (r / "05_tables.md").write_text(nl.join(["<!-- 표:요약 -->", "| a |", "<!-- /표:요약 -->", "", "<!-- 표:분포 -->", "| b |", "<!-- /표:분포 -->", ""]),
                                    encoding="utf-8")
    first = ["# 아마존 리뷰 분석: 시험", "", "> 데이터: x", "", "{{표: 요약}}", ""]
    for i in range(1, 8):
        first += [f"## {i}. 장", ""] + (["{{표: 분포}}", ""] if i == 1 else []) + ["**데이터 읽기** 내용", ""]
    parts = {"1-7": nl.join(first), "8": "## 8. 핵심 인사이트" + nl + nl + "### 강점" + nl, "9": "## 9. 브랜드(ASIN)별 비교" + nl,
             "10": "## 10. 브랜드 심층" + nl, "11": "## 11. 변형 신호" + nl, "12": "## 12. 전략 방향" + nl, "appendix": "## 부록: 방법과 한계" + nl}
    for k, v in parts.items():
        (r / f"06_report_part_{k}.md").write_text(v, encoding="utf-8")
    run("report_parts.py", "assemble", r)
    rep_ = (r / "06_report.md").read_text(encoding="utf-8")
    eq("표를 끼우고 표 자리를 남기지 않음", ("<!-- 표:요약 -->" + nl + "| a |" + nl + "<!-- /표:요약 -->" in rep_, "<!-- 표:분포 -->" in rep_, "{{표:" in rep_),
       (True, True, False))
    eq("장 순서는 틀과 같음", re.findall(r"^## (\d+)\.", rep_, re.M), [str(i) for i in range(1, 13)])
    chk = json.loads((r / "06_report_parts_check.json").read_text(encoding="utf-8"))
    eq("합치기 검사 PASS", (chk["status"], chk["tables_inserted"], chk["metrics_compared"]), ("PASS", ["분포", "요약"], False))
    # 라벨 전(early)과 뒤(final) 숫자 대조: 라벨 뒤에만 생기는 키(issues, top_issues, generated_at 등)만 다르면 같다고 본다
    (r / "05_metrics_early.json").write_text(json.dumps({"summary": {"reviews": 10}, "generated_at": "a",
                                                        "brand_deep": [{"strengths": [{"topic": "x", "top_issues": []}]}]}), encoding="utf-8")
    (r / "05_metrics.json").write_text(json.dumps({"summary": {"reviews": 10}, "generated_at": "b", "issues": {"x": 1},
                                                  "brand_deep": [{"strengths": [{"topic": "x", "top_issues": [1]}]}]}), encoding="utf-8")
    (r / "05_metrics_early.json").write_text(json.dumps({"summary": {"reviews": 10}, "generated_at": "a", "variant_signals": [{"rows": []}],
                                                        "brand_deep": [{"strengths": [{"topic": "x", "top_issues": []}]}]}), encoding="utf-8")
    (r / "05_tables_early.md").write_text((r / "05_tables.md").read_text(encoding="utf-8"), encoding="utf-8")
    run("report_parts.py", "assemble", r)
    eq("라벨에 기대는 키(세부 이슈, 변형 신호 등)만 다르면 같다고 봄", json.loads((r / "06_report_parts_check.json").read_text(encoding="utf-8"))["metrics_compared"], True)
    (r / "05_tables_early.md").write_text((r / "05_tables.md").read_text(encoding="utf-8").replace("| b |", "| b2 |"), encoding="utf-8")
    out = run("report_parts.py", "assemble", r, expect=1)
    if "미리 쓴 장이 쓰는 표가 라벨 전후로 다름: 분포" not in out:
        FAILS.append(f"미리 쓴 장의 표가 라벨 전후로 다른데 잡지 못함:{nl}{out}")
    (r / "05_tables_early.md").unlink()
    (r / "05_metrics.json").write_text(json.dumps({"summary": {"reviews": 11}, "issues": {}}), encoding="utf-8")
    out = run("report_parts.py", "assemble", r, expect=1)
    if "summary" not in out or "다시 써" not in out:
        FAILS.append(f"early와 final 숫자가 다른데 잡지 못함:{nl}{out}")
    (r / "05_metrics.json").write_text(json.dumps({"summary": {"reviews": 10}}), encoding="utf-8")
    # 표를 직접 붙인 묶음, 다른 장 제목, 묶음 파일 빠짐은 FAIL
    (r / "06_report_part_9.md").write_text("## 9. 브랜드(ASIN)별 비교" + nl + "<!-- 표:브랜드별 비교 -->" + nl, encoding="utf-8")
    out = run("report_parts.py", "check", r, "--part", "9", expect=1)
    if "표를 직접 붙였음" not in out:
        FAILS.append(f"표를 직접 붙인 묶음을 잡지 못함:{nl}{out}")
    (r / "06_report_part_9.md").write_text("## 9. 비교" + nl + "## 10. 심층" + nl, encoding="utf-8")
    out = run("report_parts.py", "check", r, "--part", "9", expect=1)
    if "장 제목이 맞지 않음" not in out:
        FAILS.append(f"다른 장 제목을 잡지 못함:{nl}{out}")
    (r / "06_report_part_9.md").write_text(parts["9"], encoding="utf-8")
    (r / "06_report_part_12.md").unlink()
    out = run("report_parts.py", "assemble", r, expect=1)
    if "묶음 파일 없음: 06_report_part_12.md" not in out:
        FAILS.append(f"빠진 묶음 파일을 잡지 못함:{nl}{out}")
    # 2. timing_report.py retry: 다시 부른 기록을 남기고 시간 표가 단계별로 센다
    d = Path(tmp) / "retry-2026-10-16"
    d.mkdir()
    run("timing_report.py", "mark", d, "start", "22_robustness", "--kind", "script")
    run("timing_report.py", "retry", d, "22_robustness", "--batches", "B1_01, B1_02", "--reason", "인용 검사 실패")
    run("timing_report.py", "mark", d, "end", "22_robustness", "--kind", "script", "--calls", "3", "--retries", "1")
    ev = [json.loads(l) for l in (d / "timing.jsonl").read_text(encoding="utf-8").splitlines()]
    eq("retry 기록(단계, 묶음, 이유)", [(e["step"], e["batches"], e["reason"]) for e in ev if e["event"] == "retry"],
       [("22_robustness", ["B1_01", "B1_02"], "인용 검사 실패")])
    out = run("timing_report.py", "report", d)
    if "다시 부른 기록(retry): 22_robustness 1번(묶음 2개)" not in out:
        FAILS.append(f"시간 표가 retry 기록을 세지 않음:{nl}{out}")
    out = run("timing_report.py", "pause", d, "--reason", "wrong", expect=2)
    if "limit|pc_off" not in out:
        FAILS.append(f"pause의 --reason 검사가 빠짐:{nl}{out}")
    # 3. market.Fetcher: 4개씩 동시에 불러도 호출 한도를 넘지 않고 기록이 섞이지 않는다
    import market
    import threading
    import time
    f = market.Fetcher(Path(tmp) / "mk2", 3)
    seen, lock = [], threading.Lock()

    def fake(*a, **k):
        with lock:
            seen.append(a)
        time.sleep(0.05)
        return ("[]", [])
    market.call_tool = fake
    market.run_all([lambda i=i: f.get("products_history", {"asin": f"B0{i}"}, f"B0{i}") for i in range(8)], 4)
    log = [json.loads(l) for l in (Path(tmp) / "mk2" / "market" / "calls.jsonl").read_text(encoding="utf-8").splitlines()]
    eq("동시 호출에서도 한도 3을 지킴(성공 3, 한도 기록 5)", (len(seen), f.calls, len(log), sum(1 for x in log if x.get("error") == "호출 한도")), (3, 3, 8, 5))
    eq("run_all은 1이면 차례로", market.run_all([lambda: seen.append("x")], 1), None)
    import mcp_http
    import urllib.error
    s = mcp_http.Session.__new__(mcp_http.Session)
    s.server, tries = "x", []

    def once(payload):
        tries.append(1)
        if len(tries) == 1:
            raise urllib.error.HTTPError("u", 429, "too many", {}, None)
        return {"ok": 1}
    s._post_once = once
    waits = mcp_http.RETRY_WAITS
    mcp_http.RETRY_WAITS = (0, 0, 0)
    try:
        eq("HTTP 429는 쉬고 다시 부름", (s._post({"method": "m"}), len(tries)), ({"ok": 1}, 2))
        tries.clear()

        def bad(payload):
            tries.append(1)
            raise urllib.error.HTTPError("u", 401, "no", {}, None)
        s._post_once = bad
        try:
            s._post({"method": "m"})
            FAILS.append("HTTP 401에서 멈추지 않음")
        except mcp_http.MCPError:
            eq("HTTP 401은 바로 멈춤", len(tries), 1)
    finally:
        mcp_http.RETRY_WAITS = waits


def test_dashboard_1019(tmp):
    """2026-10-19 대시보드(scripts/dashboard.py snapshot): 사람 차례, 멈춤, 남은 시간, 정한 것, 신호등, 유료 호출, 막은 기록, 장별 상태"""
    from datetime import datetime, timedelta
    proj = Path(tmp) / "dash_proj"
    (proj / "scripts").mkdir(parents=True)
    (proj / ".claude" / "hooks").mkdir(parents=True)
    for f in ("dashboard.py", "dashboard.html", "pipeline_io.py"):
        shutil.copy(SCRIPTS / f, proj / "scripts" / f)
    shutil.copy(HERE.parent / ".claude" / "hooks" / "guard_runs.py", proj / ".claude" / "hooks" / "guard_runs.py")
    now = datetime.now().astimezone().replace(microsecond=0)

    def at(base, m):
        return (base + timedelta(minutes=m)).isoformat()

    def write_run(name, events, steps):
        d = proj / "runs" / name
        d.mkdir(parents=True)
        (d / "timing.jsonl").write_text("".join(json.dumps(e, ensure_ascii=False) + "\n" for e in events), encoding="utf-8")
        (d / "state.json").write_text(json.dumps({"run": name, "steps": steps}, ensure_ascii=False), encoding="utf-8")
        return d
    # 지난 회차: 주제 초안 끝 0분, 정답지 기다림 10~40분, 리포트와 가이드 HTML 끝 90분 → 남은 AI 시간 60분, 정답지까지 10분
    p0 = now - timedelta(days=2)
    past = [{"ts": at(p0, 0), "event": "step_end", "step": "02_schema_draft", "kind": "agents", "status": "done"},
            {"ts": at(p0, 10), "event": "step_start", "step": "04_gold_tagging", "kind": "human", "status": "needs_human"},
            {"ts": at(p0, 10), "event": "wait_start", "gate": "04_gold_tagging"},
            {"ts": at(p0, 40), "event": "wait_end", "gate": "04_gold_tagging"},
            {"ts": at(p0, 40), "event": "step_end", "step": "04_gold_tagging", "kind": "human", "status": "done"},
            {"ts": at(p0, 80), "event": "step_end", "step": "11_html", "kind": "script", "status": "done"},
            {"ts": at(p0, 90), "event": "step_end", "step": "19_guide_html", "kind": "script", "status": "done"}]
    write_run("cat-2098-01-01", past, {"11_html": {"status": "done"}, "19_guide_html": {"status": "done"}})
    write_run("cat-rt2-2098-01-01", past, {"11_html": {"status": "done"}, "19_guide_html": {"status": "done"}})   # 시험 사본은 빠짐
    c0 = now - timedelta(minutes=5)
    cur = [{"ts": at(c0, 0), "event": "step_end", "step": "02_schema_draft", "kind": "agents", "status": "done"},
           {"ts": at(c0, 1), "event": "step_start", "step": "23_specs", "kind": "agents", "status": "running"},
           {"ts": at(c0, 1), "event": "SubagentStart", "agent_type": "product-spec-collector", "agent_id": "a1"},
           {"ts": at(c0, 2), "event": "SubagentStart", "agent_type": "schema-drafter", "agent_id": "a2"},
           {"ts": at(c0, 3), "event": "SubagentStop", "agent_type": "schema-drafter", "agent_id": "a2"},
           "깨진 줄"]
    d = proj / "runs" / "cat-2098-01-02"
    d.mkdir(parents=True)
    (d / "timing.jsonl").write_text("".join((json.dumps(e, ensure_ascii=False) if isinstance(e, dict) else e) + "\n" for e in cur), encoding="utf-8")
    (d / "state.json").write_text(json.dumps({"run": d.name, "steps": {
        "02_schema_draft": {"status": "done", "kind": "agents", "updated": at(c0, 0)},
        "23_specs": {"status": "running", "kind": "agents", "updated": at(c0, 1)},
        "05_tagging": {"status": "needs_human", "kind": "agents", "updated": at(c0, 2)}}}), encoding="utf-8")
    (proj / "runs" / "CURRENT").write_text(d.name, encoding="utf-8")
    (d / "00_auto_decisions.md").write_text("# 관문\n- 00_asin_review: 7개 승인\n\n| 관문 | 무엇 |\n|---|---|\n| 05a_pilot | 계속 |\n", encoding="utf-8")
    (d / "04_tag_audit_summary.json").write_text(json.dumps({"status": "FAIL", "fail_rate": 0.08}), encoding="utf-8")
    (d / "07_audit.yaml").write_text("audit:\n  overall_status: FAIL\n  findings:\n    - status: FAIL\n    - status: PASS\n", encoding="utf-8")
    (d / "raw").mkdir()
    (d / "raw" / "paid_calls.jsonl").write_text("{}\n{}\n{}\n", encoding="utf-8")
    (d / "00_collect_plan.yaml").write_text("source: paid_below\nmax_paid_calls: 2\n", encoding="utf-8")
    (d / "17_guide_part_01-02-A_early.md").write_text("x", encoding="utf-8")
    (d / "06_report_part_8.md").write_text("x", encoding="utf-8")
    hook = subprocess.run([sys.executable, str(proj / ".claude" / "hooks" / "guard_runs.py")], capture_output=True,
                          input=json.dumps({"tool_name": "Read", "agent_id": "a9", "agent_type": "report-writer",
                                            "tool_input": {"file_path": str(proj / "runs" / "cat-2098-01-01" / "06_report.md")}}).encode("utf-8"))
    eq("막은 호출은 막고 기록", ('"deny"' in hook.stdout.decode("utf-8"), hook.returncode), (True, 0))

    def snap():
        p = subprocess.run([sys.executable, str(proj / "scripts" / "dashboard.py"), "snapshot"], capture_output=True)
        return json.loads(p.stdout.decode("utf-8"))
    s = snap()
    eq("대시보드 도는 단계와 에이전트", ([r["id"] for r in s["running"]], [a["agent_type"] for a in s["agents"]]), (["23_specs"], ["product-spec-collector"]))
    eq("대시보드 멈춘 단계", [r["id"] for r in s["stuck"]], ["05_tagging"])
    eq("대시보드 정한 것(목록과 표, 머리줄 뺌)", [x["text"] for x in s["decisions"]], ["00_asin_review: 7개 승인", "05a_pilot / 계속"])
    chk = {c["name"]: (c["status"], c["detail"]) for c in s["checks"]}
    eq("대시보드 신호등", (chk["태그 감사"], chk["리포트 감사"], chk["입력 검사"][0]), (("FAIL", "실패 8.0%"), ("FAIL", "지적 FAIL 1개"), "NONE"))
    eq("대시보드 유료 호출", s["paid"], {"calls": 3, "limit": 2})
    eq("대시보드 막은 기록", [(g["agent_type"], g["target"]) for g in s["guard"]], [("report-writer", "runs/cat-2098-01-01/06_report.md")])
    ch = s["chapters"]
    eq("대시보드 장별 상태", ([x["state"] for x in ch["guide"]][:2], [x["state"] for x in ch["report"]][:2], ch["guide_early_ran"]),
       (["early", "none"], ["none", "done"], "waiting"))
    e = s["eta"]
    eq("대시보드 남은 시간(지난 회차 60분 - 지난 5분, 시험 사본 뺌)", (e["state"], round(e["minutes_left"]), round(e["gold_minutes"]), e["runs"]),
       ("ok", 55, 5, ["cat-2098-01-01"]))
    eq("대시보드 지난 회차(시험 사본 뺌)", [h["run"] for h in s["history"]], ["cat-2098-01-01", "cat-2098-01-02"])
    eq("대시보드 사람 차례 없음, 끝 아님", (s["human_turn"], s["finished"]), ([], False))
    # 정답지 기다림이 열리면 사람 차례가 되고, 그 시간은 남은 시간 시계에서 빠짐
    with open(d / "timing.jsonl", "a", encoding="utf-8") as f:
        f.write(json.dumps({"ts": at(c0, 0), "event": "wait_start", "gate": "04_gold_tagging"}) + "\n")
    s = snap()
    eq("대시보드 정답지 차례", ([r["name"] for r in s["human_turn"]], round(s["eta"]["minutes_left"])), (["정답지 달기"], 60))
    p = subprocess.run([sys.executable, "-c", "import sys; sys.path.insert(0, sys.argv[1]); import dashboard as d; "
                        "print(d.open_path('../outside.txt')[0], d.open_path('runs/none.txt')[0])", str(proj / "scripts")], capture_output=True)
    eq("대시보드 바로가기는 저장소 안 파일만", p.stdout.decode("utf-8").split(), ["False", "False"])


def main():
    with tempfile.TemporaryDirectory() as tmp:
        r = fresh(tmp, "ok")

        run("check_inputs.py", r)
        # 별점 묶음 검사(v1): 5★만 빠지면 긍정 묶음을 묶음 단위로 보정해 통과,
        # 4★와 5★가 다 빠지면 실제 80%인 긍정 묶음이 비어 오류
        bad = fresh(tmp, "missing_star")
        lines = (bad / "02_reviews.csv").read_text(encoding="utf-8").splitlines()
        (bad / "02_reviews.csv").write_text("\n".join(l for l in lines if "AAA1-05" not in l) + "\n", encoding="utf-8")
        run("check_inputs.py", bad)
        ic = json.loads((bad / "00_input_check.json").read_text(encoding="utf-8"))
        eq("5★만 빠진 긍정 묶음", ic["group_coverage"]["B0TESTAAA1"]["positive"], {"sample": 1, "real_pct": 80.0, "mode": "group"})
        (bad / "02_reviews.csv").write_text("\n".join(l for l in lines if "AAA1-05" not in l and "AAA1-04" not in l) + "\n",
                                            encoding="utf-8")
        out = run("check_inputs.py", bad, expect=1)
        if "positive 묶음(4,5★)에 표본이 없습니다(실제 비율 80.0%)" not in out or "50% 이상" not in out:
            FAILS.append(f"실제 비율 50% 이상인 빈 묶음을 잡지 못함:\n{out}")

        # 묶음 태깅(v1): 픽스처의 정답 세트(gold/gold_reviews.csv)는 사람이 고른 것으로 두고 묶음만 나눈다
        run("tag_batches.py", "plan", r)
        bp = json.loads((r / "04_batches.json").read_text(encoding="utf-8"))
        eq("묶음 계획", [(b["batch_id"], len(b["review_ids"]), b["models"]) for b in bp["batches"]],
           [("B0TESTAAA1_01", 5, ["sonnet"]), ("B0TESTBBB2_01", 6, ["sonnet"]), ("gold", 10, ["sonnet", "top"])])
        eq("시험 태깅 묶음", bp["pilot_batches"], ["B0TESTAAA1_01", "gold"])
        run("audit_quotes.py", "tags", r, "--model", "sonnet", "--batches", "B0TESTAAA1_01")
        if (r / "04_tags.jsonl").exists():
            FAILS.append("일부 묶음만 검사했는데 04_tags.jsonl로 합침")
        run("audit_quotes.py", "tags", r, "--model", "top", expect=1)   # 픽스처의 top gold는 리뷰 하나(B0TESTAAA1-03)를 빠뜨림: 묶음 실패
        run("audit_quotes.py", "tags", r, "--model", "sonnet")
        eq("합친 sonnet 태그 수", len((r / "04_tags.jsonl").read_text(encoding="utf-8").splitlines()), 13)
        qc = json.loads((r / "04_quote_check_sonnet.json").read_text(encoding="utf-8"))
        eq("따옴표 모양만 다른 인용", qc["batches"]["B0TESTBBB2_01"]["quote_whitespace_or_quote_marks"], 1)
        eq("top은 gold 묶음만", list(json.loads((r / "04_quote_check_top.json").read_text(encoding="utf-8"))["batches"]),
           ["gold"])

        badq = fresh(tmp, "bad_quote")
        run("tag_batches.py", "plan", badq)
        p = badq / "04_tags_sonnet_B0TESTAAA1_01.jsonl"
        p.write_text(p.read_text(encoding="utf-8").replace("Lasts maybe an hour", "Lasts about an hour"), encoding="utf-8")
        out = run("audit_quotes.py", "tags", badq, "--model", "sonnet", expect=1)
        if (badq / "04_tags.jsonl").exists():
            FAILS.append("인용이 틀렸는데 태그를 합침")
        eq("실패한 묶음", json.loads((badq / "04_quote_check_sonnet.json").read_text(encoding="utf-8"))["failed_batches"],
           ["B0TESTAAA1_01"])
        # 다른 묶음의 리뷰를 태깅하면 실패
        p.write_text(p.read_text(encoding="utf-8").replace("Lasts about an hour", "Lasts maybe an hour")
                     + json.dumps({"review_id": "B0TESTBBB2-06", "topic": "overall", "sentiment": "positive",
                                   "quote": "Love it"}) + "\n", encoding="utf-8")
        out = run("audit_quotes.py", "tags", badq, "--model", "sonnet", expect=1)
        if "이 묶음의 리뷰가 아닙니다" not in out:
            FAILS.append(f"다른 묶음 리뷰 태그를 잡지 못함:\n{out}")

        run("weight.py", r, "--impact-min", "3", "--strength-min", "2")  # 손계산은 v0 기준값으로
        m = json.loads((r / "05_metrics.json").read_text(encoding="utf-8"))
        # 리포트 작성자용 인용 후보(2026-10-14): 칸마다 10개 이하, 인용과 별점과 브랜드가 원본과 같고, 앞쪽은 별점을 돌아가며 뽑음
        qp = json.loads((r / "05_quote_pool.json").read_text(encoding="utf-8"))
        tq = {(t["review_id"], t["topic"], t["sentiment"]): t["quote"] for t in (json.loads(l) for l in (r / "04_tags.jsonl").read_text(encoding="utf-8").splitlines() if l.strip())}
        rs = {x["review_id"]: x for x in csv.DictReader(open(r / "02_reviews.csv", encoding="utf-8-sig", newline=""))}
        bad = [(k, q["review_id"]) for k, v in qp["pairs"].items() for q in v["quotes"]
               if tq.get((q["review_id"], *k.split("."))) != q["quote"] or int(rs[q["review_id"]]["star"]) != q["star"]
               or q["brand"] != m["brand_of_asin"].get(rs[q["review_id"]]["asin"], "")]
        rot = []
        for k, v in qp["pairs"].items():
            stars_avail = len({int(rs[t[0]]["star"]) for t in tq if f"{t[1]}.{t[2]}" == k and t[0] in rs})
            head = [q["star"] for q in v["quotes"][:stars_avail]]
            if len(set(head)) != len(head):
                rot.append(k)
        eq("인용 후보: 원본과 같음, 칸마다 10개 이하, 별점 돌아가며", (bad, max(len(v["quotes"]) for v in qp["pairs"].values()) <= 10, rot), ([], True, []))
        s = m["summary"]
        eq("가중 평균", s["weighted_mean_star"], 3.84)
        eq("표본 평균", s["sample_mean_star"], 2.82)
        a = {x["asin"]: x for x in m["asins"]}
        eq("A1 가중 평균", a["B0TESTAAA1"]["weighted_mean_star"], 4.25)
        eq("A2 가중 평균", a["B0TESTBBB2"]["weighted_mean_star"], 3.5)
        eq("A2 1★ 가중치", a["B0TESTBBB2"]["weights"]["1"], 0.6)
        t = {x["id"]: x for x in m["topics"]}["longevity_projection"]
        eq("지속력 언급", (t["mentions"], t["negative"], t["positive"], t["mixed"]), (7, 4, 2, 1))
        eq("지속력 부정 비율", t["neg_pct"], 57.1)
        eq("지속력 가중 부정 비율", t["weighted_neg_pct"], 22.1)
        eq("지속력 부정 언급 리뷰어", t["neg_reviewer_pct"], 15.5)
        eq("영향 분석", [(x["id"], x["neg_avg_star"], x["other_avg_star"], x["gap"]) for x in m["impact"]],
           [("longevity_projection", 1.15, 4.33, -3.19)])
        eq("감성 가중 비율", (m["sentiment"]["weighted_pct"]["positive"], m["sentiment"]["weighted_pct"]["negative"]), (79.3, 17.1))
        eq("실제 별점 비율", m["stars"]["real_pct"], {"1": 13.2, "2": 7.7, "3": 10.0, "4": 20.0, "5": 49.1})
        eq("A1 강점과 약점", (a["B0TESTAAA1"]["strength"]["id"], a["B0TESTAAA1"]["strength"]["pos_reviewer_pct"],
                          a["B0TESTAAA1"]["weakness"]["id"], a["B0TESTAAA1"]["weakness"]["neg_reviewer_pct"]),
           ("scent", 80.0, "longevity_projection", 10.0))
        eq("A2 긍정/부정", (a["B0TESTBBB2"]["weighted_pos_pct"], a["B0TESTBBB2"]["weighted_neg_pct"]), (71.4, 21.4))
        bcm = {x["brand"]: x for x in m["brand_compare"]}
        eq("브랜드 행(ASIN 하나면 ASIN 행과 같음)", (bcm["BrandB"]["asin_count"], bcm["BrandB"]["weighted_pos_pct"], bcm["BrandB"]["weighted_neg_pct"],
                                               bcm["BrandA"]["strength"]["id"], bcm["BrandA"]["weakness"]["neg_reviewer_pct"]),
           (1, 71.4, 21.4, "scent", 10.0))

        # 채점(v1): 리포트에 쓰는 sonnet(04_tags.jsonl의 정답 세트 리뷰)으로 판정하고, top(gold 묶음)은 비교
        run("eval_gold.py", "score", r)
        g = json.loads((r / "04_gold_eval.json").read_text(encoding="utf-8"))
        son, top = g["models"]["sonnet"], g["models"]["top"]
        eq("sonnet F1", (son["topic_f1"], son["recall"], son["sentiment_agreement"]), (0.96, 0.923, 1.0))
        eq("상위 모델 F1", (top["topic_f1"], top["sentiment_agreement"]), (0.88, 0.909))
        eq("판정 모델", g["judged_model"], "sonnet")
        eq("예시로 새어 나간 정답 세트", g["gold_used_as_schema_example"], [])
        run("weight.py", r, "--impact-min", "3", "--strength-min", "2")  # 손계산은 v0 기준값으로
        acc = json.loads((r / "05_metrics.json").read_text(encoding="utf-8"))["accuracy"]
        eq("리포트용 정확도", (acc["gold_reviews"], acc["sonnet"], acc["top"]["sentiment_pct"]),
           (10, {"topic_f1": 0.96, "sentiment_pct": 100.0, "topic_f1_text": "0.96", "sentiment_text": "100.0%",
                "direction_pct": 100.0, "direction_text": "100.0%", "direction_pairs": 11, "direction_same": 11,
                "mixed_pct": 100.0, "mixed_text": "100.0%", "mixed_pairs": 1, "mixed_same": 1}, 90.9))
        eq("채점 한 줄 요약", g["summary_ko"],
           ["sonnet: 주제 F1 0.96(기준 0.80, 통과), 감성 방향 일치 100.0%(기준 90.0%, 통과), mixed 일치 100.0%(짝 1개, 기준 없음), 감성 전체 일치 100.0%",
            "top: 주제 F1 0.88(기준 0.80, 통과), 감성 방향 일치 100.0%(기준 90.0%, 통과), mixed 일치 0.0%(짝 1개, 기준 없음), 감성 전체 일치 90.9%"])
        run("eval_gold.py", "score", r, "--f1", "0.90", "--sentiment", "0.95")  # 판정은 sonnet 기준이라 통과
        g = json.loads((r / "04_gold_eval.json").read_text(encoding="utf-8"))
        eq("기준 미달 한 줄 요약", g["models"]["top"]["summary_ko"],
           "top: 주제 F1 0.88(기준 0.90, 0.02 모자람), 감성 방향 일치 100.0%(기준 95.0%, 통과), mixed 일치 0.0%(짝 1개, 기준 없음), 감성 전체 일치 90.9%")
        run("eval_gold.py", "score", r, "--f1", "0.97", expect=1)  # sonnet 0.96 < 0.97이면 실패
        # 시험 태깅: 04_tags.jsonl이 아직 없으면 gold 묶음의 sonnet 태그(04_tags_sonnet_gold.jsonl)로 채점
        pilot = fresh(tmp, "pilot")
        run("tag_batches.py", "plan", pilot)
        run("audit_quotes.py", "tags", pilot, "--model", "sonnet", "--batches", "gold")
        run("eval_gold.py", "score", pilot)
        gp_ = json.loads((pilot / "04_gold_eval.json").read_text(encoding="utf-8"))
        eq("시험 태깅 채점", (gp_["sonnet_source"], gp_["models"]["sonnet"]["topic_f1"]), ("04_tags_sonnet_gold.jsonl", 0.96))
        run("eval_gold.py", "score", r)
        notes = json.loads((r / "05_metrics.json").read_text(encoding="utf-8"))["notes"]
        # 비교에서 전체 만족도 빼기(한 곳에서 정함): 기준을 1로 낮춰도 강점, 약점, 영향 분석, 공출현에 overall이 없다
        ov = fresh(tmp, "overall_rule")
        run("tag_batches.py", "plan", ov)
        run("audit_quotes.py", "tags", ov, "--model", "sonnet")
        run("weight.py", ov, "--impact-min", "1", "--strength-min", "1")
        mo = json.loads((ov / "05_metrics.json").read_text(encoding="utf-8"))
        used = ([x["id"] for x in mo["impact"]] + [x[k]["id"] for x in mo["asins"] for k in ("strength", "weakness") if x[k]]
                + [c[k] for c in mo["cooccurrence_neg"] for k in ("a", "b")])
        eq("비교에서 overall 뺌", ("overall" in used, mo["rules"]["compare_exclude_topics"]), (False, ["overall"]))
        eq("분포에는 overall 남음", any(t["id"] == "overall" and t["mentions"] for t in mo["topics"]), True)
        # 정답지 기준값(영향 분석 20개, 강점과 약점 10개)이 기본값
        run("weight.py", ov)
        mo = json.loads((ov / "05_metrics.json").read_text(encoding="utf-8"))
        eq("시간 추이(픽스처, 회차 이름에 날짜 없음)", mo["time_trend"]["as_of"] is not None, True)
        run("weight.py", ov, "--as-of", "2026-10-07")
        mo = json.loads((ov / "05_metrics.json").read_text(encoding="utf-8"))
        eq("시간 추이 기간별 리뷰", [(p["period"], p["reviews"]) for p in mo["time_trend"]["periods"]],
           [("~2024년", 0), ("2025년", 0), ("2026년 1~6월", 0), ("2026년 7~9월", 11)])
        eq("브랜드 심층 브랜드", [b["brand"] for b in mo["brand_deep"]], ["BrandA", "BrandB"])
        # 카테고리 밖 리뷰(off_category): 그 리뷰의 태그를 빼고 off_category 한 줄만 두면 집계에서 빠지고 부록 문장이 생긴다
        ow = fresh(tmp, "off_category_weight")
        run("tag_batches.py", "plan", ow)
        run("audit_quotes.py", "tags", ow, "--model", "sonnet")
        tg = [json.loads(l) for l in (ow / "04_tags.jsonl").read_text(encoding="utf-8").splitlines()]
        q0 = next(t["quote"] for t in tg if t["review_id"] == "B0TESTBBB2-06")
        tg = [t for t in tg if t["review_id"] != "B0TESTBBB2-06"] + [
            {"review_id": "B0TESTBBB2-06", "topic": "off_category", "sentiment": "neutral", "quote": q0}]
        (ow / "04_tags.jsonl").write_text("".join(json.dumps(t) + "\n" for t in tg), encoding="utf-8")
        run("weight.py", ow)
        mo = json.loads((ow / "05_metrics.json").read_text(encoding="utf-8"))
        eq("off_category 뺌", (mo["summary"]["reviews"], mo["off_category"]["by_asin"], mo["notes"]["off_category_text"]),
           (10, {"B0TESTBBB2": 1}, "이 카테고리와 무관한 리뷰 1개(B0TESTBBB2 1개)는 태거가 off_category로 표시해 모든 집계에서 뺐습니다."))
        oc = fresh(tmp, "off_category_check")
        run("tag_batches.py", "plan", oc)
        bf = oc / "04_tags_sonnet_B0TESTBBB2_01.jsonl"
        bf.write_text(bf.read_text(encoding="utf-8") + json.dumps({"review_id": "B0TESTBBB2-06", "topic": "off_category",
                                                                     "sentiment": "neutral", "quote": q0}) + "\n", encoding="utf-8")
        out = run("audit_quotes.py", "tags", oc, "--model", "sonnet", expect=1)
        if "off_category 리뷰에 다른 태그" not in out:
            FAILS.append(f"off_category와 다른 태그가 함께 있는 리뷰를 잡지 못함:\n{out}")
        eq("브랜드 심층에 overall 없음", any(t["id"] == "overall" for b in mo["brand_deep"] for t in b["top_topics"]), False)
        tb = (ov / "05_tables.md").read_text(encoding="utf-8")
        template = (HERE.parent / "config" / "report_template_ko.md").read_text(encoding="utf-8")
        eq("새 장 표 블록", sorted(re.findall(r"<!-- 표:(.+?) -->", tb)), sorted(re.findall(r"\{\{표: (.+?)\}\}", template)))
        eq("기본 기준값", (mo["rules"]["impact_min_neg_reviews"], mo["rules"]["strength_min_mentions"], mo["impact"]), (20, 10, []))
        head = (ov / "05_tables.md").read_text(encoding="utf-8").split("<!-- /표:요약 -->")[0]
        if "ASIN 2개, 리뷰 11개, 태그 13개, 가중 평균 3.84★, 브랜드 2개, 리뷰 기간 2026-09-01 ~ 2026-09-06" not in head:
            FAILS.append(f"머리 요약 줄이 다름:\n{head}")

        eq("데이터 문구", notes, {
            "data_source": "브라우저로 직접 모음",
            "sample_notice": "표본에는 낮은 별점이 실제보다 많습니다(표본 평균 2.82★, 실제 분포로 되돌린 가중 평균 3.84★).",
            "asin_sample_text": "ASIN당 표본 리뷰 5~6개"})

        tables = (r / "05_tables.md").read_text(encoding="utf-8")
        template = (HERE.parent / "config" / "report_template_ko.md").read_text(encoding="utf-8")
        eq("틀의 표 이름과 05_tables.md 블록 이름", sorted(re.findall(r"\{\{표: (.+?)\}\}", template)),
           sorted(re.findall(r"<!-- 표:(.+?) -->", tables)))
        mc = json.loads((r / "05_metrics.json").read_text(encoding="utf-8"))["must_cover"]     # 8장 약점과 12장 전략에 꼭 넣을 주제
        extra = {8: "\n\n### 약점\n\n" + "\n".join(f"{j}. **{t['name_ko']}이 약점이다** 내용" for j, t in enumerate(mc["weakness"], 1)),
                 12: "\n\n### 제품\n\n" + "\n".join(f"{j}. **{t['name_ko']} 고치기** 근거(8장). 실행: 내용." for j, t in enumerate(mc["strategy"], 1))}
        chapters = "\n\n".join(f"## {i}. 장\n\n**데이터 읽기** 내용" + extra.get(i, "") for i in range(1, 13))
        report = (f"# 아마존 리뷰 분석: 향수\n\n{tables}\n\n{chapters}\n\n"
                  '> "한 시간 정도 간다" (BrandA, 1★, B0TESTAAA1-01)\n\n## 부록: 방법과 한계\n')
        (r / "06_report.md").write_text(report, encoding="utf-8")
        run("audit_quotes.py", "report", r)
        (r / "06_report.md").write_text(report.replace("BrandA, 1★", "BrandA, 2★"), encoding="utf-8")
        out = run("audit_quotes.py", "report", r, expect=1)
        if "실제는 1★" not in out:
            FAILS.append("인용 별점 오류를 잡지 못함")
        if "| 7 | 2 | 4 |" not in report:
            FAILS.append("시험용 표 줄을 찾지 못함")
        (r / "06_report.md").write_text(report.replace("| 7 | 2 | 4 |", "| 7 | 2 | 5 |"), encoding="utf-8")
        run("audit_quotes.py", "report", r, expect=1)

        hook = r / "timing.jsonl"
        hook.write_text("\n".join(json.dumps(x) for x in [
            {"ts": "2026-10-07T10:00:00+09:00", "event": "step_start", "step": "check_inputs", "kind": "script"},
            {"ts": "2026-10-07T10:00:30+09:00", "event": "step_end", "step": "check_inputs", "kind": "script"},
            {"ts": "2026-10-07T10:01:00+09:00", "event": "SubagentStart", "agent_type": "review-tagger", "agent_id": "a1"},
            {"ts": "2026-10-07T10:01:00+09:00", "event": "SubagentStart", "agent_type": "review-tagger", "agent_id": "a2"},
            {"ts": "2026-10-07T10:05:00+09:00", "event": "SubagentStop", "agent_type": "review-tagger", "agent_id": "a1"},
            {"ts": "2026-10-07T10:07:00+09:00", "event": "SubagentStop", "agent_type": "review-tagger", "agent_id": "a2"},
            {"ts": "2026-10-07T10:07:00+09:00", "event": "step_start", "step": "schema_approval", "kind": "human"},
            {"ts": "2026-10-07T10:17:00+09:00", "event": "step_end", "step": "schema_approval", "kind": "human"},
        ]) + "\n", encoding="utf-8")
        out = run("timing_report.py", "report", r)
        for want in ("전체 경과: 17.0분", "사람 대기: 10.0분", "기계 시간(전체 경과 - 사람 대기): 7.0분", "에이전트 작업 시간 합: 10.0분"):
            if want not in out:
                FAILS.append(f"시간 표에 '{want}'가 없음:\n{out}")

        # 스키마 검사: 예시 인용이 원문에 없거나 정답 세트 리뷰면 실패
        out = run("check_inputs.py", r, "--schema")
        # overall 공통 태깅 규칙(2026-10-10): 픽스처 스키마에 tagging_rule이 없으면 주의, 공통 문장을 넣으면 주의 없음
        eq("overall tagging_rule 없음 주의", "overall의 tagging_rule이 없거나" in out, True)
        import yaml
        ov_rule = next(t["tagging_rule"] for t in yaml.safe_load((HERE.parent / "config" / "topics_common.yaml").read_text(encoding="utf-8"))["topics"]
                       if t["id"] == "overall")
        ok_schema = fresh(tmp, "ok_schema")
        osp = ok_schema / "03_schema_approved.yaml"
        sch = yaml.safe_load(osp.read_text(encoding="utf-8"))
        for t in sch["topics"]:
            if t["id"] == "overall" or t.get("common_id") == "overall":
                t["tagging_rule"] = ov_rule
        osp.write_text(yaml.safe_dump(sch, allow_unicode=True, sort_keys=False), encoding="utf-8")
        out = run("check_inputs.py", ok_schema, "--schema")
        eq("overall tagging_rule 공통 문장이면 주의 없음", "overall의 tagging_rule이 없거나" in out, False)
        bad_schema = fresh(tmp, "bad_schema")
        sp = bad_schema / "03_schema_approved.yaml"
        sp.write_text(sp.read_text(encoding="utf-8").replace("Does not last at all", "Does not last long"), encoding="utf-8")
        out = run("check_inputs.py", bad_schema, "--schema", expect=1)
        if "원문에 없습니다" not in out:
            FAILS.append("스키마 예시 인용 오류를 잡지 못함")
        sp.write_text(sp.read_text(encoding="utf-8").replace(
            'review_id: B0TESTBBB2-02\n        quote: "Does not last long"',
            'review_id: B0TESTAAA1-01\n        quote: "Lasts maybe an hour"'), encoding="utf-8")
        out = run("check_inputs.py", bad_schema, "--schema", expect=1)
        if "정답 세트 리뷰라" not in out:
            FAILS.append("정답 세트 리뷰를 예시로 쓴 것을 잡지 못함")

        # 정답 세트 형식 검사
        run("eval_gold.py", "gold", r)
        gp = r / "gold" / "gold_tags.jsonl"
        good_gold = gp.read_text(encoding="utf-8")
        gp.write_text(good_gold.replace('"price_value"', '"price"', 1), encoding="utf-8")
        out = run("eval_gold.py", "gold", r, expect=1)
        if "스키마에 없는 주제 price" not in out:
            FAILS.append("정답 세트의 틀린 주제를 잡지 못함")
        gp.write_text(good_gold, encoding="utf-8")

        # 태그 검수 집계: 정답 세트 리뷰의 태그는 감사 표본에서 빠진다. 픽스처는 정답 세트가 거의 전부라 이 시험만 정답 세트를 한 리뷰로 줄인다.
        gcsv = r / "gold" / "gold_reviews.csv"
        gold_full = gcsv.read_text(encoding="utf-8-sig")
        head_ = gold_full.splitlines()[0]
        gcsv.write_text(head_ + chr(10) + next(l for l in gold_full.splitlines() if l.startswith("B0TESTBBB2-06")) + chr(10), encoding="utf-8")
        run("eval_gold.py", "audit-sample", r, "--parts", "1")
        smp = [json.loads(l) for l in (r / "04_audit_sample.jsonl").read_text(encoding="utf-8").splitlines()]
        n06 = sum(1 for l in (r / "04_tags.jsonl").read_text(encoding="utf-8").splitlines() if '"B0TESTBBB2-06"' in l)
        eq("감사 표본에서 정답 세트 리뷰 빠짐", (len(smp), any(t["review_id"] == "B0TESTBBB2-06" for t in smp)), (13 - n06, False))
        audit_yaml = """audit:
  stage: tags
  run: fixture
  overall_status: FAIL
  summary: 시험
  checked: {checked}
  findings:
    - review_id: B0TESTAAA1-02
      topic: longevity_projection
      status: FAIL
      finding: 시험
      required_action: 시험
    - review_id: B0TESTBBB2-04
      topic: longevity_projection
      status: UNVERIFIED
      finding: 시험
      required_action: 시험
    - review_id: B0TESTBBB2-06
      topic: scent
      status: FAIL
      finding: 정답 세트 리뷰라 세지 않음
      required_action: 시험
  missed:
    - {{review_id: B0TESTBBB2-01, topic: scent, reason: "Smells like alcohol at first"}}
  next_action: RETURN_TO_OWNER
"""
        (r / "04_tag_audit.yaml").write_text(audit_yaml.format(checked=len(smp)), encoding="utf-8")
        out = run("eval_gold.py", "audit", r, expect=1)
        a = json.loads((r / "04_tag_audit_summary.json").read_text(encoding="utf-8"))
        n = len(smp)
        eq("검수 집계", (a["fail"], a["unverified"], a["missed"], a["fail_rate"], a["conservative_rate"], a["asins_with_findings"]),
           (1, 1, 1, round(1 / n, 3), round(3 / (n + 1), 3), ["B0TESTAAA1", "B0TESTBBB2"]))
        eq("검수 집계 묶음과 ASIN별", (a["batches_with_findings"], a["by_asin"]["B0TESTAAA1"]["fail"]), (["B0TESTAAA1_01", "B0TESTBBB2_01"], 1))
        run("eval_gold.py", "audit", r, "--max-fail", "0.20")
        # 옛 표본에 정답 세트 태그가 섞여 있으면 빼고 센다
        g06 = [l for l in (r / "04_tags.jsonl").read_text(encoding="utf-8").splitlines() if '"B0TESTBBB2-06"' in l][:1]
        with open(r / "04_audit_sample.jsonl", "a", encoding="utf-8") as f:
            f.write(g06[0] + chr(10))
        (r / "04_tag_audit.yaml").write_text(audit_yaml.format(checked=n + 1), encoding="utf-8")
        run("eval_gold.py", "audit", r, expect=1)
        a = json.loads((r / "04_tag_audit_summary.json").read_text(encoding="utf-8"))
        eq("옛 표본의 정답 세트 태그는 빼고 셈", (a["sample_tags"], a["excluded_gold_tags"], a["fail"], a["warnings"][:0]), (n, 1, 1, []))
        gcsv.write_text(gold_full, encoding="utf-8")

        # 단계 상태: mark가 state.json을 바꾸고, 에이전트 단계 행은 에이전트 시간 합에 들어가지 않음
        run("timing_report.py", "mark", r, "start", "03_schema_approval", "--kind", "human")
        st = json.loads((r / "state.json").read_text(encoding="utf-8"))
        eq("사람 대기 상태", st["steps"]["03_schema_approval"]["status"], "needs_human")
        run("timing_report.py", "mark", r, "end", "03_schema_approval", "--kind", "human", expect=1)   # 30초 안에 끝: 답 받기 전에 찍은 것으로 보고 거절
        run("timing_report.py", "mark", r, "end", "03_schema_approval", "--kind", "human", "--force")
        run("timing_report.py", "mark", r, "start", "05_tagging", "--kind", "agents")
        run("timing_report.py", "mark", r, "stop", "05_tagging", "--kind", "agents")
        st = json.loads((r / "state.json").read_text(encoding="utf-8"))
        eq("단계 상태", (st["steps"]["03_schema_approval"]["status"], st["steps"]["05_tagging"]["status"]),
           ("done", "needs_human"))
        hook.write_text("\n".join(json.dumps(x) for x in [
            {"ts": "2026-10-07T10:00:00+09:00", "event": "step_start", "step": "05_tagging", "kind": "agents"},
            {"ts": "2026-10-07T10:00:00+09:00", "event": "SubagentStart", "agent_type": "review-tagger", "agent_id": "a1"},
            {"ts": "2026-10-07T10:04:00+09:00", "event": "SubagentStop", "agent_type": "review-tagger", "agent_id": "a1"},
            {"ts": "2026-10-07T10:05:00+09:00", "event": "step_end", "step": "05_tagging", "kind": "agents"},
        ]) + "\n", encoding="utf-8")
        out = run("timing_report.py", "report", r)
        if "에이전트 작업 시간 합: 4.0분" not in out:
            FAILS.append(f"에이전트 단계 행이 에이전트 시간 합에 섞임:\n{out}")
        # 같은 단계를 두 번 시작하면 마지막 시도만 더한 기계 시간을 따로 적음
        hook.write_text("\n".join(json.dumps(x) for x in [
            {"ts": "2026-10-07T10:00:00+09:00", "event": "step_start", "step": "08_report", "kind": "agents"},
            {"ts": "2026-10-07T10:06:00+09:00", "event": "step_end", "step": "08_report", "kind": "agents"},
            {"ts": "2026-10-07T10:10:00+09:00", "event": "step_start", "step": "08_report", "kind": "agents"},
            {"ts": "2026-10-07T10:12:00+09:00", "event": "step_end", "step": "08_report", "kind": "agents"},
            {"ts": "2026-10-07T10:12:00+09:00", "event": "step_start", "step": "10_timing", "kind": "script"},
            {"ts": "2026-10-07T10:12:30+09:00", "event": "step_end", "step": "10_timing", "kind": "script"},
        ]) + "\n", encoding="utf-8")
        out = run("timing_report.py", "report", r)
        if "08_report 2번. 단계마다 마지막 시도만 더한 기계 시간은 2.5분" not in out:
            FAILS.append(f"다시 돌린 단계를 따로 적지 않음:\n{out}")
        # 시간 나눔(2026-10-13): AI 작업(벽시계, 기다림과 라벨링과 멈춤 뺌), 라벨링(화면 기록), 기다림(라벨링 뺌), 멈춤, 끝 없는 에이전트
        hook.write_text("\n".join(json.dumps(x) for x in [
            {"ts": "2026-10-07T10:00:00+09:00", "event": "step_start", "step": "02_schema_draft", "kind": "agents"},
            {"ts": "2026-10-07T10:02:00+09:00", "event": "SubagentStart", "agent_type": "schema-drafter", "agent_id": "s1"},
            {"ts": "2026-10-07T10:08:00+09:00", "event": "SubagentStop", "agent_type": "schema-drafter", "agent_id": "s1"},
            {"ts": "2026-10-07T10:10:00+09:00", "event": "step_end", "step": "02_schema_draft", "kind": "agents"},
            {"ts": "2026-10-07T10:10:00+09:00", "event": "wait_start", "gate": "03_schema_approval"},
            {"ts": "2026-10-07T10:20:00+09:00", "event": "SubagentStart", "agent_type": "benchmark-researcher", "agent_id": "b1"},
            {"ts": "2026-10-07T10:25:00+09:00", "event": "SubagentStop", "agent_type": "benchmark-researcher", "agent_id": "b1"},
            {"ts": "2026-10-07T11:00:00+09:00", "event": "wait_end", "gate": "03_schema_approval"},
            {"ts": "2026-10-07T11:00:00+09:00", "event": "SubagentStart", "agent_type": "review-tagger", "agent_id": "t1"},
            {"ts": "2026-10-07T11:20:00+09:00", "event": "pause", "from": "2026-10-07T11:05:00+09:00", "reason": "limit"},
        ]) + "\n", encoding="utf-8")
        out = run("timing_report.py", "report", r)
        for want in ("AI 작업(벽시계, 겹친 시간은 한 번): 10.0분", "담당자 라벨링: 기록 없음", "담당자 기다림(라벨링과 멈춤 뺌): 50.0분(관문 1번)",
                     "멈춤: 15.0분(사용량 한도 1번)", "끝 기록 없는 에이전트 실행: 1개", "schema-drafter 6.0분(1번)"):
            if want not in out:
                FAILS.append(f"시간 나눔에 '{want}'가 없음:\n{out}")
        (r / "gold").mkdir(exist_ok=True)
        (r / "gold" / "gold_label_times.json").write_text(json.dumps({"events": [
            {"event": "open", "ts": "2026-10-07T01:15:00.000Z"}, {"event": "save", "ts": "2026-10-07T01:25:00.000Z"},
            {"event": "open", "ts": "2026-10-07T01:40:00.000Z"}, {"event": "submit", "ts": "2026-10-07T01:50:00.000Z"},
            {"event": "open", "ts": "2026-10-07T01:55:00.000Z"}]}), encoding="utf-8")
        out = run("timing_report.py", "report", r)
        for want in ("담당자 라벨링: 20.0분(화면을 연 구간 2개, 끝을 모르는 구간 1개는 시간에 넣지 않음)",
                     "담당자 기다림(라벨링과 멈춤 뺌): 30.0분(관문 1번)", "AI 작업(벽시계, 겹친 시간은 한 번): 10.0분"):
            if want not in out:
                FAILS.append(f"라벨링 시간에 '{want}'가 없음:\n{out}")
        (r / "gold" / "gold_label_times.json").unlink()
        hook.write_text("", encoding="utf-8")
        run("timing_report.py", "wait", r, "start", "07a_issue_approval")
        run("timing_report.py", "wait", r, "end", "07a_issue_approval", expect=1)   # 30초 안 end는 거절
        run("timing_report.py", "wait", r, "end", "07a_issue_approval", "--force")
        run("timing_report.py", "pause", r, "--reason", "pc_off")
        evs = [json.loads(l)["event"] for l in hook.read_text(encoding="utf-8").splitlines()]
        eq("wait와 pause 기록", evs, ["wait_start", "wait_end", "pause"])

        # 시간 기록 Hook: runs/CURRENT의 회차에 한 줄을 덧붙이고, 늘 종료 코드 0
        proj = Path(tmp) / "proj"
        (proj / ".claude" / "hooks").mkdir(parents=True)
        (proj / "runs" / "r1").mkdir(parents=True)
        (proj / "runs" / "CURRENT").write_text("r1\n", encoding="utf-8")
        shutil.copy(HERE.parent / ".claude" / "hooks" / "timing.py", proj / ".claude" / "hooks" / "timing.py")
        for ev in ("SubagentStart", "SubagentStop"):
            p = subprocess.run([sys.executable, str(proj / ".claude" / "hooks" / "timing.py")],
                               input=json.dumps({"hook_event_name": ev, "agent_type": "review-tagger",
                                                 "agent_id": "x1", "session_id": "s"}).encode("utf-8"),
                               capture_output=True)
            if p.returncode != 0:
                FAILS.append(f"Hook 종료 코드 {p.returncode}")
        rows = [json.loads(l) for l in (proj / "runs" / "r1" / "timing.jsonl").read_text(encoding="utf-8").splitlines()]
        eq("Hook 기록", [(x["event"], x["agent_type"], x["agent_id"]) for x in rows],
           [("SubagentStart", "review-tagger", "x1"), ("SubagentStop", "review-tagger", "x1")])
        p = subprocess.run([sys.executable, str(proj / ".claude" / "hooks" / "timing.py")], input=b"not json",
                           capture_output=True)
        eq("Hook이 잘못된 입력에도 종료 코드 0", p.returncode, 0)
        # 다른 회차 막는 Hook(2026-10-17): 하위 에이전트만, 지금 회차와 config는 열고, 다른 회차와 시험 기록, 저장소 전체 훑기는 막음
        shutil.copy(HERE.parent / ".claude" / "hooks" / "guard_runs.py", proj / ".claude" / "hooks" / "guard_runs.py")
        (proj / "runs" / "r0").mkdir()

        def guard(tool, inp, agent="a1"):
            d = {"tool_name": tool, "tool_input": inp, **({"agent_id": agent} if agent else {})}
            p = subprocess.run([sys.executable, str(proj / ".claude" / "hooks" / "guard_runs.py")], input=json.dumps(d).encode("utf-8"),
                               capture_output=True)
            out = p.stdout.decode("utf-8")
            return ("deny" if '"deny"' in out else "allow", p.returncode)
        P = str(proj)
        eq("다른 회차 막기", [guard("Read", {"file_path": P + "\\runs\\r0\\06_report.md"}),
                           guard("Read", {"file_path": P + "\\runs\\r1\\05_metrics.json"}),
                           guard("Read", {"file_path": P + "\\runs\\r0\\06_report.md"}, agent=None),
                           guard("Read", {"file_path": P + "\\docs\\experiments_1016.md"}),
                           guard("Read", {"file_path": P + "\\config\\report_template_ko.md"}),
                           guard("Grep", {"pattern": "x"}),
                           guard("Grep", {"pattern": "x", "path": P + "\\runs\\r1"}),
                           guard("Glob", {"pattern": "runs/*/06_report*.md", "path": P}),
                           guard("Glob", {"pattern": "*.md", "path": P + "\\config"}),
                           guard("Bash", {"command": "cat runs/r0/06_report.md"})],
           [("deny", 0), ("allow", 0), ("allow", 0), ("deny", 0), ("allow", 0), ("deny", 0), ("allow", 0), ("deny", 0), ("allow", 0), ("deny", 0)])

        test_star_groups()
        test_price_band()
        test_brand_compare()
        test_price_complaints()
        test_leftover_and_unit(tmp)
        test_sections()
        test_variant()
        test_issues(Path(tmp))
        test_collect(Path(tmp))
        test_collect_rank_paid(Path(tmp))
        test_pick_and_sheet(Path(tmp))
        test_audit_sample(Path(tmp))
        test_render_html(Path(tmp))
        test_market_detail(Path(tmp))
        test_guide_pipeline(Path(tmp))
        test_i18n(Path(tmp))
        test_robustness_specs(Path(tmp))
        test_speaker_review_fixes()
        test_off_category(Path(tmp))
        test_fake_category(Path(tmp))
        test_sentiment_split()
        test_helpful_provisional()
        test_common_topic()
        test_stage_plan_packet(Path(tmp))
        try:
            test_g9_review_fixes(Path(tmp))
        except BaseException as e:   # 고치기 전 재현용: 예외도 실패로 센다
            FAILS.append(f"test_g9_review_fixes 예외: {type(e).__name__}: {e}")
        test_g10_rules_known(Path(tmp))
        test_speedup_1016(Path(tmp))
        test_guide_split_1017(Path(tmp))
        test_e2_1017(Path(tmp))
        test_dashboard_1019(Path(tmp))

    if FAILS:
        print("실패:")
        for f in FAILS:
            print(" -", f)
        sys.exit(1)
    print(f"스크립트 자체 시험 통과({CHECKS[0]}개 확인): 입력 검사, 별점 묶음 보정, 수집 변환, 스키마 검사, 정답 세트 고르기와 형식, 태그 검사, 가중 집계, 채점, "
          "검수 집계, 리포트 검사, 시간 표와 단계 상태, 시간 기록 Hook, 대시보드")


if __name__ == "__main__":
    main()
