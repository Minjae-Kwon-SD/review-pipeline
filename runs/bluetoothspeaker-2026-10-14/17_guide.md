# 아마존 미국 블루투스 스피커 제품 개발 가이드
> 새로 들어오는 브랜드를 위한 기준: 광고한 조건 그대로 재생 시간을 지키는 손바닥 크기 클립형 방수 스피커

## 머리 숫자
- [head.topic_neg] 배터리와 충전을 부정으로 말한 리뷰어 비율(별점 가중)로 불만 1위지만, 다시 뽑기에서 1위로 남은 비율이 51.6% [m:a.robust.head_first]뿐이라 품질과 내구성 3.1% [m:p.map.quality], 음질과 사실상 같은 수준이고 세 주제를 함께 첫 개발 관문으로 둔다
- [head.topic_weakest] 가장 큰 약점이 배터리와 충전인 상품 수, 모두 손바닥 크기나 샤워용 작은 스피커(JBL Go 4, JBL Clip 5, Soundcore Select 4 Go)이고 나머지 상품은 음질, 조작, 품질, 포장이 가장 큰 약점
- [head.dir_ratio] 음질 불만의 방향은 저음 부족 쪽 라벨이 훨씬 많고, 가중해도 저음 부족 1.2% [m:head.dir_high_w] 대 저음 과다 0.3% [m:head.dir_low_w]로 같은 방향
- [m.top10_share_PBT] Portable Bluetooth Speakers 노드의 상위 10개 브랜드 점유율 합(단위 미확인 값을 %로 읽음), 1위는 JBL 40.7% [m:m.top1_PBT]
- [head.market_month] Portable Bluetooth Speakers 노드의 월 매출 칸, 달러로 읽으면 500,117,948(월 매출을 달러로 읽을 때 연 환산) [m:head.market_year]

## 01 시장 개요
**TL;DR** 블루투스 스피커는 이미 넓게 찾는 범주이고(공통 검색어 검색량 합 5,225,292 [m:m.terms_common_volume]), Portable Bluetooth Speakers 노드는 JBL 한 브랜드가 40.7% [m:m.top1_share_PBT]를 차지한다. 첫 상품은 JBL의 작은 단계와 같은 값대에서 재생 시간과 충전 신뢰로 차별하는 손바닥 크기 방수 스피커를 확인이 필요한 권고로 둔다.

### TAM, SAM, SOM
- **TAM(전 세계)**: 세계 블루투스 스피커 시장을 2024년 229억 달러로 보는 보고서 [r:mkt_02]와, 들고 다니는 블루투스 스피커만 2023년 129억 달러로 보는 보고서 [r:mkt_06]가 있다.
- **미국 시장, 블루투스 스피커 전체**: 2024년 57억 달러로 보는 보고서가 있다 [r:mkt_01].
- **미국 시장, 들고 다니는 제품만**: 2023년 30억 4,230만 달러로 보는 보고서 [r:mkt_03]가 있어 범위가 달라 기준값 하나로 정하지 않고 더하거나 곱하지 않는다.
- **넓은 범위의 보고서**: 와이파이와 스마트 스피커까지 넣은 미국 무선 스피커 시장은 2024년 61.4억 달러다 [r:mkt_10].
- **성장률**: 미국 들고 다니는 블루투스 스피커는 연평균 10.1% [r:mkt_04], 미국 무선 스피커 전체는 12.01% [r:mkt_11]로 본다.
- **유통 경로**: 세계 들고 다니는 블루투스 스피커 매출의 약 62.10%가 매장 유통이라는 보고서가 있어 [r:mkt_08], 아마존 노드 값은 시장 전체의 일부로만 읽는다.
- **SAM(아마존 미국 노드)**: Portable Bluetooth Speakers는 41,676,496(월 매출 칸, 단위 미확인) [m:head.market_month], 500,117,948(월 매출을 달러로 읽을 때 연 환산) [m:head.market_year]이다.
- **SOM(확인 필요)**: 상위 10개 브랜드 몫 73.8% [m:m.top10_share_PBT] 밖에서 시작하고, 목표 금액은 매출 칸 단위를 확인한 뒤 정한다.

### 판정 3개
- **침투: 이미 넓게 찾는 범주**: 공통 검색어 94개 [m:m.terms_common_n]의 한 달 검색량 합이 5,225,292 [m:m.terms_common_volume]라, 새 범주를 알리는 일보다 이미 찾는 사람에게 고르게 하는 일이 과제다.
- **경쟁 집중: JBL 한 브랜드 중심**: 상위 10개 브랜드 점유율 합 73.8% [m:m.top10_share_PBT], 1위 JBL 40.7% [m:m.top1_PBT]이고(점유율 칸은 단위 미확인 값을 %로 읽음), 검색어도 jbl bluetooth speaker, jbl, jbl speaker처럼 브랜드 이름이 앞선다.
- **기회: 같은 값대의 재생 시간 신뢰**: 시장 가격 1구간 27.42~131.31 [m:m.price_band1_range]의 매출 비중은 17.4% [m:m.price_band1_share]로 작아 싼 값만으로 들어갈 자리는 아니고, 배터리와 충전이 불만 1위라 조사 상품의 작은 단계와 같은 값대에서 재생 시간 신뢰로 차별할 자리를 찾는다. 빠르게 크는 검색어는 이력이 없어 판단하지 않는다.

가장 큰 약점이 배터리와 충전인 상품은 10개 중 3개(리뷰를 다시 뽑아 보면 2~4개) [m:head.topic_weakest]로 JBL Go 4, JBL Clip 5, Soundcore Select 4 Go이고 셋 다 작은 스피커다. 다만 몇 안 되는 상품에서 나란히 보인 것이고 크기가 원인이라는 뜻은 아니다(작은 DEWALT 상품은 품질과 내구성이 가장 큰 약점).

Outdoor Speakers 노드는 상위 10개 합 68.8% [m:m.top10_share_OUT], 1위 Polk Audio 14.8% [m:m.top1_OUT]로 덜 몰려 있고, 조사 상품은 이 노드에 없다.

### 검색 수요
- 검색어는 성별 구분이 없는 공통 검색어 94개 [m:m.terms_common_n]가 전부이고, 여성 검색어는 0개 [m:m.terms_female_n]다.
- 남성 검색어도 0개 [m:m.terms_male_n]라 성별로 상품을 나누지 않는다.
- 상위 검색어는 bluetooth speaker, jbl bluetooth speaker, dewalt, jbl, jbl speaker 순으로 브랜드 이름이 든 검색어가 많다.
- 쓰는 곳 검색어는 shower speaker 58,183 [m:std.water.term.shower speaker]가 방수 검색어 가운데 가장 크고, outdoor speakers 38,397 [m:std.loudness.term.outdoor speakers]가 뒤를 잇는다.
- 크기 검색어는 jbl clip 41,755 [m:std.portability.term.jbl clip], small bluetooth speaker 26,328 [m:std.portability.term.small bluetooth speaker]처럼 작은 스피커를 찾는 말이 크다.
- 성장 배수는 후보 검색어 264개 [m:m.growth_candidates] 가운데 주간 이력을 받은 검색어가 0개 [m:m.growth_ranked]라 말하지 않는다.

### 진입 조건
- **크기와 형태**: 손바닥 크기 클립형을 먼저 낸다. 크기 검색어 mini speaker 28,724 [m:std.portability.term.mini speaker], small speaker 19,228 [m:std.portability.term.small speaker]이고, 조사 상품 대부분이 있는 Portable Bluetooth Speakers 노드에 둔다.
- **쓰는 곳과 방수**: 야외 6.9% [m:f.sound.usage_location.outdoor_yard_water.w], 샤워실과 욕실 2.1% [m:f.sound.usage_location.shower_bathroom.w]를 함께 받도록 JBL 작은 신제품과 같은 IP67 방진 방수 [r:ind_09]로 만든다.
- **배터리 재생 시간**: 리뷰어가 말한 재생 시간 중앙값은 4시간 [m:f.battery.battery_runtime_hours.median]이고, soundcore 작은 모델은 13~20시간을 표기한다 [r:ind_14]. 목표 시간은 시험 조건과 함께 정한다(확인 필요).
- **가격대(확인 필요)**: 조사 상품 중간 묶음 49.22~65.10달러 [m:price.band1.range] 안이고, 시장 가격 1구간 27.42~131.31 [m:m.price_band1_range]에 든다(가격 구조 절).
- **구성(상자 안)**: 충전 케이블을 넣고 전원 어댑터가 없는지를 상품명 아래에 밝힌다. 충전기나 어댑터가 원래 안 들어 있다는 불만 135개 [m:std.box_claims.label.charger_not_included_by_design]는 실제로 빠진 구성품 5개 [m:std.box_claims.label.missing_from_box]와 다른 불만이다.

## 02 경쟁사
**TL;DR** 조사 상품은 JBL이 가장 많고 Anker와 Soundcore, 저가 브랜드 BolaButty와 Ortizan, 몸에 다는 DEWALT가 섞였다. 모든 상품의 가장 큰 강점은 음질인데, 가장 큰 약점은 작은 JBL과 Soundcore 상품에서 배터리와 충전(10개 중 3개(리뷰를 다시 뽑아 보면 2~4개) [m:head.topic_weakest]), 저가 상품에서 음질로 갈린다.

