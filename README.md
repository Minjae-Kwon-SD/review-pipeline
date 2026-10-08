# 아마존 리뷰 분석 파이프라인

> **English summary**
> 1. Given a product category and a set of Amazon ASINs, this pipeline builds two HTML deliverables: a review analysis report (Korean and English) and a product development guide (Korean; the English edition waits for review).
> 2. It runs inside Claude Code: the main session orchestrates, scripts compute every number, and narrow subagents only tag, extract, write sentences or audit.
> 3. Each step writes a file to `runs/<run>/`, and a human approves the key gates (ASINs, topic schema, gold set, sub-issue labels, design-info items).
> 4. Category differences live only in `config/categories/<category>.yaml` and in human-approved schemas, so a new category needs no code changes.
> 5. The first run (perfume, 6 ASINs, 1,212 reviews from a free shared review DB) passed every machine check and audit; paid scraping is off by default.

카테고리와 ASIN을 넣으면 HTML 두 개를 만든다. 하나는 **리뷰 분석 리포트**(별점 표본 편향을 보정한 주제와 감성 분석)이고, 다른 하나는 **제품 개발 가이드**(시장 데이터, 리뷰에서 뽑은 설계 정보, 웹 조사로 만든 개발 기준)다. 리뷰 리포트는 한국어판과 영어판이 있고, 개발 가이드는 한국어판이 있다(영어판은 틀만 준비).

우진님께 드리는 자세한 설명은 [docs/walkthrough.md](docs/walkthrough.md)에 있다. 이 문서의 숫자는 모두 `python scripts/doc_facts.py build`가 실제 회차 파일에서 모은 값이고, 출처는 [docs/doc_facts.md](docs/doc_facts.md)에 있다.

## 1. 무엇을 하나

| 결과물 | 파일 | 내용 |
|---|---|---|
| 리뷰 분석 리포트(한국어) | `runs/perfume-db-2026-10-07/06_report.html` | 정답지(스크럽 리포트)와 같은 13개 장. 숫자와 막대, 인용을 누르면 근거 리뷰 원문이 열림(드릴다운). 리뷰 탐색기 포함 |
| 리뷰 분석 리포트(영어) | 저장소에 없음 | 영어판은 제출 전 요청이 있을 때 한국어 최신판으로 다시 만듦(`render_html.py build <회차> --lang en`) |
| 제품 개발 가이드(한국어) | `runs/perfume-db-2026-10-07/07_guide.html` | 시장 개요, 경쟁사, 문제, 포지셔닝, 한 장 요약, 데이터와 방법. 숫자마다 근거 리뷰 묶음, 웹 조사 주장마다 출처 링크 |

HTML은 모두 한 파일이고 외부 참조가 없다(데이터가 파일 안에 있음). 모델은 HTML을 쓰지 않는다. 스크립트가 숫자는 JSON에서, 문장은 검사를 통과한 Markdown에서 가져와 만든다.

## 2. 실행 방법

### 준비물

- Claude Code(메인 세션은 상위 모델로 연다. 예: `claude --model opus`)
- Python과 PyYAML(`python -m pip install pyyaml`)
- `.mcp.json`: 공유 리뷰 DB(amz-review), 시장 데이터(spd-amz-market) MCP 서버 주소. 토큰 값은 파일에 없고 환경 변수 `AMZ_REVIEW_TOKEN`을 참조만 한다. 값은 각자 환경 변수로 넣는다.
- 카테고리 설정 `config/categories/<카테고리>.yaml`(검색어, 상품 제목 규칙, 가이드 설정)

### 한 회차 돌리기

```text
/review-run perfume-db 2026-10-07
```

회차 이름은 `카테고리-날짜`이고 결과는 `runs/<회차>/`에 쌓인다. 단계별 명령은 [.claude/commands/review-run.md](.claude/commands/review-run.md)에 있다. 헤드리스로 돌릴 때는 권한을 넓히지 않고 허용 도구만 준다.

```text
claude -p --model opus --allowedTools "Bash(python scripts/*)" "Edit(/runs/**)" "Write(/runs/**)" --max-turns 200 --output-format json < prompt.txt
```

