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

0. **새 세션에서 시작(2026-10-16 담당자 결정)**: 이 세션에 이 명령보다 앞선 대화(다른 작업, 이전 회차)가 있으면 시작하지 않는다. "한 회차가 길어 읽어 들이는 맥락이 많습니다. 새 스레드(새 세션)를 열어 거기서 /review-run을 불러 주세요"라고 하고 멈춘다. 담당자가 "여기서 해"라고 하면 그대로 진행한다. 앞선 대화가 같은 회차(같은 인자, 회차 폴더의 state.json이 있음)를 돌리던 것이고 사용량 한도나 PC 꺼짐 뒤에 이어서 하려고 다시 부른 것이면 묻지 않고 이어서 한다. 관문 뒤에 이어서 하는 턴도 같은 세션이 맞다.
1. 지금 모델을 한 줄로 알린다. sonnet이나 haiku면 "/model로 상위 모델로 바꾼 뒤 다시 불러 주세요"라고 하고 멈춘다. schema-drafter, report-writer, evidence-auditor, asin-selector가 이 모델을 따른다.
2. `runs/<회차>/`가 없으면 만든다. 01_asins.csv, 02_reviews.csv, 02_star_distribution.csv는 0단계(00_collect)가 만든다.
3. `runs/CURRENT`에 회차 이름 한 줄을 쓴다. 시간 기록 Hook이 이 파일을 보고 기록할 곳을 정한다.
3-1. **수집 계획 한 번에 묻기(2026-10-19 담당자 결정)**: 새 회차(runs/<회차>/00_collect_plan.yaml도 02_reviews.csv도 없음)면 맨 처음 아래 질문을 한 메시지로 보내고 턴을 끝낸다(`timing_report.py wait <회차> start 00_collect_plan`). 회차 안에서 담당자에게 미리 묻는 것은 이것과 정답 세트뿐이다.
   - 1) 상품 고르기: 가) 매출 순(검색 순위와 월 매출, collect.py rank, 기본) 나) 공유 DB 리뷰 많은 순(collect.py candidates) 다) ASIN 직접 지정. 고를 개수(기본: 카테고리 설정 selection.pick).
   - 2) 리뷰 출처: 가) 공유 DB만(무료, 기본) 나) DB 리뷰가 N개 미만인 상품만 유료(기본 N = paid.scrape_below_db_reviews) 다) 고른 상품 전부 유료.
   - 3) 유료일 때 리뷰 정렬: 가) 최신순(기본) 나) 도움순.
   - 4) 유료일 때 별점마다 페이지 수(1~10, 기본 1)와 이번 회차 유료 호출 최대 수(기본 paid.max_scrape_calls). 호출은 상품 하나에 별점마다 한 번이라 상품 하나가 5번이다. 페이지를 늘리면 호출 수는 같고 한 번의 비용이 는다.
   - 5) 대시보드(2026-10-19 담당자 결정): 가) 띄움 나) 안 띄움(기본). 진행판, 알림음, 점검 신호등을 보는 화면(scripts/dashboard.py, README "대시보드").
   - 답 예시를 함께 보인다: "1가 10개, 2가, 5가"(무료, 대시보드 띄움), "1가 8개, 2나, 3가, 4 1페이지 10번"(유료).
   - **유료는 최대 호출 수를 숫자로 적은 답에서만 허용한다**. "기본대로", "추천대로", "ok"처럼 숫자 없는 답은 2가(DB만)로 읽는다(2026-10-17 숫자 없는 "추천대로"를 유료 승인으로 읽고 21번을 부른 일).
   - 답을 받은 턴 맨 처음 wait end, 그다음 runs/<회차>/00_collect_plan.yaml을 Write로 쓴다: answered_at(UTC), answer_text(담당자 답 글자 그대로), pick(rank|db|manual), pick_n, asins(manual일 때), source(db|paid_below|paid_all), paid_below_db_reviews, sort(recent|helpful), pages_per_star, max_paid_calls(유료가 아니면 0), dashboard(true|false). 이 파일이 이번 회차 유료 수집 승인의 전부다. 상한에 닿으면 멈추고 다시 묻는다.
   - dashboard가 true면 runs/CURRENT를 쓴 뒤(5번) 바로 `python scripts/dashboard.py`를 Bash 백그라운드(run_in_background)로 띄우고, 담당자에게 "대시보드: http://127.0.0.1:8765, 처음에 소리 켜기를 한 번 눌러 주세요" 한 줄을 알린다. 이미 떠 있으면(포트 사용 중 오류) 다시 띄우지 않는다. runs/CURRENT를 따라가므로 회차마다 다시 띄울 필요는 없다.
4. `runs/<회차>/state.json`이 있으면 아래 단계 순서에서 done이 아닌 첫 단계부터 이어서 하고, 어디서부터인지 알린다.
5. **형식 견본과 다른 회차 막기(2026-10-17 담당자 결정)**: 하위 에이전트는 다른 회차 폴더와 시험 기록을 열지 못한다(.claude/hooks/guard_runs.py, runs/CURRENT 기준. 그래서 3번을 먼저). 형식은 견본으로만 맞춘다. 견본 품목은 이 회차와 다른 품목으로 고른다(기본 bluetoothspeaker, 이 회차가 bluetoothspeaker면 medicalscrubs). 견본이 없거나 오래됐으면 `python scripts/exemplar.py build <완성도 높은 회차>`로 만든다(config/exemplars/<품목>/, 숫자, 브랜드, 인용이 남으면 FAIL). report-writer를 부를 때마다 프롬프트에 `견본: config/exemplars/<품목>/report_exemplar.md`, guide-writer에는 `견본: config/exemplars/<품목>/guide_exemplar.md` 한 줄을 더한다(폴더만 주면 작성자는 목록을 볼 도구가 없어 못 찾음, 2026-10-17 rt8). 메인 세션은 작성자 프롬프트에 다른 회차의 문장이나 감사 지적을 넣지 않는다(이 회차의 미리 감사 지적만). 끝나면(11, 19 뒤) `python scripts/copy_check.py <회차> --source <견본 원본 회차>`로 베낌 비율을 남긴다(기준선: 다른 품목끼리 리포트 4~10%, 가이드 6~7%, 원본을 보고 쓴 시험 15~37%).

## 단계마다 지킬 것

