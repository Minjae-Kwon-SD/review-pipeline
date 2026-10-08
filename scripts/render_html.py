"""HTML 리포트 한국어판(06_report.html)을 만들고 검사한다. 모델을 부르지 않는다.

사용:
  python scripts/render_html.py build [회차]
    숫자는 05_metrics.json, 07b_issue_counts.json, 07c_safety_summary.json에서, 문장은 06_report.md에서 그대로 가져와
    06_report.html 한 파일을 만든다(외부 스크립트, 스타일, 글꼴, 이미지 없음. 데이터는 const D 하나).
    화면에 쓴 숫자마다 (위치, 값, JSON 경로)를 06_report_html_numbers.json에 남긴다.
  python scripts/render_html.py check [회차]
    1. 숫자 대조: 06_report_html_numbers.json의 항목마다 HTML 글자와 JSON 값(같은 표기)이 같은지.
    2. 드릴다운 대조: 리뷰 수를 보여 주는 드릴다운마다 같은 필터를 파이썬으로 돌린 리뷰 수와 화면 숫자가 같은지.
       세부 이슈 라벨은 07b_issue_counts.json(전체, 브랜드면 by_asin 합), 안전 증상은 07c 판정의 리뷰 id와 같은지.
    3. 한 파일: 외부 참조(http, https) 0개(리뷰 원문 안의 주소는 제외), 우리가 쓴 글자에 가운뎃점 0개(리뷰 원문, 변형 텍스트 제외).
    결과: 06_report_html_check.json. 하나라도 FAIL이면 종료 코드 1.
"""
import argparse
import html
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import sections  # noqa: E402
from pipeline_io import (split_tags, category_conf, ROOT, ASIN_COLS, DIST_COLS, REVIEW_COLS, die, load_config, load_csv_or_die, load_schema, load_yaml,  # noqa: E402
                         now_iso, read_jsonl, resolve_run, write_json)
from weight import build_weights  # noqa: E402

for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass

SENT = {"positive": 0, "negative": 1, "mixed": 2, "neutral": 3}
SENT_KO = ["긍정", "부정", "혼합", "중립"]
SIDE_KO = {"P": "제품", "B": "브랜드"}
TITLE = "아마존 리뷰 분석"            # 카테고리 설정(report.title)이 없을 때
CHAPTERS = [(1, "분포 개요"), (2, "주제별 언급과 감성"), (3, "주제 평가"), (4, "영향 분석"), (5, "시간 추이"),
            (6, "함께 나오는 주제"), (7, "신뢰 신호"), (8, "핵심 인사이트"), (9, "브랜드(ASIN)별 비교"), (10, "브랜드 심층"),
            (11, "변형(용량) 신호"), (12, "리뷰 탐색기"), (13, "전략 방향")]
QUOTE = re.compile(r'"(.+?)"\s*\(([^()]+?),\s*([1-5])★,\s*(R[0-9A-Z]+)\)')


# ---------------------------------------------------------------- 표기(검사도 같은 함수를 쓴다)

def f_int(v):
    return f"{int(v):,}"


def f_pct(v):
    return f"{float(v):.1f}%"


def f_star(v):
    return f"{float(v):.2f}★"


def f_gap(v):
    return f"{float(v):+.2f}"


def f_usd(v):
    return f"{float(v):.2f}달러"


def f_raw(v):
    return str(v)


FMT = {"int": f_int, "pct": f_pct, "star": f_star, "gap": f_gap, "usd": f_usd, "raw": f_raw}


def esc(s):
    return html.escape(str(s), quote=True)


def md(s):
    """06_report.md 문장 한 줄을 HTML로(굵게만)."""
    return re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", esc(s))


class Out:
    """숫자 기록과 드릴다운 기록을 모은다."""

    def __init__(self, sources):
        self.src = sources
        self.nums = []

    def num(self, src, path, fmt, cls=""):
        v = resolve(self.src[src], path)
        text = FMT[fmt](v)
        k = f"n{len(self.nums)}"
        self.nums.append({"k": k, "src": src, "path": path, "fmt": fmt, "text": text})
        return f'<span data-k="{k}"{f" class={chr(39)}{cls}{chr(39)}" if cls else ""}>{esc(text)}</span>'


def resolve(obj, path):
    for p in path:
        if isinstance(obj, list):
            obj = obj[int(p)]
        else:
            obj = obj[p]
    return obj


def drill_attr(f, title, n=None):
    """드릴다운 속성. n이 있으면 화면 숫자를 data-n으로 남겨 검사가 파이썬 필터 결과와 대조한다."""
    a = f' data-f="{esc(json.dumps(f, ensure_ascii=False))}" data-t="{esc(title)}" onclick="drillEl(this)" tabindex="0"'
    if n is not None:
        a += f' data-n="{int(n)}"'
    return a


# ---------------------------------------------------------------- 06_report.md 읽기

def parse_report(path):
    t = path.read_text(encoding="utf-8")
    t = re.sub(r"<!-- 표:(.+?) -->.*?<!-- /표:\1 -->", "", t, flags=re.S)
    head, chapters, cur = [], {}, None
    for line in t.splitlines():
        m = re.match(r"^## (\d+)\.\s*(.*)$", line)
        if m:
            cur = int(m.group(1))
            chapters[cur] = []
            continue
        if line.startswith(LG.marker("appendix")) or line.startswith("## 부록"):
            cur = "appendix"
            chapters[cur] = []
            continue
        if cur is None:
            head.append(line)
        else:
            chapters[cur].append(line)
    return head, chapters


def split_claim(text):
    m = re.match(r"\s*\*\*(.+?)\*\*\s*(.*)$", text)
    return (m.group(1), m.group(2)) if m else ("", text)


def numbered_items(lines):
    """'1. **주장** 본문' 다음 줄 '> "인용" (...)'를 묶는다. 목록 밖 문단은 ('para', 글)로."""
    items = []
    for l in lines:
        s = l.strip()
        if not s:
            continue
        m = re.match(r"^\d+\.\s+(.*)$", s)
        if m:
            claim, body = split_claim(m.group(1))
            items.append({"claim": claim, "body": body, "quotes": []})
        elif s.startswith(">") and items and QUOTE.search(s):
            items[-1]["quotes"].append(QUOTE.search(s).groups())
        elif not s.startswith("#") and not s.startswith("<!--"):
            items.append({"para": s})
    return items


# ---------------------------------------------------------------- 데이터 모으기

def collect(run):
    m = json.loads((run / "05_metrics.json").read_text(encoding="utf-8"))
    counts = json.loads((run / "07b_issue_counts.json").read_text(encoding="utf-8"))
    safety = json.loads((run / "07c_safety_summary.json").read_text(encoding="utf-8"))
    verdicts = ((load_yaml(run / "07c_safety_verdicts.yaml") or {}).get("audit") or {}).get("verdicts") or []
    schema = load_schema(run)
    reviews = load_csv_or_die(run / "02_reviews.csv", REVIEW_COLS)
    # off_category 리뷰와 스키마 밖 주제 태그는 집계 전에 뺀다(weight.py와 같은 규칙). 뺀 수는 화면 안내에 적는다.
    reviews, tags, dropped = split_tags(reviews, read_jsonl(run / "04_tags.jsonl"), schema)
    m["_dropped"] = dropped
    dist = {r["asin"]: r for r in load_csv_or_die(run / "02_star_distribution.csv", DIST_COLS)}
    weight, _, _, _ = build_weights(reviews, dist, load_config())
    labels_rows = read_jsonl(run / "07b_issue_labels.jsonl")
    approved = load_yaml(run / "07a_issues_approved.yaml") or {}
    return m, counts, safety, verdicts, schema, reviews, weight, tags, labels_rows, approved


def build_data(m, counts, safety, verdicts, schema, reviews, weight, tags, labels_rows, approved):
    subs = list(schema)
    sidx = {s: i for i, s in enumerate(subs)}
    brands = [b["brand"] for b in m["brand_deep"]]
    bidx = {b: i for i, b in enumerate(brands)}
    brand_of_asin = m["brand_of_asin"]
    vkey = (m.get("variant_signal") or {}).get("key")
    R = []
    for r in reviews:
        vlabel = ""
        if vkey:
            v = sections.variant_parts(r.get("variant_text")).get(vkey)
            if v:
                vlabel = sections.norm_variant(vkey, v)[0]
        R.append([r["review_id"], r["asin"], r.get("variant_asin") or "", int(r["star"]), r["title"], r["body"], r["date"],
                  1 if r["verified"] == "true" else 0, int(r.get("helpful_votes") or 0),
                  bidx.get(brand_of_asin.get(r["asin"], ""), -1), round(weight[r["review_id"]], 4),
                  r.get("variant_text") or "", 1 if r["vine"] == "true" else 0, vlabel])
    ridx = {r[0]: i for i, r in enumerate(R)}
    T, tidx = [], {}
    for t in tags:
        tidx[(t["review_id"], t["topic"])] = len(T)
        T.append([ridx[t["review_id"]], sidx[t["topic"]], SENT[t["sentiment"]], t["quote"]])
    labels, lidx = [], {}
    for tp in approved.get("topics") or []:
        for direction, x in tp["directions"].items():
            for l in x["labels"]:
                lidx[(tp["topic"], direction, l["id"])] = len(labels)
                labels.append([sidx[tp["topic"]], 1 if direction == "negative" else 0, l["name_ko"], l["id"]])
    L = []
    for row in labels_rows:
        for lab in row["labels"]:
            if lab == "other":
                continue
            if (row["review_id"], row["topic"]) not in tidx:      # 집계에서 뺀 리뷰(off_category)의 라벨
                continue
            L.append([tidx[(row["review_id"], row["topic"])], lidx[(row["topic"], row["direction"], lab)]])
    sym = defaultdict(list)
    neg_safety = {t["review_id"] for t in tags if t["topic"] == "safety" and t["sentiment"] == "negative"}
    for v in verdicts:
        if v.get("symptom_type") and str(v.get("review_id")) in neg_safety:
            if str(v["review_id"]) in ridx:
                sym[v["symptom_type"]].append(ridx[str(v["review_id"])])
    periods = [[p["period"], p["start"], p["end"]] for p in m["time_trend"]["periods"]]
    return {"subs": [schema[s]["name_ko"] for s in subs], "sid": subs, "side": [schema[s]["side"] for s in subs],
            "brands": brands, "R": R, "T": T, "labels": labels, "L": L, "total": len(R), "periods": periods,
            "sym": {k: sorted(v) for k, v in sym.items()}}, sidx, bidx, lidx


# ---------------------------------------------------------------- 장 그리기

class Lang:
    """화면 언어. ko는 스크립트 안 한국어 원문 그대로, 그 밖은 config/i18n/report_ui_<lang>.yaml(키는 한국어 원문)과
    runs/<회차>/i18n_names_<lang>.yaml(주제, 라벨, 증상, 기간 이름)."""

    def __init__(self, code="ko", run=None, ui="report_ui"):
        self.code = code
        self.conf = category_conf(run) if run is not None else {}
        self.missing = set()
        self.cat, self.names = {}, {}
        if code != "ko":
            self.cat = load_yaml(ROOT / "config" / "i18n" / f"{ui}_{code}.yaml") or {}
            self.names = load_yaml(run / f"i18n_names_{code}.yaml") or {}
            if not self.cat or not self.names:
                die(f"{code} 문구 파일(config/i18n/{ui}_{code}.yaml)이나 이름표(i18n_names_{code}.yaml)가 없습니다.")

    def __call__(self, _text, **kw):
        if self.code == "ko":
            t = _text
        else:
            t = (self.cat.get("strings") or {}).get(_text)
            if t is None:
                self.missing.add(_text)
                t = _text
        return t.format(**kw) if kw else t

    def topic(self, tid, ko):
        return ko if self.code == "ko" else self.names["topics"].get(tid, ko)

    def label(self, topic, direction, lid, ko):
        return ko if self.code == "ko" else (self.names["labels"].get(f"{topic}.{direction}.{lid}") or {}).get("en", ko)

    def sym(self, ko):
        return ko if self.code == "ko" else self.names["symptoms"].get(ko, ko)

    def period(self, ko):
        return ko if self.code == "ko" else self.names["periods"].get(ko, ko)

    def sent(self):
        return SENT_KO if self.code == "ko" else self.names["sentiments"]

    def side(self, s):
        return SIDE_KO[s] if self.code == "ko" else self.names["sides"][s]

    def raw(self, v):
        v = str(v)
        if self.code != "ko":
            for a, b in (self.names.get("raw_replace") or {}).items():
                v = v.replace(a, b)
        return v

    def chapters(self):
        if self.code == "ko":
            return CHAPTERS
        return [(n, self.cat["chapters"][n]) for n, _ in CHAPTERS]

    def title(self):
        t = ((self.conf.get("report") or {}).get("title") or {}).get(self.code)
        if t:
            return t
        if self.code == "ko":
            return f"{TITLE}: {self.conf['name_ko']}" if self.conf.get("name_ko") else TITLE
        return self.cat["title"]

    def marker(self, k):
        if self.code == "ko":
            return KO_MARKERS[k]
        return self.cat["md_markers"][k]

    def note(self, s):
        """metrics notes의 한국어 문구를 문구 파일의 notes_patterns(정규식 -> 영어 틀)로 옮긴다. 맞는 틀이 없으면 빠진 문구로 센다."""
        if self.code == "ko":
            return s
        for p in self.cat.get("notes_patterns") or []:
            mt = re.fullmatch(p["re"], s)
            if mt:
                return p["en"].format(*mt.groups())
        self.missing.add(s)
        return s

    def ui(self):
        return UI_KO if self.code == "ko" else self.cat["ui"]


