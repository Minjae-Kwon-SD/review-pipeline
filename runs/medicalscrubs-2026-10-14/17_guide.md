# 아마존 미국 의료용 스크럽 제품 개발 가이드
> 새로 들어오는 브랜드를 위한 기준: 상하의 사이즈를 따로 고르고 키에 맞춰 기장을 고르는 스트레치 여성 세트

## 머리 숫자
- [head.topic_neg] 사이즈와 핏을 부정으로 말한 리뷰어 비율(별점 가중), 2위 원단과 착용감 7.5% [m:p.map.fabric_comfort]보다 훨씬 커 첫 개발 관문의 기준값
- [head.topic_weakest] 가장 큰 약점이 사이즈와 핏인 상품 수, 나머지 한 상품(COZY SCRUBS)의 가장 큰 약점은 원단과 착용감
- [head.dir_ratio] 크게 나온다와 작게 나온다는 라벨 리뷰 수가 거의 같아 한쪽으로 고칠 문제가 아니라 상품마다 치수 체계를 맞출 문제, 가중하면 크게 나옴 쪽 9.9% [m:head.dir_low_w]가 조금 더 흔함
- [m.top10_share_WSET] 여성 스크럽 세트 노드의 상위 10개 브랜드 점유율 합(단위 미확인 값을 %로 읽음), 1위는 CozyFit 29.4% [m:m.top1_WSET]
- [head.market_month] 여성 의료 유니폼과 스크럽 노드의 월 매출 칸, 달러로 읽으면 236,216,370(월 매출을 달러로 읽을 때 연 환산) [m:head.market_year]

## 01 시장 개요
**TL;DR** 의료용 스크럽은 이미 넓게 찾는 범주이고(여성 검색어 검색량 합 1,725,127 [m:m.terms_female_volume]), 여성 세트 노드는 상위 10개 브랜드가 84.0% [m:m.top10_share_WSET]를 차지한다. 첫 상품은 여성 상하의 세트를 시장 가격 2구간 안에 두고 사이즈 체계로 차별하는 안을 확인이 필요한 권고로 둔다.

### TAM, SAM, SOM
- **TAM(전 세계)**: 의료용 스크럽 세계 시장을 2024년 470억 달러로 보는 보고서 [r:mkt_04]와 2025년 528.8억 달러로 보는 보고서 [r:mkt_11]가 있다.
- **미국 시장, 높게 본 보고서**: 2024년 149.6억 달러 [r:mkt_01]와 128억 달러 [r:mkt_03]로 본다.
- **미국 시장, 낮게 본 보고서**: 2025년 97.8억 달러 [r:mkt_07]와 97.1억 달러 [r:mkt_09]로 보아 범위가 달라 기준값 하나로 정하지 않고 더하거나 곱하지 않는다.
- **성장률**: 미국 시장 보고서마다 연평균 6.5% [r:mkt_06]에서 9.12% [r:mkt_02]까지 갈린다.
- **대형 브랜드 기준점**: FIGS의 2025년 스크럽 순매출은 5억 890만 달러로 전년보다 14.3% 늘었다 [r:mkt_13].
- **SAM(아마존 미국 노드)**: Women's Medical Uniforms & Scrubs는 19,684,698(월 매출 칸, 단위 미확인) [m:head.market_month], 236,216,370(월 매출을 달러로 읽을 때 연 환산) [m:head.market_year]이다.
- **SOM(확인 필요)**: 여성 세트 노드 상위 10개 브랜드 몫 84.0% [m:m.top10_share_WSET] 밖에서 시작하고, 목표 금액은 매출 칸 단위를 확인한 뒤 정한다.

### 판정 3개
- **침투: 이미 넓게 찾는 범주**: 여성 검색어 39개 [m:m.terms_female_n]의 한 달 검색량 합이 1,725,127 [m:m.terms_female_volume]으로, 새 범주를 알리는 일보다 이미 찾는 사람에게 고르게 하는 일이 과제다.
- **경쟁 집중: 세트는 아마존 세트 브랜드 중심**: 여성 세트 노드 상위 10개 브랜드 점유율 합 84.0% [m:m.top10_share_WSET], 1위 CozyFit 29.4% [m:m.top1_WSET]이다(점유율 칸은 단위 미확인 값을 %로 읽음).
- **기회: 싼 값이 아닌 사이즈 체계와 대체 수요**: 시장 가격 1구간의 매출 비중은 17.0% [m:m.price_band1_share]로 작아 싼 값만으로 들어갈 자리는 아니고, FIGS 같은 원조 브랜드의 대체품으로 샀다는 리뷰가 25개 [m:f.design_value.comparison_reference.dupe_target] 있다. 빠르게 크는 검색어는 이력이 없어 판단하지 않는다.

상의와 바지 노드는 의료복 브랜드가 1위다: 상의 CHEROKEE 18.9% [m:m.top1_WTOP], 바지 CHEROKEE 25.1% [m:m.top1_WPANT].

남성 세트 노드는 상위 10개 합 98.8% [m:m.top10_share_MSET], 1위 CozyFit 60.6% [m:m.top1_MSET]로 더 몰려 있다.

### 검색 수요
- 여성 검색어 39개 [m:m.terms_female_n]와 공통 검색어 62개 [m:m.terms_common_n]가 대부분이다.
- 여성 검색어는 속에 입는 옷 검색어(underscrub long sleeve women)를 빼면 scrubs for women, figs scrubs women, scrubs for women set 순으로 앞서고, figs, fabletics, cherokee, healing hands처럼 브랜드 이름이 든 검색어가 많다.
- 공통 검색어의 검색량 합은 1,760,812 [m:m.terms_common_volume]이고, nurse costume(의상)과 underscrubs(속에 입는 옷)는 이 가이드의 범위 밖이다.
- 남성 검색어는 3개 [m:m.terms_male_n], 검색량 합 58,995 [m:m.terms_male_volume]이다.
- 성장 배수는 후보 검색어 206개 [m:m.growth_candidates] 가운데 주간 이력을 받은 검색어가 0개 [m:m.growth_ranked]라 말하지 않는다.

### 진입 조건
- **부위(구성)**: 상의와 바지 세트를 기본으로 하되 상하의 사이즈를 따로 고르게 한다. 상하의 사이즈가 서로 다르다는 리뷰 135개 [m:std.sizing.label.top_bottom_mismatch], 따로 고르기를 바란 리뷰 38개 [m:f.design_value.desired_feature.separate_top_bottom_sizes]이고, 검색어도 scrubs for women set이 앞선다.
- **성별**: 여성 먼저, 남성 세트는 다음 차례. 여성 검색어 검색량 합 1,725,127 [m:m.terms_female_volume]이 남성 58,995 [m:m.terms_male_volume]보다 크다.
- **사이즈와 기장 체계**: XXS부터 큰 사이즈까지에 키 기준 쁘띠, 레귤러, 톨 기장(경쟁 라인 사례 [r:ind_02]). 기장이 길거나 짧다는 리뷰 215개 [m:std.sizing.label.length_off], 리뷰어가 적은 키 중앙값 65inch [m:f.fit.reviewer_height.median]다.
- **가격대(확인 필요)**: 세트는 시장 가격 2구간 24.95~29.98 [m:m.price_band2_range] 안(가격 구조 절).
- **형태**: four-way stretch 원단의 V넥 상의와 바지 세트. 신축성 있음 9.3% [m:f.fabric.fabric_property.stretchy.w]이 신축성 없음 2.9% [m:f.fabric.fabric_property.no_stretch.w]보다 흔하고, 조거와 스트레이트 가운데 무엇을 먼저 낼지는 리뷰가 나누어 말하지 않아 확인 필요.

