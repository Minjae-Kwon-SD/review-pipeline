"""제품 개발 가이드 HTML(07_guide.html)을 만들고 검사한다. 모델을 부르지 않는다.

사용:
  python scripts/render_guide_html.py build [회차]
    17_guide.md(문장), 16_guide_metrics.json(숫자, 표, 근거 묶음), 15_research.yaml과 15_research_check.json(확인된 출처)으로
    한 파일을 만든다. 06_report.html과 같은 틀(외부 참조 없음, 데이터는 안에, 따라오는 목차, 밝은 화면과 어두운 화면, CSS 막대).
    드릴다운은 정답지 개발 가이드 방식: 근거로 쓴 리뷰만 넣고, 숫자마다 미리 묶은 근거 목록(최대 80개)을 연다.
    문장의 [m:키]는 그 키의 표기를 찾아 드릴다운 링크로, [r:id]는 출처 링크로 바꾼다.
  python scripts/render_guide_html.py build|check [회차] --lang en
    언어판: 17_guide_<lang>.md를 읽어 07_guide_<lang>.html을 만든다. 화면 문구는 config/i18n/guide_ui_<lang>.yaml(키는 한국어 원문),
    이름은 runs/<회차>/i18n_names_<lang>.yaml(render_html.Lang과 같은 방식). 문구 파일이 없으면 멈춘다. 빠진 문구는 numbers 파일의 missing_strings.
    16_guide_metrics.json의 숫자 표기(text)는 아직 한국어라, 영어판을 돌리려면 표기 번역 규칙이 더 필요하다.
  python scripts/render_guide_html.py check [회차]
    숫자 대조(화면 숫자와 metrics), 문장 속 [m:키] 표기 대조, 드릴다운 리뷰 수 대조, research id가 확인된 것인지,
    출처 링크 말고 외부 참조 0, 우리 글자에 가운뎃점 0. 결과: 07_guide_html_check.json
"""
import argparse
import html
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import render_html  # noqa: E402
from pipeline_io import REVIEW_COLS, load_csv_or_die, load_yaml, now_iso, resolve_run, write_json  # noqa: E402

for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass

QUOTE = re.compile(r'"(.+?)"\s*\(([^()]+?),\s*([1-5])★,\s*(R[0-9A-Z]+)\)')
MARK = re.compile(r"\s*\[m:([^\]]+)\]")
RMARK = re.compile(r"\s*\[r:([^\]\s]+)\]")
CHAPTERS = [("01", "시장 개요"), ("02", "경쟁사"), ("03", "문제"), ("04", "포지셔닝"), ("05", "한 장 요약"), ("A", "데이터와 방법")]


def esc(s):
    return html.escape(str(s), quote=True)


