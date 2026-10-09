---
description: 리뷰 분석 파이프라인을 한 회차 돌린다(수집부터 리포트, 검증, 시간 표까지). 예 /review-run perfume-db 2026-10-07
argument-hint: <카테고리> <날짜>
disable-model-invocation: true
---

# /review-run

인자: $ARGUMENTS
인자는 카테고리와 날짜 두 개다. 회차 이름은 `카테고리-날짜`(예: perfume-db 2026-10-07 → perfume-db-2026-10-07)이고, 회차 폴더는 `runs/<회차>/`다.
카테고리 설정 이름은 카테고리 인자의 첫 부분이다(perfume-db → perfume, config/categories/perfume.yaml). 회차 폴더 이름은 인자 그대로 쓴다.
너(메인 세션)는 지휘만 한다. CLAUDE.md의 원칙과 파일 계약을 따른다. 담당자에게 하는 말은 처음부터 끝까지 한국어로 쓴다.

## 시작

1. 지금 모델을 한 줄로 알린다. sonnet이나 haiku면 "/model로 상위 모델로 바꾼 뒤 다시 불러 주세요"라고 하고 멈춘다. schema-drafter, report-writer, evidence-auditor, asin-selector가 이 모델을 따른다.
2. `runs/<회차>/`가 없으면 만든다. 01_asins.csv, 02_reviews.csv, 02_star_distribution.csv는 0단계(00_collect)가 만든다.
3. `runs/CURRENT`에 회차 이름 한 줄을 쓴다. 시간 기록 Hook이 이 파일을 보고 기록할 곳을 정한다.
4. `runs/<회차>/state.json`이 있으면 아래 단계 순서에서 done이 아닌 첫 단계부터 이어서 하고, 어디서부터인지 알린다.

## 단계마다 지킬 것

- 시작과 끝에 `python scripts/timing_report.py mark <회차> start <단계> --kind <종류>`와 `... end <단계> --kind <종류>`를 부른다. state.json도 이 명령이 바꾼다. 재시도를 다 써서 멈출 때는 `stop`.
- 단계마다 담당자에게 한 줄로 무엇을 하는지, 끝나면 결과 한 줄을 알린다. 숫자는 스크립트 출력에서 그대로 옮긴다.
- 에이전트 결과 파일을 직접 고치지 않는다. 태그와 리포트는 해당 에이전트가 다시 쓴다. 예외는 evidence-auditor가 돌려준 YAML을 파일로 저장하는 것 하나.
- 재시도는 6단계와 9단계에서 각각 최대 2번. 그래도 실패하면 stop하고 무엇이 남았는지 알린다.
- Bash는 `python scripts/...` 한 명령씩 부른다. `&&`, `;`, `echo`, `cat`을 붙이면 허용 규칙에 맞지 않아 매번 묻는다. 결과는 스크립트가 찍는 PASS/FAIL 줄로 판단하고, 파일 내용은 Read로 본다. runs/CURRENT는 Write로 쓴다.
- ⏸ 단계에서는 mark start로 needs_human을 남기고 턴을 끝낸다. 담당자의 답 없이 그 단계를 대신하지 않는다.

## 작업 방식과 상한(docs/multi_agent_design_v2.md, config/stages.yaml)

- **대량 작업 방식은 단계마다 다르다**(config/stages.yaml의 method). 설계 정보 추출(14)만 v2(작업 파일과 작업자 배정)다. 태깅(5)과 이슈 라벨(6-3)은 묶음마다 에이전트 하나(per_batch)다. v2로 품질을 시험한 것은 설계 정보 다시 판정뿐이고, 태그와 라벨 작업 파일은 종류별 순서와 스키마 공통 규칙 전달(GPT 검토 F10), 태그 입력 파일 나누기(F11)를 고치고 품질 시험을 한 뒤에만 v2로 바꾼다(docs/compare_v2_result.md).