- 시작과 끝에 `python scripts/timing_report.py mark <회차> start <단계> --kind <종류>`와 `... end <단계> --kind <종류>`를 부른다. state.json도 이 명령이 바꾼다. 재시도를 다 써서 멈출 때는 `stop`.
- 단계마다 담당자에게 한 줄로 무엇을 하는지, 끝나면 결과 한 줄을 알린다. 숫자는 스크립트 출력에서 그대로 옮긴다.
- 에이전트 결과 파일을 직접 고치지 않는다. 태그와 리포트는 해당 에이전트가 다시 쓴다. 예외는 evidence-auditor가 돌려준 YAML을 파일로 저장하는 것 하나.
- 재시도는 6단계와 9단계에서 각각 최대 2번. 그래도 실패하면 stop하고 무엇이 남았는지 알린다.
- Bash는 `python scripts/...` 한 명령씩 부른다. `&&`, `;`, `echo`, `cat`을 붙이면 허용 규칙에 맞지 않아 매번 묻는다. 결과는 스크립트가 찍는 PASS/FAIL 줄로 판단하고, 파일 내용은 Read로 본다. runs/CURRENT는 Write로 쓴다.
- ⏸ 단계에서는 mark start로 needs_human을 남기고 **관문 질문을 바로 보낸 뒤 턴을 끝낸다**(2026-10-16). 뒤에서 도는 작업(23_specs, 12_market, 13_detail_schema_draft, 15_research, 08a_report_early 같은 백그라운드 에이전트와 스크립트)이 끝나기를 기다렸다가 관문 질문을 보내지 않는다. 스피커 회차에서 관문 2는 스키마 초안 검사가 끝난 뒤 7분 넘게 늦게 열렸다(시장 데이터 스크립트와 상품 사양 수집이 끝나기를 기다림). 뒤 작업은 턴이 끝나도 계속 돈다: 대화형은 끝나면 알림이 다음 턴으로 오고, `claude -p` 한 줄 실행은 뒤 작업이 끝날 때까지 프로세스가 열려 있다(공식 문서 headless. 기본으로는 10분 넘게 쉬며 기다리면 멈추므로 .claude/settings.json의 env에서 CLAUDE_CODE_PRINT_BG_WAIT_CEILING_MS를 60분으로 늘려 둠). 알림이 오면 그 결과를 파일로 정리하고 mark end를 찍는다. 담당자의 답 없이 그 단계를 대신하지 않는다.
- **시간 기록(2026-10-13)**: 세 갈래로 잰다. AI 작업, 담당자 라벨링, 담당자 기다림. 사용량 한도나 PC 꺼짐으로 멈춘 시간은 "멈춤"으로 따로.
  - 관문마다: 질문을 보내고 턴을 끝내기 직전에 `python scripts/timing_report.py wait <회차> start <관문>`, **담당자 답을 받은 턴의 맨 처음에** `... wait <회차> end <관문>`. 초안을 낸 직후에 end를 찍지 않는다(30초 안 end는 스크립트가 거절, 정말 그랬으면 --force).
  - 정답 세트 라벨링: 정답 세트 화면이 연 시각, 중간 저장, 제출 시각을 gold_label_times.json으로 내보낸다(담당자가 gold_tags.jsonl과 같은 폴더에 저장). 시간 표가 그 파일을 읽는다.
  - 멈춤: 사용량 한도나 PC 꺼짐에서 다시 시작한 턴의 맨 처음에 `python scripts/timing_report.py pause <회차> --reason limit|pc_off`(직전 기록 시각부터 지금까지를 멈춤으로 적음).
  - `python scripts/timing_report.py report <회차>`가 AI 작업(벽시계, 겹친 시간은 한 번), 에이전트별 합, 라벨링, 기다림(라벨링 뺌), 멈춤, 끝 기록 없는 에이전트 실행 수를 한 화면에 낸다. 기록이 없는 값은 "기록 없음"으로 적는다.

## 사람에게 묻는 것(질문 줄이기, 2026-10-13 담당자 결정)

- **멈추는 곳은 정답 세트 하나(관문 자동 진행, 2026-10-19 담당자 결정)**: 담당자를 기다리는 곳은 시작 때 수집 계획 질문(3-1)과 04_gold_tagging(스키마 확인과 정답 세트를 한 화면에서 함)뿐이다.
  00_asin_review, 05a_pilot, 06_gold_review, 13a_detail_schema_approval, 07a_issue_approval은 메인 세션이 추천안대로 스스로 승인하고 기다리지 않는다. 관문마다:
  1) 추천안을 정한다(초안 그대로가 기본, 검사 경고가 있으면 그 경고를 고치는 쪽). 2) 승인 명령의 --approved-by에 "자동(추천안), 담당자 2026-10-19 결정"을 적는다(명령이 없는 관문은 그대로 다음 단계로). 3) 00_auto_decisions.md에 관문 이름, 무엇을 승인했는지, 왜 한 줄을 적는다. 4) 담당자에게 "정한 것" 메시지(관문 이름, 승인한 것 요약 표, 고칠 게 있으면 채팅으로 알려 달라는 한 줄)를 보내고 턴을 끝내지 않고 이어서 한다. wait start/end는 찍지 않는다.
  담당자가 나중에 채팅으로 지적하면 그 관문 파일을 지적대로 고쳐 다시 승인하고(승인자에 담당자 말 그대로), `stage_plan.py plan`으로 바뀐 입력 뒤 단계를 골라 다시 돌린다. 유료 수집은 00_collect_plan.yaml 상한 안에서만 하므로 상품 확인을 자동으로 넘겨도 돈은 그 안에서만 든다.
- 아래 단계 설명에서 ⏸와 "턴을 끝낸다", "멈춘다"는 04_gold_tagging(과 화면을 나눠 할 때의 03_schema_approval)에만 그대로 적용하고, 나머지 관문은 위 자동 진행으로 읽는다.
- **그 밖의 갈림길은 추천안으로 정하고** docs/decisions_log.md에 한 줄 남긴다(무엇을, 무엇으로, 왜). 다음 관문 메시지에 "정한 것" 목록으로 보여 주고, 담당자가 바꾸라고 하면 그때 되돌린다.
- **관문 밖에서도 꼭 묻는 것**: 권한 파일의 막는 줄 지우기, 00_collect_plan.yaml 상한을 넘는 유료 호출. 유료 수집 켜기는 3-1 답이 숫자로 허용했으면 묻지 않고 pull 직전에 config/pipeline.yaml paid.enabled를 true로 바꾼다.
- **묻지 않고 바로 하는 것**: 수집이 끝나면 유료 수집 끄기(paid.enabled false)와 막는 줄 되돌리기. 설정 파일을 스스로 못 고치게 막히면 담당자가 칠 한 줄만 알려 준다.
- **회사 저장소 push**: 리포트가 다 되고 담당자가 "올려"라고 할 때만. 그 전에는 묻지도 않는다.
- **메인 세션 /effort**: 바꿔야 할 때만 알린다.
- **다른 사람에게 보내는 것**: 언제나 묻는다.
- **기본값**(정하고 다음 관문에서 "정한 것"으로 보여 줌):
  - 별점당 페이지 수: 승인된 유료 한도 안에서 별점마다 고르게.
  - 에이전트 노력과 입력 나누기: 기록된 기준(판단은 Opus, 반복은 Sonnet, max 금지).
  - 시험 태깅 점수 미달: 규칙을 더 고치지 않고 진행하고 부록에 밝힌다.
  - 감사가 낸 문구로 바로 고친다.
  - 검토 뒤 고칠 범위: 높음과 보통은 다 고치고, 작은 것은 목록으로 남긴다(정답지 비교 뒤도 같음).
  - 동시 작업: 기록된 상한(config/stages.yaml, 2026-10-20: 태깅 50, 묶음 50, 상위 모델 작성자 15, 감사 3, 시장 데이터 호출 4) 안에서. 묶음 단계는 남은 묶음을 한 메시지에 모두 띄운다.
