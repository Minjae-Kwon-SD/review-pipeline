# 리뷰 분석 파이프라인

아마존 리뷰를 주제와 감성으로 태깅하고, 별점 표본 편향을 보정해 한국어 리뷰 분석 리포트(L3/L2)를 만든다.
v0는 향수 한 카테고리, 손으로 모은 리뷰 20~30개로 처음부터 끝까지 한 번 통과시키는 것이 목표다.
정답지는 스크럽 리포트(review_analysis_report_en.html)이고, 계산 규칙은 정답지를 그대로 따른다.

## 가장 중요한 원칙

정확도가 먼저다. 속도는 원래 방식보다 빠르기만 하면 된다.

1. 숫자는 스크립트만 만든다. 에이전트는 05_metrics.json과 05_tables.md의 값을 그대로 옮기고, 새로 계산하지 않는다.
2. 인용은 리뷰 원문 그대로다. 태그 파일에는 영어 원문, 리포트에는 한국어 번역과 출처 (브랜드, 별점★, review_id).
3. 에이전트는 자기 출력 파일만 쓴다. 다음 단계는 파일 경로로 넘겨받는다.
4. 태깅은 승인된 스키마(03_schema_approved.yaml)의 주제만 쓴다.
5. 정답 세트 리뷰(gold/gold_reviews.csv)는 스키마를 만들 때 보지 않는다. schema-drafter는 정답 세트를 뺀 03_schema_input.csv만 읽는다. 보고 만들면 채점이 부풀려진다.
6. 근거가 없으면 지어내지 않고 UNVERIFIED로 남긴다.

## 폴더

```text
CLAUDE.md                  이 파일
.claude/agents/            asin-selector, schema-drafter, review-tagger, issue-labeler, issue-tagger, report-writer, evidence-auditor, detail-schema-drafter, detail-extractor, benchmark-researcher, guide-writer, report-translator, product-spec-collector
.claude/commands/          review-run.md (/review-run <카테고리> <회차>)
.claude/hooks/timing.py    에이전트 시작과 끝을 timing.jsonl에 기록
.claude/settings.json      Hook 등록
config/                    stages.yaml(단계마다 입력, 출력, 뒤 단계, 상한), pipeline.yaml(유료 수집 스위치, 별점 묶음과 경고 기준), categories/<카테고리>.yaml(검색어와 제목 규칙),
                           topics_common.yaml(공통 주제 11개), report_template_ko.md,
                           topics_perfume_candidates.yaml(v0 손 시험용, v1에서는 읽지 않음)
scripts/                   collect, check_inputs, eval_gold(+ gold_sheet.html), tag_batches, audit_quotes, issues, weight(+ sections), render_html, market(+ market_build), detail, research, guide_metrics, guide_check, guide_diff, render_guide_html, translate_prep, robustness, specs, report_lines, stage_plan, stage_packet, timing_report, doc_facts
                           (+ pipeline_io, mcp_http 도우미. mcp_http는 .mcp.json의 서버를 HTTP로 부르고 토큰은 환경 변수에서만 읽음)
tests/                     가짜 회차로 스크립트를 손계산과 맞춰 보는 시험(python tests/test_scripts.py)
runs/CURRENT               지금 회차 이름 한 줄
runs/<회차>/               회차마다 생기는 파일 전부
runs/<회차>/raw/           MCP 응답 원문(reviews_<ASIN>.json, product_<ASIN>.json, candidates/, paid_calls.jsonl)
```

## 실행 흐름

단계와 명령은 .claude/commands/review-run.md(`/review-run <카테고리> <회차>`), 작업 방식과 상한은 그 문서의 "작업 방식과 상한"과
config/stages.yaml, 설계는 docs/multi_agent_design_v2.md에 있다. 바뀌지 않는 규칙만 여기에 둔다.

- ⏸ 표시(ASIN 확인, 스키마 승인, 정답 세트 태깅, 시험 태깅 뒤 계속, 세부 이슈 승인, 설계 정보 항목 승인)에서 멈추고 민재님을 기다린다.
- 시작할 때 `scripts/stage_plan.py plan`으로 다시 할 단계만 고른다. 중간에 끊기면 state.json에서 done이 아닌 첫 단계부터 다시 한다.
- 재시도와 동시 실행은 config/stages.yaml 상한 안에서만 한다. 상한에 닿으면 멈추고 민재님에게 넘긴다.
- 대량 작업 방식은 단계마다 config/stages.yaml의 method를 따른다. v2(scripts/stage_packet.py가 만든 작업 파일과 그 파일이 적은 묶음 입력만 넘김)는 설계 정보 추출에만, 태깅과 이슈 라벨은 묶음마다 에이전트 하나(per_batch).