- **다시 할 단계 고르기**: 시작할 때 `python scripts/stage_plan.py plan <회차>`(마른 실행). 입력 해시가 같은 단계는 건너뛰고 그 문서도 다시 읽지 않는다. 바뀐 단계와 그 뒤 단계만 다시 한다. 이 방식을 처음 쓰는 회차는 `stage_plan.py baseline <회차>`로 기준 해시를 한 번 적는다.
- **작업 파일만 넘김(v2 단계)**: `python scripts/stage_packet.py detail <회차> --items ...`가 작업자마다 만든 packets/<종류>_w<번호>.md를 넘긴다. 에이전트는 그 파일과 거기 적힌 묶음 입력 파일만 읽는다. 프롬프트는 `회차`, `작업 파일: packets/...md` 두 줄이면 된다. 전체 스키마, 02_reviews.csv 전체, CLAUDE.md를 넘기지 않는다.
- **작업자 배정(v2 단계)**: 작업자 하나가 묶음 목록을 차례로 처리한다. 실제 묶음 크기를 차례로 더해 작업자당 4묶음이나 리뷰 200개를 넘기 직전에 다음 작업자로 넘긴다(stage_packet.py가 stage_plan.assign을 부름). 묶음 하나가 200개를 넘으면 멈춘다.
- **실패한 묶음만 다시(v2 단계)**: `stage_packet.py detail <회차> --items ... --only <실패 묶음 id들>`. 묶음 계획에 없는 id가 있으면 멈춘다. 재시도 횟수는 스크립트가 막지 않으므로 메인 세션이 묶음마다 세고 상한에서 멈춘다.
- **해시와 출력 확인**: `stage_plan.py plan`은 입력 해시와 함께 그 단계의 지시문과 코드(stages.yaml의 code)의 해시, 묶음 계획의 묶음 출력이 하나하나 있는지 본다. mark start와 end 사이에 입력이 바뀌면 mark end가 완료로 적지 않고 needs_human으로 둔다. 기존 회차를 처음 이 방식으로 볼 때 `baseline --with-code`는 지금 출력이 지금 지시문으로 만든 것일 때만 쓴다.
- **상한(기본값, config/stages.yaml)**: 상한은 담당자가 숫자를 직접 적어 지시할 때만 바꾼다. "빨리"라는 말로 올리지 않는다. 상한에 닿으면 추가 호출을 멈추고 보고한다.

| 항목 | 기본값 |
|---|---|
| 대량 작업자(sonnet) 동시 실행 | 태깅 8, 이슈 라벨과 설계 정보 추출 4 |
| 작업자 하나가 맡는 양 | 최대 4묶음 또는 리뷰 200개 |
| 단계당 에이전트 호출 | 작업자 수 + 작성자 1 + 감사자 1 + 재시도 |
| 재시도 | 묶음마다 2번, 단계 전체 재시도 호출 4번 |
| 상위 모델 | 작성자 4(서로 다른 파일을 쓰는 작성자, 예: 주제별 issue-labeler), 감사자 1(작성이 끝난 뒤 감사, 동시에 돌리지 않음) |

- **같은 모델 작업자 먼저 하나**: 같은 정의와 같은 모델의 작업자 가운데 하나를 먼저 띄우고 첫 출력이 나오면 나머지를 띄운다(캐시 후보, 절감률 미확인). 사람 관문은 큰 묶음 앞에 끝낸다.
- **감사**: 작성자와 다른 감사자 하나. 기계 검사를 통과한 결과의 표본과 바뀐 행 전부를 본다. 표본이 비면 PASS가 아니라 EMPTY로 따로 정한다.
- **검토형**(같은 큰 자료를 여럿이 읽고 판단하는 일, 읽기 전용 렌즈 최대 4)은 **매번 담당자 허락을 받는다**. 결과는 문자열로 받고 파일은 메인 세션이 쓴다. 둘 이상 실패하면 합치지 않는다.
- **기록**: 단계 끝에 `timing_report.py mark <회차> end <단계> --kind <종류> --calls <호출 수> --retries <재시도 수> --workers <동시 수>`. 입력 해시는 mark end가 state.json에 적는다.

## 단계 (이름, 종류)

0. **00_collect, script** (02 파일까지 다 있으면 건너뛰고 skip을 알린다):
   - 01_asins.csv가 없으면 차례로: `python scripts/collect.py candidates <회차> --category <카테고리 설정 이름>`, asin-selector를 부른다(프롬프트: 회차 이름, 카테고리). 그다음 ⏸ **00_asin_review, human**: 01_asins.csv의 selected와 excluded를 표로 보여 주고 "01_asins.csv를 확인하고 고칠 것이 있으면 고친 뒤 알려 주세요"라고 하고 턴을 끝낸다.
   - 01_asins.csv가 있으면(또는 담당자가 확인을 알리면) `python scripts/collect.py pull <회차>`. 유료 수집(`--mode paid --confirm-paid`)은 담당자가 이번 회차에서 직접 하라고 할 때만 쓴다(config/pipeline.yaml의 paid.enabled도 true여야 함).
   - 출력의 ASIN별 리뷰 수, 별점별 건수, 언어별 건수, 뺀 리뷰를 그대로 알린다.
