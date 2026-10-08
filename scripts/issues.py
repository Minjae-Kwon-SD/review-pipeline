"""세부 이슈 목록: 표본 뽑기, 초안 합치기와 검사.

사용: python scripts/issues.py sample [회차] [--per 150] [--min 20]
  04_tags.jsonl에서 주제(전체 만족도 제외)와 방향마다 인용을 모은다.
  방향: negative(부정과 혼합 인용), positive(긍정과 혼합 인용). 중립은 뺀다.
  인용이 min개 미만인 주제와 방향은 목록 없이 "기타"만 둔다(표본을 만들지 않음).
  그 밖에는 최대 per개를 ASIN과 별점 묶음(부정 1,2★ / 중립 3★ / 긍정 4,5★)이 고르게 섞이게 뽑는다(회차 이름으로 시드 고정).
  결과: 07a_issue_plan.json(주제와 방향마다 인용 수, 표본 수, 표본 파일), 07a_issue_samples/<주제>_<방향>.jsonl
  (review_id, asin, star, sentiment, quote). issue-labeler가 이 파일만 읽는다.

사용: python scripts/issues.py merge [회차]
  issue-labeler가 주제마다 쓴 07a_issues_<주제>.yaml을 합치고 검사해 07a_issues_draft.yaml과 07a_issues_draft.md를 쓴다.
  검사: 주제와 방향마다 라벨 8개 이하, id 겹침 없음, 라벨마다 이름(한국어, 영어), 정의(포함, 제외), 대표 인용 2개가
  그 표본에 있는 review_id인지, 어림 개수가 표본의 5% 이상인지(아니면 기타로 합쳐야 함). 오류가 있으면 종료 코드 1.

승인 뒤(07a_issues_approved.yaml):
  approve [회차] --approved-at --approved-by   초안을 승인본으로 복사하고 승인 기록을 남긴다.
  label-plan [회차] [--size 180]   라벨 붙일 인용(전체 만족도와 중립 제외, 혼합은 두 방향)을 주제와 방향별 묶음으로.
                                    기타만 있는 주제와 방향은 스크립트가 기타로 채운다(07b_labels_auto.jsonl).
  label-check [회차]               issue-tagger 출력(07b_labels_<묶음>.jsonl) 검사, 합치기(07b_issue_labels.jsonl),
                                    개수(07b_issue_counts.json: 라벨마다 리뷰 수, 가중 비율, ASIN별, 기타 비율, 향과 신뢰 겹침).
  audit-sample [회차] [--n 150]    라벨 감사 표본(ASIN과 주제 칸을 고르게). audit [회차]: 07b_issue_audit.yaml의 FAIL 비율.
  safety-input, safety-render      안전 주제 인용 전부와 evidence-auditor 판정을 합친 07c_safety_check.md.
"""
import argparse
import hashlib
import json
import random
import sys
from collections import Counter, defaultdict
from pathlib import Path

from pipeline_io import (REVIEW_COLS, die, load_csv_or_die, load_schema, load_yaml, now_iso, pct, read_jsonl,
                         resolve_run, write_json, write_jsonl)

EXCLUDE = ("overall", "off_category")       # 리뷰 단위 총평이라 세부 이슈를 나누지 않는다(weight.py COMPARE_EXCLUDE와 같은 원칙)
DIRECTIONS = {"negative": ("negative", "mixed"), "positive": ("positive", "mixed")}
GROUP = {1: "neg", 2: "neg", 3: "neu", 4: "pos", 5: "pos"}
MAX_LABELS = 8
MIN_SHARE = 0.05
# 같은 리뷰에 함께 붙는지 셀 두 라벨은 config/categories/<카테고리>.yaml의 issues.overlap(없으면 세지 않음)


def seeded(run, salt):
    return random.Random(int(hashlib.sha256(f"{run.name}:{salt}".encode("utf-8")).hexdigest()[:12], 16))


def stratified(items, k, rng):
    """(ASIN, 별점 묶음) 칸마다 섞어 돌아가며 하나씩 뽑는다."""
    cells = defaultdict(list)
    for it in sorted(items, key=lambda x: (x["review_id"], x["quote"])):
        cells[(it["asin"], GROUP[it["star"]])].append(it)
    for v in cells.values():
        rng.shuffle(v)
    keys = sorted(cells)
    out = []
    while len(out) < k and any(cells[c] for c in keys):
        for c in keys:
            if len(out) >= k:
                break
            if cells[c]:
                out.append(cells[c].pop())
    return out


