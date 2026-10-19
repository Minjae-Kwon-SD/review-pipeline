# 아마존 미국 요가 매트 제품 개발 가이드
> "두 번 썼는데 벌써 작은 구멍이 생기고 있다" (Gaiam, 4★, R3EQ959LNHZ85K)

## 머리 숫자
- [head.topic_neg] 만듦새와 내구성을 부정으로 말한 리뷰어 비율(별점 가중)로 불만 1위이고, 리뷰를 다시 뽑아도 1위로 남은 비율이 99.4% [m:a.robust.head_first]다. 2위 디자인과 크기 5.8% [m:p.map.design]보다 앞서 찢김과 윗면 벗겨짐을 첫 개발 관문으로 둔다.
- [head.topic_weakest] 가장 큰 약점이 만듦새와 내구성인 상품 수이고, 그 상품은 Gaiam Dry-Grip 16.4% [m:s.B0BYFLL1LV.topic_neg]다. 상품 하나씩 빼기에서 결론이 바뀐 6번 중 1번 [m:a.robust.loo_flips]이 이 상품을 뺄 때(불만 1위가 끈과 휴대 구성품으로 바뀜)다. Gaiam Dry-Grip이 가장 높고 Gaiam Essentials, Retrospec Solana, CAP Extra Thick도 전체 8.6% [m:head.topic_neg]에 가깝고 얇은 Gaiam 둘만 낮다(점수표, Gaiam Dry-Grip은 두께 사양을 찾지 못함). 나머지 상품의 가장 큰 약점은 두께와 쿠션(Gaiam Classic), 그립과 미끄럼(Gaiam Premium), 디자인과 크기(Retrospec Solana), 끈과 휴대 구성품(Gaiam Essentials, CAP Extra Thick)이다.
- [head.dir_ratio] 두께 불만의 방향으로, 너무 얇음 쪽이 많다. 다만 Retrospec Solana는 -0.78 [m:s.B092XTMNCC.dir_index]로 두꺼운 쪽이고 상품 하나씩 빼면 두꺼운 쪽 비율이 4.3%~29.3% [m:a.robust.loo_low_share]로 움직여, 한 두께로 맞추지 않고 두께 단계와 운동별 안내로 대응한다.
- [head.market_month] 조사 상품이 모두 있는 Yoga Mats 노드의 한 달 매출 칸이고 통화가 확인되지 않아 상대 비교로만 쓴다. 1위 Gaiam 17.7% [m:m.top1_YM], 상위 10개 브랜드 합 63.9% [m:m.top10_share_YM](매출 점유율)이다.
- [head.fastest_term] 빠르게 크는 검색어로, 한 달 검색량 기준을 넘는 카테고리 검색어 121개 [m:m.growth_candidates] 가운데 주간 이력이 있는 28개 [m:m.growth_ranked]에서 성장 배수 1위다. 땀 조건 그립을 시험으로 보이는 것을 차별 요소로 검토한다(확인 필요).


## 01 시장 개요
**TL;DR** 요가 매트는 이미 넓게 찾는 범주이고(공통 검색어 검색량 합 2,505,343 [m:m.terms_common_volume]), Yoga Mats 노드는 1위 Gaiam 17.7% [m:m.top1_YM]을 포함해 여러 브랜드가 나눠 갖는다. 가장 빠르게 큰 검색어는 yoga mat non slip 하나이고(같은 뜻의 non slip yoga mat은 거의 그대로), 첫 상품은 브랜드 평균 가격 기준 시장 가격대의 가장 낮은 구간에서 얇다는 말을 피하는 두께, 땀에 젖어도 미끄럽지 않은 겉면, 끈을 갖춘 매트를 확인이 필요한 권고로 둔다.

### TAM, SAM, SOM
- **TAM(전 세계 요가 매트)**: IMARC는 세계 요가 매트 시장이 2025년 167억 달러에서 2026년 177억 달러로 커졌다고 본다 [r:mkt_01].
- **TAM 전망(IMARC)**: 연평균 4.51% 성장해 2034년 252억 달러에 이른다고 전망한다 [r:mkt_02].
- **TAM 전망(Technavio)**: 2025~2030년 연평균 5.6%로 32.8억 달러 늘어난다고 본다 [r:mkt_06].
- **같은 범위의 다른 추정**: Market.us는 2024년 121억 달러 [r:mkt_13], Grand View Research는 2023년 136억 달러 [r:mkt_14]로 본다. 보고서마다 해와 범위가 달라 한 값으로 고르지 않는다.
- **미국 쪽 단서**: IMARC는 2025년 북미 비중을 41.8% 넘게 [r:mkt_03], 북미 매출 가운데 미국을 88.00% [r:mkt_04]로 본다. 미국 단독 금액은 확인된 출처가 없어 확인 필요이고, 두 비율을 곱해 새 금액을 만들지 않는다.
- **SAM(아마존 미국 Yoga Mats 노드)**: 지금 확인할 수 있는 아마존 쪽 크기는 9,116,723(월 매출 칸, 통화 미확인) [m:head.market_month]이다.
- **연 환산은 가정**: 109,400,681(가정: 통화 미확인 월 매출 x 12, 계절 변동 미반영) [m:head.market_year]은 확인된 연 매출이 아니라 가정이라 SAM 값으로 쓰지 않는다.
- **수요 바탕**: SFIA 보고서(2022 Tracking the Fitness Movement)에서 미국 요가 참여자는 4.7% 늘어 3430만 명이다 [r:mkt_15]. 몇 해 전 보고서 값이라 지금 수요로 바로 읽지 않는다.
- **SOM(첫해 목표)**: 확인 필요. 지금 근거는 Yoga Mats 상위 10개 브랜드 점유율 합 63.9% [m:m.top10_share_YM] 밖의 몫을 나머지 브랜드가 나눠 갖는다는 점뿐이라, 목표 점유율은 출시 뒤 판매 자료로 정할 것을 권고한다.

### 판정 3개
- **침투: 이미 넓게 찾는 범주**: 공통 검색어 72개 [m:m.terms_common_n]의 한 달 검색량 합이 2,505,343 [m:m.terms_common_volume]이라, 범주를 알리는 일보다 이미 찾는 사람이 고르게 하는 일이 과제다.
- 이 합에는 play mat, gymnastics mat, exercise equipment처럼 요가 매트가 아닌 검색어도 들어 있어 범주 수요의 위 끝으로 읽는다.
- **경쟁 집중: 한 브랜드가 쥐지 않은 노드**: Yoga Mats 상위 10개 브랜드 점유율 합 63.9% [m:m.top10_share_YM], 1위 Gaiam 17.7% [m:m.top1_YM]이다(브랜드 매출을 노드 매출로 나눈 응답 값으로 확인한 매출 점유율).
- Exercise Mats는 상위 10개 합 56.9% [m:m.top10_share_EM], 1위 BalanceFrom 13.9% [m:m.top1_EM]로 더 흩어져 있고, 두 노드 상위 10개에 모두 드는 브랜드는 CAP 하나다.
- **기회: 미끄럼 방지 검색어**: "yoga mat non slip"은 최근 기간 검색량이 한 해 전 같은 기간의 1.89배 [m:head.growth_multiple]로, 이력이 있는 검색어 28개 [m:m.growth_ranked] 가운데 가장 빠르게 컸다. 같은 낱말을 다르게 늘어놓은 non slip yoga mat은 거의 그대로라(성장 표), 검색어 하나의 움직임으로 보고 키워드에 함께 넣는 정도로 쓴다.
- **기회: 가격대**: 시장 가격대에서 가장 낮은 구간 20.68~41.93 [m:m.price_band1_range]이 매출 비중 56.1% [m:m.price_band1_share]로 가장 크다. 시장 가격대 표는 브랜드 평균 가격으로 나눈 구간이라 단품 가격과 기준이 다르다.
- 가운데 구간은 매출 비중 20.3% [m:m.price_band2_share]로 세 구간 가운데 가장 작지만, 수요가 적은 것인지 공급이 적은 것인지는 이 데이터로 가르지 못해 빈자리로 단정하지 않는다(확인 필요).

### 검색 수요
- 검색어는 성별로 나뉘지 않고 공통 검색어 72개 [m:m.terms_common_n]를 함께 보며, 성별로 상품을 나누지 않는다.
- 상위 검색어는 yoga mat, mat, play mat, exercise equipment, gymnastics mat, pilates 순이고, 상위 검색어에 브랜드 이름이 든 검색어는 없다(검색어 표).
- **두께 검색어**: yoga mat thick 60,648 [m:std.thickness.term.yoga mat thick], thick yoga mat 40,757 [m:std.thickness.term.thick yoga mat]이다.
- **미끄럼 검색어**: yoga mat non slip 18,080 [m:std.grip.term.yoga mat non slip], hot yoga mat 15,342 [m:std.grip.term.hot yoga mat]이다.
- **필라테스 검색어**: pilates 61,313 [m:std.stability.term.pilates], pilates mat 52,675 [m:std.stability.term.pilates mat]이다.
- **가장 빠르게 큰 검색어**: yoga mat non slip은 최근 네 주 117,775 [m:head.growth_recent], 한 해 전 같은 네 주 62,273 [m:head.growth_prior]이다. 성장 표의 네 주 합과 위의 검색량 칸은 서로 다른 칸이라 한 줄에서 견주지 않는다.
- 이 순위는 검색량 기준을 넘은 카테고리 검색어 121개 [m:m.growth_candidates] 가운데 두 기간 주간 이력이 있는 검색어에서만 매겼고, 그 뒤로 foldable yoga mat, stakt yoga mat, exercise mats for home workout 순이다(stakt yoga mat은 브랜드 이름이 든 검색어).

