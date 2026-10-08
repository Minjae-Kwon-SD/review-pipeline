"""리뷰 리포트 장마다 굵은 한 줄 결론 넣기. 모델을 부르지 않는다.

사용:
  python scripts/report_lines.py packet [회차] --chapters 1,2,3,4,5,6,7,9
    report-writer에게 줄 작은 입력(06_report_concl_packet.md): 장마다 제목, 그 장의 05_tables.md 표 블록(스크립트가 만든 숫자),
    지금 리포트의 첫 '데이터 읽기' 문단. 전체 리포트, 스키마, 룰북은 넣지 않는다.
  python scripts/report_lines.py insert [회차]
    report-writer가 쓴 06_report_conclusions.yaml({장 번호: 문장})을 06_report.md 각 장 제목 바로 아래에 '**결론** 문장' 한 줄로 넣는다.
    이미 결론 줄이 있으면 바꾼다. 다른 줄은 건드리지 않는다. 고치기 전 판은 06_report_before_concl.md로 남긴다.
"""
import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from pipeline_io import die, load_yaml, resolve_run  # noqa: E402

for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass

MARK = "**결론**"
READ = "**데이터 읽기**"
# 장 번호 -> 그 장의 05_tables.md 표 블록 이름(report_template_ko.md의 {{표: 이름}})
BLOCKS = {1: ["요약", "분포"], 2: ["주제별 언급"], 3: ["주제 평가"], 4: ["영향 분석"], 5: ["시간 추이"], 6: ["공출현"],
          7: ["신뢰 신호"], 9: ["ASIN별 비교"]}


def chapters(lines):
    out, cur = {}, None
    for i, l in enumerate(lines):
        m = re.match(r"^## (\d+)\. (.+)$", l)
        if m:
            cur = int(m.group(1))
            out[cur] = {"title": m.group(2).strip(), "line": i}
        elif l.startswith("## "):
            cur = None
    return out


def packet(run, chs):
    lines = (run / "06_report.md").read_text(encoding="utf-8").splitlines()
    tables = (run / "05_tables.md").read_text(encoding="utf-8")
    ch = chapters(lines)
    nums = sorted(ch)
    out = ["# 장마다 한 줄 결론을 쓸 재료", "",
           "장마다 아래 표(스크립트가 만든 숫자)와 지금 리포트의 첫 '데이터 읽기' 문단만 보고, 그 장의 결론을 굵은 한 문장으로 쓴다.",
           "숫자는 아래 표와 문단에 있는 표기 그대로만 쓰고 새로 계산하지 않는다. 원인처럼 쓰지 않는다. 가운뎃점을 쓰지 않는다.", ""]
    for n in chs:
        if n not in ch:
            die(f"{n}장이 06_report.md에 없습니다.")
        start = ch[n]["line"]
        end = ch[nums[nums.index(n) + 1]]["line"] if nums.index(n) + 1 < len(nums) else len(lines)
        body = lines[start + 1:end]
        reading = next((l for l in body if l.startswith(READ)), "")
        out += [f"## {n}. {ch[n]['title']}", ""]
        for b in BLOCKS.get(n, []):
            m = re.search(rf"<!-- 표:{re.escape(b)} -->\n(.*?)\n<!-- /표:{re.escape(b)} -->", tables, re.S)
            if m:
                out += [m.group(1), ""]
        out += [reading, ""]
    (run / "06_report_concl_packet.md").write_text("\n".join(out) + "\n", encoding="utf-8")
    print(f"결론 줄 재료 06_report_concl_packet.md({len((run / '06_report_concl_packet.md').read_text(encoding='utf-8')):,}자, 장 {len(chs)}개)")
    return 0


def insert(run):
    data = load_yaml(run / "06_report_conclusions.yaml") or {}
    concl = {int(k): str(v).strip() for k, v in (data.get("conclusions") or data).items()}
    if not concl:
        die("06_report_conclusions.yaml에 conclusions가 없습니다.")
    p = run / "06_report.md"
    lines = p.read_text(encoding="utf-8").splitlines()
    before = run / "06_report_before_concl.md"
    if not before.exists():
        before.write_text("\n".join(lines) + "\n", encoding="utf-8")
    ch = chapters(lines)
    for n in sorted(concl, reverse=True):
        if n not in ch:
            die(f"{n}장이 06_report.md에 없습니다.")
        text = concl[n]
        if "·" in text:
            die(f"{n}장 결론에 가운뎃점이 있습니다.")
        i = ch[n]["line"]
        new = f"{MARK} {text}"
        if i + 2 < len(lines) and lines[i + 2].startswith(MARK):
            lines[i + 2] = new
        else:
            lines[i + 1:i + 1] = ["", new]
    p.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"결론 줄 {len(concl)}개를 06_report.md에 넣었습니다(장 {', '.join(map(str, sorted(concl)))}).")
    return 0


def main():
    ap = argparse.ArgumentParser(description="리포트 장마다 한 줄 결론")
    ap.add_argument("mode", choices=["packet", "insert"])
    ap.add_argument("run", nargs="?")
    ap.add_argument("--chapters", default="1,2,3,4,5,6,7,9")
    a = ap.parse_args()
    run = resolve_run(a.run)
    sys.exit(packet(run, [int(x) for x in a.chapters.split(",")]) if a.mode == "packet" else insert(run))


if __name__ == "__main__":
    main()
