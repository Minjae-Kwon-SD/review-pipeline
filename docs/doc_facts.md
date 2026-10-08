# 문서 숫자 출처

회차 perfume-db-2026-10-07, 2026-10-08T23:17 기준. `python scripts/doc_facts.py build`가 만든다.

| 키 | 표기 | 출처 |
|---|---|---|
| gold.reviews | 30개 | 05_metrics.json accuracy.gold_reviews |
| gold.f1 | 0.96 | 05_metrics.json accuracy.sonnet.topic_f1_text |
| gold.sent | 93.0% | 05_metrics.json accuracy.sonnet.sentiment_text |
| gold.top_sent | 90.1% | 05_metrics.json accuracy.top.sentiment_text |
| data.asins | 6개 | 01_asins.csv status=selected |
| data.tags | 3,497개 | 04_tags.jsonl 줄 수 |
| data.reviews | 1,212개 | 02_reviews.csv 행 수 |
| data.dropped | 2개 | 02_collect_log.json dropped_count |
| data.topics | 12개 | 03_schema_approved.yaml topics |
| data.labels | 71개 | 07a_issues_approved.yaml 라벨 수(other 빼고) |
| gold.tags | 106개 | gold/gold_tags.jsonl 줄 수(내용은 읽지 않고 줄만 셈) |
| audit.tags | 147개 중 FAIL 2개(1.4%) | 04_tag_audit_summary.json |
| audit.tags_cons | 8.3% | 04_tag_audit_summary.json conservative_rate(FAIL + UNVERIFIED + missed) |
| audit.tags_parts | UNVERIFIED 1개, 빠진 태그 10개, 뺀 정답 세트 태그 3개 | 04_tag_audit_summary.json |
| audit.labels | 150개 중 FAIL 1개(0.7%) | 07b_issue_audit_summary.json |
| audit.details | 150개 중 FAIL 4개(2.7%) | 14b_detail_audit_summary.json |
| audit.translation | 91쌍 중 FAIL 2개(2.2%) | 06_report_en_audit.yaml |
| html.report_numbers | 1053개 | 06_report_html_check.json numbers_checked |
| html.report_drill | 371개 | 06_report_html_check.json drilldowns_checked |
| html.report_kb | 756KB | 06_report_html_check.json size_kb |
| html.en_numbers | 957개 | 06_report_en_html_check.json |
| html.en_drill | 371개 | 06_report_en_html_check.json |
| html.en_kb | 749KB | 06_report_en_html_check.json size_kb |
| html.guide_numbers | 312개 | 07_guide_html_check.json numbers_checked |
| html.guide_bundles | 155개 | 07_guide_html_check.json evidence_bundles |
| html.guide_links | 271개 | 07_guide_html_check.json source_links |
| html.guide_kb | 785KB | 07_guide_html_check.json size_kb |
| detail.values | 1,629개 | 14_detail_check.json values |
| detail.items | 14개 | 13_detail_schema_approved.yaml items |
| research | 104개 중 80개 | 15_research_check.json claims, verified |
| market.calls | 64번 | market/calls.jsonl 줄 수 |
| specs.verified | 52개 | 23_specs_check.json verified |
| specs.products | 6개 | 23_specs_check.json by_asin |
| robust.n | 2,000번 | 05_robustness.json bootstrap.n |
| robust.head_first | 100.0% | 05_robustness.json texts.head_first |
| robust.head_neg_ci | 8.2%~11.9% | 05_robustness.json texts.head_neg_ci |
| robust.loo_flips | 6번 중 0번 | 05_robustness.json texts.loo_flips |
| robust.weakest | 6개 중 5개(리뷰를 다시 뽑아 보면 3~5개) | 05_robustness.json texts.weakest |
| guide.growth | "hair perfume spray" 최근 4주 530,006, 1년 전 같은 4주 11,322, 46.81배 | 16_guide_metrics.json values.head.fastest_term |
| time.review.first | 113.9분 | timing.jsonl 리뷰 리포트 단계 모든 시도 합(사람 대기 빼고) |
| time.review.rerun | 63.7분 | timing.jsonl 리뷰 리포트 단계 마지막 시도 합(고치기 단계 11_report_polish, 11b_polish_audit, 18b_guide_fix, 20_head_growth, 20b_head_text, 23c_specs_cleanup, 24_report_fix, 24b_report_en_fix, 25_guide_g5, 25b_guide_consistency, 26_claim_strength, 26b_source_drop, 27_rejudge, 27b_rejudge_audit, 27c_rejudge_guide 빼고) |
| time.review.human | 206.7분 | timing.jsonl 리뷰 리포트 사람 대기(⏸) 단계 |
| time.guide.first | 81.3분 | timing.jsonl 개발 가이드 단계 모든 시도 합(사람 대기 빼고) |
| time.guide.rerun | 74.9분 | timing.jsonl 개발 가이드 단계 마지막 시도 합(고치기 단계 11_report_polish, 11b_polish_audit, 18b_guide_fix, 20_head_growth, 20b_head_text, 23c_specs_cleanup, 24_report_fix, 24b_report_en_fix, 25_guide_g5, 25b_guide_consistency, 26_claim_strength, 26b_source_drop, 27_rejudge, 27b_rejudge_audit, 27c_rejudge_guide 빼고) |
| time.guide.human | 21.4분 | timing.jsonl 개발 가이드 사람 대기(⏸) 단계 |
| time.en.first | 173.5분 | timing.jsonl 영어판과 보강(G3 이후) 단계 모든 시도 합(사람 대기 빼고) |
| time.en.rerun | 63.6분 | timing.jsonl 영어판과 보강(G3 이후) 단계 마지막 시도 합(고치기 단계 11_report_polish, 11b_polish_audit, 18b_guide_fix, 20_head_growth, 20b_head_text, 23c_specs_cleanup, 24_report_fix, 24b_report_en_fix, 25_guide_g5, 25b_guide_consistency, 26_claim_strength, 26b_source_drop, 27_rejudge, 27b_rejudge_audit, 27c_rejudge_guide 빼고) |
| time.en.human | 0.0분 | timing.jsonl 영어판과 보강(G3 이후) 사람 대기(⏸) 단계 |
| time.total.first | 368.7분 | time.<영역>.first 세 영역 합 |
| time.total.rerun | 202.2분 | time.<영역>.rerun 세 영역 합 |
| time.total.human | 228.1분 | time.<영역>.human 세 영역 합 |
| html.report_chapters | 13개 장 | scripts/render_html.py CHAPTERS |
| topics.common | 11개 | config/topics_common.yaml topics |
| step.01_inputs | 0.1분 | timing.jsonl 01_inputs 마지막 시도 |
| step.02_schema_draft | 7.0분 | timing.jsonl 02_schema_draft 마지막 시도 |
| step.03_schema_approval | 5.5분 | timing.jsonl 03_schema_approval 마지막 시도 |
| step.04_gold_tagging | 178.5분 | timing.jsonl 04_gold_tagging 마지막 시도 |
| step.05a_pilot | 9.5분 | timing.jsonl 05a_pilot 마지막 시도 |
| step.05_tagging | 22.0분 | timing.jsonl 05_tagging 마지막 시도 |
| step.06_tag_check | 3.2분 | timing.jsonl 06_tag_check 마지막 시도 |
| step.07_weight | 0.0분 | timing.jsonl 07_weight 마지막 시도 |
| step.08_report | 8.8분 | timing.jsonl 08_report 마지막 시도 |
| step.09_report_check | 11.9분 | timing.jsonl 09_report_check 마지막 시도 |
| step.10_timing | 0.0분 | timing.jsonl 10_timing 마지막 시도 |
| step.07a_issue_draft | 2.9분 | timing.jsonl 07a_issue_draft 마지막 시도 |
| step.07a_issue_approval | 13.3분 | timing.jsonl 07a_issue_approval 마지막 시도 |
| step.07b_issue_labeling | 2.4분 | timing.jsonl 07b_issue_labeling 마지막 시도 |
| step.07c_issue_check | 2.4분 | timing.jsonl 07c_issue_check 마지막 시도 |
| step.11_report_polish | 7.5분 | timing.jsonl 11_report_polish 마지막 시도 |
| step.11b_polish_audit | 2.6분 | timing.jsonl 11b_polish_audit 마지막 시도 |
| step.11_html | 3.0분 | timing.jsonl 11_html 마지막 시도 |
| step.12_market | 13.1분 | timing.jsonl 12_market 마지막 시도 |
| step.13_detail_schema_draft | 13.8분 | timing.jsonl 13_detail_schema_draft 마지막 시도 |
| step.13a_detail_schema_approval | 21.4분 | timing.jsonl 13a_detail_schema_approval 마지막 시도 |
| step.14_detail_extract | 5.2분 | timing.jsonl 14_detail_extract 마지막 시도 |
| step.14b_detail_check | 4.5분 | timing.jsonl 14b_detail_check 마지막 시도 |
| step.16_guide_metrics | 0.3분 | timing.jsonl 16_guide_metrics 마지막 시도 |
| step.15_research | 16.8분 | timing.jsonl 15_research 마지막 시도 |
| step.17_guide_write | 13.4분 | timing.jsonl 17_guide_write 마지막 시도 |
| step.18_guide_check | 6.6분 | timing.jsonl 18_guide_check 마지막 시도 |
| step.18b_guide_fix | 6.4분 | timing.jsonl 18b_guide_fix 마지막 시도 |
| step.19_guide_html | 1.1분 | timing.jsonl 19_guide_html 마지막 시도 |
| step.20_head_growth | 8.2분 | timing.jsonl 20_head_growth 마지막 시도 |
| step.20b_head_text | 10.7분 | timing.jsonl 20b_head_text 마지막 시도 |
| step.21_report_en_translate | 16.8분 | timing.jsonl 21_report_en_translate 마지막 시도 |
| step.21b_report_en_audit | 0.0분 | timing.jsonl 21b_report_en_audit 마지막 시도 |
| step.22_robustness | 2.5분 | timing.jsonl 22_robustness 마지막 시도 |
| step.24_report_fix | 15.4분 | timing.jsonl 24_report_fix 마지막 시도 |
| step.23_specs | 19.3분 | timing.jsonl 23_specs 마지막 시도 |
| step.23c_specs_cleanup | 1.9분 | timing.jsonl 23c_specs_cleanup 마지막 시도 |
| step.24b_report_en_fix | 2.7분 | timing.jsonl 24b_report_en_fix 마지막 시도 |
| step.23b_research_add | 12.8분 | timing.jsonl 23b_research_add 마지막 시도 |
| step.25_guide_g5 | 15.4분 | timing.jsonl 25_guide_g5 마지막 시도 |
| step.25b_guide_consistency | 7.0분 | timing.jsonl 25b_guide_consistency 마지막 시도 |
| step.26_claim_strength | 25.1분 | timing.jsonl 26_claim_strength 마지막 시도 |
| step.26b_source_drop | 4.9분 | timing.jsonl 26b_source_drop 마지막 시도 |
| step.27_rejudge | 6.9분 | timing.jsonl 27_rejudge 마지막 시도 |
| step.27b_rejudge_audit | 7.1분 | timing.jsonl 27b_rejudge_audit 마지막 시도 |
| step.27c_rejudge_guide | 4.5분 | timing.jsonl 27c_rejudge_guide 마지막 시도 |
| step.28_note_fix | 8.2분 | timing.jsonl 28_note_fix 마지막 시도 |
| step.29_concl_write | 0.8분 | timing.jsonl 29_concl_write 마지막 시도 |
| step.29b_concl_audit | 1.5분 | timing.jsonl 29b_concl_audit 마지막 시도 |
| step.29c_concl_fix | 1.6분 | timing.jsonl 29c_concl_fix 마지막 시도 |
| cost.review | $70.42 | costs.jsonl 리뷰 리포트 실행 14번 합 |
| cost.review.runs | 14번 | costs.jsonl |
| cost.guide | $28.31 | costs.jsonl 개발 가이드 실행 5번 합 |
| cost.guide.runs | 5번 | costs.jsonl |
| cost.en | $46.90 | costs.jsonl 영어판과 보강(G3 이후) 실행 14번 합 |
| cost.en.runs | 14번 | costs.jsonl |
| cost.total | $145.63 | costs.jsonl 전체 합 |
| cost.runs | 33번 | costs.jsonl 줄 수 |
| tests | 335개 | tests/test_scripts.py 실행 결과의 확인 개수 |
| ref.report.reviews | 3,488개, ASIN 10개 | 정답지 review_analysis_report_en.html 머리 문장 |
| ref.report.tags | 10,066개 | 정답지 review_analysis_report_en.html 머리 문장 |
| ref.guide.reviews | 12,380개, 리스팅 37개, 카테고리 9개 | 정답지 Coolmate_Scrubs_Product_Dev_Guide_v1.html 머리 문장 |
| ref.guide.specs | 리스팅 사양 37개, 사이즈표 31개 | 정답지 Coolmate_Scrubs_Product_Dev_Guide_v1.html 머리 문장 |
| ref.guide.terms | 7,346개 | 정답지 Coolmate_Scrubs_Product_Dev_Guide_v1.html 머리 문장 |