### 진입 조건
- **두께**: 얇은 쪽보다 넉넉한 쪽을 기본으로 둔다. 두께 체감에서 너무 얇음, 쿠션이 모자람 161개 [m:f.thickness.thickness_feel.too_thin]가 너무 두껍거나 물렁함 60개 [m:f.thickness.thickness_feel.too_thick_soft]보다 많다. 목표 두께 값은 확인 필요이고, 02장 점수표의 상품별 두께 표기와 방향 지수를 함께 본다.
- **겉면과 재질**: 땀에 젖어도 미끄럽지 않은 겉면을 먼저 정한다. 그립을 말한 조건은 땀이나 물기가 있을 때 110개 [m:f.grip.grip_condition.sweat_moisture], 핫요가나 뜨거운 방의 수업 88개 [m:f.grip.grip_condition.hot_yoga]다. IMARC는 PVC를 가장 큰 재질 비중으로 보지만 [r:mkt_05], 어느 재질을 쓸지는 확인 필요다.
- **크기**: 표준 길이와 긴 판을 함께 검토한다. 크기 불만에서 폭이 좁음 34개 [m:std.size.label.too_narrow], 길이가 짧음 29개 [m:std.size.label.too_short]이고, JadeYoga Harmony는 한 너비에 두 길이로 판다 [r:ind_14]. 길이와 너비 값은 확인 필요.
- **가격대**: 시장 가격대의 가장 낮은 구간 20.68~41.93 [m:m.price_band1_range] 안에서 시작할 것을 권고한다(확인 필요). 조사 상품도 Gaiam Dry-Grip 하나를 빼면 이 범위 안의 가격이지만, 시장 가격대는 브랜드 평균 가격으로 나눈 구간이라 단품 가격과 기준이 달라 나란히만 본다.
- **구성(끈과 상세 설명)**: 끈을 넣고 상세의 구성과 실물을 맞춘다. 들어 있어야 할 끈이 빠져 옴 131개 [m:std.strap.label.strap_missing], 끈이나 가방이 원래 없어 아쉬움 18개 [m:std.strap.label.strap_not_included]다.


## 02 경쟁사
**TL;DR** 조사 상품은 Gaiam이 가장 많고 Retrospec과 CAP가 하나씩이며, 모두 Yoga Mats 노드에 있다. 만듦새와 내구성 부정은 Gaiam Dry-Grip 16.4% [m:s.B0BYFLL1LV.topic_neg]이 가장 높지만, 가장 큰 약점이 이 주제인 상품은 6개 중 1개(리뷰를 다시 뽑아 보면 1~3개) [m:head.topic_weakest]이고 나머지 상품의 가장 큰 약점은 끈과 휴대 구성품, 두께와 쿠션, 그립과 미끄럼, 디자인과 크기로 갈린다.

### 점수표 해설
- **만듦새와 내구성 부정 최고**: Gaiam Dry-Grip 16.4% [m:s.B0BYFLL1LV.topic_neg]이고, 리뷰어가 말한 손상까지 걸린 날 중앙값도 180일 [m:s.B0BYFLL1LV.duration_median]로 조사 상품 가운데 가장 길다. 이 상품은 같은 상품의 사양 페이지를 찾지 못해 사양 칸이 비어 있다(찾지 못함 [m:spec.B0BYFLL1LV.match]).
- **두꺼운 매트 둘**: Gaiam Essentials 8.0% [m:s.B07H9PZDQW.topic_neg], Retrospec Solana 7.6% [m:s.B092XTMNCC.topic_neg]이다.
- **CAP Extra Thick**: 7.3% [m:s.B0CRXCBY1Y.topic_neg]이고, 손상까지 걸린 날 중앙값이 25.5일 [m:s.B0CRXCBY1Y.duration_median]로 가장 짧다(리뷰어가 적은 값).
- **만듦새와 내구성 부정 최저**: Gaiam Classic Print 2.6% [m:s.B01MY5MZSQ.topic_neg], Gaiam Premium Print 2.8% [m:s.B09WF4GPPC.topic_neg]이다.
- **사양과 나란히(얇은 쪽)**: 부정이 낮은 두 상품의 두께 표기는 4 mm [m:spec.B01MY5MZSQ.thickness], 6mm [m:spec.B09WF4GPPC.thickness]다.
- **사양과 나란히(두꺼운 쪽)**: Retrospec Solana는 1” [m:spec.B092XTMNCC.thickness], CAP Extra Thick은 1 inch [m:spec.B0CRXCBY1Y.thickness] 표기다. 상품이 적어 두께와 내구성 불만을 원인으로 잇지 않고 나란히만 놓는다.
- **두께 방향(너무 얇음 쪽)**: 방향 지수는 Gaiam Classic Print +1.00 [m:s.B01MY5MZSQ.dir_index], Gaiam Premium Print +0.88 [m:s.B09WF4GPPC.dir_index]로 너무 얇음 쪽이다.
  > "바닥이 그대로 다 느껴진다" (Gaiam, 4★, R201CO6K5VNCYT)
- **두께 방향(상품마다 다름)**: Gaiam Dry-Grip +1.00 [m:s.B0BYFLL1LV.dir_index]도 너무 얇음 쪽이지만, Retrospec Solana는 -0.78 [m:s.B092XTMNCC.dir_index]로 너무 두껍거나 푹신함 쪽이다. Gaiam Essentials와 CAP Extra Thick은 방향 라벨 리뷰가 기준 수보다 적어 비어 있다.
  > "요가용으로는 너무 두껍다" (Retrospec, 1★, R1D0E3JBFI44SA)
- 방향이 분명한 상품 넷 가운데 셋은 너무 얇음 쪽, 하나는 반대쪽이라, 두께 한 값으로 모든 불만을 줄이기는 어렵고 두께 단계를 나누는 선택지와 함께 읽힌다.
- **가장 큰 강점**: Gaiam Classic Print와 Gaiam Premium Print는 디자인과 크기, Gaiam Essentials와 Retrospec Solana와 CAP Extra Thick은 두께와 쿠션, Gaiam Dry-Grip은 그립과 미끄럼이다.
- **별점**: 가중 평균 별점은 Gaiam Premium Print 4.70★ [m:s.B09WF4GPPC.star]이 가장 높고 Gaiam Dry-Grip 4.24★ [m:s.B0BYFLL1LV.star]이 가장 낮다.
- **가격**: 개당 가격은 Gaiam Premium Print 21.55달러 [m:s.B09WF4GPPC.price]가 가장 낮고 Gaiam Dry-Grip 48.98달러 [m:s.B0BYFLL1LV.price]가 가장 높다.
- **재질 표기**: Retrospec Solana는 high-density foam [m:spec.B092XTMNCC.material], CAP Extra Thick은 high density foam [m:spec.B0CRXCBY1Y.material], Gaiam Premium Print는 latex-free PVC [m:spec.B09WF4GPPC.material]이다.
- **크기 표기**: Retrospec Solana 72x24" [m:spec.B092XTMNCC.size], CAP Extra Thick 68 inch by 24 inch [m:spec.B0CRXCBY1Y.size]다.
- **사양 출처**: Retrospec Solana와 CAP Extra Thick은 브랜드 공식 상품 페이지(retrospec.com, capbarbell.com), Gaiam Classic Print와 Gaiam Premium Print는 소매점 상품 페이지(ayurveda101.com, yeswellness.com)에서 다시 열어 확인한 값이다.
- **이름만 일치한 상품**: Gaiam Essentials의 재질 NBR Foam [m:spec.B07H9PZDQW.material]은 gaiam.com 공식 페이지 이름 기준이다(공식 페이지 상품명이 아마존 상품명과 달라 같은 판인지 이름으로 확인하지 못함).

### 하위 카테고리 비교
- 조사 상품은 모두 Yoga Mats 노드에 있어 상품을 노드끼리 견주는 비교는 약하다.
- Yoga Mats 노드는 9,116,723(월 매출 칸, 통화 미확인) [m:head.market_month]이고, 표의 Yoga Equipment와 Exercise & Fitness Accessories는 매출 칸이 이보다 크며 Yoga Towels, Yoga Blocks, Yoga Straps는 작다. 노드마다 범위가 달라 매출 칸을 더해 시장으로 쓰지 않는다.
- Yoga Mat Straps, Yoga Mat Bags처럼 끈과 가방만 파는 노드가 따로 있다(매출 칸은 표).
- 브랜드 점유율의 1위는 Yoga Mats가 Gaiam 17.7% [m:m.top1_YM], Exercise Mats가 BalanceFrom 13.9% [m:m.top1_EM]로 다르다.
- Yoga Mats 상위 10개에는 Manduka, Liforme, Stakt처럼 브랜드 평균 가격이 높은 브랜드가, Exercise Mats 상위 10개에는 Gxmmat, Gorilla Mats처럼 평균 가격이 높은 브랜드가 함께 있다(브랜드 표).

### 업계 구조
- **두께 단계로 나눈 라인(Retrospec)**: Retrospec은 Solana, Pismo, Laguna 매트를 두께로 나눈 네 모델로 팔고(표기는 출처 원문) [r:ind_12], 가장 두꺼운 1인치 매트를 관절 통증이 있는 사람에게 권한다 [r:ind_13].
- **ProsourceFit**: Classic Yoga Mat 1/8-in [r:ind_16]과 Extra Thick Yoga and Pilates Mat 1-in [r:ind_17]을 함께 판다.
- **Gaiam 공식 목록**: Fitness Mat (10mm) [r:ind_07]와 Gaiam Foldable Yoga Mat (2mm) [r:ind_08]가 요가 매트 목록에 함께 있다.
- **Gaiam 어린이 매트**: 같은 목록에 Kids Twinkle Toes Yoga Mat (3mm)도 있다 [r:ind_09].
- **Manduka PRO**: Manduka PRO Yoga Mat 6mm [r:ind_01]는 정가 144달러이고 [r:ind_02], Manduka는 PRO 매트가 OEKO-TEX 인증을 받았다고 밝힌다 [r:tst_10].
- **Manduka 여행용 매트**: PRO 계열에 PRO Travel Yoga Mat 2mm가 [r:ind_03], 천연 고무 eKO 계열에 eKO Travel Superlite Yoga Mat 1.5mm가 있다 [r:ind_04].
- **Manduka begin**: begin 매트는 정가 62달러다 [r:ind_05].
- **보증**: Manduka PRO Lite 매트는 평생 보증을 내걸고 [r:ind_06], Gorilla Mats는 매트에 결함이 생기면 바꿔 준다고 내건다 [r:ind_19].
- **CAP**: CAP High Density Exercise Yoga Mat with Strap은 1 Inch Thick, 끈 포함 구성이다 [r:ind_18].
- **JadeYoga Harmony**: 너비 하나에 68인치와 74인치 두 길이로 팔고 [r:ind_14], JadeYoga는 매트를 미국에서 만든다고 밝힌다 [r:ind_15].
- **JadeYoga 자율 고지**: 천연 고무 매트에 라텍스 단백질이 미량 있을 수 있다고 스스로 알린다 [r:reg_15](연방 의무 표시가 아니라 업체 자율 고지).
- **재질 비중**: IMARC는 2025년 재질별로 PVC가 38.7%로 가장 큰 비중이라고 본다 [r:mkt_05].


