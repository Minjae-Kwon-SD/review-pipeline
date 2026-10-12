# 아마존 리뷰 분석 파이프라인

> **English summary**
> 1. Pick a product category. The pipeline selects Amazon ASINs, collects their reviews, and builds two HTML deliverables: a review analysis report and a product development guide.
> 2. It runs inside Claude Code. The main session orchestrates, scripts compute every number, and narrow subagents only tag, extract, write sentences, or audit.
> 3. Each step writes a numbered file to `runs/<run>/`, and the next step reads that file. A human approves the key gates (ASINs, topic schema, gold set, sub-issue labels, design-info items).
> 4. Category differences live only in `config/categories/<category>.yaml` and in human-approved schemas, so a new category needs no category-specific code.
> 5. Reviews come from a shared review database through MCP. Paid scraping is off by default.

카테고리 하나를 정하면 상품(ASIN)을 고르고 리뷰를 모아 HTML 두 개를 만든다.

- **리뷰 분석 리포트**: 리뷰를 주제별로 나누고, 주제마다 좋게 말했는지 나쁘게 말했는지(감성)를 센다. 리뷰는 별점마다 비슷한 수로 모으기 때문에 실제보다 낮은 별점이 많다. 그래서 실제 아마존 별점 비율에 맞춰 다시 센 값(가중)을 함께 보여 준다.
- **제품 개발 가이드**: 리뷰에서 뽑은 설계 정보, 시장 데이터, 웹 조사를 묶어 무엇을 어떻게 만들지 기준을 제시한다.