헤드리스 실행마다 결과 JSON의 duration_ms, total_cost_usd, num_turns를 시각, 멈춘 단계와 함께 `runs/<회차>/costs.jsonl`에 한 줄로 남긴다(`scripts/log_cost.py`). ⏸에서 멈추면 그 실행은 끝난다.

### 단계 순서(요약)

| 단계 | 하는 일 | 누가 |
|---|---|---|
| 0 수집 | 공유 리뷰 DB에서 후보 ASIN과 리뷰, 실제 별점 분포를 받음 | `collect.py`, asin-selector |
| 1 입력 검사 | 형식 검사, 정답 세트와 스키마 표본 고르기 | `check_inputs.py`, `eval_gold.py pick` |
| 2~3 스키마 | 표본에서 주제 초안, 사람이 승인 | schema-drafter, ⏸ 사람 |
| 4 정답 세트 | 사람이 정답 세트를 직접 태깅(태거 결과를 보기 전에) | ⏸ 사람 |
| 5~6 태깅과 검사 | 묶음마다 동시에 태깅, 인용 기계 검사, 표본 감사, 정답 세트 채점 | review-tagger(sonnet), `audit_quotes.py`, evidence-auditor, `eval_gold.py` |
| 6-1~6-3 세부 이슈 | 주제마다 세부 이슈 목록 제안, 사람 승인, 라벨 붙이기와 감사, 안전 증상 판정 | issue-labeler, ⏸ 사람, issue-tagger(sonnet), evidence-auditor, `issues.py` |
| 7 집계 | 별점 보정 가중 집계, 리포트의 모든 숫자와 표 | `weight.py` |
| 8~9 리포트 | 문장 쓰기, 기계 검사와 감사 | report-writer, `audit_quotes.py`, evidence-auditor |
| 10~11 시간과 HTML | 시간 표, 리포트 HTML 만들기와 검사 | `timing_report.py`, `render_html.py` |
| 12~16 가이드 재료 | 시장 데이터, 설계 정보 항목 제안과 승인, 추출과 감사, 웹 조사와 출처 확인, 가이드 숫자 | `market.py`, detail-schema-drafter, ⏸ 사람, detail-extractor(sonnet), evidence-auditor, benchmark-researcher, `research.py`, `guide_metrics.py` |
| 17~19 가이드 | 문장 쓰기, 검사와 감사, HTML | guide-writer, `guide_check.py`, evidence-auditor, `render_guide_html.py` |
| 20~22 다른 언어판 | 번역 준비, 줄마다 번역, 기계 검사, 뜻 감사, HTML | `translate_prep.py`, report-translator, evidence-auditor, `render_html.py --lang en` |

### 사람이 멈춰서 정하는 관문(⏸)

1. **ASIN 확인**: asin-selector가 고른 상품 목록을 보고 확정
2. **스키마 승인**: 주제 초안을 고쳐 `03_schema_approved.yaml`로 승인
3. **정답 세트 태깅**: 정답 세트 리뷰를 태깅 화면(`gold/gold_tagging.html`)에서 직접 태깅. 태거 결과를 보기 전에 한다
4. **세부 이슈 라벨 승인**: 주제마다 제안된 라벨 목록을 고쳐 `07a_issues_approved.yaml`로 승인
5. **설계 정보 항목 승인**: 가이드용 추출 항목 초안을 고쳐 `13_detail_schema_approved.yaml`로 승인

이 밖에 시험 태깅 결과를 보고 전체 태깅을 계속할지, 정답 세트 기준에 못 미칠 때 어떻게 할지도 사람이 정한다. 관문에서 메인 세션은 상태를 `needs_human`으로 남기고 멈추며, 사람의 답 없이 대신 정하지 않는다.

## 3. 폴더 구조

