"""작업자별 입력 파일 만들기(docs/multi_agent_design_v2.md 흐름 2, 3). 모델을 부르지 않는다.

에이전트는 이 파일 하나만 읽는다. 전체 스키마, 02_reviews.csv 전체, CLAUDE.md 상세는 읽지 않는다.
작업 파일에 넣는 것: 목적 한 줄, 그 작업에 필요한 승인 기준의 원문 필드(요약하지 않고 YAML 값 그대로 복사), 맡은 묶음마다
대상 리뷰 원문과 출력 경로, 통과해야 할 검사, 상한, 기준과 입력의 해시.

사용:
  python scripts/stage_packet.py detail [회차] --items a,b [--batches-file 14_rejudge_batches.json]
    설계 정보 추출(다시 판정 포함). 기준은 13_detail_schema_approved.yaml에서 --items 항목만.
  python scripts/stage_packet.py tags [회차] [--batches-file 04_batches.json]
    주제 태깅. 기준은 03_schema_approved.yaml의 주제 전부(태깅은 주제를 다 알아야 함).
  python scripts/stage_packet.py labels [회차] [--batches-file 07b_label_batches.json]
    세부 이슈 라벨. 기준은 07a_issues_approved.yaml에서 그 묶음의 주제와 방향 라벨만.
  공통: 묶음을 config/stages.yaml 상한(작업자당 묶음, 리뷰)에 맞춰 작업자에게 나누고, 작업자마다
  packets/<종류>_w<번호>.md를 쓴다. 요약은 packets/<종류>_plan.json(작업자, 묶음, 글자 수, 해시).
"""
import argparse
import csv
import hashlib
import json
import sys
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))
from pipeline_io import die, load_yaml, now_iso, read_jsonl, resolve_run, write_json  # noqa: E402
from stage_plan import assign, load_conf  # noqa: E402

for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass

# 판정에 쓰는 필드만 원문 그대로(예시 examples와 인용 필수 여부 포함). 출처나 쓰임 설명(kind, sample_count, overlap, new_info, guide_use)은 뺀다.
DETAIL_FIELDS = ("id", "name_ko", "format", "unit", "allowed_values", "definition", "fill_rule", "extra", "quote_required", "examples")
CHECKS = {"detail": "python scripts/detail.py extract-check(다시 판정이면 rejudge-merge) <회차>",
          "tags": "python scripts/audit_quotes.py tags <회차> --model sonnet",
          "labels": "python scripts/issues.py label-check <회차>"}
GOALS = {"detail": "맡은 묶음의 리뷰마다 아래 기준 항목의 값과 원문 인용을 뽑는다. 기준에 없는 항목은 쓰지 않는다(다른 항목은 경계를 가르는 데만 본다).",
         "tags": "맡은 묶음의 리뷰마다 아래 주제 기준으로 주제, 감성, 원문 인용을 단다.",
         "labels": "맡은 묶음의 인용마다 아래 라벨 기준으로 세부 이슈 라벨을 붙인다."}


# 묶음마다 지킬 순서(카테고리와 무관). 지금 방식에서 에이전트가 묶음 하나씩 읽던 것과 같게 하고, 빠뜨림을 스스로 한 번 더 본다.
STEPS = ["묶음마다 차례로: (1) 그 묶음의 입력 파일을 읽는다(한 번에 그 묶음만). (2) 리뷰마다 기준 항목을 하나씩 보고, 항목의 fill_rule이 말하는 "
         "채우는 조건에 맞는 말이 있으면 값마다 한 줄을 쓴다(값이 여럿이면 모두). 조건에 맞는 말이 없으면 비운다. (3) 묶음 출력 파일을 쓴다. "
         "(4) 쓰고 나서 그 묶음 리뷰를 한 번 더 훑어, 채우는 조건에 맞는데 빠뜨린 값이나 여럿인데 하나만 쓴 값이 있으면 더한다. 다음 묶음으로 간다."]


RULES = Path(__file__).resolve().parent.parent / "config" / "detail_rules.yaml"


def common_rules(items, path=RULES):
    """품목에 묶이지 않는 공통 경계 규칙(config/detail_rules.yaml) 가운데 맡은 항목이 걸린 것만, 원문 그대로."""
    d = load_yaml(Path(path)) or {}
    rules = [{"id": r["id"], "rule": r["rule"]} for r in d.get("rules") or [] if set(r.get("items") or []) & set(items)]
    notes = [n for n in d.get("value_notes") or [] if n.get("item") in items]
    return {"rules": rules, "value_notes": notes} if rules or notes else None


def neighbors(run, items):
    """판정 경계를 가르는 데 쓰는 다른 항목의 이름과 정의(원문 그대로). 값을 뽑지는 않는다."""
    d = load_yaml(run / "13_detail_schema_approved.yaml") or {}
    return [{k: i[k] for k in ("id", "name_ko", "definition") if k in i} for i in d.get("items") or [] if i["id"] not in items]