class R:
    def __init__(self, run, lang="ko"):
        self.run = run
        self.lang, self.sfx = lang, ("" if lang == "ko" else f"_{lang}")
        self.T = render_html.Lang(lang, run, ui="guide_ui")
        self.M = json.loads((run / "16_guide_metrics.json").read_text(encoding="utf-8"))
        self.V = self.M["values"]
        res = load_yaml(run / "15_research.yaml") or {}
        chk = json.loads((run / "15_research_check.json").read_text(encoding="utf-8"))
        ok = {x["id"] for x in chk["items"] if x["status"] == "verified"}
        self.claims = {c["id"]: c for c in res.get("claims") or [] if c.get("id") in ok}
        self.all_claims = {c["id"]: c for c in res.get("claims") or []}
        self.reviews = {r["review_id"]: r for r in load_csv_or_die(run / "02_reviews.csv", REVIEW_COLS)}
        asins = {}
        p = run / "01_asins.csv"
        if p.exists():
            import csv
            with p.open(encoding="utf-8-sig") as f:
                asins = {r["asin"]: r.get("brand", "") for r in csv.DictReader(f)}
        self.brand = asins
        self.rv, self.ridx = [], {}
        self.nums = []
        self.misses, self.rmisses, self.used_claims = [], [], set()

    # ------------------------------------------------ 데이터
    def rid(self, review_id):
        if review_id not in self.ridx:
            r = self.reviews[review_id]
            self.ridx[review_id] = len(self.rv)
            self.rv.append({"id": review_id, "s": int(r["star"]), "d": r["date"], "t": r["title"], "b": r["body"],
                            "br": self.brand.get(r["asin"], ""), "a": r["asin"], "v": r.get("variant_text") or ""})
        return self.ridx[review_id]

    def ev_json(self):
        out = {}
        for k, e in self.M["ev"].items():
            idx = [self.rid(r) for r in e["i"]]
            out[k] = {"t": e["t"], "s": e["s"], "n": e["n"], "i": idx, "q": {str(self.rid(r)): q for r, q in e["q"].items()}}
        return out

    # ------------------------------------------------ 숫자
    def num(self, key, cls=""):
        """values의 표기를 화면에 쓰고 기록한다. 근거 묶음이 있으면 드릴다운 링크."""
        v = self.V[key]
        k = f"g{len(self.nums)}"
        self.nums.append({"k": k, "key": key, "text": v["text"]})
        if v.get("ev") and self.M["ev"].get(v["ev"], {}).get("n"):           # 리뷰 0개인 근거 묶음은 링크로 만들지 않는다
            return f'<span class="numlink {cls}" data-k="{k}" data-drill="ev" data-key="{esc(v["ev"])}" tabindex="0">{esc(v["text"])}</span>'
        return f'<span class="{cls}" data-k="{k}">{esc(v["text"])}</span>'

    def pc(self, v, n=None, kind_w=False):
        """비율 표기: 0이 아닌데 0.05% 미만이면 '0.1% 미만', 리뷰가 10개 미만이면 (잠정)"""
        tiny = (v and 0 < float(v) < 0.05) or (not v and n and n > 0 and kind_w)   # 가중 비율이 반올림으로 0이 된 경우
        t = "0.1% 미만" if tiny else f"{float(v or 0):.1f}%"
        return t + ("(잠정)" if n is not None and 0 < n < 10 else "")

    def nm(self, kind, key, sub=None):
        """영어 id 대신 승인 파일의 한국어 이름(없으면 id 그대로)"""
        names = (self.M["tables"].get("meta.names") or {}).get(kind) or {}
        if sub is not None:
            return (names.get(key) or {}).get(str(sub)) or str(sub)
        return names.get(key) or key

    def tnum(self, text, ev=None, cls=""):
        """표 칸 숫자(표기는 metrics 표에 이미 있는 값에서 만든 것)."""
        if ev and self.M["ev"].get(ev, {}).get("n"):
            return f'<span class="numlink {cls}" data-drill="ev" data-key="{esc(ev)}" tabindex="0">{esc(text)}</span>'
        return f'<span class="{cls}">{esc(text)}</span>'

    # ------------------------------------------------ 문장
    def inline(self, s):
        out, pos = [], 0
        tokens = sorted([(m.start(), m.end(), "m", m.group(1)) for m in MARK.finditer(s)]
                        + [(m.start(), m.end(), "r", m.group(1)) for m in RMARK.finditer(s)])
        for st, en, kind, key in tokens:
            seg = s[pos:st]
            if kind == "m":
                v = self.V.get(key)
                if v is None:
                    self.misses.append(f"없는 metrics 키 {key}")
                    out.append(self.md(seg))
                else:
                    i = seg.rfind(v["text"])
                    if i < 0:
                        self.misses.append(f"[m:{key}] 앞에 표기 '{v['text']}'가 없음: {seg[-60:]}")
                        out.append(self.md(seg))
                    else:
                        out.append(self.md(seg[:i]) + self.num(key) + self.md(seg[i + len(v["text"]):]))
            else:
                out.append(self.md(seg))
                c = self.claims.get(key)
                self.used_claims.add(key)
                if c is None:
                    self.rmisses.append(key)
                    out.append('<sup class="srcbad">[출처 확인 안 됨]</sup>')
                else:
                    out.append(f'<sup><a class="src" href="{esc(c["url"])}" target="_blank" rel="noopener noreferrer" '
                               f'title="{esc(c.get("source_name", ""))}">[{esc(key)}]</a></sup>')
            pos = en
        out.append(self.md(s[pos:]))
        return "".join(out)

    @staticmethod
    def md(s):
        return re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", esc(s))

    def chip(self, q):
        text, brand, star, rid = q
        if rid not in self.reviews:
            self.misses.append(f"없는 리뷰 id 인용 {rid}")
            return f'<span class="chip">“{esc(text)}”</span>'
        orig = None
        for qs in self.M["quotes"].values():
            for x in qs:
                if x["review_id"] == rid:
                    orig = x["quote"]
        i = self.rid(rid)
        return (f'<span class="chip clk" data-drill="rev" data-ri="{i}" data-q="{esc(orig or "")}" tabindex="0">“{esc(text)}”'
                f'<em>{esc(brand)} {star}★ {rid}</em></span>')

    def block(self, lines):
        """문단, 목록, 인용, ####를 HTML로."""
        out, lst, ltype = [], [], None

        def flush():
            nonlocal lst, ltype
            if lst:
                tag = "ol" if ltype == "ol" else "ul"
                out.append(f"<{tag} class='gl'>" + "".join(f"<li>{x}</li>" for x in lst) + f"</{tag}>")
            lst, ltype = [], None
        for raw in lines:
            s = raw.strip()
            if not s:
                flush()
                continue
            if s.startswith("#### "):
                flush()
                out.append(f"<h4>{self.inline(s[5:])}</h4>")
                mstd = re.match(r"기준\s*(\d+)", s[5:].strip())
                if mstd:
                    out.append(self.std_card(int(mstd.group(1))))
            elif s.startswith(">"):
                q = QUOTE.search(s)
                if q:
                    if lst:
                        lst[-1] += f"<div class='chips'>{self.chip(q.groups())}</div>"
                    else:
                        out.append(f"<div class='chips'>{self.chip(q.groups())}</div>")
                else:
                    flush()
                    out.append(f"<p class='sub2'>{self.inline(s.lstrip('> '))}</p>")
            elif re.match(r"^- ", s):
                if ltype not in (None, "ul"):
                    flush()
                ltype = "ul"
                lst.append(self.inline(s[2:]))
            elif re.match(r"^\d+\.\s", s):
                if ltype not in (None, "ol"):
                    flush()
                ltype = "ol"
                lst.append(self.inline(re.sub(r"^\d+\.\s", "", s)))
            elif s.startswith("**TL;DR**"):
                flush()
                out.append(f"<div class='tldr'><b>TL;DR</b> {self.inline(s[len('**TL;DR**'):].strip())}</div>")
            elif s.startswith("|"):
                continue                     # 표는 스크립트가 그린다
            else:
                flush()
                out.append(f"<p>{self.inline(s)}</p>")
        flush()
        return "".join(out)

    # ------------------------------------------------ 스크립트가 그리는 표
    def bars(self, rows, label, value, text, ev, mx=None, color="neg"):
        mx = mx or max((r[value] or 0) for r in rows) or 1
        return "".join(
            f'<div class="brow"><span class="blab">{esc(r[label])}</span><span class="btrack"><span class="bbar" style="width:{100 * (r[value] or 0) / mx:.1f}%">'
            f'<span style="width:100%;background:var(--{color})"></span></span></span><span class="bn">{self.tnum(r[text], r.get(ev) if ev else None)}</span></div>'
            for r in rows)

    def table(self, head, rows):
        return ('<div class="tscroll"><table class="ct"><thead><tr>' + "".join(f"<th>{esc(h)}</th>" for h in head) + "</tr></thead><tbody>"
                + "".join("<tr>" + "".join(f"<td{' class=tl' if i == 0 else ''}>{c}</td>" for i, c in enumerate(r)) + "</tr>" for r in rows)
                + "</tbody></table></div>")

    def srcs(self, lst):
        """사양 값의 출처 링크(공식, 소매점, 커뮤니티)"""
        seen, out = set(), []
        lab = {"official": "공식", "retailer": "소매점", "community": "커뮤니티"}
        for x in lst or []:
            if x["url"] in seen:
                continue
            seen.add(x["url"])
            out.append(f'<a class="src" href="{esc(x["url"])}" target="_blank" rel="noopener noreferrer">[{lab.get(x["type"], x["type"])}]</a>')
        return " ".join(out)

    def spec_table(self, sid):
        """기준 1, 2, 4, 6 아래의 상품 사양 표(23_specs_verified.json에서 확인된 값만)"""
        rows = self.M["tables"].get(f"std.spec.{sid}")
        if not rows:
            return ""
        sid = (self.M["tables"].get("std.spec_kinds") or {}).get(sid, sid)     # 사양 연결 종류(duration, notes, parts, body)
        mt = lambda r: "" if r["match"] == "일치 확인" else f"<div class='mut small'>{esc(r['match'])}</div>"
        if sid == "duration":
            body = [[f"<b>{esc(r['brand'])}</b>" + mt(r), esc(r["subcategory"] or "-"), esc(r["concentration"]) + " " + self.srcs(r["src"]),
                     esc(self.pc(r['neg_pct'])), esc(str(r["duration_values"])),
                     esc("-" if r["duration_median"] is None else f"{r['duration_median']:g}시간")] for r in rows]
            return ("<div class='coltitle' style='margin-top:10px'>상품 사양과 나란히: 농도, 지속력과 세기 부정(가중), 말한 지속 시간</div>"
                    + self.table(["상품", "하위 카테고리", "농도(사양)", "부정(가중)", "말한 지속 시간 값", "중앙값"], body)
                    + "<div class='fn'>상품이 6개라 농도와 불만의 관계를 말하지 않고 나열만 한다. 중앙값은 값 5개 이상일 때만.</div>")
        if sid == "notes":
            body = [[f"<b>{esc(r['brand'])}</b>" + mt(r), esc(r["official"]) + " " + self.srcs(r["src"]),
                     esc("-" if r["said"] is None else str(r["said"])),
                     self.tnum("-" if r["mention"] is None else f"{r['mention']}개", f"ev.spec.notes.{r['asin']}" if r["mention"] else None),
                     esc("-" if r["missing"] is None else str(r["missing"])), esc(r["missing_notes"])] for r in rows]
            return ("<div class='coltitle' style='margin-top:10px'>공식 노트 구성과 리뷰가 말한 노트</div>"
                    + self.table(["상품", "공식 노트(사양)", "노트를 말한 리뷰", "공식 노트(계열)를 말한 리뷰", "설명한 노트가 안 남", "그 리뷰가 말한 노트"], body)
                    + "<div class='fn'>리뷰의 노트는 설계 정보 항목 '리뷰에 나온 노트'의 값(계열)이고, 공식 노트 낱말과는 config의 note_map으로 맞댔다. (공식)은 그 상품 공식 노트 계열.</div>")
        if sid == "parts":
            body = [[f"<b>{esc(r['brand'])}</b>" + mt(r), esc(r["sprayer"]) + " " + self.srcs(r["src"]),
                     self.tnum(f"{r['parts']}개", r["ev"] if r["parts"] else None), esc(r["top"])] for r in rows]
            return ("<div class='coltitle' style='margin-top:10px'>병과 분사기 사양과 망가진 부품 리뷰</div>"
                    + self.table(["상품", "병과 분사기(사양)", "망가진 부품 리뷰", "많은 순"], body))
        if sid == "body":
            body = [[f"<b>{esc(r['brand'])}</b>" + mt(r), esc(str(r["symptoms"])), esc(r["by_type"]),
                     esc(r["allergens"]) + " " + self.srcs(r["src"])] for r in rows]
            return ("<div class='coltitle' style='margin-top:10px'>이상 반응 리뷰와 표시 알레르기 성분(나열만)</div>"
                    + self.table(["상품", "이상 반응 리뷰", "종류", "표시 알레르기 성분(사양)"], body)
                    + "<div class='fn'>이상 반응 리뷰가 적어 상품별 비율이나 성분과의 관계를 말하지 않는다.</div>")
        return ""

    def insert_for(self, title):
        T = self.M["tables"]
        t = title
        if "TAM" in t:
            rows = [[esc(r["name"]), self.tnum(r["revenue_text"]), esc(f"{r['brands']:,}"), esc(f"{r['asins']:,}"), esc("-" if r.get('avg_price') is None else f"{r['avg_price']:.2f}"),
                     esc(f"{r['avg_rating']:.2f}"), esc(f"{r['mom12']:.2f}"), esc(f"{r['az']:.4f}")] for r in T.get("m.subcategories", [])]
            return ("<div class='coltitle'>하위 카테고리(시장 데이터, 월 매출 칸과 증감, azRevenuePct 단위 미확인)</div>"
                    + self.table(["노드", "월 매출", "브랜드", "ASIN", "평균 가격", "평균 별점", "12개월 증감(momGrowth12)", "아마존 직판 비중(azRevenuePct)"], rows)
                    + "".join(f"<div class='coltitle' style='margin-top:12px'>브랜드 점유율 상위 10: {esc(n)}</div>"
                              + self.table(["순위", "브랜드", "점유율(marketshare, %로 읽음)", "평균 가격", "평균 별점"],
                                           [[esc(r["rank"]), esc(r["brand"]), esc(r["share_text"]), esc(f"{r['avg_price']:.2f}"),
                                             esc("-" if r.get('rating') is None else f"{r['rating']:.2f}")] for r in T.get(f"m.brands_{k}", [])])   # 빈 값은 -
                              for k, n in zip(T.get("meta.market_keys") or [], T.get("meta.brand_nodes") or [])))
        if "검색 수요" in t:
            parts = []
            for g, n in (("female", "여성 검색어"), ("male", "남성 검색어"), ("common", "공통 검색어")):
                parts.append(f"<div class='col'><div class='coltitle'>{n}(30일 검색량, 전년 대비 증감)</div>"
                             + self.table(["검색어", "검색량", "전년 대비"], [[esc(r["term"]), esc(r["volume_text"]), esc(r["yoy_text"])]
                                                                    for r in T.get(f"m.terms_{g}", [])]) + "</div>")
            pb = T.get("m.price_bands", [])
            return (f"<div class='cols'>{''.join(parts)}</div><div class='coltitle' style='margin-top:12px'>가격대(브랜드 평균 가격 3구간)</div>"
                    + self.table(["구간", "가격 범위", "브랜드 수", "평균 별점", "매출 비중"],
                                 [[esc(r["band"]), esc(r["price_range"]), esc(r["brands"]), esc("-" if r["avg_rating"] is None else f"{r['avg_rating']:.2f}"),
                                   esc(f"{r['revenue_share']:.1f}%")] for r in pb]))
        if "점수표" in t:
            sb = T.get("meta.scoreboard") or {}      # 카테고리 이름(없으면 향수 때 문구)
            tn, hi, lo = sb.get("topic_name"), sb.get("dir_high", "너무 셈"), sb.get("dir_low", "약함")
            du, dn = sb.get("duration_unit", "시간"), sb.get("duration_name", "말한 지속 시간")
            show_size = (not sb) or any(r.get("size") or r.get("price_per_oz") for r in T.get("s.scoreboard", []))
            rows = []
            for r in T.get("s.scoreboard", []):
                rows.append([f"<b>{esc(r['brand'])}</b><div class='mono mut'>{esc(r['asin'])}</div>", esc(r["subcategory"] or "-"),
                             esc(f"{r['price']:.2f}" if r["price"] else "-")]
                            + ([esc(r["size"] or "-"), esc(f"{r['price_per_oz']:.2f}" if r["price_per_oz"] else "-")] if show_size else [])
                            + [esc(f"{r['weighted_star']:.2f}★"),
                             self.tnum(self.pc(r['topic_neg_pct']), r["ev"]["topic_neg"]),
                             self.tnum("-" if r["dir_index"] is None else f"{r['dir_index']:+.2f}", r["ev"]["dir_low"])
                             + f"<div class='mut small'>{esc(lo)} {r['dir_low']} 대 {esc(hi)} {r['dir_high']}</div>",
                             self.tnum("-" if r["duration_median"] is None else (f"약 {round(r['duration_median'] * 60)}분" if du == "시간" and r['duration_median'] < 1 else f"{r['duration_median']:g}{du}"), r["ev"]["duration"])
                             + f"<div class='mut small'>값 {r['duration_values']}개</div>",
                             esc(r["strength"] or "-"), esc(r["weakness"] or "-")]
                            + ([esc(r.get("spec_concentration") or "-") + ("" if r.get("spec_match") in (None, "일치 확인") else
                                                                         f"<div class='mut small'>{esc(r['spec_match'])}</div>"),
                                esc(r.get("spec_notes") or "-") + " " + self.srcs(r.get("spec_src"))] if "spec_concentration" in r else []))
            spec_head = ["농도(사양)", "노트 구성(사양)"] if any("spec_concentration" in r for r in T.get("s.scoreboard", [])) else []
            if not sb:      # 향수 회차(이전 metrics)와 같은 화면
                head = ["상품", "하위 카테고리", "가격", "용량", "온스당", "가중 별점", "지속력 부정(가중)", "세기 방향 지수", "말한 지속 시간 중앙값"]
                fn = "세기 방향 지수 = (너무 셈 − 약함) ÷ (너무 셈 + 약함), 방향 언급 25개 이상인 상품만. 지속 시간 중앙값은 값 5개 이상일 때만."
            else:
                head = (["상품", "하위 카테고리", "가격"] + (["용량", "온스당"] if show_size else []) + ["가중 별점", f"{tn} 부정(가중)",
                        f"방향 지수({hi}, {lo})", f"{dn} 중앙값"])
                fn = (f"방향 지수 = ({hi} − {lo}) ÷ ({hi} + {lo}), 방향 언급 {sb.get('dir_min')}개 이상인 상품만. "
                      f"{dn} 중앙값은 값 {sb.get('duration_min')}개 이상일 때만.")
            return self.table(head + ["가장 큰 강점", "가장 큰 약점"] + spec_head, rows) + f"<div class='fn'>{esc(fn)}</div>"
        if "하위 카테고리 비교" in t:
            sub = {}
            for r in T.get("s.scoreboard", []):
                sub.setdefault(r["subcategory"] or "-", []).append(r["brand"])
            names = {r["name"]: r for r in T.get("m.subcategories", [])}
            return self.table(["하위 카테고리", "우리 상품", "월 매출(단위 미확인)", "브랜드 수"],
                              [[esc(k), esc(", ".join(v)), esc(names[k]["revenue_text"]) if k in names else "-",
                                esc(f"{names[k]['brands']:,}") if k in names else "-"] for k, v in sub.items()])
        if "업계 구조" in t:
            rows = [[esc(c.get("subject") or "-"), esc(c["claim_ko"]), f'<a class="src" href="{esc(c["url"])}" target="_blank" rel="noopener noreferrer">[{esc(c["id"])}]</a>']
                    for c in self.claims.values() if c.get("area") == "industry"]
            for c in self.claims.values():
                if c.get("area") == "industry":
                    self.used_claims.add(c["id"])
            return self.table(["브랜드", "제품 라인 구성(웹 조사)", "출처"], rows) if rows else ""
        if "불만 지도" in t:
            return self.bars(T.get("p.complaint_map", [])[:10], "name", "neg_reviewer_pct", "pct_text", "ev") if False else \
                self.bars([{**r, "pct_text": f"{r['neg_reviewer_pct']:.1f}%"} for r in T.get("p.complaint_map", [])[:11]], "name", "neg_reviewer_pct", "pct_text", "ev")
        if "별점 격차" in t:
            return self.table(["주제", "부정 리뷰", "부정 리뷰 평균", "나머지 평균", "격차"],
                              [[esc(g["name_ko"]), self.tnum(f"{g['neg_reviews']}개", g["ev"]), esc(f"{g['neg_avg_star']:.2f}★"),
                                esc(f"{g['other_avg_star']:.2f}★"), f"<b>{esc(f'{g[chr(103)+chr(97)+chr(112)]:+.2f}')}</b>"] for g in T.get("p.gaps", [])])
        if t.startswith("집중 분석"):
            m = re.search(r"집중 분석\s*(\d)", t)
            if not m:
                return ""
            focus = T.get("meta.focus") or []
            if not 1 <= int(m.group(1)) <= len(focus):
                return ""
            fmeta = focus[int(m.group(1)) - 1]
            fid = fmeta["id"]
            parts = []
            drawn = getattr(self, "_drawn_items", set())      # 앞 집중 분석에서 이미 그린 항목 표는 다시 그리지 않음
            self._drawn_items = drawn
            for k, rows in T.items():
                if not k.startswith(f"f.{fid}."):
                    continue
                it_id = k.split(".")[2]
                if it_id in drawn and not (k.endswith(".bins") or ".by_" in k or ".labels." in k):
                    parts.append(f"<div class='fn'>{esc(self.nm('items', it_id))} 표는 앞 집중 분석과 같아 다시 싣지 않습니다.</div>")
                    continue
                if not (".by_" in k or ".labels." in k or k.endswith(".bins")):
                    drawn.add(it_id)
                if k.endswith(".bins"):
                    parts.append(f"<div class='coltitle'>{esc(T.get('meta.duration_name') or '값')} 분포</div>" + self.bars(
                        [{**r, "n_text": f"{r['reviews']}개"} for r in rows], "bin", "reviews", "n_text", "ev", color="mix"))
                elif ".by_" in k:
                    sl = fmeta.get("split_label_name") or "라벨"
                    parts.append(f"<div class='coltitle'>{esc(self.nm('items', k.split('.')[2]))}별 {esc(sl)} 비율</div>" + self.table(
                        ["값", "리뷰", sl, "비율"], [[esc(r["ko"]), esc(r["reviews"]), esc(r["with_label"]), esc(self.pc(r['share'], r["reviews"]))] for r in rows]))
                elif k.endswith(".note_x_direction"):
                    parts.append("<div class='coltitle'>노트 x 방향(같은 인용에서 짝지은 수)</div>" + self.table(
                        ["노트", "방향", "리뷰"], [[esc(self.nm('values', 'scent_note', r["note"])), esc(self.nm('values', 'note_direction', r["direction"])), esc(r["reviews"])] for r in rows[:20]]))
                elif ".labels." in k:
                    parts.append(f"<div class='coltitle'>세부 이슈 라벨: {esc(self.nm('topics', k.split('.')[-1]))} 부정</div>" + self.table(
                        ["라벨", "리뷰", "가중"], [[esc(r["name"]), esc(r["reviews"]), esc(self.pc(r['weighted_pct'], r["reviews"], kind_w=True))] for r in rows]))
                elif rows and "ko" in rows[0]:
                    parts.append(f"<div class='coltitle'>{esc(self.nm('items', k.split('.')[-1]))}</div>" + self.bars(
                        [{**r, "n_text": f"{r['reviews']}개"} for r in rows], "ko", "reviews", "n_text", "ev", color="prod"))
                elif rows and "value" in rows[0]:
                    parts.append(f"<div class='coltitle'>{esc(self.nm('items', k.split('.')[-1]))}(원문 표기)</div>" + self.table(
                        ["값", "리뷰"], [[esc(r["value"]), esc(r["reviews"])] for r in rows]))
            return "".join(parts)
        if t.startswith("안전"):
            return self.bars([{**r, "n_text": f"{r['reviews']}개"} for r in T.get("p.safety", [])], "name", "reviews", "n_text", "ev")
        if "소비자 기준표" in t:
            return ""
        if t == "__std_all__":
            cells = []
            for i, s in enumerate(T.get("std.board", []), 1):
                labs = ", ".join(f"{esc(x['name'])} {x['reviews']}" for x in s["neg_labels"] if x["reviews"]) or "-"
                items = ", ".join(esc(x.get("text") or f"{x['ko']} {x['reviews']}") for x in s["items"][:4]) or "-"
                terms = ", ".join(f"{esc(x['term'])} {x['volume']:,}" for x in s["terms"][:3]) or "-"
                cells.append(f"<div class='std'><div class='std-h'><span class='n'>{i}</span>{esc(s['title'])}</div>"
                             f"<div class='std-grid'><div><b>불만 리뷰</b> {self.tnum(f'{s[chr(110)+chr(101)+chr(103)+chr(95)+chr(114)+chr(101)+chr(118)+chr(105)+chr(101)+chr(119)+chr(115)]:,}개', s['ev']['neg'])}"
                             f"(가중 {self.pc(s['neg_weighted_pct'])})<div class='mut small'>{labs}</div></div>"
                             f"<div><b>만족 리뷰</b> {self.tnum(f'{s[chr(112)+chr(111)+chr(115)+chr(95)+chr(114)+chr(101)+chr(118)+chr(105)+chr(101)+chr(119)+chr(115)]:,}개', s['ev']['pos'])}"
                             f"<div class='mut small'>부정이 가장 적은 상품: {esc(s['best']['brand'])} {self.pc(s['best']['neg_pct'])}</div></div>"
                             f"<div><b>설계 정보</b><div class='mut small'>{items}</div></div><div><b>관련 검색어</b><div class='mut small'>{terms}</div></div></div></div>")
            return "".join(cells)
        if "견고성" in t:
            rows = T.get("a.robust", [])
            body = [[f"<b>{esc(r['brand'] or '빼지 않음')}</b>" + (f"<div class='mono mut'>{esc(r['out'])}</div>" if r["out"] else ""),
                     esc(f"{r['reviews']:,}"), esc(r["head_neg_text"]), esc(r["first_text"]), esc(r["second_text"]), esc(r["weakest_text"]),
                     esc(r["dir_text"]), esc(r["top3_text"]), esc(r["flip_text"])] for r in rows]
            V = self.M["values"]
            bs = (f"<div class='coltitle' style='margin-top:12px'>리뷰 다시 뽑기({esc(V['a.robust.n']['text'])}, 난수 씨앗 고정)</div>"
                  + self.table(["무엇", "결과"], [["불만 1위가 1위로 남은 비율", esc(V["a.robust.head_first"]["text"])],
                                                  ["머리 숫자 2의 95% 구간", esc(V["a.robust.head_neg_ci"]["text"])],
                                                  ["머리 숫자 3(최대 약점 상품 수) 분포", esc(V["a.robust.weakest_dist"]["text"])]])) \
                if "a.robust.n" in V else ""
            return ("<div class='coltitle'>상품 하나씩 빼고 다시 계산</div>"
                    + self.table(["뺀 상품", "남은 리뷰", "머리 2", "불만 1위", "불만 2위", "머리 3", "머리 4(약함 대 너무 셈)", "불만 지도 상위 3", "뒤집힘"], body)
                    + bs + "<div class='fn'>가중치는 리뷰마다 원래 표본에서 정한 값을 그대로 쓴다(상품을 빼도 다른 상품의 가중치는 같고, 다시 뽑기에서는 근사).</div>")
        if "제품 해부도" in t:
            return self.anatomy()
        if t.strip() == "출처":
            rows = [[esc(c["id"]), esc(c.get("area")), esc(c["claim_ko"]), f'<a class="src" href="{esc(c["url"])}" target="_blank" rel="noopener noreferrer">{esc(c.get("source_name") or c["url"])}</a>']
                    for c in self.claims.values()]
            src = self.M.get("sources", {})
            base = self.table(["데이터", "내용"], [[esc(k), esc(v)] for k, v in src.items()])
            return base + "<div class='coltitle' style='margin-top:12px'>웹 조사 주장(다시 열어 원문 문장을 확인한 것만)</div>" + self.table(["id", "분야", "내용", "출처"], rows)
        return ""

    def std_card(self, n):
        """기준 n의 숫자 칸(불만 리뷰, 만족 리뷰, 부정이 가장 적은 상품, 설계 정보, 관련 검색어). 문장의 '#### 기준 n' 아래에 놓는다."""
        board = self.M["tables"].get("std.board", [])
        if not 1 <= n <= len(board):
            return ""
        s = board[n - 1]
        labs = ", ".join(f"{esc(x['name'])} {x['reviews']}" for x in s["neg_labels"] if x["reviews"]) or "-"
        items = ", ".join(esc(x.get("text") or f"{x['ko']} {x['reviews']}") for x in s["items"][:4]) or "-"
        terms = ", ".join(f"{esc(x['term'])} {x['volume']:,}" for x in s["terms"][:3]) or "-"
        neg = self.tnum(f"{s['neg_reviews']:,}개", s["ev"]["neg"])
        pos = self.tnum(f"{s['pos_reviews']:,}개", s["ev"]["pos"])
        return (f"<div class='std'><div class='std-h'><span class='n'>{n}</span>{esc(s['title'])}: 데이터</div><div class='std-grid'>"
                f"<div><b>불만 리뷰</b> {neg}(가중 {s['neg_weighted_pct']:.1f}%)<div class='mut small'>{labs}</div></div>"
                f"<div><b>만족 리뷰</b> {pos}<div class='mut small'>부정이 가장 적은 상품: {esc(s['best']['brand'])} {self.pc(s['best']['neg_pct'])}</div></div>"
                f"<div><b>설계 정보</b><div class='mut small'>{items}</div></div><div><b>관련 검색어(30일 검색량)</b><div class='mut small'>{terms}</div></div></div></div>"
                + self.spec_table(s["id"]))

    def anatomy(self):
        """제품 해부도(카테고리 설정 guide.anatomy: viewbox, shapes, points). 설정이 없으면 그림을 넣지 않는다."""
        A = self.M["tables"].get("meta.anatomy")
        if not A:
            return ""
        svg = [f'<svg class="anat" viewBox="{esc(A["viewbox"])}" role="img" aria-label="제품 해부도">']
        for sh in A.get("shapes") or []:
            svg.append(f'<rect x="{sh["x"]}" y="{sh["y"]}" width="{sh["w"]}" height="{sh["h"]}" rx="{sh.get("rx", 0)}" fill="var(--{sh.get("fill", "soft")})" '
                       f'stroke="var(--sub)"' + (f' stroke-width="{sh["width"]}"' if sh.get("width") else "") + '/>')
        for i, (x, y) in enumerate(A.get("points") or [], 1):
            svg.append(f'<circle cx="{x}" cy="{y}" r="15" fill="var(--accent)"/><text x="{x}" y="{y + 5}" text-anchor="middle" '
                       f'font-size="14" font-weight="700" fill="var(--card)">{i}</text>')
        svg.append("</svg>")
        return f"<div class='anatwrap'>{''.join(svg)}<div class='fn'>방향 잡기용 그림이고 설계 도면이 아닙니다. 번호 설명은 아래 목록.</div></div>"

    # ------------------------------------------------ 전체
    def build(self):
        text = (self.run / f"17_guide{self.sfx}.md").read_text(encoding="utf-8")
        T = self.T
        chapters_t = [(c, T(t)) for c, t in CHAPTERS]
        lines = text.splitlines()
        title = next((l[2:].strip() for l in lines if l.startswith("# ")), self.M.get("title") or T("개발 가이드"))
        subtitle = next((l.lstrip("> ").strip() for l in lines if l.startswith(">")), "")
        chapters, cur, head = {}, None, []
        for l in lines:
            m = re.match(r"^## (.+)$", l)
            if m:
                name = m.group(1).strip()
                cur = "head" if name.startswith(T("머리 숫자")) else next((c for c, _ in CHAPTERS if name.startswith(c + " ")), name)
                chapters.setdefault(cur, [])
                continue
            if cur:
                chapters[cur].append(l)
        heads = {}
        for l in chapters.get("head", []):
            m = re.match(r"^- \[([^\]]+)\]\s*(.*)$", l.strip())
            if m:
                heads[m.group(1)] = m.group(2)
        kp = []
        # 머리 숫자는 문장에 적힌 순서대로(키를 바꿔 쓸 수 있게). 문장에 없으면 기본 다섯
        for key in (list(heads) or ["head.market_year", "head.topic_neg", "head.topic_weakest", "head.dir_ratio", "head.fastest_term"]):
            if key not in self.V:
                continue
            cap = heads.get(key, "")
            kp.append(f"<div class='hkpi'><div class='v'>{self.num(key)}</div><div class='l'>{self.inline(cap) if cap else ''}</div></div>")
        parts = [f"<h1>{esc(title)}</h1>", f"<p class='sub'>{self.inline(subtitle)}</p>" if subtitle else "",
                 '<div class="toci">' + "".join(f'<a href="#sec{c}"><b>{c}</b>{esc(t)}</a>' for c, t in chapters_t) + "</div>",
                 f"<div class='callout'><div class='cb'><b>{T('안내')}</b><ul><li>{T('밑줄 친 숫자와 인용을 누르면 그 근거 리뷰 원문이 열립니다(숫자마다 미리 묶은 최대 80개, 1~3★과 4~5★로 다시 거를 수 있음).')}</li>"
                 f"<li>{T('[mkt_01] 같은 위첨자는 웹 조사 출처 링크입니다(다시 열어 원문 문장을 확인한 것만).')}</li></ul></div></div>",
                 f"<div class='hkpis'>{''.join(kp)}</div>"]
        for c, t in chapters_t:
            body = chapters.get(c, [])
            out, sub, buf = [], None, []

            def flush_sub():
                if sub is not None:
                    out.append(f"<h3>{self.inline(sub)}</h3>" + self.insert_for(sub) + self.block(buf))
                else:
                    out.append(self.block(buf))
            for l in body:
                m = re.match(r"^### (.+)$", l)
                if m:
                    flush_sub()
                    sub, buf = m.group(1).strip(), []
                else:
                    buf.append(l)
            flush_sub()
            parts.append(f'<section id="sec{c}"><h2><span class="num">{c}</span>{esc(t)}</h2>{"".join(out)}</section>')
        cav = "".join(f"<li>{esc(x)}</li>" for x in self.M.get("caveats", []))
        parts.append(f"<div class='caveat'><b>{T('주의 사항(metrics의 한계 목록)')}</b><ul>{cav}</ul></div>")
        parts.append(f"<div class='fn' style='text-align:center;margin:20px 0 40px'>{T('만든 날 {d}, 회차 {r}. ', d=esc(now_iso()[:10]), r=esc(self.run.name))}"
                     f"{T('원본: {f}, 16_guide_metrics.json, 15_research.yaml', f=f'17_guide{self.sfx}.md')}</div>")
        dd = {"rv": None, "ev": self.ev_json()}
        dd["rv"] = self.rv
        css = re.search(r"<style>(.*?)</style>", render_html.TEMPLATE, re.S).group(1)
        toc = "".join(f'<a href="#sec{c}" id="nav{c}"><span class="tn">{c}</span>{esc(t)}</a>' for c, t in chapters_t)
        ui = {"close": T("닫기"), "more": T("더 보기"), "all": T("전체"), "full": T("리뷰 전문"), "toc": T("목차")}
        page = (GUIDE_TEMPLATE.replace("%LANG%", self.lang).replace("%UI_CLOSE%", ui["close"]).replace("%UI_MORE%", ui["more"])
                .replace("%UI_ALL%", ui["all"]).replace("%UI_FULL%", ui["full"]).replace("%UI_TOC%", ui["toc"])
                .replace("%TITLE%", esc(title)).replace("%CSS%", css + GUIDE_CSS).replace("%TOC%", toc)
                .replace("%BODY%", "\n".join(parts)).replace("%DD%", json.dumps(dd, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")))
        out = f"07_guide{self.sfx}.html"
        (self.run / out).write_text(page, encoding="utf-8")
        write_json(self.run / f"07_guide{self.sfx}_html_numbers.json", {"made_at": now_iso(), "lang": self.lang, "missing_strings": sorted(T.missing),
                                                             "numbers": self.nums, "marker_misses": self.misses,
                                                             "research_misses": self.rmisses, "used_claims": sorted(self.used_claims)})
        size = (self.run / out).stat().st_size
        print(f"{out}을 만들었습니다({size / 1024:.0f}KB, 근거 리뷰 {len(self.rv)}개, 근거 묶음 {len(dd['ev'])}개, 문장 속 숫자 {len(self.nums)}개).")
        for x in self.misses[:20]:
            print(f"  주의: {x}")
        for x in self.rmisses[:20]:
            print(f"  주의: 확인되지 않은 출처 id {x}")
        return 0


def check(run, lang="ko"):
    sfx = "" if lang == "ko" else f"_{lang}"
    page = (run / f"07_guide{sfx}.html").read_text(encoding="utf-8")
    log = json.loads((run / f"07_guide{sfx}_html_numbers.json").read_text(encoding="utf-8"))
    M = json.loads((run / "16_guide_metrics.json").read_text(encoding="utf-8"))
    chk = json.loads((run / "15_research_check.json").read_text(encoding="utf-8"))
    ok_urls = {x["url"] for x in chk["items"] if x["status"] == "verified"}
    sp = run / "23_specs_check.json"
    if sp.exists():                                   # 상품 사양 출처(specs.py check가 다시 열어 확인한 값의 주소)
        ok_urls |= {x["url"] for x in json.loads(sp.read_text(encoding="utf-8"))["items"] if x.get("status") == "verified"}
    errors, warns = [], []
    spans = dict(re.findall(r'data-k="(g\d+)"[^>]*>(.*?)</span>', page))
    for e in log["numbers"]:
        want = M["values"][e["key"]]["text"]
        got = html.unescape(spans.get(e["k"], "\x00없음"))
        if got != want:
            errors.append(f"숫자 {e['k']} {e['key']}: 화면 '{got}', metrics '{want}'")
    errors += [f"문장 속 숫자: {x}" for x in log["marker_misses"]]
    errors += [f"확인되지 않은 출처 id를 씀: {x}" for x in log["research_misses"]]
    left = re.findall(r"\[(?:m|r):[^\]]+\]", re.sub(r'<script.*?</script>', "", page, flags=re.S))
    left = [x for x in left if not re.fullmatch(r"\[[a-z]{3}_\d+\]", x)]
    if left:
        errors.append(f"바꾸지 못한 표시 {len(left)}개: {left[:3]}")
    m = re.search(r'<script type="application/json" id="dd">(.*?)</script>', page, re.S)
    dd = json.loads(m.group(1).replace("<\\/", "</"))
    nrv = len(dd["rv"])
    drills = 0
    for k, e in dd["ev"].items():
        drills += 1
        if len(e["i"]) != min(e["n"], 80):
            errors.append(f"근거 묶음 {k}: 리뷰 {len(e['i'])}개, 전체 {e['n']}개")
        if any(i >= nrv for i in e["i"]):
            errors.append(f"근거 묶음 {k}: 없는 리뷰 번호")
        src = M["ev"][k]
        if [dd["rv"][i]["id"] for i in e["i"]] != src["i"]:
            errors.append(f"근거 묶음 {k}: 리뷰 목록이 metrics와 다름")
    for key, v in M["values"].items():
        mm = re.fullmatch(r"([\d,]+)개", str(v["text"]))
        if mm and v.get("ev") and int(mm.group(1).replace(",", "")) != M["ev"][v["ev"]]["n"]:
            errors.append(f"{key}: 표기 {v['text']}와 근거 묶음 리뷰 수 {M['ev'][v['ev']]['n']}가 다름")
    empty = [k for k in re.findall(r'data-drill="ev" data-key="([^"]+)"', page) if not dd["ev"].get(k, {}).get("n")]
    if empty:
        errors.append(f"리뷰 0개인 근거 묶음을 여는 링크 {len(empty)}개: {empty[:3]}")
    for k in re.findall(r'data-key="([^"]+)"', page):
        if k not in dd["ev"]:
            errors.append(f"없는 근거 묶음을 여는 링크: {k}")
    body = re.sub(r'<script type="application/json" id="dd">.*?</script>', "", page, flags=re.S)
    hrefs = re.findall(r'href="(https?://[^"]+)"', body)
    bad = [h for h in hrefs if html.unescape(h) not in ok_urls]
    srcs = re.findall(r'(?:src)\s*=\s*["\']?(https?://[^"\' >]+)', body) + re.findall(r"url\(\s*['\"]?https?://", body)
    if bad:
        errors.append(f"확인된 출처가 아닌 외부 링크 {len(bad)}개: {bad[:3]}")
    if srcs:
        errors.append(f"외부 참조 {len(srcs)}개: {srcs[:3]}")
    vt = render_html.visible_text(body)
    dots = [vt[max(0, i - 20):i + 20] for i, c in enumerate(vt) if c == "·"]
    if dots:
        errors.append(f"우리 글자에 가운뎃점 {len(dots)}개: {dots[:3]}")
    if lang != "ko":
        if log.get("missing_strings"):
            errors.append(f"번역 문구 파일에 없는 문구 {len(log['missing_strings'])}개: {log['missing_strings'][:3]}")
        han = [vt[max(0, m.start() - 20):m.start() + 20] for m in re.finditer(r"[가-힣]+", vt)]
        if han:
            errors.append(f"한글이 남음 {len(han)}곳: {han[:3]}")
    status = "FAIL" if errors else "PASS"
    out = {"checked_at": now_iso(), "status": status, "numbers_checked": len(log["numbers"]), "evidence_bundles": drills,
           "evidence_reviews": nrv, "source_links": len(hrefs), "external_refs": len(srcs), "middle_dots": len(dots),
           "size_kb": round((run / f"07_guide{sfx}.html").stat().st_size / 1024), "lang": lang, "errors": errors[:100], "warnings": warns}
    write_json(run / f"07_guide{sfx}_html_check.json", out)
    print(f"가이드 HTML 검사: {status}  (숫자 {out['numbers_checked']}개, 근거 묶음 {drills}개, 출처 링크 {len(hrefs)}개, 외부 참조 {len(srcs)}개, 가운뎃점 {len(dots)}개)")
    for e in errors[:30]:
        print(f"  오류: {e}")
    return 1 if errors else 0


GUIDE_CSS = """
.hkpis{display:flex;flex-wrap:wrap;gap:8px;margin:14px 0 6px}
.hkpi{background:var(--card);border:1px solid var(--line);border-radius:8px;padding:10px 14px;flex:1;min-width:min(170px,100%)}
.hkpi .v{font-size:15px;font-weight:800;line-height:1.35;word-break:keep-all}.hkpi .l{font-size:11.5px;color:var(--mut);margin-top:4px;line-height:1.5}
h3{font-size:14.5px;margin:20px 0 8px}h4{font-size:13.5px;margin:14px 0 6px}
section p{font-size:13px;line-height:1.75;color:var(--fg)}
ul.gl,ol.gl{font-size:13px;line-height:1.75;padding-left:20px}
.tldr{background:var(--read-bg);border-left:3px solid var(--read-line);border-radius:0 8px 8px 0;padding:10px 14px;margin:10px 0;font-size:13px;line-height:1.7}
.numlink{cursor:pointer;text-decoration:underline dotted;text-underline-offset:3px;font-weight:700;color:var(--accent)}
.numlink:hover{background:var(--hover)}
sup a.src{font-size:10px;color:var(--accent);text-decoration:none}.srcbad{color:var(--neg-fg);font-size:10px}
.std{border:1px solid var(--line);border-radius:9px;padding:12px 14px;margin:10px 0;background:var(--card)}
.std-h{font-weight:800;font-size:13.5px;display:flex;gap:8px;align-items:center;margin-bottom:8px}
.std-h .n{background:var(--fg);color:var(--card);border-radius:50%;width:22px;height:22px;display:inline-flex;align-items:center;justify-content:center;font-size:11px}
.std-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:10px;font-size:12.5px}
.anatwrap{display:flex;flex-direction:column;align-items:center}svg.anat{width:100%;max-width:300px;height:auto}
#dbk{position:fixed;inset:0;background:rgba(20,20,18,.45);display:none;z-index:50}#dbk.open{display:block}
#dpanel{position:fixed;top:0;right:0;bottom:0;width:min(640px,100%);background:var(--card);z-index:51;transform:translateX(100%);transition:transform .2s;display:flex;flex-direction:column;box-shadow:-8px 0 30px rgba(0,0,0,.2)}
#dpanel.open{transform:none}
.dhead{padding:14px 16px;border-bottom:1px solid var(--line)}#dtit{font-weight:800;font-size:14px}#dsub{font-size:11.5px;color:var(--mut);margin-top:3px}
#dfil{display:flex;gap:6px;margin-top:8px;flex-wrap:wrap}.dfb{font-size:11.5px;border:1px solid var(--line);border-radius:12px;padding:2px 10px;background:var(--card);color:var(--fg);cursor:pointer;font-family:inherit}
.dfb.on{background:var(--fg);color:var(--card)}#dclose{float:right;border:none;background:var(--line2);color:var(--fg);border-radius:6px;padding:4px 10px;cursor:pointer;font-family:inherit}
#dlist{overflow:auto;padding:12px 16px;flex:1}
.rvc{border:1px solid var(--line);border-radius:9px;padding:10px 12px;margin-bottom:9px}
.rvtop{display:flex;gap:8px;align-items:center;font-size:11.5px;color:var(--mut);flex-wrap:wrap}
.rvstar{font-weight:800;border-radius:8px;padding:1px 7px}.rvstar.lo{background:var(--neg-bg);color:var(--neg-fg)}.rvstar.mid{background:var(--mix-bg);color:var(--mix-fg)}.rvstar.hi{background:var(--pos-bg);color:var(--pos-fg)}
.rvti{font-weight:700;font-size:13px;margin:5px 0 3px}.rvbody{font-size:12.5px;color:var(--sub);line-height:1.6}
.rvc mark{background:var(--mark);color:inherit;border-radius:2px}
.dmore{display:block;margin:8px auto;padding:6px 18px;border:1px solid var(--line);border-radius:8px;background:var(--card);color:var(--fg);cursor:pointer;font-family:inherit}
.ct td,.ct th{overflow-wrap:normal;word-break:keep-all}.ct td.tl{min-width:110px}
@media(max-width:640px){.hkpi{min-width:100%}}
"""

GUIDE_TEMPLATE = r"""<!doctype html>
<html lang="%LANG%">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>%TITLE%</title>
<style>%CSS%</style>
</head>
<body>
<nav id="toc" aria-label="%UI_TOC%"><div class="tt">%UI_TOC%</div>%TOC%</nav>
<div class="page">
%BODY%
</div>
<div id="dbk"></div>
<div id="dpanel" role="dialog" aria-modal="true" aria-labelledby="dtit"><div class="dhead"><button id="dclose">%UI_CLOSE% ✕</button><div id="dtit"></div><div id="dsub"></div><div id="dfil"></div></div><div id="dlist"></div></div>
<script type="application/json" id="dd">%DD%</script>
<script>
(function(){
var DD=JSON.parse(document.getElementById('dd').textContent.replace(/<\\\//g,'</'));
var bk=document.getElementById('dbk'),pn=document.getElementById('dpanel'),tit=document.getElementById('dtit'),sub=document.getElementById('dsub'),fil=document.getElementById('dfil'),list=document.getElementById('dlist');
var PAGE=30;
function esc(s){return String(s).replace(/[&<>"]/g,function(c){return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c];});}
function mk(s,q){var h=esc(s);if(q){var qe=esc(q);var i=h.indexOf(qe);if(i>=0)return h.slice(0,i)+'<mark>'+qe+'</mark>'+h.slice(i+qe.length);}return h;}
function pill(s){var c=s<=2?'lo':(s===3?'mid':'hi');return '<span class="rvstar '+c+'">'+'★'+s+'</span>';}
function card(i,q){var r=DD.rv[i];
  return '<div class="rvc"><div class="rvtop">'+pill(r.s)+'<span>'+esc(r.d)+'</span><span><b>'+esc(r.br)+'</b></span><span class="mono">'+esc(r.a)+'</span>'+(r.v?'<span>'+esc(r.v)+'</span>':'')+'<span class="mono">'+esc(r.id)+'</span></div>'
   +(r.t?'<div class="rvti">'+mk(r.t,q)+'</div>':'')+'<div class="rvbody">'+mk(r.b,q)+'</div></div>';}
var cur={ids:[],q:{},shown:0};
function renderMore(){var end=Math.min(cur.shown+PAGE,cur.ids.length);var h='';
  for(var k=cur.shown;k<end;k++){var i=cur.ids[k];h+=card(i,cur.q[String(i)]);}
  var more=document.getElementById('dmorebtn');if(more)more.remove();
  list.insertAdjacentHTML('beforeend',h);cur.shown=end;
  if(end<cur.ids.length)list.insertAdjacentHTML('beforeend','<button class="dmore" id="dmorebtn">%UI_MORE% ('+end+'/'+cur.ids.length+')</button>');}
function openPanel(){bk.classList.add('open');pn.classList.add('open');document.body.style.overflow='hidden';list.scrollTop=0;document.getElementById('dclose').focus();}
function closePanel(){bk.classList.remove('open');pn.classList.remove('open');document.body.style.overflow='';}
function start(ids,q){list.innerHTML='';cur={ids:ids,q:q,shown:0};renderMore();openPanel();}
function openEv(key){var d=DD.ev[key];if(!d)return;tit.textContent=d.t;sub.textContent=d.s;fil.innerHTML='';
  [['all','%UI_ALL%'],['neg','1~3★'],['pos','4~5★']].forEach(function(f,k){var b=document.createElement('button');b.className='dfb'+(k===0?' on':'');
    var sel=f[0]==='all'?d.i:d.i.filter(function(i){return f[0]==='neg'?DD.rv[i].s<=3:DD.rv[i].s>=4;});
    b.textContent=f[1]+' '+sel.length;
    b.onclick=function(){fil.querySelectorAll('.dfb').forEach(function(x){x.classList.remove('on');});b.classList.add('on');start(sel,d.q);};
    fil.appendChild(b);});
  start(d.i,d.q);}
function openRev(i,q){var r=DD.rv[i];tit.textContent='%UI_FULL%';sub.textContent=r.s+'★, '+r.d+', '+r.br;fil.innerHTML='';
  list.innerHTML=card(i,q);openPanel();}
document.addEventListener('click',function(e){var el=e.target.closest('[data-drill]');
  if(el){var t=el.getAttribute('data-drill');
    if(t==='ev')openEv(el.getAttribute('data-key'));else if(t==='rev')openRev(parseInt(el.getAttribute('data-ri'),10),el.getAttribute('data-q'));return;}
  if(e.target===bk)closePanel();});
document.addEventListener('keydown',function(e){if(e.key==='Escape')closePanel();
  if((e.key==='Enter'||e.key===' ')&&e.target.matches&&e.target.matches('[data-drill]')){e.preventDefault();e.target.click();}});
document.getElementById('dclose').addEventListener('click',closePanel);
list.addEventListener('click',function(e){if(e.target.id==='dmorebtn')renderMore();});
var secs=Array.prototype.slice.call(document.querySelectorAll("section[id^='sec']"));
function spy(){var c=secs[0].id;var y=window.scrollY+100;secs.forEach(function(s){if(s.offsetTop<=y)c=s.id;});
  secs.forEach(function(s){var a=document.getElementById('nav'+s.id.slice(3));if(a)a.classList.toggle('on',s.id===c);});}
document.addEventListener('scroll',spy,{passive:true});spy();
window.openEv=openEv;window.openRev=openRev;
})();
</script>
</body>
</html>
"""


def main():
    ap = argparse.ArgumentParser(description="개발 가이드 HTML 만들기와 검사")
    ap.add_argument("mode", choices=["build", "check"])
    ap.add_argument("run", nargs="?")
    ap.add_argument("--lang", default="ko")
    args = ap.parse_args()
    run = resolve_run(args.run)
    sys.exit(R(run, args.lang).build() if args.mode == "build" else check(run, args.lang))


if __name__ == "__main__":
    main()