## 02 경쟁사
**TL;DR** 조사 상품은 대부분 여성 세트이고 Cherokee 상의 하나와 COZYFIT 남성 세트 둘이 섞였다. 가장 큰 약점이 사이즈와 핏인 상품이 10개 중 9개(리뷰를 다시 뽑아 보면 9~10개) [m:head.topic_weakest]이고, 크게 나오는 상품과 작게 나오는 상품이 함께 있어 한 방향의 사이즈 안내로는 풀리지 않는다.

### 점수표 해설
- **사이즈와 핏 부정 최고**: Dagacci 세트 49.2% [m:s.B00FT74D3E.topic_neg]이고 방향 지수 -0.60 [m:s.B00FT74D3E.dir_index]으로 크게 나옴 쪽이다.
- **크게 나오는 쪽**: Cherokee 상의도 방향 지수 -0.64 [m:s.B072R1F3TW.dir_index]로 크게 나옴 쪽이지만 사이즈와 핏 부정은 19.8% [m:s.B072R1F3TW.topic_neg]로 낮은 편이다.
- **작게 나오는 쪽**: floralhue 세트 +0.61 [m:s.B0D8BBZ7XM.dir_index], COZYFIT 여성 조거 세트 +0.39 [m:s.B0CGQZF1YT.dir_index]는 작게 나옴 쪽이다.
- **가중 별점**: Cherokee 상의 4.54★ [m:s.B072R1F3TW.star]가 가장 높고, Dvoliaw 세트 3.98★ [m:s.B0G19YL3Y8.star]가 가장 낮다.
- **입는 사람 키**: COZYFIT 남성 조거 세트는 리뷰어가 적은 키 중앙값 71inch [m:s.B0CGR6639D.duration_median]이고, 여성 세트는 64inch [m:s.B0D8BBZ7XM.duration_median] 안팎이다.
- **사양, 일치 확인 상품(나란히만)**: 이름만 일치 3개, 일치 확인 3개, 찾지 못함 4개 [m:spec.match_summary]로 확인했다. Cherokee 상의(일치 확인 [m:spec.B072R1F3TW.match])는 공식 페이지에 스트레치 트윌과 relaxed fit을, COZYFIT 남성 스트레이트 세트(일치 확인 [m:spec.B0FMDH33NX.match])는 폴리에스터 트윌과 고무줄 끈 허리를 표시한다.
- **사양, 공식 페이지 이름 기준**: Dagacci 세트(이름만 일치 [m:spec.B00FT74D3E.match])는 공식 페이지 이름 기준으로 면 혼방과 classic fit을 표시한다. Dagacci 공식 사이트의 다른 남녀 공용 세트(4-Way Stretch) 페이지는 여성에게 크게 나오니 한 사이즈 작게 사라고 안내한다 [r:ind_21]. 이 상품과 같은 판인지는 확인하지 못했고, 크게 나옴 쪽 방향 지수와 나란히 놓을 뿐 원인으로 잇지 않는다.

### 하위 카테고리 비교
- 조사 상품 대부분이 Women's Medical Scrub Sets 노드에 있고, Cherokee만 Women's Medical Scrub Shirts, COZYFIT 남성 두 세트는 Men's Medical Scrub Sets에 있어 노드끼리의 비교는 약하다.
- 세트 노드는 CozyFit, floralhue, Dagacci, Dvoliaw 같은 아마존 세트 브랜드가 상위이고, 상의와 바지 노드는 CHEROKEE 등 의료복 브랜드가 1위이고 CozyFit도 상위에 있어, 세트와 단품의 경쟁자가 일부 겹친다.
- 상의 노드 상위 10개 합은 77.7% [m:m.top10_share_WTOP], 바지 노드는 80.3% [m:m.top10_share_WPANT]다.

### 업계 구조
- **한 회사의 여러 브랜드**: Careismatic이 Cherokee, Healing Hands, Med Couture, Dickies 의료복을 함께 갖고 [r:ind_07], 저가 Scrubstar는 Walmart에서 판다 [r:ind_08].
- **신축성 표시**: FIGS는 four-way stretch 원단과 항균 가공을 [r:ind_01] [r:ind_03], Cherokee Revolution은 two-way stretch를 [r:ind_04], Barco는 나일론과 스판덱스 원단을 [r:ind_13] 내세운다.
- **기장과 사이즈 체계**: FIGS는 키 기준으로 쁘띠, 레귤러, 톨 기장을 나누고 [r:ind_02], Wink는 넓은 사이즈 범위와 레귤러, 쁘띠, 톨 기장을 표기하고 [r:ind_14], Cherokee는 XXS~6XL을 표기한다 [r:ind_05].
- **색 맞춤과 혼용률**: KOI는 색을 맞추려면 상의와 바지를 같은 컬렉션에서 고르라고 안내하고 [r:ind_12], Med Couture는 단색과 헤더 색의 혼용률이 다르다 [r:ind_11].
- **아마존 세트 브랜드**: CozyFit 자사몰은 정가와 할인가를 함께 적고 [r:ind_19] 발수 원단을 내세우며 [r:ind_20], Wink와 Healing Hands는 발수, 구김 방지, 색 바램 방지를 표시한다 [r:ind_16] [r:ind_10].

## 03 문제
**TL;DR** 불만 1위는 사이즈와 핏 22.1% [m:p.map.fit_sizing]이고 2위 원단과 착용감 7.5% [m:p.map.fabric_comfort]와 차이가 크다. 별점 격차는 브랜드 경험, 신뢰, 가격 대비 가치에서 크고, 집중 분석마다 불만을 원인 번호(설계 결함 또는 선호 차이)로 나눠 기준표와 잇는다.

### 불만 지도
- 사이즈와 핏 22.1% [m:p.map.fit_sizing], 원단과 착용감 7.5% [m:p.map.fabric_comfort]가 앞서 이 둘을 출시 관문으로 둔다.
- 만듦새와 내구성 4.5% [m:p.map.build_quality], 디자인과 색상 3.4% [m:p.map.design_color]가 그 뒤다.
- 브랜드 경험 2.6% [m:p.map.brand_experience]는 재구매와 추천 의향이라 결과 지표로 읽는다.
- 세탁과 관리 2.3% [m:p.map.wash_care], 주머니 2.2% [m:p.map.pockets]는 작지만 고칠 부품이 분명하다.
- 배송 1.8% [m:p.map.shipping]와 신뢰 1.6% [m:p.map.trust]에는 세트 구성과 받은 상품 상태의 불만이 섞여 기준 7로 묶는다.
- 물빠짐과 이염 1.1% [m:p.map.color_fastness], 가격 대비 가치 1.0% [m:p.map.price_value]는 작고, 고객 응대와 포장은 더 작아 개발 기준에서 뺀다.
> "가슴은 아주 꽉 끼는데 다른 곳은 모두 더 헐렁했다" (COZYFIT, 4★, RADE3MW6FRXTY)

