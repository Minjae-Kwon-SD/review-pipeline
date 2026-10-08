# 아마존 미국 향수(EDP, EDT) 제품 개발 가이드
> 아마존 미국에 새로 들어오는 브랜드를 위한 기준: 오래가되 세지 않게, 설명한 노트 그대로, 미니로 먼저 맡게, 깨지지 않게 보낸다

## 머리 숫자
- [f.longevity.longevity_hours.median] 리뷰어가 말한 지속 시간의 중앙값이다(시간을 적은 리뷰 81개 [m:f.longevity.longevity_hours.n]). 시장 크기 숫자는 단위를 확인하지 못해 01장 안에만 둔다.
- [head.topic_neg] 지속력과 향의 세기를 부정으로 말한 리뷰어 비율(별점 가중)로, 불만 지도에서 가장 높다. 개발에서 가장 먼저 풀 문제가 여기서 정해진다.
- [head.topic_weakest] 점수표 상품 가운데 가장 큰 약점이 지속력과 향의 세기인 상품 수이고, 괄호는 리뷰를 다시 뽑아 보았을 때 95% 이상을 덮는 범위다. 다시 뽑아도 가격대와 브랜드가 다른 여러 상품이 같은 약점을 안고 있어 개선 가설의 출발점이다.
- [head.dir_ratio] 세기 불만의 방향이다. 약하다는 쪽이 훨씬 많지만 너무 세다는 불만도 있어, 무작정 세게 만드는 것은 답이 아니다.
- [head.fastest_term] 주간 검색량 이력으로 본 성장 배수(정의는 01장 검색 수요)가 가장 큰 카테고리 검색어다. 세 번째 출시 후보(헤어 퍼퓸)로 본다.

## 01 시장 개요
**TL;DR** 외부 조사로 본 미국 향수 시장은 출처마다 규모가 다르지만 프레스티지와 대중 유통 모두에서 매출이 늘었다 [r:mkt_02] [r:mkt_03]. 아마존 Women's Fragrances 노드의 월 매출 칸은 72,057,467(월 매출 칸, 단위 미확인) [m:head.market_month]이고, Women's Eau de Parfum은 상위 10개 브랜드 합이 31.1% [m:m.top10_share_EDP]로 Women's Eau de Toilette 44.7% [m:m.top10_share_EDT]보다 집중도가 상대적으로 낮은 후보 노드다. 진입 가능성은 가격, 수요, 광고비를 확인한다. 리뷰에서 가장 흔한 불만은 지속력과 향의 세기 10.0% [m:head.topic_neg]이고, 이를 개선 가설로 삼는다.

### TAM, SAM, SOM
아래 표는 시장 데이터(spd-amz-market)의 하위 카테고리와 브랜드 점유율이다. 월 매출, 증감, azRevenuePct 칸은 문서에 단위가 없어 크기 비교로만 읽는다.

- **TAM(미국 향수 시장 전체)**: 출처마다 다르다. IMARC는 2025년 100.4억 달러 [r:mkt_12], MarketLine은 2024년 139.3억 달러 [r:mkt_13], Ken Research는 2025년 135.5억 달러 [r:mkt_14]로 본다. 세 출처가 서로 충돌하므로 하나를 고르지 않고 범위로 둔다.
- **성장 방향**: 2025년 미국 프레스티지 향수 매출은 5% 늘었고 [r:mkt_02], 대중 유통에서 향수는 가장 작은 부문이지만 15% 늘어 가장 빨리 컸다 [r:mkt_03]. 2024년 향수는 미국 프레스티지 뷰티 매출의 28%를 차지했다 [r:mkt_06].
- **SAM(아마존 미국 여성 향수)**: Women's Fragrances 노드 72,057,467(월 매출 칸, 단위 미확인) [m:head.market_month]. 이 칸을 달러로 읽어 한 해로 늘리면 864,689,610(월 매출을 달러로 읽을 때 연 환산) [m:head.market_year]이다. 단위를 확인하기 전까지는 크기의 감으로만 쓴다.
- **SOM(첫해 목표)**: 확인 필요(근거 숫자 없음). 확인이 필요한 권고로, 첫 제품이 들어갈 Women's Eau de Parfum 노드의 1위 Lattafa 8.0% [m:m.top1_EDP]와 상위 10개 합 31.1% [m:m.top10_share_EDP]를 기준선으로 두고, 단위가 확인된 매출과 우리 가격, 광고비가 정해진 뒤 다시 잡는다.

### 판정 3개
- **크기와 성장: 들어갈 만하다.** 외부 조사 세 곳 모두 미국 향수 시장을 백억 달러 단위로 보고 [r:mkt_12] [r:mkt_13] [r:mkt_14], 2024년 향수는 매출과 판매 수량 모두 프레스티지 뷰티에서 가장 빨리 큰 부문이었다 [r:mkt_05].
- **경쟁: 흩어져 있다.** Women's Eau de Parfum 상위 10개 브랜드 합은 31.1% [m:m.top10_share_EDP], Women's Eau de Toilette는 44.7% [m:m.top10_share_EDT]로 EDT가 더 몰려 있다. EDP는 집중도가 상대적으로 낮은 후보 노드이고, 진입 가능성은 가격, 수요, 광고비를 확인한다.
- **이길 자리(가설): 지속력과 세기.** 이번 표본에서 가장 큰 약점이 지속력과 향의 세기인 상품이 6개 중 5개(리뷰를 다시 뽑아 보면 3~5개) [m:head.topic_weakest]이고, 이를 개선 가설로 삼는다.

### 검색 수요
- 여성 검색어 15개 [m:m.terms_female_n]의 30일 검색량 합은 1,022,775 [m:m.terms_female_volume], 남성 검색어 17개 [m:m.terms_male_n]는 1,265,622 [m:m.terms_male_volume], 성별 낱말이 없는 공통 검색어 49개 [m:m.terms_common_n]는 3,213,197 [m:m.terms_common_volume]이다. 이 합의 차이는 검색어 수의 차이와, 공통 검색어에 브랜드 이름과 perfume 같은 일반어가 섞인 데서도 오므로, 검색량 합만으로 제목 낱말 순서를 정할 수는 없다. 낱말을 고를 때는 개별 검색어 값을 본다. 예를 들어 vanilla perfume은 94,475 [m:std.scent_accuracy.term.vanilla perfume], mini perfume은 37,436 [m:std.bottle_sprayer.term.mini perfume]이다.
- 공통 검색어 상위에는 lattafa, valentino, yara perfume 같은 브랜드와 상품 이름이 많다. 새 브랜드는 이름 검색을 기대할 수 없으니 일반 검색어(perfumes for women, vanilla perfume)에서 지속력과 노트로 클릭을 얻어야 한다.
- 가장 빨리 크는 검색어는 "hair perfume spray" 최근 4주 530,006, 1년 전 같은 4주 11,322, 46.81배 [m:head.fastest_term]이다. 성장 배수는 최근 4주 검색량 합 ÷ 1년 전 같은 4주 검색량 합(주간 이력)이고, 두 기간은 2026-09-06 ~ 2026-09-27(1년 전 2025-09-07 ~ 2025-09-28) [m:head.growth_weeks]이다. 30일 검색량 기준을 넘는 카테고리 검색어 116개 [m:m.growth_candidates] 가운데 두 기간 주간 이력이 있는 102개 [m:m.growth_ranked]에서 1위다. 외부 조사에서도 2024년 헤어 프래그런스 매출이 32% 늘었다 [r:mkt_08]. 1년 전 같은 주와 견줘 해마다 도는 계절 영향은 걸러지지만, 두 기간을 4주씩만 견준 값이라 한때의 유행이나 행사와 가려내지 못하므로, 크기보다 방향으로 읽는다.
- 가격대 표: 브랜드 평균 가격 15.76~56.22 [m:m.price_band1_range] 구간이 매출 비중 39.2% [m:m.price_band1_share]로 가장 크고 평균 별점은 4.40★ [m:m.price_band1_rating]이다. 57.57~86.98 [m:m.price_band2_range] 구간은 31.0% [m:m.price_band2_share]에 4.49★ [m:m.price_band2_rating], 88.10~164.08 [m:m.price_band3_range] 구간은 29.8% [m:m.price_band3_share]에 4.46★ [m:m.price_band3_rating]이다. 별점 차이가 작아 값을 올린다고 별점이 따라온다고 볼 근거는 없다.

### 진입 조건
아래는 확정된 사실이 아니라 확인이 필요한 권고다.