def sample(run, per, min_n):
    schema = load_schema(run)
    reviews = {r["review_id"]: r for r in load_csv_or_die(run / "02_reviews.csv", REVIEW_COLS)}
    tags = [t for t in read_jsonl(run / "04_tags.jsonl") if t["topic"] in schema]
    outdir = run / "07a_issue_samples"
    outdir.mkdir(exist_ok=True)
    plan = {"made_at": now_iso(), "per": per, "min": min_n, "exclude": list(EXCLUDE), "items": []}
    for tid in schema:
        if tid in EXCLUDE:
            continue
        for direction, sents in DIRECTIONS.items():
            items = [{"review_id": t["review_id"], "asin": reviews[t["review_id"]]["asin"],
                      "star": int(reviews[t["review_id"]]["star"]), "sentiment": t["sentiment"], "quote": t["quote"]}
                     for t in tags if t["topic"] == tid and t["sentiment"] in sents]
            entry = {"topic": tid, "name_ko": schema[tid]["name_ko"], "direction": direction, "quotes": len(items)}
            if len(items) < min_n:
                entry.update({"sampled": 0, "file": None, "only_other": True})
            else:
                picked = stratified(items, per, seeded(run, f"{tid}:{direction}"))
                name = f"{tid}_{direction}.jsonl"
                write_jsonl(outdir / name, picked)
                entry.update({"sampled": len(picked), "file": f"07a_issue_samples/{name}", "only_other": False,
                              "by_asin": dict(Counter(p["asin"] for p in picked)),
                              "by_star_group": dict(Counter(GROUP[p["star"]] for p in picked))})
            plan["items"].append(entry)
    write_json(run / "07a_issue_plan.json", plan)
    total = sum(e["sampled"] for e in plan["items"])
    print(f"세부 이슈 표본: 주제와 방향 {len(plan['items'])}개, 표본 인용 {total}개 → 07a_issue_samples/, 07a_issue_plan.json")
    for e in plan["items"]:
        print(f"  {e['topic']:<22} {e['direction']:<8} 인용 {e['quotes']:>4}개, 표본 {e['sampled']:>3}개"
              + ("  (20개 미만이라 기타만)" if e["only_other"] else ""))
    return 0