1. **01_inputs, script**: `python scripts/check_inputs.py <회차>`. 실패면 오류를 보여 주고 stop. 통과하면 `python scripts/eval_gold.py pick <회차>`(정답 세트 30개: ASIN마다 5개, 영어, 본문 40자 이상. 스키마 표본 150개: ASIN마다 25개, 정답 세트 제외). 출력의 ASIN별, 별점별 건수 표를 그대로 알린다.
2. **02_schema_draft, agents**: schema-drafter를 부른다(프롬프트: 회차 이름, 카테고리 설정 이름). 공통 주제(config/topics_common.yaml)에 카테고리 전용 주제는 표본에서 5번 이상 나온 것만 더한다. 끝나면 `python scripts/check_inputs.py <회차> --schema 03_schema_draft.yaml`. 예시 인용 오류가 있으면 schema-drafter에게 그 오류를 주고 한 번 고치게 한다. 주제 표(id, name_ko, side, common_id, evidence_count, 정의 한 줄), changes, questions를 그대로 보여 준다.
3. **03_schema_approval, human** ⏸: "03_schema_draft.yaml을 고쳐 03_schema_approved.yaml로 저장한 뒤 알려 주세요"라고 하고 턴을 끝낸다. 담당자가 알리면 `python scripts/check_inputs.py <회차> --schema`. 오류가 있으면 보여 주고 다시 기다린다. 통과하면 end.
4. **04_gold_tagging, human** ⏸: `python scripts/eval_gold.py sheet <회차>`를 부르고, 담당자에게 "runs/<회차>/gold/gold_tagging.html을 브라우저로 열어 30개를 태깅한 뒤, 'gold_tags.jsonl 내보내기'로 받은 파일을 runs/<회차>/gold/gold_tags.jsonl로 저장하고 알려 주세요"라고 하고 턴을 끝낸다. 주제나 감성을 제안하거나 고치지 않는다. 담당자가 알리면 `python scripts/eval_gold.py gold <회차>`. 오류가 있으면 보여 주고 다시 기다린다.
5. **05_tagging, agents**:
   1. `python scripts/tag_batches.py plan <회차>`. 출력의 묶음 수와 시험 태깅 묶음을 알린다.
   2. 시험 태깅: 04_batches.json의 pilot_batches(리뷰가 가장 적은 ASIN의 묶음과 gold 묶음)만 review-tagger로 부른다(작업자 상한 안에서 동시).
      - ASIN 묶음과 gold 묶음(sonnet): Agent 호출에 `model: sonnet`. 프롬프트 `회차: <회차>`, `묶음: <batch_id>`, `모델 표시: sonnet`
      - gold 묶음(상위 모델 비교): 모델을 따로 주지 않는다. 프롬프트 `회차: <회차>`, `묶음: gold`, `모델 표시: top`
      그다음 `python scripts/audit_quotes.py tags <회차> --model sonnet --batches <시험 ASIN 묶음들>,gold`, `python scripts/audit_quotes.py tags <회차> --model top`, `python scripts/eval_gold.py score <회차>`(04_tags.jsonl이 아직 없으니 gold 묶음의 sonnet 태그로 채점).
   3. ⏸ **05a_pilot, human**: 시험 태깅에 걸린 시간(timing.jsonl의 에이전트 시작과 끝), 묶음 수와 리뷰 수, 인용 검사 결과, 채점 한 줄 요약(summary_ko)을 알리고, 남은 묶음 수를 적은 뒤 "계속할까요?"라고 하고 턴을 끝낸다.
   4. 담당자가 계속이라고 하면 시험 태깅 묶음(pilot_batches)을 뺀 나머지 sonnet 묶음을 묶음마다 review-tagger 하나로 부른다(per_batch, `model: sonnet`, 위 상한 표의 동시 수 안에서 차례로). 프롬프트는 시험 태깅과 같은 형식(`회차: <회차>`, `묶음: <batch_id>`, `모델 표시: sonnet`).