## 03 문제
**TL;DR** 불만 1위는 만듦새와 내구성 8.6% [m:p.map.build_durability]이고, 리뷰를 다시 뽑아도 1위로 남은 비율이 99.4% [m:a.robust.head_first]다. 다만 상품 하나를 빼면 1위가 바뀌는 경우가 있어 상품마다 따로 읽는다. 집중 분석 네 개(내구성, 두께, 그립, 냄새)의 불만을 원인 번호(설계 결함 또는 선호 차이)로 나눠 04장 기준표와 잇는다.

### 불만 지도
- 만듦새와 내구성 8.6% [m:p.map.build_durability], 디자인과 크기 5.8% [m:p.map.design] 순으로 앞선다.
- 그다음 끈과 휴대 구성품 5.0% [m:p.map.carry_strap], 냄새 4.2% [m:p.map.odor]이다.
- 그립과 미끄럼 4.1% [m:p.map.grip_traction], 두께와 쿠션 4.0% [m:p.map.cushioning]은 냄새와 거의 같은 수준이라 세 주제를 함께 개발 관문에 둔다.
- 상품 하나씩 빼 보면 1위가 바뀐 경우는 6번 중 1번 [m:a.robust.loo_flips]이고, Gaiam B0BYFLL1LV를 뺄 때 끈과 휴대 구성품이 1위가 된다(A장 견고성 점검).
- 가장 큰 약점이 만듦새와 내구성인 상품은 6개 중 1개(리뷰를 다시 뽑아 보면 1~3개) [m:head.topic_weakest]이고, 그 상품이 Gaiam B0BYFLL1LV 16.4% [m:s.B0BYFLL1LV.topic_neg]다.
- 2위 디자인과 크기와 3위 끈과 휴대 구성품은 집중 분석 밖이다. 크기 쪽은 말면 부피가 커서 들고 다니기나 보관이 어려움 47개 [m:std.size.label.bulky_to_carry_store], 끈 쪽은 들어 있어야 할 끈이 빠져 옴 131개 [m:std.strap.label.strap_missing]가 가장 많다.

### 별점 격차
- **브랜드 경험**: 부정 1.73★ [m:p.gap1_neg], 격차 -2.83 [m:p.gap1]로 가장 크고, 인용에는 추천하지 않겠다, 다른 브랜드로 바꾸겠다는 말이 보인다.
- **묻어남과 얼룩**: 부정 1.86★ [m:p.gap2_neg], 격차 -2.65 [m:p.gap2]이고, 색이 발이나 바닥에 묻었다는 말이 많다(집중 분석 1의 원인 5와 같은 불만).
- **고객 응대**: 부정 2.03★ [m:p.gap3_neg], 격차 -2.49 [m:p.gap3]이고, 인용에는 반품 기간이 지났거나 큰 상자가 없어 반품하지 못했다는 말이 보인다.
- 격차는 낮은 별점과 함께 나온 정도이지 원인이 아니다. 불만 지도 상위 주제(만듦새와 내구성 등)는 격차 상위 세 주제에 들지 않는다.

> "추천하지 않겠다" (Gaiam, 1★, R4YRX4ALXA8QC)
> "보라색이 발등에 묻어나기 시작했다" (Gaiam, 2★, RJ351L06ZF6CL)

### 집중 분석 1: 만듦새와 내구성, 찢김과 윗면 벗겨짐
- **손상 종류**: 찢어짐, 구멍 121개 [m:f.durability.damage_type.tear_rip], 윗면이 벗겨짐, 층이 떨어짐, 기포 99개 [m:f.durability.damage_type.top_layer_peel]가 앞선다(설계 정보 값).
- **처음부터 흠과 부스러짐**: 받았을 때부터 흠이나 불량 82개 [m:f.durability.damage_type.arrived_damaged], 부스러짐, 알갱이나 재질이 떨어져 나옴 75개 [m:f.durability.damage_type.crumble_shed]다.
- **손상까지 걸린 날**: 값 105개 [m:f.durability.durability_elapsed_days.n]의 중앙값이 75일 [m:f.durability.durability_elapsed_days.median]이다(리뷰어가 적은 값이라 측정값이 아님).
- **기간 분포**: 30~180일 41개 [m:f.durability.durability_elapsed_days.bin2]가 가장 많고, 7~30일도 21개 [m:f.durability.durability_elapsed_days.bin1]다.
- **오래 쓴 뒤 손상**: 365일 이상 27개 [m:f.durability.durability_elapsed_days.bin4]도 있어, 몇 년 쓴 뒤 코팅이 벗겨졌다는 말과 몇 번 쓰고 찢어졌다는 말이 함께 있다.
- **상품 차이**: 만듦새와 내구성 부정은 Gaiam B0BYFLL1LV 16.4% [m:s.B0BYFLL1LV.topic_neg], Gaiam B01MY5MZSQ 2.6% [m:s.B01MY5MZSQ.topic_neg]로 같은 브랜드 안에서도 크게 갈린다(상품이 6개뿐이라 순위로 읽지 않음).
- **상품별 손상까지 걸린 날**: Gaiam B0BYFLL1LV 중앙값 180일 [m:s.B0BYFLL1LV.duration_median], CAP B0CRXCBY1Y 25.5일 [m:s.B0CRXCBY1Y.duration_median]이다(상품마다 값이 적음).

> "두 번 썼는데 벌써 작은 구멍이 생기고 있다" (Gaiam, 4★, R3EQ959LNHZ85K)
> "3년째에 검은 코팅이 벗겨지기 시작했다" (Gaiam, 3★, RH3FU03K6P58X)
> "기본 전사 자세 2 동작만 했는데 네 군데가 찢어졌다" (Retrospec, 1★, RT1SC037QN3XO)

**시사점**
- 찢김과 윗면 벗겨짐이 가장 많고 손상이 몇 주에서 몇 달 사이에 많이 보고되어, 출시 전 반복 사용 조건에서 표면층 접착과 찢김 강도를 확인하는 관문이 필요하다.
- 같은 브랜드 안에서도 상품마다 부정 비율이 크게 달라, 브랜드가 아니라 상품의 재질과 마감 단위로 비교한다.
- 원인 1(설계 결함), 찢김과 윗면 벗겨짐: 찢어짐이나 구멍 122개 [m:std.durability.label.tears_holes], 윗면이 벗겨지거나 기포가 생김 95개 [m:std.durability.label.surface_peels_bubbles]
- 원인 2(설계 결함), 낮은 품질과 빠른 낡음: 품질이 낮거나 오래 못 갈 것 같음 91개 [m:std.durability.label.poor_quality_general], 금방 낡아 보이거나 자국이 남음 72개 [m:std.durability.label.wear_marks]
- 원인 3(설계 결함), 부스러짐과 끝 말림: 부스러지거나 조각이 떨어짐 68개 [m:std.durability.label.crumbles_sheds], 끝이 말리고 평평하게 안 펴짐 35개 [m:std.durability.label.curls_not_flat]
- 원인 4(설계 결함), 도착 불량: 받았을 때부터 흠이나 불량 35개 [m:std.durability.label.defective_on_arrival]
- 원인 5(설계 결함), 색과 가루 묻어남: 색이 묻어나 얼룩 30개 [m:std.residue.label.color_rubs_off], 가루나 조각이 떨어져 묻음 21개 [m:std.residue.label.flakes_residue_shed]

### 집중 분석 2: 두께, 쿠션, 균형, 너무 얇음 쪽 방향
- **두께 방향**: 너무 두껍거나 푹신함 44개 대 너무 얇음 157개(0.28배) [m:head.dir_ratio]로 얇음 쪽이 많다.
- **가중 비율**: 전체 리뷰어 대비 너무 두껍거나 푹신함 1.0% [m:head.dir_low_w], 너무 얇음 4.1% [m:head.dir_high_w]이다.
- **만족이 더 많음**: 두께 체감 값은 두께와 쿠션이 좋음, 넉넉함, 알맞음 480개 [m:f.thickness.thickness_feel.good_thickness]가 너무 얇음, 쿠션이 모자람 161개 [m:f.thickness.thickness_feel.too_thin]보다 많다.
- **너무 얇음 쪽 상품**: 방향 지수가 Gaiam B01MY5MZSQ +1.00 [m:s.B01MY5MZSQ.dir_index], Gaiam B09WF4GPPC +0.88 [m:s.B09WF4GPPC.dir_index]이고, Gaiam B0BYFLL1LV도 같은 쪽이다.
- **너무 두꺼운 쪽 상품**: Retrospec B092XTMNCC는 -0.78 [m:s.B092XTMNCC.dir_index]로 반대쪽이고, Gaiam B07H9PZDQW와 CAP B0CRXCBY1Y는 방향 라벨이 적어 비어 있다. 상품마다 방향이 다르다.
- **사양과 나란히**: 표기 두께는 Gaiam B01MY5MZSQ 4 mm [m:spec.B01MY5MZSQ.thickness](소매점 페이지 ayurveda101.com 기준), Retrospec B092XTMNCC 1” [m:spec.B092XTMNCC.thickness](retrospec.com 공식 페이지 기준)다. 상품이 적어 사양과 불만을 원인으로 잇지 않는다.
- **표기보다 얇음**: 표기보다 얇음 39개 [m:std.thickness.label.thinner_than_listed]이고, 1인치 표기 상품에서 실제로는 그보다 얇다는 말이 있다.
- **무릎**: 무릎이 편함, 무릎을 받쳐 줌 104개 [m:f.thickness.body_part_effect.knees_protected], 무릎이 아픔, 무릎 받침이 모자람 28개 [m:f.thickness.body_part_effect.knees_hurt]다.
- **무릎 통증과 얇음**: 무릎이 아프다는 리뷰 가운데 너무 얇음 쪽 라벨이 함께 붙은 것은 28개 중 12개(42.9%) [m:f.thickness.body_part_effect.knees_hurt.too_thin]다(함께 나온 것이지 원인이 아님).
- **말한 두께**: 리뷰어가 적은 두께 값 85개 [m:f.thickness.thickness_mm.n]의 중앙값은 19.05mm [m:f.thickness.thickness_mm.median]로, 측정값이 아니라 리뷰어 표기다.

