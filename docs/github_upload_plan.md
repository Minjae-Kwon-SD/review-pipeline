# GitHub 올릴 목록 초안

아직 git 저장소를 만들지 않았고 아무 데도 올리지 않았다. 올릴 곳과 최종 목록은 담당자가 정한다. `.gitignore`는 아래 "뺄 후보"를 반영한 초안이다(그대로 적용하면 올림 249개 파일 7.5MB, 뺌 300개 파일 79.5MB, 2026-10-07 기준).

## 올릴 것

| 경로 | 크기 | 이유 |
|---|---|---|
| `README.md`, `CLAUDE.md` | 20K, 20K | 실행 방법, 원칙, 파일 계약 |
| `.claude/agents/` | 92K | 에이전트 정의 13개 |
| `.claude/commands/review-run.md` | 24K | 단계별 명령 |
| `.claude/hooks/timing.py`, `.claude/settings.json` | 4K, 4K | 시간 기록 Hook과 허용 규칙(토큰 없음) |
| `.mcp.json` | 1K | MCP 서버 주소. 인증 칸은 `${AMZ_REVIEW_TOKEN}` 참조만이고 값은 없음(아래 점검) |
| `config/` | 48K | 파이프라인 설정, 카테고리 설정, 공통 주제, 화면 문구 |
| `scripts/` | 520K | 숫자를 만드는 스크립트 전부 |
| `tests/` | 122K | 스크립트 시험과 작은 가짜 입력 |
| `docs/walkthrough.md`, `docs/doc_facts.md`, `docs/doc_facts.json`, `docs/doc_numbers_allow.yaml`, `docs/github_upload_plan.md`, `docs/mcp_tools.md` | 16K, 8K, 12K, 4K, 8K, 32K | 설명서, 문서 숫자 출처, MCP 도구 메모 |
| `runs/perfume-db-2026-10-07/`의 단계 결과(아래 뺄 것 제외) | 약 7MB | 결과물 HTML 3개, 승인 파일, 태그, metrics, 검사와 감사 결과, 시간 기록. 검토자가 결과물과 과정을 함께 볼 수 있게 |

## 뺄 후보(최종 결정은 담당자)

| 경로 | 크기 | 이유 |
|---|---|---|
| `.claude/settings.local.json` | 1K | 개인 권한 설정(이미 빼 둠) |
| `.env`, `*.key`, `*pwd*.txt` | 없음 | 키와 비밀번호가 생길 수 있는 이름(이미 빼 둠) |
| `runs/*/raw/` | 7.6M | 공유 리뷰 DB의 MCP 응답 원문(리뷰 원문 덤프) |
| `runs/*/market/raw/` | 59M | 시장 도구 응답 원문. 크고 다시 받을 수 있음 |
| `docs/mcp_samples/` | 6.0M | MCP 응답 견본(리뷰와 상품 원문 포함) |
| `runs/*/gold/` | 133K | 정답 세트. 공개하면 다음 채점이 오염될 수 있음 |
| `runs/*/02_reviews.csv`, `03_schema_input.csv`, `03_schema_sample.csv`, `13_detail_sample.csv` | 348K, 264K, 44K, 32K | 리뷰 원문 표 |
| `runs/*/07a_issue_samples/`, `07b_label_input/`, `14_detail_input/` | 240K, 345K, 344K | 에이전트 입력용 리뷰와 인용 묶음 |
| `runs/*/costs.jsonl` | 4K | 비용 기록(어림값이지만 내부 정보) |
| `runs/*/*_v1.*` 등 백업과 버린 판 | 2.9M | 판 바꾸기 전 백업. 최종본만 올림 |
| `.claude/launch.json` | 4K | 개인 PC 경로가 든 미리보기 설정 |

## 담당자가 정할 것

1. **결과물 HTML과 태그 파일 안의 리뷰 원문.** `06_report.html`, `06_report_en.html`, `07_guide.html`은 드릴다운을 위해 리뷰 원문을 파일 안에 담고 있고, `04_tags.jsonl`, `07b_issue_labels.jsonl`, `14_details.jsonl`에도 리뷰 인용이 있다. 원문 덤프를 빼더라도 이 파일들을 올리면 리뷰 내용이 공개된다. 비공개 저장소로 올리거나, 결과물 HTML은 저장소 밖으로 따로 전하는 방법이 있다.
2. **`docs/decisions_log.md`.** 대화 기록과 claude.ai 문서 링크, 이름이 들어 있다. 올릴지, 링크를 지운 판을 올릴지.
3. **`.mcp.json`의 서버 주소.** 값(토큰)은 없지만 사내 서버 주소가 들어 있다. 공개 저장소면 `.mcp.json.example`로 바꿔 올리는 것을 권한다.
4. **옛 시험 회차와 임시 파일**: v0 손 시험 회차(옛 runs 폴더)와 영어판 비교 임시 파일은 저장소 추적에서 뺐다(2026-10-08, PC 파일은 남김).

## 보안 점검(값은 출력하지 않음)

- `.mcp.json`의 인증 칸은 `Bearer ${AMZ_REVIEW_TOKEN}` 꼴의 환경 변수 참조만 있고 실제 값이 없다(글자 모양만 확인).
- 저장소 안 파일(`runs/`와 `docs/mcp_samples/`는 따로)에서 다음 꼴을 찾았다: Bearer 뒤 실제 값, `sk-` 꼴 키, 토큰이나 키나 비밀번호 대입, 환경 변수에 값 대입, 40자 이상 무작위 문자열, 키 폴더 경로. 키나 토큰은 0건이었다. 40자 이상 문자열로 걸린 것은 MCP 도구 이름, claude.ai 문서 링크, 미리보기 설정의 PC 경로였다.
- `runs/`와 `docs/mcp_samples/`에서도 Bearer 값, `sk-` 키, 토큰 대입은 0건이었다.
- 키 폴더는 열지 않았다.