- PC 오프라인 알림은 그대로 둔다.

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
| 대량 작업자(sonnet) 동시 실행 | 태깅 50, 이슈 라벨과 설계 정보 추출 50 (2026-10-20 담당자 결정. 2026-10-16의 20, 16에서 올림. 남은 묶음을 한 메시지에 모두 띄운다) |
| 작업자 하나가 맡는 양 | 최대 4묶음 또는 리뷰 200개 |
| 단계당 에이전트 호출 | 작업자 수 + 작성자(리포트는 장 묶음 7개) + 감사자 1 + 재시도 |
| 재시도 | 묶음마다 2번, 단계 전체 재시도 호출 4번 |
| 모든 하위 에이전트 합(하네스) | 50(.claude/settings.json env의 CLAUDE_CODE_MAX_CONCURRENT_SUBAGENTS, 2026-10-20 담당자 결정. 그전 기본 20은 2026-10-17 E6에서 확인. 50이 실제로 먹는지는 다음 회차의 최대 동시 수로 확인). 상한이 20이던 때 태깅 20은 다른 에이전트가 없을 때만 다 찬다. 다른 단계와 겹치면 남는 자리만큼 띄우고, 상한 오류로 못 띄운 묶음은 대기열에 다시 넣는다. 출력 파일이 생겨도 에이전트는 끝 알림 전까지 자리를 차지한다 |
| 상위 모델 | 작성자 15(서로 다른 파일을 쓰는 작성자, 예: 주제별 issue-labeler 15개 동시, 장 묶음별 report-writer. 2026-10-16 4에서 15로), 감사자 3(2026-10-20 담당자 결정 2에서 3으로. yogamatx3에서 라벨 검사 반쪽 둘이 추출 감사와 겹쳐 차례로 돌아 3.5분 걸림. 작성이 끝난 뒤 감사. 문서 하나에는 감사자 하나이고, 리포트 감사와 가이드 감사처럼 서로 다른 문서만 동시에) |

- **작업자는 한 번에 모두(2026-10-20 담당자 결정)**: 태깅 본 묶음, 세부 이슈 초안(주제마다 하나), 라벨, 설계 정보 추출은 작업 파일이나 묶음 계획을 만든 직후 남은 작업자 전부를 한 메시지의 Agent 호출로 띄운다. 다른 단계 결과를 챙기느라 미루지 않는다. 예전의 "같은 모델 작업자 먼저 하나, 첫 출력 뒤 나머지"(캐시 후보, 절감률 미확인)는 쓰지 않는다. yogamatx3-2026-10-20에서 설계 정보 추출 작업자 10명이 세 번에 나눠 떠(11:46, 11:50, 11:52) 약 6분 늦었고, 세부 이슈 초안 2명이 3.7분 늦게 떠 약 1분 늦었다. 태깅의 시험 태깅(05a, 정답 세트 채점)은 품질 관문이라 그대로 먼저 한다. 사람 관문은 큰 묶음 앞에 끝낸다.
- **감사**: 작성자와 다른 감사자 하나. 기계 검사를 통과한 결과의 표본과 바뀐 행 전부를 본다. 표본이 비면 PASS가 아니라 EMPTY로 따로 정한다.
- **검토형**(같은 큰 자료를 여럿이 읽고 판단하는 일, 읽기 전용 렌즈 최대 4)은 **매번 담당자 허락을 받는다**. 결과는 문자열로 받고 파일은 메인 세션이 쓴다. 둘 이상 실패하면 합치지 않는다.
- **기록**: 단계 끝에 `timing_report.py mark <회차> end <단계> --kind <종류> --calls <호출 수> --retries <재시도 수> --workers <동시 수>`. 입력 해시는 mark end가 state.json에 적는다. 묶음이나 에이전트를 다시 부를 때마다 먼저 `python scripts/timing_report.py retry <회차> <단계> --batches <묶음 id들> --reason <한 줄>`을 부른다(2026-10-16). 동시 수를 올린 뒤 실패와 재시도가 느는지 보려는 것이라 빠뜨리지 않는다. 시간 표(08_timing.md)가 단계별 재시도 수를 적는다.

## 앞당겨 돌리는 단계 (2026-10-10, H1 시간 측정에서 나온 것)

사람 관문을 기다리는 동안 기계가 놀지 않게, 서로 기대지 않는 단계는 아래처럼 앞당겨 같은 때 돌린다. 단계 번호와 산출물은 그대로이고 순서만 바뀐다.

- 00_collect가 끝나면 바로 12_market(스크립트, 무료). 01_asins.csv의 부모 ASIN과 브랜드만 쓴다. `market.py fetch`는 서로 기대지 않는 호출을 4개씩 동시에 부른다(--concurrency 4 기본, 2026-10-16. 48번을 하나씩 부르던 것을 줄임). **Bash 백그라운드(run_in_background)로 부르고 schema-drafter를 부르기 전에 띄운다**(2026-10-16). 스피커 회차에서는 mark start 뒤 schema-drafter가 끝날 때까지 8분 넘게 스크립트가 불리지 않았고, 이어서 관문 2도 늦어졌다. 끝나면 알림을 받아 `market.py build`와 mark end.
- 12_market이 끝나면 바로 15_research(benchmark-researcher)를 백그라운드로 부른다. 스키마 승인을 기다리지 않는다(2026-10-20 담당자 결정: 조사자는 공통 주제와 시장 데이터만 읽음. yogamatx4에서 시장은 21:20에 끝났는데 스키마 승인을 기다려 21:27에 시작했고, 웹 조사가 가이드 시작을 12분 늦춤).
- 02_schema_draft가 끝나면(초안 검사 통과) 승인을 기다리지 않고 바로 13_detail_schema_draft(detail.py sample과 detail-schema-drafter)를 백그라운드로 부른다(2026-10-21 담당자 결정: yogamatx5에서 설계 정보 줄이 가이드 시작을 3.3분 늦춤). 정답 세트는 01_inputs에서 이미 골라 표본에서 빠진다.
  둘 다 상위 모델 작성자라 top_writers 상한 안에서 센다. 13a_detail_schema_approval(사람)은 담당자가 정답 세트를 마친 뒤 이어서 받는다.
- 13a 승인이 07a 세부 이슈 승인보다 먼저면, 07a 승인 뒤 메인 세션이 13_detail_schema_approved.yaml과 07a_issues_approved.yaml을 함께 읽고
  뜻이 겹치는 항목과 라벨을 13_detail_overlap_note.md에 적는다(승인본은 고치지 않음, 가이드 작성자가 같은 내용을 두 번 쓰지 않게 하는 메모).