def merge(run):
    schema = load_schema(run)
    plan = json.loads((run / "07a_issue_plan.json").read_text(encoding="utf-8"))
    errors, warns, topics = [], [], []
    sample_ids = {}
    for e in plan["items"]:
        if e["file"]:
            sample_ids[(e["topic"], e["direction"])] = {json.loads(l)["review_id"]
                                                         for l in (run / e["file"]).read_text(encoding="utf-8").splitlines() if l}
    seen_ids = set()
    for tid in [t for t in schema if t not in EXCLUDE]:
        path = run / f"07a_issues_{tid}.yaml"
        if not path.exists():
            errors.append(f"{path.name}이(가) 없습니다.")
            continue
        data = load_yaml(path) or {}
        entry = {"topic": tid, "name_ko": schema[tid]["name_ko"], "directions": {}}
        for direction in DIRECTIONS:
            pe = next(x for x in plan["items"] if x["topic"] == tid and x["direction"] == direction)
            d = ((data.get("directions") or {}).get(direction)) or {}
            labels = d.get("labels") or []
            where = f"{tid} {direction}"
            if pe["only_other"] and labels:
                errors.append(f"{where}: 인용이 {pe['quotes']}개뿐이라 라벨 없이 기타만 둬야 합니다.")
            if len(labels) > MAX_LABELS:
                errors.append(f"{where}: 라벨이 {len(labels)}개입니다({MAX_LABELS}개 이하).")
            n = pe["sampled"]
            for lab in labels:
                lid = str(lab.get("id") or "")
                w = f"{where} {lid or '(id 없음)'}"
                if not lid:
                    errors.append(f"{w}: id가 없습니다.")
                if (tid, direction, lid) in seen_ids:
                    errors.append(f"{w}: id가 겹칩니다.")
                seen_ids.add((tid, direction, lid))
                for k in ("name_ko", "name_en", "include", "exclude"):
                    if not str(lab.get(k) or "").strip():
                        errors.append(f"{w}: {k}가 비었습니다.")
                ex = lab.get("examples") or []
                if len(ex) != 2:
                    errors.append(f"{w}: 대표 인용은 2개여야 합니다(지금 {len(ex)}개).")
                for x in ex:
                    rid = str((x or {}).get("review_id") if isinstance(x, dict) else x)
                    if rid not in sample_ids.get((tid, direction), set()):
                        errors.append(f"{w}: 대표 인용 {rid}가 이 주제와 방향의 표본에 없습니다.")
                cnt = lab.get("approx_count")
                if not isinstance(cnt, int):
                    errors.append(f"{w}: approx_count가 정수가 아닙니다.")
                elif n and cnt / n < MIN_SHARE:
                    errors.append(f"{w}: 어림 개수 {cnt}개가 표본 {n}개의 5% 미만이라 기타로 합쳐야 합니다.")
            entry["directions"][direction] = {"quotes": pe["quotes"], "sampled": n, "only_other": pe["only_other"],
                                              "labels": labels, "other_approx_count": d.get("other_approx_count"),
                                              "notes": d.get("notes")}
        topics.append(entry)
    status = "FAIL" if errors else "PASS"
    draft = {"made_at": now_iso(), "status": status, "version": "draft", "topics": topics, "errors": errors, "warnings": warns}
    import yaml
    (run / "07a_issues_draft.yaml").write_text(yaml.safe_dump(draft, allow_unicode=True, sort_keys=False, width=1000),
                                               encoding="utf-8")
    (run / "07a_issues_draft.md").write_text(render(draft), encoding="utf-8")
    print(f"세부 이슈 초안 합치기: {status}  (주제 {len(topics)}개, 라벨 "
          f"{sum(len(d['labels']) for t in topics for d in t['directions'].values())}개) → 07a_issues_draft.yaml, .md")
    for e in errors:
        print(f"  오류: {e}")
    return 1 if errors else 0


def render(draft):
    ko = {"negative": "부정 이슈(부정, 혼합 인용)", "positive": "긍정 이슈(긍정, 혼합 인용)"}
    lines = ["# 세부 이슈 목록 초안", "",
             f"상태: {draft['status']}. 주제마다 issue-labeler가 표본 인용(주제와 방향마다 최대 150개, ASIN과 별점 묶음을 고르게)을 읽고 제안한 목록입니다. "
             "어림 개수는 표본에서 센 값이라 리포트에 쓰지 않습니다. 전체 만족도는 리뷰 단위 총평이라 나누지 않습니다.", ""]
    for t in draft["topics"]:
        lines += [f"## {t['name_ko']} ({t['topic']})", ""]
        for direction, d in t["directions"].items():
            lines.append(f"### {ko[direction]}: 인용 {d['quotes']}개, 표본 {d['sampled']}개")
            lines.append("")
            if d["only_other"] or not d["labels"]:
                lines += ["인용이 20개 미만이거나 라벨이 없어 기타만 둡니다.", ""]
                continue
            lines += ["| id | 이름 | 영어 이름 | 포함 | 제외 | 대표 인용 | 어림 개수 |", "|---|---|---|---|---|---|---|"]
            for lab in d["labels"]:
                ex = "; ".join(f"\"{(x.get('quote') or '')[:60]}\" ({x.get('review_id')})" if isinstance(x, dict) else str(x)
                               for x in lab.get("examples") or [])
                cell = lambda v: str(v or "").replace("|", "/").replace("\n", " ")
                lines.append(f"| {cell(lab.get('id'))} | {cell(lab.get('name_ko'))} | {cell(lab.get('name_en'))} | "
                             f"{cell(lab.get('include'))} | {cell(lab.get('exclude'))} | {cell(ex)} | {lab.get('approx_count')} |")
            if d.get("other_approx_count") is not None:
                lines.append(f"| other | 기타 | Other | 위 라벨에 들지 않는 것 | - | - | {d['other_approx_count']} |")
            if d.get("notes"):
                lines += ["", f"메모: {d['notes']}"]
            lines.append("")
    if draft["errors"]:
        lines += ["## 검사 오류", ""] + [f"- {e}" for e in draft["errors"]]
    return "\n".join(lines) + "\n"