### 점수표 해설
- **배터리와 충전 부정 최고**: JBL Clip 5 4.7% [m:s.B0CTP56C5R.topic_neg], JBL Go 4 4.2% [m:s.B0CTNWBT1Z.topic_neg]로 둘 다 손바닥 크기다.
- **배터리와 충전 부정 최저**: Anker soundcore 2 1.5% [m:s.B01MTB55WH.topic_neg]이고, 공식 페이지는 큰 용량 배터리와 긴 최대 재생 시간을 표시한다 [r:ind_15](사양과 불만은 나란히만 놓음).
- **말한 재생 시간이 짧은 상품**: JBL Go 4 2시간 [m:s.B0CTNWBT1Z.duration_median], BolaButty 2시간 [m:s.B0BRKPVZB4.duration_median]이다(리뷰어가 적은 값이라 측정값이 아님).
- **말한 재생 시간이 긴 상품**: Soundcore Boom 2 6시간 [m:s.B0CQ53RVTW.duration_median], Soundcore Select 4 Go 6시간 [m:s.B0DB1753RZ.duration_median]이다.
- **표기와 리뷰(나란히만)**: JBL Charge 6은 보도자료가 Playtime Boost를 켜면 최대 28시간 [r:ind_05], 공식 사양이 Maximum music playing time (hrs) 28, extra 4 hours with JBL Playtime Boost, Charging time (hrs) 3, 10 minutes on the charger gets you up to 150 minutes of playtime [m:spec.B0DN2ZCZX6.battery_hours]로 서로 다르게 적고, 리뷰어가 말한 재생 시간 중앙값은 4.5시간 [m:s.B0DN2ZCZX6.duration_median]이다.
- **저음 부족 쪽 상품**: BolaButty +0.96 [m:s.B0BRKPVZB4.dir_index], Ortizan +0.90 [m:s.B08FDPW8KR.dir_index]로 저가 상품이 저음 부족 쪽에 있다.
- **방향이 갈린 상품**: Anker -0.11 [m:s.B01MTB55WH.dir_index], Soundcore Boom 2 +0.00 [m:s.B0CQ53RVTW.dir_index]는 저음이 넘친다는 말과 모자란다는 말이 비슷해 취향 차이로 읽는다. 방향 지수가 비어 있는 상품은 방향 라벨 리뷰가 적다.
- **가중 별점**: JBL Flip 5 4.78★ [m:s.B07QK2SPP7.star]가 가장 높고, BolaButty 4.50★ [m:s.B0BRKPVZB4.star]가 가장 낮다.
- **가격 폭**: Soundcore Select 4 Go 22.49달러 [m:s.B0DB1753RZ.price]에서 JBL Charge 6 154.82달러 [m:s.B0DN2ZCZX6.price]까지다.
- **사양 확인 범위**: 같은 상품인지는 이름만 일치 2개, 일치 확인 8개 [m:spec.match_summary]로 확인했다. 이름만 일치인 Ortizan과 DEWALT는 확인된 사양 값이 없어 사양 비교에서 뺀다.
- **작은 JBL의 재생 시간 표기(나란히만)**: Go 4는 Maximum music playing time (hrs) 7, Up to 7 hours of playtime plus 2 hours with Playtime Boost, Charging time (hrs) 3 [m:spec.B0CTNWBT1Z.battery_hours], Clip 5는 Up to 12 hours of playtime plus 3 hours with Playtime Boost, Maximum music playing time (hrs) 15, Charging time (hrs) 3 [m:spec.B0CTP56C5R.battery_hours]으로 표기한다. 배터리와 충전 부정이 가장 높은 두 상품의 표기를 불만과 나란히 놓을 뿐 원인으로 읽지 않는다.
- **soundcore의 재생 시간 표기(나란히만)**: Select 4 Go는 up to 20 hours of non-stop music on a single charge [m:spec.B0DB1753RZ.battery_hours], Boom 2는 up to 24 hours of playtime at 50% volume with BassUp and light effects turned off, around 5.5 hours to charge with a certified 5V/3A (15W) wall charger [m:spec.B0CQ53RVTW.battery_hours]로 표기하고, Boom 2는 음량 조건을 함께 적는다.
- **방수 등급 표기**: Clip 5는 IP Code IP67 [m:spec.B0CTP56C5R.water_dust_rating], Charge 6은 IP Code IP68, Waterproof, dustproof, and drop-proof [m:spec.B0DN2ZCZX6.water_dust_rating]로 표기한다.
- **방진 숫자가 없는 IPX 표기(예)**: BolaButty는 IPX5 rating for protection against water splashes and spills [m:spec.B0BRKPVZB4.water_dust_rating], Anker soundcore 2는 IPX7 waterproof protection [m:spec.B01MTB55WH.water_dust_rating]로 표기한다.
- **크기 표기**: Go 4는 Dimensions (Width x Height x Depth) (in) 3.7 x 3.0 x 1.7, Net Weight (lbs) 0.69 [m:spec.B0CTNWBT1Z.size_weight], Charge 6은 Dimensions (Width x Height x Depth) (in) 9.0 x 3.9 x 3.7, Net Weight (kgs) 1.37 [m:spec.B0DN2ZCZX6.size_weight]로 표기한다(크기와 무게 값은 10개 중 4개 상품만 있음).

### 하위 카테고리 비교
- 조사 상품은 DEWALT(Portable Line-In Speakers)를 빼면 모두 Portable Bluetooth Speakers 노드에 있어 노드끼리의 비교는 약하다.
- Portable Bluetooth Speakers와 Portable Cell Phone & MP3 Player Speakers & Audio Docks는 매출 칸과 평균 가격이 비슷해, 두 노드를 따로 시장으로 더하지 않는다.
- Outdoor Speakers는 1위가 Polk Audio 14.8% [m:m.top1_OUT]로 Portable Bluetooth Speakers와 1위 브랜드가 다르고, 조사 상품이 이 노드에 없어 직접 비교하지 않는다.
- Home Audio Speakers는 평균 가격이 훨씬 높아 이 가이드의 범위 밖이다.

### 업계 구조
- **선두 브랜드의 작은 단계**: JBL은 스스로를 들고 다니는 오디오의 세계 1위로 내세우고 [r:ind_01], Go 4를 49.95달러 [r:ind_06], Clip 5를 79.95달러 [r:ind_07]에 냈다.
- **선두 브랜드의 위 단계**: JBL Flip 7은 149.95달러 [r:ind_02], Charge 6은 199.95달러 [r:ind_03]이고, 큰 Xtreme 4도 있다 [r:ind_08].
- **Bose의 가격 단계**: SoundLink Flex는 149달러 [r:ind_10], 큰 SoundLink Max는 399달러 [r:ind_12]다.
- **방수 등급 표기**: JBL의 2024년 신제품 Go 4, Clip 5, Xtreme 4는 IP67과 블루투스 5.3을 갖추고 [r:ind_09], Bose Flex도 IP67 [r:ind_11], soundcore는 IP67 또는 IPX7을 내세운다 [r:ind_13].
- **작은 모델의 재생 시간 표기**: soundcore 작은 모델은 13~20시간 [r:ind_14], Ultimate Ears WONDERBOOM 4는 14시간 [r:ind_20]을 표기한다.
- **긴 재생 시간 표기**: Marshall Emberton III는 32시간 넘게 [r:ind_19], Beats Pill은 최대 24시간 [r:ind_23]을 내세운다.
- **조건이 붙은 표기**: JBL Flip 7의 16시간은 Playtime Boost를 켠 값이고 [r:ind_04], Bose와 soundcore는 음량 절반 조건으로 잰다고 밝힌다 [r:tst_10] [r:tst_11].
- **배터리 교체와 큰 음량**: Sonos Move 2는 배터리를 빼서 바꿀 수 있다고 내세우고 [r:ind_18], Turtlebox는 야외용 큰 음량과 내구성을 브랜드 핵심으로 둔다 [r:ind_25].

## 03 문제
**TL;DR** 불만 1위 배터리와 충전 3.2% [m:p.map.battery_life]는 품질과 내구성 3.1% [m:p.map.quality], 음질과 다시 뽑기에서 자리를 바꿀 만큼 붙어 있어 세 주제를 한 묶음의 출시 관문으로 둔다. 별점 격차는 고객 응대, 브랜드 경험, 신뢰에서 크고, 집중 분석마다 불만을 원인 번호(설계 결함 또는 선호 차이)로 나눠 기준표와 잇는다.