```text
CLAUDE.md                     원칙, 실행 흐름, 파일 계약(누가 어떤 파일을 쓰나), 가중 계산 규칙
README.md                     이 문서
.mcp.json                     MCP 서버 주소(토큰은 환경 변수 참조만)
.claude/
  agents/                     에이전트 정의(역할, 입력, 금지, 출력 형식, 도구 권한)
  commands/review-run.md      /review-run 단계별 명령
  hooks/timing.py             에이전트 시작과 끝을 timing.jsonl에 기록
  settings.json               Hook 등록과 허용 규칙
config/
  pipeline.yaml               유료 수집 스위치(기본 꺼짐), 별점 묶음, 경고 기준
  categories/perfume.yaml     카테고리 설정(검색어, 제목 규칙, 가이드 설정). 새 카테고리는 이 파일만 새로 씀
  topics_common.yaml          모든 카테고리에 공통인 주제
  report_template_ko.md       리포트 장 구성
  i18n/report_ui_en.yaml      리포트 화면 문구 영어(키는 한국어 원문)
scripts/                      숫자를 만드는 스크립트 전부(모델 호출 없음)
tests/test_scripts.py         가짜 회차로 스크립트를 손계산과 맞춰 보는 시험
tests/fixture/                시험용 작은 입력
docs/
  walkthrough.md              설명서(구조와 이유, 시키는 법, 정답지 비교, 시간)
  decisions_log.md            정한 것과 이유, 알게 된 함정
  doc_facts.md, .json         이 문서들의 숫자와 출처
  github_upload_plan.md       저장소에 올릴 것과 뺄 것 초안
  mcp_tools.md                MCP 도구 메모
runs/
  CURRENT                     지금 회차 이름
  <회차>/                     회차마다 단계 파일 전부(raw/는 MCP 응답 원문, gold/는 정답 세트, market/은 시장 데이터)
```

## 4. 에이전트

모든 에이전트는 자기 출력 파일만 쓰고, 다음 단계는 파일 경로로 넘겨받는다. "모델"은 실행 때 쓰는 모델이다(정의는 모두 `model: inherit`, 태깅과 추출만 호출할 때 sonnet을 준다).

| 에이전트 | 하는 일 | 모델 | 도구 | 왜 스크립트가 아니라 에이전트인가 |
|---|---|---|---|---|
| asin-selector | 후보 표에서 카테고리에 맞는 상품을 골라 `01_asins.csv` | 상위 | Read, Write | 상품 제목만으로 같은 카테고리인지(바디 미스트, 세트 등) 가리는 판단 |
| schema-drafter | 표본 리뷰를 읽고 공통 주제에 카테고리 전용 주제를 더한 스키마 초안 | 상위 | Read, Write | 리뷰에서 반복되는 불만과 칭찬의 범주를 찾는 일은 규칙으로 못 함 |
| review-tagger | 묶음 하나(약 50개)의 리뷰마다 주제, 감성, 원문 인용 | sonnet | Read, Write | 문장의 뜻을 읽고 승인된 주제에 맞추는 일. 양이 많아 빠른 모델로 동시에 |
| issue-labeler | 주제 하나의 표본 인용으로 세부 이슈 목록 제안 | 상위 | Read, Write | "금방 날아감", "처음부터 약함"처럼 주제 안의 하위 범주를 찾는 판단 |
| issue-tagger | 승인된 세부 이슈 목록으로 인용마다 라벨 | sonnet | Read, Write | 인용의 뜻을 라벨 정의에 맞추는 일 |
| report-writer | 스크립트가 만든 숫자와 표, 태그 인용으로 리포트 문장 | 상위 | Read, Write | 숫자를 읽고 해석하는 문장. 숫자는 새로 계산하지 않고 옮기기만 |
| evidence-auditor | 태그, 라벨, 추출 값, 리포트와 가이드 문장, 번역을 원문과 대조해 판정 | 상위 | Read, Grep, Glob(**읽기 전용**) | 뜻이 맞는지 보는 판단. 만든 쪽과 분리해 고치지 못하게 함 |
| detail-schema-drafter | 리뷰에서 뽑을 설계 정보 항목(사용 부위, 지속 시간 등) 초안 | 상위 | Read, Write | 제품 설계에 쓸 정보가 무엇인지 리뷰에서 찾는 판단 |
| detail-extractor | 승인된 항목으로 리뷰마다 값과 원문 인용 | sonnet | Read, Write | 자유 문장에서 값을 뽑는 일 |
| benchmark-researcher | 공개 웹 자료로 시장 규모, 업계 구성, 규제, 시험 기준 조사(주장마다 출처 URL과 원문 문장) | 상위 | WebSearch, WebFetch, Read, Write | 검색과 출처 읽기. 출처는 `research.py`가 다시 열어 확인 |
| guide-writer | 가이드 숫자와 확인된 웹 주장만 보고 가이드 문장 | 상위 | Read, Write | 기준과 권고를 문장으로 쓰는 일 |
| report-translator | 감사를 통과한 한국어 리포트 문장을 줄마다 다른 언어로 | 상위 | Read, Write | 뜻을 지키는 번역. 숫자와 구조 표시는 그대로 |
| product-spec-collector | 상품마다 브랜드 사이트와 소매점 상품 페이지에서 사양(농도, 노트, 성분 등)을 출처 문장과 함께 모음 | 상위 | WebSearch, WebFetch, Read, Write | 같은 상품 페이지 찾기와 맞추기. 값은 `specs.py`가 다시 열어 확인 |