# ---------------------------------------------------------------- 승인 뒤: 라벨 붙이기, 개수, 감사, 안전 확인

def approve(run, approved_at, approved_by):
    import yaml
    d = load_yaml(run / "07a_issues_draft.yaml") or {}
    if d.get("status") != "PASS":
        die("07a_issues_draft.yaml이 PASS가 아닙니다. issues.py merge를 먼저 통과시켜 주세요.")
    d.update({"version": "approved", "approved_at": approved_at, "approved_by": approved_by})
    (run / "07a_issues_approved.yaml").write_text(yaml.safe_dump(d, allow_unicode=True, sort_keys=False, width=1000),
                                                  encoding="utf-8")
    n = sum(len(x["labels"]) for t in d["topics"] for x in t["directions"].values())
    print(f"승인본을 07a_issues_approved.yaml로 저장했습니다(라벨 {n}개, {approved_at}, {approved_by}).")
    return 0


def approved_labels(run):
    """{(주제, 방향): [라벨 id...]}와 {(주제, 방향, id): 라벨}"""
    d = load_yaml(run / "07a_issues_approved.yaml") or {}
    if d.get("version") != "approved":
        die("07a_issues_approved.yaml이 없거나 승인본이 아닙니다.")
    ids, labs = {}, {}
    for t in d["topics"]:
        for direction, x in t["directions"].items():
            ids[(t["topic"], direction)] = [l["id"] for l in x["labels"]]
            for l in x["labels"]:
                labs[(t["topic"], direction, l["id"])] = l
    return ids, labs


def label_units(run):
    """라벨을 붙일 단위: 전체 만족도와 중립을 뺀 태그 하나와 방향 하나. 혼합은 두 방향에 다 들어간다."""
    tags = [t for t in read_jsonl(run / "04_tags.jsonl") if t["topic"] != "off_category"]
    reviews = {r["review_id"]: r for r in load_csv_or_die(run / "02_reviews.csv", REVIEW_COLS)}
    units = []
    for t in tags:
        if t["topic"] in EXCLUDE or t["sentiment"] == "neutral":
            continue
        for direction, sents in DIRECTIONS.items():
            if t["sentiment"] in sents:
                r = reviews[t["review_id"]]
                units.append({"review_id": t["review_id"], "asin": r["asin"], "star": int(r["star"]),
                              "topic": t["topic"], "direction": direction, "sentiment": t["sentiment"], "quote": t["quote"]})
    return units


def label_plan(run, size):
    """라벨 묶음 계획. 기타만 있는 주제와 방향은 스크립트가 바로 기타로 채운다(07b_labels_auto.jsonl)."""
    ids, _ = approved_labels(run)
    units = label_units(run)
    outdir = run / "07b_label_input"
    outdir.mkdir(exist_ok=True)
    auto, batches = [], []
    groups = defaultdict(list)
    for u in units:
        if ids.get((u["topic"], u["direction"])):
            groups[(u["topic"], u["direction"])].append(u)
        else:
            auto.append({"review_id": u["review_id"], "topic": u["topic"], "direction": u["direction"], "labels": ["other"]})
    for (topic, direction), us in sorted(groups.items()):
        us.sort(key=lambda u: (u["asin"], u["review_id"]))
        for k in range(0, len(us), size):
            bid = f"{topic}_{direction}_{k // size + 1:02d}"
            write_jsonl(outdir / f"{bid}.jsonl", [{x: u[x] for x in ("review_id", "asin", "star", "sentiment", "quote")}
                                                 for u in us[k:k + size]])
            batches.append({"batch_id": bid, "topic": topic, "direction": direction, "items": len(us[k:k + size]),
                            "input": f"07b_label_input/{bid}.jsonl", "output": f"07b_labels_{bid}.jsonl"})
    write_jsonl(run / "07b_labels_auto.jsonl", auto)
    write_json(run / "07b_label_batches.json", {"made_at": now_iso(), "size": size, "units": len(units),
                                                "auto_other": len(auto), "batches": batches})
    print(f"라벨 묶음 {len(batches)}개(라벨 붙일 인용 {len(units) - len(auto)}개, 묶음 크기 최대 {size}), "
          f"기타만 있는 주제와 방향에서 스크립트가 기타로 채운 인용 {len(auto)}개 → 07b_label_batches.json")
    for b in batches:
        print(f"  {b['batch_id']}: {b['items']}개")
    return 0