- 23_specs(상품 사양)는 01_asins.csv가 정해지면 바로(수집 직후, 정답 세트 태깅을 기다리는 동안) 백그라운드로 돌린다. 14_detail_extract는 13a와 05_tagging 사이 순서와 무관하다.
- **리포트 미리 쓰기(2026-10-16)**: 06_tag_check가 끝나면 바로(07a 초안과 같은 때) `python scripts/weight.py <회차> --early`로 05_metrics_early.json, 05_tables_early.md, 05_quote_pool_early.json(라벨 전 같은 계산)을 만들고, **08a_report_early**로 report-writer 둘을 백그라운드로 동시에 부른다(프롬프트 `회차: <회차>`, `장: 1-7`, `입력: early`, `출력: 06_report_part_1-7.md`와 `장: 9`, `입력: early`, `출력: 06_report_part_9.md`). 1~7장과 9장의 표와 숫자는 세부 이슈 라벨과 무관하다(스피커 회차로 라벨 전후를 대조해 같음을 확인). 11장은 변형 신호의 방향 지수와 합친 방향 표를 라벨로 세므로 미리 쓰지 않는다. 상위 모델 작성자 상한(15)이 차면 07a issue-labeler(관문 앞 작업)가 먼저이고 미리 쓰기는 빈 자리에 띄운다. 07b 라벨 붙이기가 끝나기 전에만 끝나면 된다. 라벨 뒤 8단계에서 나머지 묶음과 보강을 하고 `report_parts.py assemble`이 합친다.
- **가이드 미리 쓰기(2026-10-17 안 B)**: 06_tag_check, 14b, 15, 23, 12가 끝나면(리포트 미리 쓰기와 같은 때, 07b 라벨 붙이기와 겹침) `python scripts/guide_metrics.py <회차> --early`(16a, 16_guide_metrics_early.json, 라벨에 기대는 값은 late_keys로 뺌), 그다음 **17a_guide_early**로 guide-writer(`장: 01-02-A`, `입력: early`, `출력: 17_guide_part_01-02-A_early.md`)를 부르고 `python scripts/guide_parts.py check <회차> --part 01-02-A --early`, evidence-auditor(`stage: guide`, 범위 01-02-A 묶음, early 입력)의 YAML을 18_guide_audit_early.yaml로 저장한다. 미리 감사 지적은 따로 고치지 않고 라벨 뒤 보강에서 함께 고친다. 상위 모델 작성자 상한(15)과 감사자 상한(2) 안에서 센다.
  **띄우는 때(2026-10-19)**: 06, 14b, 15, 23, 12 가운데 하나가 끝날 때마다 나머지가 다 끝났는지 보고, 다 끝났으면 그때 바로 16a를 부른다(06이 끝난 때 한 번만 보지 않는다). 시장 데이터를 받지 못했어도 market.json(받지 못한 것 표시)이 있으면 끝난 것으로 본다. 07b 라벨 붙이기가 먼저 끝났어도 16_guide_metrics(라벨 뒤)를 아직 부르지 않았으면 미리 쓰기를 띄운다(2026-10-20: 라벨 뒤에도 라벨 검사, 견고성, 가중 계산에 4분쯤 걸려, 그동안 01-02-A를 먼저 쓰면 가이드 1차에서 가장 긴 묶음(yogamatx3에서 8.6분)이 빠진다. yogamatx3은 이 조건으로 미리 쓰기를 건너뜀). 16을 이미 불렀으면 00_auto_decisions.md에 이유 한 줄을 적고 17에서 01-02-A를 final로 쓴다(아래). 미리 쓰기를 건너뛰어도 가이드는 언제나 장 묶음으로 쓴다.
- 16_guide_metrics부터는 그대로 07_weight, 14b, 15, 23이 끝난 뒤. 16~19(가이드 쪽)는 08_report와 09_report_check를 기다리지 않고 같이 돈다
  (가이드 단계의 입력에 리포트 파일이 없음). 리포트 작성자와 가이드 작성자는 모두 top_writers 상한 안에서 센다.
- 02_schema_draft를 다시 하면 13_detail_schema_draft도 다시 할 단계로 잡히고(config/stages.yaml의 after), 12_market을 다시 하면 15_research가 잡힌다.

## 단계 (이름, 종류)

0. **00_collect, script** (02 파일까지 다 있으면 건너뛰고 skip을 알린다):
   - 01_asins.csv가 없으면 00_collect_plan.yaml의 pick대로: rank면 `python scripts/collect.py rank <회차> --category <카테고리 설정 이름>`(검색 순위와 매출), db면 `python scripts/collect.py candidates <회차> --category <카테고리 설정 이름>`(DB에 있는 상품), 그다음 asin-selector를 부른다(프롬프트: 회차 이름, 카테고리, `고를 개수: <pick_n>`). manual이면 asins로 01_asins.csv를 쓴다(status selected, reason "담당자 지정"). 그다음 **00_asin_review**(자동 진행): 01_asins.csv의 selected와 excluded 표를 "정한 것"으로 보내고 바로 이어서 한다.
   - 01_asins.csv가 있으면 `python scripts/collect.py pull <회차>`. 유료 수집(`--mode paid --confirm-paid`)은 00_collect_plan.yaml의 source가 paid_below나 paid_all이고 max_paid_calls가 1 이상일 때만 쓴다(collect.py가 이 파일을 읽어 대상, 정렬, 페이지 수, 호출 상한을 정하고 파일이 없으면 멈춤). paid_all이면 `--paid-asins`에 selected 전부를 준다.
   - pull 바로 뒤에 `python scripts/collect.py prices <회차>`(변형 가격, spd-amz-market products_variations, 무료)로 01_prices.json과 01_asins.csv의 가격 칸을 채운다(2026-10-20 담당자 결정. 빠뜨린 회차는 리포트 가격 칸이 "가격 없음"이 되거나, 리포트를 쓰는 중에 가격을 받아 weight.py와 작성자 셋을 다시 돌렸다).
     유료 수집은 DB 리뷰가 paid.scrape_below_db_reviews보다 적은 selected만(또는 `--paid-asins`), ASIN x 별점마다 부르고, 성공한 호출은 다시 부르지 않는다. 처음에는 `--paid-test`로 한 번만 불러 시간과 rating_summary를 확인하고 알린다(응답에 비용 칸은 없음).
   - 출력의 ASIN별 리뷰 수, 별점별 건수, 언어별 건수, 뺀 리뷰를 그대로 알린다.
1. **01_inputs, script**: `python scripts/check_inputs.py <회차>`. 실패면 오류를 보여 주고 stop. 통과하면 `python scripts/eval_gold.py pick <회차>`(정답 세트 30개: ASIN마다 5개, 영어, 본문 40자 이상. 스키마 표본 150개: ASIN마다 25개, 정답 세트 제외). 출력의 ASIN별, 별점별 건수 표를 그대로 알린다.
2. **02_schema_draft, agents**: schema-drafter를 부른다(프롬프트: 회차 이름, 카테고리 설정 이름). 공통 주제(config/topics_common.yaml)에 카테고리 전용 주제는 표본에서 5번 이상 나온 것만 더한다. 끝나면 `python scripts/check_inputs.py <회차> --schema 03_schema_draft.yaml`. 예시 인용 오류가 있으면 schema-drafter에게 그 오류를 주고 한 번 고치게 한다. 주제 표(id, name_ko, side, common_id, evidence_count, 정의 한 줄), changes, questions를 그대로 보여 준다.
   - **한 화면(2026-10-10부터 기본)**: 초안 검사를 통과하면 바로 `python scripts/eval_gold.py sheet <회차>`(승인본이 없으면 초안으로 만듦). 담당자는 gold/gold_tagging.html 한 화면에서
     맨 위 "스키마 확인"(주제마다 승인, 고침, 빼기와 메모)과 정답 세트 태깅을 함께 하고, 03_schema_review.json과 gold/gold_tags.jsonl 두 파일을 저장한다.
     전체 만족도와 효과 주제(common_id performance)는 필수 칸이라 고르지 않으면 "다 봤음"이 체크되지 않는다.
     그다음 `python scripts/eval_gold.py schema-approve <회차> --approved-at <UTC> --approved-by "<누가, 어떻게>"`. 모두 승인이면 승인본이 생긴다.
     고칠 곳이 있으면 찍힌 메모대로 초안을 고쳐 03_schema_approved.yaml로 저장하고 담당자에게 바뀐 점을 한 줄씩 알린다.
     승인본에서 주제 id가 바뀌었거나 빠졌으면 `python scripts/eval_gold.py gold <회차> --rename old:new --drop-unknown`, 아니면 `python scripts/eval_gold.py gold <회차>`.
     이 길로 오면 3, 4단계를 따로 기다리지 않는다(아래 3, 4는 화면을 나눠 할 때).