## 파일 계약

| 파일 | 누가 쓰나 | 내용 |
|---|---|---|
| 00_candidates.csv | collect.py candidates | 후보 ASIN: asin,product_title,db_reviews,db_s1~db_s5,real_s1~real_s5,total_ratings,average_rating,date_min,date_max,kind_hint,asin_count |
| raw/ | collect.py | MCP 응답 원문. 다시 받지 않고 변환만 하려면 `collect.py pull --offline` |
| 02_collect_log.json | collect.py pull | 수집 기록. 본문이 비어 02_reviews.csv에서 뺀 리뷰(dropped, dropped_count) |
| 01_asins.csv | asin-selector(민재님 확인) 또는 민재님 | asin,title,brand,price_usd,price_band,amazon_rating,status(selected/excluded),reason 뒤에 선택 칸 parent_asin. 빈 brand, title, amazon_rating, parent_asin은 pull이 products_byasin으로 채움 |
| 02_reviews.csv | collect.py pull 또는 민재님 | review_id,asin,star,date,title,body,verified,vine 뒤에 선택 칸 helpful_votes,variant_asin,variant_text,brand,language,country (UTF-8, 본문은 HTML 엔티티만 풀고 고치지 않음). language 빈 값은 영어 |
| 02_star_distribution.csv | collect.py pull 또는 민재님 | asin,s5,s4,s3,s2,s1,total_ratings 뒤에 선택 칸 average_rating,source,captured_at (상품 페이지 별점 막대의 퍼센트, DB는 rating_summary) |
| 00_input_check.json | check_inputs.py | 입력 검사 결과(ASIN별 group_coverage, missing_real_pct, 언어별 건수 포함) |
| gold/gold_reviews.csv | eval_gold.py pick | 정답 세트 리뷰 |
| gold/gold_pick_log.json | eval_gold.py pick | 정답 세트와 스키마 표본을 고른 조건, 시드, 모자라서 다른 ASIN에서 채운 기록 |
| 03_schema_sample.csv | eval_gold.py pick | 스키마 표본 150개(정답 세트 제외, 02_reviews.csv와 같은 칸). schema-drafter가 읽는 파일 |
| 03_schema_input.csv | eval_gold.py pick | 정답 세트를 뺀 리뷰 전부 |
| gold/gold_tagging.html | eval_gold.py sheet | 정답 세트 태깅 화면(한 파일, 브라우저 localStorage에 저장) |
| gold/gold_tags.jsonl | 민재님(태깅 화면에서 내보냄) | {"review_id","topic","sentiment"} 한 줄에 하나 |
| 03_schema_draft.yaml | schema-drafter | 주제 초안 |
| 03_schema_approved.yaml | 민재님 | 승인된 스키마. 태깅과 집계의 기준 |
| 03_schema_check.json | check_inputs.py --schema | 스키마 검사 결과 |
| 04_batches.json | tag_batches.py plan | 태깅 묶음(batch_id, asin, review_ids, models)과 시험 태깅 묶음 |
| 04_tags_{sonnet|top}_{batch_id}.jsonl | review-tagger | 묶음 하나의 태그(gold 묶음은 04_tags_top_gold.jsonl) |
| 04_tags.jsonl | audit_quotes.py tags --model sonnet | 검사를 통과한 sonnet 묶음 태그를 합친 것. 리포트가 쓰는 태그 |
| 04_quote_check_{model}.json | audit_quotes.py tags | 태그 기계 검사 결과(failed_batches, 인용 앞 부정어 경고) |
| 04_negation_check.json | audit_quotes.py negation | 인용 바로 앞 세 단어(같은 문장) 안에 부정어가 있는 태그(경고만) |
| 04_audit_sample.jsonl | eval_gold.py audit-sample | evidence-auditor가 판정할 태그 표본(ASIN마다 25개, 감성 비율대로, 부정 최소 3개) |
| 04_gold_eval.json, .md | eval_gold.py score | 정답 세트 점수와 불일치 목록 |
| 04_tag_audit.yaml | evidence-auditor (메인 세션이 저장) | 표본 태그 재판정 |
| 04_tag_audit_summary.json | eval_gold.py audit | 표본 FAIL 비율(전체, ASIN별)과 다시 태깅할 묶음(batches_with_findings) |
| 07a_issue_plan.json, 07a_issue_samples/ | issues.py sample | 주제와 방향마다 인용 수와 표본(최대 150개, ASIN과 별점 묶음 고르게) |
| 07a_issues_<주제>.yaml | issue-labeler | 주제 하나의 세부 이슈 목록 제안 |
| 07a_issues_draft.yaml, .md | issues.py merge | 세부 이슈 목록 초안(검사 결과 포함). 민재님이 고쳐 07a_issues_approved.yaml로 승인 |
| 01_prices.json | collect.py prices | 변형별 현재 가격과 조회 날짜(7장 가격대, 11장 온스당 가격) |
| 05_metrics.json, 05_tables.md | weight.py | 리포트에 쓰는 모든 숫자(정답 세트 정확도 accuracy와 표기 문자열, 별점 보정 weighting, 리포트 문구 notes 포함)와 리포트용 표 |
| 05_weights_preview.md | weight.py --weights-only | 태그 없이 본 ASIN별 묶음, 표본 수, 실제 %, 방식, 가중치, 경고 |
| 07a_issues_approved.yaml | issues.py approve | 승인된 세부 이슈 목록(승인 시각, 승인자) |
| 07b_label_batches.json, 07b_label_input/, 07b_labels_auto.jsonl | issues.py label-plan | 라벨 묶음, 기타만 있는 주제와 방향의 자동 기타 |
| 07b_labels_<묶음>.jsonl | issue-tagger | 인용마다 세부 이슈 라벨(1~2개 또는 other) |
| 07b_issue_labels.jsonl, 07b_issue_counts.json, 07b_issue_check.json | issues.py label-check | 합친 라벨, 라벨별 리뷰 수와 가중 비율과 ASIN별 수, 기타 비율, 겹침 |
| 07b_issue_audit_sample.jsonl, 07b_issue_audit.yaml, 07b_issue_audit_summary.json | issues.py, evidence-auditor | 라벨 감사 표본, 판정, FAIL 비율 |
| 07c_safety_input.jsonl, 07c_safety_verdicts.yaml, 07c_safety_check.md, 07c_safety_summary.json | issues.py, evidence-auditor | 안전 인용과 몸 증상 판정, 증상 종류(symptom_type)별 리뷰 수와 가중 비율(negative_text) |
| 07c_tagging_error_notes.md | 메인 세션 | 고치지 않고 남긴 의심 태그 메모 |
| 06_report.md | report-writer | 한국어 리포트 |
| market/raw/, market/calls.jsonl | market.py fetch | spd-amz-market 응답 원문과 호출 기록(무료, 40번 이하) |
| market/market.json, market/market_summary.md | market.py build | 하위 카테고리, 브랜드 상위 20, 검색어, 추이, 우리 상품, 광고 표(행마다 원본 파일), 받지 못한 것 |
| 13_detail_sample.csv | detail.py sample | 설계 정보 항목을 찾을 표본 150개(정답 세트 제외) |
| 13_detail_schema_draft.yaml, .md, 13_detail_schema_check.json | detail-schema-drafter, detail.py check | 설계 정보 항목 초안과 검사. ⏸ 승인 뒤 13_detail_schema_approved.yaml |
| 13_detail_schema_edits.yaml, 13_detail_schema_approved.yaml | 민재님(고칠 곳), detail.py approve | 승인된 설계 정보 항목 |
| 14_detail_batches.json, 14_detail_input/, 14_details_<묶음>.jsonl | detail.py plan, detail-extractor | 설계 정보 추출 묶음과 묶음별 결과 |
| 14_details.jsonl, 14_detail_counts.json, 14_detail_check.json | detail.py extract-check | 검사를 통과한 값(리뷰 id, 항목, 값, 인용), 항목과 값마다 리뷰 수와 가중 비율 |
| 14b_detail_audit_sample.jsonl, 14b_detail_audit.yaml, 14b_detail_audit_summary.json | detail.py, evidence-auditor | 추출 감사 |
| 15_research.yaml, 15_research_check.json | benchmark-researcher, research.py check | 웹 조사 주장(출처 URL, 원문 문장)과 다시 열어 확인한 결과 |
| 05_robustness.json | robustness.py | 견고성 점검: 다시 뽑기(씨앗 고정)와 상품 하나씩 빼기. metrics의 robustness와 가이드 A장 표의 원본 |
| 23_spec_input.json, 23_specs.yaml | specs.py prep, product-spec-collector | 상품마다 모을 사양 항목, 모은 값(출처 주소, 원문 문장, 같은 상품인지 확인한 정도) |
| 23_specs_check.json, 23_specs_verified.json | specs.py check | 사양 값마다 다시 열어 확인한 결과, 확인된 값만(가이드가 씀) |
| 16_guide_metrics.json | guide_metrics.py | 가이드의 모든 숫자, 표, 근거 리뷰 묶음 |
| 17_guide.md | guide-writer | 개발 가이드 문장([m:키], [r:id]) |
| 18_guide_quote_check.json, 18_guide_audit.yaml | guide_check.py, evidence-auditor | 가이드 문장 검사 |
| 07_guide.html, 07_guide_html_numbers.json, 07_guide_html_check.json | render_guide_html.py build, check | 개발 가이드 HTML과 검사 |
| 06_report.html, 06_report_html_numbers.json, 06_report_html_check.json | render_html.py build, check | HTML 리포트 한 파일(데이터는 const D), 화면 숫자의 JSON 경로, 검사 결과 |
| 18_guide_changed.md | guide_diff.py | 가이드 문장 일부를 바꿨을 때 바뀐 줄(감사는 이 줄만) |
| config/i18n/report_ui_<lang>.yaml, config/i18n/guide_ui_<lang>.yaml | 사람(한 번) | 화면 문구 번역(키는 한국어 원문), 번역문 표지(md_markers). 가이드 문구 파일은 아직 없음 |
| i18n_names_<lang>.yaml | 메인 세션(승인 이름의 번역) | 주제, 세부 이슈 라벨, 증상, 기간, 감성 이름. 승인된 이름은 한국어이고 이것은 번역 |
| 06_report_for_translation.md, 06_report_quote_sources.json | translate_prep.py prep | 표 블록을 뺀 번역 원문, 인용한 리뷰의 원문 인용 |
| 06_report_<lang>.md | report-translator | 번역 리포트 문장(줄 수, 숫자, id, 표지는 원문과 같음, 인용은 리뷰 원문) |
| 06_report_<lang>_check.json, 06_report_<lang>_pairs.jsonl | translate_prep.py check | 번역 기계 검사와 뜻 감사용 짝 |
| 06_report_<lang>_audit.yaml, _audit_fix.yaml | evidence-auditor(stage: translation) | 번역 뜻 감사 |
| 06_report_<lang>.html, _html_numbers.json, _html_check.json | render_html.py build, check --lang | 언어판 HTML(같은 숫자, 표, 드릴다운)과 검사 |
| 07_quote_check.json | audit_quotes.py report | 리포트 기계 검사 결과 |
| 07_audit.yaml | evidence-auditor (메인 세션이 저장) | 리포트 판정 |
| timing.jsonl, 08_timing.md | Hook, timing_report.py | 단계별 시간 |
| README.md, docs/walkthrough.md | 메인 세션 | 저장소 설명과 설명서. 숫자는 docs/doc_facts.json의 표기만 쓴다 |
| docs/doc_facts.json, .md, docs/doc_check.json | doc_facts.py build, check | 문서 숫자와 출처(회차 파일에서 모음), 문서 속 숫자와 경로 대조 결과 |
| docs/github_upload_plan.md, .gitignore | 메인 세션 | 저장소에 올릴 것과 뺄 것 초안(최종은 민재님) |
| state.json | timing_report.py mark, stage_plan.py baseline | 단계별 상태, 입력 해시(같으면 그 단계를 건너뜀), 호출과 재시도 수 |
| packets/<종류>_w<번호>.md, packets/<종류>_plan.json | stage_packet.py | 작업자 하나의 작업 파일(필요한 기준 원문 필드, 대상, 출력 경로, 검사, 상한)과 배정 요약 |
| config/detail_rules.yaml | 사람(민재님 결정) | 설계 정보 항목의 공통 경계 규칙(품목에 묶이지 않음). 작업 파일에는 맡은 항목이 걸린 규칙만 원문 그대로, 감사자도 함께 읽음 |
| 14_known_exceptions.yaml | 메인 세션(민재님 결정) | 그 회차에만 적용하는 첫 추출 검사의 알려진 예외(review_id, item, 이유). extract-check가 KNOWN으로 따로 보임 |
| 06_report_concl_packet.md, 06_report_conclusions.yaml | report_lines.py packet, report-writer | 장마다 한 줄 결론을 쓸 작은 입력, 결론 문장(report_lines.py insert가 06_report.md에 넣음) |