def label_check(run):
    """묶음 출력 검사(목록에 있는 라벨인지, 빠진 인용, 라벨 2개 이하)와 합치기, 개수 세기."""
    ids, labs = approved_labels(run)
    plan = json.loads((run / "07b_label_batches.json").read_text(encoding="utf-8"))
    errors, merged, failed = [], read_jsonl(run / "07b_labels_auto.jsonl"), []
    for b in plan["batches"]:
        inp = read_jsonl(run / b["input"])
        out_path = run / b["output"]
        if not out_path.exists():
            errors.append(f"{b['batch_id']}: {b['output']}이(가) 없습니다.")
            failed.append(b["batch_id"])
            continue
        n_err = len(errors)
        out = read_jsonl(out_path, errors)
        allowed = set(ids[(b["topic"], b["direction"])]) | {"other"}
        need = Counter((u["review_id"], u["quote"]) for u in inp)
        got = Counter()
        bad = len(errors) > n_err      # JSON으로 읽지 못한 줄이 있으면 묶음 실패
        for n, o in enumerate(out, 1):
            labels = o.get("labels") or []
            key = (o.get("review_id"), o.get("quote"))
            if key not in need:
                errors.append(f"{b['batch_id']} {n}번째: 입력에 없는 인용 {key[0]}")
                bad = True
                continue
            got[key] += 1
            if not labels or len(labels) > 2 or any(l not in allowed for l in labels) or len(set(labels)) != len(labels):
                errors.append(f"{b['batch_id']} {n}번째 {key[0]}: 라벨 {labels}(이 주제와 방향의 승인 라벨이나 other, 1~2개)")
                bad = True
            if "other" in labels and len(labels) > 1:
                errors.append(f"{b['batch_id']} {n}번째 {key[0]}: other는 다른 라벨과 함께 쓰지 않습니다.")
                bad = True
            merged.append({"review_id": key[0], "topic": b["topic"], "direction": b["direction"], "labels": labels})
        missing = need - got
        if missing:
            errors.append(f"{b['batch_id']}: 라벨이 없는 인용 {sum(missing.values())}개(예: {next(iter(missing))[0]})")
            bad = True
        if bad:
            failed.append(b["batch_id"])
    status = "FAIL" if errors else "PASS"
    result = {"checked_at": now_iso(), "status": status, "failed_batches": failed, "errors": errors}
    if not errors:
        write_jsonl(run / "07b_issue_labels.jsonl", merged)
        result["counts"] = count_labels(run, merged, ids, labs)
    write_json(run / "07b_issue_check.json", result)
    print(f"라벨 검사: {status}  (묶음 {len(plan['batches'])}개, 실패 {len(failed)}개)")
    for e in errors[:30]:
        print(f"  오류: {e}")
    return 1 if errors else 0


def review_weights(run):
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from pipeline_io import DIST_COLS, load_config
    from weight import build_weights
    from pipeline_io import split_tags
    reviews = load_csv_or_die(run / "02_reviews.csv", REVIEW_COLS)
    tp = run / "04_tags.jsonl"
    if tp.exists():                      # off_category 리뷰는 가중치에서도 뺀다(weight.py와 같게)
        reviews, _, _ = split_tags(reviews, read_jsonl(tp))
    dist = {r["asin"]: r for r in load_csv_or_die(run / "02_star_distribution.csv", DIST_COLS)}
    weight, _, _, _ = build_weights(reviews, dist, load_config())
    return reviews, weight