3. **03_schema_approval, human** ⏸: "03_schema_draft.yaml을 고쳐 03_schema_approved.yaml로 저장한 뒤 알려 주세요"라고 하고 턴을 끝낸다. 담당자가 알리면 `python scripts/check_inputs.py <회차> --schema`. 오류가 있으면 보여 주고 다시 기다린다. 통과하면 end.
4. **04_gold_tagging, human** ⏸(관문 기다림은 wait start/end, 라벨링 시간은 화면의 gold_label_times.json): `python scripts/eval_gold.py sheet <회차>`를 부르고, 담당자에게 "runs/<회차>/gold/gold_tagging.html을 브라우저로 열어 30개를 태깅한 뒤, '제출'로 받은 두 파일(gold_tags.jsonl, gold_label_times.json)을 runs/<회차>/gold/에 저장하고 알려 주세요"라고 하고 턴을 끝낸다. 주제나 감성을 제안하거나 고치지 않는다. 담당자가 알리면 `python scripts/eval_gold.py gold <회차>`. 오류가 있으면 보여 주고 다시 기다린다.
5. **05_tagging, agents**:
   1. `python scripts/tag_batches.py plan <회차>`(묶음 크기 기본 75). 출력의 묶음 수와 시험 태깅 묶음을 알린다. 75는 2026-10-20 담당자 결정이다: yogamatx4 시험에서 묶음 50(yogamatx3)보다 다시 태깅 4/41에서 1/30, 정답 세트 주제 F1 0.87에서 0.89, 감성 86.7%에서 89.1%, 태그 감사 FAIL 5/150 같음, sonnet 캐시 쓰기 6.24M에서 5.92M.
   2. 시험 태깅: 04_batches.json의 pilot_batches(리뷰가 가장 적은 ASIN의 묶음과 gold 묶음)만 review-tagger로 부른다(작업자 상한 안에서 동시).
      - ASIN 묶음과 gold 묶음(sonnet): Agent 호출에 `model: sonnet`. 프롬프트 `회차: <회차>`, `묶음: <batch_id>`, `모델 표시: sonnet`
      - gold 묶음(상위 모델 비교): 모델을 따로 주지 않는다. 프롬프트 `회차: <회차>`, `묶음: gold`, `모델 표시: top`
      그다음 `python scripts/audit_quotes.py tags <회차> --model sonnet --batches <시험 ASIN 묶음들>,gold`, `python scripts/audit_quotes.py tags <회차> --model top`, `python scripts/eval_gold.py score <회차>`(04_tags.jsonl이 아직 없으니 gold 묶음의 sonnet 태그로 채점).
   3. **05a_pilot**(자동 진행): 시험 태깅에 걸린 시간(timing.jsonl의 에이전트 시작과 끝), 묶음 수와 리뷰 수, 인용 검사 결과, 채점 한 줄 요약(summary_ko), 남은 묶음 수를 "정한 것"으로 알리고 이어서 한다. 인용 검사가 FAIL이면 그 묶음만 다시 태깅한 뒤 간다.
   4. 이어서 시험 태깅 묶음(pilot_batches)을 뺀 나머지 sonnet 묶음을 묶음마다 review-tagger 하나로 부른다(per_batch, `model: sonnet`, 남은 묶음 전부를 한 메시지에 모두, 위 상한 표의 동시 수 안에서). 프롬프트는 시험 태깅과 같은 형식(`회차: <회차>`, `묶음: <batch_id>`, `모델 표시: sonnet`).
6. **06_tag_check, agents**: 아래를 차례로 한다.
   0. **태거가 다 썼는지 먼저 기다린다(2026-10-21 담당자 결정)**: `python scripts/wait_files.py <회차> --batches 04_batches.json --name "04_tags_sonnet_{batch_id}.jsonl"`(모든 sonnet 묶음 출력이 생기고 15초 동안 안 바뀔 때까지). 끝 알림이나 모든 태거의 끝 보고가 온 뒤에 1을 부른다. 지난 다시 돌리기에서 아직 쓰는 묶음 파일을 검사해 FAIL로 본 일이 있었다. 다시 태깅한 묶음도 같은 방법으로 그 파일만 기다린 뒤 다시 검사한다. 06이 바꾸는 04_tags_sonnet_*.jsonl은 stages.yaml의 edits라 mark end를 막지 않는다.
   1. `python scripts/audit_quotes.py tags <회차> --model sonnet`(모든 sonnet 묶음을 검사하고 통과하면 04_tags.jsonl로 합침, 인용 앞 부정어는 경고). 합친 뒤 `python scripts/audit_quotes.py negation <회차>`로 부정어 경고 개수를 04_negation_check.json에 남긴다. 실패한 묶음(04_quote_check_sonnet.json의 failed_batches)만 review-tagger(sonnet)를 다시 부른다. 그 묶음의 오류를 프롬프트에 그대로 붙인다.
   2. 통과하면 `python scripts/eval_gold.py audit-sample <회차>`(감사자 둘 몫으로 리뷰 단위로 나눈 04_audit_sample_p1.jsonl, _p2.jsonl도 씀), 그다음 evidence-auditor(프롬프트: `stage: tags`, 회차, 자기 반쪽 파일 이름) 둘을 동시에 부른다. 돌려준 YAML 블록을 각각 04_tag_audit_p1.yaml, 04_tag_audit_p2.yaml로 저장하고 `python scripts/eval_gold.py audit <회차>`(두 반쪽이 표본을 빠짐없이 한 번씩 판정했는지 확인하고 04_tag_audit.yaml로 합침, 반쪽마다와 전체 FAIL 비율을 04_tag_audit_summary.json에 적음, 합치기 문제가 있으면 INCOMPLETE).
   3. 감사가 FAIL이면 batches_with_findings의 묶음만 review-tagger(sonnet)를 다시 부른다. 그 묶음의 감사 지적을 프롬프트에 그대로 붙인다. 그다음 1, 2를 다시.
   4. 다시 태깅은 sonnet으로 묶음마다 최대 2번. 그래도 실패한 묶음은 그 묶음만 상위 모델로 한 번 부르고(모델 표시는 sonnet 그대로, 파일 이름이 같아야 합쳐진다), 담당자에게 어느 묶음을 상위 모델로 다시 했는지 알린다.
   5. `python scripts/eval_gold.py score <회차>`. 출력의 모델별 한 줄 요약(04_gold_eval.json의 summary_ko, 예: "sonnet: 주제 F1 0.90(기준 0.80, 통과), 감성 일치 88.6%(기준 90.0%, 1.4%p 모자람)")을 담당자에게 글자 그대로 옮긴다. 기준과의 차이를 따로 계산하지 않는다. 판정은 리포트에 쓰는 sonnet 기준이다. 기준 미달이면 04_gold_eval.md의 불일치 목록을 보여 주고 `06_gold_review`(자동 진행)는 "이대로 진행(리포트 부록에 적음)"으로 정한다. 담당자가 스키마나 정답 태깅을 고치라고 하면 그때 3단계나 채점부터 다시.
   6. 끝나면 바로 "앞당겨 돌리는 단계"의 리포트 미리 쓰기(`weight.py --early`와 08a_report_early)를 부른다(2026-10-16). 6-1 세부 이슈 초안과 같은 때 돈다.
