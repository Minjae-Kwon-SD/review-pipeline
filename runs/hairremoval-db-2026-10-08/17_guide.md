# 아마존 미국 가정용 IPL, 레이저 제모기 제품 개발 가이드
> 아마존 미국에 새로 들어오는 브랜드를 위한 기준: 누구에게 맞는지 먼저 밝히고, 고장 없이 쓰게 만들고, 효과를 확인할 때까지 보증합니다

## 머리 숫자
- [head.market_year] 아마존 Laser, Light & Electrolysis Hair Removal 노드의 월 매출 칸을 달러로 읽고 한 해로 늘린 값입니다. 단위가 확인되지 않아 시장 크기의 방향만 보여 주며 SAM 확정에는 쓰지 않습니다.
- [head.topic_neg] 제모 효과를 부정으로 말한 리뷰어 비율(별점 가중)로, 불만 지도 1위입니다. 2위 품질과 차이가 작아 두 문제를 함께 풀어야 합니다.
- [head.topic_weakest] 점수표 상품 가운데 가장 큰 약점이 제모 효과인 상품 수이고, 괄호는 리뷰를 다시 뽑아 보았을 때의 범위입니다. 과반이 아니므로 효과 하나로 모든 경쟁사를 앞선다고 볼 수 없고, 품질 약점과 함께 봐야 합니다.
- [head.dir_ratio] 통증 방향입니다. 편안하다는 쪽이 아프다는 쪽보다 훨씬 많아, 냉각과 낮은 통증은 이길 자리가 아니라 갖춰야 할 기본입니다.
- [head.fastest_term] 주간 검색량 이력으로 본 성장 배수(정의는 01장 검색 수요)가 가장 큰 카테고리 검색어입니다. 새 수요가 아니라 경쟁 브랜드 이름이라, 기회보다 경쟁 신호로 읽습니다.

## 01 시장 개요
이 장은 시장 크기, 경쟁 집중도, 검색 수요로 들어갈 만한지와 들어가는 조건을 봅니다.

**TL;DR** 미국 가정용 IPL, 레이저 제모기만의 시장 규모는 공개 자료에서 확인되지 않았고, 관련 시장(미국 가정용 뷰티 기기, 세계 가정용 IPL)은 큽니다 [r:mkt_01] [r:mkt_03] [r:mkt_04]. 아마존 Light Hair Removal Devices 노드는 상위 10개 브랜드 합이 96.2% [m:m.top10_share_IPL]로 몰려 있습니다. 들어가려면 510(k) 허가와 근거 있는 효과 주장을 갖추고, 경쟁사가 약한 효과 기대 관리와 내구성에서 차이를 만들어야 합니다.

### TAM, SAM, SOM: 미국 가정용 제모기만의 규모는 확인되지 않음
아래 표는 시장 데이터(spd-amz-market)의 하위 카테고리와 브랜드 점유율입니다. 월 매출, 증감, azRevenuePct 칸은 문서에 단위가 없어 크기 비교로만 읽습니다.

- **TAM(관련 시장, 미국 가정용 제모기 단독 값 없음)**: 미국 가정용 뷰티 기기 시장은 2024년 74억 달러이고 [r:mkt_01], 그중 제모 기기가 2024년 25%로 가장 큰 비중입니다 [r:mkt_02]. 세계 가정용 IPL 제모기 시장은 QYResearch가 2024년 12억 4,800만 달러 [r:mkt_03], Spherical Insights가 2025년 19억 3천만 달러 [r:mkt_04]로 보아 서로 충돌합니다. 하나를 고르지 않고 범위로 두며, 이 값들을 곱하거나 나눠 미국 값을 만들지 않습니다.
- **주변 값**: 가정용 레이저 기기 전체 시장(제모만의 값이 아님)에서 북미는 2025년 6억 8,840만 달러, 38.2%로 가장 큰 지역입니다 [r:mkt_06]. 살롱용을 포함한 세계 제모 기기 시장은 2024년 37억 260만 달러이고 [r:mkt_08], 그중 가정용 기기가 45%입니다 [r:mkt_09]. 미국 면도와 제모 시장 전체는 2024년 38억 달러를 넘지만 성장은 제한적이고 [r:mkt_12], 가정용 레이저 시술이 다리 제모용 대체 기기의 성장에 기여한다고 봅니다 [r:mkt_13].
- **SAM(아마존 미국 Laser, Light & Electrolysis Hair Removal 노드)**: 8,196,134(월 매출 칸, 단위 미확인) [m:head.market_month]. 이 칸을 달러로 읽어 한 해로 늘리면 98,353,608(월 매출을 달러로 읽을 때 연 환산) [m:head.market_year]입니다. 단위를 확인하기 전까지는 크기의 감으로만 씁니다.
- **SOM(첫해 목표)**: UNVERIFIED(근거 숫자 없음). 확인이 필요한 권고로, 첫 제품이 들어갈 Light Hair Removal Devices 노드의 1위 Braun 38.1% [m:m.top1_IPL]와 상위 10개 합 96.2% [m:m.top10_share_IPL]를 기준선으로 두고, 단위가 확인된 매출과 우리 가격, 광고비가 정해진 뒤 다시 잡습니다.

### 판정 3개: 큰 관련 시장, 몰린 경쟁, 효과 기대와 고장이라는 빈자리
카테고리에 대한 세 가지 판단입니다.

- **크기: 관련 시장은 크지만 우리 시장의 크기는 아직 모릅니다.** 미국 가정용 뷰티 기기에서 제모 기기가 가장 큰 비중이고 [r:mkt_02], 아마존 노드의 월 매출 칸은 8,196,134(월 매출 칸, 단위 미확인) [m:head.market_month]입니다. 미국 가정용 제모기만의 규모와 성장률은 찾지 못했습니다.
- **경쟁: 몰려 있습니다.** Light Hair Removal Devices 상위 10개 브랜드 합은 96.2% [m:m.top10_share_IPL], 1위는 Braun 38.1% [m:m.top1_IPL]입니다. Braun Aura 9가 2026년 9월 OHT 510(k) 동등 판정을 받았고 [r:reg_07], Philips는 Lumea IPL을 아마존 미국 단독으로 판다고 밝혔습니다 [r:ind_11]. 성장 배수 1위 검색어도 Philips 이름으로 5.68배 [m:head.growth_multiple]입니다.
- **이길 자리(가설): 효과 기대 관리와 내구성.** 제모 효과 부정 7.2% [m:head.topic_neg]가 1위지만 품질 6.2% [m:p.map.quality]와 차이가 작고, 가장 큰 약점이 제모 효과인 상품은 5개 중 2개(리뷰를 다시 뽑아 보면 1~4개) [m:head.topic_weakest]로 과반이 아닙니다. 그래서 효과에 대한 기대와 고장을 함께 다루는 것을 개선 가설로 삼습니다.

### 검색 수요: 일반 검색어 중심, 성장 1위는 경쟁 브랜드 이름
표의 검색어에서 읽히는 것은 네 가지입니다.

- **어디서 시작할지: 일반 검색어.** 성별 낱말이 없는 공통 검색어 40개 [m:m.terms_common_n]의 30일 검색량 합은 1,051,188 [m:m.terms_common_volume]이고, 여성 검색어 10개 [m:m.terms_female_n]는 355,407 [m:m.terms_female_volume]입니다. 검색어 수가 달라 합만으로 비교하지 않습니다. 공통 검색어 상위의 laser hair removal, ipl laser hair removal, hair removal device가 새 브랜드가 노릴 일반 검색어입니다.
- **소비자가 무엇으로 검색하는지: laser라는 낱말.** IPL 기기를 찾는 검색어에도 laser가 붙습니다(ipl laser hair removal, lazer hair removal for women). 여성 검색어 상위에는 facial hair removal for women 같은 얼굴 검색어가 있습니다. 표에는 크림(veet hair removal cream for women), 면도기(braun series 9 pro), 더마플레이닝(michael todd beauty dermaplaning) 같은 다른 제모 방식의 검색어도 섞여 있어 개별 검색어를 골라 봐야 합니다.
- **검색에 보이지 않는 것: 남성 검색어와 피부색.** 성별 검색어 표(시장 데이터 관련 검색어) 안에서 남성 검색어는 0개 [m:m.terms_male_n]입니다. 다만 성장 표에는 nads hair removal for men(제모 크림 브랜드 검색어로 보임)이 있어, 남성 검색이 전혀 없다는 뜻은 아닙니다. 점수표 상품 제목에 for Women and Men이 있지만 기기를 찾는 남성 검색 수요는 이 표에서 확인되지 않습니다. 표의 상위 검색어에는 피부색이나 털 색 낱말도 없습니다.
- **가장 빨리 크는 것: 경쟁 브랜드 이름.** "philips hair removal" 최근 4주 37,227, 1년 전 같은 4주 6,556, 5.68배 [m:head.fastest_term]입니다. 성장 배수는 최근 4주 검색량 합을 1년 전 같은 4주 검색량 합으로 나눈 값이고, 두 기간은 2026-09-06 ~ 2026-09-27(1년 전 2025-09-07 ~ 2025-09-28) [m:head.growth_weeks]입니다. 30일 검색량 기준을 넘는 카테고리 검색어 49개 [m:m.growth_candidates] 가운데 두 기간 주간 이력이 있는 20개 [m:m.growth_ranked]에서 1위입니다. Philips가 Lumea IPL을 아마존 미국 단독으로 판다는 보도자료가 있지만 [r:ind_11], 검색 증가와의 관계는 확인하지 않았습니다. 두 기간을 4주씩만 견준 값이라 크기보다 방향으로 읽습니다.

가격대 표에서는 브랜드 평균 가격 207.96~572.23 [m:m.price_band3_range] 구간이 매출 비중 76.5% [m:m.price_band3_share]로 가장 크지만 평균 별점은 4.01★ [m:m.price_band3_rating]로 세 구간 중 가장 낮습니다. 88.14~199.84 [m:m.price_band2_range] 구간은 22.4% [m:m.price_band2_share]에 4.28★ [m:m.price_band2_rating]로 가장 높고, 8.98~82.46 [m:m.price_band1_range] 구간은 1.1% [m:m.price_band1_share]에 4.09★ [m:m.price_band1_rating]입니다. 별점은 가격과 함께 나온 값일 뿐이고, 값을 낮추면 별점이 오른다는 근거는 아닙니다.