> "아주 얇아서 필라테스 같은 바닥 운동을 할 매트는 아니다" (Gaiam, 4★, R1HV2GVQKOU05O)
> "실제로는 3/4인치 두께이고 적힌 대로 1인치가 아니다" (Retrospec, 4★, R6CRJ4N4HLZ41)
> "쿠션이 더해져서 균형을 잡고 버티기가 훨씬 어렵다" (Retrospec, 4★, R1BL8596L6QFQ2)
> "충격을 받는 자리가 종이 한 장처럼 납작해졌다" (CAP, 1★, R8HVSDKU7L31R)

**시사점**
- 얇음 쪽 불만이 많지만 두꺼운 상품에서는 너무 푹신해 균형이 어렵다는 반대 불만이 있어, 한 두께로 모두를 맞추기보다 두께 선택지와 운동 종류별 안내로 대응한다(원인 8, 10).
- 쓰다 보니 꺼진다는 말과 표기보다 얇다는 말이 있어, 눌림 뒤 복원과 표기 두께의 실측 일치를 함께 확인한다.
- 원인 6(설계 결함), 얇고 딱딱함: 너무 얇음 113개 [m:std.thickness.label.too_thin], 딱딱하거나 쿠션이 부족함 45개 [m:std.thickness.label.hard_no_cushion]
- 원인 7(설계 결함), 무릎 받침 부족과 꺼짐: 무릎이나 관절을 받쳐 주지 못함 20개 [m:std.thickness.label.knee_joint_strain], 쓰다 보니 꺼짐 11개 [m:std.thickness.label.flattens_over_time]
- 원인 8(선호 차이), 너무 두꺼움: 너무 두껍거나 물렁함 44개 [m:std.thickness.label.too_thick_soft]
- 원인 9(설계 결함), 늘어남과 불안정: 매트가 늘어남 32개 [m:std.stability.label.stretches_out], 균형 잡기 어렵고 불안정함 29개 [m:std.stability.label.unstable_balance]
- 원인 10(선호 차이), 푹신해서 균형 어려움: 두껍거나 푹신해서 균형이 어려움 22개 [m:std.stability.label.thick_hard_to_balance]

### 집중 분석 3: 그립과 미끄럼, 땀과 바닥 조건
- **그립을 말한 조건**: 땀이나 물기가 있을 때 110개 [m:f.grip.grip_condition.sweat_moisture], 핫요가나 뜨거운 방의 수업 88개 [m:f.grip.grip_condition.hot_yoga]다(긍정과 부정을 함께 센 설계 정보 값).
- **겉면 질감**: 끈적함 44개 [m:f.grip.surface_texture.sticky_tacky], 밀도 있고 단단함 41개 [m:f.grip.surface_texture.dense_firm]가 앞선다.
- **땀과 젖음**: 땀을 빨아들임 36개 [m:f.grip.surface_texture.sweat_absorbing], 젖은 뒤 잘 마르지 않음 15개 [m:f.grip.surface_texture.stays_wet]다.
- **설명과의 차이**: 미끄럼 방지 설명이 틀림 14개 [m:std.listing.label.nonslip_claim_false]이고, 미끄러지거나 흔들려 다칠 위험 8개 [m:std.safety.label.slip_injury_risk]는 안전 불만으로도 셌다.
- **부정이 가장 적은 상품**: CAP 1.6% [m:std.grip.best]다.
- **시간이 지나 미끄러워짐**: 몇 달에서 몇 년 쓴 뒤 그립이 떨어졌다는 말이 있어, 첫 사용 그립과 오래 쓴 뒤 그립을 따로 본다.

> "아주 조금만 땀이나 물기가 있어도 다운독 같은 자세에서 손이 미끄러졌다" (Gaiam, 4★, RYIWUWCRCLXR6)
> "발은 그대로 있는데 매트가 큰 끽 소리를 내며 바닥에서 밀린다" (Gaiam, 4★, R125MURUAY00KJ)
> "끈끈한 표면은 9개월쯤 가고, 그 뒤로는 미끄러워진다" (Gaiam, 4★, R6EBF64X7IBS6)

**시사점**
- 손발이 윗면에서 미끄러지는 불만과 매트가 바닥에서 밀리는 불만이 나뉘어, 윗면 그립과 밑면 고정을 따로 확인한다.
- 땀과 물기 조건, 오래 쓴 뒤 그립 유지가 함께 말해져, 젖은 상태와 반복 사용 뒤의 그립을 출시 전 관문에 둔다.
- 원인 11(설계 결함), 윗면과 바닥 미끄럼: 손발이 표면에서 미끄러짐 187개 [m:std.grip.label.surface_slippery], 매트가 바닥에서 밀림 65개 [m:std.grip.label.slides_on_floor]
- 원인 12(설계 결함), 땀 미끄럼과 그립 저하: 땀나거나 젖으면 미끄러움 36개 [m:std.grip.label.slips_when_sweaty], 쓰다 보니 그립이 떨어짐 29개 [m:std.grip.label.grip_wears_off]

### 집중 분석 4: 냄새와 성분, 첫 냄새와 남는 냄새
- **해 봐도 남는 냄새**: 바람, 햇볕, 세척을 해 봤는데도 남음 63개 [m:f.odor.odor_outcome.persists_after_tries]가 바람, 햇볕, 세척으로 빠짐 24개 [m:f.odor.odor_outcome.faded_after_airing_washing]보다 많다.
- **기다림과 무취**: 빠지기를 기다리는 중, 결과 모름 34개 [m:f.odor.odor_outcome.waiting_unknown], 냄새가 없었음 22개 [m:f.odor.odor_outcome.no_odor]다.
- **냄새가 간 날**: 값 45개 [m:f.odor.odor_duration_days.n]의 중앙값이 7일 [m:f.odor.odor_duration_days.median]이다(리뷰어가 적은 값).
- **오래 남은 경우**: 30~180일 8개 [m:f.odor.odor_duration_days.bin2], 365일 이상 3개 [m:f.odor.odor_duration_days.bin4]도 있다.
- **몸에 뱀**: 냄새가 손이나 몸에 뱀 3개 [m:f.odor.odor_outcome.transfers_to_body]다.
- **부정이 가장 적은 상품**: CAP 2.6% [m:std.odor.best]다.
- **몸 반응과 함께**: 안전에서 두통으로 판정한 리뷰는 16개 [m:p.safety.두통]이고, 그 인용에는 화학 냄새를 함께 든 말이 있다(예 R32UI56DRSVY4X, 안전 소제목).

> "일주일 동안 펼쳐 두고 '숨 쉬게' 했는데도 아직 방 전체에 냄새가 진동한다" (Gaiam, 1★, R22ETK6EL0RYIL)
> "하루 종일 밖에 두어 바람을 쐬었더니 문제가 완전히 해결됐다" (Gaiam, 4★, R2H55F5G86GVA9)
> "썩은 삶은 달걀이나 유황 같은 냄새가 난다" (CAP, 3★, R3W4V1LH2J1CG5)

**시사점**
- 첫 냄새가 바람 쐬기로 빠졌다는 리뷰와 해 봐도 남는다는 리뷰가 함께 있어, 출하 전 냄새 빼기와 상자 안 안내(펼쳐 두는 기간)를 같이 둔다.
- 냄새가 두통이나 메스꺼움 같은 몸 반응 말과 함께 나와, 재질과 성분 확인을 안전 관문과 잇는다.
- 원인 13(설계 결함), 화학 냄새: 화학이나 플라스틱 냄새 145개 [m:std.odor.label.chemical_smell], 종류 없이 냄새가 심함 132개 [m:std.odor.label.unspecified_bad_smell]
- 원인 14(설계 결함), 오래 남는 냄새: 바람을 쐬거나 씻어도 안 빠짐 60개 [m:std.odor.label.smell_persists], 처음 냄새가 빠지는 데 시간이 걸림 48개 [m:std.odor.label.slow_to_fade]
- 원인 15(설계 결함), 이상한 냄새: 생선이나 유황 같은 냄새 12개 [m:std.odor.label.odd_smell]

### 안전
- 안전 부정 리뷰 109개: 두통 16개(가중 0.2%), 메스꺼움 13개(가중 0.1%), 호흡 6개(가중 0.2%), 어지럼 3개(가중 0.0%), 피부 8개(가중 0.1%), 이상 반응 없음 63개 [m:p.safety_text]
- 안전 부정 라벨: 발암 경고나 유해 성분 표시 22개, 두통이나 어지러움 20개, 독성이나 건강 해로움 우려 17개, 구역질이나 메스꺼움 14개, 숨 막힘이나 눈과 목 따가움 9개, 피부 발진이나 쓸림 8개, 미끄러지거나 흔들려 다칠 위험 8개 [m:p.safety_labels]
- **경고 표시와 성분 걱정**: 발암 경고나 유해 성분 표시 22개 [m:std.safety.label.cancer_warning]는 상품의 경고 문구나 성분 이름을 본 말이고, 독성이나 건강 해로움 우려 17개 [m:std.safety.label.toxic_health_concern]는 실제 몸 반응이 아니라 걱정이다.
- **몸 반응**: 두통 16개 [m:p.safety.두통], 메스꺼움 13개 [m:p.safety.메스꺼움]이고, 인용에는 냄새를 함께 든 말이 있다(예 R32UI56DRSVY4X).
- **피부와 호흡**: 피부 8개 [m:p.safety.피부], 호흡 6개 [m:p.safety.호흡]다.
- **비율**: 안전 부정 가중 1.4% [m:std.safety.neg_pct]이고, 가장 적은 상품은 Gaiam 0.6% [m:std.safety.best]다. 안전 불만은 원인 번호 밖(03 원인 밖)이고 04장 기준표에서 따로 다룬다.