메인 세션은 지휘만 한다(단계 순서, 스크립트 실행, 에이전트 호출, 감사 YAML 저장, 관문에서 멈춤).

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
| `translate_prep.py` | 번역 원문 준비, 번역 기계 검사(줄 수, 숫자, 인용, 한글 잔여) |
| `timing_report.py`, `log_cost.py` | 단계 시간과 상태 기록, 헤드리스 실행 비용 기록 |
| `robustness.py` | 견고성 점검(리뷰 다시 뽑기, 상품 하나씩 빼고 다시 계산) |
| `specs.py` | 상품 사양 수집 준비, 출처를 다시 열어 값 확인 |
| `stage_plan.py` | 입력 해시로 다시 할 단계만 고르기, 단계 정의의 출력 겹침과 상한 검사, 작업자 배정 |
| `stage_packet.py` | 작업자마다 작업 파일 하나(필요한 기준 원문 필드, 대상, 출력 경로, 검사, 상한) |
| `report_lines.py` | 리포트 장마다 한 줄 결론의 작은 입력 만들기와 넣기 |
| `doc_facts.py` | 이 문서들의 숫자를 회차 파일에서 모으고 대조 |
| `pipeline_io.py`, `mcp_http.py` | 공용 입출력, MCP 서버 HTTP 호출(토큰은 환경 변수에서만 읽음) |

## 6. 원칙

- **숫자는 스크립트가 계산하고 모델은 문장만 쓴다.** 리포트와 가이드의 숫자는 모두 `05_metrics.json`, `16_guide_metrics.json`의 값이고, 기계 검사가 문장 속 숫자를 그 값과 대조한다.
- **감사관은 읽기 전용이고 고치지 않는다.** evidence-auditor는 Read, Grep, Glob만 갖고 판정 YAML만 돌려준다. 고치는 일은 만든 에이전트가 다시 한다.
- **카테고리 차이는 config와 승인된 스키마에만 있다.** 에이전트 지시문에는 향수 이야기가 없다. 주제, 세부 이슈, 설계 정보 항목은 파이프라인이 리뷰에서 제안하고 사람이 승인한다.
- **룰북.** 태깅 규칙(주제 정의, 포함과 제외 예, 경계 사례)은 승인된 스키마와 정답 세트 태깅 메모에 모여 있고, 태거와 감사관이 같은 룰북을 본다.
- **정답 세트 격리.** 정답 세트 리뷰는 스키마를 만들 때 보지 않고, 에이전트는 gold 폴더를 읽지 않는다(헤드리스에서도 막음).
- **유료 수집은 기본값 꺼짐.** `config/pipeline.yaml`의 `paid.enabled`와 실행 인자 `--confirm-paid`가 둘 다 있어야 돈다. 이번 회차의 데이터는 모두 무료였다. 에이전트나 메인 세션이 MCP 유료 도구를 직접 부르지 못하게 `.claude/settings.json`의 permissions deny에 `mcp__amz-review__scrape_reviews`를 넣어 두었다. 민재님이 유료 수집을 허락하면 이 줄을 뺀다.
- **근거가 없으면 지어내지 않는다.** 확인하지 못한 웹 주장은 가이드에 쓰지 않고, 단위를 모르는 시장 칸은 "단위 미확인"으로 적는다.