### 불만 지도
- 배터리와 충전 3.2% [m:p.map.battery_life], 품질과 내구성 3.1% [m:p.map.quality]가 앞선다.
- 음질 3.0% [m:p.map.sound_quality]도 거의 같고, 상품 하나를 빼면 1위가 품질과 내구성이나 음질로 바뀌는 경우가 있다(A장 견고성 점검).
- 조작과 부가 기능 2.0% [m:p.map.features_controls], 연결 1.9% [m:p.map.connectivity]가 그 뒤다.
- 브랜드 경험 1.8% [m:p.map.brand_experience]는 재구매와 추천 의향이라 결과 지표로 읽는다.
- 음량과 힘 1.7% [m:p.map.loudness], 가격 대비 가치 1.1% [m:p.map.price_value]가 그다음이다.
- 디자인과 휴대 1.0% [m:p.map.design], 포장 0.9% [m:p.map.packaging]이고, 포장 쪽 불만의 가장 큰 라벨은 충전기나 어댑터가 원래 안 들어 있다는 말이다.
- 신뢰 0.6% [m:p.map.trust], 고객 응대 0.5% [m:p.map.customer_service]는 불만 지도에서 작은 주제다.
- 그래도 고객 응대 격차 -3.02 [m:p.gap1]와 신뢰 격차 -2.43 [m:p.gap3]는 별점 격차 상위 세 주제에 든다.
- 방수 0.2% [m:p.map.water_resistance], 안전과 몸 반응 0.1% [m:p.map.safety]는 작고, 배송은 개발 기준에서 뺀다.
> "꽂으면 충전이 시작되고 켜져서 휴대폰과 잠깐 연결되더니 꺼지고 충전도 멈춘다" (JBL, 1★, R30KHPY7WLEOUS)

### 별점 격차
- **고객 응대**: 부정 1.63★ [m:p.gap1_neg], 격차 -3.02 [m:p.gap1]로 가장 크고, 고장 뒤 교환과 환불 과정의 불만이 많다.
- **브랜드 경험**: 부정 1.73★ [m:p.gap2_neg], 격차 -2.97 [m:p.gap2]이고, 다시 사지 않겠다는 말이 많다.
- **신뢰**: 부정 2.22★ [m:p.gap3_neg], 격차 -2.43 [m:p.gap3]이고, 인용 후보에는 같은 SKU인데 이전 세대와 묶이지 않는다는 말과 출력 과장이 있다.
- **읽는 법**: 고객 응대와 신뢰는 불만 지도에서 작은 주제라, 흔한 불만(배터리, 고장, 음질)과 별점 격차가 큰 불만(교환 응대와 표기 신뢰)을 따로 관리한다.
> "Soundcore는 옛 제품을 먼저 돌려보내기 전까지 해결해 주지 않았다" (Soundcore, 1★, RK9DSKQ0F9H1N)
> "이전 모델과 근본적으로 호환되지 않는 제품을 같은 SKU로 파는 것은 오해를 부른다" (Soundcore, 1★, R2OHSC7HE2UFCV)
> "케이블은 '전자 폐기물을 줄이려고' 뺐다는 답을 들었다" (JBL, 1★, R2CRQ0DRH3RPBB)

### 집중 분석 1: 음질과 음량, 저음 부족 쪽 방향
- **소리 대역 방향**: 저음이 부족함 1.4% [m:f.sound.sound_band_direction.bass_lacking.w]가 저음이 너무 많음 0.4% [m:f.sound.sound_band_direction.bass_too_much.w]보다 흔하다.
- **그 밖의 대역 문제**: 먹먹하고 뭉개짐 68개 [m:f.sound.sound_band_direction.muffled_muddy], 큰 음량에서 찌그러지거나 떨림 50개 [m:f.sound.sound_band_direction.distorts_at_high_volume]다.
- **저음 부족 라벨이 함께 붙은 비율**: 휴대폰 자체 스피커와 비교한 리뷰 46개 중 5개(10.9%) [m:f.sound.comparison_reference.phone_builtin.weak_bass], 팟캐스트와 오디오북 용도 55개 중 5개(9.1%) [m:f.sound.audio_use.spoken_word.weak_bass]다(함께 나온 비율이지 원인이 아님).
- **쓰는 곳별 저음 부족**: 야외를 말한 리뷰 193개 중 4개(2.1%) [m:f.sound.usage_location.outdoor_yard_water.weak_bass]처럼 쓰는 곳마다 낮아, 쓰는 곳에 따라 크게 갈리지 않는다.
- **음악 밖의 용도**: TV, 컴퓨터, 영상 소리 1.6% [m:f.sound.audio_use.tv_pc_video.w], 전화 통화 0.6% [m:f.sound.audio_use.phone_call.w]다.
- **음량**: 최대 음량이 작음 186개 [m:std.loudness.label.too_quiet], 밖이나 넓은 곳에서 부족 32개 [m:std.loudness.label.weak_in_space]다.
- **강점이기도 한 음질**: 점수표에서 모든 상품의 가장 큰 강점이 음질이고, 음질 만족 리뷰가 1,511개 [m:std.sound.pos]다.
> "저음역이 없어서 음악을 즐길 수 없다" (DEWALT, 4★, R2VKFGKPGTXDGC)
> "저음이 너무 두드러진다" (JBL, 3★, R3H5ETVHICXGR6)
> "음량 60%를 넘으면 소리가 금세 찌그러지기 시작한다" (JBL, 2★, R3THCN0QMN26XI)

**시사점**
- 원인 1(설계 결함), 저음 부족과 선명하지 않은 소리: 저음이 약하거나 없음 150개 [m:std.sound.label.weak_bass], 얇거나 답답해 선명하지 않음 142개 [m:std.sound.label.lacks_clarity]. 작은 몸체의 저음 튜닝과 대역 균형을 고치면 줄어든다.
- 원인 2(설계 결함), 큰 음량의 찌그러짐과 잡음: 큰 음량에서 찌그러지거나 뭉개짐 51개 [m:std.sound.label.distorts_at_high_volume], 지지직 잡음이나 찌그러짐 125개 [m:std.sound.label.static_noise]. 출력 한계에 맞춘 음량 제한과 부품 품질로 줄어든다.
- 원인 3(선호 차이), 저음 양의 취향: 저음이 과해 소리가 뭉개짐 45개 [m:std.sound.label.bass_overpowering], EQ나 저음 조절이 없거나 약함 32개 [m:std.controls.label.no_eq_control]. 같은 상품에서 넘친다와 모자란다가 함께 나와 저음 강화를 켜고 끄는 선택지로 대응한다.
- 원인 4(선호 차이), 쓰는 곳에 따른 음량 기대: 최대 음량이 작음 186개 [m:std.loudness.label.too_quiet], 조금 더 컸으면 함 44개 [m:std.loudness.label.wish_bit_louder]. 크기 단계마다 어디까지 채우는지 안내해 대응한다.

### 집중 분석 2: 배터리와 충전, 짧은 재생 시간과 광고와의 차이
- **말한 재생 시간**: 값 368개 [m:f.battery.battery_runtime_hours.n]의 중앙값이 4시간 [m:f.battery.battery_runtime_hours.median]이다(리뷰어가 적은 값).
- **짧은 쪽에 몰림**: 4시간 미만 161개 [m:f.battery.battery_runtime_hours.bin0], 4~8시간 145개 [m:f.battery.battery_runtime_hours.bin1]이다.
- **긴 쪽**: 12~20시간 13개 [m:f.battery.battery_runtime_hours.bin3], 20시간 이상 4개 [m:f.battery.battery_runtime_hours.bin4]뿐이다.
- **광고와의 차이**: 광고한 재생 시간에 못 미침 140개 [m:std.battery.label.below_advertised], 재생 시간 광고가 거짓 31개 [m:std.box_claims.label.battery_claim_false]다.
- **음량과 시험 조건**: 큰 음량이나 저음에서 빨리 닳음 29개 [m:std.battery.label.drains_at_high_volume]이고, 경쟁사는 재생 시간을 음량 절반 조건에서 잰다고 밝힌다 [r:tst_10] [r:tst_11].
- **충전 고장**: 충전이 안 되거나 멈춤 160개 [m:std.battery.label.stopped_charging], 충전이 유지되지 않거나 점점 줄어듦 139개 [m:std.battery.label.wont_hold_charge]다.
- **잔량 표시**: 잔량 표시나 부족 경고가 없음 26개 [m:f.battery.battery_indicator_issue.no_indicator], 부족 경고가 너무 잦거나 재생을 끊음 9개 [m:f.battery.battery_indicator_issue.warning_intrusive]다.
- **상자 구성**: 충전기나 어댑터가 원래 안 들어 있음 135개 [m:std.box_claims.label.charger_not_included_by_design], 들어 있는 케이블 단자가 맞지 않음 10개 [m:std.box_claims.label.wrong_cable_type]다.
> "작은 크기 때문에 배터리 크기도 제한되고, 그래서 사용 시간에 영향을 준다" (DEWALT, 3★, R2DVMVA0S4J88W)
> "광고한 12시간은 고사하고 8시간도 간 적이 없다" (JBL, 3★, R1ZYZBBLCJ5QEU)
> "최대 24시간이라고 적혀 있지만 최대 음량이면 4시간쯤밖에 안 간다" (JBL, 2★, R3ANDOGFQ57A0R)
> "99% 충전과 11% 충전을 구별할 방법이 전혀 없다" (Soundcore, 2★, RD01U7OXWKRAR)