### 진입 조건: 510(k) 허가와 효과 주장의 근거
아래는 확정된 사실이 아니라 확인이 필요한 권고입니다.

- **FDA 분류와 허가.** 빛 기반 일반 판매 제모기는 FDA 제품 코드 OHT로, 열 에너지로 모낭을 죽여 털을 없애는 일반 판매 기기로 정의됩니다 [r:reg_01]. 이 조항의 기기는 2등급(Class II)입니다 [r:reg_02]. Ulike 제조사의 IPL도 OHT 510(k) 동등 판정을 받았습니다 [r:reg_03]. 우리 제품의 허가 경로와 일정은 확인 필요(조사 근거 없음).
- **"영구"라는 말.** 허가 문구의 영구 털 감소(permanent reduction in hair regrowth)는 시술을 마친 뒤 일정 기간에 걸쳐 다시 나는 털 수가 오래 안정적으로 줄어든 것으로 정의되며, 영구 제거가 아닙니다 [r:reg_04]. Nood는 상세페이지에 permanent hair removal이라고 적지만 [r:ind_15] 이는 허가 문구와 다릅니다. 우리 상세페이지는 우리 허가 문구 안에서만 씁니다.
- **효과 숫자 주장.** FTC는 건강 효과 주장에 대체로 무작위 대조 인체 임상시험이 필요하다고 보고 [r:reg_16], 광고법은 모든 제품과 주장에 적용됩니다 [r:reg_17]. 업계 자율 심의기구 NAD는 IPL 제모기 광고를 회사가 심의를 거부하자 FTC와 FDA에 넘긴 적이 있습니다 [r:reg_18]. 경쟁사의 "몇 주 만에 몇 % 감소" 같은 문구를 근거 없이 따라 쓰지 않습니다.
- **피부색 범위.** 허가된 피부 유형은 브랜드마다 다릅니다. Ulike K223618은 Fitzpatrick I~V [r:reg_05], Cosbeauty는 I~IV [r:reg_06]입니다. 우리 범위는 우리 허가와 시험으로 정합니다.
- **반품과 보증.** 반품 기한이 지나 반품이나 환불이 안 된다는 불만이 17개 [m:std.returns_service.label.missed_return_window], 효과를 확인하기 전에 기한이 끝났다는 불만이 4개 [m:std.returns_service.label.window_ends_before_results]입니다. Braun은 100일 환불 보장을 내겁니다 [r:ind_07]. 효과를 확인할 때까지를 덮는 보증은 경쟁 기준선에 맞추기를 권하는 항목입니다(가설). 아마존 반품 정책과의 관계는 확인 필요(조사 근거 없음).
- **무선이라면 배터리 운송.** 리튬 전지는 UN 시험 기준 38.3을 통과한 형식이어야 운송할 수 있습니다 [r:reg_20].

## 02 경쟁사
리뷰로 본 각 경쟁사의 강점과 약점입니다.

**TL;DR** 가중 별점이 가장 높은 상품은 Ulike Air 10 Deluxe 4.57★ [m:s.B0G39WBP1S.star]이고, 가장 싼 INNZA 90.42달러 [m:s.B0CWL9S4L1.price]도 4.42★ [m:s.B0CWL9S4L1.star]로 비싼 Braun 4.20★ [m:s.B07WYY6KKC.star]보다 높습니다. 가장 큰 약점은 Ulike 두 리스팅이 제모 효과, Braun과 INNZA가 품질, PHILIPS가 가격 대비 가치입니다. 업계는 효과를 몇 주 만의 감소율로 내세우고 [r:ind_02] [r:ind_08], 환불과 보증 기간으로 차이를 둡니다 [r:ind_07] [r:ind_11].

### 점수표 해설: 강점은 효과와 편안함으로 갈리고 약점은 효과와 고장
- **Braun Silk Expert Pro 5 (B07WYY6KKC)**: 377.16달러 [m:s.B07WYY6KKC.price], 별점 4.20★ [m:s.B07WYY6KKC.star]로 다섯 상품 중 가장 낮습니다. 가장 큰 강점은 제모 효과지만 제모 효과 부정도 8.3% [m:s.B07WYY6KKC.topic_neg]이고, 가장 큰 약점은 품질입니다. 방향 지수 -0.10 [m:s.B07WYY6KKC.dir_index]로 아프다는 말과 편하다는 말이 비슷하게 섞여 통증 면에서 가장 약합니다. 말한 한 번 시술 시간 중앙값은 30분 [m:s.B07WYY6KKC.duration_median]입니다.
- **Ulike Air 10 (B0CV3ZJ2PN)**: 349.00달러 [m:s.B0CV3ZJ2PN.price], 별점 4.35★ [m:s.B0CV3ZJ2PN.star]. 제모 효과 부정 9.1% [m:s.B0CV3ZJ2PN.topic_neg]로 다섯 상품 중 가장 높고 가장 큰 약점도 제모 효과입니다. 강점은 통증과 시술 편안함으로, 방향 지수 -0.85 [m:s.B0CV3ZJ2PN.dir_index]입니다. 말한 시술 시간 중앙값은 60분 [m:s.B0CV3ZJ2PN.duration_median]으로 가장 깁니다.
- **INNZA (B0CWL9S4L1)**: 90.42달러 [m:s.B0CWL9S4L1.price]로 가장 싸고 별점은 4.42★ [m:s.B0CWL9S4L1.star]입니다. 제모 효과 부정 5.1% [m:s.B0CWL9S4L1.topic_neg]로 낮고 가장 큰 강점도 제모 효과입니다. 가장 큰 약점은 품질입니다. 방향 지수 -0.36 [m:s.B0CWL9S4L1.dir_index], 시술 시간 중앙값 10분 [m:s.B0CWL9S4L1.duration_median]입니다. 값과 효과 불만이 같은 방향으로 움직이지 않는다는 사례입니다.
- **PHILIPS Lumea 9000 (B0FGB2NS3C)**: 579.97달러 [m:s.B0FGB2NS3C.price]로 가장 비싸고 제모 효과 부정 2.1% [m:s.B0FGB2NS3C.topic_neg]로 가장 낮습니다. 가장 큰 약점은 가격 대비 가치입니다. 부정 표본이 하나뿐이라 낮은 불만 비율은 약한 근거입니다(A장). 방향 지수와 시술 시간은 값이 적어 내지 않았습니다. Philips는 제품 등록 시 5년 보증을 줍니다 [r:ind_11].
- **Ulike Air 10 Deluxe (B0G39WBP1S)**: 347.08달러 [m:s.B0G39WBP1S.price], 별점 4.57★ [m:s.B0G39WBP1S.star]로 가장 높습니다. 방향 지수 -1.00 [m:s.B0G39WBP1S.dir_index]로 아프다는 리뷰가 없습니다. 제모 효과 부정 8.2% [m:s.B0G39WBP1S.topic_neg]로 가장 큰 약점은 제모 효과입니다. Air 10과 같은 모델의 다른 리스팅이고 중립 표본이 없습니다. Ulike 공식몰은 Air 10 Deluxe를 369달러에 팝니다 [r:ind_01].

읽는 법: Ulike 두 리스팅은 같은 모델로 보이지만 시술 시간 중앙값이 60분 [m:s.B0CV3ZJ2PN.duration_median]과 10분 [m:s.B0G39WBP1S.duration_median]으로 다릅니다. 시간을 적은 리뷰가 적어 중앙값은 방향만 보여 줍니다. 광고의 시술 시간과 실제 경험이 다르면 감점된다는 점은 03장 집중 분석 4에서 다룹니다.

> "몸의 절반도 안 되는 부위를 하는 데 2시간쯤 걸린다" (Ulike, 1★, R253Q5MQJEFCR1)
> "한 번 전체 시술이 10분 정도밖에 걸리지 않는다" (Ulike, 5★, R3I3HAIAL07C08)

### 하위 카테고리 비교: 다섯 상품 모두 Light Hair Removal Devices
점수표 다섯 상품은 모두 Light Hair Removal Devices 노드에 있어 하위 카테고리끼리의 비교는 약합니다. 이 노드는 Laser, Light & Electrolysis Hair Removal의 하위 노드이고, 상위 10개 브랜드 합이 96.2% [m:m.top10_share_IPL]입니다. 상위 노드의 브랜드 표는 Braun 97.4% [m:m.top1_LLE], 상위 10개 합 100.0% [m:m.top10_share_LLE]로 한 브랜드가 거의 전부인데, 이 표가 하위 노드 상품을 얼마나 담는지는 확인 필요입니다. 다이오드 레이저는 Tria 4X가 공식몰 599.99달러 [r:ind_24]로 점수표 최고가인 PHILIPS 579.97달러 [m:s.B0FGB2NS3C.price]보다 높고, DermRays V4S 549달러 [r:ind_19]는 점수표 상단과 비슷한 값입니다(다이오드 레이저는 공식몰 값, 점수표는 아마존 값).

### 업계 구조: 숫자로 약속하는 효과, 길게 거는 보증
표의 업계 사례를 개발 결정으로 옮기면 다음과 같습니다.

- **효과를 숫자로 약속합니다.** Ulike는 Air 10에 2주 만에 96% 털 감소 [r:ind_02], Air 4에 4주 만에 95.8% [r:ind_04], Braun은 한 달 만에 95% [r:ind_08]를 각주와 함께 적습니다. Ulike의 510(k)는 벤치 시험만으로 이뤄졌고 임상 자료는 내지 않았다고 정리돼 있습니다(제3자 사이트 Innolitics의 정리 문장) [r:tst_10]. 새 브랜드가 같은 숫자를 쓰려면 FTC 기준의 임상 근거가 필요합니다 [r:reg_16].
- **환불과 보증 기간으로 차이를 둡니다.** Braun은 100일 환불 보장 [r:ind_07], Philips는 제품 등록 시 5년 보증 [r:ind_11]을 내겁니다.
- **본체 등급으로 값 사다리를 만듭니다.** Ulike는 Air 4 259달러 [r:ind_03]와 Air 10 Deluxe 369달러 [r:ind_01], Nood는 The Flasher 2.0 199달러 [r:ind_14]와 The Flasher Pro 379달러 [r:ind_16]를 둡니다. 위 단계에는 피부 관리 같은 두 번째 기능을 붙이기도 합니다 [r:ind_17].
- **200달러 안팎의 경쟁 상품이 있습니다.** SmoothSkin Pure Fit 199달러 [r:ind_20], wavytalk Bare It 216달러 [r:ind_22]입니다.
- **냉각을 내세웁니다.** wavytalk는 아이스 쿨링으로 시술을 시원하고 편하게 한다고 적습니다 [r:ind_23].
- **피부색과 털 색 범위를 밝힙니다.** Braun은 피부 유형 I~V에만 쓰도록 하고 [r:ind_09], 아주 옅은 금발, 붉은 털, 회색이나 흰 털에는 가장 맞지 않는다고 적습니다 [r:ind_10]. SmoothSkin도 흰 털, 회색 털, 붉은 털에는 IPL이 듣지 않는다고 적습니다 [r:ind_21]. DermRays는 어두운 피부색용 1064nm 다이오드 레이저를 따로 둡니다 [r:ind_18].
- **수명과 출력 단계를 숫자로 적습니다.** Braun Skin i-expert는 수명 발광 40만 회(권장 일정 기준) [r:ind_05], 출력 10단계 [r:ind_06]를 적습니다.