태그 한 줄 예시:

```json
{"review_id": "B0XXXXXXX1-03", "topic": "longevity_projection", "sentiment": "negative", "quote": "fades after an hour"}
```

sentiment는 positive, negative, mixed, neutral 중 하나. 리뷰 하나에 같은 주제 태그는 하나만.
카테고리와 무관한 리뷰는 topic "off_category", sentiment "neutral" 한 줄만 단다(다른 태그 없음). weight.py가 그 리뷰를 모든 집계에서 빼고 개수를 notes.off_category_text로 부록에 적는다.
리포트와 라벨 이름에는 가운뎃점(·)을 쓰지 않는다(audit_quotes.py report가 FAIL로 봄).

## 가중 계산 (weight.py가 함)

- 별점 묶음 보정. 묶음은 config/pipeline.yaml의 weighting.groups(부정 1,2★ / 중립 3★ / 긍정 4,5★).
- ASIN마다 n = 표본 수, real[s] = 실제 비율(합 1). covered = 표본이 있는 묶음, R = covered 묶음의 실제 비율 합.
- 묶음 안 별점이 모두 표본을 가지면 별점마다 w(s) = (real[s] / R) / (표본 수(s) / n).
  하나라도 비면 묶음 단위 w_g = (real_g / R) / (표본 수(g) / n)을 묶음 안 표본이 있는 별점에 똑같이 준다.
