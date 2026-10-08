"""다시 할 단계 고르기와 상한 검사(docs/multi_agent_design_v2.md 흐름 1, 3, 7). 모델을 부르지 않는다.

단계 정의는 config/stages.yaml(입력, 출력, 뒤 단계, 상한).

사용:
  python scripts/stage_plan.py plan [회차] [--json]
    단계마다 입력 파일 해시(input_hash)와 지시문과 코드 해시(code_hash, 단계의 code: 목록)를 state.json에 남은 해시
    (timing_report.py mark end가 적음)와 비교하고, 출력 파일(묶음 계획이 정한 묶음 출력 하나하나까지)이 다 있는지 본다.
    해시가 없거나 다르거나 출력이 빠졌으면 그 단계와, 뒤 단계(after)를 따라 이어지는 단계 모두를 다시 할 단계로 고른다.
    같으면 건너뛰고 그 단계의 문서는 다시 읽지 않는다. 결과를 찍기만 하고 아무것도 돌리지 않는다(마른 실행).
  python scripts/stage_plan.py baseline [회차] [--with-code]
    출력 파일이 모두 있는 단계마다 지금 입력 해시를 state.json에 기준으로 적는다(이 방식을 처음 쓸 때 한 번).
    --with-code는 지금 지시문과 코드 해시도 기준으로 적는다(지금 출력이 지금 지시문으로 만든 것일 때만).
  python scripts/stage_plan.py check [--config config/stages.yaml]
    단계 정의 검사: 두 단계가 같은 출력 파일을 쓰는지(겹침), 뒤 단계가 정의에 있는지, 상한 값이 있는지.
  python scripts/stage_plan.py assign --batches N [--reviews M] [--sizes 50,50,26]
    묶음을 상한(작업자당 묶음, 리뷰)에 맞춰 작업자에게 나누고, 호출 수와 동시 실행 수를 찍는다.
    묶음 크기(--sizes, 없으면 M을 N으로 고르게 나눈 값)를 차례로 더해 상한을 넘기 직전에 다음 작업자로 넘긴다.
    묶음 하나가 리뷰 상한보다 크면 멈춘다(묶음을 나눠야 함).
"""
import argparse
import fnmatch
import glob
import hashlib
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from pipeline_io import ROOT, die, load_yaml, now_iso, resolve_run, write_json  # noqa: E402

for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass

CONF = ROOT / "config" / "stages.yaml"
LIMIT_KEYS = ("bulk_concurrency", "tagging_concurrency", "worker_max_batches", "worker_max_reviews", "retry_per_batch", "retry_per_stage",
              "top_writers", "top_auditors", "review_lenses")


def load_conf(path=CONF):
    c = load_yaml(Path(path)) or {}
    if not c.get("stages"):
        die(f"{path}에 stages가 없습니다.")
    return c


def expand(run, pattern):
    """입력 하나(경로나 글롭)를 실제 파일 목록으로. config:로 시작하면 저장소 맨 위 기준."""
    base, pat = (ROOT, pattern[len("config:"):]) if pattern.startswith("config:") else (run, pattern)
    return sorted(Path(p) for p in glob.glob(str(base / pat)) if Path(p).is_file())


def input_hash(run, stage):
    """입력 파일들의 경로와 내용으로 만든 해시(파일이 없으면 'missing'으로 섞음)"""
    h = hashlib.sha256()
    for pat in stage.get("inputs") or []:
        files = expand(run, pat)
        if not files:
            h.update(f"{pat}:missing".encode("utf-8"))
        for f in files:
            h.update(str(f.relative_to(ROOT if pat.startswith("config:") else run)).replace("\\", "/").encode("utf-8"))
            h.update(f.read_bytes())
    return h.hexdigest()[:16]


def input_files(run, stage):
    """단계 입력 가운데 지금 있는 파일마다 내용 해시 {상대 경로: 해시}. 단계가 스스로 만드는 입력(예: market/raw)은 시작 때 없으므로 빠진다."""
    out = {}
    for pat in stage.get("inputs") or []:
        base = ROOT if pat.startswith("config:") else run
        for f in expand(run, pat):
            out[str(f.relative_to(base)).replace("\\", "/")] = hashlib.sha256(f.read_bytes()).hexdigest()[:16]
    return out