## 03 문제
이 장은 리뷰의 불만을 주제별로 재고, 큰 네 가지를 설계 정보 항목으로 나눠 봅니다.

**TL;DR** 가장 흔한 불만은 제모 효과 7.2% [m:p.map.hair_reduction]와 품질 6.2% [m:p.map.quality]이고, 가격 대비 가치 5.3% [m:p.map.price_value]가 뒤따릅니다. 효과 불만은 털 색이 짙은 리뷰어에게도 있고 얼굴에서 특히 약해, 출력만이 아니라 부위별 기대와 사용 조건을 함께 다뤄야 합니다. 고장은 발광과 센서에 몰리고, 고장까지 쓴 기간 중앙값은 6.5개월 [m:f.durability.failure_time.median]입니다.

### 불만 지도: 제모 효과와 품질이 근소한 1, 2위
주제별 부정 언급 리뷰어 비율(별점 가중)은 제모 효과 7.2% [m:p.map.hair_reduction], 품질 6.2% [m:p.map.quality], 가격 대비 가치 5.3% [m:p.map.price_value] 순입니다.
그다음은 안전 3.1% [m:p.map.safety], 시술 시간과 관리 부담 2.7% [m:p.map.treatment_time], 피부색과 털 색 적합성 2.5% [m:p.map.skin_hair_suitability], 디자인과 형태 2.1% [m:p.map.design], 사용 편의 2.0% [m:p.map.ease_of_use], 브랜드 경험 2.0% [m:p.map.brand_experience], 고객 응대 1.7% [m:p.map.customer_service], 통증과 시술 편안함 1.4% [m:p.map.pain_comfort], 신뢰 1.3% [m:p.map.trust], 구성품과 보관 케이스 0.6% [m:p.map.accessories]입니다.

읽는 법: 위 세 주제는 기기가 일을 하는지, 버티는지, 값을 하는지의 문제입니다. 통증과 시술 편안함은 1.4% [m:p.map.pain_comfort]로 아래쪽에 있어, 이 표본에서 통증은 큰 불만이 아닙니다. 리뷰를 다시 뽑아 보면 제모 효과가 1위로 남은 비율은 81.7% [m:a.robust.head_first]라 품질과 순위가 바뀔 수 있습니다.

> "18주 넘게 썼는데 나아진 게 없고, 오히려 일부 털은 더 빨리 다시 자라는 것 같다" (Braun, 1★, R2MTD56P6QYOUV)
> "여전히 정상보다 빨리 과열된다" (Ulike, 4★, RPKW26NCED8Q8)

### 별점 격차: 브랜드 경험, 신뢰, 가격 대비 가치
- **브랜드 경험**: 부정 리뷰 평균 1.48★ [m:p.gap1_neg] 대 나머지 4.40★ [m:p.gap1_other], 격차 -2.92 [m:p.gap1]. 다시 사지 않겠다, 추천하지 않겠다는 말입니다. 수리나 교체를 거절당한 리뷰에 붙은 사례가 있습니다(아래 인용).
- **신뢰**: 1.55★ [m:p.gap2_neg] 대 4.38★ [m:p.gap2_other], 격차 -2.83 [m:p.gap2]. 사기라는 말과, 어두운 피부에도 된다고 광고했다는 불만이 있습니다.
- **가격 대비 가치**: 1.68★ [m:p.gap3_neg] 대 4.49★ [m:p.gap3_other], 격차 -2.82 [m:p.gap3]. 비싸다는 말, 효과 없이 돈과 시간을 버렸다는 말, 산 뒤 값이 내려갔다는 말이 있습니다.

읽는 법: 별점 격차는 함께 나온 것이지 원인이 아닙니다. 세 주제 모두 기대와 실제의 차이, 판매 조건에 걸린 불만이라 상세페이지 문구와 보증 설계로 줄일 여지가 있습니다.

> "다시는 사지 않겠다" (Braun, 1★, R1BT7Y43OAYIN7)
> "어두운 피부도 쓸 수 있다고 하는 일종의 허위 광고와, 이 제품을 선물받아 그렇게 말하는 사람들" (Ulike, 2★, R2WKT4WSARV4ZP)
> "제조사가 내가 산 값보다 100달러 넘게 싸게 할인 판매했다" (Ulike, 4★, R1MER6HMWWEBWK)

### 집중 분석 1: 제모 효과, 부위와 조건에 따라 갈리는 결과
모든 리뷰를 다시 읽고 효과를 본 부위, 결과가 보인 시점, 리뷰어가 말한 털 색과 피부색, 사용 빈도, 출력 단계를 뽑았습니다.

- **얼굴이 가장 약한 부위입니다.** 얼굴에 효과가 없거나 약하다는 리뷰가 35개 [m:f.efficacy.area_result.face_weak]로 효과가 있다는 31개 [m:f.efficacy.area_result.face_works]보다 많은, 유일하게 약하다는 쪽이 많은 부위입니다. 다리는 효과 있음 68개 [m:f.efficacy.area_result.legs_works] 대 약함 17개 [m:f.efficacy.area_result.legs_weak], 겨드랑이는 65개 [m:f.efficacy.area_result.underarm_works] 대 23개 [m:f.efficacy.area_result.underarm_weak], 비키니는 25개 [m:f.efficacy.area_result.bikini_intimate_works] 대 25개 [m:f.efficacy.area_result.bikini_intimate_weak]입니다. 같은 기기라도 부위마다 기대를 다르게 말해야 합니다.
- **결과는 대개 일찍 보입니다.** 결과가 보인 시점을 말한 55개 [m:f.efficacy.time_to_results.total] 중 1~3회 쓰고 보였다는 리뷰가 24개 [m:f.efficacy.time_to_results.sessions_1_to_3], 4주 안에 보였다는 리뷰가 14개 [m:f.efficacy.time_to_results.weeks_under_4]이고, 3달 이상 걸렸다는 리뷰는 2개 [m:f.efficacy.time_to_results.months_3_plus]입니다. 몇 달을 기다리게 하기보다 언제쯤 변화를 확인할지 기준을 안내하는 편이 데이터와 맞습니다.
- **짙은 털에서도 효과 없음이 많습니다.** 검은, 갈색 털이라고 말한 리뷰는 106개 중 33개(31.1%) [m:f.efficacy.reviewer_hair_type.dark.no_effect], 금발이나 옅은 털은 20개 중 6개(30.0%) [m:f.efficacy.reviewer_hair_type.light_or_blonde.no_effect]가 효과 없음입니다. 밝은 피부는 85개 중 30개(35.3%) [m:f.efficacy.reviewer_skin_tone.fair_light.no_effect], 중간 톤은 17개 중 1개(5.9%) [m:f.efficacy.reviewer_skin_tone.medium.no_effect]입니다. 짙은 털과 밝은 피부라는 조건만으로 효과가 보장되지는 않습니다. 함께 나온 수일 뿐이고, 효과가 없었던 사람이 털 색과 피부색을 더 자주 적었을 수 있습니다.
- **자주, 세게 써도 효과 없음이 있습니다.** 주 2~4회 쓴다는 리뷰는 70개 중 25개(35.7%) [m:f.efficacy.usage_frequency.every_2_3_days.no_effect], 주 1회는 52개 중 10개(19.2%) [m:f.efficacy.usage_frequency.weekly.no_effect]가 효과 없음입니다. 가장 높은 단계로 쓴다는 리뷰는 34개 중 9개(26.5%) [m:f.efficacy.intensity_setting.highest.no_effect]가 효과 없음이었고, 낮게 시작해 높였다는 리뷰는 8개 중 0개(0.0%) [m:f.efficacy.intensity_setting.raised_over_time.no_effect]였습니다. 효과가 없어 더 자주, 세게 썼을 수도 있어 원인으로 읽지 않습니다.
- **개발에 주는 의미.** 효과 불만은 출력만으로 풀리는 문제가 아닙니다. 부위별 기대(특히 얼굴), 변화를 확인할 시점, 맞는 털 색과 피부색을 상세페이지와 설명서에 함께 적고, 효과 없음 161개 [m:std.efficacy.label.no_effect]를 줄이는 것을 첫 개발 목표로 둡니다.

> "두 달 동안 매일 썼는데도 여전히 이틀에 한 번 밤에 턱 털을 뽑아야 한다." (INNZA, 2★, R2NCETRZSVJSE1)
> "팔, 겨드랑이, 정강이에 가장 효과가 좋았고, 허벅지에는 절반 정도, 몸의 어두운 부위에는 거의 효과가 없었다" (Braun, 4★, R2WS99DB5KE8U8)
> "두 번째 시술 뒤 겨드랑이 털이 덜 나는 것을 느끼기 시작했다" (Braun, 5★, RBBCFQWS2G0TM)

### 집중 분석 2: 통증과 피부 반응, 편안함은 이미 기본
모든 리뷰를 다시 읽고 불편이 생긴 부위, 출력 단계, 면도 준비, 리뷰어가 말한 피부와 털 상태를 뽑았습니다.