- 표본이 없는 묶음의 실제 비율(missing_real_pct)은 가중 결과에서 빠지고, 05_tables.md 분포 블록의 공개 문장에 적힌다.
- 유효 별점: 평균 별점(가중 평균, 별점 격차, ASIN 비교)에는 별점마다 보정한 리뷰는 실제 별점, 묶음 단위로 보정한 리뷰는 그 묶음의 실제 평균 별점(묶음 안 s x real[s] 합 / real_g)을 쓴다. 02_reviews.csv의 별점은 바꾸지 않는다.
- 입력 검사 오류: 표본이 있는 묶음이 2개 미만, 또는 실제 비율 50% 이상인 묶음이 비어 있음. 경고: 묶음 표본 30개 미만, 리뷰 한 개 비중 w(s) / n이 max_review_share(2%) 초과.
- 자체 검사: ASIN마다 가중치 합 = n, covered 묶음의 가중 비중 = real_g / R, 유효 별점 가중 평균 = 덮인 묶음만으로 다시 나눈 분포 평균. 모든 묶음이 별점마다면 이 값이 원래 분포 평균과 같다.
- 가중 부정 비율 = 그 주제 부정 태그의 가중치 합 / 그 주제 태그 전체의 가중치 합.
- 부정 언급 리뷰어(가중) = 그 주제를 부정으로 언급한 리뷰의 가중치 합 / 전체 리뷰의 가중치 합.
- 별점 격차 = 그 주제 부정 언급 리뷰의 가중 평균 별점 - 나머지 리뷰의 가중 평균 별점(부정 언급 3개 이상).
- 원본 수는 "무엇을 불평하는가", 가중 비율은 "얼마나 흔한가"로 읽는다.

## 모델

판단은 상위 모델이 한다: 메인 세션, asin-selector, schema-drafter, report-writer, evidence-auditor.
태깅은 sonnet이 전부 한다. 상위 모델은 gold 묶음(정답 세트 비교)과, sonnet으로 두 번 다시 해도 실패한 묶음에만 쓴다.
에이전트는 모두 model: inherit라 메인 세션의 모델을 따른다. 그래서 메인 세션을 상위 모델로 열고(/model 또는 --model opus),
sonnet 태깅만 Agent 호출에 model: sonnet을 준다(호출 때 준 모델이 frontmatter보다 먼저다).
리포트는 sonnet 태그(04_tags.jsonl)로 만들고, 정답 세트 판정 기준(주제 F1 0.80, 감성 90%)도 sonnet에 적용한다.

## 언어와 환경

- 지시문, 리포트, 사람에게 하는 말은 한국어. 주제 id는 영어 snake_case, 이름(name_ko)은 한국어.
- PC는 Windows. 스크립트는 `python scripts/<이름>.py`, 처음 한 번 `python -m pip install pyyaml`. CSV는 UTF-8.
- 헤드리스 실행 명령과 비용 기록(costs.jsonl)은 README.md "실행 방법"에 있다.