KO_MARKERS = {"reading": "**데이터 읽기**", "strengths": "강점", "weaknesses": "약점", "bullet": r"^- (강점|약점) \d+:\s*(.*)$",
              "bullet_map": {"강점": "강점", "약점": "약점"}, "product": "제품", "branding": "브랜딩", "appendix": "## 부록",
              "label_count_re": "{name}(?:이|가|은|는)? 리뷰 (\\d+)개", "symptom_re": "{name} (\\d+)개\\(가중", "symptom_text": "{name} {n}개",
              "overlap_re": "함께 붙은 리뷰 {n}개", "conclusion": "**결론**"}
UI_KO = {"all": "전체", "close": "닫기", "variant": "변형", "verified": "구매 확인", "unverified": "구매 미확인", "helpful": "도움돼요",
         "more": "더 보기", "reviews": "리뷰", "count_suffix": "개", "sample_avg": "표본 평균", "full": "리뷰 전문", "tags": "태그",
         "positive": "긍정", "negative": "부정"}
LG = Lang("ko")


def readings(lines):
    mk = LG.marker("reading")
    return [l.split(mk, 1)[1].strip() for l in lines if l.startswith(mk)]


def reading_html(texts, linker=None):
    if not texts:
        return ""
    body = "".join(f"<p>{linker(md(t)) if linker else md(t)}</p>" for t in texts)
    return f'<div class="reading"><span class="rt">{esc(LG("데이터 읽기"))}</span>{body}</div>'


def quote_chip(q, sent_cls):
    text, brand, star, rid = q
    return (f'<span class="chip {sent_cls} clk" onclick="openRev(\'{rid}\')" tabindex="0">“{esc(text)}”'
            f'<em>{esc(brand)} {star}★ {rid}</em></span>')


CONCL = {}   # 장 번호 -> 그 장의 한 줄 결론(06_report.md의 '**결론**' 줄)


def section(n, title, sub, body, new=False):
    tag = ' <span class="newtag">NEW</span>' if new else ""
    concl = f'<p class="concl"><b>{md(CONCL[n])}</b></p>' if CONCL.get(n) else ""
    return (f'<section id="sec{n}"><h2><span class="num">{n}</span>{esc(title)}{tag}</h2>'
            f'<p class="sub">{esc(sub)}</p>{concl}{body}</section>')


def neg_pill(v):
    cls = "hi" if v >= 60 else ("mid" if v >= 30 else "lo")
    return cls


class Linker:
    """문장 속 '<라벨 이름> 리뷰 n개'(영어판은 '<label> (n reviews)'), '<증상> n개(가중', '함께 붙은 리뷰 n개'를 드릴다운으로 바꾼다.
    숫자가 07b(전체 또는 그 브랜드) 값과 같을 때만 바꾸고, 다르면 misses에 남긴다."""

    def __init__(self, D, counts, lidx, overlap, bidx, m, sym_names):
        self.D, self.counts, self.lidx, self.overlap, self.m = D, counts, lidx, overlap, m
        self.by_name = defaultdict(list)
        for key, v in counts["topics"].items():
            for l in v["labels"]:
                if l["id"] != "other":
                    self.by_name[LG.label(v["topic"], v["direction"], l["id"], l["name_ko"])].append((v["topic"], v["direction"], l))
        self.misses = []
        self.asins_of_brand = {b["brand"]: b["asins"] for b in m["brand_deep"]}
        self.bidx = bidx
        self.sym_names = sym_names          # 화면 이름 -> 리뷰 번호 목록

    def __call__(self, h, brand=None):
        slots = []

        def slot(s):
            slots.append(s)
            return f"\x00{len(slots) - 1}\x00"
        for name in sorted(self.by_name, key=len, reverse=True):
            pat = re.compile(LG.marker("label_count_re").replace("{name}", re.escape(esc(name))))

            def rep(mt, name=name):
                n = int(mt.group(1))
                for topic, direction, l in self.by_name[name]:
                    want = l["reviews"] if brand is None else sum(l["by_asin"].get(a, 0) for a in self.asins_of_brand[brand])
                    if want == n:
                        f = {"label": self.lidx[(topic, direction, l["id"])]}
                        title = LG("{t}({d})", t=name, d=LG("부정") if direction == "negative" else LG("긍정"))
                        if brand is not None:
                            f["brand"] = self.bidx[brand]
                            title = LG("{b}: {t}", b=brand, t=title)
                        return slot(f'<span class="lnk"{drill_attr(f, title, n)}>{mt.group(0)}</span>')
                self.misses.append(f"{brand or '전체'}: {name} {n}(07b 값과 다름)")
                return mt.group(0)
            h = pat.sub(rep, h)
        for name, ids in self.sym_names.items():
            pat = re.compile(LG.marker("symptom_re").replace("{name}", re.escape(esc(name))))

            def rep2(mt, name=name, ids=ids):
                n = int(mt.group(1))
                if n != len(ids):
                    self.misses.append(f"증상 {name} {n}(07c 값 {len(ids)})")
                    return mt.group(0)
                whole = mt.group(0)
                shown = LG.marker("symptom_text").format(name=esc(name), n=n)
                rest = whole[len(shown):] if whole.startswith(shown) else whole[whole.find(str(n)) + len(str(n)):]
                return slot(f'<span class="lnk"{drill_attr({"rids": ids}, LG("안전 부정: {s}", s=name), n)}>{shown}</span>{rest}')
            h = pat.sub(rep2, h)
        if self.overlap:
            ov = self.overlap
            la = [self.lidx[tuple(x.split(".", 2))] for x in ov["labels"]]

            def rep3(mt):
                return slot(f'<span class="lnk"{drill_attr({"labels": la}, LG("두 라벨이 함께 붙은 리뷰"), ov["reviews"])}>{mt.group(0)}</span>')
            h = re.sub(re.escape(LG.marker("overlap_re").format(n=ov["reviews"])), rep3, h)
        return re.sub(r"\x00(\d+)\x00", lambda mt: slots[int(mt.group(1))], h)