### 별점 격차
- **브랜드 경험**: 부정 1.68★ [m:p.gap1_neg], 격차 -2.66 [m:p.gap1]로 가장 크고, 다시 사지 않겠다거나 원래 브랜드로 돌아가겠다는 말이 많다.
- **신뢰**: 부정 1.99★ [m:p.gap2_neg], 격차 -2.31 [m:p.gap2]이고, 인용 후보에는 세트로 알고 샀는데 상의만 왔다는 말이 많다.
- **가격 대비 가치**: 부정 2.10★ [m:p.gap3_neg], 격차 -2.19 [m:p.gap3]이다.
- **읽는 법**: 격차가 큰 주제는 불만 지도에서 작은 주제라, 흔한 불만(사이즈와 핏)과 별점을 크게 깎는 불만(구성과 신뢰)을 따로 관리한다.
> "앞으로는 믿고 입는 FIGS만 살 것이다" (Dvoliaw, 1★, R2S1J7HWUCBD76)
> "허위 광고다" (Dagacci Medical Uniform, 3★, R2TSLYRS64KB5M)

### 집중 분석 1: 사이즈와 핏, 상품마다 반대인 방향
- **표기 대비 크기**: 크게 나옴 7.9% [m:f.fit.size_vs_label.runs_large.w], 작게 나옴 5.4% [m:f.fit.size_vs_label.runs_small.w]로 크게 나온다는 쪽이 조금 더 흔하다.
- **표기대로 맞음**: 11.3% [m:f.fit.size_vs_label.true_to_size.w]로 어느 한 방향보다 흔하다.
- **상의**: 전체가 작거나 조임 2.9% [m:f.fit.fit_part_direction.top_too_tight.w], 크거나 헐렁함 3.1% [m:f.fit.fit_part_direction.top_too_loose.w]로 비슷하다.
- **바지**: 크거나 헐렁함 2.2% [m:f.fit.fit_part_direction.pants_too_loose.w]가 작거나 조임 1.3% [m:f.fit.fit_part_direction.pants_too_tight.w]보다 흔하다.
- **작게 나옴 라벨이 함께 붙은 비율**: 상의 전체가 조인다는 리뷰는 159개 중 70개(44.0%) [m:f.fit.fit_part_direction.top_too_tight.runs_small], 가슴만 조인다는 리뷰는 69개 중 11개(15.9%) [m:f.fit.fit_part_direction.chest_bust_tight.runs_small]다(함께 나온 비율이지 원인이 아님).
- **체형**: 엉덩이나 허벅지가 큰 곡선 체형 1.9% [m:f.fit.body_type.curvy_hips_thighs.w], 키가 크거나 다리가 김 1.3% [m:f.fit.body_type.tall_or_long_legs.w] 순으로 체형을 밝힌 리뷰 가운데 앞서고, 키가 작음이 그 뒤다.
- **주문마다 다름**: 같은 표기 사이즈인데 크기가 다르다는 리뷰 1.9% [m:f.fit.cross_order_variation.size.w]가 있다.
> "같은 사이즈를 샀는데도 훨씬 헐렁하고 크게 맞는다" (Cherokee, 4★, R3VBOBOMBE2I9X)
> "평소 FIGS Rafaela 상의는 XS를 입는데 이건 S인데도 아주 꽉 낀다. 바지는 FIGS와 똑같이 맞는다!" (Dvoliaw, 4★, R2GJM9TXOIMSF5)
> "검정과 회색을 둘 다 M으로 주문했는데 핏이 많이 달랐다" (COZYFIT, 4★, RHB8RARCBZOJX)

**시사점**
- 원인 1(설계 결함), 표기 사이즈와 실제 치수의 어긋남: 작게 나옴 418개 [m:std.sizing.label.runs_small], 크게 나옴 409개 [m:std.sizing.label.runs_large]. 상품마다 방향이 달라 치수 등급과 실측 사이즈표를 맞추면 줄어든다.
- 원인 2(설계 결함), 주문과 색마다 다른 치수: 같은 표기 사이즈인데 크기가 다름 138개 [m:f.fit.cross_order_variation.size]. 생산 묶음마다 치수를 재면 줄어든다.
- 원인 3(선호 차이), 상하의와 부위의 체형 차이: 상하의 사이즈가 서로 다름 135개 [m:std.sizing.label.top_bottom_mismatch], 특정 부위가 조이거나 헐렁함 203개 [m:std.sizing.label.area_fit]. 상하의 따로 고르기와 체형별 안내로 대응한다.
- 원인 4(선호 차이), 키에 따른 기장: 기장이 길거나 짧음 215개 [m:std.sizing.label.length_off], 기장 선택지를 바란 리뷰 8개 [m:f.design_value.desired_feature.more_length_options]. 쁘띠, 레귤러, 톨 선택지로 대응한다.

### 집중 분석 2: 원단과 착용감, 신축성과 비침
- **긍정 쪽 원단 성질**: 신축성 있음 9.3% [m:f.fabric.fabric_property.stretchy.w], 부드러움 8.2% [m:f.fabric.fabric_property.soft.w]가 앞선다.
- **부정 쪽 원단 성질**: 신축성 없음 2.9% [m:f.fabric.fabric_property.no_stretch.w], 비침 0.8% [m:f.fabric.fabric_property.see_through.w]다.
- **통풍**: 통풍되고 시원함 4.5% [m:f.fabric.fabric_property.breathable_cool.w]가 덥거나 통풍 안 됨 1.3% [m:f.fabric.fabric_property.hot_not_breathable.w]보다 흔하다.
- **입는 상황**: 긴 근무 시간 3.3% [m:f.fabric.use_context.long_shift.w], 숙이고 들고 많이 움직이는 일 0.8% [m:f.fabric.use_context.active_movement.w]다.
> "더 뻣뻣하고 전혀 늘어나지 않는다" (Dagacci Medical Uniform, 3★, R2XFBIR8PNZAXO)
> "브라와 속옷이 그대로 비쳐 보인다" (floralhue, 2★, R16UDODT0FY6QF)
> "원단은 편하지만 걸을 때 서로 쓸려 꽤 시끄럽다" (COZYFIT, 4★, R7HRUDHL89PKW)

**시사점**
- 원인 5(설계 결함), 신축성 부족과 뻣뻣함: 신축성이 없거나 적음 160개 [m:std.fabric.label.no_stretch], 뻣뻣하거나 거칠고 따가움 122개 [m:std.fabric.label.stiff_rough]. 원단 혼용과 가공을 바꾸면 줄어든다.
- 원인 6(설계 결함), 얇거나 비치는 원단과 표시와 다른 원단: 얇거나 비침 136개 [m:std.fabric.label.thin_see_through], 원단이 설명이나 전과 다름 17개 [m:std.fabric.label.fabric_inconsistent]. 원단 무게와 표시를 고정하면 줄어든다.
- 원인 7(선호 차이), 합성섬유 느낌과 더위: 사각거리는 소리나 정전기 52개 [m:std.fabric.label.noisy_static], 덥고 통풍이 안 됨 62개 [m:std.fabric.label.runs_hot]. 같은 원단을 시원하다고 말한 리뷰도 있어 원단 성격 안내로 대응한다.