- **지속력을 숫자로 말하려면 근거부터.** FTC는 객관적 광고 주장에 합리적 근거가 있어야 한다고 본다 [r:tst_09]. "시험으로 입증" 같은 표현을 쓰면 그 수준의 자료가 있어야 한다 [r:tst_10]. 리뷰어가 말한 지속 시간 중앙값이 1시간 [m:f.longevity.longevity_hours.median]인 시장에서 지속 시간을 내세우려면 감각 시험(ASTM E1958) [r:tst_01] 결과가 먼저다.
- **위험물 운송.** 인화성 용제(에탄올 등)를 포함한 향료 제품은 미국 위험물 분류에서 UN1266, 3급 인화성 액체로 분류된다 [r:reg_19]. 우리 제품 조성과 운송 경로로 확인한다. USPS로는 국내 지상 운송만 되고 항공은 사전 승인이 필요하다 [r:reg_15] [r:reg_18]. 한 소포에 향수는 모두 16온스까지다 [r:reg_16]. 아마존 FBA의 위험물 심사 절차는 조사하지 않았다: 확인 필요(조사 근거 없음).
- **라벨과 주 법.** 성분은 많은 순서로 적되 향료는 fragrance로 적을 수 있다 [r:reg_03]. 캘리포니아는 향료 20% 이하 개인용 향수의 VOC 75% 한도를 넘긴 수입업체에 벌금을 물렸다 [r:reg_12]. 워싱턴주는 특정 독성 물질을 제한하며 [r:reg_13], 그 물질이 향료 조성물(고정제 등) 안에 들어 있어도 의도적으로 넣은 것으로 본다 [r:reg_14].
- **향료 안전 기준.** IFRA 51차 개정은 40개 넘는 새 기준을 넣었고 [r:reg_20], 52차 개정은 2026년 8월 31일 의견 수렴을 마쳤다 [r:reg_21]. 2026년 2월 기준 FDA는 향료 알레르겐 규칙안을 아직 작성 중이었고 확정 규칙은 없다 [r:reg_09]. 법은 규칙안을 2022년 12월 29일부터 18개월 안에 내도록 정했고 [r:reg_34], 규칙안 목표 시점은 2025년 9월 정리 자료에서 2026년 5월이었다가 [r:reg_08] 2026년 7월 연방 규제 일정에서 2026년 11월로 다시 미뤄졌다 [r:reg_36]. 거듭 미뤄져 왔으므로 한 날짜로 잡지 않고 출시 시점에 다시 확인한다.
- **반품이 어려운 상품이라는 점.** 시향과 반품 불만 74개 [m:std.sampling_returns.neg] 가운데 반품이나 환불이 안 된다는 말이 58개 [m:std.sampling_returns.label.not_returnable]다. 블라인드 구매의 위험을 줄일 미니나 샘플 구성이 사실상의 진입 조건이다.

## 02 경쟁사
**TL;DR** 점수표 상품 중 가중 별점이 가장 높은 Jean Paul Gaultier 4.76★ [m:s.B08FBQWRYC.star]는 말한 지속 시간 중앙값도 6시간 [m:s.B08FBQWRYC.duration_median]으로 가장 길지만 가장 비싸다. 나머지 상품은 값과 상관없이 지속력과 향의 세기가 가장 큰 약점이고, 값이 가장 싼 Bella Vita Luxury는 별점 3.97★ [m:s.B09X5BQ969.star]로 가장 낮다. 업계 사례로는 농도 표기와 명품 향을 닮은 저가 향수(듀프) 고지(Dossier) [r:ind_01] [r:ind_02], 미니와 샘플(Dossier, philosophy) [r:ind_03] [r:ind_11], 공식몰 정품 보증(Lattafa) [r:ind_05]이 있다.

### 점수표 해설
점수표의 농도와 노트 구성 칸은 브랜드 사이트와 소매점 상품 페이지에서 다시 열어 확인한 값이고, 같은 상품인지 확인한 정도는 일치 확인 6개 [m:spec.match_summary]다.