def build_html(run, lang="ko"):
    global LG
    LG = Lang(lang, run)
    FMT["usd"] = f_usd if lang == "ko" else (lambda v: f"${float(v):.2f}")
    FMT["raw"] = (lambda v: LG.raw(v))
    m, counts, safety, verdicts, schema, reviews, weight, tags, labels_rows, approved = collect(run)
    D, sidx, bidx, lidx = build_data(m, counts, safety, verdicts, schema, reviews, weight, tags, labels_rows, approved)
    D["subs"] = [LG.topic(s, schema[s]["name_ko"]) for s in D["sid"]]
    D["labels"] = [[l[0], l[1], LG.label(D["sid"][l[0]], "negative" if l[1] else "positive", l[3], l[2]), l[3]] for l in D["labels"]]
    D["periods"] = [[LG.period(p[0]), p[1], p[2]] for p in D["periods"]]
    sym_ko = D["sym"]
    D["sym"] = {LG.sym(k): v for k, v in sym_ko.items()}
    md_name = "06_report.md" if lang == "ko" else f"06_report_{lang}.md"
    head, ch = parse_report(run / md_name)
    CONCL.clear()
    cm = KO_MARKERS["conclusion"] if lang == "ko" else (LG.cat.get("md_markers") or {}).get("conclusion")
    for n_, ls in (ch.items() if cm else []):
        c_ = next((l.split(cm, 1)[1].strip() for l in ls if l.startswith(cm)), None)
        if c_:
            CONCL[n_] = c_
    o = Out({"metrics": m, "counts": counts, "safety": safety})
    link = Linker(D, counts, lidx, m.get("issue_overlap"), bidx, m, D["sym"])
    name = {s: LG.topic(s, schema[s]["name_ko"]) for s in schema}
    SENTL = LG.sent()
    T = LG
    S = m["summary"]
    CH = dict(LG.chapters())
    parts = []

    # 머리
    notes = [l.lstrip("> ").strip() for l in head if l.startswith(">")]
    dr = m.get("_dropped") or {}
    if dr.get("off_category_reviews") or dr.get("unknown_topic_tags"):
        notes.append(T("카테고리와 무관한 리뷰 {n}개(off_category)와 승인 스키마에 없는 주제의 태그 {u}개는 모든 집계에서 뺐습니다.",
                       n=len(dr.get("off_category_reviews") or []), u=dr.get("unknown_topic_tags", 0)))
    kpis = [(o.num("metrics", ["summary", "asins"], "int"), T("ASIN")), (o.num("metrics", ["summary", "reviews"], "int"), T("리뷰")),
            (o.num("metrics", ["summary", "tags"], "int"), T("태그(리뷰 x 주제)")),
            (o.num("metrics", ["summary", "weighted_mean_star"], "star"), T("평균 별점(가중)")),
            (o.num("metrics", ["summary", "brands"], "int"), T("브랜드")),
            (o.num("metrics", ["summary", "date_min"], "raw") + " ~ " + o.num("metrics", ["summary", "date_max"], "raw"), T("리뷰 기간"))]
    parts.append(f'<h1>{esc(LG.title())}</h1>')
    parts.append('<div class="toci">' + "".join(f'<a href="#sec{n}"><b>{n}</b>{esc(t)}</a>' for n, t in LG.chapters()) + "</div>")
    parts.append(f'<div class="callout"><div class="cb"><b>{esc(T("안내"))}</b><ul>' + "".join(f"<li>{md(x)}</li>" for x in notes)
                 + f"<li>{esc(T('숫자, 막대, 표 행, 인용을 누르면 그 바탕이 된 리뷰 원문이 열립니다.'))}</li></ul></div></div>")
    parts.append('<div class="kpis">' + "".join(f'<div class="kpi"><div class="v">{v}</div><div class="l">{esc(l)}</div></div>'
                                                for v, l in kpis) + "</div>")

    # 1장 분포
    sr = m["sentiment"]
    cuts, acc = [], 0.0
    for s, var in (("positive", "pos"), ("negative", "neg"), ("mixed", "mix"), ("neutral", "neu")):
        cuts.append(f"var(--{var}) {acc:.2f}% {acc + sr['raw_pct'][s]:.2f}%")
        acc += sr["raw_pct"][s]
    legend = "".join(
        f'<div class="lg clk"{drill_attr({"sent": SENT[s]}, T("{s} 태그가 있는 리뷰", s=SENTL[SENT[s]]))}><span class="dot" style="background:var(--{var})"></span>'
        f'{esc(SENTL[SENT[s]])} {o.num("metrics", ["sentiment", "raw", s], "int")}({o.num("metrics", ["sentiment", "raw_pct", s], "pct")}), '
        f'{esc(T("가중"))} {o.num("metrics", ["sentiment", "weighted_pct", s], "pct")}</div>'
        for s, var in (("positive", "pos"), ("negative", "neg"), ("mixed", "mix"), ("neutral", "neu")))
    side = m["side"]
    pcut = side["raw_pct"]["P"]
    donut1 = (f'<div class="col"><div class="coltitle">{esc(T("감성 구성(태그 기준)"))}</div><div class="donutwrap"><div class="donut" '
              f'style="background:conic-gradient({",".join(cuts)})"><div class="hole"><span class="hv">{o.num("metrics", ["summary", "tags"], "int")}</span>'
              f'<span class="hl">{esc(T("태그"))}</span></div></div><div class="legend">{legend}</div></div></div>')
    donut2 = (f'<div class="col"><div class="coltitle">{esc(T("제품과 브랜드 주제"))}</div><div class="donutwrap"><div class="donut" '
              f'style="background:conic-gradient(var(--prod) 0 {pcut:.2f}%,var(--brandc) {pcut:.2f}% 100%)"><div class="hole">'
              f'<span class="hv">{o.num("metrics", ["summary", "tags"], "int")}</span><span class="hl">{esc(T("태그"))}</span></div></div><div class="legend">'
              f'<div class="lg"><span class="dot" style="background:var(--prod)"></span>{esc(LG.side("P"))} {o.num("metrics", ["side", "raw", "P"], "int")}'
              f'({o.num("metrics", ["side", "raw_pct", "P"], "pct")})</div><div class="lg"><span class="dot" style="background:var(--brandc)"></span>'
              f'{esc(LG.side("B"))} {o.num("metrics", ["side", "raw", "B"], "int")}({o.num("metrics", ["side", "raw_pct", "B"], "pct")})</div></div></div></div>')
    st = m["stars"]
    mx = max(st["sample_counts"].values())
    mxr = max(st["real_pct"].values())
    color = {1: "neg", 2: "neg", 3: "mix", 4: "pos", 5: "pos"}
    sample_bars = "".join(
        f'<div class="sb clk"{drill_attr({"star": s}, T("{s}★ 리뷰", s=s), st["sample_counts"][str(s)])}>'
        f'{o.num("metrics", ["stars", "sample_counts", str(s)], "int")}<div class="sbar" style="height:{max(2, 90 * st["sample_counts"][str(s)] / mx):.0f}px;'
        f'background:var(--{color[s]})"></div><span>{s}★</span></div>' for s in range(1, 6))
    real_bars = "".join(
        f'<div class="sb">{o.num("metrics", ["stars", "real_pct", str(s)], "pct")}<div class="sbar" style="height:{max(2, 90 * st["real_pct"][str(s)] / mxr):.0f}px;'
        f'background:var(--{color[s]})"></div><span>{s}★</span></div>' for s in range(1, 6))
    body = (f'<div class="cols">{donut1}{donut2}</div><div class="cols" style="margin-top:22px"><div class="col"><div class="coltitle">'
            f'{T("표본(모은 그대로), 평균 {v}", v=o.num("metrics", ["summary", "sample_mean_star"], "star"))}</div><div class="stardist">{sample_bars}</div></div>'
            f'<div class="col"><div class="coltitle">{T("아마존 실제 분포, 가중 평균 {v}", v=o.num("metrics", ["summary", "weighted_mean_star"], "star"))}</div>'
            f'<div class="stardist">{real_bars}</div><div class="fn">'
            f'{T("표본이 없는 별점 묶음의 실제 비율 {v}는 가중 결과에서 빠졌습니다.", v=o.num("metrics", ["stars", "missing_real_pct"], "pct"))}</div></div></div>'
            + reading_html(readings(ch[1]), link))
    parts.append(section(1, CH[1], T("태그(리뷰 x 주제) 기준 감성 구성, 제품과 브랜드 주제 비중, 별점 분포"), body))

    # 2장 주제별 언급
    topics = m["topics"]
    tmax = max(t["mentions"] for t in topics)
    rows = []
    for i, t in enumerate(topics):
        n = t["mentions"]
        tn = name[t["id"]]
        segs = "".join(f'<span style="width:{100 * t[s] / n:.2f}%;background:var(--{v})"></span>'
                       for s, v in (("positive", "pos"), ("negative", "neg"), ("mixed", "mix"), ("neutral", "neu")) if n)
        rows.append(f'<div class="brow clk"{drill_attr({"sub": sidx[t["id"]]}, tn, n)}><span class="blab">'
                    f'<span class="tcat {"tp" if t["side"] == "P" else "tb"}">{esc(LG.side(t["side"]))}</span> {esc(tn)}</span>'
                    f'<span class="btrack"><span class="bbar" style="width:{100 * n / tmax:.1f}%">{segs}</span></span>'
                    f'<span class="bn">{o.num("metrics", ["topics", i, "mentions"], "int")}</span>'
                    f'<span class="bneg">{o.num("metrics", ["topics", i, "neg_pct"], "pct")}</span></div>')
    body = (f'<div class="bhead"><span class="blab"></span><span class="btrack" style="background:none">{esc(T("언급"))}</span><span class="bn">{esc(T("리뷰"))}</span>'
            f'<span class="bneg">{esc(T("부정 비율"))}</span></div>' + "".join(rows) + reading_html(readings(ch[2]), link))
    parts.append(section(2, CH[2], T("막대 길이는 언급 수(리뷰 수), 색은 감성 구성(초록 긍정, 빨강 부정, 주황 혼합, 회색 중립)"), body))

    # 3장 주제 평가
    trs = []
    for i, t in enumerate(topics):
        si = sidx[t["id"]]
        tn = name[t["id"]]
        trs.append(
            f'<tr><td><span class="tcat {"tp" if t["side"] == "P" else "tb"}">{esc(LG.side(t["side"]))}</span></td>'
            f'<td class="tl clk"{drill_attr({"sub": si}, tn, t["mentions"])}><b>{esc(tn)}</b></td>'
            f'<td>{o.num("metrics", ["topics", i, "mentions"], "int")}</td>'
            f'<td class="cpos clk"{drill_attr({"sub": si, "sent": 0}, T("{t} {s}", t=tn, s=SENTL[0]), t["positive"])}>{o.num("metrics", ["topics", i, "positive"], "int")}</td>'
            f'<td class="cneg clk"{drill_attr({"sub": si, "sent": 1}, T("{t} {s}", t=tn, s=SENTL[1]), t["negative"])}>{o.num("metrics", ["topics", i, "negative"], "int")}</td>'
            f'<td class="clk"{drill_attr({"sub": si, "sent": 2}, T("{t} {s}", t=tn, s=SENTL[2]), t["mixed"])}>{o.num("metrics", ["topics", i, "mixed"], "int")}</td>'
            f'<td class="clk"{drill_attr({"sub": si, "sent": 3}, T("{t} {s}", t=tn, s=SENTL[3]), t["neutral"])}>{o.num("metrics", ["topics", i, "neutral"], "int")}</td>'
            f'<td><span class="negpill {neg_pill(t["neg_pct"])}">{o.num("metrics", ["topics", i, "neg_pct"], "pct")}</span></td>'
            f'<td><span class="negpill {neg_pill(t["weighted_neg_pct"])}">{o.num("metrics", ["topics", i, "weighted_neg_pct"], "pct")}</span></td>'
            f'<td>{o.num("metrics", ["topics", i, "neg_reviewer_pct"], "pct")}</td><td>{o.num("metrics", ["topics", i, "pos_reviewer_pct"], "pct")}</td></tr>')
    heads3 = [T("주제"), T("언급")] + list(SENTL) + [T("부정 비율"), T("가중 부정 비율"), T("부정 언급 리뷰어(가중)"), T("긍정 언급 리뷰어(가중)")]
    body = ('<div class="tscroll"><table class="ct"><thead><tr><th></th>' + "".join(f'<th{" class=tl" if j == 0 else ""}>{esc(h)}</th>' for j, h in enumerate(heads3))
            + '</tr></thead><tbody>' + "".join(trs) + '</tbody></table></div><div class="fn">'
            + esc(T('원본 수는 어떤 불만이 있는지, 가중 비율은 아마존 실제 별점 분포로 되돌렸을 때 그 불만이 얼마나 흔한지를 보여 줍니다. 숫자를 누르면 그 리뷰가 열립니다.'))
            + '</div>' + reading_html(readings(ch[3]), link))
    parts.append(section(3, CH[3], T("모은 표본의 원본 수와, 실제 별점 분포로 되돌린 가중 비율"), body))

    # 4장 영향 분석
    imp = m["impact"]
    W, top, rowh, x0, x1 = 760, 30, 34, 210, 730
    xs = lambda v: x0 + (x1 - x0) * (v - 1) / 4
    svg = [f'<svg class="imp" viewBox="0 0 {W} {top + rowh * len(imp) + 20}" role="img" aria-label="{esc(T("영향 분석"))}">']
    for s in range(1, 6):
        svg.append(f'<line class="gl" x1="{xs(s):.1f}" x2="{xs(s):.1f}" y1="{top - 10}" y2="{top + rowh * len(imp)}"/>'
                   f'<text class="ax" x="{xs(s):.1f}" y="{top - 14}" text-anchor="middle">{s}★</text>')
    for i, r in enumerate(imp):
        y = top + rowh * i + rowh / 2
        tn = name[r["id"]]
        svg.append(f'<g class="clk"{drill_attr({"sub": sidx[r["id"]], "sent": 1}, T("{t} 부정 리뷰", t=tn), r["neg_reviews"])}>'
                   f'<text class="lb" x="{x0 - 10}" y="{y + 4:.1f}" text-anchor="end">{esc(tn)}</text>'
                   f'<line x1="{xs(r["neg_avg_star"]):.1f}" x2="{xs(r["other_avg_star"]):.1f}" y1="{y:.1f}" y2="{y:.1f}" stroke="var(--line)" stroke-width="3"/>'
                   f'<circle class="dotneg" cx="{xs(r["neg_avg_star"]):.1f}" cy="{y:.1f}" r="{6 + min(10, r["neg_reviews"] / 40):.1f}"/>'
                   f'<circle cx="{xs(r["other_avg_star"]):.1f}" cy="{y:.1f}" r="5" fill="var(--pos)"/></g>')
    svg.append("</svg>")
    trs = "".join(
        f'<tr class="clk"{drill_attr({"sub": sidx[r["id"]], "sent": 1}, T("{t} 부정 리뷰", t=name[r["id"]]), r["neg_reviews"])}><td class="tl">{esc(name[r["id"]])}</td>'
        f'<td>{o.num("metrics", ["impact", i, "neg_reviews"], "int")}</td><td class="cneg">{o.num("metrics", ["impact", i, "neg_avg_star"], "star")}</td>'
        f'<td class="cpos">{o.num("metrics", ["impact", i, "other_avg_star"], "star")}</td><td><b>{o.num("metrics", ["impact", i, "gap"], "gap")}</b></td></tr>'
        for i, r in enumerate(imp))
    body = (f'<div class="svgwrap">{"".join(svg)}</div><div class="fn">'
            + T("빨간 점: 그 주제를 부정으로 말한 리뷰의 가중 평균 별점(점 크기는 리뷰 수), 초록 점: 나머지 리뷰의 가중 평균 별점. 부정 언급 리뷰 {n}개 이상인 주제만.",
                n=o.num("metrics", ["rules", "impact_min_neg_reviews"], "int"))
            + f'</div><div class="tscroll"><table class="ct"><thead><tr><th class="tl">{esc(T("주제"))}</th><th>{esc(T("부정 언급 리뷰"))}</th>'
            f'<th>{esc(T("부정 리뷰 평균"))}</th><th>{esc(T("나머지 평균"))}</th><th>{esc(T("격차"))}</th></tr></thead><tbody>{trs}</tbody></table></div>'
            + reading_html(readings(ch[4]), link))
    parts.append(section(4, T("영향 분석: 별점을 가장 많이 깎는 불만"), T("그 주제를 부정으로 말한 리뷰와 나머지 리뷰의 가중 평균 별점 비교"), body, new=True))

    # 5장 시간 추이
    tt = m["time_trend"]
    cols = []
    for i, p in enumerate(tt["periods"]):
        g = p["weighted_group_pct"]
        f = {"dfrom": p["start"], "dto": p["end"]}
        pn = LG.period(p["period"])
        stack = "".join(f'<span style="height:{g[k]:.1f}%;background:var(--{v})"></span>'
                        for k, v in (("negative", "neg"), ("neutral", "mix"), ("positive", "pos")))
        cols.append(f'<div class="tcol clk"{drill_attr(f, T("{p} 리뷰", p=pn), p["reviews"])}><span class="tv">'
                    f'{T("리뷰 {v}", v=o.num("metrics", ["time_trend", "periods", i, "reviews"], "int"))}</span><div class="tstack">{stack}</div>'
                    f'<span class="ty">{esc(pn)}</span><span class="tv">{T("표본 평균 {v}", v=o.num("metrics", ["time_trend", "periods", i, "sample_mean_star"], "star"))}</span>'
                    f'<span class="tv">{T("가중 부정 {v}", v=o.num("metrics", ["time_trend", "periods", i, "weighted_group_pct", "negative"], "pct"))}</span>'
                    f'<span class="tv">{T("부정 태그 {v}", v=o.num("metrics", ["time_trend", "periods", i, "negative_tags"], "int"))}</span></div>')
    share_topics = sorted({k for p in tt["periods"] for k in p["neg_topic_share"]},
                          key=lambda k: -max(p["neg_topic_share"].get(k, 0) for p in tt["periods"]))
    trs = ""
    for k in share_topics:
        tds = ""
        for i, p in enumerate(tt["periods"]):
            if k in p["neg_topic_share"]:
                tds += (f'<td class="clk"{drill_attr({"sub": sidx[k], "sent": 1, "dfrom": p["start"], "dto": p["end"]}, T("{p} {t} 부정", p=LG.period(p["period"]), t=name[k]))}>'
                        f'{o.num("metrics", ["time_trend", "periods", i, "neg_topic_share", k], "pct")}</td>')
            else:
                tds += "<td>-</td>"
        trs += f'<tr><td class="tl">{esc(name[k])}</td>{tds}</tr>'
    nlink = (f'<span class="lnk"{drill_attr({"dfrom": tt["in_progress_from"]}, T("진행 중인 분기 리뷰"), tt["in_progress_reviews"])}>'
             f'{T("{n}개", n=o.num("metrics", ["time_trend", "in_progress_reviews"], "int"))}</span>')
    prog = (f'<div class="fn">{T("진행 중인 분기({d}부터)의 리뷰 {n}는 기간에서 뺐습니다.", d=o.num("metrics", ["time_trend", "in_progress_from"], "raw"), n=nlink)}</div>')
    body = (f'<div class="tchart">{"".join(cols)}</div><div class="fn">{esc(T("막대: 그 기간 리뷰의 가중 별점 묶음 비율(빨강 1~2★, 주황 3★, 초록 4~5★)."))}</div>{prog}'
            f'<div class="coltitle" style="margin-top:16px">{esc(T("기간별 부정 태그의 주제 비중"))}</div><div class="tscroll"><table class="ct"><thead><tr><th class="tl">{esc(T("주제"))}</th>'
            + "".join(f"<th>{esc(LG.period(p['period']))}</th>" for p in tt["periods"]) + f"</tr></thead><tbody>{trs}</tbody></table></div>"
            + reading_html(readings(ch[5]), link))
    parts.append(section(5, CH[5], T("리뷰 날짜 기준. 공유 DB 표본이라 오래된 기간은 낮은 별점 위주일 수 있어, 별점 수준보다 불만 구성을 읽습니다"), body, new=True))

    # 6장 공출현
    co = m["cooccurrence"]

    def pairs(kind, key, var):
        lst = co[kind]
        mxp = max((p["reviews"] for p in lst), default=1)
        return "".join(
            f'<div class="brow clk"{drill_attr({key: [sidx[p["a"]], sidx[p["b"]]]}, f"{name[p[chr(97)]]} + {name[p[chr(98)]]}", p["reviews"])}>'
            f'<span class="blab">{esc(name[p["a"]])} + {esc(name[p["b"]])}</span><span class="btrack"><span class="bbar" style="width:{100 * p["reviews"] / mxp:.1f}%">'
            f'<span style="width:100%;background:var(--{var})"></span></span></span><span class="bn">{o.num("metrics", ["cooccurrence", kind, i, "reviews"], "int")}</span></div>'
            for i, p in enumerate(lst))
    body = (f'<div class="cols"><div class="col"><div class="coltitle">{esc(T("함께 나오는 부정 주제(리뷰 수)"))}</div>{pairs("negative", "pair", "neg")}</div>'
            f'<div class="col"><div class="coltitle">{esc(T("함께 나오는 긍정 주제(리뷰 수)"))}</div>{pairs("positive", "pairPos", "pos")}</div></div>'
            f'<div class="fn">{esc(T("한 리뷰 안에서 두 주제가 같은 감성으로 함께 나온 수입니다. 원인이 아니라 함께 나온다는 뜻입니다."))}</div>'
            + reading_html(readings(ch[6]), link))
    parts.append(section(6, CH[6], T("같은 리뷰에 함께 나온 주제 쌍(행을 누르면 두 주제를 모두 말한 리뷰)"), body, new=True))

    # 7장 신뢰 신호
    ts = m["trust_signals"]
    kp = ""
    for key, label, f in (("verified", T("확인된 구매"), {"verified": 1}), ("unverified", T("확인 안 된 구매"), {"verified": 0}), ("vine", "Vine", {"vine": 1})):
        kp += (f'<div class="kpi clk"{drill_attr(f, T("{l} 리뷰", l=label), ts[key]["reviews"])}><div class="v">{o.num("metrics", ["trust_signals", key, "reviews"], "int")}</div>'
               f'<div class="l">{T("{l}, 평균 {s}, 1~2★ {p}", l=esc(label), s=o.num("metrics", ["trust_signals", key, "mean_star"], "star"), p=o.num("metrics", ["trust_signals", key, "negative_pct"], "pct"))}</div></div>')
    kp += (f'<div class="kpi clk"{drill_attr({"hv": 1}, T("도움돼요가 있는 리뷰"), ts["helpful_reviews"])}><div class="v">{o.num("metrics", ["trust_signals", "helpful_reviews"], "int")}</div>'
           f'<div class="l">{T("도움돼요가 있는 리뷰(표 {t}개), 1~2★ 쪽 {n}, 4~5★ 쪽 {p}", t=o.num("metrics", ["trust_signals", "helpful_total"], "int"), n=o.num("metrics", ["trust_signals", "helpful_negative_pct"], "pct"), p=o.num("metrics", ["trust_signals", "helpful_positive_pct"], "pct"))}</div></div>')
    hw = "".join(
        f'<tr class="clk"{drill_attr({"sub": sidx[x["topic"]], "sent": 1}, T("{t} 부정", t=name[x["topic"]]))}><td class="tl">{esc(name[x["topic"]])}</td>'
        f'<td>{o.num("metrics", ["trust_signals", "helpful_weighted_complaints", i, "votes"], "int")}</td>'
        f'<td>{o.num("metrics", ["trust_signals", "helpful_weighted_complaints", i, "share_pct"], "pct")}</td></tr>'
        for i, x in enumerate(ts["helpful_weighted_complaints"]))
    th = "".join(
        f'<tr class="clk" onclick="openRev(\'{x["review_id"]}\')" tabindex="0"><td class="mono">{x["review_id"]}</td><td>{esc(m["brand_of_asin"].get(x["asin"], x["asin"]))}</td>'
        f'<td>{o.num("metrics", ["trust_signals", "top_helpful", i, "star"], "int")}★</td><td class="tl">{esc(x["title"])}</td>'
        f'<td>{o.num("metrics", ["trust_signals", "top_helpful", i, "votes"], "int")}</td></tr>'
        for i, x in enumerate(ts["top_helpful"]))
    body = (f'<div class="kpis">{kp}</div><div class="cols"><div class="col"><div class="coltitle">{esc(T("도움돼요로 가중한 불만 순위"))}{esc(T(" (잠정)")) if ts.get("helpful_provisional") else ""}</div><div class="tscroll">'
            f'<table class="ct"><thead><tr><th class="tl">{esc(T("주제"))}</th><th>{esc(T("도움돼요 표"))}</th><th>{esc(T("비중"))}</th></tr></thead><tbody>{hw}</tbody></table></div></div>'
            f'<div class="col"><div class="coltitle">{esc(T("도움돼요가 가장 많은 리뷰"))}</div><div class="tscroll"><table class="ct"><thead><tr><th>{esc(T("리뷰"))}</th><th>{esc(T("브랜드"))}</th>'
            f'<th>{esc(T("별점"))}</th><th class="tl">{esc(T("제목(원문)"))}</th><th>{esc(T("표"))}</th></tr></thead><tbody>{th}</tbody></table></div></div></div>'
            f'<div class="fn">{esc(T("이 장의 숫자는 모두 원본(가중 안 함)입니다."))}'
            + (esc(T(" 도움돼요 표를 받은 리뷰가 {n}개로 기준 {k}개보다 적어 순위는 잠정이고 해석하지 않습니다.", n=ts["helpful_reviews"], k=ts["helpful_min_voted"]))
               if ts.get("helpful_provisional") else "") + '</div>' + reading_html(readings(ch[7]), link))
    parts.append(section(7, CH[7], T("확인된 구매, Vine, 도움돼요로 리뷰 데이터 자체를 점검"), body, new=True))

    # 8장 핵심 인사이트
    iss = m["issues"]
    order = sorted(iss, key=lambda k: (iss[k]["direction"] != "negative", -iss[k]["units"]))
    rows = ""
    sym_en = {x["name"]: LG.sym(x["name"]) for x in (m.get("safety_check") or {}).get("by_symptom") or []}
    for key in order:
        s = iss[key]
        ci = counts["topics"][key]
        if key == "safety.negative" and m.get("safety_check", {}).get("by_symptom"):
            sc = m["safety_check"]
            cells = ", ".join(
                f'<span class="lnk"{drill_attr({"rids": D["sym"][sym_en[x["name"]]]}, T("안전 부정: {s}", s=sym_en[x["name"]]), x["reviews"])}>{esc(sym_en[x["name"]])} '
                f'{T("{n}개", n=o.num("metrics", ["safety_check", "by_symptom", j, "reviews"], "int"))}</span>({o.num("metrics", ["safety_check", "by_symptom", j, "weighted_pct"], "pct")})'
                for j, x in enumerate(sc["by_symptom"]))
            other = esc(T("증상별 분류(07c)"))
        else:
            labs = [(j, l) for j, l in enumerate(ci["labels"]) if l["id"] != "other" and l["reviews"] > 0]
            chips = []
            for j, l in labs:
                f = {"label": lidx[(s["topic"], s["direction"], l["id"])]}
                ln = LG.label(s["topic"], s["direction"], l["id"], l["name_ko"])
                chips.append(f'<span class="lnk{" top" if len(chips) < 3 else " more"}"{drill_attr(f, ln, l["reviews"])}>{esc(ln)} '
                             f'{T("{n}개", n=o.num("counts", ["topics", key, "labels", j, "reviews"], "int"))}</span>'
                             f'({o.num("counts", ["topics", key, "labels", j, "weighted_pct"], "pct")})')
            cells = ", ".join(chips[:3]) or esc(T("기타만"))
            if len(chips) > 3:
                cells += f'<details class="dtl"><summary>{esc(T("나머지 라벨 {n}개", n=len(chips) - 3))}</summary>{", ".join(chips[3:])}</details>'
            other = o.num("counts", ["topics", key, "other_pct"], "pct")
        rows += (f'<tr><td class="tl"><b>{esc(name[s["topic"]])}</b></td><td class="{"cneg" if s["direction"] == "negative" else "cpos"}">'
                 f'{esc(T("부정") if s["direction"] == "negative" else T("긍정"))}</td><td class="tl small">{cells}</td><td>{other}</td></tr>')
    ov = m.get("issue_overlap")
    extra = ""
    if ov:
        la = [lidx[tuple(x.split(".", 2))] for x in ov["labels"]]
        na = [LG.label(*x.split(".", 2), nk) for x, nk in zip(ov["labels"], ov["names"])]
        olink = (f'<span class="lnk"{drill_attr({"labels": la}, T("두 라벨이 함께 붙은 리뷰"), ov["reviews"])}>'
                 f'{T("{n}개", n=o.num("metrics", ["issue_overlap", "reviews"], "int"))}</span>')
        extra += ('<div class="fn">' + T('향 부정 "{a}"과 신뢰 부정 "{b}"이 함께 붙은 리뷰 {n}(가중 {p}). 두 수를 더해 읽지 않습니다.',
                                         a=esc(na[0]), b=esc(na[1]), n=olink, p=o.num("metrics", ["issue_overlap", "weighted_pct"], "pct")) + '</div>')
    extra += ('<div class="fn">' + esc(T("주제와 방향마다 리뷰 수가 많은 라벨 3개(기타 제외), 괄호는 가중 비율(그 라벨 리뷰의 가중치 합 ÷ 전체 리뷰 가중치 합). "
                                         "기타 비율은 승인 라벨에 들지 않은 인용 비율. 안전 부정은 라벨 대신 증상별 분류 전부(07c, 알레르기 언급은 본인 반응을 직접 묘사하지 않은 리뷰).")) + '</div>')
    table = (f'<div class="coltitle">{esc(T("세부 이슈(라벨을 누르면 그 리뷰)"))}</div><div class="tscroll"><table class="ct"><thead><tr><th class="tl">{esc(T("주제"))}</th><th>{esc(T("방향"))}</th>'
             f'<th class="tl">{esc(T("세부 이슈(리뷰 수, 가중 비율)"))}</th><th>{esc(T("기타 비율"))}</th></tr></thead><tbody>{rows}</tbody></table></div>{extra}')
    kinds = {LG.marker("strengths"): "강점", LG.marker("weaknesses"): "약점"}
    cards = {"강점": [], "약점": []}
    cur = None
    for l in ch[8]:
        if l.startswith("### "):
            cur = kinds.get(l[4:].strip())
            continue
        if cur in cards:
            cards[cur].append(l)
    sw = ""
    for kind, cls in (("강점", "g"), ("약점", "r")):
        items = [x for x in numbered_items(cards[kind]) if "claim" in x]
        inner = "".join(
            f'<div class="icard"><span class="iclaim {cls}">{md(x["claim"])}</span><div class="ibody">{link(md(x["body"]))}</div>'
            f'<div class="chips">{"".join(quote_chip(q, cls) for q in x["quotes"])}</div></div>' for x in items)
        sw += f'<div class="swcol"><div class="swh {cls}">{esc(T(kind))}</div>{inner or "<div class=fn>" + esc(T("근거 부족")) + "</div>"}</div>'
    body = table + f'<div class="swgrid">{sw}</div>'
    parts.append(section(8, CH[8], T("이번에 고른 상품 표본의 강점과 약점. 세부 이슈 개수와 인용을 누르면 리뷰 원문이 열립니다"), body))

    # 9장 ASIN 비교
    trs = ""
    for i, a in enumerate(m["asins"]):
        b = bidx[a["brand"]]
        wp, wn = a["weighted_pos_pct"], a["weighted_neg_pct"]
        stn, wkn = name[a["strength"]["id"]], name[a["weakness"]["id"]]
        trs += (f'<tr><td class="tl clk"{drill_attr({"asin": a["asin"]}, a["brand"], a["sample_reviews"])}><b>{esc(a["brand"])}</b><div class="mono mut">{a["asin"]}</div></td>'
                f'<td class="small tl">{o.num("metrics", ["asins", i, "price_band"], "raw")}</td><td>{o.num("metrics", ["asins", i, "amazon_rating"], "raw")}★</td>'
                f'<td class="clk"{drill_attr({"asin": a["asin"]}, a["brand"], a["sample_reviews"])}>{o.num("metrics", ["asins", i, "sample_reviews"], "int")}</td>'
                f'<td>{o.num("metrics", ["asins", i, "weighted_mean_star"], "star")}</td>'
                f'<td><div class="minibar"><span style="width:{wp:.1f}%;background:var(--pos)"></span><span style="width:{wn:.1f}%;background:var(--neg)"></span></div>'
                f'<span class="cpos small">{o.num("metrics", ["asins", i, "weighted_pos_pct"], "pct")}</span> / <span class="cneg small">{o.num("metrics", ["asins", i, "weighted_neg_pct"], "pct")}</span></td>'
                f'<td class="tl cpos small clk"{drill_attr({"asin": a["asin"], "sub": sidx[a["strength"]["id"]], "sent": 0}, T("{b}: {t} 긍정", b=a["brand"], t=stn))}>'
                f'{esc(stn)} {o.num("metrics", ["asins", i, "strength", "pos_reviewer_pct"], "pct")}</td>'
                f'<td class="tl cneg small clk"{drill_attr({"asin": a["asin"], "sub": sidx[a["weakness"]["id"]], "sent": 1}, T("{b}: {t} 부정", b=a["brand"], t=wkn))}>'
                f'{esc(wkn)} {o.num("metrics", ["asins", i, "weakness", "neg_reviewer_pct"], "pct")}</td></tr>')
    heads9 = [T("브랜드, ASIN"), T("가격대(현재)"), T("아마존 별점"), T("표본 리뷰"), T("가중 평균"), T("가중 긍정 / 부정"),
              T("가장 큰 강점(긍정 언급 리뷰어, 가중)"), T("가장 큰 약점(부정 언급 리뷰어, 가중)")]
    asin_note = LG.note(m["notes"]["asin_sample_text"])
    body = ('<div class="tscroll"><table class="ct"><thead><tr>' + "".join(f'<th{" class=tl" if j in (0, 1, 6, 7) else ""}>{esc(h)}</th>' for j, h in enumerate(heads9))
            + f'</tr></thead><tbody>{trs}</tbody></table></div><div class="fn">{T("{t}라 브랜드끼리의 비교는 참고용입니다.", t=md(asin_note))}</div>'
            + reading_html(readings(ch[9]), link))
    parts.append(section(9, CH[9], T("ASIN {n}개, 브랜드마다 하나", n=len(m["asins"])), body))

    # 10장 브랜드 심층
    per_brand, cur = defaultdict(list), None
    for l in ch[10]:
        if l.startswith("### "):
            cur = l[4:].strip()
            continue
        if cur:
            per_brand[cur].append(l)
    bullet_re = re.compile(LG.marker("bullet"))
    bmap = LG.marker("bullet_map")
    tabs, panes = "", ""
    for bi, b in enumerate(m["brand_deep"]):
        bn = b["brand"]
        lines = per_brand.get(bn, [])
        tabs += f'<button class="btab{" on" if bi == 0 else ""}" id="bt{bi}" onclick="showTab(\'b\',{bi})">{esc(bn)}<span class="bn2">{b["reviews"]}</span></button>'
        trs = "".join(
            f'<tr class="clk"{drill_attr({"brand": bi, "sub": sidx[t["id"]]}, T("{b}: {t}", b=bn, t=name[t["id"]]), t["mentions"])}><td class="tl"><b>{esc(name[t["id"]])}</b></td>'
            f'<td>{o.num("metrics", ["brand_deep", bi, "top_topics", j, "mentions"], "int")}</td>'
            f'<td class="cpos">{o.num("metrics", ["brand_deep", bi, "top_topics", j, "positive"], "int")}</td>'
            f'<td class="cneg">{o.num("metrics", ["brand_deep", bi, "top_topics", j, "negative"], "int")}</td>'
            + (f'<td>{o.num("metrics", ["brand_deep", bi, "top_topics", j, "mixed"], "int")}</td>'
               f'<td>{o.num("metrics", ["brand_deep", bi, "top_topics", j, "neutral"], "int")}</td>' if "mixed" in t else "")
            + f'<td><span class="negpill {neg_pill(t["neg_pct"])}">{o.num("metrics", ["brand_deep", bi, "top_topics", j, "neg_pct"], "pct")}</span></td>'
            f'<td><span class="negpill {neg_pill(t["weighted_neg_pct"])}">{o.num("metrics", ["brand_deep", bi, "top_topics", j, "weighted_neg_pct"], "pct")}</span></td></tr>'
            for j, t in enumerate(b["top_topics"]))
        bul = {"강점": [], "약점": []}
        for l in lines:
            mm = bullet_re.match(l.strip())
            if mm:
                text = mm.group(2)
                q = QUOTE.search(text)
                main = text[:text.rfind(">")].strip() if q and ">" in text else text
                claim, rest = split_claim(main)
                bul[bmap[mm.group(1)]].append({"claim": claim, "body": rest, "quotes": [q.groups()] if q else []})
        sw = ""
        for kind, cls in (("강점", "g"), ("약점", "r")):
            inner = "".join(
                f'<div class="icard"><span class="iclaim {cls}">{md(x["claim"])}</span><div class="ibody">{link(md(x["body"]), brand=bn)}</div>'
                f'<div class="chips">{"".join(quote_chip(q, cls) for q in x["quotes"])}</div></div>' for x in bul[kind])
            sw += f'<div class="swcol"><div class="swh {cls}">{esc(T("{b}: {k}", b=bn, k=T(kind)))}</div>{inner or "<div class=fn>" + esc(T("근거 부족")) + "</div>"}</div>'
        h10 = [T("주제"), T("언급"), T("긍정"), T("부정")] + ([T("혼합"), T("중립")] if b["top_topics"] and "mixed" in b["top_topics"][0] else [])             + [T("부정 비율"), T("가중 부정 비율")]
        panes += (f'<div class="bpane{" on" if bi == 0 else ""}" id="bp{bi}"><div class="bname">{esc(bn)} '
                  f'<span class="badge clk"{drill_attr({"brand": bi}, bn, b["reviews"])}>{T("리뷰 {n}개", n=o.num("metrics", ["brand_deep", bi, "reviews"], "int"))}</span>'
                  f'</div><div class="bmeta">{" / ".join(b["asins"])}</div><div class="coltitle">{esc(T("주제 평가(언급 상위 8개, 전체 만족도 제외)"))}</div>'
                  '<div class="tscroll"><table class="ct"><thead><tr>' + "".join(f'<th{" class=tl" if j == 0 else ""}>{esc(h)}</th>' for j, h in enumerate(h10))
                  + f'</tr></thead><tbody>{trs}</tbody></table></div>{reading_html(readings(lines), lambda h, bn=bn: link(h, brand=bn))}'
                  f'<div class="swgrid">{sw}</div></div>')
    body = f'<div class="btabs">{tabs}</div>{panes}'
    parts.append(section(10, CH[10], T("브랜드 버튼을 누르면 그 브랜드의 주제 평가와 강점, 약점(세부 이슈 개수는 그 브랜드 안 리뷰 수)"), body))

    # 11장 변형 신호
    vs = m["variant_signal"]
    blocks = ""
    for ai, a in enumerate(vs["asins"]):
        bn = m["brand_of_asin"].get(a["asin"], a["asin"])
        heads = "".join(f"<th>{esc(T('{t} 부정 비율', t=name[t]))}</th>" for t in a["topics"])
        trs = ""
        for ri, r in enumerate(a["rows"]):
            f = {"asin": a["asin"], "vlabel": r["variant"]}
            tds = "".join(f'<td>{o.num("metrics", ["variant_signal", "asins", ai, "rows", ri, "neg_reviewer_pct", t], "pct")}</td>' for t in a["topics"])
            price = (o.num("metrics", ["variant_signal", "asins", ai, "rows", ri, "price"], "usd") if r["price"] is not None else "-")
            ppo = (o.num("metrics", ["variant_signal", "asins", ai, "rows", ri, "price_per_oz"], "usd") if r["price_per_oz"] is not None else "-")
            trs += (f'<tr><td class="tl"><b>{esc(r["variant"])}</b><div class="mono mut">{r["variant_asin"]}</div></td>'
                    f'<td class="clk"{drill_attr(f, T("{b} {v}", b=bn, v=r["variant"]), r["reviews"])}>{o.num("metrics", ["variant_signal", "asins", ai, "rows", ri, "reviews"], "int")}</td>'
                    f'<td>{price}</td><td>{ppo}</td>{tds}</tr>')
        hidden = f'<div class="fn">{esc(T("태그가 적어 숨긴 변형: {v}", v=", ".join(a["hidden_low_tags"])))}</div>' if a["hidden_low_tags"] else ""
        blocks += (f'<div class="coltitle" style="margin-top:14px">{esc(bn)} <span class="mono mut">{a["asin"]}</span></div><div class="tscroll"><table class="ct">'
                   f'<thead><tr><th class="tl">{esc(T("용량"))}</th><th>{esc(T("리뷰"))}</th><th>{esc(T("현재 가격"))}</th><th>{esc(T("온스당 가격"))}</th>{heads}</tr></thead><tbody>{trs}</tbody></table></div>{hidden}')
    body = (blocks + '<div class="fn">' + T("부정 비율은 그 용량 리뷰 가운데 그 주제를 부정으로 말한 리뷰의 가중 비율입니다. 같은 ASIN 안에서만 비교하고, 가격은 {d}에 조회한 현재 가격입니다. 리뷰 수가 적은 용량은 순위로 읽지 않습니다.",
                                            d=o.num("metrics", ["variant_signal", "checked_on"], "raw")) + '</div>'
            + reading_html(readings(ch[11]), link))
    parts.append(section(11, CH[11], T("같은 ASIN 안 용량별 부정 비율과 온스당 가격(리뷰 15개 이상인 용량)"), body, new=True))

    # 12장 리뷰 탐색기
    opt = lambda pairs_: "".join(f'<option value="{esc(v)}">{esc(t)}</option>' for v, t in pairs_)
    lab_opts = [(i, T("{t} {d}: {l}", t=D["subs"][l[0]], d=T("부정") if l[1] else T("긍정"), l=l[2])) for i, l in enumerate(D["labels"])]
    body = ('<div class="xbar">'
            f'<select id="xb" aria-label="{esc(T("브랜드"))}"><option value="">{esc(T("브랜드 전체"))}</option>{opt(list(enumerate(D["brands"])))}</select>'
            f'<select id="xs" aria-label="{esc(T("주제"))}"><option value="">{esc(T("주제 전체"))}</option>{opt(list(enumerate(D["subs"])))}</select>'
            f'<select id="xe" aria-label="{esc(T("감성"))}"><option value="">{esc(T("감성 전체"))}</option>{opt(list(enumerate(SENTL)))}</select>'
            f'<select id="xl" aria-label="{esc(T("세부 이슈"))}"><option value="">{esc(T("세부 이슈 전체"))}</option>{opt(lab_opts)}</select>'
            f'<select id="xst" aria-label="{esc(T("별점"))}"><option value="">{esc(T("별점 전체"))}</option>{opt([(s, f"{s}★") for s in range(1, 6)])}</select>'
            f'<select id="xy" aria-label="{esc(T("기간"))}"><option value="">{esc(T("기간 전체"))}</option>{opt([(i, p[0]) for i, p in enumerate(D["periods"])])}</select>'
            f'<select id="xv" aria-label="{esc(T("구매 확인"))}"><option value="">{esc(T("구매 확인 전체"))}</option><option value="1">{esc(T("확인된 구매"))}</option><option value="0">{esc(T("확인 안 된 구매"))}</option></select>'
            f'<input id="xq" type="search" placeholder="{esc(T("본문 검색(원문)"))}" aria-label="{esc(T("본문 검색"))}"><button class="btab" onclick="xReset()">{esc(T("초기화"))}</button></div>'
            '<div class="xstat" id="xstat"></div><div id="xres"></div>')
    parts.append(section(12, CH[12], T("모든 리뷰를 걸러 원문을 읽습니다. 위 장의 숫자를 여기서 다시 확인할 수 있습니다"), body, new=True))

    # 13장 전략
    gk = {LG.marker("product"): "제품", LG.marker("branding"): "브랜딩"}
    groups, cur = {"제품": [], "브랜딩": []}, None
    for l in ch[12]:
        if l.startswith("### "):
            cur = gk.get(l[4:].strip())
            continue
        if cur in groups:
            groups[cur].append(l)
    tabs, panes = "", ""
    for gi, (g, lines) in enumerate(groups.items()):
        items = numbered_items(lines)
        tabs += f'<button class="btab{" on" if gi == 0 else ""}" id="st{gi}" onclick="showTab(\'s\',{gi})">{esc(T(g))}</button>'
        inner, k = "", 0
        for x in items:
            if "para" in x:
                inner += f'<div class="fn" style="margin:4px 0 12px">{link(md(x["para"]))}</div>'
                continue
            k += 1
            chips = "".join(quote_chip(q, "g") for q in x["quotes"])
            inner += (f'<div class="stgy"><span class="n">{k}</span><div><b>{md(x["claim"])}</b><p>{link(md(x["body"]))}</p>'
                      f'{f"<div class={chr(39)}chips{chr(39)} style={chr(39)}margin-top:6px{chr(39)}>{chips}</div>" if chips else ""}</div></div>')
        panes += f'<div class="bpane{" on" if gi == 0 else ""}" id="sp{gi}">{inner}</div>'
    body = f'<div class="btabs">{tabs}</div>{panes}'
    parts.append(section(13, CH[13], T("위 데이터에서 나온 할 일(괄호는 근거가 나온 장). 제품과 브랜딩 탭"), body))

    # 주의 사항(부록)
    app = [l[2:].strip() for l in ch.get("appendix", []) if l.startswith("- ")]
    caveat = (f'<div class="caveat"><b>{esc(T("주의 사항(방법과 한계)"))}</b><ul>' + "".join(f"<li>{link(md(x))}</li>" for x in app)
              + f'<li>{esc(T("안전 판정: 안전 주제로 태깅된 인용 전부를 상위 모델이 원문과 대조해 이상 반응 여부와 종류를 정했습니다(07c_safety_check.md)."))}</li></ul></div>')
    parts.append(caveat)
    parts.append(f'<div class="fn" style="text-align:center;margin:20px 0 40px">'
                 + esc(T("만든 날 {d}(v1 HTML, {ed}), 회차 {r}. 원본: 02_reviews.csv(리뷰 {n}개), 04_tags.jsonl(태그 {t}개), 05_metrics.json, 07b_issue_counts.json, 07c_safety_summary.json, {md}",
                         d=now_iso()[:10], ed=T("한국어판"), r=run.name, n=f_int(S["reviews"]), t=f_int(S["tags"]), md=md_name)) + '</div>')

    ui = LG.ui()
    toc = "".join(f'<a href="#sec{n}" id="nav{n}"><span class="tn">{n}</span>{esc(t)}</a>' for n, t in LG.chapters())
    data_js = json.dumps(D, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
    page = (TEMPLATE.replace("%TITLE%", esc(LG.title())).replace("%TOC%", toc).replace("%BODY%", "\n".join(parts))
            .replace("%DATA%", data_js).replace("%SENTKO%", json.dumps(list(SENTL), ensure_ascii=False))
            .replace("%UI%", json.dumps(ui, ensure_ascii=False)).replace("%LANG%", lang)
            .replace("%TOCT%", esc(T("목차"))))
    for k, v in ui.items():
        page = page.replace(f"%UI_{k}%", esc(v))
    for k, v in enumerate(SENTL):
        page = page.replace(f"%SENT{k}%", esc(v))
    out_name = "06_report.html" if lang == "ko" else f"06_report_{lang}.html"
    num_name = "06_report_html_numbers.json" if lang == "ko" else f"06_report_{lang}_html_numbers.json"
    (run / out_name).write_text(page, encoding="utf-8")
    write_json(run / num_name, {"made_at": now_iso(), "lang": lang, "numbers": o.nums, "link_misses": link.misses,
                                "missing_strings": sorted(LG.missing)})
    size = (run / out_name).stat().st_size
    print(f"{out_name}을 만들었습니다({size / 1024:.0f}KB, 리뷰 {len(D['R'])}개, 태그 {len(D['T'])}개, 라벨 연결 {len(D['L'])}개, 화면 숫자 {len(o.nums)}개).")
    for x in link.misses:
        print(f"  주의: 문장 속 개수를 연결하지 못함: {x}")
    for x in sorted(LG.missing):
        print(f"  주의: 영어 문구가 없음: {x}")
    return 1 if (lang != "ko" and LG.missing) else 0


# ---------------------------------------------------------------- 검사

def extract_data(page):
    m = re.search(r"const D=(\{.*?\});\n", page, re.S)
    if not m:
        die("06_report.html에서 const D를 찾지 못했습니다.")
    return json.loads(m.group(1).replace("<\\/", "</"))


def py_match(D, f):
    """화면의 matchReviews와 같은 필터(드릴다운 대조용)."""
    tby = defaultdict(list)
    for ti, t in enumerate(D["T"]):
        tby[t[0]].append((ti, t))
    lby = defaultdict(set)
    for ti, li in D["L"]:
        lby[D["T"][ti][0]].add(li)
    rset = set(f["rids"]) if "rids" in f else None
    out = []
    for ri, r in enumerate(D["R"]):
        if rset is not None and ri not in rset:
            continue
        if "brand" in f and r[9] != f["brand"]:
            continue
        if "asin" in f and r[1] != f["asin"]:      # 같은 브랜드에 상품이 둘 이상일 때 9장은 상품(ASIN)으로 거른다
            continue
        if "star" in f and r[3] != f["star"]:
            continue
        if "dfrom" in f and r[6] < f["dfrom"]:
            continue
        if "dto" in f and r[6] > f["dto"]:
            continue
        if "verified" in f and r[7] != f["verified"]:
            continue
        if "vine" in f and r[12] != f["vine"]:
            continue
        if "hv" in f and r[8] < f["hv"]:
            continue
        if "asin" in f and r[1] != f["asin"]:
            continue
        if "vlabel" in f and r[13] != f["vlabel"]:
            continue
        if "label" in f and f["label"] not in lby[ri]:
            continue
        if "labels" in f and not all(x in lby[ri] for x in f["labels"]):
            continue
        tg = [t for _, t in tby[ri]]
        if "pair" in f:
            if not (any(t[1] == f["pair"][0] and t[2] == 1 for t in tg) and any(t[1] == f["pair"][1] and t[2] == 1 for t in tg)):
                continue
        elif "pairPos" in f:
            if not (any(t[1] == f["pairPos"][0] and t[2] == 0 for t in tg) and any(t[1] == f["pairPos"][1] and t[2] == 0 for t in tg)):
                continue
        elif "sub" in f:
            if not any(t[1] == f["sub"] and ("sent" not in f or t[2] == f["sent"]) for t in tg):
                continue
        elif "sent" in f:
            if not any(t[2] == f["sent"] for t in tg):
                continue
        out.append(ri)
    return out


def visible_text(page):
    """우리가 쓴 화면 글자: const D(리뷰 원문, 변형 텍스트)와 스크립트, 태그를 뺀 글자."""
    body = re.sub(r"<script>.*?</script>", "", page, flags=re.S)
    body = re.sub(r"<style>.*?</style>", "", body, flags=re.S)
    return html.unescape(re.sub(r"<[^>]+>", " ", body))


def check(run, lang="ko"):
    global LG
    LG = Lang(lang, run)
    FMT["usd"] = f_usd if lang == "ko" else (lambda v: f"${float(v):.2f}")
    FMT["raw"] = (lambda v: LG.raw(v))
    html_name = "06_report.html" if lang == "ko" else f"06_report_{lang}.html"
    page = (run / html_name).read_text(encoding="utf-8")
    numbers = json.loads((run / ("06_report_html_numbers.json" if lang == "ko" else f"06_report_{lang}_html_numbers.json")).read_text(encoding="utf-8"))
    src = {"metrics": json.loads((run / "05_metrics.json").read_text(encoding="utf-8")),
           "counts": json.loads((run / "07b_issue_counts.json").read_text(encoding="utf-8")),
           "safety": json.loads((run / "07c_safety_summary.json").read_text(encoding="utf-8"))}
    D = extract_data(page)
    errors, warns = [], []

    # 1. 숫자 대조
    spans = dict(re.findall(r'<span data-k="(n\d+)"[^>]*>(.*?)</span>', page))
    for e in numbers["numbers"]:
        try:
            want = FMT[e["fmt"]](resolve(src[e["src"]], e["path"]))
        except (KeyError, IndexError, ValueError) as ex:
            errors.append(f"숫자 {e['k']}: JSON 경로 {e['src']}:{'.'.join(map(str, e['path']))}를 읽지 못함({ex})")
            continue
        got = html.unescape(spans.get(e["k"], "\x00없음"))
        if got != want:
            errors.append(f"숫자 {e['k']} {e['src']}:{'.'.join(map(str, e['path']))}: 화면 '{got}', JSON '{want}'")
    if len(spans) != len(numbers["numbers"]):
        errors.append(f"화면의 숫자 칸 {len(spans)}개와 기록 {len(numbers['numbers'])}개가 다릅니다.")
    for x in numbers.get("link_misses", []):
        errors.append(f"문장 속 세부 이슈 개수가 07b와 달라 연결하지 못함: {x}")

    # 2. 드릴다운 대조
    drills = 0
    counts = src["counts"]
    asins_of_brand = {i: b["asins"] for i, b in enumerate(src["metrics"]["brand_deep"])}
    verdicts = ((load_yaml(run / "07c_safety_verdicts.yaml") or {}).get("audit") or {}).get("verdicts") or []
    rid = {r[0]: i for i, r in enumerate(D["R"])}
    neg_safety = {D["R"][t[0]][0] for t in D["T"] if D["sid"][t[1]] == "safety" and t[2] == 1}
    for mt in re.finditer(r'data-f="([^"]*)" data-t="([^"]*)" onclick="drillEl\(this\)" tabindex="0" data-n="(\d+)"', page):
        f = json.loads(html.unescape(mt.group(1)))
        title, n = html.unescape(mt.group(2)), int(mt.group(3))
        drills += 1
        got = len(py_match(D, f))
        if got != n:
            errors.append(f"드릴다운 '{title}' {f}: 화면 {n}개, 필터 결과 {got}개")
        if "label" in f:
            lab = D["labels"][f["label"]]
            key = f"{D['sid'][lab[0]]}.{'negative' if lab[1] else 'positive'}"
            row = next(l for l in counts["topics"][key]["labels"] if l["id"] == lab[3])
            want = row["reviews"] if "brand" not in f else sum(row["by_asin"].get(a, 0) for a in asins_of_brand[f["brand"]])
            if want != n:
                errors.append(f"라벨 드릴다운 '{title}': 화면 {n}개, 07b {want}개")
        if "rids" in f:
            name = title.split(": ", 1)[-1]
            want = {rid[str(v["review_id"])] for v in verdicts
                    if LG.sym(v.get("symptom_type") or "") == name and str(v["review_id"]) in neg_safety}       # 화면 제목은 언어판 이름
            if set(f["rids"]) != want:
                errors.append(f"안전 증상 드릴다운 '{title}': 리뷰 목록이 07c 판정과 다릅니다.")
        if page[max(0, mt.start() - 30):mt.start()].endswith('<span class="lnk"'):      # 문장 속 링크는 글자에 그 숫자가 있어야 한다
            inner = html.unescape(re.sub(r"<[^>]+>", "", page[mt.end():page.find("</span>", page.find(">", mt.end()) + 1) + 400]))[:80]
            if not re.search(rf"(?<![\d,]){re.escape(f_int(n))}개|(?<![\d,]){n}개", inner):
                errors.append(f"드릴다운 링크 '{title}': 글자에 {n}개가 없습니다.")

    # 3. 한 파일
    no_data = re.sub(r"const D=\{.*?\};\n", "", page, flags=re.S)
    ext = re.findall(r"(?:src|href)\s*=\s*[\"']?(https?://[^\"' >]+)", no_data) + re.findall(r"url\(\s*['\"]?(https?://[^)'\"]+)", no_data) \
        + re.findall(r"@import[^;]*https?://", no_data)
    if ext:
        errors.append(f"외부 참조 {len(ext)}개: {ext[:3]}")
    stray = [u for u in re.findall(r"https?://\S+", visible_text(no_data))]
    if stray:
        warns.append(f"화면 글자 안 주소 {len(stray)}개(외부 참조 아님): {stray[:3]}")
    vt = visible_text(page)
    dots = [vt[max(0, i - 20):i + 20] for i, c in enumerate(vt) if c == "·"]
    if dots:
        errors.append(f"우리가 쓴 화면 글자에 가운뎃점 {len(dots)}개: {dots[:3]}")
    js = "".join(re.findall(r"<script>(.*?)</script>", no_data, flags=re.S))
    if "·" in js:
        errors.append("스크립트가 화면에 쓰는 글자에 가운뎃점이 있습니다.")
    hangul = []
    if lang != "ko":
        errors += [f"영어 문구가 없음: {x}" for x in numbers.get("missing_strings", [])]
        cards = re.sub(r'<span class="chip[^>]*>.*?</span></span>|<td class="tl">[^<]*</td>', " ", no_data, flags=re.S)
        vt2 = visible_text(cards) + " " + "".join(re.findall(r"<script>(.*?)</script>", no_data, flags=re.S))
        hangul = sorted({vt2[max(0, i - 15):i + 15].strip() for i in [mt.start() for mt in re.finditer(r"[가-힣]", vt2)]})
        if hangul:
            errors.append(f"영어판에 한글이 남음 {len(hangul)}곳: {hangul[:5]}")

    status = "FAIL" if errors else "PASS"
    out = {"checked_at": now_iso(), "status": status, "numbers_checked": len(numbers["numbers"]), "drilldowns_checked": drills,
           "external_refs": len(ext), "middle_dots": len(dots), "size_kb": round((run / "06_report.html").stat().st_size / 1024),
           "errors": errors, "warnings": warns}
    out["hangul_left"] = len(hangul)
    write_json(run / ("06_report_html_check.json" if lang == "ko" else f"06_report_{lang}_html_check.json"), out)
    print(f"HTML 검사: {status}  (숫자 대조 {out['numbers_checked']}개, 드릴다운 대조 {drills}개, 외부 참조 {len(ext)}개, 가운뎃점 {len(dots)}개)")
    for e in errors[:30]:
        print(f"  오류: {e}")
    for w in warns[:10]:
        print(f"  주의: {w}")
    return 1 if errors else 0


# ---------------------------------------------------------------- 틀

TEMPLATE = r"""<!doctype html>
<html lang="%LANG%">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>%TITLE%</title>
<style>
:root{--bg:#f7f7f5;--card:#fff;--fg:#37352f;--sub:#5a5852;--mut:#787774;--faint:#9b9a97;--line:#e6e6e3;--line2:#f1f1ef;--soft:#fbfbfa;--hover:#f3f6fa;
--pos:#2e9e5b;--neg:#d64550;--mix:#e3a33b;--neu:#b9b8b4;--prod:#3f7fbf;--brandc:#8a7ad6;--accent:#2f4467;
--pos-fg:#1f7a43;--neg-fg:#c4233c;--mix-fg:#b06b00;--pos-bg:#e7f6ec;--neg-bg:#fdebed;--mix-bg:#fdf3e3;--read-bg:#f6f8fb;--read-line:#7a9cc6;--mark:#ffe98a;
--f:'Apple SD Gothic Neo','Noto Sans KR','Malgun Gothic','Segoe UI',-apple-system,'Helvetica Neue',Arial,sans-serif}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){--bg:#191918;--card:#222221;--fg:#e8e7e4;--sub:#c5c4bf;--mut:#9d9c97;--faint:#85847f;--line:#34332f;--line2:#2c2b28;--soft:#262624;--hover:#27303b;
--pos:#3fb071;--neg:#e0606a;--mix:#e3a33b;--neu:#6f6e6a;--prod:#5b97d4;--brandc:#9d8fe0;--accent:#9db6de;
--pos-fg:#6fd39a;--neg-fg:#f08a92;--mix-fg:#f0b957;--pos-bg:#173524;--neg-bg:#3a1c20;--mix-bg:#3a2d15;--read-bg:#1f2630;--read-line:#5f7fa8;--mark:#6b5a12;color-scheme:dark}}
:root[data-theme="dark"]{--bg:#191918;--card:#222221;--fg:#e8e7e4;--sub:#c5c4bf;--mut:#9d9c97;--faint:#85847f;--line:#34332f;--line2:#2c2b28;--soft:#262624;--hover:#27303b;
--pos:#3fb071;--neg:#e0606a;--mix:#e3a33b;--neu:#6f6e6a;--prod:#5b97d4;--brandc:#9d8fe0;--accent:#9db6de;
--pos-fg:#6fd39a;--neg-fg:#f08a92;--mix-fg:#f0b957;--pos-bg:#173524;--neg-bg:#3a1c20;--mix-bg:#3a2d15;--read-bg:#1f2630;--read-line:#5f7fa8;--mark:#6b5a12;color-scheme:dark}
*{box-sizing:border-box}
body{font-family:var(--f);background:var(--bg);color:var(--fg);margin:0;padding-block:32px;padding-inline:16px;font-size:14px;word-break:keep-all;overflow-wrap:anywhere}
.page{max-width:980px;margin:0 auto}
h1{font-size:26px;margin:0 0 10px}
.toci{display:flex;flex-wrap:wrap;gap:4px 14px;font-size:12px;margin:0 0 10px}
.toci a{color:var(--sub);text-decoration:none}.toci a b{color:var(--faint);margin-right:4px;font-weight:600}
.kpis{display:flex;flex-wrap:wrap;gap:8px;margin:14px 0 6px}
.kpi{background:var(--card);border:1px solid var(--line);border-radius:8px;padding:10px 14px;min-width:108px;max-width:100%}
.kpi .v{font-size:20px;font-weight:700;font-variant-numeric:tabular-nums}.kpi .l{font-size:11.5px;color:var(--mut)}
section{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:20px 22px;margin:18px 0;min-width:0}
h2{font-size:17px;margin:0 0 4px;display:flex;align-items:center;gap:8px;flex-wrap:wrap}
h2 .num{background:var(--fg);color:var(--card);border-radius:5px;font-size:11px;padding:2px 7px}
.newtag{font-size:9px;background:var(--accent);color:var(--card);border-radius:4px;padding:2px 6px}
.sub{color:var(--mut);font-size:12.5px;margin:0 0 16px}
.cols{display:flex;gap:24px;flex-wrap:wrap}.col{flex:1;min-width:min(300px,100%)}
.coltitle{font-size:13px;font-weight:700;margin-bottom:10px;color:var(--sub)}
.donutwrap{display:flex;align-items:center;gap:18px;flex-wrap:wrap}
.donut{width:150px;height:150px;border-radius:50%;position:relative;flex:none}
.hole{position:absolute;inset:30px;background:var(--card);border-radius:50%;display:flex;flex-direction:column;align-items:center;justify-content:center}
.hv{font-weight:700;font-size:17px}.hl{font-size:10.5px;color:var(--mut)}
.legend{font-size:12.5px;display:flex;flex-direction:column;gap:5px}
.lg .dot{display:inline-block;width:9px;height:9px;border-radius:2px;margin-right:6px}
.mut{color:var(--faint)}
.bhead,.brow{display:flex;align-items:center;gap:8px;margin:5px 0;font-size:12.5px}
.blab{width:200px;flex:none;text-align:right;color:var(--sub)}
.btrack{flex:1;background:var(--line2);border-radius:4px;height:16px;overflow:hidden;font-size:11px;color:var(--mut)}
.bbar{display:flex;height:100%;border-radius:4px;overflow:hidden}.bbar span{display:block;height:100%}
.bn{width:48px;flex:none;text-align:right;font-variant-numeric:tabular-nums}
.bneg{width:52px;flex:none;text-align:right;color:var(--neg-fg);font-weight:600;font-variant-numeric:tabular-nums}
.tcat{font-size:9.5px;font-weight:700;border-radius:4px;padding:1px 5px;flex:none}
.tb{background:color-mix(in srgb,var(--brandc) 18%,transparent);color:var(--brandc)}.tp{background:color-mix(in srgb,var(--prod) 15%,transparent);color:var(--prod)}
.tscroll{overflow-x:auto}
table.ct{border-collapse:collapse;width:100%;font-size:12.5px}
.ct th{background:var(--soft);border-bottom:1px solid var(--line);padding:7px 8px;font-weight:600;color:var(--sub);text-align:center;white-space:nowrap}
.ct td{border-bottom:1px solid var(--line2);padding:6px 8px;text-align:center;font-variant-numeric:tabular-nums}
.ct .tl{text-align:left}
.mono{font-family:ui-monospace,Menlo,Consolas,monospace;font-size:11.5px}
.cpos{color:var(--pos-fg);font-weight:600}.cneg{color:var(--neg-fg);font-weight:600}
.negpill{border-radius:10px;padding:2px 9px;font-weight:700;font-size:11.5px;white-space:nowrap}
.negpill.hi{background:var(--neg-bg);color:var(--neg-fg)}.negpill.mid{background:var(--mix-bg);color:var(--mix-fg)}.negpill.lo{background:var(--pos-bg);color:var(--pos-fg)}
.small{font-size:11.5px}
.minibar{display:flex;height:9px;width:120px;border-radius:4px;overflow:hidden;background:var(--line2);margin:0 auto 3px}.minibar span{display:block;height:100%}
.svgwrap{overflow-x:auto}
svg.imp{width:100%;min-width:620px;height:auto;display:block}
svg.imp .gl{stroke:var(--line2)} svg.imp .ax{fill:var(--mut);font-size:11px;font-family:var(--f)}
svg.imp .lb{fill:var(--sub);font-size:12px;font-family:var(--f)}
svg.imp .dotneg{fill:var(--neg);fill-opacity:.55;stroke:var(--card);stroke-width:2}
svg.imp g.clk:hover .dotneg{fill-opacity:.9}
.tchart{display:flex;gap:10px;align-items:flex-end;flex-wrap:wrap}
.tcol{flex:1;display:flex;flex-direction:column;align-items:center;gap:3px;font-size:11px;color:var(--mut);min-width:110px}
.tstack{width:70%;height:110px;display:flex;flex-direction:column-reverse;background:var(--line2);border-radius:4px;overflow:hidden}
.tstack span{display:block;width:100%}
.tv{font-size:11.5px;white-space:nowrap}.ty{font-weight:700;color:var(--sub)}
.tcol.clk:hover .tstack{outline:2px solid var(--read-line)}
.swgrid{display:flex;gap:18px;flex-wrap:wrap;margin-top:14px}.swcol{flex:1;min-width:min(320px,100%)}
.swh{font-size:14px;font-weight:800;padding:7px 12px;border-radius:7px;margin-bottom:10px;display:inline-block}
.swh.g{background:var(--pos-bg);color:var(--pos-fg)}.swh.r{background:var(--neg-bg);color:var(--neg-fg)}
.icard{border:1px solid var(--line);border-radius:9px;padding:13px 15px;margin-bottom:11px;background:var(--card)}
.iclaim{font-weight:700;font-size:13.5px;line-height:1.45;display:inline;box-decoration-break:clone;-webkit-box-decoration-break:clone;padding:1px 4px;border-radius:3px}
.iclaim.g{background:var(--pos-bg);color:var(--pos-fg)}.iclaim.r{background:var(--neg-bg);color:var(--neg-fg)}
.ibody{font-size:12.5px;color:var(--sub);margin:8px 0 9px;line-height:1.65}
.chips{display:flex;flex-wrap:wrap;gap:6px}
.chip{font-size:11.5px;border-radius:12px;padding:3px 10px;line-height:1.5}
.chip em{font-style:normal;opacity:.65;margin-left:6px;font-size:10.5px}
.chip.g{background:var(--pos-bg);color:var(--pos-fg);border:1px solid color-mix(in srgb,var(--pos) 30%,transparent)}
.chip.r{background:var(--neg-bg);color:var(--neg-fg);border:1px solid color-mix(in srgb,var(--neg) 30%,transparent)}
.chip.clk:hover{box-shadow:0 0 0 1.5px currentColor}
.lnk{cursor:pointer;text-decoration:underline dotted;text-underline-offset:3px;font-weight:600;color:var(--accent)}
.lnk:hover{background:var(--hover)}
.bname{font-size:15.5px;font-weight:800;display:flex;align-items:center;gap:10px;margin:14px 0 3px;flex-wrap:wrap}
.bmeta{font-size:12px;color:var(--mut);margin-bottom:12px;font-family:ui-monospace,Menlo,Consolas,monospace}
.badge{font-size:10.5px;background:var(--line2);border-radius:10px;padding:2px 9px;color:var(--sub);font-weight:600}
.stgy{display:flex;gap:12px;align-items:flex-start;border:1px solid var(--line);border-radius:9px;padding:13px 15px;margin-bottom:10px;background:var(--card)}
.stgy .n{flex:none;width:24px;height:24px;border-radius:50%;background:var(--fg);color:var(--card);font-size:12px;font-weight:700;display:flex;align-items:center;justify-content:center}
.stgy b{font-size:13.5px}.stgy p{margin:4px 0 0;font-size:12.5px;color:var(--sub);line-height:1.65}
.caveat{font-size:11.5px;color:var(--mut);background:var(--soft);border:1px solid var(--line);border-radius:8px;padding:11px 14px;line-height:1.7}
.caveat b{color:var(--sub)}.caveat ul{margin:7px 0 0;padding-left:17px;display:flex;flex-direction:column;gap:4px}
.fn{font-size:11.5px;color:var(--faint);margin-top:6px;line-height:1.6}
.stardist{display:flex;gap:4px;align-items:flex-end;height:130px;margin-top:8px}
.stardist .sb{flex:1;display:flex;flex-direction:column;align-items:center;gap:3px;font-size:10.5px;color:var(--mut)}
.stardist .sbar{width:78%;border-radius:3px 3px 0 0}
.reading{background:var(--read-bg);border-left:3px solid var(--read-line);border-radius:0 8px 8px 0;padding:10px 14px;margin-top:14px;font-size:12.5px;color:var(--sub);line-height:1.75}
.reading b{color:var(--accent)}.reading .rt{display:inline-block;font-weight:800;color:var(--accent);margin-right:6px}
.reading p{margin:6px 0 0}
.clk{cursor:pointer}
.brow.clk:hover{background:var(--hover);border-radius:6px}
.ct tr.clk:hover,.ct td.clk:hover{background:var(--hover)}
.kpi.clk:hover,.badge.clk:hover{border-color:var(--read-line);outline:1px solid var(--read-line)}
.lg.clk:hover{text-decoration:underline}
.dtl{margin-top:6px}.dtl summary{cursor:pointer;color:var(--sub)}
#ovl{position:fixed;inset:0;background:rgba(20,20,18,.45);display:none;z-index:50;align-items:flex-start;justify-content:center;padding:30px 12px;overflow:auto}
#ovl.on{display:flex}
#mbox{background:var(--card);border-radius:12px;max-width:780px;width:100%;max-height:86vh;display:flex;flex-direction:column;box-shadow:0 12px 40px rgba(0,0,0,.25)}
#mhead{padding:13px 18px;border-bottom:1px solid var(--line);display:flex;align-items:center;gap:10px;flex-wrap:wrap}
#mtitle{font-weight:800;font-size:14px}
.sfcs{display:flex;gap:5px;flex-wrap:wrap}
#mclose{margin-left:auto;cursor:pointer;border:none;background:var(--line2);color:var(--fg);border-radius:6px;padding:5px 12px;font-size:12px;font-family:inherit}
#mbody{overflow:auto;padding:12px 18px}
.sfc{font-size:11px;border:1px solid var(--line);border-radius:12px;padding:2px 10px;cursor:pointer;background:var(--card);color:var(--fg);font-family:inherit}
.sfc.on{background:var(--fg);color:var(--card);border-color:var(--fg)}
.rcard{border:1px solid var(--line);border-radius:9px;padding:11px 13px;margin-bottom:10px;background:var(--card)}
.rhead{display:flex;gap:8px;align-items:center;font-size:11.5px;color:var(--mut);flex-wrap:wrap}
.rbrand{font-weight:700;color:var(--fg)}.rstar{font-weight:800}
.rtitle{font-weight:700;font-size:13px;margin:6px 0 4px}
.rbody{font-size:12.5px;color:var(--sub);line-height:1.6;display:-webkit-box;-webkit-line-clamp:4;-webkit-box-orient:vertical;overflow:hidden;cursor:pointer}
.rbody.open{display:block;-webkit-line-clamp:unset}
.rtags{display:flex;gap:5px;flex-wrap:wrap;margin-top:7px}
.rtg{font-size:10.5px;border-radius:10px;padding:2px 8px}
.rtg.s0{background:var(--pos-bg);color:var(--pos-fg)}.rtg.s1{background:var(--neg-bg);color:var(--neg-fg)}.rtg.s2{background:var(--mix-bg);color:var(--mix-fg)}.rtg.s3{background:var(--line2);color:var(--sub)}
mark.hlt{background:var(--mark);color:inherit;border-radius:2px;padding:0 1px}
.morebtn{display:block;margin:8px auto;padding:6px 18px;border:1px solid var(--line);border-radius:8px;background:var(--card);color:var(--fg);cursor:pointer;font-size:12px;font-family:inherit}
.xbar{display:flex;gap:8px;flex-wrap:wrap;margin:10px 0;align-items:center}
.xbar select,.xbar input{font-size:12px;padding:5px 8px;border:1px solid var(--line);border-radius:7px;background:var(--card);color:var(--fg);font-family:inherit;max-width:100%}
.xstat{font-size:12.5px;color:var(--sub);margin:8px 0;display:flex;gap:16px;flex-wrap:wrap;align-items:baseline}
.xstat b{font-size:15px;color:var(--fg)}
.btabs{display:flex;gap:8px;flex-wrap:wrap;margin:4px 0 2px}
.btab{font-size:12.5px;font-weight:700;padding:7px 14px;border:1px solid var(--line);border-radius:8px;background:var(--card);cursor:pointer;font-family:inherit;color:var(--sub)}
.btab:hover{border-color:var(--read-line)}.btab.on{background:var(--fg);color:var(--card);border-color:var(--fg)}
.btab .bn2{font-weight:400;opacity:.65;margin-left:5px;font-size:11px}
.bpane{display:none}.bpane.on{display:block}
.concl{margin:6px 0 12px;padding:9px 13px;border-left:3px solid var(--accent);background:var(--read-bg);border-radius:6px;font-size:14px;line-height:1.6}
.callout{display:flex;gap:12px;background:var(--read-bg);border:1px solid var(--line);border-radius:10px;padding:13px 16px;margin:12px 0 4px;font-size:12.5px}
.callout .cb b{font-size:13px;color:var(--accent)}
.callout ul{margin:6px 0 0;padding-left:18px;display:flex;flex-direction:column;gap:3px}
.callout li{line-height:1.6;color:var(--sub)}
button:focus-visible,a:focus-visible,select:focus-visible,input:focus-visible,.clk:focus-visible,.lnk:focus-visible{outline:2px solid var(--read-line);outline-offset:2px}
html{scroll-behavior:smooth;scroll-padding-top:18px}
#toc{position:fixed;left:14px;top:32px;width:200px;max-height:calc(100vh - 64px);overflow:auto;background:var(--card);border:1px solid var(--line);border-radius:10px;padding:12px 10px;font-size:12px;display:none;z-index:10}
#toc .tt{font-weight:800;font-size:11px;color:var(--faint);margin:0 0 8px 7px}
#toc a{display:flex;gap:7px;align-items:flex-start;color:var(--sub);text-decoration:none;padding:5px 7px;border-radius:6px;line-height:1.35}
#toc a:hover{background:var(--hover)}#toc a.on{background:var(--hover);color:var(--accent);font-weight:700}
#toc .tn{flex:none;background:var(--line2);color:var(--mut);border-radius:4px;font-size:9.5px;padding:1px 5px;margin-top:1px;min-width:14px;text-align:center}
#toc a.on .tn{background:var(--accent);color:var(--card)}
@media(min-width:1400px){#toc{display:block}.toci{display:none}}
@media(min-width:1240px) and (max-width:1399px){#toc{display:block}.toci{display:none}.page{margin-left:236px;margin-right:auto}}
@media(max-width:640px){.blab{width:118px}section{padding:16px 14px}.bn,.bneg{width:42px}h1{font-size:21px}}
@media(prefers-reduced-motion:reduce){html{scroll-behavior:auto}}
</style>
</head>
<body>
<nav id="toc" aria-label="%TOCT%"><div class="tt">%TOCT%</div>%TOC%</nav>
<div class="page">
%BODY%
</div>
<div id="ovl" onclick="closeM(event)"><div id="mbox" role="dialog" aria-modal="true" aria-labelledby="mtitle"><div id="mhead"><span id="mtitle"></span><span id="mcount" class="small mut"></span>
<span class="sfcs"><button class="sfc" data-s="" onclick="setSent('')">%UI_all%</button><button class="sfc" data-s="0" onclick="setSent('0')">%SENT0%</button><button class="sfc" data-s="1" onclick="setSent('1')">%SENT1%</button><button class="sfc" data-s="2" onclick="setSent('2')">%SENT2%</button><button class="sfc" data-s="3" onclick="setSent('3')">%SENT3%</button></span>
<button id="mclose" onclick="closeM()">%UI_close% ✕</button></div><div id="mbody"><div id="mlist"></div><button class="morebtn" id="mmore" onclick="renderChunk()"></button></div></div></div>
<script>
const D=%DATA%;
const SENTL=%SENTKO%;
const UI=%UI%;
const TBYR={};D.T.forEach((t,ti)=>{(TBYR[t[0]]=TBYR[t[0]]||[]).push(ti);});
const LBYT={};D.L.forEach(x=>{(LBYT[x[0]]=LBYT[x[0]]||[]).push(x[1]);});
const LBYR={};D.L.forEach(x=>{const ri=D.T[x[0]][0];(LBYR[ri]=LBYR[ri]||new Set()).add(x[1]);});
const RIDX={};D.R.forEach((r,i)=>{RIDX[r[0]]=i;});
const fmt=n=>n.toLocaleString('en-US');
function matchReviews(f){
  const out=[];const rs=f.rids?new Set(f.rids):null;
  for(let ri=0;ri<D.R.length;ri++){
    const r=D.R[ri];
    if(rs&&!rs.has(ri))continue;
    if(f.brand!=null&&r[9]!==f.brand)continue;
    if(f.asin!=null&&r[1]!==f.asin)continue;
    if(f.star!=null&&r[3]!==f.star)continue;
    if(f.dfrom!=null&&r[6]<f.dfrom)continue;
    if(f.dto!=null&&r[6]>f.dto)continue;
    if(f.verified!=null&&r[7]!==f.verified)continue;
    if(f.vine!=null&&r[12]!==f.vine)continue;
    if(f.hv!=null&&r[8]<f.hv)continue;
    if(f.asin!=null&&r[1]!==f.asin)continue;
    if(f.vlabel!=null&&r[13]!==f.vlabel)continue;
    const ls=LBYR[ri];
    if(f.label!=null&&!(ls&&ls.has(f.label)))continue;
    if(f.labels&&!f.labels.every(x=>ls&&ls.has(x)))continue;
    if(f.q&&!(r[4]+' '+r[5]).toLowerCase().includes(f.q))continue;
    const tg=(TBYR[ri]||[]).map(ti=>D.T[ti]);
    if(f.pair){if(!(tg.some(t=>t[1]===f.pair[0]&&t[2]===1)&&tg.some(t=>t[1]===f.pair[1]&&t[2]===1)))continue;}
    else if(f.pairPos){if(!(tg.some(t=>t[1]===f.pairPos[0]&&t[2]===0)&&tg.some(t=>t[1]===f.pairPos[1]&&t[2]===0)))continue;}
    else if(f.sub!=null){if(!tg.some(t=>t[1]===f.sub&&(f.sent==null||t[2]===f.sent)))continue;}
    else if(f.sent!=null){if(!tg.some(t=>t[2]===f.sent))continue;}
    out.push(ri);
  }
  out.sort((a,b)=>(D.R[b][8]-D.R[a][8])||(D.R[b][6]>D.R[a][6]?1:(D.R[b][6]<D.R[a][6]?-1:0)));
  return out;
}
function escH(s){return String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;').replace(/'/g,'&#39;');}
function hlText(s,ri,f){
  let e=escH(s);const seen=new Set();
  (TBYR[ri]||[]).forEach(ti=>{
    const t=D.T[ti];
    if(f){
      if(f.sub!=null&&t[1]!==f.sub)return;
      if(f.label!=null&&!(LBYT[ti]||[]).includes(f.label))return;
      if(f.labels&&!(LBYT[ti]||[]).some(x=>f.labels.includes(x)))return;
      if(f.rids&&D.subs[t[1]]!==D.subs[D.sid.indexOf('safety')])return;
    }
    const q=escH(t[3]);if(!q||seen.has(q))return;seen.add(q);
    const i=e.indexOf(q);if(i>=0)e=e.slice(0,i)+"<mark class='hlt'>"+q+"</mark>"+e.slice(i+q.length);
  });
  return e;
}
function card(ri,full,f){
  const r=D.R[ri];
  const scls=r[3]<=2?'cneg':(r[3]>=4?'cpos':'');
  const tags=(TBYR[ri]||[]).map(ti=>{const t=D.T[ti];const ls=(LBYT[ti]||[]).map(li=>D.labels[li][2]);
    return `<span class='rtg s${t[2]}' title='${SENTL[t[2]]}'>${escH(D.subs[t[1]])} ${SENTL[t[2]]}${ls.length?': '+escH(ls.join(', ')):''}</span>`;}).join('');
  const brand=r[9]>=0?escH(D.brands[r[9]]):'';
  return `<div class='rcard'><div class='rhead'><span class='rbrand'>${brand}</span><span class='rstar ${scls}'>${'★'.repeat(r[3])} ${r[3]}</span><span>${r[6]}</span>`+
    `<span class='mono'>${r[1]}${r[2]&&r[2]!==r[1]?' | '+UI.variant+' '+r[2]:''}</span>${r[11]?`<span>${escH(r[11])}</span>`:''}`+
    `${r[7]?`<span class='cpos'>${UI.verified}</span>`:`<span class='cneg'>${UI.unverified}</span>`}${r[12]?'<span>Vine</span>':''}${r[8]>0?`<span>${UI.helpful} ${r[8]}</span>`:''}<span class='mono'>${r[0]}</span></div>`+
    `<div class='rtitle'>${hlText(r[4],ri,f)}</div><div class='rbody${full?' open':''}' onclick='this.classList.toggle("open")'>${hlText(r[5],ri,f)}</div><div class='rtags'>${tags}</div></div>`;
}
let curF=null,curList=[],shown=0;
function renderChunk(){
  const box=document.getElementById('mlist');const next=curList.slice(shown,shown+30);
  box.insertAdjacentHTML('beforeend',next.map(ri=>card(ri,false,curF)).join(''));shown+=next.length;
  const mb=document.getElementById('mmore');mb.hidden=shown>=curList.length;mb.textContent=`${UI.more} (${shown}/${curList.length})`;
}
function drillEl(el){drill(JSON.parse(el.dataset.f),el.dataset.t);}
function drill(f,title){curF=Object.assign({},f);document.getElementById('mtitle').textContent=title;rerunDrill();document.getElementById('ovl').classList.add('on');document.getElementById('mclose').focus();}
function avgStar(list){let s=0;list.forEach(ri=>{s+=D.R[ri][3];});return list.length?(s/list.length).toFixed(2):'-';}
function rerunDrill(){
  curList=matchReviews(curF);shown=0;
  document.getElementById('mcount').innerHTML=`${UI.reviews} <b>${fmt(curList.length)}</b>${UI.count_suffix}, ${UI.sample_avg} ${avgStar(curList)}★`;
  document.querySelectorAll('.sfc').forEach(c=>c.classList.toggle('on',String(curF.sent??'')===c.dataset.s));
  document.getElementById('mlist').innerHTML='';renderChunk();
}
function setSent(s){if(curF==null)return;curF.sent=s===''?null:parseInt(s);rerunDrill();}
function openRev(rid){
  const ri=RIDX[rid];if(ri==null)return;curF=null;
  document.getElementById('mtitle').textContent=UI.full;document.getElementById('mcount').innerHTML='';
  document.querySelectorAll('.sfc').forEach(c=>c.classList.remove('on'));
  document.getElementById('mlist').innerHTML=card(ri,true,null);document.getElementById('mmore').hidden=true;
  document.getElementById('ovl').classList.add('on');curList=[];shown=0;document.getElementById('mclose').focus();
}
function closeM(e){if(e&&e.target!==e.currentTarget)return;document.getElementById('ovl').classList.remove('on');}
document.addEventListener('keydown',e=>{
  if(e.key==='Escape')closeM();
  if((e.key==='Enter'||e.key===' ')&&e.target.matches&&e.target.matches('[data-f],[onclick].clk,.chip')){e.preventDefault();e.target.click();}
});
const secEls=Array.from(document.querySelectorAll("section[id^='sec']"));
function spy(){let cur=secEls[0].id;const y=window.scrollY+100;for(const s of secEls){if(s.offsetTop<=y)cur=s.id;}
  secEls.forEach(s=>{const a=document.getElementById('nav'+s.id.slice(3));if(a)a.classList.toggle('on',s.id===cur);});}
document.addEventListener('scroll',spy,{passive:true});spy();
function showTab(p,i){
  document.querySelectorAll(`[id^='${p}p']`).forEach(x=>x.classList.toggle('on',x.id===p+'p'+i));
  document.querySelectorAll(`[id^='${p}t']`).forEach(x=>x.classList.toggle('on',x.id===p+'t'+i));
}
let xList=[],xShown=0;
function xF(){
  const g=id=>document.getElementById(id).value;const f={};
  if(g('xb')!=='')f.brand=parseInt(g('xb'));
  if(g('xs')!=='')f.sub=parseInt(g('xs'));
  if(g('xe')!=='')f.sent=parseInt(g('xe'));
  if(g('xl')!=='')f.label=parseInt(g('xl'));
  if(g('xst')!=='')f.star=parseInt(g('xst'));
  if(g('xy')!==''){const p=D.periods[parseInt(g('xy'))];f.dfrom=p[1];f.dto=p[2];}
  if(g('xv')!=='')f.verified=parseInt(g('xv'));
  const q=g('xq').trim().toLowerCase();if(q)f.q=q;
  return f;
}
function xApply(){
  const f=xF();xList=matchReviews(f);xShown=0;let pos=0,neg=0,tot=0;
  xList.forEach(ri=>(TBYR[ri]||[]).forEach(ti=>{const t=D.T[ti];if(f.sub!=null&&t[1]!==f.sub)return;tot++;if(t[2]===0)pos++;if(t[2]===1)neg++;}));
  document.getElementById('xstat').innerHTML=`<span>${UI.reviews} <b>${fmt(xList.length)}</b> / ${fmt(D.total)}</span><span>${UI.sample_avg} <b>${avgStar(xList)}★</b></span>`+
    `<span>${UI.tags} ${fmt(tot)}${UI.count_suffix}: <span class='cpos'>${UI.positive} ${tot?(100*pos/tot).toFixed(1):'0.0'}%</span>, <span class='cneg'>${UI.negative} ${tot?(100*neg/tot).toFixed(1):'0.0'}%</span></span>`;
  document.getElementById('xres').innerHTML='';xChunk(f);
}
function xChunk(f){
  const box=document.getElementById('xres');const old=document.getElementById('xmore');if(old)old.remove();
  box.insertAdjacentHTML('beforeend',xList.slice(xShown,xShown+30).map(ri=>card(ri,false,f)).join(''));
  xShown=Math.min(xShown+30,xList.length);
  if(xShown<xList.length){box.insertAdjacentHTML('beforeend',`<button class='morebtn' id='xmore'>${UI.more} (${xShown}/${xList.length})</button>`);
    document.getElementById('xmore').onclick=()=>xChunk(f);}
}
function xReset(){['xb','xs','xe','xl','xst','xy','xv','xq'].forEach(id=>document.getElementById(id).value='');xApply();}
['xb','xs','xe','xl','xst','xy','xv'].forEach(id=>document.getElementById(id).addEventListener('change',xApply));
document.getElementById('xq').addEventListener('input',()=>{clearTimeout(window._xt);window._xt=setTimeout(xApply,300);});
xApply();
</script>
</body>
</html>
"""


def main():
    ap = argparse.ArgumentParser(description="HTML 리포트(06_report.html) 만들기와 검사")
    ap.add_argument("mode", choices=["build", "check"])
    ap.add_argument("run", nargs="?")
    ap.add_argument("--lang", default="ko", help="화면 언어(ko, en). 영어판은 06_report_en.md와 config/i18n/report_ui_en.yaml, i18n_names_en.yaml을 쓴다")
    args = ap.parse_args()
    run = resolve_run(args.run)
    sys.exit(build_html(run, args.lang) if args.mode == "build" else check(run, args.lang))


if __name__ == "__main__":
    main()