**시사점**
- 원인 5(설계 결함), 작은 몸체의 짧은 재생 시간: 재생 시간이 짧음 343개 [m:std.battery.label.short_runtime], 말한 재생 시간 4시간 미만 161개 [m:f.battery.battery_runtime_hours.bin0]. 셀 용량과 전력 관리를 고치면 줄어든다.
- 원인 6(설계 결함), 광고 조건과 실제 사용의 차이: 광고한 재생 시간에 못 미침 140개 [m:std.battery.label.below_advertised], 큰 음량이나 저음에서 빨리 닳음 29개 [m:std.battery.label.drains_at_high_volume]. 시험 조건을 정하고 표기에 함께 적으면 줄어든다.
- 원인 7(설계 결함), 충전 회로와 배터리 노화: 충전이 안 되거나 멈춤 160개 [m:std.battery.label.stopped_charging], 충전이 유지되지 않음 139개 [m:std.battery.label.wont_hold_charge]. 충전 보호 회로와 셀 품질 관리로 줄어든다.
- 원인 8(선호 차이), 잔량 표시와 경고 방식: 잔량 표시나 부족 경고가 없음 26개 [m:f.battery.battery_indicator_issue.no_indicator], 잔량을 앱에서만 볼 수 있음 5개 [m:f.battery.battery_indicator_issue.app_only]. 경고가 너무 잦다는 말도 함께 있어 몸체 표시등과 앱 표시를 함께 두고 경고음을 끌 수 있게 대응한다.
- 원인 9(선호 차이), 상자 구성에 대한 기대: 충전기나 어댑터가 원래 안 들어 있음 135개 [m:std.box_claims.label.charger_not_included_by_design]는 실제 누락 5개 [m:std.box_claims.label.missing_from_box]와 달리 구성대로 온 상품의 불만이라, 구성 표기와 케이블 안내로 대응한다.

### 집중 분석 3: 고장과 방수, 좋다가 고장
- **고장 증상**: 작동 멈춤 1.4% [m:f.durability.failure_type.stopped_working.w], 충전이 안 되거나 충전을 유지하지 못함 1.1% [m:f.durability.failure_type.charge_fail.w]이 앞선다.
- **저절로 꺼짐과 연결 고장**: 저절로 꺼짐 0.9% [m:f.durability.failure_type.shuts_off_by_itself.w], 잘 되다가 고장으로 연결이 안 됨 157개 [m:f.durability.failure_type.connection_lost]다.
- **좋다가 고장**: 문제가 생기기까지 기간은 20일 이상 384개 [m:f.durability.time_to_problem_days.bin4], 중앙값 90일 [m:f.durability.time_to_problem_days.median]로 몇 달 잘 쓰다 멈췄다는 말이 많다.
- **첫날 불량**: 처음부터 불량 100개 [m:std.durability.label.defective_on_arrival], 문제까지 4일 미만 17개 [m:f.durability.time_to_problem_days.bin0]다.
- **부품 파손**: 스피커가 나가거나 소리 부품 고장 77개 [m:std.durability.label.speaker_blown], 끈, 손잡이, 단자 같은 부품 파손 67개 [m:std.durability.label.parts_broken]다.
- **방수**: 방수가 아니거나 약함 29개 [m:std.water.label.not_waterproof], 충전 단자 덮개 없음 8개 [m:std.water.label.port_cover_missing]다.
- **물과 먼지에 닿는 곳**: 작업장 3.8% [m:f.durability.usage_location.work_jobsite.w], 몸에 달거나 들고 다님 4.6% [m:f.durability.usage_location.on_the_move.w]이다.
> "두 주 쓰고 고장 났다" (Soundcore, 1★, R2SVGLOM3XP1H6)
> "1년이 막 지나자 배터리가 완전히 죽었다" (Soundcore, 3★, RZJNAAJJROMDE)
> "Charge 6의 충전 단자에는 덮개가 없다" (JBL, 4★, R1S5835Y2IFSZU)

**시사점**
- 원인 10(설계 결함), 몇 달 뒤 멈추는 전원과 충전: 쓰다가 고장 남 307개 [m:std.durability.label.stopped_working], 저절로 꺼지거나 켜짐 170개 [m:std.durability.label.random_power_cycling]. 전원부와 충전부의 수명 시험으로 줄어든다.
- 원인 11(설계 결함), 첫날 불량과 받은 상품 상태: 처음부터 불량 100개 [m:std.durability.label.defective_on_arrival], 새 제품이 아니거나 정품 의심 18개 [m:std.box_claims.label.used_or_not_genuine]. 출고 검사와 봉인 포장으로 줄어든다.
- 원인 12(설계 결함), 스피커와 부착 부품 파손: 스피커가 나감 77개 [m:std.durability.label.speaker_blown], 끈과 클립 같은 부품 파손 67개 [m:std.durability.label.parts_broken]. 드라이버 보호와 부착 부품 강도를 올리면 줄어든다.
- 원인 13(설계 결함), 방수 마감과 단자 덮개: 방수가 아니거나 약함 29개 [m:std.water.label.not_waterproof], 젖은 뒤 고장이나 성능 저하 16개 [m:std.water.label.water_damage]. 외함 밀봉과 단자 덮개로 줄어든다.

### 집중 분석 4: 연결과 조작, 묶기 호환과 버튼
- **연결**: 연결이 자주 끊김 116개 [m:std.connectivity.label.connection_drops], 페어링이 안 되거나 어려움 95개 [m:std.connectivity.label.pairing_trouble]이 앞선다.
- **여러 대 묶기**: 두 대 묶기나 스테레오 설정이 어려움 46개 [m:std.connectivity.label.speaker_link_trouble], 다른 모델이나 세대와 묶이지 않음 43개 [m:std.connectivity.label.model_incompatible]다.
- **호환 표기**: 묶기 호환이나 모델 변경을 알리지 않음 22개 [m:std.box_claims.label.pairing_version_mismatch]는 신뢰 불만으로 별점 격차와 맞닿는다.
- **보이지 않는 버튼**: 색이나 위치 때문에 버튼이 안 보임 22개 [m:f.controls.button_control_issue.hard_to_see], 손으로 구분이 안 되거나 장갑 끼면 누르기 어려움 20개 [m:f.controls.button_control_issue.no_tactile_feel]다.
- **오래 누르기**: 오래 눌러야 하거나 기능이 헷갈림 30개 [m:f.controls.button_control_issue.long_press_or_confusing]다.
- **앱**: 앱으로 기능이 나아짐 1.9% [m:f.controls.app_dependency.app_helps.w]이 기본 기능이 앱에만 있음 0.3% [m:f.controls.app_dependency.required_for_basic.w]보다 흔하다.
- **통화와 조명**: 마이크 없음이나 통화 품질 나쁨 48개 [m:std.controls.label.poor_mic_calls], 조명이 거슬리거나 조절 안 됨 34개 [m:std.controls.label.lights_annoying]다.
- **바라는 기능**: 바라는 기능을 적은 리뷰 178개 [m:f.controls.desired_feature.n]에서 더 큰 음량, 더 오래 가는 배터리, 더 많은 저음, 마이크가 앞선다.
> "새로 산 두 대가 예전 제품과 연결되지 않는다" (Soundcore, 1★, RDCGMKA6HHW7J)
> "위쪽 검은 버튼이 완전히 평평하고 불이 없어 어두운 곳에서는 보거나 만져서 찾기가 거의 불가능하다" (Anker, 3★, R268YNJ10BDKUW)

**시사점**
- 원인 14(설계 결함), 연결 끊김과 페어링: 연결이 자주 끊김 116개 [m:std.connectivity.label.connection_drops], 재생 중 소리가 끊기거나 건너뜀 71개 [m:std.connectivity.label.audio_cuts_out]. 무선 칩과 안테나 배치, 펌웨어로 줄어든다.
- 원인 15(설계 결함), 세대 사이 묶기 호환과 그 표기: 다른 모델이나 세대와 묶이지 않음 43개 [m:std.connectivity.label.model_incompatible], 호환 변경을 알리지 않음 22개 [m:std.box_claims.label.pairing_version_mismatch]. 묶기 방식을 세대 사이에 유지하고 바뀌면 모델 이름을 바꾸면 줄어든다.
- 원인 16(설계 결함), 보이지 않고 만져지지 않는 버튼: 버튼이 안 보임 22개 [m:f.controls.button_control_issue.hard_to_see], 손으로 구분이 안 됨 20개 [m:f.controls.button_control_issue.no_tactile_feel]. 튀어나온 버튼과 대비되는 표시로 줄어든다.
- 원인 17(선호 차이), 앱과 조명, 소리 안내의 정도: 앱 강요나 앱 미지원, 앱 오류 33개 [m:std.controls.label.app_problems], 조명이 거슬리거나 조절 안 됨 34개 [m:std.controls.label.lights_annoying]. 앱이 도움이 됐다는 말도 많아 기본 기능은 몸체에 두고 조명과 안내음을 끌 수 있게 대응한다.