6. **06_tag_check, agents**: 아래를 차례로 한다.
   1. `python scripts/audit_quotes.py tags <회차> --model sonnet`(모든 sonnet 묶음을 검사하고 통과하면 04_tags.jsonl로 합침, 인용 앞 부정어는 경고). 합친 뒤 `python scripts/audit_quotes.py negation <회차>`로 부정어 경고 개수를 04_negation_check.json에 남긴다. 실패한 묶음(04_quote_check_sonnet.json의 failed_batches)만 review-tagger(sonnet)를 다시 부른다. 그 묶음의 오류를 프롬프트에 그대로 붙인다.
   2. 통과하면 `python scripts/eval_gold.py audit-sample <회차>`, 그다음 evidence-auditor(프롬프트: `stage: tags`, 회차). 돌려준 YAML 블록만 runs/<회차>/04_tag_audit.yaml로 저장하고 `python scripts/eval_gold.py audit <회차>`.
   3. 감사가 FAIL이면 batches_with_findings의 묶음만 review-tagger(sonnet)를 다시 부른다. 그 묶음의 감사 지적을 프롬프트에 그대로 붙인다. 그다음 1, 2를 다시.
   4. 다시 태깅은 sonnet으로 묶음마다 최대 2번. 그래도 실패한 묶음은 그 묶음만 상위 모델로 한 번 부르고(모델 표시는 sonnet 그대로, 파일 이름이 같아야 합쳐진다), 담당자에게 어느 묶음을 상위 모델로 다시 했는지 알린다.
   5. `python scripts/eval_gold.py score <회차>`. 출력의 모델별 한 줄 요약(04_gold_eval.json의 summary_ko, 예: "sonnet: 주제 F1 0.90(기준 0.80, 통과), 감성 일치 88.6%(기준 90.0%, 1.4%p 모자람)")을 담당자에게 글자 그대로 옮긴다. 기준과의 차이를 따로 계산하지 않는다. 판정은 리포트에 쓰는 sonnet 기준이다. 기준 미달이면 04_gold_eval.md의 불일치 목록을 보여 주고 ⏸ `06_gold_review`(human)로 멈춘다. 고를 수 있는 것: 스키마를 고쳐 3단계부터 다시, 정답 태깅을 고쳐 다시 채점, 이대로 진행(리포트 부록에 적음).
6-1. **07a_issue_draft, agents** (세부 이슈 목록 초안):
   1. `python scripts/issues.py sample <회차>`: 주제(전체 만족도 제외)와 방향(부정 이슈: 부정과 혼합 인용, 긍정 이슈: 긍정과 혼합 인용)마다 인용을 최대 150개, ASIN과 별점 묶음이 고르게 섞이게 뽑는다. 인용 20개 미만인 주제와 방향은 기타만.
   2. issue-labeler를 주제마다 하나씩 부른다(모델은 따로 주지 않음, 상위 모델. 상위 모델 작성자 상한(4) 안에서 동시에). 프롬프트 `회차: <회차>`, `주제: <topic id>`. 출력은 07a_issues_<주제>.yaml.
   3. `python scripts/issues.py merge <회차>`. 오류가 있으면 그 주제의 issue-labeler에게 오류를 주고 한 번 고치게 한다. 주제를 따로 동시에 썼으므로, 메인 세션이 주제끼리 뜻이 겹치는 라벨(같은 불만이 두 주제에 있음)을 확인해 담당자에게 보여 줄 표에 적는다. 07a_issues_draft.md의 주제별 표를 담당자에게 보여 준다.
6-2. **07a_issue_approval, human** ⏸: "07a_issues_draft.yaml을 고쳐 07a_issues_approved.yaml로 저장한 뒤 알려 주세요"라고 하고 턴을 끝낸다.
   - 승인 기록: `python scripts/issues.py approve <회차> --approved-at <UTC 시각> --approved-by "<누가, 어떻게>"`가 초안을 07a_issues_approved.yaml로 복사하고 승인 시각과 승인자를 적는다.
     perfume-db-2026-10-07: 2026-10-07T09:09Z, 담당자, 카드 "제안 반영 후 승인"(라벨 71개).