### 집중 분석 3: 만듦새와 세탁, 허리끈과 염료
- **망가진 부분**: 허리끈이 빠짐 0.9% [m:f.durability.defect_part_type.drawstring_falls_out.w], 원단이 찢어지거나 구멍이 남 0.6% [m:f.durability.defect_part_type.hole_or_tear.w]다.
- **솔기와 실밥**: 솔기나 바느질이 터짐 37개 [m:f.durability.defect_part_type.seam_stitching_open], 실밥이 삐져나옴 30개 [m:f.durability.defect_part_type.loose_threads]다.
- **세탁 뒤 주름**: 주름이 잘 생김 1.9% [m:f.durability.wash_change.wrinkles.w]보다 주름이 안 생김 3.4% [m:f.durability.wash_change.wrinkle_free.w]가 흔하다.
- **물 빠짐**: 물이 빠지거나 옮음 1.0% [m:f.durability.wash_change.dye_bleeds.w], 색이 안 바램 2.5% [m:f.durability.wash_change.no_fade.w]다.
- **문제가 난 색**: 색을 적은 리뷰 168개 [m:f.durability.problem_color.n] 가운데 black이 가장 많다.
> "허리끈이 제자리에 있지 않는다... 끝의 고무 마개가 작아 허리 밴드 구멍으로 빠져나온다" (COZYFIT, 5★, RGFZ9MWLOYA2X)
> "여러 번 빨았는데도 검은 염료가 피부와 기댄 다른 천에 묻어났다" (COZYFIT, 1★, R1WCIZSSAMJJ48)

**시사점**
- 원인 8(설계 결함), 봉제와 허리끈: 찢어짐이나 구멍, 솔기 터짐 53개 [m:std.durability.label.rips_holes], 허리끈 빠짐이나 부속 파손 44개 [m:std.durability.label.drawstring_parts]. 솔기 보강과 허리끈 고정으로 줄어든다.
- 원인 9(설계 결함), 염료와 마감 약품: 피부나 겨드랑이에 물듦 13개 [m:std.wash.label.dye_on_skin], 화학 냄새나 염료 냄새 13개 [m:std.durability.label.chemical_smell]. 염색 견뢰도와 마감 세척을 관리하면 줄어든다.
- 원인 10(설계 결함), 세탁 뒤 주름과 보풀: 주름이 잘 생기고 잘 안 펴짐 75개 [m:std.wash.label.wrinkles_easily], 보풀이나 뭉침 24개 [m:std.durability.label.pilling]. 원단 선정과 세탁 시험으로 줄어든다.

### 집중 분석 4: 디자인, 주머니, 가격과 세트 구성
- **주머니**: 주머니 불만 2.2% [m:p.map.pockets], 그중 얕거나 작아 물건이 빠짐 66개 [m:std.pockets.label.shallow_or_small]가 가장 많다.
- **바라는 옵션**: 상의와 바지 사이즈를 따로 고르기 38개 [m:f.design_value.desired_feature.separate_top_bottom_sizes], 그 밖의 바람 56개 [m:f.design_value.desired_feature.other](주머니 추가, 예전 원단 등)다.
- **비교 대상**: 다른 스크럽과 비교한 리뷰 6.3% [m:f.design_value.comparison_reference.other_product.w], 원조의 대체품으로 산 리뷰 25개 [m:f.design_value.comparison_reference.dupe_target]다.
- **구매 맥락**: 같은 제품을 다시 산 리뷰 6.1% [m:f.design_value.purchase_context.repurchase.w], 한 번에 여러 벌 산 리뷰 3.6% [m:f.design_value.purchase_context.multiple_units.w]다.
- **세트 구성**: 세트로 보였는데 상의나 하의만 옴 39개 [m:std.set_delivery.label.set_but_single_piece], 세트 일부 누락 37개 [m:std.set_delivery.label.missing_set_piece]다.
- **색**: 디자인과 색상 불만 3.4% [m:p.map.design_color], 같은 색 이름인데 색이 다름 21개 [m:f.fit.cross_order_variation.color_shade]다.
> "상의 주머니가 얕아 단백질 바, 펜, 호출기를 넣었더니 자꾸 떨어졌다" (COZYFIT, 5★, RJ1GPTTEDMGQJ)
> "받는 건 상의뿐이다" (Cherokee, 4★, RQRSG6U01JCAW)
> "말 그대로 FIGS와 똑같은데 80달러 싸다" (Dvoliaw, 5★, R379TKQRXERRZQ)

**시사점**
- 원인 11(설계 결함), 얕은 상의 주머니와 주머니 봉제: 얕거나 작음 66개 [m:std.pockets.label.shallow_or_small], 주머니 찢어짐이나 바느질 불량 14개 [m:std.pockets.label.torn_or_bad_sewing]. 주머니 깊이와 박음질을 고치면 줄어든다.
- 원인 12(선호 차이), 주머니 수와 위치: 주머니가 모자람 18개 [m:std.pockets.label.missing_pockets], 위치가 이상함 14개 [m:std.pockets.label.odd_placement]. 주머니 배치 안내와 선택지로 대응한다.
- 원인 13(설계 결함), 판매 구성과 받은 상품 상태: 세트로 보였는데 한 벌만 옴 39개 [m:std.set_delivery.label.set_but_single_piece], 쓰던 물건이나 반품된 물건을 받음 80개 [m:std.set_delivery.label.received_used_item]. 구성 표기와 봉인 포장을 고치면 줄어든다.
- 원인 14(선호 차이), 값에 대한 기대: 상의 한 벌 값으로 비쌈 11개 [m:std.value.label.pricey_for_top_only], 싼 게 비지떡 20개 [m:std.value.label.get_what_you_pay_for]. 구성별 가격 안내로 대응한다.

### 안전
- 안전 부정 리뷰 16개: 메스꺼움 1개(가중 0.0%), 피부 8개(가중 0.1%), 알레르기 언급 2개(가중 0.0%), 이상 반응 없음 5개 [m:p.safety_text]
- **증상 종류**: 고무 밴드가 닿는 자리의 발진, 날카로운 솔기에 긁힌 상처, 염료가 몸에 묻은 일이 있고, 수가 적어 상품별 비율로 말하지 않는다.
- **보호복이 아님**: OSHA는 평상복처럼 입는 스크럽을 대개 개인보호구로 보지 않아 [r:reg_13] [r:reg_14] 보호 기능을 말하지 않는다.
- **가연성**: 16 CFR 1610 시험에서 1등급은 의류에 쓸 수 있고 3등급은 쓸 수 없어 [r:tst_10], 폴리에스터나 나일론만으로 된 원단은 면제지만 레이온과 스판덱스는 면제 목록에 없어 [r:reg_09] 혼방 원단은 시험 대상인지 확인한다.
- **PFAS**: 캘리포니아는 규제 PFAS가 든 섬유 제품의 판매를 막아 [r:reg_16] 발수 가공을 쓰면 확인한다.
> "고무 밴드가 닿는 배 양쪽에 심한 발진이 생겼다" (COZYFIT, 4★, R3SMX6VQ3YVQPK)
> "솔기의 날카로운 끝 때문에 골반 쪽에 상처가 나 두 주 넘게 갔다" (COZYFIT, 2★, R23I37EEYT3IXS)

## 04 포지셔닝
**TL;DR** 포지션은 상하의 사이즈를 따로 고르고 키에 맞는 기장을 고르는 스트레치 여성 세트다. 근거는 사이즈와 핏 불만 1위 22.1% [m:head.topic_neg]와 가장 큰 약점이 사이즈와 핏인 상품 10개 중 9개(리뷰를 다시 뽑아 보면 9~10개) [m:head.topic_weakest]이고, 남성 세트와 단품은 첫 세트의 치수 체계를 확인한 뒤로 미룰 것을 권고한다(확인 필요).

### 한 줄 포지션
상의와 바지 사이즈를 따로, 키에 맞춰 기장을 고르는 four-way stretch 여성 스크럽 세트, 실측 사이즈표와 세탁 시험값을 적는 브랜드