def count_labels(run, merged, ids, labs):
    """라벨마다 리뷰 수(리뷰 하나는 라벨마다 한 번), 가중 비율(그 라벨이 붙은 리뷰의 가중치 합 / 전체 리뷰 가중치 합),
    ASIN별 리뷰 수. 주제와 방향마다 기타 비율. 향과 신뢰의 향 차이 라벨 겹침."""
    reviews, weight = review_weights(run)
    asin_of = {r["review_id"]: r["asin"] for r in reviews}
    total_w = sum(weight.values())
    by_label = defaultdict(set)
    units = Counter()
    other_units = Counter()
    for m in merged:
        units[(m["topic"], m["direction"])] += 1
        if m["labels"] == ["other"]:
            other_units[(m["topic"], m["direction"])] += 1
        for l in m["labels"]:
            by_label[(m["topic"], m["direction"], l)].add(m["review_id"])
    out = {"total_reviews": len(reviews), "topics": {}}
    for (topic, direction), lids in sorted(ids.items()):
        key = f"{topic}.{direction}"
        rows = []
        for lid in lids + ["other"]:
            rids = by_label.get((topic, direction, lid), set())
            lab = labs.get((topic, direction, lid), {"name_ko": "기타", "name_en": "Other"})
            rows.append({"id": lid, "name_ko": lab["name_ko"], "name_en": lab["name_en"], "reviews": len(rids),
                         "weighted_pct": pct(sum(weight[r] for r in rids), total_w),
                         "by_asin": dict(sorted(Counter(asin_of[r] for r in rids).items()))})
        rows.sort(key=lambda r: (r["id"] == "other", -r["reviews"], r["id"]))
        n = units[(topic, direction)]
        out["topics"][key] = {"topic": topic, "direction": direction, "units": n,
                              "other_units": other_units[(topic, direction)],
                              "other_pct": pct(other_units[(topic, direction)], n), "labels": rows}
    # 겹침: 향 부정의 '원래 알던 향과 다름'과 신뢰 부정의 '정품이나 늘 쓰던 것과 향이 다름'(승인 목록의 id로 찾음)
    from pipeline_io import category_conf
    ov = (category_conf(run).get("issues") or {}).get("overlap")
    (ta, a), (tb, b) = ov if ov else ((None, None), (None, None))
    if ov and (ta, "negative", a) in labs and (tb, "negative", b) in labs:
        both = by_label.get((ta, "negative", a), set()) & by_label.get((tb, "negative", b), set())
        out["overlap"] = {"labels": [f"{ta}.negative.{a}", f"{tb}.negative.{b}"],
                          "names": [labs[(ta, "negative", a)]["name_ko"], labs[(tb, "negative", b)]["name_ko"]],
                          "reviews": len(both),
                          "weighted_pct": pct(sum(weight[r] for r in both), total_w), "review_ids": sorted(both)}
    write_json(run / "07b_issue_counts.json", out)
    return {"labels": sum(len(v["labels"]) for v in out["topics"].values()), "overlap": out.get("overlap", {}).get("reviews")}


def audit_sample(run, n):
    """라벨 감사 표본: (ASIN, 주제) 칸을 돌아가며 n개. 기타도 포함. 시드 고정."""
    merged = read_jsonl(run / "07b_issue_labels.jsonl")
    reviews = {r["review_id"]: r for r in load_csv_or_die(run / "02_reviews.csv", REVIEW_COLS)}
    tags = {(t["review_id"], t["topic"]): t for t in read_jsonl(run / "04_tags.jsonl")}
    rng = seeded(run, "issue_audit")
    cells = defaultdict(list)
    for m in sorted(merged, key=lambda m: (m["review_id"], m["topic"], m["direction"])):
        cells[(reviews[m["review_id"]]["asin"], m["topic"])].append(m)
    for v in cells.values():
        rng.shuffle(v)
    keys = sorted(cells)
    out = []
    while len(out) < n and any(cells[k] for k in keys):
        for k in keys:
            if len(out) >= n:
                break
            if cells[k]:
                m = cells[k].pop()
                t = tags[(m["review_id"], m["topic"])]
                out.append({**m, "asin": reviews[m["review_id"]]["asin"], "sentiment": t["sentiment"], "quote": t["quote"]})
    write_jsonl(run / "07b_issue_audit_sample.jsonl", out)
    print(f"라벨 감사 표본 {len(out)}개 → 07b_issue_audit_sample.jsonl")
    return 0