### 안전
- 안전 부정 리뷰 26개: 두통 1개(가중 0.0%), 귀 2개(가중 0.0%), 이상 반응 없음 23개 [m:p.safety_text]
- **몸 반응**: 두통 1개 [m:p.safety.두통], 귀 2개 [m:p.safety.귀]뿐이고, 귀 통증은 리뷰어가 소리 품질을 이유로 든다.
- **제품 위험**: 나머지는 몸 반응이 아니라 충전 단자 과열, 단자와 케이블이 녹음, 충전 중 연기 같은 제품 위험이고, 수가 적어 상품별 비율로 말하지 않는다.
- **배터리 시험 기준**: 리튬 전지는 UN 38.3을 통과한 형식이어야 하고 [r:reg_08], 휴대용 리튬 이차 전지의 안전 시험 표준은 IEC 62133-2다 [r:tst_14].
- **완제품 기준**: 오디오 영상 기기 안전 표준 UL 62368-1은 위험 기반 방식이다 [r:tst_15]. 블루투스 스피커 과열 리콜 원문은 찾지 못했다.
> "USB-C 단자가 그을리고 일부 녹았다" (Anker, 3★, R3VYHI6THZVEIR)
> "충전 중에 기기에서 연기가 나기 시작했다" (JBL, 1★, R9FEUQZYGM94K)
> "귀가 아프다" (BolaButty, 1★, RFYLSJY1HR6DZ)

## 04 포지셔닝
**TL;DR** 포지션은 광고한 조건 그대로 재생 시간을 지키는 손바닥 크기 클립형 방수 스피커다. 근거는 배터리와 충전 불만 1위 3.2% [m:head.topic_neg]와 점수표의 상품별 배터리와 충전 부정 값이고, 가장 큰 약점이 배터리와 충전인 상품 10개 중 3개(리뷰를 다시 뽑아 보면 2~4개) [m:head.topic_weakest]가 모두 작은 스피커였던 것은 몇 안 되는 상품에서 나란히 보인 것일 뿐 크기가 원인이라는 뜻은 아니다. 품질과 음질도 같은 수준이라 충전 보호와 저음 튜닝을 같은 관문에 두고, 중간 크기와 큰 야외용은 첫 상품의 재생 시간 신뢰를 확인한 뒤로 미룰 것을 권고한다(확인 필요).

### 한 줄 포지션
광고한 조건 그대로 재생 시간을 지키는 손바닥 크기 클립형 방수 스피커, 잔량 표시와 튀어나온 버튼, 덮개 있는 충전 단자를 갖추고 재생 시간 시험 조건을 상자에 적는 브랜드

### 이기는 이유
- **작은 스피커의 배터리 공백**: 배터리와 충전 부정이 가장 높은 상품이 JBL Clip 5 4.7% [m:s.B0CTP56C5R.topic_neg], JBL Go 4 4.2% [m:s.B0CTNWBT1Z.topic_neg]로 선두 브랜드의 작은 단계다.
- **같은 값대의 배터리 불만**: 중간 가격 묶음의 배터리와 충전 부정 4.1% [m:price.band1.head_neg]가 세 묶음 가운데 가장 높고 이 묶음 별점은 4.67★ [m:price.band1.star]라, 배터리 불만이 가장 높은 묶음이다(묶음마다 상품이 적어 나란히만 읽음).
- **광고와 실제의 차이를 메우는 표기**: 광고한 재생 시간에 못 미침 140개 [m:std.battery.label.below_advertised]가 있고, 들고 다니는 스피커의 재생 시간 측정법은 표준으로 정해져 있다 [r:tst_08].
- **저음 부족 쪽 방향**: 저음 과다 45개 대 저음 부족 150개(0.30배) [m:head.dir_ratio]라 작은 몸체에서 저음을 살리는 튜닝이 차별점이 되고, 저음이 넘친다는 소수를 위해 저음 강화를 끌 수 있게 둔다.
- **표기 신뢰**: 신뢰 격차 -2.43 [m:p.gap3]이 크고 묶기 호환을 알리지 않았다는 불만 22개 [m:std.box_claims.label.pairing_version_mismatch]가 있어, 구성품과 호환 목록을 정직하게 적는 것만으로도 차별이 된다.

### 소비자 기준표
#### 기준 1: 음질과 저음(원인 1, 2, 3 대응)
- 감점 기준: 음질 불만 가중 4.7% [m:std.sound.neg_pct], 그중 음질이 전반적으로 나쁨 235개 [m:std.sound.label.poor_sound_overall]가 가장 많다.
- 만족 기준: 음질 만족 리뷰 1,511개 [m:std.sound.pos]의 크기에 비해 꽉 찬 소리 수준이고, 부정이 가장 적은 상품은 JBL 1.3% [m:std.sound.best]다.
- 개발 기준: 저음 강화 모드를 따로 둔 경쟁 사례(soundcore Boom 2의 BassUp 2.0 [r:ind_16])처럼 기본 튜닝은 중립에 두고 저음 강화를 켜고 끄게 한다. 저음 대역 목표와 큰 음량의 찌그러짐 한계는 확인 필요(조사 근거 없음).
- 상세페이지 문구: "Fuller bass you can switch on, clean sound at high volume" (켜고 끌 수 있는 더 풍부한 저음, 큰 음량에서도 깨끗한 소리). 청음 시험과 최대 음량 찌그러짐 확인 뒤에만 쓴다.
> "BassUp 기능이 뭉개지지 않으면서 저음을 분명히 살려 준다" (Anker, 4★, R3JG5LZRAF3B3N)

#### 기준 2: 음량(원인 4 대응)
- 감점 기준: 음량 불만 가중 2.3% [m:std.loudness.neg_pct], 그중 최대 음량이 작음 186개 [m:std.loudness.label.too_quiet]가 가장 많다.
- 만족 기준: 음량 만족 리뷰 502개 [m:std.loudness.pos]의 쓰는 곳을 채우는 수준이고, 부정이 가장 적은 상품은 JBL 0.4% [m:std.loudness.best]다.
- 개발 기준: 확인 필요(조사 근거 없음). 최대 음압 목표 대신 크기 단계마다 어디까지 채우는지(책상, 샤워실, 캠핑장)를 상세에 적는다.
- 상세페이지 문구: "Made for close-range listening: desk, shower and campsite" (책상, 샤워, 캠핑처럼 가까이서 듣는 곳에 맞춤). 쓰는 곳별 청취 시험 뒤에만 쓴다.
> "작은 방이나 혼자 쓰기에는 괜찮지만 넓은 곳을 채우거나 여럿이 쓰기에는 힘에 부친다" (JBL, 4★, R3AUV6OKK7THXK)

#### 기준 3: 배터리 재생 시간과 충전(원인 5, 6, 7, 8 대응)
- 감점 기준: 배터리 불만 가중 3.2% [m:std.battery.neg_pct], 그중 재생 시간이 짧음 343개 [m:std.battery.label.short_runtime]가 가장 많다.
- 만족 기준: 배터리 만족 리뷰 365개 [m:std.battery.pos]의 표기한 시간을 채우는 수준이고, 부정이 가장 적은 상품은 Anker 1.5% [m:std.battery.best]다.
- 개발 기준: 재생 시간은 IEC 63296-1 [r:tst_08](미국 채택판 ANSI/CTA-6008 [r:tst_09])로 재고, 경쟁사처럼 음량과 온도 조건을 함께 적는다 [r:tst_10]. soundcore 작은 모델은 13~20시간을 표기한다 [r:ind_14]. 목표 시간, 큰 음량 조건의 하한, 잔량 표시 단계는 확인 필요(조사 근거 없음).
- 상세페이지 문구: "Honest playtime, measured at half volume and printed on the box" (절반 음량에서 잰 정직한 재생 시간을 상자에 표기). 재생 시간 시험을 통과한 뒤에만 쓴다.
> "적당한 음량에서 표기한 24시간을 거뜬히 채운다, 인상적이다" (Anker, 4★, R3JG5LZRAF3B3N)

#### 기준 4: 연결(원인 14, 15 대응)
- 감점 기준: 연결 불만 가중 2.0% [m:std.connectivity.neg_pct], 그중 연결이 자주 끊김 116개 [m:std.connectivity.label.connection_drops]가 가장 많다.
- 만족 기준: 연결 만족 리뷰 302개 [m:std.connectivity.pos]의 빠르게 짝짓고 끊기지 않는 수준이고, 부정이 가장 적은 상품은 DEWALT 0.4% [m:std.connectivity.best]다.
- 개발 기준: 판매 전에 Bluetooth SIG 인증 절차를 마치고 [r:reg_06], JBL Go 4, Clip 5, Xtreme 4처럼 블루투스 5.3(LE 오디오)을 쓴다 [r:ind_09]. 연결 거리와 끊김 시험 기준은 확인 필요(조사 근거 없음).
- 상세페이지 문구: "Quick pairing and stereo link, with every compatible model listed" (빠른 페어링과 스테레오 묶기, 묶을 수 있는 모델을 모두 표기). 묶기 시험 뒤 호환 목록을 확정한 다음에만 쓴다.
> "같은 세대의 다른 모델과는 묶는 기술이 호환되지 않는다" (JBL, 4★, RWDAZSF8JSD7G)

#### 기준 5: 방수와 야외 사용(원인 13 대응)
- 감점 기준: 방수 불만 가중 0.3% [m:std.water.neg_pct], 그중 방수가 아니거나 약함 29개 [m:std.water.label.not_waterproof]가 가장 많다.
- 만족 기준: 방수 만족 리뷰 100개 [m:std.water.pos]의 비와 물튀김에 걱정 없는 수준이고, 부정이 가장 적은 상품은 JBL 0.0% [m:std.water.best]다.
- 개발 기준: IP 등급은 IEC 60529로 시험하고 [r:tst_01], JBL 작은 신제품과 같은 IP67 [r:ind_09]을 목표로 한다. 충전 단자 덮개의 내구 기준은 확인 필요(조사 근거 없음).
- 상세페이지 문구: "IP67 dustproof and waterproof, ready for the shower and the beach" (IP67 방진 방수, 샤워와 해변에서도). IP67 시험을 통과한 뒤에만 쓴다.
> "충전 단자가 완전히 드러나 있어 정말 방수인지 모르겠다" (JBL, 4★, R3QJ68GNQ0IFOH)