def dump(obj):
    return yaml.safe_dump(obj, allow_unicode=True, sort_keys=False, width=1000).rstrip()


def h(s):
    return hashlib.sha256(s.encode("utf-8")).hexdigest()[:16]


def file_hash(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()[:16]


def criteria(run, kind, items=None, batch=None):
    """승인 기준에서 필요한 필드만 원문 그대로(값을 고치지 않고) 꺼낸다."""
    if kind == "detail":
        d = load_yaml(run / "13_detail_schema_approved.yaml") or {}
        by = {i["id"]: i for i in d.get("items") or []}
        miss = [x for x in items if x not in by]
        if miss:
            die(f"승인 항목이 아님: {miss}")
        return [{k: by[x][k] for k in DETAIL_FIELDS if k in by[x]} for x in items]
    if kind == "tags":
        return (load_yaml(run / "03_schema_approved.yaml") or {}).get("topics") or []
    if kind == "labels":
        d = load_yaml(run / "07a_issues_approved.yaml") or {}
        tp = next((t for t in d.get("topics") or [] if t["topic"] == batch["topic"]), None)
        if tp is None:
            die(f"승인 목록에 주제가 없음: {batch['topic']}")
        return {"topic": tp["topic"], "name_ko": tp.get("name_ko"), "direction": batch["direction"],
                "labels": (tp["directions"].get(batch["direction"]) or {}).get("labels") or []}
    die(f"모르는 종류: {kind}")


def batch_rows(run, kind, b, reviews):
    """묶음의 대상(리뷰 원문 또는 인용)"""
    src = run / b["input"]
    rows = read_jsonl(src)
    if kind in ("detail", "tags") and rows and "body" not in rows[0]:
        rows = [{"review_id": r["review_id"], "title": reviews[r["review_id"]]["title"], "body": reviews[r["review_id"]]["body"]} for r in rows]
    return rows


def build(run, kind, items, batches_file, max_batches=None, max_reviews=None, only=None):
    conf = load_conf()
    # 실험용 한 번 덮어쓰기(기본 상한 config/stages.yaml은 바꾸지 않음). 기본값보다 크게는 못 한다.
    if max_batches:
        conf["limits"]["worker_max_batches"] = min(max_batches, conf["limits"]["worker_max_batches"])
    if max_reviews:
        conf["limits"]["worker_max_reviews"] = min(max_reviews, conf["limits"]["worker_max_reviews"])
    bf = run / batches_file
    if not bf.exists():
        die(f"{batches_file}이(가) 없습니다.")
    plan_ = json.loads(bf.read_text(encoding="utf-8"))
    batches = plan_["batches"]
    if only:             # 기계 검사에서 실패한 묶음만 다시(작업 파일과 요약 이름에 retry가 붙음)
        unknown = sorted(set(only) - {b["batch_id"] for b in batches})
        if unknown:      # 오타 id를 조용히 버리지 않는다
            die(f"묶음 계획에 없는 묶음: {unknown}")
        batches = [b for b in batches if b["batch_id"] in only]
    elif kind == "tags":  # 시험 태깅 묶음(gold 포함)은 이미 따로 했으므로 빼고, sonnet 묶음만
        pilot = set(plan_.get("pilot_batches") or [])
        batches = [b for b in batches if b["batch_id"] not in pilot and "sonnet" in (b.get("models") or ["sonnet"])]
        if not batches:
            die("시험 태깅 묶음을 빼면 남은 sonnet 묶음이 없음")
    if kind == "tags":
        for b in batches:
            b.setdefault("input", None)
    reviews = {}
    with open(run / "02_reviews.csv", encoding="utf-8-sig", newline="") as f:
        for r in csv.DictReader(f):
            reviews[r["review_id"]] = r
    if kind == "tags":       # 04_batches.json은 리뷰 id 목록만 있다
        for b in batches:
            b["_rows"] = [{"review_id": x, "title": reviews[x]["title"], "body": reviews[x]["body"]} for x in b["review_ids"]]
            b["output"] = f"04_tags_sonnet_{b['batch_id']}.jsonl"
    else:
        for b in batches:
            b["_rows"] = batch_rows(run, kind, b, reviews)
    n_reviews = sum(len(b["_rows"]) for b in batches)
    a = assign(conf, len(batches), n_reviews, [len(b["_rows"]) for b in batches])   # 실제 묶음 크기로 배정
    outdir = run / "packets"
    outdir.mkdir(exist_ok=True)
    lim = conf["limits"]
    summary = {"made_at": now_iso(), "kind": kind, "items": items, "batches_file": batches_file, "workers": []}
    shared_crit = None if kind == "labels" else dump(criteria(run, kind, items))
    for wi, grp in enumerate(a["groups"], 1):
        mine = [batches[i] for i in grp]
        parts = [f"# 작업 파일: {kind} 작업자 {wi}", "",
                 f"목적: {GOALS[kind]}", "",
                 "이 파일과 여기 적힌 묶음 입력 파일만 읽는다. 전체 스키마, 02_reviews.csv, CLAUDE.md, 다른 작업자의 묶음은 읽지 않는다. 묶음을 아래 순서대로 처리한다.", "",
                 f"상한: 이 작업자는 묶음 {len(mine)}개(최대 {lim['worker_max_batches']}개, 리뷰 최대 {lim['worker_max_reviews']}개). "
                 f"재시도는 묶음마다 {lim['retry_per_batch']}번까지.", "",
                 f"통과해야 할 검사: `{CHECKS[kind]}`", ""]
        crit_texts = []
        if shared_crit is not None:
            parts += ["## 기준(승인 파일의 원문 필드 그대로)", "", "```yaml", shared_crit, "```", ""]
            crit_texts.append(shared_crit)
        if kind == "detail" and common_rules(items):
            cr = dump(common_rules(items))
            parts += ["## 공통 경계 규칙(config/detail_rules.yaml 원문 그대로, 위 기준의 fill_rule이나 값 설명과 다르면 이 규칙이 먼저)", "",
                      "```yaml", cr, "```", ""]
            crit_texts.append(cr)
        if kind == "detail":
            nb = dump(neighbors(run, items))
            parts += ["## 다른 항목(경계를 가르는 데만 본다, 값은 쓰지 않음, 승인 파일 원문 그대로)", "", "```yaml", nb, "```", ""]
            crit_texts.append(nb)
        parts += ["## 순서", ""] + [f"- {x}" for x in STEPS] + [""]
        for b in mine:
            parts += [f"## 묶음 {b['batch_id']}", "", f"출력: runs/{run.name}/{b['output']}", ""]
            if kind == "labels":
                ct = dump(criteria(run, kind, batch=b))
                crit_texts.append(ct)
                parts += ["### 기준(이 묶음의 주제와 방향 라벨, 원문 그대로)", "", "```yaml", ct, "```", ""]
            if b.get("input"):       # 입력 파일이 있으면 경로만 적고, 그 묶음 차례에 그 파일을 읽게 한다(작업 파일을 나눠 읽지 않게)
                # 입력 파일 내용 해시를 적어 둔다(작업 파일 해시가 입력 내용까지 덮게)
                parts += [f"입력: runs/{run.name}/{b['input']}(리뷰 {len(b['_rows'])}개, sha256 {file_hash(run / b['input'])})", ""]
            else:
                parts += ["### 대상", "", "```json"] + [json.dumps(r, ensure_ascii=False) for r in b["_rows"]] + ["```", ""]
        text = "\n".join(parts) + "\n"
        name = f"{kind}_{'retry_' if only else ''}w{wi}.md"
        (outdir / name).write_text(text, encoding="utf-8")
        crit_chars = sum(len(c) for c in crit_texts)
        summary["workers"].append({"worker": wi, "file": f"packets/{name}", "batches": [b["batch_id"] for b in mine],
                                   "input_hashes": {b["batch_id"]: file_hash(run / b["input"]) for b in mine if b.get("input")},
                                   "reviews": sum(len(b["_rows"]) for b in mine), "chars": len(text), "criteria_chars": crit_chars,
                                   "criteria_hash": h("".join(crit_texts)), "packet_hash": h(text)})
    summary["assign"] = {k: v for k, v in a.items() if k != "groups"}
    write_json(outdir / f"{kind}_{'retry_' if only else ''}plan.json", summary)
    for w in summary["workers"]:
        print(f"  작업자 {w['worker']}: 묶음 {', '.join(w['batches'])}, 리뷰 {w['reviews']}개, 파일 {w['chars']:,}자(기준 {w['criteria_chars']:,}자)")
    return summary


def main():
    ap = argparse.ArgumentParser(description="작업자별 입력 파일")
    ap.add_argument("kind", choices=["detail", "tags", "labels"])
    ap.add_argument("run", nargs="?")
    ap.add_argument("--items", default="")
    ap.add_argument("--batches-file", default=None)
    ap.add_argument("--max-batches", type=int, default=None, help="실험용: 작업자당 묶음 상한을 이번만 줄임(기본보다 크게는 못 함)")
    ap.add_argument("--max-reviews", type=int, default=None, help="실험용: 작업자당 리뷰 상한을 이번만 줄임")
    ap.add_argument("--only", default="", help="기계 검사에서 실패한 묶음만 다시(쉼표로 batch_id)")
    a = ap.parse_args()
    run = resolve_run(a.run)
    bf = a.batches_file or {"detail": "14_detail_batches.json", "tags": "04_batches.json", "labels": "07b_label_batches.json"}[a.kind]
    items = [x.strip() for x in a.items.split(",") if x.strip()]
    if a.kind == "detail" and not items:
        die("detail에는 --items가 필요합니다.")
    build(run, a.kind, items, bf, a.max_batches, a.max_reviews, [x for x in a.only.split(",") if x])
    sys.exit(0)


if __name__ == "__main__":
    main()