## 7. 향수 실행 결과(perfume-db-2026-10-07)

### 데이터

- ASIN 6개, 리뷰 1,212개(본문이 빈 2개 제외), 태그 3,497개
- 승인 주제 12개(공통 11개에 카테고리 전용 더함), 세부 이슈 라벨 71개, 설계 정보 항목 14개(추출 값 1,629개)
- 시장 데이터 호출 64번(무료), 웹 조사 주장 104개 중 80개 출처 확인, 상품 사양 확인 값 52개(상품 6개, 브랜드 사이트와 소매점 상품 페이지)

### 검사

| 무엇 | 결과 |
|---|---|
| 정답 세트(리뷰 30개, 태그 106개) | sonnet 주제 F1 0.96, 감성 93.0%(기준: F1 0.80, 감성 90%) |
| 태그 표본 감사 | 147개 중 FAIL 2개(1.4%). 판정을 받지 못한 것(UNVERIFIED 1개, 빠진 태그 10개)을 FAIL로 센 보수적 비율 8.3%. 정답 세트 리뷰의 태그 3개는 표본에서 뺌 |
| 세부 이슈 라벨 감사 | 150개 중 FAIL 1개(0.7%) |
| 설계 정보 추출 감사 | 150개 중 FAIL 4개(2.7%) |
| 번역 뜻 감사 | 91쌍 중 FAIL 2개(2.2%), 두 줄 고친 뒤 다시 감사 PASS |
| 리뷰 리포트 HTML(한국어, 영어) | 한국어 화면 숫자 1053개, 영어 957개, 드릴다운 371개 대조 PASS, 외부 참조 0, 영어판 한글 잔여 0 |
| 개발 가이드 HTML | 화면 숫자 312개, 근거 묶음 155개, 출처 링크 271개 대조 PASS |
| 견고성 점검 | 상품 하나씩 빼고 다시 계산: 결론 뒤집힘 6번 중 0번. 리뷰 다시 뽑기 2,000번: 불만 1위 유지 100.0%, 머리 숫자 2의 95% 구간 8.2%~11.9%, 머리 숫자 3은 6개 중 5개(리뷰를 다시 뽑아 보면 3~5개) |
| 스크립트 시험 | 335개 확인 통과 |

정답 세트 F1 0.96은 **같은 30개로 태깅 규칙(룰북)을 다듬은 뒤 잰 값**이라 표본 안 점수다. 처음 보는 리뷰에서의 정확도는 이보다 낮을 수 있다(8장 한계).

### 시간(분, 사람 대기 빼고)

| 영역 | 첫 실행(모든 시도 합) | 다시 실행 어림(마지막 1회 합, 고치기 단계 빼고) | 사람 시간 |
|---|---|---|---|
| 리뷰 리포트 | 113.9분 | 63.7분 | 206.7분 |
| 개발 가이드 | 81.3분 | 74.9분 | 21.4분 |
| 영어판과 보강(G3 이후) | 173.5분 | 63.6분 | 0.0분 |
| 합 | 368.7분 | 202.2분 | 228.1분 |

- "첫 실행"은 이번에 실제로 쓴 기계 시간이다. 코드나 지시를 고친 뒤 다시 돌린 시도가 모두 들어 있다.
- "다시 실행 어림"은 단계마다 마지막 성공 1회만 더하고, 이번 회차에서 고치느라 생긴 단계(리포트 손질, 가이드 고치기, 머리 숫자 다시 계산)를 뺀 값이다.
- 사람 시간 대부분은 정답 세트 태깅(178.5분)이다. 규칙을 함께 정하며 한 첫 회차라 길었다.
- 첫 수집 단계는 시간 기록을 켜기 전에 돌아 빠져 있다.

### 비용