#### 기준 6: 고장과 내구성(원인 10, 11, 12 대응)
- 감점 기준: 내구성 불만 가중 3.3% [m:std.durability.neg_pct], 그중 쓰다가 고장 남 307개 [m:std.durability.label.stopped_working]가 가장 많다.
- 만족 기준: 몇 달 뒤에도 그대로 켜지는 수준을 기준으로 둔다. 내구성 만족 리뷰는 274개 [m:std.durability.pos]이고, 부정이 가장 적은 상품은 JBL 1.9% [m:std.durability.best]다.
- 개발 기준: 낙하는 경쟁사처럼 콘크리트 바닥 위 1m [r:tst_05], 또는 1.5m(바닥 조건 미기재) [r:tst_06] 높이로 시험한다. 충방전 반복 수명과 출고 검사 기준은 확인 필요(조사 근거 없음).
- 상세페이지 문구: "Drop-tested and built to keep playing season after season" (낙하 시험을 거쳐 여러 계절 계속 쓰도록). 낙하와 수명 시험을 통과한 뒤에만 쓴다.
> "여러 해 동안 스피커를 많이 써 봤지만 이렇게 빨리 기계적으로 고장 난 건 처음이다" (Soundcore, 1★, R3QYKXJZGG6H6S)

#### 기준 7: 버튼, 앱, 통화(원인 16, 17 대응)
- 감점 기준: 조작 불만 가중 2.1% [m:std.controls.neg_pct], 그중 버튼 불편이나 곡 넘기기 버튼 없음 71개 [m:std.controls.label.awkward_buttons]가 가장 많다.
- 만족 기준: 조작 만족 리뷰 221개 [m:std.controls.pos]의 버튼만으로 쉽게 쓰는 수준이고, 부정이 가장 적은 상품은 JBL 0.7% [m:std.controls.best]다.
- 개발 기준: 확인 필요(조사 근거 없음). 버튼 높이, 표시 대비, 마이크 성능 기준을 찾지 못했다.
- 상세페이지 문구: "Raised buttons you can find by touch, full control without the app" (손으로 찾을 수 있는 튀어나온 버튼, 앱 없이도 모든 기본 기능). 사용성 시험 뒤에만 쓴다.
> "버튼에 결이나 손에 느껴지는 감촉이 전혀 없다" (Soundcore, 4★, R36CGV22MXIRHN)

#### 기준 8: 크기와 휴대(원인 12 대응)
- 감점 기준: 휴대 불만 가중 1.2% [m:std.portability.neg_pct], 그중 클립이 약하거나 쓰기 불편함 45개 [m:std.portability.label.clip_weak_awkward]가 가장 많다.
- 만족 기준: 휴대 만족 리뷰 435개 [m:std.portability.pos]의 가방에 넣고 걸기 쉬운 수준이고, 부정이 가장 적은 상품은 Anker 0.2% [m:std.portability.best]다.
- 개발 기준: 끈 달린 초소형 경쟁 사례 [r:ind_22]처럼 부착 부품을 몸체와 함께 설계한다. 클립 고정력과 반복 굽힘 시험 기준은 확인 필요(조사 근거 없음).
- 상세페이지 문구: "Built-in carabiner that clips on and stays on" (걸면 빠지지 않는 일체형 카라비너). 고정력 시험 뒤에만 쓴다.
> "클립이 약해서 고정이 안 된다" (DEWALT, 2★, R1OU7LUX1WQ8XO)

#### 기준 9: 발열과 안전(원인 7 대응)
- 감점 기준: 이 기준의 부정은 몸 반응 리뷰 3개 [m:std.safety.neg], 가중 0.0% [m:std.safety.neg_pct]만 세고, 충전 단자 과열과 녹음, 충전 중 연기는 안전 인용으로 따로 본다.
- 만족 기준: 긍정 리뷰는 0개 [m:std.safety.pos]라 발열과 과열 언급이 없는 수준을 기준으로 둔다.
- 개발 기준: 셀과 배터리는 UN 38.3 [r:reg_08]과 IEC 62133-2 [r:tst_14], 완제품은 UL 62368-1 [r:tst_15]로 시험한다. 충전 단자 온도 상한은 확인 필요(조사 근거 없음).
- 상세페이지 문구: "Battery tested to UN 38.3 and IEC 62133-2" (UN 38.3과 IEC 62133-2 시험을 거친 배터리). 시험 통과 뒤에만 쓴다.
> "충전 단자가 과열되기 시작해 꽂는 충전 케이블마다 녹였다" (Anker, 1★, R2T1NCQNCWSPCN)

#### 기준 10: 구성품과 광고(원인 6, 9, 15 대응)
- 감점 기준: 구성품과 광고 불만 가중 1.2% [m:std.box_claims.neg_pct], 그중 충전기나 어댑터가 원래 안 들어 있음 135개 [m:std.box_claims.label.charger_not_included_by_design]가 가장 많다.
- 만족 기준: 설명대로 왔다는 리뷰 34개 [m:std.box_claims.pos]처럼 상자와 기능이 상세와 같은 수준이고, 부정이 가장 적은 상품은 Soundcore 0.2% [m:std.box_claims.best]다.
- 개발 기준: 서면 보증 전문을 구매 전에 볼 수 있게 하고 [r:reg_12], 캘리포니아에서는 내장 배터리 제품에 제조사 이름이나 브랜드를 표시한다 [r:reg_16](블루투스 스피커가 SB 1215 대상 품목이면, 대상 여부는 확인 필요). 상자 구성(케이블 단자 종류, 어댑터 유무) 표기 기준은 확인 필요(조사 근거 없음).
- 상세페이지 문구: "In the box: speaker and USB-C charging cable. Wall adapter not included" (상자 구성: 스피커와 USB-C 충전 케이블, 벽 충전기는 별도). 실제 구성과 맞춘 뒤에만 쓴다.
> "C to C 케이블이라 어댑터가 따로 필요한데, 어댑터는 주지 않는다" (Anker, 3★, R84VZL42VZCY8)

#### 기준 11: 가격 대비 가치(원인 10 대응)
- 감점 기준: 가치 불만 가중 1.3% [m:std.value.neg_pct], 그중 돈값을 못 함 110개 [m:std.value.label.not_worth_money]가 가장 많다.
- 만족 기준: 가치 만족 리뷰 510개 [m:std.value.pos]의 값에 비해 좋다는 수준이고, 부정이 가장 적은 상품은 Anker 0.3% [m:std.value.best]다.
- 개발 기준: JBL 작은 단계의 출시가 Go 4 [r:ind_06]와 Clip 5 [r:ind_07] 사이에서 값을 정하고, 가격 구조 절의 묶음 값과 함께 확인한다.
- 상세페이지 문구: "Full-day playtime in a clip-size speaker" (손바닥 크기에 하루 종일 가는 재생 시간). 재생 시간 시험으로 하루 사용 시간을 확인한 뒤에만 쓴다.
> "그 값이면 몇 번이 아니라 몇 년은 갈 거라 기대한다" (JBL, 1★, R38I9299FDEGG6)

### 하위 카테고리별 출시 계획
- **첫 출시, 손바닥 크기 클립형(Portable Bluetooth Speakers)**: 샤워와 야외를 함께 받는 IP67 카라비너형으로 낸다. shower speaker 58,183 [m:std.water.term.shower speaker], small speaker 19,228 [m:std.portability.term.small speaker]처럼 브랜드 없는 검색어를 노린다.
- **다음 출시, 중간 크기**: 시장 가격 2구간 131.76~228.99 [m:m.price_band2_range]의 매출 비중이 60.6% [m:m.price_band2_share]로 가장 크지만 JBL Flip과 Charge가 있는 자리라, 첫 상품의 재생 시간 신뢰를 쌓은 뒤 연다.
- **그다음, 몸에 다는 작업용**: 작업장을 말한 리뷰 3.8% [m:f.sound.usage_location.work_jobsite.w], 마이크와 통화 불만 48개 [m:std.controls.label.poor_mic_calls]가 있어 통화 마이크를 갖춘 변형으로 검토한다(조사 상품은 DEWALT 하나라 확인 필요).
- **보류, 큰 야외용과 파티용**: 조사 상품이 Soundcore Boom 2뿐이라 판단하지 않는다. 파티 검색어 party bluetooth speakers bass는 11,824 [m:std.sound.term.party bluetooth speakers bass]다.