### 이기는 이유
- **사이즈를 맞춘 상품의 공백**: 가장 큰 약점이 사이즈와 핏인 상품이 10개 중 9개(리뷰를 다시 뽑아 보면 9~10개) [m:head.topic_weakest]이고, 사이즈 부정이 가장 적은 COZY SCRUBS 18.2% [m:std.sizing.best]도 리뷰가 적은 상품이다.
- **한쪽으로 고칠 수 없는 방향**: 크게 나옴 409개 대 작게 나옴 418개(0.98배) [m:head.dir_ratio]이고 상품마다 방향이 반대라, 크게 사라거나 작게 사라는 안내보다 실측 사이즈표가 차별점이 된다.
- **상하의 따로 고르기**: 따로 고르기를 바란 리뷰 38개 [m:f.design_value.desired_feature.separate_top_bottom_sizes]와 상하의 사이즈가 서로 다르다는 리뷰 135개 [m:std.sizing.label.top_bottom_mismatch]가 있고, 세트 노드 상위 브랜드가 상하의 사이즈를 따로 고르게 하는지는 확인 필요다.
- **원조 브랜드 대체 수요**: 다른 스크럽과 비교한 리뷰 6.3% [m:f.design_value.comparison_reference.other_product.w]와 대체품으로 산 리뷰 25개 [m:f.design_value.comparison_reference.dupe_target]가 있어, 원조 브랜드의 기장 체계 [r:ind_02]를 세트 값에 주는 것이 자리다.
- **긴 근무의 신축성**: 신축성 있음 9.3% [m:f.fabric.fabric_property.stretchy.w]가 긍정 원단 성질 1위이고 긴 근무 시간을 말한 리뷰가 3.3% [m:f.fabric.use_context.long_shift.w]다.

### 소비자 기준표
#### 기준 1: 사이즈 표기와 핏(원인 1, 2, 3, 4 대응)
- 감점 기준: 사이즈 불만 가중 30.7% [m:std.sizing.neg_pct]이고, 작게 나옴 418개 [m:std.sizing.label.runs_small]와 크게 나옴이 거의 같은 수로 갈린다.
- 만족 기준: 핏 만족 리뷰 954개 [m:std.sizing.pos]처럼 평소 사이즈 그대로 맞는 수준이고, 부정이 가장 적은 상품은 COZY SCRUBS 18.2% [m:std.sizing.best](리뷰가 적은 상품)다.
- 개발 기준: XXS부터 큰 사이즈까지 [r:ind_05] 상하의를 따로 고르게 하고, 기장은 키 기준 쁘띠, 레귤러, 톨 [r:ind_02]로 나눈다. 상품을 합친 사이즈별 방향은 XXS~M 크게 나옴, L~5XL 작게 나옴 [m:std.sizing.vdir.Size.flip]이고, 모든 상품에 있는 양 끝 사이즈의 방향 지수는 XS -0.82 [m:std.sizing.vdir.Size.XS], XXL +0.61 [m:std.sizing.vdir.Size.XXL]이다. 상품을 합친 값이라 상품마다 방향은 다를 수 있으므로(점수표의 상품별 방향 지수), 사이즈 사이 등급 폭을 한 값으로 두지 않고 작은 사이즈와 큰 사이즈를 따로 보정하는 안을 시제품 실측과 착용 시험으로 확인한다. 세탁 뒤 치수 변화는 AATCC TM135로 잰다 [r:tst_01]. 치수 허용 오차와 생산 묶음 검수 기준은 확인 필요(조사 근거 없음).
- 상세페이지 문구: "Mix your top and pant sizes, in Petite, Regular and Tall" (상의와 바지 사이즈를 따로, 쁘띠, 레귤러, 톨 기장으로). 실측 사이즈표를 생산품으로 검증한 뒤에만 쓴다.
> "판매자가 상의와 바지 사이즈를 따로 고르게 해 준다면 완벽할 것이다" (COZYFIT, 5★, R24MCM32PQEIJO)

#### 기준 2: 원단과 착용감(원인 5, 6, 7 대응)
- 감점 기준: 원단 불만 가중 10.6% [m:std.fabric.neg_pct], 그중 신축성이 없거나 적다는 말 160개 [m:std.fabric.label.no_stretch]가 가장 많다.
- 만족 기준: 원단 만족 리뷰 1,192개 [m:std.fabric.pos]의 부드럽고 늘어나는 수준이고, 부정이 가장 적은 상품은 COZYFIT 5.2% [m:std.fabric.best]다.
- 개발 기준: 경쟁 라인의 스판덱스 혼용은 FIGS 조거 7% [r:ind_01], Fabletics 6% [r:ind_18]이고 이를 시작점으로 four-way stretch를 고른다. 신축과 회복은 ASTM D3107 [r:tst_09], 땀 배출은 AATCC TM195 [r:tst_06]로 잰다. 비침 기준은 확인 필요(조사 근거 없음).
- 상세페이지 문구: "Four-way stretch that moves with every bend and reach" (숙이고 뻗을 때마다 따라 늘어나는 사방 스트레치). 신축과 회복 시험을 통과한 뒤에만 쓴다.
> "허벅지와 엉덩이가 굵은 내게 딱 알맞게 늘어난다" (COZYFIT, 5★, RJ1GPTTEDMGQJ)

#### 기준 3: 만듦새와 내구성(원인 8, 10 대응)
- 감점 기준: 내구성 불만 가중 4.9% [m:std.durability.neg_pct], 그중 찢어짐이나 구멍, 솔기 터짐 53개 [m:std.durability.label.rips_holes]가 품질 일반 불만 다음으로 많다.
- 만족 기준: 내구성 만족 리뷰 480개 [m:std.durability.pos]의 빨아도 해지지 않는 수준이고, 부정이 가장 적은 상품은 Cherokee 2.1% [m:std.durability.best]다.
- 개발 기준: 보풀은 ASTM D3512로 잰다 [r:tst_08]. 솔기 강도와 허리끈 고정 시험 기준은 확인 필요(조사 근거 없음).
- 상세페이지 문구: "Drawstring stitched in place, won't slip out in the wash" (세탁해도 빠지지 않게 박음질로 고정한 허리끈). 반복 세탁 뒤 허리끈과 솔기를 확인한 뒤에만 쓴다.
> "빨 때 끈이 바지에서 빠지지 않게 끈을 박음질로 고정해야 한다!" (COZYFIT, 1★, R2NSTAJWTX0GH8)

#### 기준 4: 세탁과 물빠짐(원인 9, 10 대응)
- 감점 기준: 세탁 불만 가중 3.9% [m:std.wash.neg_pct], 그중 주름이 잘 생기고 잘 안 펴진다는 말 75개 [m:std.wash.label.wrinkles_easily]가 가장 많다.
- 만족 기준: 세탁 만족 리뷰 179개 [m:std.wash.pos]의 줄지 않고 색이 그대로인 수준이고, 부정이 가장 적은 상품은 Cherokee 1.2% [m:std.wash.best]다.
- 개발 기준: 세탁 줄어듦 AATCC TM135 [r:tst_01], 세탁 색 빠짐 TM61 [r:tst_02], 마찰 이염 TM8 [r:tst_03], 세탁 뒤 매끈함 TM124 [r:tst_05]를 시험한다. 합격 등급은 확인 필요(조사 근거 없음).
- 상세페이지 문구: "Colorfast and wrinkle-resistant, tumble dry safe" (물이 빠지지 않고 구김에 강하며 건조기 사용 가능). 세탁 시험을 통과한 뒤에만 쓴다.
> "다림질을 해야 한다" (COZYFIT, 3★, R1FL3ARFI8BWJT)