- **편안하다는 쪽이 많습니다.** 편안함 180개 대 아픔 40개(4.50배) [m:head.dir_ratio]입니다. 통증 부정 64개 [m:std.pain_comfort.neg]는 약간 따끔함 15개 [m:std.pain_comfort.label.mild_sting], 민감한 부위 통증 14개 [m:std.pain_comfort.label.sensitive_area_pain], 심하게 아픔 13개 [m:std.pain_comfort.label.strong_pain] 순입니다. 냉각과 낮은 통증은 차별점이 아니라 빠지면 감점되는 기본입니다.
- **피부 반응은 다리에 몰립니다.** 불편 부위를 말한 47개 [m:f.pain_skin.discomfort_area.total] 중 다리 피부 반응이 19개 [m:f.pain_skin.discomfort_area.legs_reaction]로 가장 많고, 겨드랑이 통증 7개 [m:f.pain_skin.discomfort_area.underarm_pain], 비키니 통증 7개 [m:f.pain_skin.discomfort_area.bikini_intimate_pain]입니다. 오래 쓸수록 뜨거워진다는 리뷰도 4개 [m:std.pain_comfort.label.heats_up_with_use] 있어 넓은 부위 시술의 열 관리를 함께 봅니다.
- **문신과 점 위 사용.** 문신이나 점 위 피부 반응 5개 [m:f.pain_skin.discomfort_area.tattoo_or_spot_reaction], 통증 4개 [m:f.pain_skin.discomfort_area.tattoo_or_spot_pain]입니다. 사용 안내로 막을 수 있는 감점이라 설명서 앞쪽에 둡니다.
- **면도 준비가 제각각입니다.** 면도 방법을 말한 20개 [m:f.pain_skin.shaving_prep.total] 중 바로 전에 면도 4개 [m:f.pain_skin.shaving_prep.shaved_right_before], 전날 면도 4개 [m:f.pain_skin.shaving_prep.shaved_day_before], 털을 다 밀지 않음 3개 [m:f.pain_skin.shaving_prep.stubble_left]입니다. 리뷰어마다 다르게 하고 있어 설명서에 면도 시점을 하나로 정해 적을 필요가 있습니다.
- **털 고민이 큰 사용자.** 리뷰어 상태를 말한 44개 [m:f.pain_skin.user_condition.total] 중 PCOS, 호르몬 문제, 임신 뒤 털이 늘었다는 리뷰가 21개 [m:f.pain_skin.user_condition.hormonal], 인그로운 헤어나 면도 발진이 17개 [m:f.pain_skin.user_condition.ingrown_or_razor_bumps]입니다. 상세페이지가 말을 걸 사용자 설명에 반영합니다.
- **개발에 주는 의미.** 출력 단계는 부위마다 낮출 수 있게 하고(높은 단계가 세서 낮춰야 함 7개 [m:std.pain_comfort.label.high_setting_too_strong]), 냉각은 기본으로 넣으며, 설명서에 면도 시점과 문신, 점 회피를 그림으로 넣습니다.

> "냉각 기술 덕분에 사실상 아프지 않다" (Ulike, 4★, RPKW26NCED8Q8)
> "다리와 팔은 최고 출력도 문제없지만 더 민감한 부위는 6단계까지만 견딜 수 있다" (INNZA, 4★, R2Z9MITKBORPPL)
> "발목 문신 위에 썼다. 나쁜 생각이었다, 하지 마라. 부풀어 오르고 말 그대로 심하게 데었다." (INNZA, 4★, R2U724P47TBIDT)
> "쓰기 바로 전에 꼭 면도하세요. 면도하고 하루를 기다리면 털이 조금 자라기 시작해 IPL로 반응이 생길 수 있다." (PHILIPS, 5★, R2S5WD06YE4TMI)

### 집중 분석 3: 고장과 내구성, 발광과 센서에 몰린 고장
모든 리뷰를 다시 읽고 고장 난 부품, 고장까지 쓴 기간, 리뷰를 쓸 때까지 쓴 기간을 뽑았습니다.

- **발광과 센서.** 고장 부품을 말한 78개 [m:f.durability.failed_component.total] 중 켜지지만 발광하지 않음 29개 [m:f.durability.failed_component.no_flash], 피부 접촉 센서 18개 [m:f.durability.failed_component.skin_sensor], 전원이 켜지지 않음 9개 [m:f.durability.failed_component.no_power], 충전기나 배터리 7개 [m:f.durability.failed_component.power_supply]입니다. 램프와 발광 회로, 센서가 내구 시험의 첫 대상입니다.
- **고장 시기.** 고장까지 쓴 기간을 말한 46개 [m:f.durability.failure_time.n]의 중앙값은 6.5개월 [m:f.durability.failure_time.median]이고, 5개월 미만이 22개 [m:f.durability.failure_time.bin0], 5~15개월이 17개 [m:f.durability.failure_time.bin1]입니다. 보증 기간이 이 구간을 덮어야 감점이 줄어듭니다.
- **열과 탄 흔적.** 기기 과열 16개 [m:std.durability.label.overheating], 조사창 얼룩이나 탄내, 연기 17개 [m:std.durability.label.scorch_marks_smell], 가끔 발광 안 함이나 저절로 꺼짐 17개 [m:std.durability.label.intermittent_malfunction]입니다. 연속 사용 때의 열 관리와 조사창 재질이 설계 항목입니다.
- **리뷰는 대부분 초기 사용.** 쓴 기간을 말한 278개 [m:f.durability.use_duration.total] 중 4주 이상 3달 미만이 120개 [m:f.durability.use_duration.months_1_to_3], 4주 미만이 52개 [m:f.durability.use_duration.under_1_month]이고 1년 이상은 37개 [m:f.durability.use_duration.year_1_plus]입니다. 리뷰 표본은 초기 고장을 주로 보여 주고, 오래 쓴 뒤의 고장은 덜 잡힙니다.
- **개발에 주는 의미.** 경쟁사는 수명 발광 횟수를 숫자로 적습니다 [r:ind_05]. 우리는 발광 수명, 센서 내구, 과열 보호를 시험으로 확인하고 그 결과로 보증 기간을 정합니다. 받자마자 또는 한 달 안에 고장 24개 [m:std.durability.label.early_failure]를 막으려면 출고 전 발광 검사도 필요합니다.

> "40만 회에 한참 못 미쳐 발광이 멈췄다" (Braun, 1★, RSCSB7G8UO720)
> "갑자기 피부를 감지하지 못하고 발광하지 않는다." (Ulike, 3★, R38YNQA8ATNIF1)
> "귀를 찢는 듯한 쾅 소리가 난 뒤 기기에서 연기가 났다" (Ulike, 4★, R1XYM58U3K0JNP)
> "2년이 되자 작동을 멈췄다" (Braun, 3★, R3G3WO0OIHNYQG)

### 집중 분석 4: 시술 시간과 사용 편의, 넓은 부위의 긴 시간
모든 리뷰를 다시 읽고 한 번 시술 시간, 바라는 개선, 비교 대상을 뽑았습니다.

- **한 번 시술 시간.** 시간을 적은 30개 [m:f.time_use.session_minutes.n]의 중앙값은 30분 [m:f.time_use.session_minutes.median]이고, 60분 이상이 10개 [m:f.time_use.session_minutes.bin4], 5~15분이 9개 [m:f.time_use.session_minutes.bin1]입니다. 몇 부위만 하는 사람과 몸 전체를 하는 사람으로 갈리는 모습입니다(인용 참고). 리뷰어가 적은 값이라 측정값이 아닙니다.
- **시간 불만.** 한 번 시술이 오래 걸림 26개 [m:std.treatment_time.label.long_session], 일정이 부담 21개 [m:std.treatment_time.label.demanding_schedule], 넓은 부위가 오래 걸림 14개 [m:std.treatment_time.label.large_area_slow], 광고나 기대보다 오래 걸림 6개 [m:std.treatment_time.label.longer_than_expected]입니다. 광고한 시술 시간이 실제와 다르면 감점됩니다.
- **바라는 개선.** 바라는 점을 말한 26개 [m:f.time_use.desired_improvement.total] 중 보안경 8개 [m:f.time_use.desired_improvement.better_goggles], 더 큰 헤드 5개 [m:f.time_use.desired_improvement.larger_head], 자세한 사용 안내 4개 [m:f.time_use.desired_improvement.clearer_instructions], 더 빠른 발광 3개 [m:f.time_use.desired_improvement.faster_flash]입니다. 보안경 동봉, 넓은 부위용 큰 창, 부위별 순서 안내가 요청됩니다.
- **비교 대상은 살롱.** 비교 대상을 말한 115개 [m:f.time_use.comparison_reference.total] 중 살롱이나 클리닉의 전문 시술이 63개 [m:f.time_use.comparison_reference.professional_treatment]로 가장 많습니다. 비교 대상을 말한 리뷰어는 살롱이나 클리닉 시술과 견주는 경우가 가장 많습니다.
- **개발에 주는 의미.** 창 크기와 발광 간격을 정할 때 부위별 시술 시간을 함께 정하고, 자체 측정으로 확인한 시간만 상세페이지에 씁니다. 얼굴처럼 좁은 부위는 작은 헤드가 따로 필요합니다.

> "온몸(팔, 다리, 겨드랑이, 턱, 배꼽 아래 털, 비키니 부위)을 하는 데 두 시간이 걸린다" (Braun, 4★, R1NZEC16D5FOP4)
> "광고처럼 10분이 아니라 훨씬 오래 걸린다" (Ulike, 3★, R3DS39VF4SYRUU)
> "'여기서 시작해 이쪽으로 진행하라' 같은 글이나 다리 격자 같은 것이 있어 더 쉽게 할 수 있으면 좋겠다" (Braun, 3★, R25H686ZWIWEWC)
> "1년치 레이저 시술을 예약하는 것보다는 그래도 싸다!" (Braun, 4★, R3JL1X6MGXLUXX)

### 안전: 피부 반응 중심, 센서와 사용 경고로 줄일 수 있는 감점
안전 부정 리뷰 79개: 두통 1개(가중 0.0%), 피부 55개(가중 2.0%), 이상 반응 없음 23개 [m:p.safety_text]. 피부 안전 라벨로는 화상이나 물집 22개 [m:std.skin_safety.label.skin_burns], 발진이나 알레르기 반응 16개 [m:std.skin_safety.label.rash_bumps_allergy], 자극과 붉음 12개 [m:std.skin_safety.label.irritation_redness], 색소 변화나 흉터 12개 [m:std.skin_safety.label.pigment_scars], 눈부심이나 눈 안전 11개 [m:std.skin_safety.label.eye_flash_glare]입니다.

설계에서 막을 수 있는 것은 다음과 같습니다.