### 가격 구조
- **읽는 법**: 묶음 값은 단위로 나누지 않은 상품 한 개의 가격이고, 묶음마다 상품이 적다(낮음 4개 [m:price.band0.n], 중간 3개 [m:price.band1.n]).
- **낮음 묶음**: 22.49~36.07달러 [m:price.band0.range], 음질 부정 4.2% [m:price.band0.skin_neg]로 세 묶음 가운데 가장 높다.
- **낮음 묶음의 배터리와 별점**: 배터리와 충전 부정 2.5% [m:price.band0.head_neg], 별점 4.57★ [m:price.band0.star]로 별점이 가장 낮다.
- **중간 묶음**: 49.22~65.10달러 [m:price.band1.range], 배터리와 충전 부정 4.1% [m:price.band1.head_neg]로 세 묶음 가운데 가장 높다(JBL Go 4, JBL Clip 5, DEWALT).
- **중간 묶음의 음질과 별점**: 음질 부정 2.3% [m:price.band1.eff_neg], 별점 4.67★ [m:price.band1.star]이다.
- **높음 묶음**: 89.17~154.82달러 [m:price.band2.range], 음질 부정 2.0% [m:price.band2.skin_neg]로 가장 낮다.
- **높음 묶음의 배터리와 별점**: 배터리와 충전 부정 3.0% [m:price.band2.head_neg], 별점 4.69★ [m:price.band2.star]이다.
- **나란히만 읽기**: 높음 묶음도 3개 [m:price.band2.n]뿐이라, 가격이 불만을 만든다고 읽지 않고 나란히만 놓는다.
- **시장 가격대**: 2구간 매출 비중 60.6% [m:m.price_band2_share], 평균 별점 4.34★ [m:m.price_band2_rating]이다.
- **시장 위쪽 구간**: 3구간 302.06~1606.67 [m:m.price_band3_range]은 매출 비중 22.0% [m:m.price_band3_share]이고 큰 야외용과 집 오디오가 섞여 첫 상품 범위 밖이다(브랜드 평균 가격 구간이라 단품 가격 근거로는 약함).
- **권고(확인 필요)**: 첫 상품은 중간 묶음 49.22~65.10달러 [m:price.band1.range] 안에서 JBL Go 4 출시가 [r:ind_06]와 Clip 5 출시가 [r:ind_07] 사이에 두고, 값을 더 내리기보다 같은 값에서 재생 시간과 충전 신뢰로 이긴다.

### 메시지와 키워드
- **썸네일**: "Real Playtime, Tested at Half Volume" (절반 음량에서 잰 실제 재생 시간)과 "IP67 + Carabiner" (IP67 방수와 카라비너) 두 줄, 재생 시간과 방수 시험 통과 뒤에만.
- **상세**: 재생 시간과 그 시험 조건 [r:tst_08], 잔량 표시등 읽는 법, 상자 구성(케이블 단자 종류, 어댑터 별도), 묶을 수 있는 모델 목록, 보증 전문 [r:reg_12]을 적는다.
- **박스 안**: 첫 충전 방법, 잔량 표시등 색의 뜻, 충전 단자 덮개를 닫는 법, 두 대 묶기 순서, 교환 연락처를 담은 안내지.
- **키워드**: shower speaker 58,183 [m:std.water.term.shower speaker], small bluetooth speaker 26,328 [m:std.portability.term.small bluetooth speaker]를 기본으로 두고 mini speaker, waterproof speaker, bluetooth speaker를 더한다. jbl clip, jbl clip 5는 경쟁 브랜드 검색어라 광고 대상으로만 검토한다.

### 실행 순서
1. **P1 셀 용량과 재생 시간 목표**: IEC 63296-1 [r:tst_08]로 재는 시험 조건을 먼저 정하고 셀 용량을 고른다.
2. **P1 배터리 안전 시험**: UN 38.3 [r:reg_08]과 IEC 62133-2 [r:tst_14], 운송용 시험 요약서 [r:reg_09].
3. **P1 충전 회로와 단자**: 충전 보호 회로, 단자 덮개, 충방전 반복 수명 시험(합격 기준은 확인 필요).
4. **P1 저음 튜닝과 큰 음량 청음**: 중립 기본 튜닝에 저음 강화 모드 [r:ind_16]를 두고 최대 음량의 찌그러짐을 확인한다.
5. **P1 방수와 낙하 시험**: IEC 60529 [r:tst_01]로 IP67, 콘크리트 위 낙하 [r:tst_05].
6. **P1 무선 인증**: FCC Part 15 인증 [r:reg_01]과 Bluetooth SIG 인증 [r:reg_06].
7. **P1 표시와 포장**: FCC ID 표시 [r:reg_02], 준수 문구 [r:reg_03], 리튬 전지 표지 [r:reg_11], 캘리포니아 브랜드 표시 [r:reg_16], 보증 전문 [r:reg_12].
8. **P1 출고 검사와 봉인 포장**: 첫날 불량과 새 제품이 아니라는 불만을 줄이는 출고 검사(기준은 확인 필요).
9. **P1 버튼 설계**: 튀어나온 버튼과 대비되는 표시, 기본 기능을 앱 없이 쓰게 한다.
10. **P2 앱과 EQ**: 출시 뒤 리뷰를 보고 EQ와 조명 끄기를 앱에 더한다.
11. **P2 묶기 호환 목록 관리**: 다음 세대에도 묶기 방식을 유지하고 바뀌면 모델 이름을 바꾼다.
12. **P2 중간 크기 모델**: 첫 상품의 재생 시간 신뢰를 확인한 뒤 연다.

### 개발 단계와 관문
- **배터리 관문**: 시험 조건을 적은 재생 시간이 표기와 맞고, 충방전 반복 뒤 용량이 유지되어야 한다(조사 상품 기준 리뷰어가 말한 재생 시간 중앙값 4시간 [m:f.battery.battery_runtime_hours.median], 목표값은 확인 필요).
- **안전과 운송 관문**: UN 38.3 형식 시험 [r:reg_08], IEC 62133-2 [r:tst_14], UL 62368-1 [r:tst_15]을 통과하고, 작은 리튬 이온 전지 예외는 100Wh 이하에만 해당하는지 확인한다 [r:reg_10].
- **무선과 표시 관문**: FCC 인증 [r:reg_01], 설명서의 개조 경고 [r:reg_05], 새 설계의 Bluetooth SIG 인증 수수료 [r:reg_07]까지 마쳐야 출시한다.
- **캘리포니아 관문**: 사용자가 쉽게 뺄 수 없는 배터리가 든 제품은 SB 1215 대상이고 [r:reg_14], 2026년부터 구매 때 재활용 수수료가 붙는다 [r:reg_15]. 블루투스 스피커가 대상 품목인지와 수수료 금액은 확인 필요.
- **충전기 효율 기준**: 미국 에너지부가 배터리 충전기 효율 기준을 없애자고 제안했지만 최종 여부는 확인되지 않아 [r:reg_17] 출시 시점에 다시 본다.
- **출시 뒤 관문**: 첫 리뷰의 배터리와 충전 부정 비율을 조사 상품 기준 3.2% [m:head.topic_neg]와 비교하고, 문제까지 기간 중앙값이 90일 [m:f.durability.time_to_problem_days.median]이라 출시 몇 달 뒤의 고장 리뷰를 따로 본다.

### 결론
- **무엇을**: 광고한 조건 그대로 재생 시간을 지키는 손바닥 크기 클립형 IP67 방수 스피커.
- **누구에게**: 샤워실, 야외, 일터에서 가까이 두고 듣는 사람(야외를 말한 리뷰 6.9% [m:f.sound.usage_location.outdoor_yard_water.w]).
- **얼마에**: 조사 상품 중간 묶음 49.22~65.10달러 [m:price.band1.range] 안(확인 필요).
- **무엇으로 이기는지**: 배터리와 충전 부정을 조사 상품 기준 3.2% [m:head.topic_neg]보다 낮추는 시험 조건 표기, 충전 보호, 잔량 표시.

## 05 한 장 요약
### 제품 해부도
1. **배터리 셀과 전력 관리**: 작은 몸체에서도 표기 시간을 채우는 셀 용량, 시험 조건을 상자에 표기 [r:tst_08] (재생 시간이 짧음 343개 [m:std.battery.label.short_runtime])
2. **충전 단자와 덮개**: 과열 보호가 있는 USB-C 단자와 닫히는 덮개 (충전 단자 덮개 없음 8개 [m:std.water.label.port_cover_missing])
3. **잔량 표시등**: 몸체에서 단계로 보이는 잔량 표시, 끌 수 있는 부족 경고음 (잔량 표시나 부족 경고가 없음 26개 [m:f.battery.battery_indicator_issue.no_indicator])
4. **드라이버와 저음 튜닝**: 중립 기본 튜닝에 켜고 끄는 저음 강화 [r:ind_16] (저음이 부족함 178개 [m:f.sound.sound_band_direction.bass_lacking])
5. **버튼**: 튀어나오고 대비되는 버튼, 기본 기능은 앱 없이 (손으로 구분이 안 되거나 장갑 끼면 누르기 어려움 20개 [m:f.controls.button_control_issue.no_tactile_feel])
6. **외함과 방수**: IEC 60529 시험을 거친 IP67 [r:tst_01] (방수가 아니거나 약함 29개 [m:std.water.label.not_waterproof])
7. **카라비너와 끈**: 몸체와 함께 설계한 일체형 고리 (클립이 약하거나 쓰기 불편함 45개 [m:std.portability.label.clip_weak_awkward])
8. **무선 칩과 묶기**: 블루투스 5.3 [r:ind_09], 세대 사이에 유지하는 묶기 방식 (다른 모델이나 세대와 묶이지 않음 43개 [m:std.connectivity.label.model_incompatible])