> "이 매트에 발암 물질이 들어 있다고 분명히 적힌 Prop 65 경고" (Retrospec, 1★, R2F2AQY1GFGUF3)
> "몇 분 만에 매트의 화학 냄새 때문에 두통이 났다" (Gaiam, 3★, R32UI56DRSVY4X)
> "매트 때문에 심한 발진이 났다" (Retrospec, 1★, R4IUA69LVOND8)

## 04 포지셔닝
**TL;DR** 포지션은 찢김과 벗겨짐을 시험으로 막은 겉층에 땀에도 미끄럽지 않은 그립을 더하고, 두께를 단계로 나눠 고르게 하는 요가 매트다. 근거는 불만 1위 만듦새와 내구성 8.6% [m:head.topic_neg]와 너무 두껍거나 푹신함 44개 대 너무 얇음 157개(0.28배) [m:head.dir_ratio]이고, 가장 큰 약점이 이 주제인 상품은 6개 중 1개(리뷰를 다시 뽑아 보면 1~3개) [m:head.topic_weakest]이다. Gaiam Dry-Grip이 가장 높고 Gaiam Essentials, Retrospec Solana, CAP Extra Thick도 7.3% [m:s.B0CRXCBY1Y.topic_neg]~8.0% [m:s.B07H9PZDQW.topic_neg]로 전체 8.6% [m:head.topic_neg]에 가깝고 얇은 Gaiam 둘만 낮다(02장 점수표, Gaiam Dry-Grip은 두께 사양을 찾지 못함). 끈 빠짐과 냄새도 같은 출시 관문에 두고, 두꺼운 운동 매트 단계는 첫 상품의 내구성 결과를 본 뒤로 미룰 것을 권고한다(확인 필요).

### 한 줄 포지션
찢김 시험을 거친 겉층과 땀에도 미끄럽지 않은 그립을 갖추고, 두께를 단계로 나눠 실측값을 상자에 적으며, 끈을 빠짐없이 넣는 요가 매트 브랜드

### 이기는 이유
- **내구성 불만 1위의 공백**: 만듦새와 내구성 부정 8.6% [m:head.topic_neg]가 불만 1위이고, 리뷰를 다시 뽑아도 1위로 남은 비율이 99.4% [m:a.robust.head_first]다.
- **Gaiam Dry-Grip에서 가장 높은 내구성 불만**: Gaiam Dry-Grip이 16.4% [m:s.B0BYFLL1LV.topic_neg]로 가장 높고, 상품 하나씩 빼기에서 결론이 바뀐 6번 중 1번 [m:a.robust.loo_flips]이 이 상품을 뺄 때(불만 1위가 끈과 휴대 구성품으로 바뀜)다.
- **두꺼운 매트 둘은 전체 수준**: Gaiam Essentials 8.0% [m:s.B07H9PZDQW.topic_neg], Retrospec Solana 7.6% [m:s.B092XTMNCC.topic_neg]로 전체 8.6% [m:head.topic_neg]에 가깝다.
- **CAP Extra Thick도 같은 수준**: 7.3% [m:s.B0CRXCBY1Y.topic_neg]이라, 내구성은 차별 요소로 검토하되 어느 값대에서나 지킬 기본 조건으로 둔다(확인 필요).
- **얇은 Gaiam 둘만 낮음**: Gaiam Classic 2.6% [m:s.B01MY5MZSQ.topic_neg], Gaiam Premium 2.8% [m:s.B09WF4GPPC.topic_neg]이다(상품이 적어 두께와 내구성 불만을 원인으로 잇지 않음).
- **얇은 쪽 불만이 많은 상품**: Gaiam Classic +1.00 [m:s.B01MY5MZSQ.dir_index], Gaiam Premium +0.88 [m:s.B09WF4GPPC.dir_index]이 너무 얇음 쪽이고, Gaiam Dry-Grip도 같은 쪽이다.
- **두꺼운 쪽 불만이 많은 상품**: Retrospec Solana는 -0.78 [m:s.B092XTMNCC.dir_index]로 너무 두껍거나 푹신함 쪽이고 공식 사양 두께는 1” [m:spec.B092XTMNCC.thickness]다(사양과 불만은 나란히만 놓음). Gaiam Essentials와 CAP Extra Thick은 방향 라벨이 적어 비어 있다.
- **두께 단계와 안내**: 상품마다 방향이 달라 한 두께로 모두를 맞추기 어렵다. Retrospec이 이미 두께로 나눈 네 모델을 두므로 [r:ind_12] 단계 구성만으로 차별된다고 보지 않고, 단계마다 맞는 운동을 적는 안내를 차별 요소로 검토한다(확인 필요).
- **빠르게 크는 미끄럼 방지 검색**: "yoga mat non slip"의 검색량 성장 배수가 1.89배 [m:head.growth_multiple]이고, 손발이 표면에서 미끄러짐 리뷰가 187개 [m:std.grip.label.surface_slippery]다. 땀 조건 그립을 시험으로 보이는 것을 차별 요소로 검토한다(확인 필요).
- **끈 빠짐**: 들어 있어야 할 끈이 빠져 옴 131개 [m:std.strap.label.strap_missing]다. 끈을 넣는 구성은 CAP가 이미 판매하므로 [r:ind_18], 빠짐없이 넣는 포장 검품을 차별 요소로 검토한다(확인 필요).
- **보증**: Manduka PRO Lite는 평생 보증을 [r:ind_06], Gorilla Mats는 결함이 생기면 바꿔 주는 보증을 [r:ind_19] 내건다. 보증은 차별 요소가 아니라 따라잡을 조건으로 검토한다(확인 필요).

### 소비자 기준표
#### 기준 1: 찢어짐과 내구성(원인 1, 2, 3, 4 대응)
- 감점 기준: 내구성 불만 가중 8.8% [m:std.durability.neg_pct], 그중 찢어짐이나 구멍 122개 [m:std.durability.label.tears_holes]가 가장 많다.
- 만족 기준: 내구성 만족 리뷰 238개 [m:std.durability.pos]처럼 몇 달 써도 찢기거나 벗겨지지 않는 수준이고, 부정이 가장 적은 상품은 Gaiam 2.2% [m:std.durability.best](Gaiam Premium)다.
- 개발 기준: 겉층과 몸체 재질을 ASTM D624 찢김 강도 [r:tst_01]와 ASTM D412 인장 성질 [r:tst_02]로 비교해 고르고, 리뷰어가 말한 손상까지 걸린 날 중앙값이 75일 [m:f.durability.durability_elapsed_days.median]이라 몇 달 사용 시험을 함께 둔다(목표 값은 확인 필요).
- 상세페이지 문구: "Tear-resistant surface, lab-tested for tear strength" (찢김에 강한 겉면, 찢김 강도 시험), 시험 통과 뒤에만.

#### 기준 2: 두께와 쿠션(원인 6, 7, 8 대응)
- 감점 기준: 두께와 쿠션 불만 가중 5.8% [m:std.thickness.neg_pct], 그중 너무 얇음 113개 [m:std.thickness.label.too_thin]가 가장 많다.
- 만족 기준: 두께와 쿠션 만족 리뷰 667개 [m:std.thickness.pos]처럼 무릎과 손목을 받쳐 주는 수준이고, 부정이 가장 적은 상품은 CAP 3.1% [m:std.thickness.best]다.
- 개발 기준: 방향은 너무 두껍거나 푹신함 44개 대 너무 얇음 157개(0.28배) [m:head.dir_ratio]라 얇은 쪽을 먼저 막되, 두꺼운 쪽을 원하는 사람도 있어(선호 차이) Retrospec처럼 두께 단계를 나눈다 [r:ind_12]. 쓰다 보니 꺼짐을 막는 압축 회복 시험은 확인 필요(조사 근거 없음).
- 상세페이지 문구: "Pick the thickness that fits your practice" (운동에 맞는 두께를 고르세요).

#### 기준 3: 그립과 미끄럼(원인 11, 12 대응)
- 감점 기준: 그립 불만 가중 5.7% [m:std.grip.neg_pct], 그중 손발이 표면에서 미끄러짐 187개 [m:std.grip.label.surface_slippery]가 가장 많다.
- 만족 기준: 그립 만족 리뷰 321개 [m:std.grip.pos]처럼 땀이 나도 손발이 버티는 수준이고, 부정이 가장 적은 상품은 CAP 1.6% [m:std.grip.best]다.
- 개발 기준: 출하 검품에 미끄럼 저항 시험을 넣고 [r:tst_14](검품 업체 기준, 공인 표준 아님), 그립을 땀이나 물기 조건에서 말한 리뷰 110개 [m:f.grip.grip_condition.sweat_moisture]에 맞춰 젖은 상태로도 잰다. 매트가 바닥에서 밀림 65개 [m:std.grip.label.slides_on_floor]라 아랫면 질감도 함께 보고, 목표 마찰 값은 확인 필요.
- 상세페이지 문구: "Grips even when you sweat" (땀이 나도 미끄럽지 않음), 미끄럼 시험 통과 뒤에만.

#### 기준 4: 균형과 늘어남(원인 9, 10 대응)
- 감점 기준: 균형과 늘어남 불만 가중 2.2% [m:std.stability.neg_pct], 그중 매트가 늘어남 32개 [m:std.stability.label.stretches_out]가 가장 많다.
- 만족 기준: 만족 리뷰는 20개 [m:std.stability.pos]라 균형 자세에서 늘어나거나 출렁이지 않는 수준을 기준으로 두고, 부정이 가장 적은 상품은 Gaiam 0.2% [m:std.stability.best](Gaiam Classic)다.
- 개발 기준: 늘어남은 ASTM D412 인장 성질 [r:tst_02]로 재질을 비교하고, 두껍거나 푹신해서 균형이 어려움 22개 [m:std.stability.label.thick_hard_to_balance]는 선호 차이라 두꺼운 단계의 상세에 균형 자세에는 얇은 단계를 권하는 안내를 둔다(목표 값은 확인 필요).
- 상세페이지 문구: "Stays firm and flat in balance poses" (균형 자세에서도 늘어나지 않고 평평함), 인장 시험 뒤에만.