6-3. **07b_issue_labeling, agents**: 승인 목록으로 라벨을 붙인다. 주제와 감성 태그는 다시 하지 않는다.
   1. `python scripts/issues.py label-plan <회차>`: 전체 만족도와 중립을 뺀 태그 인용(혼합은 두 방향 모두)을 주제와 방향마다 최대 180개 묶음으로 나눈다(07b_label_batches.json, 07b_label_input/). 승인 라벨이 없는 주제와 방향은 스크립트가 기타로 채운다(07b_labels_auto.jsonl).
      `python scripts/issues.py safety-input <회차>`: 안전 주제 인용 전부와 리뷰 원문(07c_safety_input.jsonl).
   2. issue-tagger를 묶음마다 하나씩 부른다(per_batch, Agent 호출에 model: sonnet, 상한 표의 동시 수 안에서 차례로). 프롬프트 `회차: <회차>`, `묶음: <batch_id>`. 같은 때 evidence-auditor(`stage: safety`)를 부르고 돌려준 YAML 블록만 07c_safety_verdicts.yaml로 저장한다.
   3. `python scripts/issues.py label-check <회차>`: 승인 라벨이나 other, 1~2개, other 단독, 입력 인용 빠짐 없음. 통과하면 07b_issue_labels.jsonl과 07b_issue_counts.json(라벨마다 리뷰 수, 가중 비율, ASIN별 수, 기타 비율, 향과 신뢰의 향 차이 라벨 겹침)을 쓴다. 실패한 묶음(failed_batches)만 오류를 붙여 다시 부른다. 최대 2번, 그래도 실패하면 stop.
   4. `python scripts/issues.py safety-render <회차>`: 07c_safety_check.md(인용, 원문, 판정, 이유)와 07c_safety_summary.json.
6-4. **07c_issue_check, script와 agents**: `python scripts/issues.py audit-sample <회차>`(ASIN과 주제를 고르게 150개), evidence-auditor(`stage: issues`)의 YAML 블록만 07b_issue_audit.yaml로 저장, `python scripts/issues.py audit <회차>`(FAIL 5% 이하면 PASS). FAIL이면 stop하고 리포트로 넘어가지 않는다.
   - 의심 태그(주제나 감성이 틀려 보이는 인용)는 고치지 않고 07c_tagging_error_notes.md에 review_id와 이유를 적는다.
   - 7단계 weight.py가 07b_issue_counts.json, 07b_issue_labels.jsonl, 07c_safety_summary.json을 읽어 05_metrics.json의 issues, issue_overlap, safety_check, brand_deep[].strengths/weaknesses[].top_issues와 05_tables.md의 세부 이슈 표를 만든다.
7. **07_weight, script**: `python scripts/weight.py <회차>`. 실패하면(자체 검사 포함) 계산 문제이니 stop하고 출력을 그대로 보여 준다.
8. **08_report, agents**: report-writer를 부른다(프롬프트: 회차 이름).
9. **09_report_check, agents**: `python scripts/audit_quotes.py report <회차>`, 그다음 evidence-auditor(`stage: report`, 회차). 돌려준 YAML 블록만 07_audit.yaml로 저장한다. 둘 중 하나라도 FAIL이면 report-writer에게 07_quote_check.json과 07_audit.yaml을 주고 고치게 한 뒤 9단계를 다시. next_action이 HUMAN_REVIEW_REQUIRED면 그 항목을 보여 주고 ⏸ 기다린다.
10. **10_timing, script**: 이 단계만 start와 end mark를 먼저 부르고 `python scripts/timing_report.py report <회차>`를 부른다. 그래야 시간 표에 이 단계가 "끝 기록 없음"으로 남지 않는다. 출력에 "두 번 이상 시작한 단계"가 있으면 그 줄도 그대로 알린다.
11. **11_html, script**: HTML 리포트 만들기. 모델을 부르지 않는다(HTML을 쓰는 에이전트 없음).
   - 명령: mark start 11_html, `python scripts/render_html.py build <회차>`, `python scripts/render_html.py check <회차>`, mark end 11_html, 그다음 `python scripts/timing_report.py report <회차>`로 시간 표를 다시 만든다.
   - 입력: 05_metrics.json, 07b_issue_counts.json, 07b_issue_labels.jsonl, 07a_issues_approved.yaml, 07c_safety_summary.json, 07c_safety_verdicts.yaml, 02_reviews.csv, 02_star_distribution.csv, 04_tags.jsonl, 03_schema_approved.yaml, 06_report.md(문장만).
   - 출력: 06_report.html(한 파일, 외부 참조 없음), 06_report_html_numbers.json(화면 숫자와 JSON 경로), 06_report_html_check.json(숫자 대조, 드릴다운 대조, 외부 참조, 가운뎃점).
   - check가 FAIL이면 stop하고 오류를 그대로 보여 준다. 문장 속 세부 이슈 개수가 07b와 달라 연결하지 못한 것도 FAIL이다(06_report.md를 고칠 일).