def audit(run, max_fail):
    data = load_yaml(run / "07b_issue_audit.yaml") or {}
    a = data.get("audit") if isinstance(data, dict) else None
    if not isinstance(a, dict):
        die("07b_issue_audit.yaml 맨 위에 audit: 항목이 없습니다.")
    sample = read_jsonl(run / "07b_issue_audit_sample.jsonl")
    keys = {(s["review_id"], s["topic"], s["direction"]) for s in sample}
    fails, warns = [], []
    for f in a.get("findings") or []:
        k = (str(f.get("review_id")), str(f.get("topic")), str(f.get("direction")))
        if str(f.get("status", "")).upper() != "FAIL":
            continue
        if k not in keys:
            warns.append(f"표본에 없는 항목 {k}")
            continue
        fails.append(k)
    rate = len(fails) / len(sample) if sample else 0.0
    checked = a.get("checked")
    if not sample:
        status = "EMPTY"
    elif checked != len(sample):
        status = "INCOMPLETE"       # 감사자가 표본을 다 보지 않았으면 PASS로 넘기지 않음
    else:
        status = "PASS" if rate <= max_fail else "FAIL"
    write_json(run / "07b_issue_audit_summary.json", {"checked_at": now_iso(), "status": status, "sample": len(sample),
                                                      "auditor_checked": checked,
                                                      "fail": len(fails), "fail_rate": round(rate, 3), "max_fail_rate": max_fail,
                                                      "warnings": warns})
    print(f"라벨 감사 집계: {status}  (표본 {len(sample)}개 중 FAIL {len(fails)}개 = {rate:.1%}, 기준 {max_fail:.0%} 이하)")
    return 0 if status == "PASS" else 1


def safety_input(run):
    """안전 주제 인용 전부(라벨 없음)를 판정용 표로. 인용과 리뷰 원문을 줄이지 않는다."""
    tags = [t for t in read_jsonl(run / "04_tags.jsonl") if t["topic"] == "safety"]
    reviews = {r["review_id"]: r for r in load_csv_or_die(run / "02_reviews.csv", REVIEW_COLS)}
    rows = [{"review_id": t["review_id"], "asin": reviews[t["review_id"]]["asin"], "star": int(reviews[t["review_id"]]["star"]),
             "sentiment": t["sentiment"], "quote": t["quote"], "title": reviews[t["review_id"]]["title"],
             "body": reviews[t["review_id"]]["body"]} for t in tags]
    rows.sort(key=lambda r: (r["sentiment"] != "negative", r["asin"], r["review_id"]))
    write_jsonl(run / "07c_safety_input.jsonl", rows)
    print(f"안전 인용 {len(rows)}개(부정 {sum(r['sentiment'] == 'negative' for r in rows)}, "
          f"긍정 {sum(r['sentiment'] == 'positive' for r in rows)}) → 07c_safety_input.jsonl")
    return 0


SYMPTOMS = ("두통", "메스꺼움", "호흡", "어지럼", "피부", "알레르기 언급")   # 안전 판정의 증상 분류(symptom_type), 이 순서로 적는다