#### 기준 5: 냄새(원인 13, 14, 15 대응)
- 감점 기준: 냄새 불만 가중 7.7% [m:std.odor.neg_pct], 그중 화학이나 플라스틱 냄새 145개 [m:std.odor.label.chemical_smell]가 가장 많다.
- 만족 기준: 냄새 만족 리뷰 73개 [m:std.odor.pos]처럼 꺼내자마자 냄새가 적거나 금방 빠지는 수준이고, 부정이 가장 적은 상품은 CAP 2.6% [m:std.odor.best]다.
- 개발 기준: 출하 검품에 냄새 확인을 넣고 [r:tst_15], 실내 화학물질 방출은 UL 2818 같은 기준의 GREENGUARD [r:tst_11]나 CDPH 방출 시험까지 요구하는 GREENGUARD Gold [r:tst_12]를 검토한다. 리뷰어가 말한 냄새가 간 날 중앙값은 7일 [m:f.odor.odor_duration_days.median]이라 출고 전 바람 쐬기 기간은 확인 필요.
- 상세페이지 문구: "Low odor out of the box, certified for low chemical emissions" (꺼내자마자 냄새가 적음, 화학물질 방출 인증), 인증 뒤에만.

#### 기준 6: 성분과 안전(03 원인 밖)
- 감점 기준: 안전 불만 가중 1.4% [m:std.safety.neg_pct], 그중 발암 경고나 유해 성분 표시 22개 [m:std.safety.label.cancer_warning]가 가장 많다.
- 만족 기준: 긍정 리뷰는 0개 [m:std.safety.pos]라 몸 반응과 성분 걱정이 나오지 않는 수준을 기준으로 두고, 부정이 가장 적은 상품은 Gaiam 0.6% [m:std.safety.best](Gaiam Essentials)다.
- 개발 기준: 성분은 OEKO-TEX STANDARD 100처럼 물질 목록으로 시험하는 인증 [r:tst_09]을 검토하고(Manduka PRO가 이 인증을 밝힘 [r:tst_10]), Proposition 65 경고가 필요하면 정해진 문장 형식 [r:reg_09]을 따른다. 근거 없이 무독성(non-toxic)이라 쓰면 기만으로 본다 [r:reg_11]. 천연 고무를 쓰면 라텍스 단백질을 ASTM D6499로 재되 알레르기 척도는 아니다 [r:tst_03].
- 상세페이지 문구: "Third-party tested for harmful substances" (유해 물질 제3자 시험), 시험 통과 뒤에만이고 "non-toxic"은 쓰지 않는다.

#### 기준 7: 크기, 무게, 휴대(03 원인 밖)
- 감점 기준: 크기와 휴대 불만 가중 6.7% [m:std.size.neg_pct], 그중 말면 부피가 커서 들고 다니기나 보관이 어려움 47개 [m:std.size.label.bulky_to_carry_store]가 가장 많다.
- 만족 기준: 크기와 휴대 만족 리뷰 127개 [m:std.size.pos]처럼 몸에 맞는 길이에 들고 다니기 쉬운 수준이고, 부정이 가장 적은 상품은 Gaiam 0.5% [m:std.size.best](Gaiam Classic)다.
- 개발 기준: 폭이 좁음 34개 [m:std.size.label.too_narrow], 길이가 짧음 29개 [m:std.size.label.too_short]라 기본 판 밖에 긴 판이나 넓은 판을 두고(JadeYoga Harmony는 두 길이로 판다 [r:ind_14]), 두꺼운 단계의 무게와 말았을 때 지름 목표는 확인 필요.
- 상세페이지 문구: "Extra-long and extra-wide sizes available" (더 긴 판과 더 넓은 판 있음).

#### 기준 8: 끈과 구성품(03 원인 밖)
- 감점 기준: 끈과 구성품 불만 가중 4.8% [m:std.strap.neg_pct], 그중 들어 있어야 할 끈이 빠져 옴 131개 [m:std.strap.label.strap_missing]가 가장 많다.
- 만족 기준: 끈 만족 리뷰 42개 [m:std.strap.pos]처럼 상세에 적힌 끈이 그대로 오고 쓸 만한 수준이고, 부정이 가장 적은 상품은 Gaiam 1.8% [m:std.strap.best](Gaiam Dry-Grip)다.
- 개발 기준: CAP처럼 끈을 넣는 구성으로 내고 [r:ind_18], 끈이 늘어나 매트가 빠짐 24개 [m:std.strap.label.strap_loose_slips]라 조임 방식을 고른다. 출하 때 끈이 들어 있는지 확인하는 포장 검품 방법은 확인 필요(조사 근거 없음).
- 상세페이지 문구: "Carrying strap included in every box" (모든 상자에 휴대 끈 포함).

#### 기준 9: 묻어남과 표면 마감(원인 5 대응)
- 감점 기준: 묻어남 불만 가중 0.9% [m:std.residue.neg_pct], 그중 색이 묻어나 얼룩 30개 [m:std.residue.label.color_rubs_off]가 가장 많다.
- 만족 기준: 긍정 리뷰는 0개 [m:std.residue.pos]라 손, 옷, 바닥에 색이나 가루가 묻지 않는 수준을 기준으로 두고, 부정이 가장 적은 상품은 CAP 0.0% [m:std.residue.best]다.
- 개발 기준: 색 묻어남은 AATCC TM8 마찰 견뢰도 [r:tst_08]로 보되 원래 직물용이라 매트에 맞는지는 확인 필요이고, 가루나 조각이 떨어져 묻음 21개 [m:std.residue.label.flakes_residue_shed]는 찢어짐과 내구성 기준의 겉층 재질 시험과 함께 본다.
- 상세페이지 문구: "Color-safe surface that won't rub off on hands or floors" (손이나 바닥에 색이 묻어나지 않는 겉면), 시험 통과 뒤에만.

#### 기준 10: 설명과 실물(03 원인 밖)
- 감점 기준: 설명과 실물 불만 가중 2.3% [m:std.listing.neg_pct], 그중 설명에 있던 끈이 안 옴 41개 [m:std.listing.label.strap_missing_vs_listing]가 가장 많다.
- 만족 기준: 만족 리뷰 36개 [m:std.listing.pos]처럼 사진과 표기대로 오는 수준이고, 부정이 가장 적은 상품은 Gaiam 0.8% [m:std.listing.best](Gaiam Classic)다.
- 개발 기준: 표기보다 얇음 39개 [m:std.listing.label.thinner_than_listed]라 두께는 잰 값으로 적고(측정 방법은 확인 필요), 미끄럼 방지 설명이 틀림 14개 [m:std.listing.label.nonslip_claim_false]라 미끄럼 방지 표시는 미끄럼 저항 시험 [r:tst_14] 뒤에만 쓴다.
- 상세페이지 문구: "Thickness measured and printed on the box" (두께를 재서 상자에 표기).

#### 기준 11: 가격 대비 가치(03 원인 밖)
- 감점 기준: 가치 불만 가중 1.7% [m:std.value.neg_pct], 그중 값어치를 못 함, 너무 비쌈 62개 [m:std.value.label.not_worth_price]가 가장 많다.
- 만족 기준: 가치 만족 리뷰 138개 [m:std.value.pos]처럼 값에 비해 좋다는 수준이고, 부정이 가장 적은 상품은 Gaiam 0.3% [m:std.value.best](Gaiam Premium)다.
- 개발 기준: 값에 비해 금방 상함 14개 [m:std.value.label.doesnt_last_for_price]라 가격은 찢어짐과 내구성 기준의 시험 결과와 함께 정하고, 보증은 Manduka PRO Lite [r:ind_06]와 Gorilla Mats [r:ind_19]의 보증을 참고해 조건을 정한다(보증 기간은 확인 필요).
- 상세페이지 문구: "Built to last, backed by a replacement warranty" (오래 쓰도록 만들고 교환 보증), 보증 조건을 정한 뒤에만.

### 하위 카테고리별 출시 계획
- **첫 출시, Yoga Mats 노드의 요가 매트**: 조사 상품이 모두 Yoga Mats 노드에 있고, 이 노드의 월 매출 칸은 9,116,723(월 매출 칸, 통화 미확인) [m:head.market_month], 1위 Gaiam 17.7% [m:m.top1_YM](매출 점유율)이다.
- **첫 상품의 두께**: 얇은 Gaiam Classic과 Gaiam Premium은 얇다는 쪽, 두꺼운 Retrospec Solana는 두껍다는 쪽 불만이 많지만, 상품이 적고 방향이 상품마다 달라 두께와 불만 방향을 원인으로 잇지 않는다. 주력 두께는 얇은 단계와 그 위 단계를 두고 착용 시험으로 정한다(확인 필요). Retrospec의 0.5인치 모델 [r:ind_12]은 비교 대상으로만 둔다.
- **첫 상품의 검색어**: 빠르게 크는 "yoga mat non slip"을 노린다. "yoga mat non slip" 최근 4주 117,775, 1년 전 같은 4주 62,273, 1.89배 [m:head.fastest_term].
- **다음 출시, Exercise Mats 노드의 두꺼운 운동 매트**: 1위 BalanceFrom 13.9% [m:m.top1_EM](매출 점유율)인 노드이고, 일반 운동, 바닥 운동, 홈트를 말한 리뷰가 117개 [m:f.thickness.activity.floor_exercise_workout]다. Retrospec은 가장 두꺼운 매트를 관절 통증이 있는 사람에게 권하므로 [r:ind_13], 두꺼운 단계는 요가보다 바닥 운동과 관절 보호용으로 안내하고 첫 상품의 내구성 결과를 본 뒤 연다.
- **미루는 자리, 여행용 얇은 매트**: Manduka PRO Travel [r:ind_03]과 Gaiam 접이식 매트 [r:ind_08]가 있는 자리이고, 너무 얇음 쪽 불만이 많아 첫 상품 뒤로 미룬다.
- **내지 않는 자리, 어린이용 매트**: Gaiam이 어린이용 매트를 팔지만 [r:ind_09], 어린이 제품 규제 근거를 이번 조사에서 확인하지 못해 내지 않는다(확인 필요).