## 개발 가이드(초안)

두 번째 결과물(제품 개발 가이드)의 준비 단계다. 리뷰는 다시 모으지 않고 태깅도 다시 하지 않는다. 시장 데이터는 spd-amz-market(무료)만 쓰고 amz-review와 유료 수집은 부르지 않는다.

12. **12_market, script**: mark start 12_market, `python scripts/market.py fetch <회차>`(호출 40번 이하, 이미 받은 응답은 다시 부르지 않음, 오류는 한 번만 다시), `python scripts/market.py build <회차>`, mark end 12_market.
   - 입력: 01_asins.csv(부모 ASIN, 브랜드), raw/product_*.json, raw/variations_*.json(같은 날 받은 응답을 복사해 씀).
   - 출력: market/raw/<도구>_<입력>.json(원문), market/calls.jsonl(호출 기록), market/market.json(표의 숫자와 행마다 원본 파일), market/market_summary.md(호출 목록, 하위 카테고리, 브랜드 상위 20, 검색어 상위 50, 검색어 추이, 우리 상품, 광고와 상위 상품, 받지 못한 것, 응답 칸 이름).
   - 주의: 하위 카테고리 도구는 노드 이름만("Eau de Parfum")으로 부르면 다른 카테고리 결과가 온다. subcategoryContextName("Women's Eau de Parfum")으로 부른다.
13. **13_detail_schema_draft, agents**: `python scripts/detail.py sample <회차>`(13_detail_sample.csv, 150개, ASIN과 별점 묶음 고르게, 정답 세트 제외), detail-schema-drafter(모델 따로 주지 않음, 프롬프트 `회차: <회차>`), `python scripts/detail.py check <회차>`(FAIL이면 오류를 주고 최대 2번 다시).
   - 입력: 13_detail_sample.csv, config/categories/<카테고리>.yaml, 03_schema_approved.yaml, 07a_issues_approved.yaml.
   - 출력: 13_detail_schema_draft.yaml, 13_detail_schema_draft.md, 13_detail_schema_check.json.
13a. **13a_detail_schema_approval, human** ⏸: "13_detail_schema_draft.yaml을 고칠 곳을 알려 주시거나 승인해 주세요"라고 하고 멈춘다. 고칠 곳은 13_detail_schema_edits.yaml(split_values, extra)에 적고 `python scripts/detail.py approve <회차> --approved-at <UTC> --approved-by "<누가, 어떻게>"`로 13_detail_schema_approved.yaml을 만든다. 승인 전에는 전체 추출을 하지 않는다.
14. **14_detail_extract, agents**: `python scripts/detail.py plan <회차>`(ASIN마다 50개씩 묶음), `python scripts/stage_packet.py detail <회차> --items <항목들>`로 작업자별 작업 파일을 만들고 detail-extractor를 작업자마다 하나씩(Agent 호출에 model: sonnet, 상한 표의 동시 수 안에서), `python scripts/detail.py extract-check <회차>`(형식, extra 조건, 빠진 리뷰, JSON으로 읽지 못한 줄, 원문에 없는 인용은 모두 묶음 실패. 그 회차의 14_known_exceptions.yaml에 있는 칸만 KNOWN으로 따로 보임). 작업 파일에는 config/detail_rules.yaml의 공통 경계 규칙 가운데 맡은 항목이 걸린 것이 원문 그대로 들어간다. 실패한 묶음만 `--only`로 최대 2번 다시.
    - 출력: 14_details_<묶음>.jsonl, 14_details.jsonl, 14_detail_counts.json(항목과 값마다 리뷰 수, 가중 비율, ASIN별 수, 숫자 항목 중앙값), 14_detail_check.json