- **피부 접촉 센서와 색소 센서.** 피부 근접 센서와 색소 센서를 단 허가 사례가 있습니다 [r:tst_13]. 문헌 검토는 접촉 센서를 우회하지 말라는 경고를 포장에 분명히 적도록 권고합니다 [r:reg_21].
- **문신과 점.** 문신이나 점 위 피부 반응 5개 [m:f.pain_skin.discomfort_area.tattoo_or_spot_reaction]는 사용 안내로 막을 수 있습니다. 의료기기 표시에는 일반인이 안전하게 쓸 수 있는 사용 설명이 있어야 합니다 [r:reg_13].
- **눈.** 같은 검토는 가정용 기기 노출 뒤 보고된 눈 손상 사례를 찾지 못했지만 [r:reg_22], 눈부심 불만은 11개 [m:std.skin_safety.label.eye_flash_glare]이고 보안경을 바란다는 리뷰가 8개 [m:f.time_use.desired_improvement.better_goggles]입니다. 보안경을 상자에 넣고 눈 위험 경고와 보안경 착용을 포장에 적습니다 [r:reg_21].
- **광생물학적 안전 시험.** IPL은 FDA가 OHT에 연결한 인정 표준 IEC 62471 [r:tst_01]로 노출 한계와 위험군을 보고 [r:tst_02], 레이저로 가면 IEC 60825-1 [r:tst_08]을 따릅니다.

> "보안경을 써도 빛이 여전히 밝고, 쓰고 나면 가끔 두통이 생긴다" (Braun, 2★, R30MIFDD6J1ZO9)
> "실제로 다리를 데어 빨간 직사각형 자국이 생길 정도였다" (Braun, 4★, R2T2JDN7PVVK4G)
> "운 나쁘게도 빛 펄스에 일부 사람이 겪는 히스타민 반응이 생겼다" (Ulike, 4★, R33AU9CUYNIANU)

## 04 포지셔닝
포지션, 소비자 데이터에서 도출한 개발 기준, 실행 순서를 정리했습니다. 모든 기준값의 근거는 앞 장의 숫자입니다.

**TL;DR** 88.14~199.84 [m:m.price_band2_range] 가격대에서, 집에서 털을 줄이려는 미국 소비자에게 누구에게, 어느 부위에, 언제쯤 효과가 보이는지 먼저 밝히고 고장 없이 쓰게 만든 IPL을 냅니다. 제모 효과 7.2% [m:head.topic_neg]와 품질 6.2% [m:p.map.quality]가 근소한 1, 2위이고, 가격 대비 가치를 부정으로 말한 리뷰의 별점 격차가 -2.82 [m:p.gap3]로 크기 때문입니다. 편안함은 이미 경쟁사의 강점이라 기본으로 갖춥니다. 아래 가격과 SOM은 확인이 필요한 권고입니다.

### 한 줄 포지션
88.14~199.84 [m:m.price_band2_range] 가격대의 IPL로, 맞는 피부색과 털 색, 부위별 효과, 변화를 확인할 시점을 먼저 밝히고, 발광과 센서가 오래 버티며, 효과를 확인할 때까지 환불을 보장합니다.

### 이기는 이유: 기대 관리, 내구성, 보증
- **효과에 대한 기대를 먼저 맞춥니다.** 효과 없음이 161개 [m:std.efficacy.label.no_effect]이고, 얼굴은 효과 약함 35개 [m:f.efficacy.area_result.face_weak]가 효과 있음 31개 [m:f.efficacy.area_result.face_works]보다 많습니다. 경쟁사는 몇 주 만의 감소율을 앞에 내세웁니다 [r:ind_02] [r:ind_08]. 부위별 기대와 맞는 사용자를 먼저 밝히는 리스팅이 신뢰 격차 -2.83 [m:p.gap2]를 줄일 수 있다는 것이 가설입니다.
- **값이 크게 다른 두 상품 모두 고장이 약점입니다.** 값이 크게 다른 두 상품(Braun 377.16달러 [m:s.B07WYY6KKC.price], INNZA 90.42달러 [m:s.B0CWL9S4L1.price]) 모두 가장 큰 약점이 품질입니다(상품이 다섯 개라 값과의 관계는 판단할 수 없음). 발광하지 않음 29개 [m:f.durability.failed_component.no_flash], 센서 고장 18개 [m:f.durability.failed_component.skin_sensor]이고 고장까지 쓴 기간 중앙값은 6.5개월 [m:f.durability.failure_time.median]입니다. 새 브랜드는 처음부터 발광 회로와 센서의 내구 시험을 출시 기준으로 삼습니다.
- **보증으로 반품 감점을 없앱니다.** 반품 기한이 지나 감점한 리뷰가 17개 [m:std.returns_service.label.missed_return_window], 효과 확인 전에 기한이 끝났다는 리뷰가 4개 [m:std.returns_service.label.window_ends_before_results]입니다. 결과가 보였다고 말한 55개 [m:f.efficacy.time_to_results.total] 중 3달 이상 걸렸다는 리뷰는 2개 [m:f.efficacy.time_to_results.months_3_plus]뿐이라, 이 수 기준으로는 Braun의 100일 환불 보장 [r:ind_07] 기간 안에 대부분 들어옵니다. 효과를 보지 못한 리뷰는 이 수에 없어, 그 사용자들이 100일 안에 효과 없음을 확인할 수 있는지는 알 수 없습니다. 보증 기간은 가설입니다. 아마존에서 산 사람에게도 같은 보증을 적용합니다.

> "90일 보장인 줄 알았는데 제품 웹사이트에서 샀을 때만 그렇다고 해서, 반품 기한을 넘긴 게 정말 짜증 난다" (Ulike, 2★, R3TBTATZWLRUQN)

### 소비자 기준표
각 기준은 감점 기준, 만족 기준, 개발 기준, 상세페이지 문구 순서로 정리했습니다. 상세페이지 문구는 실제로 쓸 영어 그대로 적었습니다. 부정이 가장 적은 상품 값 가운데 PHILIPS와 Ulike Air 10 Deluxe는 부정 표본이 매우 적은 리스팅이라 약한 기준으로 읽습니다.

#### 기준 1: 제모 효과
- 감점 기준: 부정 268개 [m:std.efficacy.neg], 가중 11.0% [m:std.efficacy.neg_pct]. 효과 없음 161개 [m:std.efficacy.label.no_effect], 줄었지만 다 없어지지 않음 41개 [m:std.efficacy.label.partial_reduction], 부위마다 효과 차이 36개 [m:std.efficacy.label.uneven_by_area]가 가장 많습니다. 얼굴은 효과 약함 35개 [m:f.efficacy.area_result.face_weak]로 감점이 가장 큰 부위입니다.
- 만족 기준: 만족 리뷰 432개 [m:std.efficacy.pos]. 부정이 가장 적은 상품은 PHILIPS 5.1% [m:std.efficacy.best]입니다(부정 표본이 적음). 결과 시점을 말한 리뷰 가운데 1~3회 쓰고 변화가 보였다는 리뷰가 24개 [m:f.efficacy.time_to_results.sessions_1_to_3]로 가장 많아, 몇 번 안에 보이는 변화가 만족의 기준입니다.
- 개발 기준: 허가 문구에서 영구 털 감소는 시술을 마친 뒤 일정 기간에 걸쳐 다시 나는 털 수가 오래 안정적으로 줄어든 것으로 정의됩니다 [r:reg_04]. 효과 숫자를 주장하려면 무작위 대조 인체 임상시험 수준의 근거가 필요합니다 [r:reg_16]. 경쟁사 Ulike의 허가는 벤치 시험만으로 이뤄졌다고 정리돼 있어 [r:tst_10] 허가만으로 효과 숫자의 근거가 생기지는 않습니다. 부위별 효과 시험 방법과 목표 감소율은 확인 필요(조사 근거 없음). 숫자 목표를 정하더라도 출발점일 뿐이며 시험으로 확정합니다.
- 상세페이지 문구: "Results vary by body area, hair color, and skin tone. Check the chart below to see if this device is right for you." (털 감소율 숫자와 permanent는 우리 임상 근거와 허가 문구가 생긴 뒤에만 쓴다 [r:reg_04] [r:reg_16])

> "굵고 검은 털이라면 이 기기는 시간과 돈을 쓸 만하다. 가늘고 면도하기 쉬워 별 문제 없는 털이라면 굳이 살 필요 없다." (INNZA, 4★, R1JLZT6OS3U6JO)

#### 기준 2: 통증과 냉각
- 감점 기준: 부정 64개 [m:std.pain_comfort.neg], 가중 4.0% [m:std.pain_comfort.neg_pct]. 약간 따끔함 15개 [m:std.pain_comfort.label.mild_sting], 민감한 부위 통증 14개 [m:std.pain_comfort.label.sensitive_area_pain], 쏠 때 뜨겁거나 타는 느낌 11개 [m:std.pain_comfort.label.hot_burning_sensation]입니다. 냉각이 약하다는 불만도 6개 [m:std.pain_comfort.label.cooling_insufficient] 있습니다.
- 만족 기준: 만족 리뷰 186개 [m:std.pain_comfort.pos]. 부정이 가장 적은 상품은 Ulike 0.0% [m:std.pain_comfort.best](Air 10 Deluxe 리스팅, 부정 표본이 적음)입니다. 편안함 180개 대 아픔 40개(4.50배) [m:head.dir_ratio]로, 냉각 덕분에 거의 아프지 않다는 수준이 만족선입니다.
- 개발 기준: 냉각을 내세우는 업계 사례가 있고 [r:ind_23], 출력을 10단계로 나눈 사례가 있습니다 [r:ind_06]. 높은 단계가 세서 낮춰야 한다는 리뷰 7개 [m:std.pain_comfort.label.high_setting_too_strong]가 있어 부위마다 낮출 수 있게 합니다. 냉각면 온도와 단계별 통증 목표는 확인 필요(조사 근거 없음). 정하는 값은 출발점이며 시험으로 확정합니다.
- 상세페이지 문구: "Built-in cooling and adjustable levels, so you can go lower on sensitive areas."