def code_hash(stage):
    """단계의 지시문과 코드(code: 목록, 저장소 맨 위 기준 경로)로 만든 해시. 목록이 없으면 None"""
    if not stage.get("code"):
        return None
    h = hashlib.sha256()
    for rel in stage["code"]:
        f = ROOT / rel
        h.update(rel.encode("utf-8"))
        h.update(f.read_bytes() if f.is_file() else b"missing")
    return h.hexdigest()[:16]


def expected_outputs(run, stage):
    """단계가 남겨야 할 출력 가운데 없는 것. 출력 글롭마다 파일 하나 이상, expect가 있으면 묶음 계획의 묶음 출력 하나하나."""
    missing = [o for o in stage.get("outputs") or [] if not expand(run, o)]
    ex = stage.get("expect")
    if ex:
        bf = run / ex["batches"]
        if not bf.exists():
            return missing + [ex["batches"]]
        for b in json.loads(bf.read_text(encoding="utf-8")).get("batches") or []:
            if ex.get("output"):
                names = [ex["output"].format(model=m, batch_id=b["batch_id"]) for m in b.get("models") or []]
            else:
                names = [b["output"]]
            missing += [n for n in names if not (run / n).is_file()]
    return missing


def stage_by_id(conf):
    return {s["id"]: s for s in conf["stages"]}


def downstream(conf, ids):
    """ids와 그 뒤 단계(after)를 따라 이어지는 단계 전부"""
    S = stage_by_id(conf)
    out, todo = set(), list(ids)
    while todo:
        x = todo.pop()
        if x in out:
            continue
        out.add(x)
        todo += S.get(x, {}).get("after") or []
    return out


def plan(run, conf, as_json=False):
    state = json.loads((run / "state.json").read_text(encoding="utf-8")) if (run / "state.json").exists() else {"steps": {}}
    steps = state.get("steps") or {}
    changed, reasons = [], {}
    for s in conf["stages"]:
        rec = steps.get(s["id"]) or {}
        now, code = input_hash(run, s), code_hash(s)
        why = None
        if rec.get("status") != "done":
            why = f"상태가 {rec.get('status') or '기록 없음'}"
        elif not rec.get("input_hash"):
            why = "기준 해시 없음(stage_plan.py baseline 먼저)"
        elif rec["input_hash"] != now:
            why = f"입력이 바뀜({rec['input_hash']} -> {now})"
        elif code and not rec.get("code_hash"):
            why = "지시문과 코드의 기준 해시 없음(지금 출력을 어느 지시문으로 만들었는지 모름)"
        elif code and rec["code_hash"] != code:
            why = f"지시문이나 코드가 바뀜({rec['code_hash']} -> {code})"
        else:
            miss = expected_outputs(run, s)
            if miss:
                why = f"출력이 없음({len(miss)}개, 예: {miss[0]})"
        if why:
            reasons[s["id"]] = why
            changed.append(s["id"])
    redo = downstream(conf, changed)
    order = [s["id"] for s in conf["stages"] if s["id"] in redo]
    out = {"planned_at": now_iso(), "run": run.name, "redo": order, "changed": changed, "reasons": reasons,
           "skip": [s["id"] for s in conf["stages"] if s["id"] not in redo]}
    if as_json:
        print(json.dumps(out, ensure_ascii=False, indent=2))
    else:
        print(f"다시 할 단계 {len(order)}개, 건너뛸 단계 {len(out['skip'])}개(마른 실행, 아무것도 돌리지 않음)")
        for x in order:
            print(f"  다시: {x}" + (f"  ({reasons[x]})" if x in reasons else "  (앞 단계가 바뀌어 뒤 단계로)"))
    return out


def baseline(run, conf, with_code=False):
    p = run / "state.json"
    state = json.loads(p.read_text(encoding="utf-8")) if p.exists() else {"run": run.name, "steps": {}}
    n = 0
    for s in conf["stages"]:
        if s.get("outputs") and not expected_outputs(run, s):     # 묶음 출력까지 다 있어야 기준으로 삼음
            rec = state["steps"].setdefault(s["id"], {"status": "done", "kind": s.get("kind")})
            if rec.get("status") != "done":
                continue
            rec["input_hash"] = input_hash(run, s)
            if with_code and code_hash(s):
                rec["code_hash"] = code_hash(s)
            rec["baseline_at"] = now_iso()
            n += 1
    write_json(p, state)
    print(f"기준 해시를 적은 단계 {n}개(출력이 모두 있고 done인 단계) → state.json")
    return 0