14b. **14b_detail_check, agents**: `python scripts/detail.py audit-sample <회차>`(항목과 ASIN 고르게 150개), evidence-auditor(`stage: details`)의 YAML 블록만 14b_detail_audit.yaml로 저장, `python scripts/detail.py audit <회차>`. FAIL 5%를 넘으면 멈추고 보고한다.
15. **15_research, agents**: benchmark-researcher(모델 따로 주지 않음, 헤드리스면 --allowedTools에 WebSearch, WebFetch를 더함)가 15_research.yaml을 쓴다. amazon.com은 열지 않는다. `python scripts/research.py check <회차>`가 출처를 다시 열어 원문 문장을 확인한다(15_research_check.json, verified만 가이드에 씀). 확인된 주장이 2개 미만인 분야만 한 번 더 조사.
16. **16_guide_metrics, script**: `python scripts/guide_metrics.py <회차>`. 카테고리마다 다른 것(머리 숫자 노드, 방향 지수 라벨, 기준표 후보, 검색어 성별 낱말, 집중 분석)은 config/categories/<카테고리>.yaml의 guide 절에서 읽는다. 출력: 16_guide_metrics.json(values, tables, ev 근거 묶음 최대 80개, quotes, caveats).
17. **17_guide_write, agents**: guide-writer(모델 따로 주지 않음)가 16_guide_metrics.json과 확인된 15_research만 보고 17_guide.md를 쓴다. 숫자 뒤에 [m:키], 사양과 규제 뒤에 [r:id]. 표는 쓰지 않는다(HTML 스크립트가 그림).
18. **18_guide_check, script와 agents**: `python scripts/guide_check.py <회차>`(18_guide_quote_check.json), evidence-auditor(`stage: guide`)의 YAML 블록만 18_guide_audit.yaml로 저장. 기계 검사 FAIL이나 감사 FAIL이 확인 수의 5%를 넘으면 guide-writer가 고치고 다시. 두 번째도 넘으면 멈추고 보고.
19. **19_guide_html, script**: `python scripts/render_guide_html.py build <회차>`와 `check <회차>`(화면 숫자와 metrics, 문장 속 [m:키], 근거 묶음 리뷰 수, 확인된 출처만 링크, 외부 참조 0, 가운뎃점 0, 리뷰 0개인 근거 묶음은 링크로 만들지 않음). 출력: 07_guide.html, 07_guide_html_numbers.json, 07_guide_html_check.json.
   - 머리 숫자 5번(가장 빨리 크는 검색어)은 성장 배수 = 최근 4주 검색량 합 ÷ 1년 전 같은 4주(52주 앞) 합이다. 후보는 30일 검색량 guide.growth.min_volume 이상이고 guide.growth.exclude_words가 없는 카테고리 검색어, 순위는 8주 이력이 모두 있는 것만. 주간 이력이 모자라면 `python scripts/market.py fetch-trends <회차> --months 24 --seeds "a,b" --max-calls N`(무료, 받은 것은 다시 부르지 않음).
   - 문장 일부만 바꿨으면 `python scripts/guide_diff.py <회차> 17_guide_vN.md`(18_guide_changed.md)로 바뀐 줄을 뽑아 evidence-auditor는 그 줄만 본다.

   - 견고성 점검: 7_weight 앞에 `python scripts/robustness.py <회차>`(다시 뽑기 2,000번 씨앗 고정, 상품 하나씩 빼기 → 05_robustness.json). weight.py가 metrics의 robustness로 넣고(리포트 부록 문장과 "6개 중 5개(리뷰를 다시 뽑아 보면 3~5개)" 같은 표기), guide_metrics.py가 머리 숫자 3의 표기와 A장 "견고성 점검" 표로 쓴다. 가이드 A장에 `### 견고성 점검` 소제목이 있으면 HTML이 표를 넣는다.
   - 상품 사양(선택, 무료 웹): `python scripts/specs.py prep <회차>`(23_spec_input.json, 항목은 config/categories/<카테고리>.yaml의 specs.items), product-spec-collector(모델 따로 주지 않음, 헤드리스면 --allowedTools에 WebSearch, WebFetch)가 23_specs.yaml, `python scripts/specs.py check <회차>`(주소를 다시 열어 원문 문장과 값 확인 → 23_specs_check.json, 확인된 값만 23_specs_verified.json). 버려진 값만 한 번 다시 찾기. guide_metrics.py가 점수표의 농도와 노트 칸, 기준 1(농도와 지속력), 2(공식 노트와 리뷰 노트, config specs.note_map), 4(병과 분사기와 망가진 부품), 6(이상 반응과 표시 알레르기 성분, 나열만) 표로 쓴다. amazon 주소는 열지 않는다.

   - 추출 항목 일부를 다시 판정할 때: `python scripts/detail.py rejudge-plan <회차> --items a,b`, detail-extractor(model: sonnet, "다시 판정" 절), `rejudge-merge`, 새로 생긴 값만 evidence-auditor(stage: details, 표본 14b_rejudge_audit_sample.jsonl), `detail.py audit --sample-file 14b_rejudge_audit_sample.jsonl --audit-file 14b_rejudge_audit.yaml`, 그다음 16~19.
   - 카테고리 전용 설정은 config/categories/<카테고리>.yaml에만: report.title, issues.overlap, guide.focus[].pair_items, guide.anatomy, guide.caveats_extra, guide.caveat_subcategory, specs.links, specs.note_item, specs.part_item. 없으면 그 표나 그림을 건너뛴다.