### 가격 구조
- **읽는 법**: 묶음 값은 상품 한 개의 개당 가격이고, 묶음마다 상품이 2개 [m:price.band0.n]뿐이라 가격과 불만은 나란히만 읽는다. 시장 가격대 표는 브랜드 평균 가격으로 나눈 구간이라 단품 가격과 기준이 다르다.
- **낮음 묶음(Gaiam Classic, Gaiam Premium)**: 21.55~22.64달러/개 [m:price.band0.range], 두께와 쿠션 부정 8.7% [m:price.band0.skin_neg]로 세 묶음 가운데 가장 높다.
- **낮음 묶음의 내구성과 별점**: 만듦새와 내구성 부정 2.7% [m:price.band0.eff_neg], 별점 4.60★ [m:price.band0.star]이다.
- **중간 묶음(CAP Extra Thick, Gaiam Essentials)**: 22.67~24.46달러/개 [m:price.band1.range], 두께와 쿠션 부정 1.1% [m:price.band1.skin_neg]로 세 묶음 가운데 가장 낮다.
- **중간 묶음의 내구성과 별점**: 만듦새와 내구성 부정 7.7% [m:price.band1.eff_neg], 별점 4.61★ [m:price.band1.star]이다.
- **높음 묶음(Retrospec Solana, Gaiam Dry-Grip)**: 39.99~48.98달러/개 [m:price.band2.range], 만듦새와 내구성 부정 12.0% [m:price.band2.eff_neg]로 세 묶음 가운데 가장 높다.
- **높음 묶음의 별점**: 4.38★ [m:price.band2.star]로 세 묶음 가운데 가장 낮고, 이 묶음에 만듦새와 내구성 부정이 가장 높은 Gaiam Dry-Grip 16.4% [m:s.B0BYFLL1LV.topic_neg]가 들어 있다(상품이 둘뿐이라 가격 탓으로 읽지 않음).
- **시장 가격대**: 가장 낮은 구간 20.68~41.93 [m:m.price_band1_range]의 매출 비중이 56.1% [m:m.price_band1_share]로 세 구간 가운데 가장 크다.
- **시장 위 구간**: 가운데 구간 매출 비중 20.3% [m:m.price_band2_share], 가장 높은 구간 23.6% [m:m.price_band3_share]이다.
- **상위 브랜드(Yoga Mats 4위) Manduka의 가격 단계**: Manduka는 PRO 정가 144달러 [r:ind_02]와 입문용 begin 정가 62달러 [r:ind_05]로 단계를 나눈다.
- **권고 가격대(확인 필요)**: 첫 상품은 시장의 가장 낮은 구간 20.68~41.93 [m:m.price_band1_range] 안에 둔다. 높음 묶음의 값대로 올리려면 찢어짐과 내구성 기준의 시험 결과를 먼저 갖춘다.

### 메시지와 키워드
- **썸네일**: "Tear-tested surface" (찢김 시험을 거친 겉면)와 "Grips when you sweat" (땀이 나도 미끄럽지 않음) 두 줄에 두께 단계 표시, 찢김과 미끄럼 시험 통과 뒤에만.
- **상세**: 단계마다 잰 두께와 맞는 운동, 겉층 재질과 시험 이름 [r:tst_01], 처음 냄새를 빼는 법, 끈 포함 사진, Proposition 65 경고가 필요하면 정해진 문장 [r:reg_09]을 적고, 근거 없는 "non-toxic"은 쓰지 않는다 [r:reg_11].
- **박스 안**: 끈이 들어 있는지 확인한 검품 표, 처음 바람 쐬기와 세척 방법, 보증과 연락처를 적은 안내지를 넣는다(보증 조건은 확인 필요).
- **키워드**: yoga mat, yoga mat non slip, non slip yoga mat, thick yoga mat, extra thick yoga mat, hot yoga mat.

### 실행 순서
1. **P1 겉층과 몸체 재질 선택**: ASTM D624 찢김 강도 [r:tst_01]와 ASTM D412 인장 성질 [r:tst_02]로 후보 재질을 비교한다.
2. **P1 두께 단계 결정**: 얇은 단계와 그 위 단계를 정하고 Retrospec의 두께 구성 [r:ind_12]과 나란히 놓는다. 꺼짐 회복 시험은 확인 필요(조사 근거 없음).
3. **P1 땀 조건 그립 시험**: 마른 상태와 젖은 상태에서 미끄럼 저항 시험 [r:tst_14]을 하고 아랫면 밀림도 본다.
4. **P1 냄새와 방출 확인**: 출하 냄새 확인 [r:tst_15]을 넣고 GREENGUARD Gold [r:tst_12]를 검토한다.
5. **P1 성분 시험과 표시 문구**: OEKO-TEX STANDARD 100 [r:tst_09]을 검토하고, Proposition 65 경고 필요 여부 판단과 정해진 문장 [r:reg_09], 근거 없는 무독성 표시 금지 [r:reg_11]를 상세 문구에 반영한다.
6. **P1 끈 포함과 두께 표기 검품**: 끈을 넣는 구성 [r:ind_18]으로 내고, 끈이 들어 있는지와 잰 두께가 표기와 맞는지 출하 때 확인한다(검품 방법은 확인 필요).
7. **P2 색 묻어남 시험**: AATCC TM8 [r:tst_08]을 매트 겉면에 맞게 쓸 수 있는지 확인한다.
8. **P2 긴 판과 넓은 판**: JadeYoga Harmony처럼 길이를 나눈 판 [r:ind_14]을 검토한다.
9. **P2 보증 조건**: Manduka PRO Lite [r:ind_06]와 Gorilla Mats [r:ind_19]의 보증을 참고해 정한다.
10. **P2 두꺼운 운동 매트 단계**: Exercise Mats 노드용 두꺼운 단계를 첫 상품의 내구성 결과를 본 뒤 낸다(확인 필요).

### 개발 단계와 관문
- **재질 관문**: 찢김 강도 [r:tst_01]와 인장 성질 [r:tst_02]이 비교 매트보다 나아야 하고, 리뷰어가 말한 손상까지 걸린 날 중앙값 75일 [m:f.durability.durability_elapsed_days.median]을 넘는 사용 시험을 거친다(목표 값은 확인 필요).
- **두께와 쿠션 관문**: 단계마다 잰 두께가 표기와 맞아야 한다. 무릎이 아프다는 리뷰 가운데 너무 얇음 라벨이 함께 나온 비율은 28개 중 12개(42.9%) [m:f.thickness.body_part_effect.knees_hurt.too_thin]이라 무릎 자세 착용 시험을 넣는다(꺼짐 회복 기준은 확인 필요).
- **그립 관문**: 땀 조건 미끄럼 저항 시험 [r:tst_14]을 통과해야 미끄럼 방지 문구를 쓴다(목표 마찰 값은 확인 필요).
- **냄새와 성분 관문**: 출하 냄새 확인 [r:tst_15], 방출 인증 [r:tst_12], 성분 인증 [r:tst_09]의 결과로 상세 문구를 정하고, Proposition 65 경고가 필요하면 정해진 문장 [r:reg_09]을 붙인다.
- **포장과 표기 관문**: 끈이 들어 있는지와 두께 표기를 출하 때 확인한다. 표기보다 얇음 리뷰가 39개 [m:std.listing.label.thinner_than_listed]다(검품 방법은 확인 필요).

### 결론
- **무엇을**: 찢김 시험을 거친 겉층, 땀에도 미끄럽지 않은 그립, 두께 단계를 갖춘 요가 매트.
- **누구에게**: 집과 스튜디오에서 요가를 하는 사람(요가를 말한 리뷰 232개 [m:f.thickness.activity.yoga]).
- **얼마에**: 시장의 가장 낮은 구간 20.68~41.93 [m:m.price_band1_range] 안(확인 필요).
- **무엇으로 이기는지**: 불만 1위 만듦새와 내구성 8.6% [m:head.topic_neg]를 시험으로 줄이고, 끈을 빠짐없이 넣고 두께를 잰 값대로 적는 것.

## 05 한 장 요약
### 제품 해부도
1. **겉층(윗면)**: 찢김 강도 ASTM D624 [r:tst_01]로 비교해 고른 겉층, 몇 달 사용 시험으로 확인한 접착 (찢어짐이나 구멍 122개 [m:std.durability.label.tears_holes], 윗면이 벗겨지거나 기포가 생김 95개 [m:std.durability.label.surface_peels_bubbles])
2. **윗면 질감과 아랫면**: 마른 상태와 젖은 상태에서 잰 미끄럼 저항 [r:tst_14](검품 업체 기준, 공인 표준 아님)과 바닥에서 밀리지 않는 아랫면 질감 (손발이 표면에서 미끄러짐 187개 [m:std.grip.label.surface_slippery], 매트가 바닥에서 밀림 65개 [m:std.grip.label.slides_on_floor])
3. **몸체 두께 단계**: 얇은 단계와 그 위 단계로 나누고 단계마다 맞는 운동을 적음, Retrospec의 두께 구성 [r:ind_12]과 나란히 놓음 (너무 얇음 113개 [m:std.thickness.label.too_thin], 너무 두껍거나 물렁함 44개 [m:std.thickness.label.too_thick_soft])
4. **몸체 탄성과 늘어남**: 인장 성질 ASTM D412 [r:tst_02]로 재질을 비교하고, 눌림 뒤 복원 시험은 확인 필요(조사 근거 없음) (매트가 늘어남 32개 [m:std.stability.label.stretches_out], 쓰다 보니 꺼짐 11개 [m:std.thickness.label.flattens_over_time])
5. **재질 성분과 표시**: OEKO-TEX STANDARD 100처럼 물질 목록으로 시험하는 인증 [r:tst_09]을 검토하고, Proposition 65 경고가 필요하면 정해진 문장 [r:reg_09]을 붙이며, 근거 없는 "non-toxic" 표시는 쓰지 않음 [r:reg_11] (발암 경고나 유해 성분 표시 22개 [m:std.safety.label.cancer_warning])
6. **냄새와 방출**: 출하 냄새 확인 [r:tst_15]과 GREENGUARD Gold [r:tst_12] 검토, 상자 안에 처음 바람 쐬기 안내 (화학이나 플라스틱 냄새 145개 [m:std.odor.label.chemical_smell], 바람을 쐬거나 씻어도 안 빠짐 60개 [m:std.odor.label.smell_persists])
7. **색과 인쇄 마감**: AATCC TM8 [r:tst_08]을 매트 겉면에 쓸 수 있는지 확인한 뒤 색 묻어남 시험 (색이 묻어나 얼룩 30개 [m:std.residue.label.color_rubs_off], 가루나 조각이 떨어져 묻음 21개 [m:std.residue.label.flakes_residue_shed])
8. **끈, 길이, 표기**: 모든 상자에 끈을 넣는 구성 [r:ind_18], JadeYoga Harmony처럼 길이를 나눈 판 [r:ind_14] 검토, 잰 두께를 상자에 표기 (들어 있어야 할 끈이 빠져 옴 131개 [m:std.strap.label.strap_missing], 표기보다 얇음 39개 [m:std.listing.label.thinner_than_listed])