6-1. **07a_issue_draft, agents** (세부 이슈 목록 초안):
   1. `python scripts/issues.py sample <회차>`: 주제(전체 만족도 제외)와 방향(부정 이슈: 부정과 혼합 인용, 긍정 이슈: 긍정과 혼합 인용)마다 인용을 최대 150개, ASIN과 별점 묶음이 고르게 섞이게 뽑는다. 인용 20개 미만인 주제와 방향은 기타만.
   2. issue-labeler를 주제마다 하나씩 부른다(모델은 따로 주지 않음, 상위 모델. 상위 모델 작성자 상한(15) 안에서 동시에. 주제가 15개 이하면 기타만인 주제까지 모두 한 메시지에. 작은 주제를 뒤로 미루지 않는다). 프롬프트 `회차: <회차>`, `주제: <topic id>`. 출력은 07a_issues_<주제>.yaml.
   3. `python scripts/issues.py merge <회차>`. 오류가 있으면 그 주제의 issue-labeler에게 오류를 주고 한 번 고치게 한다. 주제를 따로 동시에 썼으므로, 메인 세션이 주제끼리 뜻이 겹치는 라벨(같은 불만이 두 주제에 있음)을 확인해 담당자에게 보여 줄 표에 적는다. 07a_issues_draft.md의 주제별 표를 담당자에게 보여 준다.
6-2. **07a_issue_approval**(자동 진행): 07a_issues_draft.md의 주제별 표와 merge 검사 경고를 "정한 것"으로 보내고, 초안 그대로(검사 경고가 있으면 그것만 고쳐) 승인한 뒤 이어서 한다.
   - 승인 기록: `python scripts/issues.py approve <회차> --approved-at <UTC 시각> --approved-by "<누가, 어떻게>"`가 초안을 07a_issues_approved.yaml로 복사하고 승인 시각과 승인자를 적는다.
     perfume-db-2026-10-07: 2026-10-07T09:09Z, 담당자, 카드 "제안 반영 후 승인"(라벨 71개).
6-3. **07b_issue_labeling, agents**: 승인 목록으로 라벨을 붙인다. 주제와 감성 태그는 다시 하지 않는다.
   1. `python scripts/issues.py label-plan <회차>`: 전체 만족도와 중립을 뺀 태그 인용(혼합은 두 방향 모두)을 주제와 방향마다 최대 180개 묶음으로 나눈다(07b_label_batches.json, 07b_label_input/). 승인 라벨이 없는 주제와 방향은 스크립트가 기타로 채운다(07b_labels_auto.jsonl).
      `python scripts/issues.py safety-input <회차>`: 안전 주제 인용 전부와 리뷰 원문(07c_safety_input.jsonl).
   2. issue-tagger를 묶음마다 하나씩 부른다(per_batch, Agent 호출에 model: sonnet, 묶음 전부를 한 메시지에 모두, 상한 표의 동시 수 안에서). 프롬프트 `회차: <회차>`, `묶음: <batch_id>`. 같은 때 evidence-auditor(`stage: safety`)를 부르고 돌려준 YAML 블록만 07c_safety_verdicts.yaml로 저장한다.
   3. `python scripts/issues.py label-check <회차>`: 승인 라벨이나 other, 1~2개, other 단독, 입력 인용 빠짐 없음. 통과하면 07b_issue_labels.jsonl과 07b_issue_counts.json(라벨마다 리뷰 수, 가중 비율, ASIN별 수, 기타 비율, 향과 신뢰의 향 차이 라벨 겹침)을 쓴다. 실패한 묶음(failed_batches)만 오류를 붙여 다시 부른다. 최대 2번, 그래도 실패하면 stop.
   4. `python scripts/issues.py safety-render <회차>`: 07c_safety_check.md(인용, 원문, 판정, 이유)와 07c_safety_summary.json.
6-4. **07c_issue_check, script와 agents**: `python scripts/issues.py audit-sample <회차>`(ASIN과 주제를 고르게 150개, 감사자 둘 몫으로 07b_issue_audit_sample_p1.jsonl과 _p2.jsonl 75개씩), evidence-auditor(`stage: issues`) 둘을 동시에 부르고(프롬프트에 자기 반쪽 파일 이름) 돌려준 YAML 블록을 각각 07b_issue_audit_p1.yaml, 07b_issue_audit_p2.yaml로 저장, `python scripts/issues.py audit <회차>`(두 반쪽이 표본 150개를 빠짐없이 한 번씩 판정했는지 확인하고 07b_issue_audit.yaml로 합침, 반쪽마다와 전체 FAIL 비율을 07b_issue_audit_summary.json에 적음, 전체 FAIL 5% 이하면 PASS, 합치기 문제가 있으면 INCOMPLETE). FAIL이면 stop하고 리포트로 넘어가지 않는다.
   - 의심 태그(주제나 감성이 틀려 보이는 인용)는 고치지 않고 07c_tagging_error_notes.md에 review_id와 이유를 적는다.
   - 7단계 weight.py가 07b_issue_counts.json, 07b_issue_labels.jsonl, 07c_safety_summary.json을 읽어 05_metrics.json의 issues, issue_overlap, safety_check, brand_deep[].strengths/weaknesses[].top_issues와 05_tables.md의 세부 이슈 표를 만든다.