## 리뷰 리포트 다른 언어판(선택, 언어는 실행 설정)

같은 장, 숫자, 표, 드릴다운에 문장만 다른 언어다. 스크립트를 복사하지 않고 `--lang`과 문구 파일로 만든다. 승인된 이름은 한국어이고 다른 언어 이름은 번역이다.

20. **20_report_<lang>_prep, script**: `python scripts/translate_prep.py prep <회차>`(06_report_for_translation.md: 표 블록 뺀 원문, 06_report_quote_sources.json: 인용한 리뷰의 태그 인용 원문). 이름표 runs/<회차>/i18n_names_<lang>.yaml(주제, 세부 이슈 라벨, 증상, 기간, 감성 이름. 라벨의 en 이름은 07a_issues_approved.yaml의 name_en)과 화면 문구 config/i18n/report_ui_<lang>.yaml(키는 한국어 원문, md_markers는 번역문에서 찾을 표지)이 있어야 한다.
21. **21_report_<lang>_translate, agents**: report-translator(모델 따로 주지 않음, 프롬프트 `회차`, `원문: 06_report_for_translation.md`, `언어`, `출력: 06_report_<lang>.md`, `문구 파일`)가 줄마다 옮긴다(더하거나 빼지 않음, 숫자와 id 그대로, 인용은 리뷰 원문 그대로). `python scripts/translate_prep.py check <회차> --lang <lang>`(줄 수, 줄마다 숫자 표기, 리뷰 id, 인용이 원문에 글자 그대로, 한글 잔여, 가운뎃점. 기간 이름은 이름표로 바꿔 견주고 순위 N위는 서수로 있는지 봄). FAIL이면 지적된 줄만 고쳐 최대 2번. 그다음 `python scripts/render_html.py build <회차> --lang <lang>`, `check <회차> --lang <lang>`(숫자 대조, 드릴다운 대조, 빠진 화면 문구 0, 한글 잔여 0). 드릴다운 목록과 개수가 한국어판과 같은지 비교한다.
22. **21b_report_<lang>_audit, agents**: evidence-auditor(`stage: translation`, 06_report_<lang>_pairs.jsonl 전부)의 YAML을 06_report_<lang>_audit.yaml로 저장. FAIL이 checked의 5%를 넘으면 멈추고 보고. 넘지 않아도 FAIL은 그 줄을 고치고 21의 검사를 다시 한 뒤 고친 줄만 다시 감사(06_report_<lang>_audit_fix.yaml). 브라우저로 드릴다운 전부 열기, 스크립트 오류 0, 375px 폭 확인.
   - 개발 가이드 언어판은 `render_guide_html.py build|check <회차> --lang <lang>`로 틀만 준비돼 있다(config/i18n/guide_ui_<lang>.yaml이 없으면 멈춤, 17_guide_<lang>.md 필요, 16_guide_metrics.json 숫자 표기의 번역 규칙은 아직 없음).

## 마칠 때

아래 표를 파일에 있는 값 그대로 채워 보여 준다. 계산하지 않는다. 값은 Read로 파일을 열어 옮기고, `python -c`로 읽지 않는다(허용 규칙 밖이라 매번 묻는다).

| 기준 | 값 | 출처 |
|---|---|---|
| 입력 검사 | PASS/FAIL | 00_input_check.json |
| 태그 형식과 인용(sonnet, top gold) | PASS/FAIL | 04_quote_check_sonnet.json, 04_quote_check_top.json |
| 정답 세트 주제 F1, 감성 일치(sonnet, top) | 값 | 04_gold_eval.json의 summary_ko |
| 태그 검수 FAIL 비율(감사 표본) | 값 | 04_tag_audit_summary.json |
| 리포트 기계 검사, 감사 판정 | PASS/FAIL | 07_quote_check.json, 07_audit.yaml |
| 기계 시간, 사람 대기 | 분 | 08_timing.md(다시 돌린 단계가 있으면 마지막 시도 기준 값도) |

마지막 줄은 "06_report.md를 읽고 판정해 주세요"로 끝낸다.