#### 기준 3: 피부 안전
- 감점 기준: 부정 74개 [m:std.skin_safety.neg], 가중 3.9% [m:std.skin_safety.neg_pct]. 화상이나 물집 22개 [m:std.skin_safety.label.skin_burns], 발진이나 알레르기 반응 16개 [m:std.skin_safety.label.rash_bumps_allergy], 색소 변화나 흉터 12개 [m:std.skin_safety.label.pigment_scars]가 가장 많고, 문신이나 점 위 반응 5개 [m:f.pain_skin.discomfort_area.tattoo_or_spot_reaction]도 있습니다.
- 만족 기준: 만족 리뷰 29개 [m:std.skin_safety.pos]. 부정이 가장 적은 상품은 PHILIPS 1.2% [m:std.skin_safety.best]입니다(부정 표본이 적음). 자극이 없었다는 말, 피부에 다 닿을 때만 발광해 안심된다는 말이 만족의 내용입니다.
- 개발 기준: IPL은 IEC 62471로 광생물학적 안전을 보고 [r:tst_01] [r:tst_02], 비레이저 광원 의료기기 안전 표준 IEC 60601-2-57 [r:tst_03]을 다른 OTC IPL 허가가 시험 표준으로 적었습니다 [r:tst_11]. 가정 의료 환경에는 IEC 60601-1-11이 적용됩니다 [r:tst_06]. 피부 근접 센서와 색소 센서를 다는 사례가 있고 [r:tst_13], 포장에는 눈 위험, 보안경, 센서 우회 금지 경고를 적습니다 [r:reg_21]. 레이저로 가면 IEC 60825-1 [r:tst_08]을 따르고, 4등급 레이저 제품이면 눈과 피부 노출 경고 문구 [r:reg_11]를 붙입니다. 우리 제품의 레이저 등급은 확인 필요(조사 근거 없음). 화상률 같은 합격 기준 값은 확인 필요(조사 근거 없음).
- 상세페이지 문구: "Never use over tattoos, moles, or dark spots. Eye protection is in the box. Wear it every session."

#### 기준 4: 내구성
- 감점 기준: 부정 154개 [m:std.durability.neg], 가중 6.5% [m:std.durability.neg_pct]. 몇 달 쓴 뒤 고장 35개 [m:std.durability.label.failed_after_months], 시기 언급 없는 고장 30개 [m:std.durability.label.failure_unspecified], 받자마자 또는 한 달 안에 고장 24개 [m:std.durability.label.early_failure]입니다. 부품으로는 발광하지 않음 29개 [m:f.durability.failed_component.no_flash], 센서 18개 [m:f.durability.failed_component.skin_sensor]이고 고장까지 쓴 기간 중앙값은 6.5개월 [m:f.durability.failure_time.median]입니다.
- 만족 기준: 만족 리뷰 64개 [m:std.durability.pos]. 부정이 가장 적은 상품은 PHILIPS 0.9% [m:std.durability.best]입니다(부정 표본이 적음). 튼튼하고 잘 만들었다는 말이 만족의 내용입니다.
- 개발 기준: 경쟁사는 수명 발광 횟수를 권장 일정 기준으로 적고 [r:ind_05], 제품 등록 시 5년 보증을 주기도 합니다 [r:ind_11]. 가정용 미용 광원 기기 안전 표준 IEC 60335-2-113은 털 성장 억제 기기를 포함합니다 [r:tst_04]. 무선이면 리튬 전지가 UN 38.3 시험을 통과해야 합니다 [r:reg_20]. 발광 수명과 센서 내구 시험의 표준과 합격 기준은 확인 필요(조사 근거 없음). 리뷰가 말한 고장 중앙값 6.5개월 [m:f.durability.failure_time.median]은 넘어야 할 최소선이고, 목표는 시험으로 다시 정합니다.
- 상세페이지 문구: "Backed by a (warranty period) warranty. Lamp tested to (flash count) flashes in our lab." (보증 기간과 발광 수명은 내구 시험 결과로 채운다)

> "40만 회에 한참 못 미쳐 발광이 멈췄다" (Braun, 1★, RSCSB7G8UO720)

#### 기준 5: 시술 시간과 일정
- 감점 기준: 부정 79개 [m:std.treatment_time.neg], 가중 3.1% [m:std.treatment_time.neg_pct]. 한 번 시술이 오래 걸림 26개 [m:std.treatment_time.label.long_session], 일정이 부담 21개 [m:std.treatment_time.label.demanding_schedule], 넓은 부위가 오래 걸림 14개 [m:std.treatment_time.label.large_area_slow], 발광 간격이 김 9개 [m:std.treatment_time.label.slow_flash]입니다. 말한 시술 시간 중앙값은 30분 [m:f.time_use.session_minutes.median]입니다.
- 만족 기준: 만족 리뷰 42개 [m:std.treatment_time.pos]. 부정이 가장 적은 상품은 PHILIPS 1.3% [m:std.treatment_time.best]입니다(부정 표본이 적음). 두 겨드랑이를 몇 분에 끝낸다는 말, 일주일에 잠깐만 쓴다는 말이 만족선입니다.
- 개발 기준: IEC 60335-2-113은 발광 면적 25cm² 미만 기기를 다루므로 [r:tst_05], 창 크기를 정할 때 적용 표준을 함께 확인합니다. 넓은 부위용 큰 창을 바라는 리뷰 5개 [m:f.time_use.desired_improvement.larger_head]가 있습니다. 발광 간격과 부위별 목표 시간은 확인 필요(조사 근거 없음). 정하는 값은 출발점이며 자체 측정으로 확정합니다.
- 상세페이지 문구: "Time per area, measured in our own tests: underarms (minutes), lower legs (minutes)." (부위별 시간은 자체 측정 뒤에만 채운다. 광고보다 오래 걸린다는 불만이 있으므로 가장 짧은 값이 아니라 보통 값을 쓴다)

#### 기준 6: 피부색과 털 색 적합성
- 감점 기준: 부정 58개 [m:std.suitability.neg], 가중 2.7% [m:std.suitability.neg_pct]. 어두운 피부색에는 못 씀 21개 [m:std.suitability.label.dark_skin_tone], 금발이나 옅은 털 13개 [m:std.suitability.label.light_fine_hair], 굵고 억센 털 13개 [m:std.suitability.label.thick_coarse_hair], 어두운 부위 9개 [m:std.suitability.label.dark_body_areas], 흰 털이나 회색 털 6개 [m:std.suitability.label.gray_white_hair]입니다. 신뢰 격차 -2.83 [m:p.gap2]에는 어두운 피부에도 된다고 광고했다는 불만이 들어 있습니다.
- 만족 기준: 이 기준의 만족 리뷰는 0개 [m:std.suitability.pos]이고, 부정이 가장 적은 상품은 Ulike 0.7% [m:std.suitability.best](Air 10 Deluxe 리스팅)입니다. 칭찬받는 항목이 아니라 감점을 피하는 항목입니다. 피부색을 말한 리뷰어 중 갈색이나 어두운 피부는 6개 [m:f.efficacy.reviewer_skin_tone.dark]뿐이라 이 사용자들의 경험은 이번 표본으로 알기 어렵습니다.
- 개발 기준: 허가된 피부 유형은 브랜드마다 다릅니다. Ulike K223618은 Fitzpatrick I~V [r:reg_05], Cosbeauty는 I~IV [r:reg_06], Braun은 I~V에만 쓰도록 합니다 [r:ind_09]. 털 색은 아주 옅은 금발, 붉은 털, 회색이나 흰 털에 맞지 않는다고 적는 사례가 있습니다 [r:ind_10] [r:ind_21]. 어두운 피부색은 1064nm 레이저를 따로 두는 사례가 있습니다 [r:ind_18]. 색소 센서를 달고 [r:tst_13], 라벨 이해와 자가 선택 시험(허가 사례에서 참가자 전원 정답)을 거칩니다 [r:tst_12]. 우리 허가 범위는 확인 필요(조사 근거 없음).
- 상세페이지 문구: "For Fitzpatrick skin types (cleared range). Not for white, gray, red, or light blonde hair. Not sure? Use the skin tone chart before you buy." (범위는 우리 510(k) 허가 문구로 채운다 [r:reg_05] [r:reg_06])

> "흑인이나 피부색이 어두운 사람에게는 맞지 않는다고 한 번도 말하지 않았다" (Ulike, 1★, RL4CIP8VWPLYA)

#### 기준 7: 반품과 고객 응대
- 감점 기준: 부정 48개 [m:std.returns_service.neg], 가중 1.7% [m:std.returns_service.neg_pct]. 반품 기한이 지나 반품이나 환불 불가 17개 [m:std.returns_service.label.missed_return_window], 고객센터 무응답 13개 [m:std.returns_service.label.no_response], 환불이나 교체, 수리 거절 8개 [m:std.returns_service.label.refund_replace_refused], 효과 확인 전 기한 종료 4개 [m:std.returns_service.label.window_ends_before_results]입니다. 브랜드 경험 부정 리뷰의 평균 별점은 1.48★ [m:p.gap1_neg]까지 떨어집니다.
- 만족 기준: 만족 리뷰 20개 [m:std.returns_service.pos]. 부정이 가장 적은 상품은 PHILIPS 0.0% [m:std.returns_service.best]입니다(부정 표본이 적음). 기한이 지났는데도 회사가 먼저 연락해 환불해 줬다는 말이 만족의 수준입니다.
- 개발 기준: 업계는 100일 환불 보장 [r:ind_07]과 등록 시 5년 보증 [r:ind_11]을 씁니다. 결과가 보인 시점을 말한 리뷰 가운데 3달 이상 걸렸다는 리뷰는 2개 [m:f.efficacy.time_to_results.months_3_plus]라, 보증 기간은 이 확인 기간을 덮도록 정합니다. 아마존 반품 정책과 우리 보증의 관계, 응답 시간 목표는 확인 필요(조사 근거 없음).
- 상세페이지 문구: "(guarantee period)-day money-back guarantee, whether you buy on Amazon or from our site. Real people answer within (response time)."

> "100일이 지났는데도 회사가 먼저 연락해 전액 환불을 제안했다" (Ulike, 3★, R1SDYJMPTO5X2D)
> "반품 기간은 4주뿐인데 효과는 4주는 지나야 보인다고 적혀 있다" (Ulike, 2★, R3I8VU9TXZJ1N2)

### 하위 카테고리별 출시 계획: IPL 본체 먼저, 레이저는 후순위
확인이 필요한 권고입니다.