- **Jean Paul Gaultier(Men's Eau de Parfum 노드)**: 153.10달러 [m:s.B08FBQWRYC.price], 온스당 36.45달러 [m:s.B08FBQWRYC.price_per_oz], 별점 4.76★ [m:s.B08FBQWRYC.star], 지속력 부정 7.3% [m:s.B08FBQWRYC.topic_neg]로 가장 낮다. 가장 큰 약점은 배송이다(03장 집중 분석 4). 잘 만든 향도 깨지고 새서 도착하면 점수를 잃는다는 사례다.
- **Calvin Klein**: 115.54달러 [m:s.B00021AJ5I.price], 별점 4.52★ [m:s.B00021AJ5I.star]. 세기 방향 지수 -0.95 [m:s.B00021AJ5I.dir_index]로 세기 불만이 거의 모두 약하다는 쪽이고, 말한 지속 시간 중앙값은 1시간 [m:s.B00021AJ5I.duration_median]이다. 정품 의심 리뷰가 이 상품에 많이 몰린다(03장 집중 분석 4).
- **Glossier**: 82.00달러 [m:s.B0GFGL26JD.price], 온스당 48.24달러 [m:s.B0GFGL26JD.price_per_oz]로 온스당 가장 비싸다. 지속력 부정 12.5% [m:s.B0GFGL26JD.topic_neg], 방향 지수 -0.94 [m:s.B0GFGL26JD.dir_index]로 약하다는 불만이 거의 전부다. 공식 페이지는 피부 가까이 남고 사람마다 다르게 난다고 미리 알리지만 [r:ind_07], 리뷰에서는 값에 비해 오래가지 않는다는 말이 나온다.
- **Dossier**: 26.12달러 [m:s.B0BZDZJDTG.price], 온스당 15.36달러 [m:s.B0BZDZJDTG.price_per_oz], 별점 4.41★ [m:s.B0BZDZJDTG.star], 지속력 부정 10.8% [m:s.B0BZDZJDTG.topic_neg], 방향 지수 -0.75 [m:s.B0BZDZJDTG.dir_index]. 듀프 가격대의 대표 상품으로, 원조 향과 비교당하고 설명한 노트가 안 난다는 불만을 함께 받는다.
- **Elizabeth Taylor(Women's Fragrance Sets 노드)**: 25.73달러 [m:s.B0009OAI8Q.price], 온스당 7.80달러 [m:s.B0009OAI8Q.price_per_oz], 별점 4.66★ [m:s.B0009OAI8Q.star]. 방향 지수 -0.13 [m:s.B0009OAI8Q.dir_index]로 약하다는 불만과 너무 세다는 불만이 비슷하게 섞인다. 말한 지속 시간 중앙값은 약 18분 [m:s.B0009OAI8Q.duration_median]이다.
- **Bella Vita Luxury**: 20.99달러 [m:s.B09X5BQ969.price], 온스당 6.21달러 [m:s.B09X5BQ969.price_per_oz]로 가장 싸고 별점 3.97★ [m:s.B09X5BQ969.star]로 가장 낮다. 지속력 부정 13.6% [m:s.B09X5BQ969.topic_neg]로 가장 높고, 방향 지수 -0.16 [m:s.B09X5BQ969.dir_index]으로 너무 세다는 불만도 많다.

읽는 법: 값과 말한 지속 시간은 같은 방향으로 움직이지 않는다. Glossier는 온스당 가장 비싸지만 말한 지속 시간 중앙값이 2시간 [m:s.B0GFGL26JD.duration_median]이다. 상품마다 시간을 적은 리뷰 수가 적어 중앙값은 방향만 보여 준다.

> "아침 6시 30분에 뿌리면 저녁 6시 30분에도 내 향이 맡힌다." (Bella Vita Luxury, 5★, R3P5BEA6U907NJ)
> "이렇게 비싼데 오래가지 않는다" (Glossier, 2★, RPK76O08CXYUS)

### 하위 카테고리 비교
점수표 상품은 대부분 Women's Eau de Parfum 노드에 있고, Jean Paul Gaultier는 Men's Eau de Parfum, Elizabeth Taylor는 Women's Fragrance Sets 노드로 잡혀 있다. 그래서 하위 카테고리끼리의 비교는 약하다. 시장 데이터로만 보면 Women's Eau de Toilette는 상위 10개 합 44.7% [m:m.top10_share_EDT]에 1위 Versace 9.0% [m:m.top1_EDT]로 몰려 있고, Women's Eau de Parfum은 31.1% [m:m.top10_share_EDP]에 1위 Lattafa 8.0% [m:m.top1_EDP]로 더 흩어져 있다. 2024년 농도별로는 퍼퓸이 43%, 오드퍼퓸이 14% 늘어 [r:mkt_07] 고농도 쪽이 커지는 흐름도 EDP 우선을 뒷받침한다.

### 업계 구조
표의 업계 사례를 개발 결정으로 옮기면 다음과 같다.

- **농도를 숫자로 적는다.** Dossier는 향료 농도 12%를 상세페이지에 적고 오래감의 근거로 쓴다 [r:ind_01]. 지속력 불만이 큰 시장에서 농도 표기는 쉬운 차별점이지만, 농도만으로 지속 시간을 약속할 수는 없다.
- **듀프임을 밝힌다.** Dossier는 명품 향의 영감 제품임을 밝히고 원 브랜드와 무관하다고 고지한다 [r:ind_02]. 듀프로 가면 원조와의 비교를 피할 수 없다.
- **미니와 샘플로 먼저 맡게 한다.** Dossier는 유료 회원에게 3ml 샘플을 준다 [r:ind_03]. philosophy는 같은 향을 2oz 68달러, 4oz 89달러 [r:ind_10]와 0.33oz 펜 스프레이 29달러 [r:ind_11]로 나눠 판다. 2025년 프레스티지 향수에서도 미니 사이즈 인기가 계속 영향을 줬다 [r:mkt_04].
- **공식 판매 경로를 정품 보증으로 쓴다.** Lattafa 북미 공식 온라인몰은 자기 사이트 판매분이 100% 정품이라고 내세운다 [r:ind_05].
- **사람마다 다르게 난다고 미리 알린다.** Glossier You는 피부 가까이 남는 스킨 센트로 소개된다 [r:ind_07].
- **리필.** Mugler는 1992년부터 매장 리필 스테이션을 운영해 왔다 [r:ind_14]. 아마존 첫 제품의 과제는 아니지만 재구매 장치로 기억해 둔다.

## 03 문제
**TL;DR** 가장 흔한 불만은 지속력과 향의 세기 10.0% [m:p.map.longevity_projection]이고, 리뷰어가 말한 지속 시간 중앙값은 1시간 [m:f.longevity.longevity_hours.median]이다. 드물지만 일단 나오면 별점을 가장 크게 깎는 것은 고객 응대(대부분 반품 불가)로, 부정 리뷰 평균 1.28★ [m:p.gap1_neg]이다. 정품 의심의 근거로 가장 많이 댄 것도 약하거나 금방 날아감 41개 [m:f.trust_arrival.fake_suspicion_basis.weak_or_short]라, 지속력은 향 품질과 신뢰를 함께 건드린다.

### 불만 지도
주제별 부정 언급 리뷰어 비율(별점 가중)은 지속력과 향의 세기 10.0% [m:p.map.longevity_projection], 향 6.5% [m:p.map.scent], 신뢰 4.1% [m:p.map.trust] 순이다. 그다음은 가격 대비 가치 2.1% [m:p.map.price_value], 배송 2.1% [m:p.map.shipping], 고객 응대 1.8% [m:p.map.customer_service], 품질 1.7% [m:p.map.quality], 브랜드 경험 1.5% [m:p.map.brand_experience], 병 디자인과 용량 1.4% [m:p.map.bottle_design], 포장 1.3% [m:p.map.packaging], 안전 0.5% [m:p.map.safety]다.

읽는 법: 위 세 주제가 향수 자체(얼마나 가는지, 어떤 냄새인지, 진짜인지)의 문제이고, 아래쪽은 병과 배송, 판매 조건의 문제다. 개발 순서는 위에서 아래로 가되, 아래쪽 가운데 고객 응대(-3.27 [m:p.gap1])와 브랜드 경험(-3.02 [m:p.gap2])은 빈도는 낮아도 별점 격차가 크다.

### 별점 격차
- **고객 응대**: 부정 리뷰 평균 1.28★ [m:p.gap1_neg] 대 나머지 4.54★ [m:p.gap1_other], 격차 -3.27 [m:p.gap1]. 내용은 대부분 향수는 반품이 안 된다는 것이다.
- **브랜드 경험**: 1.51★ [m:p.gap2_neg] 대 4.53★ [m:p.gap2_other], 격차 -3.02 [m:p.gap2]. 다시 사지 않겠다, 추천하지 않는다는 말이고, 예를 들어 분사기 고장 뒤에 붙어 나온다(아래 인용).
- **향**: 2.15★ [m:p.gap3_neg] 대 4.65★ [m:p.gap3_other], 격차 -2.49 [m:p.gap3]. 향이 싫다는 리뷰는 흔하면서 별점도 크게 깎는다.

읽는 법: 별점 격차는 함께 나온 것이지 원인이 아니다. 다만 반품 불가 불만은 판매 조건에서 생기므로, 미니와 샘플, 반품 안내 같은 판매 설계로 줄일 수 있는 몇 안 되는 큰 감점이다.

> "향수는 환불이 안 된다." (Calvin Klein, 1★, R15HIDYPL5720F)
> "앞으로 이 브랜드 제품은 사지 않겠다" (Jean Paul Gaultier, 1★, R3DSZM9BOJ9YFF)

### 집중 분석 1: 지속력과 세기
- **리뷰에 적힌 지속 시간.** 시간을 적은 리뷰 81개 [m:f.longevity.longevity_hours.n]의 중앙값은 1시간 [m:f.longevity.longevity_hours.median]이다. 1시간 미만 31개 [m:f.longevity.longevity_hours.bin0], 1~3시간 32개 [m:f.longevity.longevity_hours.bin1], 3~6시간 9개 [m:f.longevity.longevity_hours.bin2], 6~12시간 7개 [m:f.longevity.longevity_hours.bin3], 12시간 이상 2개 [m:f.longevity.longevity_hours.bin4]다. 리뷰어가 적은 값이라 측정값이 아니고, 벌받는 구간이 어디인지로 읽는다.
- **불만의 방향.** 금방 날아감 231개 [m:std.longevity_strength.label.fades_fast], 처음부터 약함 67개 [m:std.longevity_strength.label.weak_scent], 기대보다 짧음 28개 [m:std.longevity_strength.label.shorter_than_hoped]에 비해 너무 셈은 50개 [m:std.longevity_strength.label.too_strong]다. 약함 쪽 307개 [m:head.dir_low] 대 너무 셈 쪽 50개 [m:head.dir_high]로, 목표는 오래 남는 것이지 세게 퍼지는 것이 아니다.
- **뿌린 양.** 조금 뿌렸다는 리뷰는 21개 중 0개(0.0%) [m:f.longevity.application_amount.light.fades_fast]만 금방 날아간다고 했고, 많이 뿌렸다는 리뷰는 13개 중 10개(76.9%) [m:f.longevity.application_amount.heavy.fades_fast], 덧뿌려야 한다는 리뷰는 12개 중 8개(66.7%) [m:f.longevity.application_amount.reapplied.fades_fast]가 금방 날아간다고 했다. 많이 뿌리고도 날아갔다는 말은 사용법보다 제품 쪽을 가리키는 신호로 읽을 수 있지만, 표본이 작고 함께 나온 것일 뿐이다. 다만 "조금만 뿌려도 오래간다"는 말 자체가 칭찬으로 쓰이는 경우가 많아, 조금 뿌림 쪽에서 0%가 나오기 쉬운 구조일 수 있다(추정).
- **뿌린 곳.** 피부에 뿌렸다는 리뷰는 18개 중 13개(72.2%) [m:f.longevity.application_site.skin.fades_fast], 옷은 19개 중 10개(52.6%) [m:f.longevity.application_site.clothing.fades_fast], 바디 제품 위에 겹친 경우는 6개 중 4개(66.7%) [m:f.longevity.application_site.layered_over_body_product.fades_fast], 손목은 7개 중 2개(28.6%) [m:f.longevity.application_site.wrist_pulse_points.fades_fast], 공중에 뿌리고 지나간 경우는 4개 중 0개(0.0%) [m:f.longevity.application_site.air_mist.fades_fast]가 금방 날아간다고 했다. 옷에 뿌려도 절반 넘게 날아갔다고 하므로 옷에 뿌리라는 안내만으로는 불만을 막기 어렵다(표본 작음).
- **지속력 불만이 정품 의심으로 이어짐.** 정품을 의심하며 근거를 댄 58개 [m:f.longevity.fake_suspicion_basis.total] 중 41개 [m:f.longevity.fake_suspicion_basis.weak_or_short]가 약하거나 금방 날아간다는 것이었다. 새 브랜드도 향이 약하면 "물 탄 것 같다"는 말을 들을 수 있다는 것은 확인이 필요한 추정이다(이 표본은 기존 브랜드 상품뿐이다).

> "정오쯤 뿌린 향수가 완전히 사라졌다." (Calvin Klein, 1★, RITE6TUC3TTUA)
> "30분 뒤 향이 완전히 사라졌다" (Elizabeth Taylor, 4★, R4HVFOK3EB74D)
> "로션을 바르고 피부와 옷에 뿌려도 오래가지 않는다" (Dossier, 2★, RH65DR60CMEZG)
> "아주 세고, 좋은 쪽으로 센 게 아니다" (Bella Vita Luxury, 2★, R1LEPX34SICQ8B)
> "아침 11시쯤 뿌렸는데 밤 8시에도 맡혔다." (Dossier, 5★, R1BPS6WJ0CYY8J)

### 집중 분석 2: 향 정확도
- **리뷰에 나온 노트.** 노트를 말한 210개 [m:f.scent_accuracy.scent_note.total]에서 바닐라가 75개 [m:f.scent_accuracy.scent_note.vanilla]로 가장 많고, 꽃향 50개 [m:f.scent_accuracy.scent_note.floral], 상쾌함과 깨끗함 42개 [m:f.scent_accuracy.scent_note.fresh_clean], 단 향 36개 [m:f.scent_accuracy.scent_note.sweet_gourmand], 앰버 32개 [m:f.scent_accuracy.scent_note.amber_warm] 순이다.
- **방향.** 좋다는 말이 72개 [m:f.scent_accuracy.note_direction.liked]지만 없거나 약하다는 말도 62개 [m:f.scent_accuracy.note_direction.missing_or_weak], 과하다는 말이 46개 [m:f.scent_accuracy.note_direction.too_much]다. 노트와 방향을 짝지은 표에서 가장 많은 짝은 바닐라가 없거나 약하다는 것이고, 알코올은 과하다는 쪽에 몰린다(한 인용에 노트와 방향이 둘 이상씩 있어 짝을 정하지 않은 인용 8개 [m:f.scent_accuracy.note_pairs_unclear]는 빼고 셌다). 상세페이지에 바닐라를 내세웠다면 잔향에서 실제로 바닐라가 맡혀야 한다.
- **비교 대상.** 비교 기준을 말한 175개 [m:f.scent_accuracy.comparison_reference.total] 중 예전에 산 같은 제품이 59개 [m:f.scent_accuracy.comparison_reference.same_product_before], 다른 상품 40개 [m:f.scent_accuracy.comparison_reference.other_product], 밝히지 않은 원래 것 31개 [m:f.scent_accuracy.comparison_reference.original_unspecified], 듀프의 원조 26개 [m:f.scent_accuracy.comparison_reference.dupe_target], 매장에서 산 같은 제품 25개 [m:f.scent_accuracy.comparison_reference.store_purchase]다(한 리뷰가 비교 기준을 여럿 말할 수 있어 다섯 값의 합은 비교 기준을 말한 리뷰 수보다 크다). 이름을 댄 비교는 67개 [m:f.scent_accuracy.comparison_named.n]이고 YSL Black Opium이 가장 자주 나온다.
- **라벨.** 원래 알던 향과 다름 52개 [m:std.scent_accuracy.label.differs_from_original], 정품이나 늘 쓰던 것과 다름 35개 [m:std.scent_accuracy.label.differs_from_genuine], 설명한 노트가 안 남 34개 [m:std.scent_accuracy.label.missing_described_notes], 싸구려 인공 냄새 19개 [m:std.scent_accuracy.label.cheap_artificial], 예전과 달라짐 18개 [m:std.scent_accuracy.label.formula_changed], 알코올 냄새 16개 [m:std.scent_accuracy.label.alcohol_smell]. 이유 없이 향이 싫다는 라벨이 가장 많아 향 취향 자체는 개발로 다 풀 수 없다.

새 브랜드에게 주는 뜻: 기억 속 원조나 예전 병과 비교당하지 않으려면 듀프보다 자기 향으로 가는 편이 비교 기준을 줄인다. 듀프로 간다면 원조 이름과 다르다는 불만(Black Opium 비교)을 각오해야 한다. 어느 쪽이든 배치마다 같은 향이 나야 한다(예전과 달라짐 불만).

> "설명한 은은한 바닐라나 앰버가 없다" (Dossier, 1★, R39RG9GM6NMXFK)
> "딸이 소호 매장에서 산 것과 냄새가 완전히 다르다." (Glossier, 1★, R2A1Z3FMZ4GM7O)
> "그냥 소독용 알코올 냄새가 난다" (Glossier, 1★, R1T8ST53B96R3E)
> "끔찍한 새 제조법!!!" (Glossier, 1★, RE2KNU3LPS61F)
> "생각보다 훨씬 비싼 향이 난다" (Bella Vita Luxury, 5★, R1528CQ8SFSG5O)

### 집중 분석 3: 병과 분사기
- **고장 난 부품과 증상.** 부품 문제를 말한 84개 [m:f.bottle_sprayer.part_failure.total] 중 병에서 샘 29개 [m:f.bottle_sprayer.part_failure.bottle_leak], 분사기가 안 뿜어짐 19개 [m:f.bottle_sprayer.part_failure.sprayer_no_spray], 겉상자나 케이스 훼손 18개 [m:f.bottle_sprayer.part_failure.outer_case_damaged], 분사기 부서짐 10개 [m:f.bottle_sprayer.part_failure.sprayer_broken], 물줄기로 나감 6개 [m:f.bottle_sprayer.part_failure.sprayer_stream], 노즐 걸림 5개 [m:f.bottle_sprayer.part_failure.sprayer_stuck], 뚜껑 없음 5개 [m:f.bottle_sprayer.part_failure.cap_missing], 병 금감 5개 [m:f.bottle_sprayer.part_failure.bottle_cracked], 장식 부서짐 4개 [m:f.bottle_sprayer.part_failure.decoration_broken]다. 이 수에는 받았을 때 망가진 것과 쓰다가 망가진 것이 함께 들어 있다.
- **쓰다가 생기는 고장.** 분사기 불량 13개 [m:std.bottle_sprayer.label.sprayer_defective], 쓰다가 분사기 고장 12개 [m:std.bottle_sprayer.label.sprayer_stopped_working], 부품 빠짐 9개 [m:std.bottle_sprayer.label.missing_parts]. 몇 주나 몇 달 뒤 펌프가 멈췄다는 말이 반복된다.
- **병과 분사기는 칭찬도 많음.** 병과 분사기를 좋게 말한 리뷰가 52개 [m:std.bottle_sprayer.pos]로 부정 37개 [m:std.bottle_sprayer.neg]보다 많다. 자석 뚜껑과 단순한 병이 칭찬받는다.

> "노즐이 눌린 채 다시 올라오지 않아 더 뿌릴 수 없다." (Bella Vita Luxury, 2★, R1WVLWI1BHKZE5)
> "안개처럼 뿌려지지 않고 물줄기로 쏘아진다." (Dossier, 2★, R2C8OYSB7YQ5WR)
> "6주 뒤 펌프가 작동을 멈췄다" (Elizabeth Taylor, 1★, ROVDCAOW4O6LR)
> "단순한 병과 자석 뚜껑은 별 다섯 개" (Dossier, 3★, R3TKPOTESXG4F8)

### 집중 분석 4: 정품 신뢰와 도착
- **정품 의심.** 정품 신뢰 부정 94개 [m:std.authenticity.neg] 중 가짜라고 단정 43개 [m:std.authenticity.label.fake_asserted], 정품인지 의심 36개 [m:std.authenticity.label.authenticity_doubt], 희석되거나 손댄 것 같음 16개 [m:std.authenticity.label.diluted_or_tampered]다.
- **의심의 근거.** 근거를 댄 58개 [m:f.trust_arrival.fake_suspicion_basis.total] 중 약하거나 금방 날아감 41개 [m:f.trust_arrival.fake_suspicion_basis.weak_or_short], 향이 다름 17개 [m:f.trust_arrival.fake_suspicion_basis.smell_differs], 상자나 라벨이 이상함 6개 [m:f.trust_arrival.fake_suspicion_basis.packaging_label], 열린 흔적 2개 [m:f.trust_arrival.fake_suspicion_basis.opened_or_moved], 내용물 색이 다름 1개 [m:f.trust_arrival.fake_suspicion_basis.liquid_color], 값이 너무 쌈 1개 [m:f.trust_arrival.fake_suspicion_basis.cheap_price]다. 겉모양보다 향의 성능이 의심을 부른다.
- **도착 상태.** 깨지거나 부서져 도착 24개 [m:f.trust_arrival.label.arrived_broken], 새서 도착 21개 [m:f.trust_arrival.label.leaked_in_transit], 덜 든 채 도착 6개 [m:f.trust_arrival.label.arrived_underfilled], 다른 상품이나 개봉된 상품 6개 [m:f.trust_arrival.label.wrong_or_opened_item]. 도착 불만은 금속 캔 포장의 Jean Paul Gaultier에 몰려 있다.

> "아마도 물을 탔거나 손을 댄 것 같다" (Dossier, 1★, RE6BXDD0FAGRD)
> "포장과 글씨가 원래 상자와 다르다" (Calvin Klein, 1★, R29L2DLQMAJE18)
> "타깃에서 산 것은 보통 바닐라색이었는데 아마존에서 산 이것은 갈색이었다." (Dossier, 1★, R3LHM29XXXIQ1R)
> "병이 새고 있었고 반쯤만 차 있었다" (Jean Paul Gaultier, 1★, R102M04EISH23G)
> "담겨 오는 캔 전체가 찌그러지고 망가졌다" (Jean Paul Gaultier, 1★, R98NF186B6WVR)

### 안전
안전 부정 리뷰 18개: 두통 8개(가중 0.2%), 메스꺼움 5개(가중 0.1%), 호흡 2개(가중 0.1%), 어지럼 1개(가중 0.0%), 알레르기 언급 2개(가중 0.1%) [m:p.safety_text]. 피부 발진 같은 피부 반응은 판정에서 나오지 않았다. 두통과 메스꺼움 인용 몇 개는 너무 세다는 리뷰와 같은 리뷰에서 나오지만, 함께 나온 것이지 원인으로 단정할 수 없다. 빈도는 낮아도 이상 반응은 규제(MoCRA)와 IFRA 기준을 지켜야 하는 영역이고 [r:reg_20] [r:reg_08], hypoallergenic 같은 표시는 흔히 RIPT나 HRIPT 결과를 근거로 쓰이지만 [r:tst_26], 우리 완제품 시험 결과가 없으므로 쓰지 않는다.

> "1분 안에 두통이 온다" (Jean Paul Gaultier, 1★, R2MJO4BBCWGL72)
> "천식이 도졌다" (Elizabeth Taylor, 3★, R3HTG089Q8UVI8)

## 04 포지셔닝
**TL;DR** 듀프 가격대의 여성 EDP로 들어가, 지속력을 시험으로 보증하되 세지 않게 만드는 것을 개선 가설로 삼는다. 이번 표본에서 가장 큰 약점이 지속력과 향의 세기인 상품이 6개 중 5개(리뷰를 다시 뽑아 보면 3~5개) [m:head.topic_weakest]이기 때문이다. 반품이 어려운 상품이라는 감점(고객 응대 격차 -3.27 [m:p.gap1])은 미니와 샘플로 줄이고, 깨짐과 샘은 포장 시험으로 막는다. 아래 가격과 SOM은 확인이 필요한 권고다.

### 한 줄 포지션
듀프 값으로 사는, 설명한 노트가 그대로 오래 남고 세지 않은 여성 EDP. 미니로 먼저 맡아 보고 본품을 산다.

### 이기는 이유
- **이번 표본에서 가장 큰 약점이 겹친다.** 이번 표본에서 가장 큰 약점이 지속력과 향의 세기인 상품이 6개 중 5개(리뷰를 다시 뽑아 보면 3~5개) [m:head.topic_weakest]이고, 이를 개선 가설로 삼는다. 값이 싼 Bella Vita Luxury 20.99달러 [m:s.B09X5BQ969.price]와 비싼 Calvin Klein 115.54달러 [m:s.B00021AJ5I.price] 모두 이 표본에서 같은 약점이 가장 크게 나왔다.
- **방향이 분명하다.** 약함 307개 대 너무 셈 50개(6.14배) [m:head.dir_ratio]. 오래 남되 퍼짐은 은은하게라는 목표가 데이터로 정해진다.
- **지속력 불만과 정품 의심이 함께 나온다.** 정품 의심 근거 58개 [m:f.trust_arrival.fake_suspicion_basis.total] 중 41개 [m:f.trust_arrival.fake_suspicion_basis.weak_or_short]가 약하거나 금방 날아간다는 것이었다. 정품을 의심한 리뷰에서 약하거나 금방 날아간다는 말이 함께 나온다는 뜻으로 읽는다.
- **판매 설계로 줄일 수 있는 감점.** 반품 불가 불만 58개 [m:std.sampling_returns.label.not_returnable]는 향수라서, 아마존 규정이나 위험물이라서, 반품 옵션이 없어서 반품이나 환불을 할 수 없다는 말이다(라벨 정의). 미니와 샘플은 업계에서 이미 쓰는 방법이고 [r:ind_03] [r:ind_11], 미니 사이즈 인기도 확인된다 [r:mkt_04].

### 소비자 기준표
기준마다 감점 기준은 리뷰에서 감점이 나오는 지점, 만족 기준은 부정이 가장 적은 상품의 수준, 개발 기준은 확인된 조사 근거가 있는 사양이나 시험, 상세페이지 문구는 그 근거가 있을 때만 쓸 문장이다.

#### 기준 1: 지속력과 세기
- 감점 기준: 리뷰어가 말한 지속 시간 중앙값 1시간 [m:f.longevity.longevity_hours.median], 1~3시간 구간까지가 불만의 몸통이다(1시간 미만 31개 [m:f.longevity.longevity_hours.bin0], 1~3시간 32개 [m:f.longevity.longevity_hours.bin1]). 부정 357개 [m:std.longevity_strength.neg], 가중 10.8% [m:std.longevity_strength.neg_pct]이고 너무 셈 50개 [m:std.longevity_strength.label.too_strong]도 감점이다. 값에 비해 오래가지 않는다는 말도 4개 [m:std.longevity_strength.label.not_lasting_for_price] 있고, 대부분 Dossier에서, 나머지는 Glossier에서 나왔다.
- 만족 기준: 부정이 가장 적은 상품은 Jean Paul Gaultier 8.7% [m:std.longevity_strength.best]이고, 이 상품의 말한 지속 시간은 값 7개, 중앙값 6시간 [m:std.spec.longevity_strength.B08FBQWRYC.duration]이다. 다만 이 상품은 Men's Eau de Parfum [m:std.longevity_strength.best_sub] 노드 상품이라 여성 EDP의 기준으로 그대로 옮기기 어렵다. 여성 상품 가운데 가장 나은 상품은 Elizabeth Taylor 9.2% [m:std.longevity_strength.best_women]이고, 말한 지속 시간은 값 6개, 중앙값 약 18분 [m:std.spec.longevity_strength.B0009OAI8Q.duration]이다. 두 상품 모두 말한 지속 시간 값이 적어 시간 기준으로 삼기 어렵다. 여성 상품 중 부정이 가장 적은데 말한 시간은 가장 짧다는 점은 값이 6개라 해석하지 않는다. 만족 리뷰는 140개 [m:std.longevity_strength.pos]로, 아침에 뿌려 밤까지 맡힌다는 말이 대표적이다.
- 개발 기준: 목표 지속 시간 숫자는 리뷰에서 정하지 않고, 시제품을 소비자 감각 시험(ASTM E1958)에 부쳐 그 결과로 정한다 [r:tst_01]. 세기는 ASTM E544의 냄새 세기 기준 비교로 잰다 [r:tst_02]. 숫자 주장에는 합리적 근거가 있어야 한다 [r:tst_09]. 점수표 상품의 농도 표기는 Calvin Klein Eau de Parfum [m:spec.B00021AJ5I.concentration], Dossier Eau de Parfum, 15% [m:spec.B0BZDZJDTG.concentration], Elizabeth Taylor Eau de Toilette [m:spec.B0009OAI8Q.concentration], Bella Vita Luxury Eau De Parfum [m:spec.B09X5BQ969.concentration], Jean Paul Gaultier intense eau de parfum [m:spec.B08FBQWRYC.concentration], Glossier Eau de parfum [m:spec.B0GFGL26JD.concentration]이다. 상품이 적어 농도와 지속력 불만의 관계는 말하지 않는다. 향료 농도를 상세페이지에 적는 업계 사례가 있지만 [r:ind_01], 피부 지속 시간을 재는 ISO나 ASTM 공식 표준은 찾지 못했다. 우리 농도 값은 확인 필요(조사 근거 없음). 향료 20% 이하로 설계하면 캘리포니아 VOC 한도를 따져야 한다 [r:reg_12].
- 상세페이지 문구: "피부 가까이 오래, 주변에는 은은하게." (분사 횟수와 지속 시간 문구는 정한 사용 조건의 감각 시험 뒤 확정한다. 지속 시간 숫자는 감각 시험 결과가 나온 뒤에만 넣는다)

#### 기준 2: 향 정확도와 일관성
- 감점 기준: 부정 141개 [m:std.scent_accuracy.neg], 가중 3.3% [m:std.scent_accuracy.neg_pct]. 원래 알던 향과 다름 52개 [m:std.scent_accuracy.label.differs_from_original], 설명한 노트가 안 남 34개 [m:std.scent_accuracy.label.missing_described_notes], 알코올 냄새 16개 [m:std.scent_accuracy.label.alcohol_smell]. 특히 바닐라를 말한 75개 [m:f.scent_accuracy.scent_note.vanilla]에서 없거나 약하다는 쪽이 가장 많다.
- 만족 기준: 부정이 가장 적은 상품은 Jean Paul Gaultier 1.5% [m:std.scent_accuracy.best], 만족 리뷰 94개 [m:std.scent_accuracy.pos]. 예를 들어 생각보다 훨씬 비싼 향이 난다는 칭찬이 있다(R1528CQ8SFSG5O).
- 개발 기준: 공식 노트로 적을 노트가 첫 향에서만이 아니라 잔향 단계에서도 맡히는지 시제품으로 확인한 뒤 노트 목록을 정한다. 근거는 점수표 상품의 공식 노트 구성과 리뷰가 말한 노트를 나란히 놓은 표다. 예를 들어 Dossier는 공식 노트의 베이스에 바닐라가 있고, 노트를 말한 리뷰 81개 [m:std.spec.scent_accuracy.B0BZDZJDTG.said] 가운데 공식 노트나 그 계열을 말한 리뷰가 75개 [m:std.spec.scent_accuracy.B0BZDZJDTG.mention]이며, 설명한 노트가 안 남 리뷰는 32개 [m:std.spec.scent_accuracy.B0BZDZJDTG.missing]다(그 리뷰들이 말한 노트는 표에 있다). 상품이 적어 공식 노트 구성과 이 불만을 원인으로 잇지 않고 나란히 놓기만 한다. 노트별 잔향 확인 방법(몇 시간 뒤 어떤 노트가 남는지를 누가 어떻게 맡는지)은 확인 필요(조사 근거 없음). 배치마다 같은 향이 나도록 화장품 GMP(ISO 22716)로 생산과 관리, 보관을 관리하고 [r:tst_07], 안정성 시험 조건과 기준은 ISO/TR 18811을 참고해 우리가 정하고 근거를 남긴다 [r:tst_08]. 성분 표기는 많은 순서로 적되 향료는 fragrance로 묶을 수 있다 [r:reg_03].
- 상세페이지 문구: "첫 향: (노트), 중간 향: (노트), 잔향: (노트). 그 단계에서 실제로 맡히는 노트만 적었습니다." (공식 노트 구성은 단계별로 적되, 시제품에서 그 단계에 맡히는 것으로 확인된 노트만 올린다. 바닐라처럼 많이 찾는 노트도 잔향에서 맡히지 않으면 적지 않는다. "확인했다"는 표현은 확인 기록이 생긴 뒤에만 쓴다 [r:tst_10])

#### 기준 3: 정품 신뢰
- 감점 기준: 부정 94개 [m:std.authenticity.neg], 가중 2.2% [m:std.authenticity.neg_pct]. 의심의 근거는 약하거나 금방 날아감 41개 [m:f.trust_arrival.fake_suspicion_basis.weak_or_short]가 가장 많고, 상자나 라벨이 이상함 6개 [m:f.trust_arrival.fake_suspicion_basis.packaging_label], 열린 흔적 2개 [m:f.trust_arrival.fake_suspicion_basis.opened_or_moved]가 뒤따른다.
- 만족 기준: 부정이 가장 적은 상품은 Elizabeth Taylor 0.4% [m:std.authenticity.best], 정품이 맞다는 리뷰는 17개 [m:std.authenticity.pos]뿐이다. 정품은 칭찬받는 항목이 아니라 감점을 피하는 항목이다.
- 개발 기준: 공식 판매 경로 직판을 정품 보증으로 쓰는 업계 사례가 있다 [r:ind_05]. 배치 번호와 제조 기록은 GMP(ISO 22716)로 남긴다 [r:tst_07]. 개봉 방지 봉인과 배치 조회 방식의 사양은 확인 필요(조사 근거 없음).
- 상세페이지 문구: "브랜드가 직접 보내는 정품입니다. 상자에 열린 흔적이 있으면 바로 알려 주세요."

#### 기준 4: 병과 분사기
- 감점 기준: 부정 37개 [m:std.bottle_sprayer.neg], 가중 0.8% [m:std.bottle_sprayer.neg_pct]와 별개로 부품 문제를 말한 리뷰가 84개 [m:f.bottle_sprayer.part_failure.total]다(받았을 때 망가진 것 포함). 병에서 샘 29개 [m:f.bottle_sprayer.part_failure.bottle_leak], 안 뿜어짐 19개 [m:f.bottle_sprayer.part_failure.sprayer_no_spray], 물줄기 6개 [m:f.bottle_sprayer.part_failure.sprayer_stream], 쓰다가 고장 12개 [m:std.bottle_sprayer.label.sprayer_stopped_working].
- 만족 기준: 부정이 가장 적은 상품은 Calvin Klein 0.3% [m:std.bottle_sprayer.best]. 만족 리뷰 52개 [m:std.bottle_sprayer.pos]에서 자석 뚜껑, 단순하고 잘 만든 병이 칭찬받는다.
- 개발 기준: 점수표 상품의 브랜드 사이트와 소매점 상품 페이지에서는 병과 분사기 사양을 확인하지 못했다. 망가진 부품을 말한 리뷰가 가장 많은 상품은 Jean Paul Gaultier 43개 [m:std.spec.bottle_sprayer.B08FBQWRYC.parts]이고(받았을 때 망가진 것 포함), 그래서 받았을 때와 쓰는 동안을 모두 시험 범위에 넣는다. 빈 용기의 누수 저항은 ASTM D4991(항공 운송 같은 압력 차 조건)로 시험한다 [r:tst_03]. 분사기는 소비자 제품 펌프 전반에 쓰는 ASTM 방법으로 잰다: 처음 뿜어질 때까지 누르는 횟수는 ASTM D3890 [r:tst_30], 1회 분사량은 ASTM D4336 [r:tst_31](펌프마다 분사량을 견줘 사용량 안내와 규격을 정하는 데 쓰임 [r:tst_32]), 분사 모양은 ASTM D4041 [r:tst_33]이다. 이 세 표준은 향수 전용이 아니라 소비자 제품 펌프 전반의 방법이고, 분사 모양은 분사 버튼 설계와 액체 성질에 따라 크게 달라지므로 [r:tst_34] 우리 향수 액을 넣은 상태로 시험한다. 오래 눌러도 고장 나지 않는지 보는 작동 횟수 시험의 표준과 각 시험의 합격 기준 값은 확인 필요(조사 근거 없음).
- 상세페이지 문구: "고운 안개로 뿌려지는 펌프, 딸깍 닫히는 자석 뚜껑."

#### 기준 5: 도착 상태와 포장
- 감점 기준: 부정 56개 [m:std.arrival_packaging.neg], 가중 1.9% [m:std.arrival_packaging.neg_pct]. 깨져 도착 24개 [m:std.arrival_packaging.label.arrived_broken], 새서 도착 21개 [m:std.arrival_packaging.label.leaked_in_transit], 덜 든 채 도착 6개 [m:std.arrival_packaging.label.arrived_underfilled], 다른 상품이나 개봉된 상품 6개 [m:std.arrival_packaging.label.wrong_or_opened_item].
- 만족 기준: 부정이 가장 적은 상품은 Bella Vita Luxury 0.0% [m:std.arrival_packaging.best], 만족 리뷰 25개 [m:std.arrival_packaging.pos]에서 상자가 예쁘고 병을 잘 보호한다는 말이 나온다.
- 개발 기준: 택배 운송 충격은 ISTA 3A로 [r:tst_05], 운송 단위의 유통 환경 내성은 ASTM D4169로 시험한다 [r:tst_06]. 병은 밀봉 2차 포장에 넣고 깨짐과 누수를 막는 흡수재를 쓴다 [r:reg_17]. 인화성 용제(에탄올 등)를 포함한 향료 제품은 UN1266, 3급 인화성 액체로 분류되므로 [r:reg_19] 우리 제품 조성과 운송 경로로 확인하고, 에탄올 함유 제품의 항공 우편은 사전 서면 승인이 필요하다 [r:reg_18].
- 상세페이지 문구: "깨짐과 샘을 막는 밀봉 이중 포장으로 보냅니다."

#### 기준 6: 피부와 몸 반응
- 감점 기준: 안전 부정 18개 [m:std.skin_body.neg](알레르기 언급 2개 [m:p.safety.알레르기 언급] 포함), 가중 0.5% [m:std.skin_body.neg_pct]. 두통 8개 [m:p.safety.두통], 메스꺼움 5개 [m:p.safety.메스꺼움], 호흡 2개 [m:p.safety.호흡], 어지럼 1개 [m:p.safety.어지럼], 알레르기 언급 2개 [m:p.safety.알레르기 언급].
- 만족 기준: 부정이 가장 적은 상품은 Glossier 0.0% [m:std.skin_body.best]다. 이번 표본에서 이 상품의 안전 부정 리뷰가 0건이라는 뜻이고, 안전성 비교를 입증하는 시험 결과가 아니다. 몸 반응이 없었다는 리뷰(안전 주제 긍정 태그)는 4개 [m:std.skin_body.pos_tags]뿐이라, 이 기준은 만족을 얻는 곳이 아니라 감점과 규제 위험을 막는 곳이다.
- 개발 기준: 향료 원료는 IFRA 기준(51차 개정의 새 기준 [r:reg_20], 52차 개정 진행 [r:reg_21])에 맞춘다. 점수표 상품 가운데 표시 알레르기 성분을 확인한 상품은 6개 중 4개 [m:std.spec.skin_body.allergen_products]다. 이 성분은 공개된 전 성분에 든 EU 표시 대상 성분을 이름으로 골라낸 것이고(상품별 성분은 표에 있다), 이상 반응 리뷰가 적어 성분과 증상의 관계는 말하지 않는다. 미국에서는 MoCRA 조문이 라벨에 향료 알레르겐을 하나하나 적도록 하고 [r:reg_33], FDA가 표시 기준 농도를 정할 수 있게 했다 [r:reg_35]. 법은 규칙안을 2022년 12월 29일부터 18개월 안에 내도록 정했지만 [r:reg_34], 2026년 2월 기준 FDA는 규칙안을 아직 작성 중이었다 [r:reg_09]. 규칙안 목표 시점은 2025년 9월 정리 자료에서 2026년 5월이었다가 [r:reg_08] 2026년 7월 연방 규제 일정에서 2026년 11월로 다시 미뤄졌다 [r:reg_36]. 거듭 미뤄져 왔으므로 한 날짜로 잡지 않고, 확정 규칙과 기준 농도가 없으니 출시 시점에 다시 확인한다. 참고로 EU는 피부에 남는 제품(향수 포함)의 향료 알레르겐이 0.001%를 넘으면 하나하나 표시하게 하고 [r:reg_28], 늘어난 표시 대상은 새로 내놓는 제품은 2026년 7월 31일까지, 이미 시장에 있는 제품은 2028년 7월 31일까지 맞춰야 한다 [r:reg_29]. 표시 대상 수는 자료마다 다르게 적는다 [r:reg_26] [r:reg_27]. 워싱턴주는 특정 독성 물질을 제한하며 [r:reg_13], 제한 물질이 향료 조성물(고정제 등) 안에 들어 있어도 의도적 첨가로 본다 [r:reg_14]. 피부 감작은 향료 업계(RIFM)의 사람 반복 첩포 시험(HRIPT) 프로토콜을 참고한다: 유도기와 유발기 두 단계로 [r:tst_11], 같은 자리에 3주 동안 9번 패치를 붙이고 [r:tst_13], 약 2주 쉰 뒤 처음 쓰는 부위에 한 번 붙여 감작을 본다 [r:tst_14]. 이 시험은 정해진 농도에서 감작이 없음을 확인하는 용도이고 [r:tst_16], 자원자에게 감작을 일으킬 수 있어 이득이 위험보다 훨씬 클 때만 드물게 해야 한다는 비판적 견해도 있다 [r:tst_21]. RIFM 프로토콜은 향료 원료를 용매에 녹여 붙이는 방법이고 [r:tst_12], 완제품 예시로는 반밀폐 패치를 주 3번씩 3주 붙인 사례가 있다 [r:tst_22]. HRIPT 자료는 논문 원문이 아니라 초록으로 확인했다. 시험 기관 설명으로 완제품 RIPT 패널은 보통 50~200명이고 [r:tst_25], 완제품 시험의 합격 기준과 시험 기관은 확인 필요(조사 근거 없음).
- 상세페이지 문구: "IFRA 기준에 맞춰 조향했습니다. 처음에는 손목에 한 번 뿌려 보세요." (hypoallergenic, 피부과 테스트 완료 같은 표시는 흔히 RIPT나 HRIPT 결과를 근거로 쓰이지만 [r:tst_26], 우리 완제품 시험 결과가 없으므로 쓰지 않는다)

#### 기준 7: 시향과 반품
- 감점 기준: 부정 74개 [m:std.sampling_returns.neg], 가중 1.6% [m:std.sampling_returns.neg_pct]. 반품이나 환불 불가 58개 [m:std.sampling_returns.label.not_returnable], 환불이나 교체 요청 11개 [m:std.sampling_returns.label.refund_request], 반품 기간 놓침 5개 [m:std.sampling_returns.label.return_window_missed]. 고객 응대 부정 리뷰의 평균 별점은 1.28★ [m:p.gap1_neg]까지 떨어진다.
- 만족 기준: 부정이 가장 적은 상품은 Jean Paul Gaultier 0.3% [m:std.sampling_returns.best]. 이 기준에서 칭찬받은 리뷰는 0개 [m:std.sampling_returns.pos]라, 목표는 감점을 없애는 것이다.
- 개발 기준: 본품과 같은 향의 미니(펜 스프레이 크기)를 함께 낸다. philosophy는 0.33oz 펜 스프레이를 따로 팔고 [r:ind_11], Dossier는 3ml 샘플을 준다 [r:ind_03]. 미니 크기와 가격, 아마존 반품 정책 문구는 확인 필요(조사 근거 없음).
- 상세페이지 문구: "향수는 개봉 뒤 반품이 어려울 수 있습니다. 미니로 먼저 맡아 보세요."

> "위험물이라서 반품할 수 없다(?)" (Calvin Klein, 1★, R2NKW7XTDK219O)

### 하위 카테고리별 출시 계획
확인이 필요한 권고다.

- **첫째, Women's Eau de Parfum 본품과 미니.** 리뷰 근거가 가장 많은 노드이고, 상위 10개 합 31.1% [m:m.top10_share_EDP]로 흩어져 있다. 2024년 오드퍼퓸 매출이 14% 늘었다 [r:mkt_07].
- **둘째, 미니와 디스커버리 세트(Women's Fragrance Sets).** 블라인드 구매 위험을 줄이는 판매 설계이자 별도 상품이다. 미니 사이즈 인기는 외부 조사에서도 확인된다 [r:mkt_04]. 점수표에서 이 노드 상품은 Elizabeth Taylor 하나뿐이라 리뷰 근거는 약하다.
- **셋째, 헤어 퍼퓸 스프레이.** 성장 배수가 가장 큰 검색어가 "hair perfume spray" 최근 4주 530,006, 1년 전 같은 4주 11,322, 46.81배 [m:head.fastest_term]이고, 2024년 헤어 프래그런스 매출이 32% 늘었다 [r:mkt_08]. 이번 리뷰 표본에는 헤어 퍼퓸 리뷰가 없어 사용 불만은 따로 조사해야 한다.
- **후순위, Women's Eau de Toilette.** 상위 10개 합 44.7% [m:m.top10_share_EDT], 1위 Versace 9.0% [m:m.top1_EDT]로 더 몰려 있다.

### 가격 구조
확인이 필요한 권고다.

- **본품은 첫 가격 구간 안에서.** 브랜드 평균 가격 15.76~56.22 [m:m.price_band1_range] 구간이 매출 비중 39.2% [m:m.price_band1_share]로 가장 크고, 별점은 다른 구간과 큰 차이가 없다(4.40★ [m:m.price_band1_rating] 대 4.49★ [m:m.price_band2_rating]). 듀프 가격대의 Dossier가 26.12달러 [m:s.B0BZDZJDTG.price], 온스당 15.36달러 [m:s.B0BZDZJDTG.price_per_oz]다.
- **값을 올려도 지속력 불만은 사라지지 않는다.** 값에 비해 오래가지 않는다는 불만 4개 [m:std.longevity_strength.label.not_lasting_for_price] 가운데 대부분은 값이 싼 축의 Dossier에서 나왔고, 나머지는 Glossier에서 나왔다. 온스당 48.24달러 [m:s.B0GFGL26JD.price_per_oz]로 온스당 가장 비싼 Glossier에서도 비싼데 오래가지 않는다는 리뷰가 있다(RPK76O08CXYUS).
- **사다리는 미니와 본품 두 단.** philosophy는 2oz 68달러, 4oz 89달러 [r:ind_10] 위에 0.33oz 29달러 [r:ind_11]를 둔다. 미니 값은 본품을 사기 전 시향 비용으로 설계한다. 구체 가격과 마진은 원가와 광고비가 정해진 뒤 정한다: 확인 필요.

> "50달러를 썼는데 좋은 냄새는 한두 시간뿐이다" (Dossier, 3★, R26U67LD084EK3)

### 메시지와 키워드
- **메시지 하나: 오래, 하지만 은은하게.** 약함 307개 [m:head.dir_low] 대 너무 셈 50개 [m:head.dir_high]. 지속 시간 숫자는 감각 시험 근거가 생긴 뒤에만 쓴다 [r:tst_10].
- **메시지 둘: 적힌 노트 그대로.** 설명한 노트가 안 남 34개 [m:std.scent_accuracy.label.missing_described_notes]. 바닐라처럼 많이 찾는 노트를 내세울 때는 잔향에서 확인된 것만 적는다.
- **메시지 셋: 미니로 먼저.** 반품 불가 불만 58개 [m:std.sampling_returns.label.not_returnable].
- **메시지 넷: 브랜드가 직접, 안전하게 도착.** 깨져 도착 24개 [m:f.trust_arrival.label.arrived_broken], 새서 도착 21개 [m:f.trust_arrival.label.leaked_in_transit].
- **키워드.** 공통 검색어 합 3,213,197 [m:m.terms_common_volume]과 여성 검색어 합 1,022,775 [m:m.terms_female_volume]의 차이는 검색어 수와 브랜드 이름 검색어에서도 오므로 제목 낱말 순서의 근거가 되지 않는다. 개별 검색량은 vanilla perfume 94,475 [m:std.scent_accuracy.term.vanilla perfume]이고, 제목 앞쪽에 vanilla perfume 같은 향 낱말을 두고 perfumes for women을 뒤에 두는 순서는 확인이 필요한 권고다. long lasting perfume은 검색량 미확인이라 근거 없이 넣지 않는다. 미니에는 mini perfume 37,436 [m:std.bottle_sprayer.term.mini perfume], travel perfume 34,634 [m:std.bottle_sprayer.term.travel perfume], 세 번째 단계에는 hair perfume spray를 쓴다. 상세페이지 문구는 이 장의 한국어 초안을 영어로 옮겨 쓴다.

### 실행 순서
- 시장 숫자의 단위부터 확인한다(월 매출 칸, 점유율, 증감 칸). 확인되면 SOM과 가격을 다시 잡는다.
- 향 개발: 오래 남되 세지 않은 EDP, 내세울 노트(바닐라 등)가 잔향에 남는지 확인.
- 감각 시험으로 지속 시간과 세기를 잰다. 결과가 상세페이지 숫자의 유일한 출처다.
- 용기와 분사기를 고르고 누수 시험을 한다.
- 규제 확인(라벨, IFRA, 주 법, MoCRA 알레르겐 진행 상황).
- 포장과 운송 시험, 위험물 운송 경로 확정.
- 미니를 본품과 함께 내고, 상세페이지에 반품 안내와 노트 설명을 넣는다.
- 출시 뒤 리뷰를 기준표의 감점 기준과 대조한다.

### 개발 단계와 관문
- **단계 A, 향과 농도.** 관문: 감각 시험(ASTM E1958) 결과로 지속 시간 주장을 정한다 [r:tst_01]. 세기는 ASTM E544로 잰다 [r:tst_02]. 비교 기준은 리뷰어가 말한 지속 시간 중앙값 1시간 [m:f.longevity.longevity_hours.median]이다. 목표 시간은 감각 시험으로 정한다(부정이 가장 적은 상품은 남성 향수이고 값이 7개라 비교에 쓰지 않는다). 캘리포니아 VOC 한도 검토 [r:reg_12].
- **단계 B, 배치 일관성.** 관문: GMP(ISO 22716) 기록 [r:tst_07], 안정성 시험(ISO/TR 18811) [r:tst_08]. 예전과 달라짐 불만 18개 [m:std.scent_accuracy.label.formula_changed]를 피하려면 배치마다 같은 향이어야 한다.
- **단계 C, 용기와 분사기.** 관문: ASTM D4991 누수 시험 통과 [r:tst_03]. 분사는 소비자 제품 펌프 전반에 쓰는 ASTM 방법으로 우리 향수 액을 넣은 상태에서 잰다: 처음 뿜어질 때까지 누르는 횟수 ASTM D3890 [r:tst_30], 1회 분사량 ASTM D4336 [r:tst_31], 분사 모양 ASTM D4041 [r:tst_33](분사 버튼 설계와 액체 성질에 따라 크게 달라짐 [r:tst_34]). 이 방법들은 향수 전용이 아니고, 작동 횟수(내구) 시험의 표준과 각 시험의 합격 기준 값은 확인 필요(조사 근거 없음). 병에서 샘 29개 [m:f.bottle_sprayer.part_failure.bottle_leak], 안 뿜어짐 19개 [m:f.bottle_sprayer.part_failure.sprayer_no_spray]가 넘어야 할 선이다.
- **단계 D, 규제와 라벨.** 관문: 성분 표기 [r:reg_03], IFRA 기준 [r:reg_20], 워싱턴주 제한 물질 [r:reg_13], MoCRA 향료 알레르겐 표시 [r:reg_33]. 2026년 2월 기준 FDA는 규칙안을 아직 작성 중이었고 [r:reg_09], 목표 시점은 2026년 5월이었다가 [r:reg_08] 2026년 11월로 다시 미뤄졌다 [r:reg_36]. 거듭 미뤄져 왔으므로 한 날짜로 잡지 않고, 출시 시점에 확정 규칙과 표시 기준 농도 [r:reg_35]를 다시 확인한다.
- **단계 E, 포장과 운송.** 관문: ISTA 3A [r:tst_05], ASTM D4169 [r:tst_06] 통과, 밀봉 2차 포장과 흡수재 [r:reg_17]. 인화성 용제(에탄올 등)를 포함한 향료 제품은 UN1266, 3급 인화성 액체로 분류되므로 [r:reg_19] 우리 제품 조성과 운송 경로로 확인한 뒤 운송 경로를 확정한다. 아마존 FBA 위험물 절차는 확인 필요(조사 근거 없음).
- **단계 F, 상세페이지와 출시.** 관문: 모든 숫자 주장에 근거 자료 [r:tst_09] [r:tst_10]. 미니 동시 출시, 반품 안내 문구.

## 05 한 장 요약
### 제품 해부도
1. **뚜껑**: 자석으로 딸깍 닫히는 뚜껑, 출고 때 빠짐 검사 (뚜껑 없음 5개 [m:f.bottle_sprayer.part_failure.cap_missing], 자석 뚜껑은 칭찬받음)
2. **분사기와 노즐**: 고운 안개, 눌린 채 걸리지 않는 펌프 (안 뿜어짐 19개 [m:f.bottle_sprayer.part_failure.sprayer_no_spray], 물줄기 6개 [m:f.bottle_sprayer.part_failure.sprayer_stream], 분사 시험 기준은 확인 필요)
3. **목과 밀봉**: 누수 시험 통과한 체결부 (병에서 샘 29개 [m:f.bottle_sprayer.part_failure.bottle_leak], ASTM D4991 [r:tst_03])
4. **병 유리**: 단순하고 두꺼운 병, 운송 충격에 견딤 (병 금감 5개 [m:f.bottle_sprayer.part_failure.bottle_cracked], 깨져 도착 24개 [m:f.trust_arrival.label.arrived_broken])
5. **향의 지속과 세기**: 오래 남되 퍼짐은 은은하게, 지속 시간은 감각 시험으로 입증 (말한 지속 시간 중앙값 1시간 [m:f.longevity.longevity_hours.median], 약함 307개 [m:head.dir_low] 대 너무 셈 50개 [m:head.dir_high])
6. **향 구성**: 적은 노트가 잔향까지 맡힘, 알코올 냄새가 앞서지 않음 (바닐라 언급 75개 [m:f.scent_accuracy.scent_note.vanilla], 없거나 약함 62개 [m:f.scent_accuracy.note_direction.missing_or_weak])
7. **라벨과 성분 표기**: 성분은 많은 순서, 향료는 fragrance, 배치 번호 (상자나 라벨이 이상해 정품을 의심한 6개 [m:f.trust_arrival.fake_suspicion_basis.packaging_label], 21 CFR 701.3 [r:reg_03])
8. **겉상자와 운송 포장**: 밀봉 2차 포장과 흡수재, 찌그러지지 않는 상자 (겉상자 훼손 18개 [m:f.bottle_sprayer.part_failure.outer_case_damaged], 새서 도착 21개 [m:f.trust_arrival.label.leaked_in_transit], ISTA 3A [r:tst_05])

### 단계와 관문
- **향과 농도**: 감각 시험으로 지속 시간과 세기 확정 [r:tst_01]. 비교 기준은 리뷰어가 말한 중앙값 1시간 [m:f.longevity.longevity_hours.median]이고, 목표 시간은 감각 시험으로 정한다(부정이 가장 적은 상품은 남성 향수이고 값이 7개라 비교에 쓰지 않음).
- **배치 일관성**: GMP와 안정성 시험 [r:tst_07] [r:tst_08].
- **용기와 분사기**: 누수 시험 [r:tst_03], 분사 시험은 소비자 제품 펌프 전반의 방법(ASTM D3890, D4336, D4041)을 우리 향수 액으로 [r:tst_30] [r:tst_31] [r:tst_33] [r:tst_34]. 내구(작동 횟수) 시험 기준은 확인 필요.
- **규제와 라벨**: 성분 표기, IFRA, 주 법 [r:reg_03] [r:reg_20] [r:reg_13]. MoCRA 향료 알레르겐 표시 [r:reg_33]는 규칙안 목표 시점이 거듭 미뤄져 와 [r:reg_09] [r:reg_08] [r:reg_36] 한 날짜로 잡지 않고 출시 시점에 확정 규칙을 다시 확인.
- **포장과 운송**: ISTA 3A, ASTM D4169, 밀봉 2차 포장 [r:tst_05] [r:tst_06] [r:reg_17].
- **상세페이지와 출시**: 숫자 주장마다 근거 [r:tst_09], 미니 동시 출시, 반품 안내. 출시 뒤 지속력과 향의 세기를 부정으로 언급한 리뷰어 비율(가중)을 이번에 고른 상품 6개 표본의 10.0% [m:head.topic_neg]와 참고로 대조한다.

> "공중에 뿌리고 그 사이로 지나간다" (Dossier, 5★, R21IFXQ51DU8CY)
> "포장도 예쁘고 병을 잘 보호한다" (Dossier, 5★, R2BG8L01VQAU1S)

## A 데이터와 방법
### 출처
- **리뷰**: 공유 리뷰 DB에서 받은 아마존 미국 리뷰(점수표의 상품들). 주제와 감성 태그, 세부 이슈 라벨, 설계 정보 항목(말한 지속 시간, 뿌린 곳과 양, 노트, 망가진 부품, 정품 의심 근거 등)을 붙였다. 파일과 개수는 아래 표에 있다.
- **시장 데이터**: spd-amz-market(하위 카테고리, 브랜드 점유율, 검색어). 매출, 점유율, 증감 칸은 단위 미확인이다.
- **웹 조사**: 웹 조사 파일에서 다시 열어 원문 문장을 확인한 주장만 썼다. FDA 페이지(알레르겐 표시, MoCRA 등록과 이상 반응 보고, hypoallergenic 표시)처럼 열리지 않아 확인되지 않은 주장은 쓰지 않았다.
- **방법**: 비율은 별점 묶음(부정, 중립, 긍정) 가중으로 표본 편향을 되돌린 값이다. 원본 수는 어떤 불만이 있는지로, 가중 비율은 그 불만이 얼마나 흔한지로 읽는다. 세기 방향 지수는 (너무 셈 − 약함) ÷ (너무 셈 + 약함)이고 방향 언급이 기준 수 이상인 상품만 냈다. 말한 지속 시간 중앙값은 값이 기준 수 이상인 상품만 냈다. 별점 격차는 그 주제 부정 리뷰와 나머지 리뷰의 가중 평균 별점 차이다.

### 견고성 점검
상품을 하나씩 빼고 다시 계산해도 결론이 뒤집히거나 불만 지도 상위 3개 순서가 바뀐 경우는 6번 중 0번 [m:a.robust.loo_flips]이었고, 그때 머리 숫자 2는 9.5%~10.6% [m:a.robust.loo_head_neg], 세기 불만 가운데 약함 쪽 비율은 79.2%~90.4% [m:a.robust.loo_low_share] 안에 있었다. 리뷰를 다시 뽑아 보면 지속력과 향의 세기가 불만 1위로 남은 비율은 100.0% [m:a.robust.head_first], 머리 숫자 2의 95% 구간은 8.2%~11.9% [m:a.robust.head_neg_ci]이며, 이 점검은 고른 상품 안의 표본 흔들림만 잴 뿐 어떤 상품을 골랐는지에서 오는 치우침은 재지 못한다.

### 주의 사항
- 리뷰는 공유 리뷰 DB 표본이라 낮은 별점이 실제보다 많다(표본 평균 별점이 가중 평균보다 낮음, 숫자는 페이지 끝 한계 목록). 비율은 별점 묶음 가중으로 되돌렸다.
- 자유 서술에서 뽑은 수치(말한 지속 시간 등)는 리뷰어가 적은 값이라 측정값이 아니다. 방향과 분포로만 읽는다.
- 개발 기준의 사양 숫자는 웹 조사 출처를 근거로 한 시작점이고 시험으로 확인해야 한다.
- 상품 수가 적고 대부분 한 하위 카테고리(Women's Eau de Parfum)라 상품끼리, 하위 카테고리끼리의 비교가 약하다.
- 시장 데이터(spd-amz-market)의 매출, 점유율, 증감, 승률 칸은 문서에 단위가 없어 단위 미확인으로 적었다. 연 환산 값은 월 매출 칸을 달러로 가정한 것이다.
- ASIN은 매출 순위가 아니라 공유 DB에 리뷰가 많은 후보 가운데 사람이 고른 것이다.
- Jean Paul Gaultier(B08FBQWRYC)는 Men's Eau de Parfum, Elizabeth Taylor(B0009OAI8Q)는 Women's Fragrance Sets 노드로 잡혀 있다.
- 향수와 무관한 리뷰 하나(R1T7FSK04S0DMQ)가 숫자에 들어 있다.
- 미국 향수 시장 규모는 IMARC, MarketLine, Ken Research가 서로 다르다 [r:mkt_12] [r:mkt_13] [r:mkt_14]. TAM은 범위로만 읽는다.
- 이번 조사에서 찾은 것: 분사 시험은 소비자 제품 펌프 전반의 ASTM 방법(D3890, D4336, D4041) [r:tst_30] [r:tst_31] [r:tst_33]이고, HRIPT는 RIFM 프로토콜의 방법을 논문 초록으로 확인했다 [r:tst_11] [r:tst_13] [r:tst_14]. 아직 찾지 못한 것: 향수 전용 분사 시험 표준, 분사기 작동 횟수(내구) 시험 표준과 각 시험의 합격 기준 값, 향수 피부 지속 시간을 재는 ISO나 ASTM 공식 표준, HRIPT 논문 원문과 완제품 시험의 합격 기준, FDA 향료 알레르겐 규칙안 게재본. 해당 개발 기준은 확인 필요로 남겼다.
- SOM, 구체 가격, 아마존 FBA 위험물 절차와 반품 정책은 근거 숫자나 조사가 없어 확인 필요로 둔다.
- 별점 격차와 라벨의 함께 나옴(예: 많이 뿌림과 금방 날아감, 두통과 너무 셈)은 원인 관계가 아니다.
- 설계 정보 추출은 감사 표본에서 FAIL이 기준(5%) 안이었다: 표본 150개 중 FAIL 4개(2.7%) [m:a.detail_audit](고친 뒤).
- 웹 조사 주장은 원문을 다시 열어 문장을 확인한 것만 썼다: 104개 중 80개 [m:a.research_verified].