#### 기준 5: 피부 반응(원인 9 대응)
- 감점 기준: 피부 반응 불만 가중 0.1% [m:std.skin_safety.neg_pct], 11개 [m:std.skin_safety.neg]로 적지만 염료가 피부에 묻은 일과 밴드 자리의 발진이 감점이다.
- 만족 기준: 피부 반응 긍정 리뷰는 0개 [m:std.skin_safety.pos]라 피부 반응 언급이 없는 수준을 기준으로 두고, 부정이 가장 적은 상품은 COZY SCRUBS 0.0% [m:std.skin_safety.best]다.
- 개발 기준: 마찰 이염을 AATCC TM8로 잰다 [r:tst_03]. 의류 가연성 1등급 [r:tst_10]을 확인하고 혼방 원단의 면제 여부를 본다 [r:reg_09]. 항균 표현은 제품 보호에 한정한다 [r:reg_10].
- 상세페이지 문구: "Smooth seams and colorfast dye for all-day wear" (종일 입어도 부드러운 솔기와 묻어나지 않는 염색). 이염 시험을 통과한 뒤에만 쓰고, 저자극 표현은 근거가 없어 쓰지 않는다.
> "여러 번 빨았는데도 검은 염료가 피부와 기댄 다른 천에 묻어났다" (COZYFIT, 1★, R1WCIZSSAMJJ48)

#### 기준 6: 주머니(원인 11, 12 대응)
- 감점 기준: 주머니 불만 가중 2.6% [m:std.pockets.neg_pct], 그중 얕거나 작아 물건이 빠진다는 말 66개 [m:std.pockets.label.shallow_or_small]가 가장 많다.
- 만족 기준: 주머니 만족 리뷰 171개 [m:std.pockets.pos]의 많고 깊은 수준이고, 부정이 가장 적은 상품은 COZYFIT 0.7% [m:std.pockets.best]다.
- 개발 기준: 확인 필요(조사 근거 없음)
- 상세페이지 문구: "Deep top pockets that hold your phone when you bend" (숙여도 휴대폰이 빠지지 않는 깊은 상의 주머니). 착용 시험으로 확인한 뒤에만 쓴다.
> "셔츠 주머니가 옆 뒤쪽에 너무 붙어 있어 펜을 꽂거나 휴대폰을 꺼내려면 뒤로 손을 어색하게 뻗어야 한다" (Dvoliaw, 3★, R6AHJ8GMY1R2V)

#### 기준 7: 세트 구성과 배송(원인 2, 13 대응)
- 감점 기준: 구성과 배송 불만 가중 2.7% [m:std.set_delivery.neg_pct], 그중 쓰던 물건이나 반품된 물건을 받았다는 말 80개 [m:std.set_delivery.label.received_used_item]가 가장 많다.
- 만족 기준: 구성과 배송 만족 리뷰 45개 [m:std.set_delivery.pos]의 봉인된 새 상품이 주문대로 오는 수준이고, 부정이 가장 적은 상품은 COZY SCRUBS 0.0% [m:std.set_delivery.best]다.
- 개발 기준: 상하의 색은 같은 컬렉션 안에서 맞추고 [r:ind_12], 색마다 혼용률이 다르면 색별로 표기한다 [r:ind_11]. 구성 표기와 봉인 포장 기준은 확인 필요(조사 근거 없음).
- 상세페이지 문구: "Top and pant set, both pieces in one sealed bag" (상의와 바지 두 벌이 한 봉인 포장에 든 세트). 단품 상의는 상품명 앞에 Top only를 적는다.
> "세트가 아니라 상의만이다" (Cherokee, 2★, R1693OU6ROFGMA)

#### 기준 8: 가격 대비 가치(원인 14 대응)
- 감점 기준: 가치 불만 가중 1.0% [m:std.value.neg_pct], 그중 돈 낭비 30개 [m:std.value.label.waste_of_money]가 가장 많다.
- 만족 기준: 가치 만족 리뷰 423개 [m:std.value.pos]의 값에 비해 좋다는 수준이고, 부정이 가장 적은 상품은 COZY SCRUBS 0.0% [m:std.value.best]다.
- 개발 기준: CozyFit 자사몰 세트는 정가 45.99달러, 할인가 29.99달러 [r:ind_19]이고, Cherokee Workwear Revolution은 상의와 바지를 따로 팔아 값을 따로 받는다 [r:ind_04]. 이 범위 안에서 세트 값을 정한다.
- 상세페이지 문구: "Complete set, no need to buy pants separately" (바지를 따로 살 필요 없는 완성 세트). 상하의가 모두 든 구성에만 쓴다.
> "스크럽 상의 하나에 28달러는 너무 비싸다고 생각한다" (Cherokee, 3★, RA0OTR47NR386)