- **첫째, Light Hair Removal Devices의 IPL 본체.** 점수표 다섯 상품이 모두 이 노드에 있어 리뷰 근거가 가장 많습니다. 상위 10개 합이 96.2% [m:m.top10_share_IPL]로 몰려 있으므로 가격대, 적합성 안내, 보증으로 자리를 만듭니다.
- **둘째, 얼굴용 정밀 헤드 구성.** 얼굴은 효과 약함 35개 [m:f.efficacy.area_result.face_weak]가 효과 있음 31개 [m:f.efficacy.area_result.face_works]보다 많은 부위이고, 호르몬 문제로 털이 늘었다는 리뷰어가 21개 [m:f.pain_skin.user_condition.hormonal]입니다. 여성 검색어 상위에도 얼굴 검색어가 있습니다. 시제품으로 얼굴 효과를 먼저 확인한 뒤에만 냅니다.
- **후순위, 다이오드 레이저(어두운 피부용 포함).** 어두운 피부색에 못 쓴다는 불만이 21개 [m:std.suitability.label.dark_skin_tone]이고 어두운 피부색용 1064nm 레이저를 따로 두는 사례가 있습니다 [r:ind_18]. 다만 피부색을 말한 리뷰어 가운데 어두운 피부는 6개 [m:f.efficacy.reviewer_skin_tone.dark]뿐이라 리뷰 근거가 약하고, 레이저 제품은 레이저 안전 표준 [r:tst_08]을 따라야 하며 4등급 레이저 제품이면 눈과 피부 노출 경고 문구 [r:reg_11]도 붙여야 합니다(우리 제품의 레이저 등급은 확인 필요, 조사 근거 없음). 상위 노드의 브랜드 표도 Braun 97.4% [m:m.top1_LLE]입니다.
- **따로 내지 않음(확인이 필요한 권고), 남성용.** 성별 검색어 표(시장 데이터 관련 검색어) 안에서 남성 검색어가 0개 [m:m.terms_male_n]라 남성용을 따로 내지 않고 본체 리스팅 안에서 다룹니다. 다만 성장 표에 nads hair removal for men(제모 크림 브랜드 검색어로 보임)이 있어 남성 검색이 없다는 뜻은 아니므로, 기기를 찾는 남성 검색 수요는 따로 확인합니다.

### 가격 구조: Ulike와 Braun 아래, INNZA 위
확인이 필요한 권고입니다.

- **본체는 둘째 가격 구간 안.** 88.14~199.84 [m:m.price_band2_range] 구간은 매출 비중 22.4% [m:m.price_band2_share]에 평균 별점 4.28★ [m:m.price_band2_rating]로 세 구간 중 별점이 가장 높습니다. 207.96~572.23 [m:m.price_band3_range] 구간은 76.5% [m:m.price_band3_share]로 가장 크지만 4.01★ [m:m.price_band3_rating]입니다.
- **경쟁 기준선.** 아래에 INNZA 90.42달러 [m:s.B0CWL9S4L1.price], 위에 Ulike Air 10 349.00달러 [m:s.B0CV3ZJ2PN.price]와 Braun 377.16달러 [m:s.B07WYY6KKC.price]가 있습니다. 공식몰 기준으로 Nood The Flasher 2.0과 SmoothSkin Pure Fit이 199달러 [r:ind_14] [r:ind_20], wavytalk Bare It이 216달러 [r:ind_22], Ulike Air 4가 259달러 [r:ind_03]입니다.
- **값만 낮춰서는 가치 불만이 남습니다.** 가격 대비 가치 부정 리뷰의 평균 별점은 1.68★ [m:p.gap3_neg]이고, 비싸다는 말과 함께 효과 없이 시간과 돈을 버렸다는 말이 있습니다. 가치 불만을 줄이는 것은 값과 함께 효과 기대와 보증이라는 것이 가설입니다.
- **보증을 가격의 일부로.** 환불 기간과 보증 기간을 가격과 함께 설계합니다 [r:ind_07] [r:ind_11]. 구체 가격과 마진은 원가와 광고비가 정해진 뒤 정합니다: UNVERIFIED.

### 메시지와 키워드: 맞는 사람, 보이는 시점, 연락되는 브랜드
- **메시지 하나: 맞는 사람을 먼저 밝힙니다.** 어두운 피부색 불만 21개 [m:std.suitability.label.dark_skin_tone], 금발이나 옅은 털 불만 13개 [m:std.suitability.label.light_fine_hair]. 상세페이지 첫 이미지들 가운데 하나에 피부색과 털 색 표를 둡니다.
- **메시지 둘: 부위별로, 언제쯤.** 얼굴 효과 약함 35개 [m:f.efficacy.area_result.face_weak], 효과 확인 전 반품 기한 종료 4개 [m:std.returns_service.label.window_ends_before_results]. 부위별 기대와 변화를 확인할 시점을 그림으로 보여 줍니다.
- **메시지 셋: 고장 없이, 연락되는 브랜드.** 발광하지 않음 29개 [m:f.durability.failed_component.no_flash], 고객센터 무응답 13개 [m:std.returns_service.label.no_response]. 보증 기간과 연락 방법을 앞에 둡니다.
- **키워드.** 공통 검색어 40개 [m:m.terms_common_n]의 합 1,051,188 [m:m.terms_common_volume]과 여성 검색어 10개 [m:m.terms_female_n]의 합 355,407 [m:m.terms_female_volume]은 검색어 수가 달라 낱말 순서의 근거가 되지 않습니다. 제목에는 ipl laser hair removal, hair removal device 같은 일반 검색어를 쓰고, 여성용 문구는 laser hair removal for women을 참고합니다. IPL 기기 제목에 laser를 써도 되는지는 확인 필요(조사 근거 없음). 피부색과 털 색 낱말의 검색량은 확인하지 않았습니다.

### 실행 순서: 해결하는 문제의 크기 순
- **시장 숫자의 단위 확인.** 월 매출 칸과 점유율 칸의 단위를 먼저 확인하고, 확인되면 SOM과 가격을 다시 잡습니다.
- **제모 효과와 기대 관리**: 부정 언급 리뷰어 7.2% [m:p.map.hair_reduction]. 부위별(특히 얼굴) 시제품 효과 확인, 적합성 표와 변화 확인 시점 안내.
- **품질과 내구성**: 6.2% [m:p.map.quality]. 발광, 센서, 과열 시험과 출고 전 발광 검사.
- **가격 대비 가치**: 5.3% [m:p.map.price_value]. 둘째 가격 구간 안의 가격과 보증 설계.
- **안전**: 3.1% [m:p.map.safety]. 접촉 센서, 색소 센서, 보안경, 문신과 점 경고.
- **시술 시간**: 2.7% [m:p.map.treatment_time]. 창 크기, 발광 간격, 부위별 시간 측정.
- **피부색과 털 색 적합성**: 2.5% [m:p.map.skin_hair_suitability]. 허가 범위와 자가 선택 시험.
- **고객 응대**: 1.7% [m:p.map.customer_service]. 빈도는 낮지만 브랜드 경험 격차 -2.92 [m:p.gap1]가 커서 출시 전에 보증과 응대 체계를 정합니다.
- **통증과 냉각**: 1.4% [m:p.map.pain_comfort]. 경쟁사 수준을 유지하는 기본 항목입니다.
- **출시 뒤 대조.** 리뷰를 기준표의 감점 기준과 대조합니다.

### 개발 단계와 관문: 단계 A~F
- **단계 A, 광원과 창.** IPL 광원, 창 크기, 출력 단계, 냉각을 정합니다. 관문: IEC 62471 광생물학적 안전 [r:tst_01] [r:tst_02], 창 크기에 따른 IEC 60335-2-113 범위 확인 [r:tst_05]. 부위별 효과(얼굴 포함) 시제품 확인의 방법과 기준은 확인 필요(조사 근거 없음).
- **단계 B, 센서와 사용 안내.** 피부 접촉 센서와 색소 센서 [r:tst_13], 센서 우회 금지와 눈 위험 경고 [r:reg_21], 일반인용 사용 설명 [r:reg_13]. 관문: 라벨 이해와 자가 선택 시험 [r:tst_12].
- **단계 C, 내구.** 발광 회로, 램프, 센서, 과열 보호. 관문: 내구 시험 표준과 합격 기준은 확인 필요(조사 근거 없음). 리뷰가 말한 고장까지 쓴 기간 중앙값 6.5개월 [m:f.durability.failure_time.median]은 최소선이고 목표는 시험으로 다시 정합니다.
- **단계 D, 규제와 허가.** 관문: OHT, Class II, 510(k) [r:reg_01] [r:reg_02], IEC 60601-2-57 [r:tst_03] [r:tst_11], 가정 환경 IEC 60601-1-11 [r:tst_06], 라벨의 UDI [r:reg_15], 무선이면 UN 38.3 [r:reg_20]. 레이저로 가면 IEC 60825-1 [r:tst_08], 4등급 레이저 제품이면 눈과 피부 노출 경고 문구 [r:reg_11](우리 제품의 레이저 등급은 확인 필요, 조사 근거 없음).
- **단계 E, 상세페이지와 주장.** 관문: 모든 효과 주장에 근거 [r:reg_16] [r:reg_17], permanent는 허가 문구의 정의 안에서만 [r:reg_04], 시술 시간은 자체 측정값만.
- **단계 F, 출시와 보증.** 관문: 아마존 구매를 포함한 환불과 보증 기간 확정, 고객 응대 체계. 출시 뒤 제모 효과를 부정으로 언급한 리뷰어 비율(가중)을 이번 표본의 7.2% [m:head.topic_neg]와 참고로 대조합니다.

## 05 한 장 요약
제품 자체에 대한 결정과, 이를 출시까지 가져갈 단계 계획입니다.