### 단계와 관문
- **배터리와 충전**: P1 세 건(셀과 재생 시간, 배터리 안전 시험, 충전 회로와 단자), 관문은 시험 조건을 적은 재생 시간과 충방전 수명 (충전이 안 되거나 멈춤 160개 [m:std.battery.label.stopped_charging])
- **소리**: P1 한 건(저음 튜닝과 청음), 관문은 최대 음량의 찌그러짐 확인 (큰 음량에서 찌그러지거나 뭉개짐 51개 [m:std.sound.label.distorts_at_high_volume])
- **외함과 내구**: P1 한 건(방수와 낙하), 관문은 IP67 [r:tst_01]과 낙하 시험 [r:tst_05]
- **인증과 표시**: P1 세 건(무선 인증, 표시와 포장, 출고 검사), 관문은 FCC [r:reg_01]와 Bluetooth SIG [r:reg_06], 리튬 전지 표지 [r:reg_11]
- **출시 뒤**: P2 세 건(앱과 EQ, 묶기 호환 목록, 중간 크기 모델), 관문은 배터리와 충전 부정을 조사 상품 기준 3.2% [m:head.topic_neg]와 비교

## A 데이터와 방법
### 출처
- 리뷰, 태그, 세부 이슈 라벨, 설계 정보, 시장 데이터, 웹 조사, 상품 사양의 파일과 건수는 아래 표에 있다.
- 웹 조사 주장은 76개 중 74개 [m:a.research_verified]를 다시 열어 원문 문장을 확인했고, 확인된 주장만 썼다. 확인되지 않은 두 주장(Beats Pill의 휴대폰 충전 기능, FTC 광고 근거 정책)은 쓰지 않았다.
- 상품 사양은 같은 상품인지 이름만 일치 2개, 일치 확인 8개 [m:spec.match_summary]로 확인했다. 일치 확인 상품의 재생 시간, 방수 방진 등급, 크기와 무게는 브랜드 공식 페이지를 다시 열어 확인한 원문 그대로 점수표와 02장에 실었고, 이름만 일치인 Ortizan과 DEWALT는 사양 값이 없으며 일치 확인 상품 가운데도 크기와 무게 칸이 빈 상품이 있다. 사양은 불만과 나란히만 놓고 원인으로 잇지 않았다.
- 설계 정보 추출 감사 결과는 표본 150개 중 FAIL 6개(4.0%) [m:a.detail_audit]다.
- **읽는 법**: 비율은 별점 묶음(부정, 중립, 긍정) 가중으로 표본 편향을 되돌린 값이고, 원본 수는 무엇을 말하는지, 가중 비율은 얼마나 흔한지로 읽는다.
- **기준표 불만 비율**: 그 기준의 부정 라벨이 붙은 리뷰어 비율이라 불만 지도의 주제 부정 비율과 세는 대상이 다르고(음질은 기준표 4.7% [m:std.sound.neg_pct], 불만 지도 3.0% [m:p.map.sound_quality]), 불만 순위는 불만 지도 값으로 말한다.
- **원인 번호와 별점 격차**: 원인 번호는 대응 방법(설계 결함, 선호 차이)으로 나눈 분류이고, 별점 격차는 그 주제 부정 리뷰와 나머지 리뷰의 가중 평균 별점 차이라 둘 다 인과가 아니다.
- **방향 지수**: 저음 부족 라벨 리뷰에서 저음 과다 라벨 리뷰를 뺀 값을 둘의 합으로 나눈 값(리뷰 가중치 합으로 계산)이고, 양수면 저음 부족 쪽, 음수면 저음 과다 쪽이다. 방향 라벨 리뷰가 적은 상품은 비워 두었다.
- **저음 부족 비율**: 그 설계 정보 값을 말한 리뷰 가운데 저음이 약하거나 없음 라벨이 함께 붙은 리뷰의 비율(원본 수)이다.
- **가격 묶음과 검색량**: 가격 묶음은 조사 상품을 점수표 가격 순으로 세 묶음으로 나눈 것이고 시장 가격대는 브랜드 평균 가격 구간이다. 검색어 옆 숫자는 시장 데이터의 한 달 검색량이다.

### 견고성 점검
- 리뷰를 2,000번 [m:a.robust.n] 다시 뽑으면 배터리와 충전이 불만 1위로 남은 비율은 51.6% [m:a.robust.head_first]로, 품질과 내구성, 음질과 1위를 나눠 갖는다.
- 배터리와 충전 부정 비율(머리 숫자)의 다시 뽑기 구간은 2.8%~3.5% [m:a.robust.head_neg_ci]이다.
- 가장 큰 약점이 배터리와 충전인 상품 수의 다시 뽑기 분포는 0개 0.1%, 1개 3.2%, 2개 28.9%, 3개 46.1%, 4개 20.9%, 5개 0.8% [m:a.robust.weakest_dist]다.
- 상품을 하나씩 빼도 배터리와 충전 부정은 3.0%~3.4% [m:a.robust.loo_head_neg], 저음 과다 쪽 비율은 10.2%~26.2% [m:a.robust.loo_low_share] 안에 있다.
- 상품을 하나씩 뺀 계산에서 결론이 바뀐 것으로 센 경우는 10번 중 10번 [m:a.robust.loo_flips]이다. 전체 데이터에서도 저음 과다 쪽이 절반 이하이고 최대 약점 상품이 과반이 아니어서 이 두 항목은 늘 바뀜으로 셈되고, 불만 1위가 실제로 바뀐 것은 JBL Flip 5, JBL Go 4, JBL Clip 5, JBL Charge 6, Soundcore Select 4 Go를 뺐을 때다.
- 이 점검은 고른 상품 안의 표본 흔들림만 재고, 어떤 상품을 골랐는지에 따른 치우침은 재지 못한다.

### 주의 사항
- 리뷰는 공유 리뷰 DB 표본이라 낮은 별점이 실제보다 많고, 비율은 별점 묶음 가중으로 되돌렸다(표본 평균과 가중 평균 별점은 원문 목록).
- 자유 서술에서 뽑은 수치(말한 재생 시간, 문제까지 걸린 날 등)는 리뷰어가 적은 값이라 측정값이 아니고 방향과 분포로만 읽는다.
- 개발 기준의 사양 숫자는 웹 조사 출처를 근거로 한 시작점이라 시험으로 확인해야 한다.
- 조사 상품이 적고 대부분 한 하위 카테고리(Portable Bluetooth Speakers)라 상품끼리, 하위 카테고리끼리의 비교가 약하고, JBL 상품이 가장 많아 결과가 이 브랜드 쪽으로 기울 수 있다.
- 시장 데이터(spd-amz-market)의 매출, 점유율, 증감, 승률 칸은 문서에 단위가 없어 단위 미확인으로 적었고, 연 환산 값은 월 매출 칸을 달러로 가정한 것이다.
- ASIN은 매출 순위가 아니라 공유 DB에 리뷰가 많은 후보 가운데 고른 상품이고(상품 확인 관문에서 사람이 확인), 팀 DB 리뷰만 썼으며 유료 수집은 켜지 않았다.
- 성장 배수 머리 숫자는 후보 검색어 264개 [m:m.growth_candidates] 가운데 주간 이력을 받은 검색어가 0개 [m:m.growth_ranked]라 쓰지 않았고, 시장 데이터의 yoYChangePct 칸은 뜻과 단위가 확인되지 않아 검색 수요 표의 전년 대비 칸도 참고로만 본다.
- 배터리와 고장 집중 분석의 문제까지 걸린 날은 같은 설계 정보 항목이라 두 분석에서 같은 값이고, 배터리 문제만의 기간이 아니다.
- 가격 묶음은 단위로 나누지 않은 상품 한 개의 가격으로 나눠 크기가 다른 상품이 같은 묶음에 섞이고, 가격이 없어 묶음에서 뺀 상품은 0개 [m:price.unpriced]다.
- 정답 세트로 잰 sonnet 태그는 주제 F1 0.83 [m:acc.topic_f1]으로 기준을 넘었지만 감성 전체 일치 87.7% [m:acc.sentiment]는 판정 기준에 못 미친다.
- 감성 방향 일치는 98.9% [m:acc.direction]로 높고 한쪽이라도 mixed인 짝의 mixed 일치는 35.0% [m:acc.mixed]라, 어긋남은 주로 mixed가 낀 짝에 있어 부정 비율이 조금 움직일 수 있다.
- 미국 시장 규모는 보고서마다 범위(블루투스 스피커, 들고 다니는 제품, 무선 스피커 전체)와 연도가 달라 더하거나 곱하지 않았다.
- 아직 찾지 못한 것: 블루투스 스피커 과열 리콜 원문, 캘리포니아 Proposition 65 경고 원문, SB 1215 수수료 금액과 대상 품목, IEC 63296-1의 측정 음압과 절차, 연결 거리와 끊김의 공인 시험 기준, 버튼과 클립의 시험 기준. 해당 칸은 확인 필요로 남겼다.