def safety_render(run):
    """evidence-auditor 판정(07c_safety_verdicts.yaml)과 원문을 합쳐 07c_safety_check.md와 07c_safety_summary.json.
    몸 증상이 있으면 symptom_type(SYMPTOMS 중 하나)이 있어야 하고, 증상마다 리뷰 수와 가중 비율을 센다."""
    rows = read_jsonl(run / "07c_safety_input.jsonl")
    data = load_yaml(run / "07c_safety_verdicts.yaml") or {}
    verdicts = {str(v.get("review_id")): v for v in ((data.get("audit") or {}).get("verdicts") or [])}
    missing = [r["review_id"] for r in rows if r["review_id"] not in verdicts]
    if missing:
        die(f"판정이 없는 안전 인용: {', '.join(missing)}")
    is_sym = lambda v: str(v.get("verdict")).lower() in ("symptom", "몸 증상 있음", "yes", "true")
    bad = [r["review_id"] for r in rows if is_sym(verdicts[r["review_id"]])
           and verdicts[r["review_id"]].get("symptom_type") not in SYMPTOMS]
    if bad:
        die(f"몸 증상인데 symptom_type({', '.join(SYMPTOMS)})이 없거나 목록 밖: {', '.join(bad)}")
    reviews, weight = review_weights(run)
    total_w = sum(weight.values())
    cell = lambda s: str(s or "").replace("|", "/").replace("\n", " ")
    lines = ["# 안전 인용 확인", "", "안전 주제로 태깅된 인용 전부(라벨 없음). 상위 모델(evidence-auditor)이 몸 증상(피부 반응, 두통, 알레르기, 호흡 등)이 "
             "있는지 판정했고, 몸 증상은 증상별로 나눴습니다. 태그는 고치지 않았습니다.", "",
             "| review_id | ASIN | 별점 | 감성 | 인용 원문 | 리뷰 원문(제목 / 본문) | 판정 | 증상 | 이유 |", "|---|---|---|---|---|---|---|---|---|"]
    summary = Counter()
    by_sym = defaultdict(set)
    for r in rows:
        v = verdicts[r["review_id"]]
        sym = is_sym(v)
        summary[(r["sentiment"], sym)] += 1
        if sym and r["sentiment"] == "negative":
            by_sym[v["symptom_type"]].add(r["review_id"])
        lines.append(f"| {r['review_id']} | {r['asin']} | {r['star']}★ | {r['sentiment']} | {cell(r['quote'])} | "
                     f"{cell(r['title'])} / {cell(r['body'])} | {'몸 증상 있음' if sym else '없음'} | "
                     f"{v.get('symptom_type', '-') if sym else '-'} | {cell(v.get('reason'))} |")
    out = {"negative_symptom": summary[("negative", True)], "negative_no_symptom": summary[("negative", False)],
           "positive_symptom": summary[("positive", True)], "positive_no_symptom": summary[("positive", False)],
           "other_sentiment": sum(n for (s, _), n in summary.items() if s not in ("negative", "positive")),
           "by_symptom": [{"name": k, "reviews": len(by_sym[k]), "weighted_pct": pct(sum(weight[r] for r in by_sym[k]), total_w)}
                          for k in SYMPTOMS if by_sym[k]]}
    neg = out["negative_symptom"] + out["negative_no_symptom"]
    parts = [f"{s['name']} {s['reviews']}개(가중 {s['weighted_pct']}%)" for s in out["by_symptom"]]
    if out["negative_no_symptom"]:
        parts.append(f"몸 증상 없음 {out['negative_no_symptom']}개(향의 세기 등)")
    out["negative_text"] = f"안전 부정 리뷰 {neg}개: " + ", ".join(parts) if neg else ""
    lines += ["", f"부정 {neg}개 중 몸 증상 있음 {out['negative_symptom']}개, 없음 {out['negative_no_symptom']}개. "
                  f"긍정 {out['positive_symptom'] + out['positive_no_symptom']}개 중 몸 증상 있음 {out['positive_symptom']}개, "
                  f"없음 {out['positive_no_symptom']}개.", "", f"증상별(부정): {out['negative_text']}. "
                  "가중 비율은 그 증상 리뷰의 가중치 합 ÷ 전체 리뷰 가중치 합. 알레르기 언급은 본인 반응을 직접 묘사하지 않은 리뷰."]
    (run / "07c_safety_check.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    write_json(run / "07c_safety_summary.json", out)
    print(f"안전 확인표: {out['negative_text'] or '안전 부정 없음'}. 긍정 몸 증상 {out['positive_symptom']}개, "
          f"없음 {out['positive_no_symptom']}개 → 07c_safety_check.md")
    return 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("mode", choices=["sample", "merge", "approve", "label-plan", "label-check", "audit-sample", "audit",
                                     "safety-input", "safety-render"])
    ap.add_argument("run", nargs="?")
    ap.add_argument("--per", type=int, default=150)
    ap.add_argument("--min", type=int, default=20)
    ap.add_argument("--size", type=int, default=180, help="label-plan 묶음 크기")
    ap.add_argument("--n", type=int, default=150, help="audit-sample 표본 수")
    ap.add_argument("--max-fail", type=float, default=0.05)
    ap.add_argument("--approved-at", default=None)
    ap.add_argument("--approved-by", default=None)
    args = ap.parse_args()
    run = resolve_run(args.run)
    if args.mode == "approve":
        if not args.approved_at or not args.approved_by:
            die("--approved-at과 --approved-by가 필요합니다.")
        sys.exit(approve(run, args.approved_at, args.approved_by))
    fn = {"sample": lambda: sample(run, args.per, args.min), "merge": lambda: merge(run),
          "label-plan": lambda: label_plan(run, args.size), "label-check": lambda: label_check(run),
          "audit-sample": lambda: audit_sample(run, args.n), "audit": lambda: audit(run, args.max_fail),
          "safety-input": lambda: safety_input(run), "safety-render": lambda: safety_render(run)}[args.mode]
    sys.exit(fn())


if __name__ == "__main__":
    main()