7. **07_weight, script**: `python scripts/weight.py <회차>`. 실패하면(자체 검사 포함) 계산 문제이니 stop하고 출력을 그대로 보여 준다.
8. **08_report, agents**: 라벨이 끝난 뒤의 장 묶음만 쓴다(2026-10-16, 장 묶음 7개: 1-7, 8, 9, 10, 11, 12, appendix).
   1. report-writer 다섯을 동시에 부른다. 프롬프트는 `회차: <회차>`, `장: <묶음>`, `입력: <early|final|보강>`, `출력: <파일>`, `견본: config/exemplars/<품목>/report_exemplar.md`(시작 5번) 다섯 줄이다.
      - `장: 8`, `장: 10`, `장: 11`, `장: appendix`: `입력: final`, 출력 06_report_part_8.md, _10.md, _11.md, _appendix.md. 10장 작성자는 06_report_part_9.md를 먼저 읽는다.
      - `장: 1-7, 9`, `입력: 보강`, 출력 06_report_part_1-7.md와 _9.md(Edit로 고침): 미리 쓴 데이터 읽기에 세부 이슈 라벨, 안전 부정, 견고성 근거를 더한다(스피커 회차의 2, 3, 4, 7장에 있던 근거).
      - 08a 묶음 파일(06_report_part_1-7.md, _9.md)이 없으면(미리 쓰지 못한 회차) 보강 대신 `장: 1-7`, `장: 9`를 `입력: final`로 이때 함께 쓴다. 모두 top_writers 상한 안에서 센다.
   - **끝 보고를 기다리지 않는다(2026-10-20 담당자 결정)**: 작성자들을 띄운 직후 `python scripts/wait_files.py <회차> <그 작성자들의 출력 파일들>`을 Bash 백그라운드로 부른다. 그 끝 알림이나 작성자 끝 알림 가운데 먼저 오는 것으로 다음으로 간다. 파일이 다 생겼는데 끝 보고가 아직인 작성자는 기다리지 않는다(자리는 차지한 채 둠). 그 파일을 다시 고쳐 쓸 일이 생기면 그때만 그 작성자가 끝났는지 본다. yogamatx3-2026-10-20에서 12장 작성자가 12:17에 파일을 다 쓰고 끝 보고에 16분을 썼다(다른 작성자는 0.2~0.5분).
   2. 다섯이 끝나면(위 wait_files 알림 포함) `장: 12`, `입력: final`, `출력: 06_report_part_12.md`를 부른다(12장 작성자는 06_report_part_8.md, _10.md, _11.md를 먼저 읽는다). 인용은 05_quote_pool.json과 05_metrics.json의 quote_candidates에서만 고른다(04_tags.jsonl, 02_reviews.csv는 읽지 않음).
   3. `python scripts/report_parts.py assemble <회차>`: 묶음을 틀 순서로 이어 붙이고 `{{표: 이름}}` 자리에 05_tables.md 블록을 끼워 06_report.md를 쓴다. 묶음 빠짐, 다른 장 제목, 표를 직접 붙임, 표 자리 남음, early와 final 숫자 불일치는 FAIL이다. 불일치면 적힌 장을 `입력: final`로 다시 쓰고 assemble을 다시 부른다. 그 밖의 FAIL은 그 묶음만 다시 쓴다(한 번까지).
9. **09_report_check, agents**: `python scripts/audit_quotes.py report <회차>`, 그다음 evidence-auditor(`stage: report`, 회차). 돌려준 YAML 블록만 07_audit.yaml로 저장한다. 둘 중 하나라도 FAIL이면 다시 쓰기 줄이기(2026-10-14)대로 고친다: 06_report.md를 06_report_v<N>.md로 복사해 두고, report-writer에게 FAIL 항목(07_quote_check.json의 실패 줄, 07_audit.yaml의 FAIL과 고칠 문구)만 주고 Edit로 그 줄만 바꾸게 한다(2026-10-16. 파일 전체를 다시 쓰지 않고, 표 블록은 그대로). 그다음 audit_quotes.py report는 전체로, 감사는 `python scripts/guide_diff.py <회차> 06_report_v<N>.md 06_report.md --out 06_report_changed.md`의 바뀐 줄만 본다. 고치기는 한 번까지, 두 번째도 FAIL이면 멈추고 보고. next_action이 HUMAN_REVIEW_REQUIRED면 그 항목을 보여 주고 ⏸ 기다린다.
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
13. **13_detail_schema_draft, agents** (02 스키마 초안 뒤 바로, 승인을 기다리지 않음, "앞당겨 돌리는 단계"): `python scripts/detail.py sample <회차>`(13_detail_sample.csv, 150개, ASIN과 별점 묶음 고르게, 정답 세트 제외), detail-schema-drafter(모델 따로 주지 않음, 프롬프트 `회차: <회차>`), `python scripts/detail.py check <회차>`(FAIL이면 오류를 주고 최대 2번 다시).
   - 입력: 13_detail_sample.csv, config/categories/<카테고리>.yaml, 03_schema_approved.yaml(없으면 03_schema_draft.yaml), 07a_issues_approved.yaml(있을 때만. 없으면 출력에 labels_checked: false).
   - 출력: 13_detail_schema_draft.yaml, 13_detail_schema_draft.md, 13_detail_schema_check.json.
13a. **13a_detail_schema_approval**(자동 진행): 13_detail_schema_draft.md 표와 13_detail_schema_check.json 경고를 "정한 것"으로 보내고 초안 그대로(경고가 있으면 그것만 고쳐) 승인한 뒤 이어서 한다. 고칠 곳은 13_detail_schema_edits.yaml(split_values, extra)에 적고 `python scripts/detail.py approve <회차> --approved-at <UTC> --approved-by "<누가, 어떻게>"`로 13_detail_schema_approved.yaml을 만든다. 승인 전에는 전체 추출을 하지 않는다.
14. **14_detail_extract, agents**: `python scripts/detail.py plan <회차>`(ASIN마다 50개씩 묶음), `python scripts/stage_packet.py detail <회차> --items <항목들>`로 작업자별 작업 파일을 만들고 detail-extractor를 작업자마다 하나씩(Agent 호출에 model: sonnet, 작업 파일을 만든 직후 작업자 전부를 한 메시지에 모두, 상한 표의 동시 수 안에서), `python scripts/detail.py extract-check <회차>`(형식, extra 조건, 빠진 리뷰, JSON으로 읽지 못한 줄, 원문에 없는 인용은 모두 묶음 실패. 그 회차의 14_known_exceptions.yaml에 있는 칸만 KNOWN으로 따로 보임). 작업 파일에는 config/detail_rules.yaml의 공통 경계 규칙 가운데 맡은 항목이 걸린 것이 원문 그대로 들어간다. 실패한 묶음만 `--only`로 최대 2번 다시.
    - 출력: 14_details_<묶음>.jsonl, 14_details.jsonl, 14_detail_counts.json(항목과 값마다 리뷰 수, 가중 비율, ASIN별 수, 숫자 항목 중앙값), 14_detail_check.json
14b. **14b_detail_check, agents**: `python scripts/detail.py audit-sample <회차>`(항목과 ASIN 고르게 150개), evidence-auditor(`stage: details`)의 YAML 블록만 14b_detail_audit.yaml로 저장, `python scripts/detail.py audit <회차>`. FAIL 5%를 넘으면 멈추고 보고한다.
15. **15_research, agents** (12_market 뒤 바로, 스키마를 기다리지 않음, "앞당겨 돌리는 단계"): benchmark-researcher(모델 따로 주지 않음, 헤드리스면 --allowedTools에 WebSearch, WebFetch를 더함)가 15_research.yaml을 쓴다. amazon.com은 열지 않는다. `python scripts/research.py check <회차>`가 출처를 다시 열어 원문 문장을 확인한다(15_research_check.json, verified만 가이드에 씀).
    - **보충 조사(2026-10-20 담당자 결정, 한 번만)**: `python scripts/research.py followup-plan <회차>`가 첫 조사의 not_found와 check에서 unverified인 주장을 15_research_followup_input.json에 모은다. 0개면 건너뛴다. 1개 이상이면 benchmark-researcher를 한 번 더 부른다(프롬프트 `회차: <회차>`, `보충: 15_research_followup_input.json`). 그 목록만 찾아 15_research_followup.yaml에 쓴다(id는 fu_로 시작). 그다음 `python scripts/research.py merge <회차>`(첫 조사를 15_research_first.yaml로 남기고, 보충 주장을 더한 15_research.yaml을 씀, not_found는 보충 조사의 것으로 바꿈)와 `python scripts/research.py check <회차>`를 다시. 보충 조사는 다시 부르지 않는다(실패해도 첫 조사 결과로 간다).
      - **보충은 가이드를 기다리게 하지 않는다(2026-10-20 담당자 결정)**: followup-plan은 대상을 15개까지만 모으고(찾지 못한 것 먼저), 조사자는 페이지 열기 30번까지다. 16_guide_metrics를 부를 수 있게 됐는데 보충이 아직이면 기다리지 않고 첫 조사의 15_research_check.json으로 16, 17을 간다. 보충이 늦게 끝나면 merge와 check는 18_guide_check 전에 한다(merge는 주장을 더하기만 해서 가이드가 쓴 [r:id]는 그대로). 늦게 들어온 fu_ 주장은 이번 가이드에 쓰지 않고 00_auto_decisions.md에 개수만 적는다. yogamatx4에서 보충 10.4분과 다시 확인 2.3분이 가이드 시작을 그대로 늦췄다.