def check(conf):
    errors = []
    lim = conf.get("limits") or {}
    for k in LIMIT_KEYS:
        if not isinstance(lim.get(k), int) or lim[k] < 1:
            errors.append(f"상한 {k}가 1 이상의 정수가 아님: {lim.get(k)}")
    S = stage_by_id(conf)
    if len(S) != len(conf["stages"]):
        errors.append("단계 id가 겹침")
    owner = {}
    for s in conf["stages"]:
        for rel in s.get("code") or []:
            if not (ROOT / rel).is_file():
                errors.append(f"{s['id']}의 지시문이나 코드 파일이 없음: {rel}")
        for a in s.get("after") or []:
            if a not in S:
                errors.append(f"{s['id']}의 뒤 단계 {a}가 정의에 없음")
        for o in s.get("outputs") or []:
            for other, pat in owner.items():
                if o == pat[1] or fnmatch.fnmatch(o, pat[1]) or fnmatch.fnmatch(pat[1], o):
                    errors.append(f"출력 겹침: {s['id']}의 {o}와 {pat[0]}의 {pat[1]}")
            owner[(s["id"], o)] = (s["id"], o)
    status = "FAIL" if errors else "PASS"
    print(f"단계 정의 검사: {status}  (단계 {len(S)}개)")
    for e in errors:
        print(f"  오류: {e}")
    return errors


def assign(conf, batches, reviews=None, sizes=None):
    """묶음을 작업자에게 나눈다: 실제 묶음 크기를 차례로 더해, 작업자당 묶음 수나 리뷰 수 상한을 넘기 직전에 다음 작업자로.
    sizes가 없으면 reviews를 batches로 고르게 나눈 크기로 본다. 묶음 하나가 리뷰 상한보다 크면 멈춘다."""
    lim = conf["limits"]
    if sizes is None:
        sizes = [reviews / batches] * batches if reviews and batches else [0] * batches
    sizes = list(sizes)
    batches = len(sizes)
    big = [i for i, x in enumerate(sizes) if x > lim["worker_max_reviews"]]
    if big:
        die(f"묶음 하나가 작업자 리뷰 상한({lim['worker_max_reviews']})보다 큼: {[(i, sizes[i]) for i in big]}. 묶음을 나눠 주세요.")
    workers, cur, tot = [], [], 0
    for i, x in enumerate(sizes):
        if cur and (len(cur) >= lim["worker_max_batches"] or tot + x > lim["worker_max_reviews"]):
            workers.append(cur)
            cur, tot = [], 0
        cur.append(i)
        tot += x
    if cur:
        workers.append(cur)
    k = max((len(g) for g in workers), default=0)
    out = {"batches": batches, "reviews": reviews if reviews is not None else sum(sizes), "per_worker": k, "workers": len(workers),
           "worker_reviews": [round(sum(sizes[i] for i in g), 1) for g in workers],
           "concurrency": min(len(workers), lim["bulk_concurrency"]), "waves": -(-len(workers) // lim["bulk_concurrency"]),
           "calls_without_retry": len(workers), "groups": workers}
    print(f"묶음 {batches}개 → 작업자 {out['workers']}명(작업자당 최대 {k}묶음), 동시 {out['concurrency']}, 차례 {out['waves']}번, "
          f"호출 {out['calls_without_retry']}번(재시도 제외)")
    return out


def main():
    ap = argparse.ArgumentParser(description="다시 할 단계와 상한")
    ap.add_argument("mode", choices=["plan", "baseline", "check", "assign"])
    ap.add_argument("run", nargs="?")
    ap.add_argument("--config", default=str(CONF))
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--batches", type=int, default=0)
    ap.add_argument("--reviews", type=int, default=0)
    ap.add_argument("--sizes", default="", help="묶음 크기(쉼표로). 있으면 --batches, --reviews 대신 씀")
    ap.add_argument("--with-code", action="store_true", help="baseline: 지금 지시문과 코드 해시도 기준으로 적음")
    a = ap.parse_args()
    conf = load_conf(a.config)
    if a.mode == "check":
        sys.exit(1 if check(conf) else 0)
    if a.mode == "assign":
        sz = [int(x) for x in a.sizes.split(",") if x.strip()] or None
        assign(conf, a.batches, a.reviews or None, sz)
        sys.exit(0)
    run = resolve_run(a.run)
    sys.exit(baseline(run, conf, a.with_code) if a.mode == "baseline" else (0 if plan(run, conf, a.json) is not None else 1))


if __name__ == "__main__":
    main()