처음 보는 말(감성, 가중, 정답 세트 등)은 [11. 용어](#11-용어)에 모아 두었다. 구조와 설계 이유는 [docs/walkthrough.md](docs/walkthrough.md)에 더 자세히 있다. 이 문서의 결과 숫자는 `python scripts/doc_facts.py build`가 실제 회차 파일에서 모은 값이고, 출처는 [docs/doc_facts.md](docs/doc_facts.md)에 있다.

## 1. 결과물

| 결과물 | 파일 | 내용 |
|---|---|---|
| 리뷰 분석 리포트 | `runs/<회차>/06_report.html` | 13개 장. 숫자, 막대, 인용을 누르면 근거가 된 리뷰 원문이 펼쳐진다(드릴다운). 리뷰를 직접 걸러 보는 리뷰 탐색기 포함 |
| 제품 개발 가이드 | `runs/<회차>/07_guide.html` | 시장 개요, 경쟁사, 문제, 포지셔닝, 한 장 요약, 데이터와 방법. 숫자마다 근거 리뷰 묶음, 웹 조사 주장마다 출처 링크 |
| 리뷰 분석 리포트(영어) | `runs/<회차>/06_report_en.html` | 필요할 때 한국어판에서 만든다(`render_html.py build <회차> --lang en`) |

예시: `runs/hairremovalcream-2026-10-10/06_report.html`, `runs/hairremovalcream-2026-10-10/07_guide.html`(문장 원문은 같은 폴더의 `06_report.md`, `17_guide.md`)

HTML은 데이터까지 담은 파일 하나라서 다른 파일이나 인터넷 연결 없이 열린다. HTML은 모델이 아니라 스크립트가 만든다. 숫자는 JSON에서, 문장은 검사를 통과한 Markdown에서 가져온다.

## 2. 시작하기

### 필요한 것

- Claude Code(메인 세션은 상위 모델로 연다. 예: `claude --model opus`)
- Python과 PyYAML(`python -m pip install pyyaml`)
- `.mcp.json`에 적힌 MCP 서버: 공유 리뷰 DB(amz-review), 시장 데이터(spd-amz-market), 순위 데이터(spd-amz-rank)
- 환경 변수 `AMZ_REVIEW_TOKEN`: 리뷰 DB 토큰. 파일에는 값을 적지 않고 환경 변수만 참조한다.
- 카테고리 설정 `config/categories/<카테고리>.yaml`

### 한 회차 돌리기

```text
/review-run hairremovalcream 2026-10-10
```

인자는 카테고리와 날짜다. 회차 이름은 `카테고리-날짜`(예: `hairremovalcream-2026-10-10`)이고, 결과는 `runs/<회차>/`에 쌓인다. 카테고리 설정 파일은 카테고리 인자의 첫 부분으로 찾는다(`hairremovalcream`이면 `config/categories/hairremovalcream.yaml`, `perfume-db`면 `config/categories/perfume.yaml`). 같은 회차를 다시 부르면 `state.json`을 보고 끝나지 않은 첫 단계부터 이어서 한다. 단계별 명령은 [.claude/commands/review-run.md](.claude/commands/review-run.md)에 있다.

사람 없이 명령 한 줄로 돌릴 때(헤드리스)는 권한을 통째로 열지 않고, 필요한 도구만 허용한다.

```text
claude -p --model opus --allowedTools "Bash(python scripts/*)" "Edit(/runs/**)" "Write(/runs/**)" --max-turns 200 --output-format json < prompt.txt
```

헤드리스 실행이 끝날 때마다 결과 JSON의 duration_ms, total_cost_usd, num_turns를 `runs/<회차>/costs.jsonl`에 한 줄로 남긴다(`scripts/log_cost.py`). ⏸ 관문에 닿으면 그 실행은 거기서 끝나고, 사람이 답한 뒤 다시 부르면 이어서 한다.

### 단계 순서

| 단계 | 하는 일 | 누가 |
|---|---|---|
| 0 수집 | 공유 리뷰 DB에서 후보 ASIN과 리뷰, 실제 별점 분포를 받음 | `collect.py`, asin-selector |
| 1 입력 검사 | 형식 검사, 정답 세트와 스키마 표본 고르기 | `check_inputs.py`, `eval_gold.py pick` |
| 2~3 스키마 | 표본 리뷰로 주제 초안을 만들고 사람이 승인 | schema-drafter, ⏸ 사람 |
| 4 정답 세트 | 사람이 정답 세트를 직접 태깅(태거 결과를 보기 전에) | ⏸ 사람 |
| 5~6 태깅과 검사 | 묶음마다 동시에 태깅, 인용 기계 검사, 표본 감사, 정답 세트 채점 | review-tagger(sonnet), `audit_quotes.py`, evidence-auditor, `eval_gold.py` |
| 6-1~6-3 세부 이슈 | 주제마다 세부 이슈 목록 제안, 사람 승인, 라벨 붙이기와 감사, 안전 증상 판정 | issue-labeler, ⏸ 사람, issue-tagger(sonnet), evidence-auditor, `issues.py` |
| 7 집계 | 별점 보정 가중 집계, 리포트의 모든 숫자와 표 | `weight.py` |
| 8~9 리포트 | 문장 쓰기, 기계 검사와 감사 | report-writer, `audit_quotes.py`, evidence-auditor |
| 10~11 시간과 HTML | 시간 표, 리포트 HTML 만들기와 검사 | `timing_report.py`, `render_html.py` |
| 12~16 가이드 재료 | 시장 데이터, 설계 정보 항목 제안과 승인, 추출과 감사, 웹 조사와 출처 확인, 가이드 숫자 | `market.py`, detail-schema-drafter, ⏸ 사람, detail-extractor(sonnet), evidence-auditor, benchmark-researcher, `research.py`, `guide_metrics.py` |
| 17~19 가이드 | 문장 쓰기, 검사와 감사, HTML | guide-writer, `guide_check.py`, evidence-auditor, `render_guide_html.py` |
| 20~22 다른 언어판 | 번역 준비, 줄마다 번역, 기계 검사, 뜻 감사, HTML | `translate_prep.py`, report-translator, evidence-auditor, `render_html.py --lang en` |

### 사람이 정하는 관문(⏸)

1. **ASIN 확인**: asin-selector가 고른 상품 목록을 보고 확정한다.
2. **스키마 승인**: 주제 초안을 고쳐 `03_schema_approved.yaml`로 승인한다.
3. **정답 세트 태깅**: 정답 세트 리뷰를 태깅 화면(`gold/gold_tagging.html`)에서 직접 태깅한다. 태거 결과를 보기 전에 한다.
4. **세부 이슈 라벨 승인**: 주제마다 제안된 라벨 목록을 고쳐 `07a_issues_approved.yaml`로 승인한다.
5. **설계 정보 항목 승인**: 가이드용 추출 항목 초안을 고쳐 `13_detail_schema_approved.yaml`로 승인한다.

이 밖에 시험 태깅 결과를 보고 전체 태깅을 계속할지, 정답 세트 점수가 기준에 못 미칠 때 어떻게 할지도 사람이 정한다. 관문에 닿으면 메인 세션은 상태를 `needs_human`으로 남기고 멈춘다. 사람이 답하기 전에는 대신 정하지 않는다.

### 다시 돌리기와 상한

- `python scripts/stage_plan.py plan <회차>`가 단계마다 입력 파일, 지시문, 코드가 바뀌었는지(해시)를 보고, 바뀐 단계와 그 뒤 단계만 다시 한다.
- 대량 작업 방식은 단계마다 `config/stages.yaml`의 method로 정한다. 설계 정보 추출은 작업자마다 작업 파일 하나를 주는 방식(`stage_packet.py`)이고, 태깅과 이슈 라벨은 묶음마다 에이전트 하나다.
- 동시 실행 수(태깅, 대량 작업, 상위 모델 작성자와 감사자), 작업자당 묶음과 리뷰 수, 재시도 횟수의 상한도 `config/stages.yaml`에 있다.

## 3. 폴더 구조

```text
CLAUDE.md                     원칙, 실행 흐름, 파일 계약(누가 어떤 파일을 쓰나), 가중 계산 규칙
README.md                     이 문서
.mcp.json                     MCP 서버 주소(토큰은 환경 변수 참조만)
.claude/
  agents/                     에이전트 정의(역할, 입력, 금지, 출력 형식, 도구 권한, 모델과 effort)
  commands/review-run.md      /review-run 단계별 명령
  hooks/timing.py             에이전트 시작과 끝을 timing.jsonl에 기록
  settings.json               Hook 등록과 허용, 금지 규칙
config/
  pipeline.yaml               유료 수집 스위치(기본 꺼짐), 별점 묶음, 경고 기준
  stages.yaml                 단계마다 입력, 출력, 작업 방식, 상한
  categories/<카테고리>.yaml  카테고리 설정(검색어, 제목 규칙, 리포트와 시장, 가이드 설정)
  topics_common.yaml          모든 카테고리에 공통인 주제
  detail_rules.yaml           설계 정보 항목의 공통 경계 규칙
  report_template_ko.md       리포트 장 구성
  guide_style.css             가이드 HTML 디자인
  i18n/report_ui_en.yaml      리포트 화면 문구 영어(키는 한국어 원문)
scripts/                      숫자를 만드는 스크립트 전부(모델 호출 없음)
tests/test_scripts.py         가짜 회차로 스크립트 결과를 손계산과 맞춰 보는 시험
tests/fixture/                시험용 작은 입력
docs/
  walkthrough.md              설명서(구조와 이유, 시키는 법, 시간)
  multi_agent_design_v2.md    대량 작업 방식 설계
  decisions_log.md            정한 것과 이유, 알게 된 함정
  doc_facts.md, .json         문서 속 숫자와 출처
  mcp_tools.md                MCP 도구 메모
runs/
  CURRENT                     지금 회차 이름(시간 기록 Hook이 읽음)
  <회차>/                     회차마다 단계 파일 전부
```

리뷰 원문, 정답 세트(`gold/`), MCP 응답 원문, 비용 기록은 `.gitignore`로 저장소에서 뺀다.

## 4. 에이전트

모든 에이전트는 자기 출력 파일만 쓰고, 다음 단계는 그 파일 경로를 받아 읽는다. 에이전트 정의는 모두 `model: inherit`라 메인 세션의 모델을 따르고, 태깅과 추출처럼 양이 많은 일만 호출할 때 sonnet을 준다. effort는 에이전트 정의 파일 머리말(frontmatter)에 적혀 있다.

| 에이전트 | 하는 일 | 모델 | effort | 도구 | 왜 스크립트가 아니라 에이전트인가 |
|---|---|---|---|---|---|
| asin-selector | 후보 표에서 카테고리에 맞는 상품을 골라 `01_asins.csv` | 상위 | medium | Read, Write | 상품 제목만으로 같은 카테고리인지(바디 미스트, 세트 등) 가려야 함 |
| schema-drafter | 표본 리뷰를 읽고 공통 주제에 카테고리 전용 주제를 더한 스키마 초안 | 상위 | high | Read, Write | 리뷰에서 반복되는 불만과 칭찬의 범주를 찾는 일은 규칙으로 못 함 |
| review-tagger | 묶음 하나(약 50개)의 리뷰마다 주제, 감성, 원문 인용 | sonnet | medium | Read, Write | 문장의 뜻을 읽고 승인된 주제에 맞추는 일. 양이 많아 빠른 모델로 동시에 |
| issue-labeler | 주제 하나의 표본 인용으로 세부 이슈 목록 제안 | 상위 | high | Read, Write | "금방 날아감", "처음부터 약함"처럼 주제 안의 하위 범주를 찾는 판단 |
| issue-tagger | 승인된 세부 이슈 목록으로 인용마다 라벨 | sonnet | medium | Read, Write | 인용의 뜻을 라벨 정의에 맞추는 일 |
| report-writer | 스크립트가 만든 숫자와 표, 태그 인용으로 리포트 문장 | 상위 | high | Read, Write | 숫자를 읽고 해석하는 문장. 숫자는 새로 계산하지 않고 옮기기만 |
| evidence-auditor | 태그, 라벨, 추출 값, 리포트와 가이드 문장, 번역을 원문과 대조해 판정 | 상위 | high | Read, Grep, Glob(**읽기 전용**) | 뜻이 맞는지 보는 판단. 만든 쪽과 분리해 고치지 못하게 함 |
| detail-schema-drafter | 리뷰에서 뽑을 설계 정보 항목(바른 부위, 둔 시간 등) 초안 | 상위 | high | Read, Write | 제품 설계에 쓸 정보가 무엇인지 리뷰에서 찾는 판단 |
| detail-extractor | 승인된 항목으로 리뷰마다 값과 원문 인용 | sonnet | medium | Read, Write | 자유롭게 쓴 문장에서 값을 뽑는 일 |
| benchmark-researcher | 공개 웹 자료로 시장 규모, 업계 구성, 규제, 시험 기준 조사(주장마다 출처 URL과 원문 문장) | 상위 | high | WebSearch, WebFetch, Read, Write | 검색과 출처 읽기. 출처는 `research.py`가 다시 열어 확인 |
| guide-writer | 가이드 숫자와 확인된 웹 주장만 보고 가이드 문장 | 상위 | high | Read, Write | 기준과 권고를 문장으로 쓰는 일 |
| report-translator | 감사를 통과한 한국어 리포트 문장을 줄마다 다른 언어로 | 상위 | high | Read, Write | 뜻을 지키는 번역. 숫자와 구조 표시는 그대로 |
| product-spec-collector | 상품마다 브랜드 사이트와 소매점 상품 페이지에서 사양을 출처 문장과 함께 모음 | 상위 | high | WebSearch, WebFetch, Read, Write | 같은 상품 페이지를 찾아 맞추는 일. 값은 `specs.py`가 다시 열어 확인 |

메인 세션은 지휘만 한다. 단계 순서를 정하고, 스크립트를 실행하고, 에이전트를 부르고, 감사 결과를 저장하고, 관문에서 멈춘다.

### 모델과 effort를 나눈 기준

- **판단은 상위 모델, effort high.** 무엇을 고르고, 어떤 범주로 나누고, 문장을 쓰고, 맞는지 확인하는 일이다.
- **반복은 sonnet, effort medium.** 태깅, 라벨, 추출처럼 같은 일을 수천 번 하는 일이다. 정답 세트로 medium과 high를 비교했을 때 점수 차이가 거의 없어 medium으로 둔다.
- **asin-selector는 medium.** 상품 제목만 보는 가벼운 판단이다.
- **감사자는 high.** 일부러 틀리게 만든 태그를 섞어 high와 xhigh를 비교했더니 잡아낸 수가 같아 high로 되돌렸다. max는 쓰지 않는다.
- **숫자는 모델이 아니라 스크립트가 계산한다.**

시험 방법과 결과는 [docs/decisions_log.md](docs/decisions_log.md)에 있다.

### 에이전트끼리 일을 넘기는 방식

에이전트끼리는 서로 메시지를 주고받지 않는다. 앞 단계가 `runs/<회차>/`에 파일을 쓰면, 메인 세션이 다음 에이전트에게 그 파일 경로를 넘긴다.

- **번호 붙은 파일**: 파일 이름 앞 번호가 단계 순서다.

| 번호 | 단계 | 대표 파일 |
|---|---|---|
| `00`~`02` | 후보 고르기, 상품 확정, 리뷰 수집 | `00_candidates.csv`, `01_asins.csv`, `02_reviews.csv` |
| `03` | 주제 스키마 | `03_schema_approved.yaml` |
| `04` | 태깅, 태그 검사와 감사, 정답 세트 채점 | `04_tags.jsonl`, `04_tag_audit.yaml`, `04_gold_eval.json` |
| `05` | 숫자 집계 | `05_metrics.json`, `05_tables.md` |
| `06` | 리뷰 리포트 | `06_report.md`, `06_report.html` |
| `07` | 리포트 감사, 세부 이슈(`07a` 목록, `07b` 라벨, `07c` 안전 증상) | `07_audit.yaml`, `07a_issues_approved.yaml`, `07b_issue_labels.jsonl` |
| `13`~`14` | 설계 정보 항목과 추출 | `13_detail_schema_approved.yaml`, `14_details.jsonl` |
| `15`~`16` | 웹 조사, 가이드 숫자 | `15_research.yaml`, `16_guide_metrics.json` |
| `17`~`18` | 가이드 문장과 검사 | `17_guide.md`, `18_guide_audit.yaml` |
| `23` | 상품 사양 | `23_specs_verified.json` |

가이드 HTML 이름 `07_guide.html`의 `07`은 단계 번호가 아니다.

- **누가 무엇을 쓰고 읽는지**: [CLAUDE.md](CLAUDE.md)의 "파일 계약" 표에 파일마다 한 줄씩 적어 두었다. 에이전트 지시문에도 읽을 파일과 쓸 파일이 정해져 있어, 정해진 파일만 읽고 자기 출력 파일만 쓴다.
- **같은 긴 파일을 여러 에이전트가 각자 읽지 않게**: 큰 입력은 스크립트가 미리 잘라 준다. 태거는 묶음 하나의 리뷰만 담은 `04_tag_input/<묶음>.csv`만 읽고, 설계 정보 추출 작업자는 필요한 기준 원문과 맡은 대상만 담은 작업 파일(`packets/<종류>_w<번호>.md`) 하나만 읽는다. 처음에는 여러 에이전트가 같은 긴 파일을 각자 읽으면서 토큰이 많이 들고 해석도 조금씩 달라졌다. 그래서 각 에이전트가 읽는 양을 줄이고, 같은 기준은 같은 글자 그대로 보게 했다.
- **숫자와 문장 분리**: 숫자는 `05_metrics.json`, `16_guide_metrics.json`에만 있다. 문장 파일은 숫자를 새로 쓰지 않고 그 값을 옮기거나 키로 가리킨다(가이드의 `[m:키]`).
- **상태와 이어 하기**: `state.json`에 단계마다 상태와 입력 해시가 남는다. 입력이 같으면 그 단계는 건너뛰고, 중간에 끊기면 끝나지 않은 첫 단계부터 다시 한다.

## 5. 스크립트

| 스크립트 | 하는 일 |
|---|---|
| `collect.py` | 공유 리뷰 DB에서 후보와 리뷰, 별점 분포 받기(유료 수집은 설정과 확인 인자가 둘 다 있어야 돎) |
| `check_inputs.py` | 회차 입력 파일과 스키마 검사 |
| `eval_gold.py` | 정답 세트 고르기, 태깅 화면, 형식 검사, 채점, 감사 표본 |
| `tag_batches.py` | 태깅 묶음 나누기 |
| `audit_quotes.py` | 태그와 리포트 기계 검사(인용이 원문에 글자 그대로 있는지, 숫자가 metrics에 있는지) |
| `issues.py` | 세부 이슈 표본, 초안 합치기, 라벨 묶음, 라벨 검사와 개수, 안전 증상 정리 |
| `weight.py`, `sections.py` | 별점 보정 가중 집계, 리포트의 모든 숫자와 표 |
| `render_html.py` | 리뷰 리포트 HTML 만들기와 검사(`--lang en`이면 영어판) |
| `market.py`, `market_build.py` | 무료 시장 데이터(spd-amz-market) 받기와 표 |
| `detail.py` | 설계 정보 표본, 항목 검사와 승인, 추출 묶음, 추출 검사와 감사 |
| `research.py` | 웹 조사 출처를 다시 열어 원문 문장 확인 |
| `guide_metrics.py` | 가이드의 숫자, 표, 근거 리뷰 묶음 |
| `guide_check.py`, `guide_diff.py` | 가이드 문장 기계 검사, 바뀐 줄만 뽑기 |
| `render_guide_html.py` | 가이드 HTML 만들기와 검사 |
| `translate_prep.py` | 번역 원문 준비, 번역 기계 검사(줄 수, 숫자, 인용, 남은 한글) |
| `timing_report.py`, `log_cost.py` | 단계 시간과 상태 기록, 헤드리스 실행 비용 기록 |
| `robustness.py` | 견고성 점검(리뷰 다시 뽑기, 상품 하나씩 빼고 다시 계산) |
| `specs.py` | 상품 사양 수집 준비, 출처를 다시 열어 값 확인 |
| `stage_plan.py` | 다시 할 단계만 고르기(입력 해시), 단계 정의의 출력 겹침과 상한 검사, 작업자 배정 |
| `stage_packet.py` | 작업자마다 작업 파일 하나(필요한 기준 원문, 대상, 출력 경로, 검사, 상한) |
| `report_lines.py` | 리포트 장마다 한 줄 결론을 쓸 작은 입력 만들기와 넣기 |
| `doc_facts.py` | 문서 속 숫자를 회차 파일에서 모으고 대조 |
| `pipeline_io.py`, `mcp_http.py` | 공용 입출력, MCP 서버 HTTP 호출(토큰은 환경 변수에서만 읽음) |

## 6. 원칙

- **숫자는 스크립트가 계산하고 모델은 문장만 쓴다.** 리포트와 가이드의 숫자는 모두 `05_metrics.json`, `16_guide_metrics.json`의 값이고, 기계 검사가 문장 속 숫자를 그 값과 대조한다.
- **감사자는 읽기만 하고 고치지 않는다.** evidence-auditor는 Read, Grep, Glob만 갖고 판정 YAML만 돌려준다. 고치는 일은 그 결과물을 만든 에이전트가 다시 한다.
- **카테고리 차이는 config와 승인된 스키마에만 있다.** 에이전트 지시문에는 특정 카테고리 이야기가 없다. 주제, 세부 이슈, 설계 정보 항목은 파이프라인이 리뷰에서 제안하고 사람이 승인한다.
- **룰북을 한곳에 모은다.** 태깅 규칙(주제 정의, 넣을 것과 뺄 것, 헷갈리는 예)은 승인된 스키마와 정답 세트 태깅 메모에 모여 있고, 태거와 감사자가 같은 룰북을 본다.
- **정답 세트는 에이전트에게 보이지 않는다.** 스키마를 만들 때 정답 세트 리뷰를 빼고, 에이전트는 gold 폴더를 읽지 못하게 막아 둔다(헤드리스 실행도 같다). 정답을 보고 태깅하면 점수가 부풀기 때문이다.
- **유료 수집은 기본으로 꺼져 있다.** `config/pipeline.yaml`의 `paid.enabled`와 실행 인자 `--confirm-paid`가 둘 다 있어야 돈다. 에이전트나 메인 세션이 유료 도구를 직접 부르지 못하게 `.claude/settings.json`의 permissions deny에 `mcp__amz-review__scrape_reviews`를 넣어 두었다. 유료 수집을 쓰려면 이 줄을 빼고 설정을 켠다.
- **근거가 없으면 지어내지 않는다.** 확인하지 못한 웹 주장은 가이드에 쓰지 않고, 단위를 모르는 시장 칸은 "단위 미확인"으로 적는다.

## 7. 예시 실행 결과(hairremovalcream-2026-10-10)

제모 크림 회차다. 저장소에는 리포트와 가이드의 HTML과 문장 원문(md)만 넣고, 리뷰 원문, 정답 세트, 비용 기록, 수집 응답 원문은 넣지 않는다.

### 데이터

- ASIN 8개, 리뷰 2,002개(본문이 빈 1개 제외), 태그 6,288개
- 리뷰는 유료 수집으로 받음: 호출 41번(시험 호출 포함), 호출 시간 합 27.6분
- 승인 주제 14개(공통 11개에 카테고리 전용을 더함), 세부 이슈 라벨 80개, 설계 정보 항목 15개(추출 값 2,593개)
- 시장 데이터 호출 40번(무료), 웹 조사 주장 51개 중 39개 출처 확인, 상품 사양 확인 값 116개

### 검사

| 무엇 | 결과 |
|---|---|
| 정답 세트(리뷰 32개, 태그 104개) | sonnet 주제 F1 0.87(기준 0.80). 감성 방향 일치 97.0%(67개 중 65개, 기준 90%), 혼합 일치 18.2%(22개 중 4개, 기준 없음), 감성 전체 일치 77.5%. 감성을 방향과 혼합으로 나눠 보는 방식은 이번 결과를 본 뒤 정했으므로 통과로 단정하지 않고, 다음 회차에 새 정답 세트로 다시 잰다 |
| 태그 표본 감사 | 144개 중 FAIL 1개(0.7%). 감사자가 확인하지 못한 태그(UNVERIFIED 1개)와 태거가 빠뜨린 태그(18개)까지 틀린 것으로 치면 12.3% |
| 세부 이슈 라벨 감사 | 150개 중 FAIL 2개(1.3%) |
| 설계 정보 추출 감사 | 150개 중 FAIL 1개(0.7%) |
| 리뷰 리포트 HTML | 화면 숫자 900개와 드릴다운 378개를 원본과 대조해 모두 일치, 외부 참조 0 |
| 개발 가이드 HTML | 문장 속 숫자 155개, 근거 묶음 187개, 출처 링크 124개를 대조해 모두 일치 |
| 견고성 점검 | 리뷰를 다시 뽑아 2,000번 계산해도 불만 1위(피부 반응)가 99.9%에서 그대로였다. 상품을 하나씩 빼고 다시 계산하면 8번 중 4번 결론이 바뀌었다. 불만 1위는 매번 그대로이고, 피부 반응이 상품 절반 이상에서 가장 큰 약점인지만 흔들렸다 |
| 스크립트 시험 | 378개 확인 통과 |

감성 전체 일치가 낮은 까닭은 대부분 혼합 기준 차이다. 정답 세트를 만든 사람은 "조금 따가웠다", "일부만 지워졌다" 같은 약한 불만을 혼합으로 봤고, 스키마 규칙은 피부 반응을 겪었으면 부정, 결론이 반반일 때만 혼합으로 보게 되어 있었다. 긍정과 부정을 정반대로 본 경우는 드물었다. 혼합 기준은 다음 회차 태깅 전에 정한다([docs/decisions_log.md](docs/decisions_log.md)).

### 시간

| 무엇 | 값 |
|---|---|
| 에이전트 호출 | 174번 |
| 에이전트가 하나라도 돌던 시간(겹친 구간은 한 번만) | 202분 |
| 에이전트마다 걸린 시간을 모두 더한 값(동시에 돈 시간이 겹쳐 실제 걸린 시간보다 큼) | 435분 |
| 유료 수집 호출 시간 | 27.6분 |

리포트와 가이드의 첫 감사 통과본까지는 사람 대기를 빼고 약 3시간 반이 걸린 것으로 어림한다. 에이전트가 돌던 시간, 유료 수집 시간, 스크립트 시간 어림을 더한 값이다. 위 표의 에이전트 시간에는 effort 시험, 실패 묶음 재시도, 참고 리포트와 비교한 뒤 다시 쓰기와 감사 반복까지 모두 들어 있다. 이 회차는 관문의 사람 대기를 `timing.jsonl`에 따로 표시하지 않아 정확한 값이 아니다. 다음 회차부터 AI 작업 시간, 정답 세트 태깅 시간, 사람 응답 대기 시간을 나눠 잰다.

### 비용

대화 세션으로 돌려 헤드리스 실행 기록(`costs.jsonl`)이 없다. 유료 수집 응답에는 비용 칸이 없어 금액은 수집 서비스 계정에서만 볼 수 있다.

## 8. 알려진 한계

- **정답 세트 점수는 규칙을 다듬은 리뷰로 잰 점수다.** 같은 리뷰를 보며 규칙을 고친 뒤 채점했으니, 시험 문제를 보고 공부한 셈이라 실제보다 높게 나올 수 있다.
- **ASIN은 매출 순위로 고르고, 리뷰가 모자란 상품만 유료로 받는다.** 카테고리 검색어의 매출 상위 후보에서 ASIN을 고르고(`collect.py rank`, 사람이 확인), 공유 리뷰 DB에 리뷰가 100개 미만인 상품만 유료 수집으로 리뷰를 받는다. 유료 수집을 켜지 않으면 DB에 리뷰가 많은 상품 위주가 된다. 검색어 몇 개의 상위 후보라 카테고리 전체를 대표하지는 않는다.
- **모은 리뷰는 실제보다 낮은 별점이 많다.** 별점마다 비슷한 수로 모으기 때문이다. 별점 묶음 가중으로 실제 비율에 맞춰 다시 세지만, 표본이 하나도 없는 별점 묶음은 보정할 수 없어 그 비율을 리포트에 적는다.
- **시장 데이터 칸 중 단위를 모르는 것이 있다.** 단위가 문서에 없는 칸은 "단위 미확인"으로 두고 크기를 단정하지 않는다.
- **상품 사양은 일부만 있다.** 브랜드 사이트와 소매점 상품 페이지에서 확인되는 값만 모으고, 측정한 사양(사이즈표 등)은 없다. 상품이 적으면 사양과 불만의 관계는 말하지 않고 나란히 놓기만 한다.
- **영어판은 리뷰 리포트만 있다.** 개발 가이드는 한국어판만 만든다.

### 다음 회차에 고칠 것

1. 태깅 전에 혼합 기준을 정하고, 새 정답 세트로 다시 잰다.
2. 정답 세트를 규칙을 다듬는 용도와 채점하는 용도로 나눈다.
3. AI 작업 시간, 정답 세트 태깅 시간, 사람 응답 대기 시간을 따로 기록한다.
4. 관문은 남기고, 그 밖에 사람에게 묻는 확인 질문을 줄인다.
5. 상품 고르는 방식을 다시 정한다. 지금은 검색어 매출 상위에서 고르는데, 누구를 위한 제품인지(성별, 부위 등)를 먼저 정하고 고를지 검토한다.

## 9. 새 카테고리 추가

1. `config/categories/<카테고리>.yaml` 하나를 쓴다. `config/categories/hairremovalcream.yaml`이나 `config/categories/perfume.yaml`을 본떠 검색어(`keywords`), 상품 제목 규칙(`title_include`, `title_exclude`, `kind_rules`), 리포트 제목, 시장 노드(`market`), 가이드 설정(`guide`)을 적는다.
2. `/review-run <카테고리> <날짜>`처럼 부른다.
3. 주제(스키마), 세부 이슈, 설계 정보 항목은 파이프라인이 그 카테고리 리뷰에서 제안하고, 사람이 관문에서 고쳐 승인한다. 카테고리마다 에이전트 지시문이나 스크립트를 따로 고칠 필요는 없다.
4. 정답 세트는 새 카테고리에서 다시 태깅한다. 다른 언어판이 필요하면 이름표 `runs/<회차>/i18n_names_en.yaml`을 승인된 이름의 번역으로 만든다.

## 10. 시험

```text
python tests/test_scripts.py
```

가짜 회차(`tests/fixture/`)로 가중 집계, 인용 검사, 정답 세트 채점 등 스크립트 결과를 손계산과 맞춰 본다. 모델을 부르지 않는다.

## 11. 용어

리포트와 이 문서에서 쓰는 말이다. 오른쪽 칸은 구조와 논리의 본보기로 삼은 참고 리포트(스크럽 리뷰 분석 리포트와 개발 가이드)에서 같은 개념을 부르는 말이다. 감성, 주제, 태그, 가중 비율은 참고 리포트에도 같은 개념으로 있고, 감성을 긍정, 부정, 혼합, 중립 네 가지로 주제마다 매기는 방식도 같다.

### 리뷰를 나누고 세는 말

| 용어 | 뜻 | 참고 리포트 |
|---|---|---|
| 회차 | 한 번 돌린 실행 하나. 그 실행의 파일은 모두 `runs/<회차>/`에 쌓인다 | |
| 카테고리 | 분석할 상품 종류(예: 제모 크림). 설정 파일 하나로 정한다 | category |
| 주제 | 리뷰를 나눠 세는 칸(예: 피부 반응, 털 제거 효과). 공통 주제에 카테고리 전용 주제를 더해 사람이 승인한다 | Subcategory, topic |
| 태그 | 리뷰 하나에서 주제 하나를 잡은 기록. 리뷰가 주제 셋을 말하면 태그도 셋이다. 태그마다 감성과 원문 인용이 붙는다 | Tags (review × topic) |
| 감성 | 리뷰가 그 주제를 좋게 말했는지 나쁘게 말했는지. 긍정, 부정, 혼합, 중립 네 가지이고 주제마다 따로 매긴다. 그래서 리뷰 하나에 감성이 여럿일 수 있다 | Sentiment (Positive, Negative, Mixed, Neutral) |
| 혼합(mixed) | 한 주제 안에 좋은 말과 나쁜 말이 함께 있는 경우. 예: "털은 빠지는데 두 번 발라야 했다" | Mixed |
| 중립 | 평가 없이 사실만 말한 경우. 예: "바르고 기다렸다가 닦아 냈다" | Neutral |
| 언급 수 | 그 주제가 나온 태그 수. 모은 그대로 센 값이다 | Mentions |
| 부정 비율 | 그 주제 태그 가운데 부정의 비율. 모은 그대로 센 값이라 "무엇을 불평하는가"로 읽는다 | Neg % |
| 가중(별점 보정) | 별점마다 비슷한 수로 모은 리뷰를 실제 아마존 별점 비율에 맞춰 다시 세는 것. 실제보다 적게 모인 별점(대개 높은 별점)의 리뷰에 더 큰 무게를 준다 | weighted |
| 가중 부정 비율 | 가중으로 다시 센 부정 비율. "얼마나 흔한가"로 읽는다 | Weighted neg % |
| 부정 언급 리뷰어(가중) | 그 주제를 나쁘게 말한 리뷰어가 전체 리뷰어에서 차지하는 비율(가중) | Reviewers w/ negative mention |
| 세부 이슈 | 주제 안의 더 작은 갈래(예: 피부 반응 안의 "타거나 따가운 느낌", "자극, 붉어짐이나 가려움"). 파이프라인이 제안하고 사람이 승인한다 | |
| 설계 정보 항목 | 가이드를 쓰려고 리뷰에서 뽑는 값(예: 바른 부위, 둔 시간). 사람이 승인한 항목만 뽑는다 | 설계 정보 추출 |
| 드릴다운 | 리포트의 숫자, 막대, 인용을 누르면 근거가 된 리뷰가 펼쳐지는 기능 | 같은 기능 있음 |

### 정확도와 검사에 쓰는 말

| 용어 | 뜻 | 참고 리포트 |
|---|---|---|
| 룰북 | 태깅 기준을 모은 것(주제 정의, 넣을 것과 뺄 것, 헷갈리는 예). 승인된 스키마와 정답 세트 태깅 메모에 있고, 태거와 감사자가 같은 룰북을 본다 | written guide |
| 정답 세트 | 사람이 직접 태깅한 채점용 리뷰(제모 크림 회차는 32개). 별점마다 고르게 스크립트가 뽑는다. 에이전트는 이 정답을 보지 못한다 | |
| 참고 리포트 | 구조와 논리의 본보기로 받은 스크럽 리뷰 분석 리포트와 개발 가이드. 숫자가 아니라 장 구성, 결론을 쓰는 방식, 계산 규칙을 맞춘다 | |
| 주제 F1 | 정답 세트에서 주제를 얼마나 맞게 잡았는지 보는 점수. 놓친 주제와 괜히 붙인 주제를 함께 따지고, 1에 가까울수록 정답 세트와 같다 | |
| 방향 일치 | 정답과 에이전트 어느 쪽도 혼합이 아닌 태그에서 감성이 같은 비율 | |
| 혼합 일치 | 한쪽이라도 혼합인 태그에서 둘 다 혼합인 비율 | |
| 기계 검사 | 스크립트가 하는 검사. 인용이 리뷰 원문에 글자 그대로 있는지, 문장 속 숫자가 계산 파일에 있는지 본다 | 인용 글자 일치 검사 있음 |
| 감사 | 결과물을 만든 쪽과 다른 에이전트(evidence-auditor)가 표본을 원문과 대조해 PASS, FAIL, UNVERIFIED로 판정하는 것. 읽기만 하고 고치지 않는다 | |
| UNVERIFIED | 근거를 찾지 못해 맞다 틀리다를 정하지 못한 것 | |
| 견고성 점검 | 결론이 우연인지 보는 검사. 리뷰를 무작위로 다시 뽑아 여러 번 계산하고, 상품을 하나씩 빼고 다시 계산한다 | |
| 관문(⏸) | 사람이 답해야 다음 단계로 넘어가는 곳. 다섯 곳이다([사람이 정하는 관문](#사람이-정하는-관문)) | |

### 실행에 쓰는 말

| 용어 | 뜻 |
|---|---|
| 메인 세션 | 단계를 지휘하는 Claude Code 세션. 스크립트를 돌리고 에이전트를 부른다 |
| 에이전트 | 한 가지 일만 맡은 하위 세션. 정해진 파일만 읽고 자기 출력 파일만 쓴다 |
| 상위 모델, sonnet | 판단하는 일은 상위 모델(Opus), 같은 일을 많이 반복하는 일은 sonnet이 한다 |
| effort | 모델이 답하기 전에 얼마나 깊이 생각할지 정하는 단계(medium, high 등) |
| 묶음 | 대량 작업을 나눈 단위. 태깅은 묶음 하나에 리뷰 약 50개다 |
| 작업 파일 | 설계 정보 추출 작업자 한 명이 읽을 파일 하나. 필요한 기준 원문과 맡은 대상만 담는다 |
| 헤드리스 | 사람이 대화하지 않고 명령 한 줄로 돌리는 실행 |