API 요금 환산 어림값(Claude Max 구독, 실제 결제 없음). 헤드리스 실행 33번의 기록(`costs.jsonl`) 합이다.

| 영역 | 실행 수 | 어림값 |
|---|---|---|
| 리뷰 리포트 | 14번 | $70.42 |
| 개발 가이드 | 5번 | $28.31 |
| 영어판과 보강(G3 이후) | 14번 | $46.90 |
| 합 | 33번 | $145.63 |

대화 세션에서 직접 한 일(코드 작성, 일부 감사, 중간에 멈춘 번역 실행)은 기록이 없어 빠져 있다. 리뷰와 시장 데이터는 모두 무료 도구로 받았다.

## 8. 알려진 한계

- **정답 세트 점수는 표본 안 점수다.** 같은 30개로 규칙을 만든 뒤 쟀다. 새 카테고리에서는 규칙을 만들 리뷰와 채점할 리뷰를 나누는 것이 좋다.
- **ASIN이 매출 상위가 아니다.** 공유 리뷰 DB에 리뷰가 많은 상품 가운데 골랐다. 정답지는 검색 1페이지 매출 상위였다. 대표성이 다르다.
- **데이터가 정답지보다 작다.** 리뷰 리포트 정답지는 리뷰 3,488개, ASIN 10개(태그 10,066개)이고, 이번은 리뷰 1,212개, ASIN 6개다. 개발 가이드 정답지는 리뷰 12,380개, 리스팅 37개, 카테고리 9개를 썼다.
- **리뷰 표본이 낮은 별점 쪽으로 치우쳐 있다.** 별점 묶음 가중으로 실제 분포에 맞춰 보정하지만, 표본이 없는 묶음은 보정할 수 없어 리포트에 그 비율을 적는다.
- **시장 데이터 칸의 단위를 모르는 것이 있다.** 아마존 노드의 매출 칸 등은 단위가 문서에 없어 "단위 미확인"으로 두고 크기를 단정하지 않는다.
- **상품 사양이 일부뿐이다.** 정답지 가이드는 리스팅 사양 37개, 사이즈표 31개를 썼다. 이번에는 브랜드 사이트와 소매점 상품 페이지에서 상품 6개의 농도, 노트, 성분 등 확인 값 52개를 모았지만, 병과 분사기 사양은 확인하지 못했고 측정 사양(사이즈표에 해당하는 것)은 없다. 상품이 적어 사양과 불만의 관계는 말하지 않고 나란히 놓기만 한다.
- **영어판은 리뷰 리포트만 있고, 제출 전 요청이 있을 때 한국어 최신판으로 다시 만든다.** 개발 가이드 영어판은 만들지 않는다. G6 시점 영어판(06_report_en.html, .md)은 그 뒤 한국어판에 더한 것(10장 브랜드 표의 혼합과 중립 칸, 장마다 굵은 한 줄 결론, 도움돼요 잠정 표시)이 없어 저장소에서 뺐다(PC에는 남김). 아래 검사 표의 영어판 숫자는 그 판의 기록이다.

## 9. 새 카테고리로 돌리는 법(예: 제모)

1. 사람이 `config/categories/hair_removal.yaml` 하나를 쓴다. `config/categories/perfume.yaml`을 본떠 검색어(`keywords`), 상품 제목 규칙(`title_include`, `title_exclude`, `kind_rules`), 가이드 설정(`guide` 절: 머리 숫자에 쓸 시장 노드와 주제, 성장 배수 제외 낱말, 집중 분석, 기준표 후보)을 적는다.
2. `/review-run hair_removal 2026-10-20`처럼 부른다.
3. 주제(스키마), 세부 이슈, 설계 정보 항목은 파이프라인이 그 카테고리 리뷰에서 제안하고, 사람이 관문에서 고쳐 승인한다. 에이전트 지시문과 스크립트는 바꾸지 않는다.
4. 정답 세트는 새 카테고리에서 다시 태깅한다. 다른 언어판이 필요하면 이름표 `runs/<회차>/i18n_names_en.yaml`을 승인된 이름의 번역으로 만든다.