16. **16_guide_metrics, script**: `python scripts/guide_metrics.py <회차>`. **가이드 장 선택 고정(2026-10-20 담당자 결정)**: config/guide_plans/ 안에 이 회차 품목과 product(품목 이름)가 같은 계획이 있으면(회차 이름이나 설정 파일 이름이 달라도) 품목 설정 맨 위에 `guide_plan: <계획 파일 이름>`을 적고, guide 절을 채울 때 머리 주제, 방향 지수의 주제와 두 방향 이름, 집중 분석과 기준표의 id, 제목, 주제, 순서를 그 계획 그대로 쓴다. 라벨 id와 설계 정보 항목만 이 회차 승인본에서 고르고, 라벨은 그 장의 주제에 속한 것만 쓴다. guide_metrics.py가 대조해 다르면 멈춘다. 계획이 없는 처음 품목은 지금처럼 정하고, 회차가 끝나면 그 선택을 config/guide_plans/<품목>.yaml로 남겨 다음 회차부터 고정한다(담당자 확인). yogamatx3과 yogamatx4가 같은 자료로 방향 지수를 두께와 그립으로 다르게 골라 가이드 머리가 달라졌다. 카테고리마다 다른 것(머리 숫자 노드, 방향 지수 라벨, 기준표 후보, 검색어 성별 낱말, 집중 분석)은 config/categories/<카테고리>.yaml의 guide 절에서 읽는다. 출력: 16_guide_metrics.json(values, tables, ev 근거 묶음 최대 80개, quotes, caveats)과 작성자용 16_guide_writer_input.json(ev의 리뷰 id 목록만 뺌).
17. **17_guide_write, agents**: guide-writer(모델 따로 주지 않음)가 16_guide_writer_input.json과 확인된 15_research만 보고 쓴다. 숫자 뒤에 [m:키], 사양과 규제 뒤에 [r:id]. 표는 쓰지 않는다(HTML 스크립트가 그림).
   - 장 묶음(2026-10-17 안 B): 1차로 `장: 03`과 `장: 04`(`입력: final`, 출력 17_guide_part_03.md, _04.md)를 같은 때 부른다. 이 둘은 Agent 호출에 effort: high를 준다(2026-10-20 담당자 결정: 정확도 우선. medium은 2026-10-17 E7에서 6.7분 대 high 11.0분으로 빨랐지만 기계 검사 FAIL이 하나 더 나옴). 18_guide_audit_early.yaml의 지적(required_action)을 두 프롬프트에 "같은 단정을 쓰지 말 것"으로 붙인다(E1에서 02장에 고친 단정을 04장이 되풀이함). 원인 번호는 둘 다 16_guide_metrics.json의 p.causes(guide_metrics.make_causes, 카테고리 설정 guide.preference_labels)를 따른다. 17_guide_part_01-02-A_early.md가 없으면(미리 쓰지 못한 회차) 1차에 `장: 01-02-A`(`입력: final`, 출력 17_guide_part_01-02-A.md)도 03, 04와 같은 때 부른다(셋을 같은 때, effort는 기본). 둘(또는 셋)이 끝나면 2차로 `장: head-05`(`입력: final`, 출력 17_guide_part_head-05.md)와, 미리 쓴 판이 있을 때만 `장: 01-02-A`(`입력: 보강`, 17_guide_part_01-02-A_early.md를 읽고 17_guide_part_01-02-A.md로 씀, 18_guide_audit_early.yaml의 지적을 프롬프트에 붙임)를 같은 때 부른다. 그다음 `python scripts/guide_parts.py assemble <회차>`(장 순서로 이어 17_guide.md, 맡지 않은 장, 원인 번호와 기준 제목 대조, 방향 부호 FAIL, 머리 숫자 주제 1위 단정은 경고 → 17_guide_parts_check.json). FAIL이면 그 묶음만 다시 쓴다(한 번까지).
   - **끝 보고를 기다리지 않는다(2026-10-20)**: 1차와 2차 모두 08_report와 같이 `wait_files.py`를 백그라운드로 불러, 파일이 다 생기면 작성자 끝 보고를 기다리지 않고 다음(2차, assemble)으로 간다. 가이드 줄(17, 18, 19)은 리포트 줄(08, 09, 11)의 작성자나 감사자를 기다리지 않는다. 한쪽 알림이 오면 그쪽만 다음 단계로 보낸다. yogamatx3-2026-10-20에서 가이드는 12:20에 다 썼는데, 리포트 12장 작성자의 끝 보고를 기다리느라 18 가이드 감사가 12:36(사용량 한도 멈춤)까지 시작되지 않았다.
   - **한 명이 17_guide.md 전체를 쓰지 않는다(2026-10-19 담당자 결정)**. 새 폴더 회차는 미리 쓴 판이 없다는 이유로 한 명이 다 써서 18.4분(나눠 쓴 r2는 11.7분)이 걸렸다. guide_check.py가 17_guide_parts_check.json이 없거나 PASS가 아니면 FAIL로 본다.
   - 18 라벨 뒤 감사는 17_guide.md의 03, 04, 05, 머리 숫자 장과 `python scripts/guide_diff.py <회차> 17_guide_part_01-02-A_early.md 17_guide_part_01-02-A.md --out 18_guide_changed.md`(보강으로 바뀐 줄)만 본다. 미리 쓴 판이 없던 회차는 01-02-A도 전체를 본다. 기계 검사(guide_check.py)는 전체로.
18. **18_guide_check, script와 agents**: `python scripts/guide_check.py <회차>`(18_guide_quote_check.json), evidence-auditor(`stage: guide`, 작성자와 같은 16_guide_writer_input.json을 읽음)의 YAML 블록만 18_guide_audit.yaml로 저장. 기계 검사 FAIL이나 감사 FAIL이 확인 수의 5%를 넘으면 다시 쓰기 줄이기(2026-10-14)대로 고친다: 17_guide.md를 17_guide_v<N>.md로 복사해 두고, guide-writer에게 FAIL 항목과 고칠 문구만 주고 Edit로 그 줄만 고치게 한다(처음부터 다시 쓰지 않음. 2026-10-17 E7: Write로 전체를 다시 쓰면 5.1분, Edit로 0.9분). 다시 감사는 guide_diff.py로 뽑은 바뀐 줄(18_guide_changed.md)만, 기계 검사는 전체로. 고치기는 한 번까지, 두 번째도 넘으면 멈추고 보고.
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