### 단계와 관문
- **재질과 내구성**: P1 한 건(겉층과 몸체 재질 선택), 관문은 찢김 강도 [r:tst_01]와 인장 성질 [r:tst_02] 비교와 리뷰어가 말한 손상까지 걸린 날 중앙값 75일 [m:f.durability.durability_elapsed_days.median]을 넘는 사용 시험(목표 값은 확인 필요)
- **두께와 쿠션**: P1 한 건(두께 단계 결정), 관문은 단계마다 잰 두께와 표기의 일치, 무릎 자세 착용 시험 (무릎이 아프다는 리뷰 가운데 너무 얇음 라벨이 함께 나온 비율 28개 중 12개(42.9%) [m:f.thickness.body_part_effect.knees_hurt.too_thin])
- **그립**: P1 한 건(땀 조건 그립 시험), 관문은 젖은 상태 미끄럼 저항 시험 [r:tst_14] 통과 뒤에만 미끄럼 방지 문구 (땀이나 물기가 있을 때 그립을 말한 리뷰 110개 [m:f.grip.grip_condition.sweat_moisture])
- **냄새와 성분**: P1 두 건(냄새와 방출 확인, 성분 시험과 표시 문구), 관문은 출하 냄새 확인 [r:tst_15], 방출 인증 [r:tst_12], 성분 인증 [r:tst_09]의 결과와 Proposition 65 정해진 문장 [r:reg_09] (냄새 불만 가중 7.7% [m:std.odor.neg_pct])
- **포장과 표기**: P1 한 건(끈 포함과 두께 표기 검품), 관문은 출하 때 끈이 들어 있는지와 잰 두께가 표기와 맞는지 확인(검품 방법은 확인 필요) (들어 있어야 할 끈이 빠져 옴 131개 [m:std.strap.label.strap_missing])
- **출시 뒤 개선**: P2 네 건(색 묻어남 시험 [r:tst_08], 길이를 나눈 판 [r:ind_14], 보증 조건 [r:ind_06], 두꺼운 운동 매트 단계), 두꺼운 단계는 첫 상품의 내구성 결과를 본 뒤 연다(확인 필요)

## A 데이터와 방법
### 출처
- 리뷰, 태그, 세부 이슈 라벨, 설계 정보, 시장 데이터, 웹 조사, 상품 사양의 파일과 건수는 아래 표에 있다.
- 웹 조사 주장은 66개 중 40개 [m:a.research_verified]를 다시 열어 원문 문장을 확인했고, 확인된 주장만 썼다.
- 확인되지 않은 주장(Global Growth Insights와 Fortune Business Insights의 시장 규모와 북미 비중, 미국 단독 시장 금액, CPSC 어린이 제품과 프탈레이트와 납 규정, Proposition 65 프탈레이트 안내서와 짧은 경고 형식, FTC Green Guides 안내와 Made in USA 안내, PFA 폼 시험 안내, BIS 면 요가 매트 표준, Academy 판매 페이지의 Gaiam Premium 사양과 성분 표시, Liforme 가격)은 쓰지 않았다.
- 시장 데이터는 spd-amz-market 응답이다. Yoga Mats와 Exercise Mats 두 노드의 브랜드 점유율은 응답 값으로 매출 점유율임을 확인했고, 매출 칸은 통화가 확인되지 않았다.
- 상품 사양은 브랜드 공식 사이트와 소매점 상품 페이지에서 다시 열어 확인한 값만 썼다. 같은 상품인지 확인한 정도는 이름만 일치 1개, 일치 확인 4개, 찾지 못함 1개 [m:spec.match_summary]다.
- 태깅 정확도는 정답 세트 기준 주제 F1 0.87 [m:acc.topic_f1], 감성 방향 일치 98.6% [m:acc.direction](mixed가 아닌 짝 기준)이다.
- mixed 일치는 43.8% [m:acc.mixed], 감성 전체 일치는 88.9% [m:acc.sentiment]이다.
- 방향 지수는 너무 얇음 쪽 라벨 리뷰에서 너무 두껍거나 푹신함 쪽 라벨 리뷰를 뺀 값을 두 쪽의 합으로 나눈 값이고, 방향 라벨 리뷰가 기준 수보다 적은 상품은 비운다.
- 03장 원인 번호는 집중 분석의 부정 라벨을 기준마다 설계 결함과 선호 차이로 나누고 리뷰 많은 순으로 묶은 분류이고, 인과가 아니다.

### 견고성 점검
- 리뷰를 2,000번 [m:a.robust.n] 다시 뽑으면 만듦새와 내구성이 불만 1위로 남은 비율은 99.4% [m:a.robust.head_first]다.
- 만듦새와 내구성 부정 언급 리뷰어 비율의 다시 뽑기 구간은 7.5%~9.8% [m:a.robust.head_neg_ci]이다.
- 가장 큰 약점이 만듦새와 내구성인 상품 수는 6개 중 1개(리뷰를 다시 뽑아 보면 1~3개) [m:a.robust.weakest]이다. 다시 뽑기 분포(표)에서는 한 개보다 많이 나오는 경우가 흔해, 이 상품 수는 확정 값으로 읽지 않는다.
- 상품을 하나씩 빼면 결론이 달라진 경우는 6번 중 1번 [m:a.robust.loo_flips]이다. Gaiam Dry-Grip을 빼면 만듦새와 내구성이 5.9% [m:a.robust.B0BYFLL1LV.head_neg]로 내려가 끈과 휴대 구성품이 불만 1위가 된다.
- 하나씩 뺐을 때 만듦새와 내구성 부정 비율의 범위는 5.9%~9.5% [m:a.robust.loo_head_neg]이다.
- 너무 두껍거나 푹신함 쪽 비율은 상품을 하나씩 빼면 4.3%~29.3% [m:a.robust.loo_low_share]로 움직인다.
- Retrospec Solana를 빼면 그 비율이 4.3% [m:a.robust.B092XTMNCC.low_share]로 가장 낮아져, 너무 두껍거나 푹신함 쪽 불만은 이 한 상품에 많이 모여 있다.
- Gaiam Essentials나 Retrospec Solana를 빼면 불만 지도 상위 주제의 순서가 바뀐다(표).

### 주의 사항
- 리뷰는 공유 리뷰 DB 표본이라 낮은 별점이 실제보다 많고, 비율은 별점 묶음 가중으로 되돌렸다(리뷰 수, 표본 평균과 가중 평균 별점은 원문 목록).
- 자유 서술에서 뽑은 수치(손상까지 걸린 날, 냄새가 간 날, 말한 두께)는 리뷰어가 적은 값이라 측정값이 아니고 방향과 분포로만 읽는다.
- 개발 기준의 사양 숫자는 웹 조사 출처를 근거로 한 시작점이고 시험으로 확인해야 한다.
- 조사 상품이 적고 모두 한 하위 카테고리(Yoga Mats)라 상품끼리, 하위 카테고리끼리의 비교가 약하다. 상품 사양과 불만은 원인으로 잇지 않고 나란히만 놓았다.
- 시장 데이터(spd-amz-market)의 매출, 증감, 승률 칸은 문서에 단위가 없어 단위 미확인으로 적었다. 브랜드 점유율은 두 노드 모두 응답 값으로 매출 점유율임을 확인했다.
- 연 환산 109,400,681(가정: 통화 미확인 월 매출 x 12, 계절 변동 미반영) [m:head.market_year]은 가정이라 SAM 확정 값이나 머리 숫자로 쓰지 않는다.
- 시장 가격대 표는 브랜드 평균 가격으로 나눈 구간이라 단품 가격(점수표의 개당 가격)과 기준이 다르다.
- 성장 배수는 검색량 기준을 넘은 카테고리 검색어 가운데 두 기간 주간 이력을 받은 검색어에서만 골랐고, 나머지는 이력이 없어 순위에서 빠졌다. 시장 데이터의 전년 대비 증감 칸은 뜻과 단위가 확인되지 않아 머리 숫자에 쓰지 않는다.
- 공통 검색어 합에는 play mat, gymnastics mat처럼 요가 매트가 아닌 검색어도 들어 있다.
- 상품은 카테고리 검색어의 매출 상위 후보 가운데 골랐고(상품 확인 관문에서 사람이 확인), DB 리뷰 수 순으로 고른 뒤 리뷰가 모자란 상품은 담당자 승인 상한 안에서 유료 수집한 리뷰를 더했다.
- 사양이 이름만 일치한 상품(Gaiam Essentials)은 공식 페이지 이름 기준이고, 같은 상품 페이지를 찾지 못한 상품(Gaiam Dry-Grip)은 사양 칸이 비어 있다.
- 방향 지수는 방향 라벨 리뷰가 기준 수보다 적은 상품(Gaiam Essentials, CAP Extra Thick)에서 비어 있다.
- 03장 원인 번호와 별점 격차는 함께 나온 값의 분류와 비교라 원인으로 읽지 않는다.