### 하위 카테고리별 출시 계획
- **첫 출시, 여성 상하의 세트(Women's Medical Scrub Sets)**: 상하의 사이즈를 따로 고르는 세트로 낸다. 세트 검색어 scrubs for women set의 검색량은 106,128 [m:std.set_delivery.term.scrubs for women set]이다.
- **다음 출시, 여성 상의와 바지 단품**: 같은 치수 체계로 단품을 열어 따로 사기를 받친다. 상의 노드 상위 10개 합 77.7% [m:m.top10_share_WTOP]이고 CHEROKEE가 1위이며 의료복 브랜드와 CozyFit이 함께 상위다.
- **그다음, 남성 세트**: 남성 검색어 검색량 합 58,995 [m:m.terms_male_volume]로 작고 노드 1위 CozyFit 60.6% [m:m.top1_MSET]로 몰려 있어, 여성 세트의 치수 체계를 옮긴 뒤 낸다.
- **보류, 재킷과 랩 코트**: 리뷰 표본에 없어 판단하지 않는다.

### 가격 구조
- **읽는 법**: 이 회차의 묶음 값은 점수표 가격을 단위로 나누지 않은 상품 한 개의 가격이라, 세트는 상하의 한 벌 값, Cherokee 상의는 상의 한 벌 값으로 읽는다.
- **낮음 묶음**: 19.99~23.83달러 [m:price.band0.range], 사이즈와 핏 부정 26.5% [m:price.band0.skin_neg]로 세 묶음 가운데 가장 높다.
- **낮음 묶음 구성**: 사이즈와 핏 부정이 가장 높은 Dagacci 세트 49.2% [m:s.B00FT74D3E.topic_neg]가 이 묶음에 들어 있다(나란히만 놓음).
- **중간 묶음**: 25.30~28.71달러 [m:price.band1.range], 사이즈와 핏 부정 17.8% [m:price.band1.skin_neg]로 세 묶음 가운데 가장 낮다.
- **높음 묶음**: 29.22~31.99달러 [m:price.band2.range], 사이즈와 핏 부정 21.7% [m:price.band2.skin_neg]다.
- **별점**: 중간 묶음이 4.43★ [m:price.band1.star]로 가장 높고, 높음 묶음은 4.16★ [m:price.band2.star]다.
- **상품 수**: 낮음 묶음 4개 [m:price.band0.n], 높음 묶음 3개 [m:price.band2.n]처럼 묶음마다 상품이 적어, 가격이 불만을 만든다고 읽지 않고 나란히만 놓는다.
- **시장 가격대**: 2구간 24.95~29.98 [m:m.price_band2_range]의 매출 비중이 40.6% [m:m.price_band2_share]다.
- **시장 위쪽 구간**: 3구간의 매출 비중 42.4% [m:m.price_band3_share], 평균 별점 4.33★ [m:m.price_band3_rating]로 가장 높다(브랜드 평균 가격 구간이라 단품 가격 근거로는 약함).
- **권고(확인 필요)**: 첫 여성 세트는 시장 2구간 24.95~29.98 [m:m.price_band2_range] 안에 두고, 값을 더 내리기보다 사이즈와 원단 기준을 먼저 맞춘다. 가격 대비 가치 불만 1.0% [m:p.map.price_value]는 사이즈와 원단 불만보다 작다.

### 메시지와 키워드
- **썸네일**: "Mix & Match Top and Pant Sizes" (상하의 사이즈 따로)와 "Petite, Regular, Tall" (쁘띠, 레귤러, 톨) 두 줄, 실측 사이즈표 검증 뒤에만.
- **상세**: 상의 가슴, 바지 허리와 엉덩이, 인심을 적은 실측 사이즈표와 키별 기장 추천, 색마다 혼용률, 세탁 시험 결과를 적는다.
- **박스 안**: 허리끈 매듭과 세탁, 건조 안내, 사이즈 교환 방법, 같은 컬렉션 안에서 색을 맞추라는 안내 [r:ind_12]를 담은 안내지.
- **키워드**: scrubs for women set, scrubs for women, scrub sets for woman, scrub pants for women, womens scrubs를 기본으로 두고, black scrubs sets for women(검색량 44,880 [m:std.set_delivery.term.black scrubs sets for women])처럼 색이 든 세트 검색어를 더한다. figs scrubs women, fabletics scrubs for women은 경쟁 브랜드 검색어라 광고 대상으로만 검토한다.

### 실행 순서
1. **P1 치수 체계**: XXS부터 큰 사이즈까지 등급을 매기고 쁘띠, 레귤러, 톨 기장 [r:ind_02]과 상하의 따로 고르는 SKU를 짠다.
2. **P1 실측 사이즈표 검증**: 생산 묶음마다 치수를 재 표와 맞춘다(허용 오차는 확인 필요).
3. **P1 원단 선정과 신축 시험**: four-way stretch 원단을 ASTM D3107 [r:tst_09]과 AATCC TM195 [r:tst_06]로 고른다.
4. **P1 세탁 시험**: AATCC TM135 [r:tst_01], TM61 [r:tst_02], TM8 [r:tst_03], TM124 [r:tst_05].
5. **P1 봉제와 허리끈**: 솔기 보강, 허리끈 고정, 보풀 ASTM D3512 [r:tst_08].
6. **P1 가연성과 PFAS**: 의류 가연성 1등급 [r:tst_10]과 혼방 면제 여부 [r:reg_09], 발수 가공을 쓰면 캘리포니아 PFAS 기준과 준수 증명서 [r:reg_17] [r:reg_18].
7. **P1 표시 문구 검토**: 항균 표현은 제품 보호에 한정하고 [r:reg_10] [r:reg_11], 보호복이라 말하지 않으며 [r:reg_13], 재활용 소재를 쓰면 함량을 밝힌다 [r:reg_20]. 섬유 조성과 세탁 라벨 의무는 확인 필요(조사 근거 없음).
8. **P1 세트 구성 표기와 봉인 포장**: 상품명과 사진에 구성을 적고 봉인 포장으로 보낸다.
9. **P2 여성 상의와 바지 단품**: 같은 치수 체계로 연다.
10. **P2 남성 세트**: 남성 키와 체형으로 등급을 다시 맞춘다.
11. **P2 주머니 배치와 색 확장**: 출시 뒤 리뷰로 주머니 위치와 색을 늘린다.

### 개발 단계와 관문
- **치수 관문**: 생산품 실측이 사이즈표와 맞고, 사내 착용 시험에서 크게 나옴과 작게 나옴 어느 쪽도 한쪽으로 몰리지 않아야 한다(시장은 크게 나옴 9.9% [m:head.dir_low_w] 대 작게 나옴 7.7% [m:head.dir_high_w]).
- **원단과 세탁 관문**: 신축과 회복 [r:tst_09], 세탁 줄어듦 [r:tst_01], 색 빠짐 [r:tst_02], 마찰 이염 [r:tst_03]을 통과해야 한다(합격 등급은 확인 필요).
- **안전과 표시 관문**: 가연성 1등급 [r:tst_10], PFAS 준수 증명서 [r:reg_18], 표시 문구 검토가 끝나야 출시한다.
- **출시 뒤 관문**: 첫 리뷰의 사이즈와 핏 부정 비율을 시장 22.1% [m:head.topic_neg]와 비교하고, 세트 구성과 받은 상품 상태 불만을 따로 본다.

### 결론
- **무엇을**: 상하의 사이즈를 따로 고르고 쁘띠, 레귤러, 톨 기장을 고르는 four-way stretch 여성 스크럽 세트.
- **누구에게**: 긴 근무에 입는 여성 의료 종사자와 실습생(리뷰어가 적은 키 중앙값 65inch [m:f.fit.reviewer_height.median]), 남성 세트는 다음 차례.
- **얼마에**: 시장 가격 2구간 24.95~29.98 [m:m.price_band2_range] 안(확인 필요).
- **무엇으로 이기는지**: 사이즈와 핏 부정을 시장 22.1% [m:head.topic_neg]보다 낮추는 실측 사이즈표와 치수 관리, 세탁 시험을 통과한 원단.

## 05 한 장 요약
### 제품 해부도
1. **상의 몸판과 가슴**: 상의 치수를 따로 등급 매기고 실측표에 가슴 둘레를 적음 (상의 전체가 작거나 조임 2.9% [m:f.fit.fit_part_direction.top_too_tight.w])
2. **바지 허리와 허리끈**: 고무줄과 끈 허리, 끈은 박음질로 고정 (허리끈이 빠짐 36개 [m:f.durability.defect_part_type.drawstring_falls_out])
3. **바지 기장**: 키 기준 쁘띠, 레귤러, 톨 [r:ind_02] (바지 기장이 김 2.2% [m:f.fit.fit_part_direction.pants_too_long.w])
4. **엉덩이와 허벅지**: 곡선 체형을 위한 여유 (엉덩이나 가랑이가 조임 58개 [m:f.fit.fit_part_direction.hips_butt_crotch_tight])
5. **원단**: 비치지 않는 무게의 four-way stretch [r:tst_09] (신축성이 없거나 적음 160개 [m:std.fabric.label.no_stretch])
6. **상의 주머니**: 숙여도 휴대폰이 빠지지 않는 깊이 (얕거나 작아 물건이 빠짐 66개 [m:std.pockets.label.shallow_or_small])
7. **솔기와 봉제**: 보강한 솔기와 피부에 닿지 않는 솔기 끝 (찢어짐이나 구멍, 솔기 터짐 53개 [m:std.durability.label.rips_holes])
8. **염색과 마감**: 묻어나지 않는 염색과 냄새 없는 마감 [r:tst_03] (피부나 겨드랑이에 물듦 13개 [m:std.wash.label.dye_on_skin])

### 단계와 관문
- **치수**: P1 두 건(치수 체계, 실측 사이즈표 검증), 관문은 생산품 실측과 착용 시험 (상하의 사이즈가 서로 다름 135개 [m:std.sizing.label.top_bottom_mismatch])
- **원단과 세탁**: P1 두 건(원단 선정, 세탁 시험), 관문은 신축과 세탁 시험 통과 [r:tst_09] [r:tst_01]
- **봉제와 부속**: P1 한 건, 관문은 반복 세탁 뒤 허리끈과 솔기 상태 (허리끈 빠짐이나 부속 파손 44개 [m:std.durability.label.drawstring_parts])
- **안전과 표시**: P1 세 건(가연성과 PFAS, 표시 문구, 세트 구성과 포장), 관문은 가연성 1등급 [r:tst_10]과 PFAS 준수 증명서 [r:reg_18]
- **출시 뒤**: P2 세 건(단품, 남성 세트, 주머니와 색), 관문은 사이즈와 핏 부정을 시장 22.1% [m:head.topic_neg]와 비교

## A 데이터와 방법
### 출처
- 리뷰, 태그, 세부 이슈 라벨, 설계 정보, 시장 데이터, 웹 조사, 상품 사양의 파일과 건수는 아래 표에 있다.
- 웹 조사 주장은 69개 중 53개 [m:a.research_verified]를 다시 열어 원문 문장을 확인했고, 확인된 주장만 썼다.
- 상품 사양은 다시 열어 확인한 값만 썼고, 같은 상품인지 확인한 정도는 이름만 일치 3개, 일치 확인 3개, 찾지 못함 4개 [m:spec.match_summary]다.
- 설계 정보 추출 감사 결과는 표본 150개 중 FAIL 6개(4.0%) [m:a.detail_audit]다.
- **읽는 법**: 비율은 별점 묶음(부정, 중립, 긍정) 가중으로 표본 편향을 되돌린 값이고, 원본 수는 무엇을 말하는지, 가중 비율은 얼마나 흔한지로 읽는다.
- **기준표 불만 비율**: 그 기준의 부정 라벨이 붙은 리뷰어 비율이라 불만 지도의 주제 부정 비율과 세는 대상이 다르고(사이즈는 기준표 30.7% [m:std.sizing.neg_pct], 불만 지도 22.1% [m:p.map.fit_sizing]), 불만 순위는 불만 지도 값으로 말한다.
- **원인 번호와 별점 격차**: 원인 번호는 대응 방법(설계 결함, 선호 차이)으로 나눈 분류이고, 별점 격차는 그 주제 부정 리뷰와 나머지 리뷰의 가중 평균 별점 차이라 둘 다 인과가 아니다.
- **방향 지수**: (작게 나옴 − 크게 나옴) ÷ (작게 나옴 + 크게 나옴)을 리뷰 가중치 합으로 계산한 값이고, 양수면 작게 나옴 쪽, 음수면 크게 나옴 쪽이다.
- **작게 나옴 비율**: 그 설계 정보 값을 말한 리뷰 가운데 작게 나옴 라벨이 함께 붙은 리뷰의 비율(원본 수)이다.
- **가격 묶음과 검색량**: 가격 묶음은 조사 상품을 점수표 가격 순으로 세 묶음으로 나눈 것이고 시장 가격대는 브랜드 평균 가격 구간이다. 검색어 옆 숫자는 시장 데이터의 한 달 검색량이다.

### 견고성 점검
- 리뷰를 2,000번 [m:a.robust.n] 다시 뽑으면 사이즈와 핏이 불만 1위로 남은 비율은 100.0% [m:a.robust.head_first]다.
- 사이즈와 핏 부정 비율(머리 숫자)의 다시 뽑기 구간은 20.4%~23.8% [m:a.robust.head_neg_ci]이고, 가장 큰 약점이 사이즈와 핏인 상품 수는 9개 55.1%, 10개 44.9% [m:a.robust.weakest_dist]로 나뉜다.
- 상품을 하나씩 빼도 사이즈와 핏 부정은 19.4%~23.1% [m:a.robust.loo_head_neg], 크게 나옴 쪽 비율(가중)은 51.0%~60.1% [m:a.robust.loo_low_share] 안에 있다.
- 상품을 하나씩 뺀 계산에서 결론이나 불만 지도 상위 세 주제 순서가 바뀐 경우는 10번 중 0번 [m:a.robust.loo_flips]이다.
- 이 점검은 고른 상품 안의 표본 흔들림만 재고, 어떤 상품을 골랐는지에 따른 치우침은 재지 못한다.

### 주의 사항
- 리뷰는 공유 리뷰 DB 표본이라 낮은 별점이 실제보다 많고, 비율은 별점 묶음 가중으로 되돌렸다(표본 평균과 가중 평균 별점은 아래 원문 목록).
- 원본 수와 가중 비율은 방향이 다를 수 있다. 라벨 원본 수는 크게 나옴 409개 대 작게 나옴 418개(0.98배) [m:head.dir_ratio]로 작게 나옴이 조금 많지만, 가중하면 크게 나옴 쪽이 더 흔해 이 가이드는 가중 비율로 말한다.
- 리뷰어가 적은 키와 몸무게는 측정값이 아니라 방향과 분포로만 읽고, 개발 기준의 사양 숫자는 웹 조사 출처의 시작점이라 시험으로 확인해야 한다.
- 조사 상품이 적고 대부분 한 하위 카테고리(Women's Medical Scrub Sets)라 상품끼리, 하위 카테고리끼리의 비교가 약하고, COZYFIT(이름을 바꾼 COZY SCRUBS 포함) 상품이 여럿이라 결과가 이 브랜드 쪽으로 기울 수 있다.
- 시장 데이터(spd-amz-market)의 매출, 점유율, 증감, 승률 칸은 단위가 없어 단위 미확인으로 적었고, 연 환산 값은 월 매출 칸을 달러로 가정한 것이다.
- ASIN은 매출 순위가 아니라 공유 DB에 리뷰가 많은 후보 가운데 고른 상품이고(상품 확인 관문에서 사람이 확인), 블라인드 회차라 답지 상품과 같은 상품을 팀 DB에서 골랐으며 유료 수집은 켜지 않았다.
- 성장 배수 머리 숫자는 후보 검색어 206개 [m:m.growth_candidates] 가운데 주간 이력을 받은 검색어가 0개 [m:m.growth_ranked]라 쓰지 않았고, yoYChangePct 칸은 뜻과 단위가 확인되지 않아 검색 수요 표의 전년 대비 칸도 참고로만 본다.
- 가격 묶음은 단위로 나누지 않은 상품 한 개의 가격으로 나눠 세트와 상의 단품(Cherokee)이 같은 묶음에 섞이고, 가격이 없어 묶음에서 뺀 상품은 0개 [m:price.unpriced]다.
- 정답 세트로 잰 sonnet 태그는 주제 F1 0.83 [m:acc.topic_f1]으로 기준을 넘었지만 감성 전체 일치 89.7% [m:acc.sentiment]는 판정 기준에 조금 못 미친다.
- 감성 방향 일치는 97.9% [m:acc.direction]로 높고 한쪽이라도 mixed인 짝의 mixed 일치는 52.4% [m:acc.mixed]라, 어긋남은 주로 혼합과 부정의 경계에 있어 부정 비율이 조금 움직일 수 있다.
- 미국 시장 규모는 보고서마다 범위와 연도가 달라 더하거나 곱하지 않았고, 웹 조사에서 섬유 조성 표시와 세탁 라벨 의무, 뉴욕주 PFAS 규정, 수술 가운 규제, 간호사 일자리 수, 경쟁사 세탁 시험 주장은 출처를 다시 열지 못했거나 원문 문장을 찾지 못해 쓰지 않았다.
- 아직 찾지 못한 것: 치수 허용 오차 기준, AATCC와 ASTM 시험의 합격 등급, 솔기 강도와 허리끈 고정 시험, 주머니 깊이 기준, 원단 비침 기준. 해당 칸은 확인 필요로 남겼다.