### 제품 해부도
1. **조사창과 헤드**: 넓은 부위용 큰 창과 얼굴용 작은 헤드 (넓은 부위가 오래 걸림 14개 [m:std.treatment_time.label.large_area_slow], 더 큰 헤드 바람 5개 [m:f.time_use.desired_improvement.larger_head], 창 크기에 따른 표준 범위 [r:tst_05])
2. **광원과 출력 단계**: 부위마다 낮출 수 있는 단계, 낮게 시작하는 안내 (높은 단계가 세서 낮춰야 함 7개 [m:std.pain_comfort.label.high_setting_too_strong], 민감한 부위 통증 14개 [m:std.pain_comfort.label.sensitive_area_pain])
3. **냉각면**: 기본 탑재, 오래 써도 뜨거워지지 않게 (편안함 180개 대 아픔 40개(4.50배) [m:head.dir_ratio], 오래 쓸수록 뜨거워짐 4개 [m:std.pain_comfort.label.heats_up_with_use])
4. **피부 접촉 센서**: 붙이면 확실히 발광하고 떼면 멈춤 (센서 고장 18개 [m:f.durability.failed_component.skin_sensor], 센서 우회 금지 경고 [r:reg_21])
5. **색소 센서와 적합성 표**: 맞지 않는 피부색에서 발광 차단, 상자와 상세페이지에 같은 표 (어두운 피부색 불만 21개 [m:std.suitability.label.dark_skin_tone], 색소 센서 사례 [r:tst_13])
6. **발광 회로와 램프**: 수명 시험으로 보증 기간을 정함 (발광하지 않음 29개 [m:f.durability.failed_component.no_flash], 고장까지 중앙값 6.5개월 [m:f.durability.failure_time.median])
7. **본체 열 관리와 전원**: 과열 보호, 조사창 얼룩 방지, 전원 방식 결정 (과열 16개 [m:std.durability.label.overheating], 얼룩이나 탄내 17개 [m:std.durability.label.scorch_marks_smell], 충전기나 배터리 7개 [m:f.durability.failed_component.power_supply])
8. **상자 구성과 설명서**: 보안경 동봉, 부위별 순서와 면도 시점, 문신과 점 경고 (보안경 바람 8개 [m:f.time_use.desired_improvement.better_goggles], 눈부심 11개 [m:std.skin_safety.label.eye_flash_glare], 문신이나 점 반응 5개 [m:f.pain_skin.discomfort_area.tattoo_or_spot_reaction])

센서는 너무 둔해도, 너무 예민해도 감점됩니다. 밝은 피부에서 센서가 출력을 지나치게 낮춘다는 요청도 있으므로 센서 기준은 시험으로 정합니다.

> "피부가 흰 사용자를 위해 피부 센서를 끄거나 민감도를 조절하는 옵션을 넣어 달라" (Ulike, 3★, RRHU7A16IHWSW)
> "보안경이나 가리개 같은 것을 함께 줬으면 정말 좋겠다" (Braun, 4★, R2QV46JTGZRGAW)

### 단계와 관문
- **광원과 창**: IEC 62471 [r:tst_01], 창 크기와 표준 범위 [r:tst_05], 부위별 효과 확인(방법 확인 필요).
- **센서와 안내**: 라벨 이해와 자가 선택 시험 [r:tst_12], 포장 경고 [r:reg_21].
- **내구**: 발광, 센서, 과열 시험(표준 확인 필요). 고장 중앙값 6.5개월 [m:f.durability.failure_time.median]이 최소선.
- **규제와 허가**: OHT 510(k) [r:reg_01] [r:reg_02], IEC 60601-2-57 [r:tst_03], UDI [r:reg_15].
- **상세페이지와 주장**: 근거 있는 주장만 [r:reg_16], permanent는 허가 정의 안에서만 [r:reg_04].
- **출시와 보증**: 아마존 구매 포함 보증 확정, 출시 뒤 7.2% [m:head.topic_neg]와 참고 대조.

## A 데이터와 방법
이 가이드의 모든 숫자는 아래 자료에 근거합니다.

### 출처
- **리뷰**: 공유 리뷰 DB에서 받은 아마존 미국 리뷰(점수표의 다섯 상품). 주제와 감성 태그, 세부 이슈 라벨, 설계 정보 항목(효과를 본 부위, 결과가 보인 시점, 털 색과 피부색, 사용 빈도, 출력 단계, 불편 부위, 면도 준비, 리뷰어 상태, 고장 부품, 고장까지 쓴 기간, 쓴 기간, 한 번 시술 시간, 바라는 개선, 비교 대상)을 붙였습니다. 파일과 개수는 아래 표에 있습니다.
- **시장 데이터**: spd-amz-market(하위 카테고리, 브랜드 점유율, 검색어, 주간 검색량 이력). 매출, 점유율, 증감 칸은 단위 미확인입니다.
- **웹 조사**: 다시 열어 원문 문장을 확인한 주장만 썼습니다. 열리지 않거나 원문 문장이 없어 확인되지 않은 주장(FDA 레이저 제품 안내 페이지, FDA Laser Notice, FDA 일반 표시 요건 페이지, Philips와 Tria의 효과와 허가 문구 주장, Market Intelo의 세계 규모와 제모 용도 비중 등)은 쓰지 않았습니다.
- **상품 사양**: 이번 회차는 상품 사양 표를 설정하지 않았습니다. 사양은 확인된 웹 조사 주장으로만 적었습니다.
- **방법**: 비율은 별점 묶음(부정, 중립, 긍정) 가중으로 표본 편향을 되돌린 값입니다. 원본 수는 어떤 불만이 있는지로, 가중 비율은 그 불만이 얼마나 흔한지로 읽습니다. 통증 방향 지수는 (아픔 − 편안함) ÷ (아픔 + 편안함)이고 방향 언급이 기준 수 이상인 상품만 냈습니다. 시술 시간 중앙값은 값이 기준 수 이상인 상품만 냈습니다. 별점 격차는 그 주제 부정 리뷰와 나머지 리뷰의 가중 평균 별점 차이입니다. 효과 없음 비율은 그 설계 정보 값을 말한 리뷰 가운데 효과 없음 라벨이 함께 붙은 리뷰의 비율입니다.

### 견고성 점검: 제모 효과 1위는 대체로 유지, 품질과 차이는 작음
상품을 하나씩 빼고 다시 계산하면 뒤집힘 표시가 5번 중 5번 [m:a.robust.loo_flips] 붙었습니다. 모두 최대 약점 상품이 과반이 아니라는 표시이고, 이는 상품을 빼지 않은 전체 계산에서도 같습니다. INNZA를 빼면 불만 지도 2위와 3위가 바뀌어 가격 대비 가치가 2위가 됩니다.
상품을 하나씩 뺄 때 머리 숫자 2는 6.5%~8.0% [m:a.robust.loo_head_neg], 통증 방향 가운데 편안함 쪽 비율은 76.1%~87.8% [m:a.robust.loo_low_share] 안에 있었습니다.
리뷰를 2,000번 [m:a.robust.n] 다시 뽑으면 제모 효과가 불만 1위로 남은 비율은 81.7% [m:a.robust.head_first], 머리 숫자 2의 구간은 5.9%~8.8% [m:a.robust.head_neg_ci]입니다. 최대 약점 상품 수의 분포는 1개 5.5%, 2개 52.8%, 3개 36.3%, 4개 5.4% [m:a.robust.weakest_dist]입니다.
이 점검은 고른 상품 안의 표본 흔들림만 재며, 어떤 상품을 골랐는지에 따른 치우침은 재지 못합니다.

### 주의 사항
- 리뷰는 공유 리뷰 DB 표본이라 낮은 별점이 실제보다 많습니다(표본 평균 별점이 가중 평균보다 낮음, 숫자는 페이지 끝 한계 목록). 비율은 별점 묶음 가중으로 되돌렸습니다.
- 자유 서술에서 뽑은 수치(한 번 시술 시간, 고장까지 쓴 기간 등)는 리뷰어가 적은 값이라 측정값이 아닙니다. 방향과 분포로만 읽습니다.
- 개발 기준의 사양 숫자는 웹 조사 출처를 근거로 한 시작점이고 시험으로 확인해야 합니다.
- 상품이 다섯 개이고 모두 한 하위 카테고리(Light Hair Removal Devices)라 상품끼리, 하위 카테고리끼리의 비교가 약합니다.
- 시장 데이터(spd-amz-market)의 매출, 점유율, 증감, 승률 칸은 문서에 단위가 없어 단위 미확인으로 적었습니다. 연 환산 값은 월 매출 칸을 달러로 가정한 것입니다.
- ASIN은 매출 순위가 아니라 공유 DB에 리뷰가 많은 후보 가운데 고른 것입니다(상품 확인 관문에서 사람이 확인).
- 머리 숫자 5번(성장 배수)은 30일 검색량 기준을 넘는 카테고리 검색어 49개 [m:m.growth_candidates] 중 2년 주간 이력을 받은 20개 [m:m.growth_ranked]에서 골랐고, 나머지는 이력이 없어 순위에서 빠졌습니다. 시장 데이터의 yoYChangePct 칸은 뜻과 단위가 확인되지 않아 머리 숫자에 쓰지 않습니다.
- 무료 공유 DB에 있는 IPL, 레이저 제모기 다섯 종을 모두 썼습니다. Ulike Air 10과 Air 10 Deluxe는 같은 모델의 두 리스팅이라 Ulike가 두 번 들어갑니다. PHILIPS는 부정 표본이 하나, Ulike Deluxe는 중립 표본이 없어, 이 두 상품이 부정이 가장 적은 상품으로 잡힌 기준은 약합니다.
- 쓴 기간을 말한 리뷰는 4주 이상 3달 미만이 120개 [m:f.durability.use_duration.months_1_to_3]로 가장 많아, 오래 쓴 뒤의 고장과 효과 지속은 덜 잡힙니다.
- 미국 가정용 IPL, 레이저 제모기만의 시장 규모는 찾지 못했습니다. 확인된 값은 세계, 북미, 미국 가정용 뷰티 기기 전체, 미국 면도와 제모 시장 전체 값뿐이고, 세계 가정용 IPL 규모는 QYResearch와 Spherical Insights가 서로 다릅니다 [r:mkt_03] [r:mkt_04]. TAM은 범위로만 읽습니다.
- FDA 허가 문구는 영구 털 감소(permanent reduction)이고 permanent hair removal은 허가 문구가 아닙니다 [r:reg_04]. 허가된 피부 유형은 브랜드마다 다릅니다 [r:reg_05] [r:reg_06] [r:ind_09].
- 510(k) 요약 일부는 제3자 정리 사이트(Innolitics)의 문장으로 확인했고 FDA 원문 PDF와는 대조하지 못했습니다 [r:tst_10].
- 이번 회차에는 상품 사양 표, 소비자 설문, 사용 시험 자료가 없습니다.
- 별점 격차와 설계 정보의 함께 나옴(예: 밝은 피부와 효과 없음, 잦은 사용과 효과 없음)은 원인 관계가 아닙니다.
- 아직 찾지 못한 것: 부위별 효과 시험 방법과 목표, 발광 수명과 센서 내구 시험의 표준과 합격 기준, 냉각면 온도 기준, 아마존 반품 정책과 보증의 관계, IPL 기기에 laser를 쓰는 표기 기준, 우리 제품의 허가 경로와 피부 유형 범위. 해당 개발 기준은 확인 필요로 남겼습니다.
- SOM과 구체 가격은 근거 숫자나 조사가 없어 UNVERIFIED입니다.
