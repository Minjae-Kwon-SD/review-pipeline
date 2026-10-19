# 아마존 미국 요가 매트 제품 개발 가이드
> "두 번 썼는데 벌써 작은 구멍이 생기고 있다" (Gaiam, 4★, R3EQ959LNHZ85K)

## 머리 숫자
- [head.topic_neg] 만듦새와 내구성을 부정으로 말한 리뷰어 비율(별점 가중)로 불만 1위이고, 리뷰를 다시 뽑아도 1위로 남은 비율이 99.2% [m:a.robust.head_first]라 찢김과 윗층 분리를 첫 개발 관문으로 둔다. 그다음은 디자인과 크기 6.2% [m:p.map.design]다.
- [head.topic_weakest] 가장 큰 약점이 만듦새와 내구성인 상품 수로, 그 상품은 Gaiam Dry-Grip 매트(내구성 부정 17.3% [m:s.B0BYFLL1LV.topic_neg])다. 이 상품을 빼면 불만 1위가 끈과 휴대 구성품으로 바뀌어, 상품 하나씩 빼 본 점검에서 결론이 바뀐 경우가 6번 중 1번 [m:a.robust.loo_flips]이다.
- [head.dir_ratio] 두께 불만의 방향으로, 너무 얇음 쪽이 훨씬 많아 첫 상품은 얇은 쪽을 피한다. 방향이 분명한 상품 가운데 Retrospec Solana 매트만 -0.87 [m:s.B092XTMNCC.dir_index]로 너무 두꺼움 쪽이고 Gaiam 상품 셋은 얇음 쪽이라, 두께 단계를 둘로 나눠 고르게 한다(단계 값은 확인 필요).
- [head.market_month] Yoga Mats 노드의 월 매출 칸이고, 1위 브랜드는 Gaiam 17.7% [m:m.top1_YM](매출 점유율)다. 통화가 확인되지 않아 시장 크기의 방향으로만 읽는다.
- [head.fastest_term] 두 기간의 주간 검색 이력이 있는 검색어 28개 [m:m.growth_ranked] 가운데 가장 빨리 크는 검색어로, 최근 검색량이 지난해 같은 기간의 1.89배 [m:head.growth_multiple]다. 미끄럼 방지 검색어라 그립 기준의 마른 조건과 젖은 조건 마찰 시험을 상세페이지 주장의 근거로 둔다.


## 01 시장 개요
**TL;DR** 요가 매트는 이미 많이 찾는 범주이고(공통 검색어 검색량 합 2,505,343 [m:m.terms_common_volume]), Yoga Mats 노드는 1위가 Gaiam 17.7% [m:m.top1_YM]인 노드다. 첫 상품은 매출이 몰린 시장 가격 1구간 안에서 쿠션 있는 두께, 실측 크기 표기, 매트를 붙잡는 끈 구성을 갖춘 매트로 두고 길이 단계는 출시 뒤 검토(P2)하는 것을 확인이 필요한 권고로 둔다.

### TAM, SAM, SOM
- **TAM(전 세계)**: IMARC는 세계 요가 매트 시장을 2025년 167억 달러 [r:mkt_01], 2026년 177억 달러 [r:mkt_02]로 본다.
- **TAM 보고서 사이 차이**: The Insight Partners는 2025년을 103.9억 달러로 보고 [r:mkt_06], Grand View Research는 2023년을 136억 달러로 본다 [r:mkt_08]. 보고서마다 값이 달라 한 값으로 단정하지 않는다.
- **성장 전망 1**: IMARC는 2026~2034년 연평균 4.51% [r:mkt_03], The Insight Partners는 같은 기간 5.93% [r:mkt_07] 성장을 전망한다.
- **성장 전망 2**: Technavio는 연평균 5.6% [r:mkt_11], Grand View Research는 연평균 3.6% [r:mkt_09]로 보아 성장률도 보고서마다 갈린다.
- **북미와 미국**: IMARC는 2025년 북미 비중을 41.8% 넘게 보고 [r:mkt_04], 북미 매출 가운데 미국 몫을 88.00%로 본다 [r:mkt_05]. 미국만의 시장 금액은 공개 요약에서 찾지 못했다.
- **SAM(아마존 미국 Yoga Mats 노드)**: 월 매출 칸이 9,116,723(월 매출 칸, 통화 미확인) [m:head.market_month]이다. 연 환산 값 109,400,681(가정: 통화 미확인 월 매출 x 12, 계절 변동 미반영) [m:head.market_year]은 가정이라 SAM 확정 값으로 쓰지 않는다.
- **SAM에 더하지 않는 노드**: Exercise Mats 노드도 매트를 팔지만 하위 카테고리 표에 매출 칸이 없고, Yoga Equipment와 Exercise & Fitness Accessories는 매트만 담는 노드인지 확인되지 않아 SAM에 더하지 않는다(확인 필요).
- **SOM**: 첫 해 목표 매출이나 점유율을 정할 근거는 없다(확인 필요, 조사 근거 없음). 출시 전에는 판정 3개의 1위와 상위 10개 점유율을 경쟁 강도로만 참고하고, 출시 뒤 실제 판매로 다시 정할 것을 권고한다.

### 판정 3개
- **침투: 이미 넓게 찾는 범주**: 공통 검색어 72개 [m:m.terms_common_n]의 검색량 합이 2,505,343 [m:m.terms_common_volume]이라, 범주를 알리는 일보다 이미 찾는 사람에게 고르게 하는 일이 과제다. 검색량 합에는 범위 밖 검색어도 섞여 있다(검색 수요).
- **경쟁 집중: 한 브랜드보다 상위 묶음 중심**: Yoga Mats 상위 10개 브랜드 점유율 합 63.9% [m:m.top10_share_YM], 1위 Gaiam 17.7% [m:m.top1_YM]이다(브랜드 매출 ÷ 노드 매출로 확인한 매출 점유율). 상위 10개에는 Amazon Basics, Retrospec, Manduka, CAP 같은 브랜드가 함께 있다.
- **기회: 매출이 몰린 시장 가격 1구간**: 시장 가격 1구간 20.68~41.93 [m:m.price_band1_range]의 매출 비중이 56.1% [m:m.price_band1_share]로 세 구간 가운데 가장 크고, 조사 상품의 단품 가격도 대부분 이 구간 안에 든다. 이 구간 안에서 두께와 구성으로 고르는 자리를 노린다. 시장 가격대 표는 브랜드 평균 가격으로 나눈 구간이라 상품 한 개 가격과 기준이 다르다.

### 검색 수요
- 검색어는 성별로 나뉘지 않고 공통 검색어 72개 [m:m.terms_common_n]를 함께 보며, 성별로 상품을 나누지 않는다.
- 상위 검색어는 yoga mat, mat, play mat, exercise equipment, gymnastics mat, pilates, yoga mat thick 순이고, 상위 10개에 브랜드 이름이 든 검색어는 없다.
- play mat, gymnastics mat, exercise equipment처럼 이번 범위(아이 놀이 매트 제외) 밖이거나 넓은 검색어가 섞여 있어, 검색량 합을 요가 매트 수요로 그대로 읽지 않는다.
- **두께 검색어**: yoga mat thick 60,648 [m:std.thickness.term.yoga mat thick], thick yoga mat 40,757 [m:std.thickness.term.thick yoga mat]이다.
- **필라테스 검색어**: pilates 61,313 [m:std.stability.term.pilates], pilates mat 52,675 [m:std.stability.term.pilates mat]이라, 요가 밖 바닥 운동 쓰임도 함께 본다.
- **그립 검색어**: yoga mat non slip 18,080 [m:std.grip.term.yoga mat non slip], hot yoga mat 15,342 [m:std.grip.term.hot yoga mat]이다.
- **빠르게 크는 검색어 후보**: 기준 검색량을 넘는 검색어 121개 [m:m.growth_candidates] 가운데 두 기간의 주간 이력이 있는 검색어 28개 [m:m.growth_ranked]로 성장 배수를 견줬다(A장 주의 사항).
- **가장 빨리 크는 검색어**: yoga mat non slip으로, 최근 검색량 117,775 [m:head.growth_recent]가 지난해 같은 기간 62,273 [m:head.growth_prior]보다 크다. 그립 불만(03장 집중 분석 3)과 나란히 본다.

### 진입 조건
- **두께**: 두꺼운 쪽 검색어가 크고(yoga mat thick 60,648 [m:std.thickness.term.yoga mat thick]), 두께감 방향도 너무 얇거나 쿠션이 모자람 177개 [m:f.thickness.thickness_feel.too_thin]가 반대쪽보다 많아 쿠션 있는 두께를 먼저 낸다. 두꺼운 상품에는 너무 두껍거나 푹신하다는 말도 있어(02장 점수표 해설) 두께를 한 가지로 낼지 두 단계로 낼지와 두께 수치는 확인 필요(조사 근거 없음)다.
- **재질과 겉면**: 세계 시장에서 재질별로는 PVC가 38.7%로 가장 크다는 보고서가 있고 [r:mkt_16], 조사 상품은 폼 매트(Retrospec Solana, CAP Extra Thick)와 PVC 매트(Gaiam Premium Print, latex-free PVC [m:spec.B09WF4GPPC.material])가 섞였다. 핫요가나 땀이 많이 나는 수업을 말한 리뷰가 151개 [m:f.thickness.activity.hot_yoga]라 땀에도 잡히는 겉면을 재질 선택의 조건으로 두고, 재질은 확인 필요다.
- **크기와 길이**: 너비가 좁음 34개 [m:std.size.label.too_narrow], 길이가 짧음 26개 [m:std.size.label.too_short]라 첫 상품은 실측 크기를 적고, 길이 단계는 출시 뒤 검토(P2)한다. Manduka PRO는 85인치 긴 판을 따로 둔다 [r:ind_12].
- **가격대**: 조사 상품의 개당 가격 낮음 묶음은 21.55~22.64달러/개 [m:price.band0.range], 높음 묶음은 39.99~48.98달러/개 [m:price.band2.range]이다. 시장 가격 1구간(판정 3개) 안에 드는 값을 확인이 필요한 권고로 두고, 정할 값은 04장 가격 구조에서 묶음별 불만과 함께 읽는다.
- **구성(끈)**: 들어 있어야 할 끈이 빠져 옴 132개 [m:std.strap.label.strap_missing], 끈이 늘어나거나 헐거워 매트가 빠짐 27개 [m:std.strap.label.strap_loose_slips]다. 끈을 넣는다면 상자 구성과 상세 사진을 맞추고 매트를 붙잡는 끈을 고른다. Retrospec Solana 상품 페이지와 BalanceFrom GoYoga+ 판매처 페이지는 끈을 함께 준다고 적는다 [r:ind_23] [r:ind_29].


## 02 경쟁사
**TL;DR** 조사 상품은 Gaiam이 가장 많고 Retrospec과 CAP이 섞였으며, 모두 Yoga Mats 노드에 있다. 두꺼운 상품(Gaiam Essentials Thick, Retrospec Solana, CAP Extra Thick)의 가장 큰 강점은 두께와 쿠션이고, 만듦새와 내구성이 가장 큰 약점인 상품은 6개 중 1개(리뷰를 다시 뽑아 보면 1~3개) [m:head.topic_weakest]이며 나머지는 끈, 크기, 두께, 그립으로 갈린다.

### 점수표 해설
- **읽는 법**: 점수표는 상품마다 개당 가격, 가중 별점, 만듦새와 내구성 부정, 두께 방향 지수, 손상까지 걸린 날, 가장 큰 강점과 약점, 확인된 사양을 나란히 놓는다. 방향 지수는 +면 너무 얇음 쪽, -면 너무 두껍거나 푹신함 쪽이다. 상품이 적어 사양과 불만은 나란히만 놓는다.
- **만듦새와 내구성 부정 최고**: Gaiam Dry-Grip 17.3% [m:s.B0BYFLL1LV.topic_neg]이고 별점도 점수표에서 가장 낮은 4.24★ [m:s.B0BYFLL1LV.star]다. 같은 상품(Marbled 판)의 사양 페이지는 찾지 못함 [m:spec.B0BYFLL1LV.match]이라 사양 칸은 비어 있다.
- **만듦새와 내구성 부정 최저**: Gaiam Classic Print 2.7% [m:s.B01MY5MZSQ.topic_neg], Gaiam Premium Print 2.8% [m:s.B09WF4GPPC.topic_neg]이고, 둘 다 개당 가격 낮음 묶음 상품이다.
- **별점 최고**: Gaiam Premium Print 4.70★ [m:s.B09WF4GPPC.star]이고, 이 상품의 가장 큰 강점은 만듦새와 내구성, 가장 큰 약점은 그립과 미끄럼이다.
- **두께 방향, 얇은 쪽**: Gaiam Classic Print +1.00 [m:s.B01MY5MZSQ.dir_index], Gaiam Premium Print +0.96 [m:s.B09WF4GPPC.dir_index]이고, Gaiam Dry-Grip도 너무 얇음 쪽이다.
- **얇은 쪽 상품의 두께 사양**: 소매점 페이지 기준 Gaiam Classic Print는 4 mm [m:spec.B01MY5MZSQ.thickness](ayurveda101.com), Gaiam Premium Print는 6mm [m:spec.B09WF4GPPC.thickness](yeswellness.com)다.
- **두께 방향, 두꺼운 쪽**: Retrospec Solana -0.87 [m:s.B092XTMNCC.dir_index]로 너무 두껍거나 푹신함 쪽이고, 공식 사이트(retrospec.com) 두께는 1” [m:spec.B092XTMNCC.thickness]다. 방향이 분명한 상품 가운데 두꺼운 쪽은 이 상품뿐이라 상품마다 방향이 다르다.
- **방향 빈칸**: Gaiam Essentials Thick과 CAP Extra Thick은 방향 라벨 리뷰가 기준보다 적어 지수가 비어 있다(-). 사양 두께는 Gaiam 공식 페이지 이름 기준(Essentials Fitness Mat & Sling, 이름만 일치) 10mm [m:spec.B07H9PZDQW.thickness], CAP 공식 사이트(capbarbell.com) 1 inch [m:spec.B0CRXCBY1Y.thickness]다.
- **손상까지 걸린 날**: 리뷰어가 적은 값의 중앙값이 Retrospec Solana 14days [m:s.B092XTMNCC.duration_median]로 가장 짧고 Gaiam Premium Print 120days [m:s.B09WF4GPPC.duration_median]로 가장 길다. 측정값이 아니고 상품마다 값의 수가 달라 방향으로만 읽는다.
- **가장 큰 강점**: 두께와 쿠션이 Gaiam Essentials Thick, Retrospec Solana, CAP Extra Thick의 가장 큰 강점이고, Gaiam Classic Print는 디자인과 크기, Gaiam Dry-Grip은 그립과 미끄럼이 가장 큰 강점이다.
- **가장 큰 약점**: 끈과 휴대 구성품이 Gaiam Essentials Thick과 CAP Extra Thick의 가장 큰 약점이고, CAP High Density Exercise Yoga Mat with Strap은 끈을 넣어 판다 [r:ind_25]. Retrospec Solana는 디자인과 크기, Gaiam Classic Print는 두께와 쿠션이 가장 큰 약점이다.
- **크기와 재질 사양**: 공식 사이트 기준 Retrospec Solana는 72x24" [m:spec.B092XTMNCC.size], CAP Extra Thick은 68 inch by 24 inch [m:spec.B0CRXCBY1Y.size]이고, 재질은 둘 다 고밀도 폼 표기다. Retrospec Solana의 가장 큰 약점이 디자인과 크기라는 점과 나란히 둔다.
- **가격**: 점수표 개당 가격은 Gaiam Premium Print 21.55달러 [m:s.B09WF4GPPC.price]에서 Gaiam Dry-Grip 48.98달러 [m:s.B0BYFLL1LV.price]까지다.

### 하위 카테고리 비교
- 조사 상품은 모두 Yoga Mats 노드에 있어 노드끼리 상품을 견주는 비교는 약하다.
- **Exercise Mats**: 1위 BalanceFrom 13.9% [m:m.top1_EM], 상위 10개 브랜드 점유율 합 56.9% [m:m.top10_share_EM](매출 점유율)이다. 이 상위 10개 가운데 Yoga Mats 상위 10개와 겹치는 브랜드는 CAP뿐이라 두 노드는 앞선 브랜드가 다르다.
- **매트 곁 용품 노드**: 하위 카테고리 표에는 Yoga Towels, Yoga Mat Straps, Yoga Mat Bags처럼 매트와 함께 쓰는 용품 노드가 따로 있다. 끈 불만(01장 진입 조건), yoga mat towel 검색어와 나란히 놓고 구성품 범위를 정한다.
- **시장 크기로 더하지 않는 노드**: Yoga Equipment와 Exercise & Fitness Accessories는 매트만 담는 노드인지 확인되지 않아 Yoga Mats 노드와 더하지 않는다(노드 사이 관계는 확인 필요).

### 업계 구조
- **Gaiam의 두께 단계**: Gaiam 공식 사이트 요가 매트 목록의 두께 필터는 6mm 상품 26개를 보인다 [r:ind_07].
- **Gaiam의 여행용과 상위 라인**: 같은 목록에 접는 Foldable Yoga Mat(2mm) [r:ind_09]와 상위 라인 Performance Dry-Grip Yoga Mat(5mm) [r:ind_10]가 있다.
- **Gaiam Premium 2-Color 6mm 사양**: 이 상품 페이지는 68"L x 24"W [r:ind_01], 재질 PVC와 Latex-Free [r:ind_03]를 적는다.
- **Gaiam Premium 2-Color 6mm 냄새와 성분 안내**: 같은 페이지는 새 매트 냄새가 아주 강하지만 해롭지 않다고 미리 적고 [r:ind_05], 펴서 2~3일 바람을 쐰 뒤 쓰라고 안내한다 [r:ind_04]. 라텍스와 가장 해로운 프탈레이트 6종 없이 만들고 평생 보증을 준다고도 적는다 [r:ind_06].
- **Manduka의 라인**: 목록에 PRO Yoga Mat 6mm [r:ind_11], begin yoga mat 5mm [r:ind_14], PRO Travel Yoga Mat 2mm [r:ind_13]가 있다.
- **Manduka PRO의 크기**: Manduka PRO는 85인치 긴 판을 따로 둔다 [r:ind_12]. 판매처 Escapade(escapade.com.hk)는 PRO 85인치를 85x26인치, 9.5파운드로 적는다 [r:ind_16].
- **Manduka PRO의 인증 표시**: 같은 판매처는 PRO를 OEKO-TEX STANDARD 100 인증 PVC로 만든다고 적는다 [r:ind_15].
- **JadeYoga의 천연 고무 매트**: 목록 페이지는 매트를 미국에서 만든다고 적고 [r:ind_20], Harmony Mat 페이지는 라텍스 알레르기가 있으면 닿지 말라고 스스로 적는다 [r:reg_18].
- **JadeYoga의 크기와 여행용**: Harmony Mat는 3/16인치 두께, 24인치 너비에 길이 두 가지이고 [r:ind_17], Voyager Mat는 1/16인치, 1.5파운드다 [r:ind_19]. 작은 Fusion Mini 매트도 따로 판다 [r:ind_21].
- **두꺼운 폼 매트**: Retrospec 목록은 Solana와 Pismo를 폼 매트로 적고 [r:ind_22], ProsourceFit은 Extra Thick Yoga and Pilates Mat를 판다 [r:ind_24].
- **두꺼운 폼 매트의 끈**: Retrospec Solana 1인치 상품 페이지 [r:ind_23], CAP High Density Exercise Yoga Mat with Strap [r:ind_25], 판매처 GreenToe의 BalanceFrom GoYoga+ 페이지 [r:ind_29]가 끈을 함께 준다고 적는다.
- **PVC 밖 재질**: The Stakt Mat은 PVC 대신 EVA 폼 혼합 재질을 쓴다고 적고 [r:ind_26], The Stakt Mat Pro는 3.4파운드다 [r:ind_27].


## 03 문제
**TL;DR** 불만 1위는 만듦새와 내구성 8.9% [m:head.topic_neg]이고, 리뷰를 다시 뽑아도 1위로 남은 비율이 99.2% [m:a.robust.head_first]라 첫 개발 관문으로 둔다. 그다음 디자인과 크기, 끈과 휴대 구성품이 앞서고 냄새, 두께와 쿠션, 그립과 미끄럼은 거의 같은 수준으로 붙어 있다. 집중 분석은 내구성, 두께, 그립, 냄새 넷이고, 분석마다 불만을 원인 번호(설계 결함 또는 선호 차이)로 나눠 04장 기준표와 잇는다.

### 불만 지도
- **만듦새와 내구성 1위**: 부정 언급 리뷰어(가중) 8.9% [m:p.map.build_durability]로 가장 높고, 다시 뽑기에서도 1위로 남은 비율이 99.2% [m:a.robust.head_first]다.
- **2위와 3위**: 디자인과 크기 6.2% [m:p.map.design], 끈과 휴대 구성품 5.0% [m:p.map.carry_strap]이다. 두 주제는 집중 분석에 넣지 않고 04장 크기, 무게, 휴대 기준과 끈과 구성품 기준(03 원인 밖)에서 다룬다.
- **같은 수준의 세 주제**: 냄새 4.3% [m:p.map.odor], 두께와 쿠션 4.2% [m:p.map.cushioning]가 거의 같다.
- **그립도 같은 값**: 그립과 미끄럼 4.2% [m:p.map.grip_traction]로 두께와 쿠션과 같은 수준이다.
- **그 아래 주제**: 신뢰 2.5% [m:p.map.trust], 브랜드 경험 2.2% [m:p.map.brand_experience]이다.
- **흔하지 않은 두 주제**: 안전 1.3% [m:p.map.safety]은 흔하지 않지만 아래 안전에서 따로 읽는다. 묻어남과 얼룩 1.0% [m:p.map.residue_transfer]은 별점 격차가 큰 주제라 아래 별점 격차에서 따로 읽는다.
- **상품 하나를 뺀 점검**: 상품 하나씩 빼 본 6번 중 1번 [m:a.robust.loo_flips] 결론이 바뀌었다. Gaiam B0BYFLL1LV를 빼면 1위가 끈과 휴대 구성품으로 바뀌고 만듦새와 내구성은 6.0% [m:a.robust.B0BYFLL1LV.head_neg]로 내려간다(A장 견고성 점검).

### 별점 격차
- **브랜드 경험**: 부정 1.78★ [m:p.gap1_neg], 격차 -2.78 [m:p.gap1]로 가장 크고, 사지 말라거나 다른 브랜드로 바꾸겠다는 말이 많다.
- **묻어남과 얼룩**: 부정 1.93★ [m:p.gap2_neg], 격차 -2.58 [m:p.gap2]이고, 매트 색이 발이나 바닥에 묻었다는 말이 많다. 이 불만은 집중 분석 1의 원인 5로 묶는다.
- **고객 응대**: 부정 2.15★ [m:p.gap3_neg], 격차 -2.35 [m:p.gap3]이고, 반품이 막히거나 회사 답이 없었다는 말이 많다.
- **읽는 법**: 별점 격차는 그 주제를 부정으로 말한 리뷰와 나머지 리뷰의 별점 차이일 뿐 그 주제가 별점을 낮췄다는 뜻은 아니다.

> "업독 자세를 하는 동안 보라색이 발등에 묻어나기 시작했다" (Gaiam, 2★, RJ351L06ZF6CL)

### 집중 분석 1: 만듦새와 내구성, 층 분리와 찢어짐
- **손상 종류**: 윗면 벗겨짐, 부스러짐, 층이 떨어져 기포가 생김 177개 [m:f.durability.damage_type.peel_flake_crumble], 찢어짐, 구멍 126개 [m:f.durability.damage_type.tear_puncture]가 앞선다.
- **자국과 말림**: 눌린 자국이나 긁힌 자국이 남음 72개 [m:f.durability.damage_type.dent_scratch_mark], 끝이 말리거나 평평하게 펴지지 않음 40개 [m:f.durability.damage_type.curl_not_flat]다.
- **얼룩과 들러붙음**: 매트 자체에 얼룩이나 변색이 생김 36개 [m:f.durability.damage_type.stain_discolor], 겉면이 끈적이거나 녹아 붙음 24개 [m:f.durability.damage_type.sticky_melted]다. 들러붙음 인용은 말아 둔 윗면과 뒷면이 서로 붙었다는 말이 많다.
- **변화까지 쓴 기간**: 리뷰어가 적은 값 208개 [m:f.durability.durability_elapsed_days.n]의 중앙값이 30days [m:f.durability.durability_elapsed_days.median]이다(측정값이 아니라 리뷰어가 말한 기간).
- **짧은 기간과 긴 기간**: 7days 미만 59개 [m:f.durability.durability_elapsed_days.bin0]는 받자마자 흠이 있었다는 말이 많고, 365days 이상 49개 [m:f.durability.durability_elapsed_days.bin4]는 한 해 넘게 쓴 뒤의 상태를 말한다.
- **상품별**: 만듦새와 내구성 부정은 Gaiam B0BYFLL1LV 17.3% [m:s.B0BYFLL1LV.topic_neg]가 가장 높고 Gaiam B01MY5MZSQ 2.7% [m:s.B01MY5MZSQ.topic_neg]가 가장 낮다. 같은 브랜드 안에서도 상품마다 크게 다르다.
- **약점 상품 수**: 가장 큰 약점이 만듦새와 내구성인 상품은 6개 중 1개(리뷰를 다시 뽑아 보면 1~3개) [m:head.topic_weakest]다.

> "두 번 썼는데 벌써 작은 구멍이 생기고 있다" (Gaiam, 4★, R3EQ959LNHZ85K)

> "Lysol을 뿌린 뒤 벗겨지기 시작해서, 수업이 끝날 때마다 바닥에 윗층 조각이 남는다" (Gaiam, 4★, R3HA5YEHE8PCKZ)

**시사점**
- 손상은 받자마자와 몇 년 뒤 양쪽에 모두 있어, 출고 검사(마감 흠)와 반복 사용 시험(윗층 접착, 찢어짐)을 따로 둔다.
- 말아 두는 동안 윗면과 뒷면이 붙는 문제와 색 묻어남은 둘 다 겉면에서 보이는 불만이라 겉면 마감 시험 묶음에서 함께 확인한다.
- 원인 1(설계 결함), 찢어짐과 표면 닳음: 찢어짐이나 구멍 111개 [m:std.durability.label.tears_holes], 표면 닳음이나 자국 87개 [m:std.durability.label.surface_wear]
- 원인 2(설계 결함), 층 분리와 부스러짐: 윗층 분리나 기포 77개 [m:std.durability.label.top_layer_peels], 부스러지거나 조각이 떨어짐 76개 [m:std.durability.label.crumbles_sheds]
- 원인 3(설계 결함), 마감 품질: 품질이 낮거나 싸구려 같음 62개 [m:std.durability.label.low_quality], 받았을 때부터 불량이나 마감 흠 48개 [m:std.durability.label.defect_on_arrival]
- 원인 4(설계 결함), 수명과 말림: 내구성이 약하거나 오래 못 갈 것 같음 42개 [m:std.durability.label.weak_durability], 끝이 말리거나 평평하게 안 펴짐 30개 [m:std.durability.label.curls_not_flat]
- 원인 5(설계 결함), 색과 가루 묻어남: 색이 몸이나 옷에 물듦 35개 [m:std.residue.label.dye_color_transfer], 가루나 부스러기가 몸에 붙음 18개 [m:std.residue.label.material_shedding]

### 집중 분석 2: 두께, 쿠션, 균형, 너무 얇음 쪽 방향
- **두께 방향**: 너무 두껍거나 푹신함 33개 대 너무 얇음 148개(0.22배) [m:head.dir_ratio]로 얇다는 쪽이 훨씬 많다.
- **가중 비율**: 너무 얇음 쪽 3.9% [m:head.dir_high_w], 너무 두껍거나 푹신함 쪽 0.8% [m:head.dir_low_w]이다.
- **만족이 더 큼**: 두께와 쿠션이 알맞음, 충분히 푹신함 510개 [m:f.thickness.thickness_feel.right_thickness], 가중 41.0% [m:f.thickness.thickness_feel.right_thickness.w]라 불만보다 만족이 훨씬 많은 주제다.
- **상품별 방향(얇음 쪽)**: 방향이 분명한 Gaiam 상품은 모두 너무 얇음 쪽이다. B01MY5MZSQ +1.00 [m:s.B01MY5MZSQ.dir_index], B09WF4GPPC +0.96 [m:s.B09WF4GPPC.dir_index]이다.
- **상품별 방향(나머지)**: Gaiam B0BYFLL1LV도 +1.00 [m:s.B0BYFLL1LV.dir_index]으로 얇음 쪽이고, Retrospec B092XTMNCC만 -0.87 [m:s.B092XTMNCC.dir_index]로 너무 두꺼움 쪽이다. Gaiam B07H9PZDQW와 CAP B0CRXCBY1Y는 방향 라벨이 적어 비어 있다.
- **두꺼움 쪽 불만의 쏠림**: Retrospec B092XTMNCC 하나를 빼면 너무 두껍거나 푹신함 쪽 비율이 2.3% [m:a.robust.B092XTMNCC.low_share]로 내려가, 두꺼움 쪽 불만은 거의 이 상품 하나에 몰려 있다.
- **사양과 나란히**: Retrospec B092XTMNCC는 공식 페이지 두께 1” [m:spec.B092XTMNCC.thickness], Gaiam B01MY5MZSQ는 소매점 페이지 두께 4 mm [m:spec.B01MY5MZSQ.thickness]이다. 상품이 적어 두께가 방향을 정한다고 읽지 않고 나란히만 놓는다.
- **리뷰어가 말한 두께**: 값 51개 [m:f.thickness.thickness_mm.n]의 중앙값이 12.7mm [m:f.thickness.thickness_mm.median]다(리뷰어가 적은 값).
- **무릎**: 무릎이 편함 107개 [m:f.thickness.body_part_effect.knee_ok]가 무릎이 아프거나 받쳐 주지 못함 30개 [m:f.thickness.body_part_effect.knee_pain]보다 많다.
- **무릎 통증과 얇음**: 무릎 통증 리뷰 가운데 너무 얇음 라벨이 함께 붙은 것은 30개 중 13개(43.3%) [m:f.thickness.body_part_effect.knee_pain.too_thin]다(함께 나온 수일 뿐 원인 관계는 아님).
- **균형과 늘어남**: 균형과 늘어남 불만 리뷰 93개 [m:std.stability.neg]는 동작 중 매트가 늘어나 균형을 잃는다는 말이 많다.
- **표기와 실물**: 원인 번호에 들지 않은 표기보다 얇음 39개 [m:std.thickness.label.thinner_than_listed]는 04장 설명과 실물 기준에서 다룬다.

> "4mm는 편하게 쓰기에 충분히 두껍지 않다" (Gaiam, 3★, RA4BHEQBTAAAH)

> "요가용으로는 너무 두껍다" (Retrospec, 1★, R1D0E3JBFI44SA)

> "어떤 자세에서는 늘어나서 균형을 잃을 수 있다" (Retrospec, 3★, R31CLFWU7R6IND)

**시사점**
- 불만은 너무 얇음 쪽이 많지만, 두꺼운 쪽을 고른 상품에서는 반대로 너무 두껍고 균형이 어렵다는 불만이 있어 한 두께로 모두를 맞추기 어렵다. 두께 선택지와 쓰임새 안내로 나눠 대응한다.
- 얇음, 쿠션 부족, 눌려 꺼짐, 늘어남은 제품을 고치면 줄어드는 설계 결함으로, 두께 취향과 두꺼워 균형이 어려움은 선택지와 안내로 대응할 선호 차이로 나눈다.
- 원인 6(설계 결함), 얇음과 쿠션 부족: 너무 얇음 111개 [m:std.thickness.label.too_thin], 쿠션이나 패딩 부족 45개 [m:std.thickness.label.lacks_cushion]
- 원인 7(설계 결함), 관절 통증과 꺼짐: 무릎이나 관절이 아픔 19개 [m:std.thickness.label.knee_joint_pain], 눌리면 꺼지거나 쓰다 보니 납작해짐 18개 [m:std.thickness.label.compresses_flat]
- 원인 8(선호 차이), 두께와 단단함 취향: 너무 두껍거나 푹신함 33개 [m:std.thickness.label.too_thick_soft], 딱딱함 14개 [m:std.thickness.label.too_hard]
- 원인 9(설계 결함), 늘어남과 불안정: 매트가 늘어남 34개 [m:std.stability.label.mat_stretches], 균형 잡기 어렵거나 불안정함 29개 [m:std.stability.label.hard_to_balance]
- 원인 10(선호 차이), 두꺼워 균형이 어려움: 두껍거나 푹신해서 균형 잡기 어려움 23개 [m:std.stability.label.too_thick_to_balance]

### 집중 분석 3: 그립과 미끄럼, 손발 미끄러짐과 바닥 밀림
- **손발 미끄러짐**: 조건 말 없이 손발이 미끄러짐 158개 [m:f.grip.grip_condition.hands_feet_slip], 땀이나 물기가 있을 때 손발이 미끄러짐 54개 [m:f.grip.grip_condition.hands_feet_slip_sweaty]이다.
- **마른 상태**: 땀이 나기 전 마른 상태에서도 손발이 미끄러짐은 8개 [m:f.grip.grip_condition.hands_feet_slip_dry]로 적다.
- **바닥 밀림**: 매트가 바닥에서 밀리거나 움직임 80개 [m:f.grip.grip_condition.mat_slides_on_floor]가 밀리지 않음 43개 [m:f.grip.grip_condition.mat_stays_on_floor]보다 많다.
- **잘 잡힌다는 말도 많음**: 땀이 나도 잘 잡힘 86개 [m:f.grip.grip_condition.grips_when_sweaty], 가중 6.7% [m:f.grip.grip_condition.grips_when_sweaty.w]라 그립은 상품에 따라 강점도 된다.
- **반대 방향 선호**: 너무 끈적이거나 잘 안 미끄러져 불편함 18개 [m:f.grip.grip_condition.too_sticky], 매끈하거나 번들거리는 코팅 같은 겉면 17개 [m:f.grip.surface_texture.slick_coating]가 함께 있어 겉면 마감은 양쪽 끝을 모두 본다.
- **쓰는 바닥**: 바닥 종류로는 마루, 강화마루, 나무 바닥 39개 [m:f.grip.use_location.wood_floor], 종류 말 없는 딱딱한 바닥 33개 [m:f.grip.use_location.hard_floor_other]가 많다.
- **땀 나는 운동**: 핫요가, 땀이 많이 나는 수업을 말한 리뷰는 151개 [m:f.grip.activity.hot_yoga]다(그립 불만과 따로 센 값).
- **다칠 위험**: 안전 라벨 미끄러지거나 넘어져 다칠 위험 10개 [m:std.safety.label.slip_injury_risk]가 그립 불만과 이어진다.
- **상품별**: 그립 불만이 가장 적은 상품은 CAP 1.6% [m:std.grip.best]이고, 점수표에서 Gaiam B09WF4GPPC는 가장 큰 약점이 그립과 미끄럼이다.

> "보통 요가 수업에서 땀이 조금만 나도 매트 위에서 이리저리 미끄러진다" (Gaiam, 3★, RSI3BBGOF8YNS)

> "미끄럽고 바닥 위에서 많이 움직인다" (CAP, 3★, R3W4V1LH2J1CG5)

> "끈끈한 겉면은 9개월쯤 가는 것 같고, 그 뒤로 미끄러워진다" (Gaiam, 4★, R6EBF64X7IBS6)

**시사점**
- 손발이 미끄러지는 윗면과 바닥에서 밀리는 뒷면은 다른 면의 문제라 윗면 그립과 뒷면 마찰을 따로 시험한다.
- 그립이 시간이 지나며 떨어진다는 불만이 있어, 새 매트만이 아니라 반복 사용 뒤의 그립도 관문에 넣는다.
- 원인 11(설계 결함), 윗면 미끄러움과 바닥 밀림: 표면이 미끄러움 191개 [m:std.grip.label.surface_slippery], 바닥에서 매트가 밀림 62개 [m:std.grip.label.slides_on_floor]
- 원인 12(설계 결함), 땀과 사용 뒤 그립 저하: 땀이나 물기에 미끄러움 36개 [m:std.grip.label.slips_when_sweaty], 쓰다 보니 그립이 떨어짐 28개 [m:std.grip.label.grip_wears_off]

### 집중 분석 4: 냄새와 성분, 빠지지 않는 새 매트 냄새
- **냄새의 변화**: 시간이 지나거나 바람을 쐬어도 그대로 79개 [m:f.odor.odor_outcome.persists]가 냄새가 사라짐 25개 [m:f.odor.odor_outcome.gone]보다 많다.
- **줄거나 새로 생김**: 냄새가 줄었지만 남음 18개 [m:f.odor.odor_outcome.reduced], 쓰다 보니 땀이나 습기로 냄새가 생김 14개 [m:f.odor.odor_outcome.developed_after_use]다.
- **냄새 기간**: 리뷰어가 적은 값 47개 [m:f.odor.odor_duration_days.n]의 중앙값이 14days [m:f.odor.odor_duration_days.median]이다.
- **오래 가는 냄새**: 365days 이상 냄새가 갔다는 리뷰도 5개 [m:f.odor.odor_duration_days.bin4] 있다.
- **상품별**: 냄새 불만이 가장 적은 상품은 CAP 2.6% [m:std.odor.best]이다.
- **몸 반응과 함께**: 두통, 메스꺼움 판정 리뷰에서 고른 인용은 냄새를 함께 말한다(아래 안전, 함께 나온 말일 뿐 원인 관계로 읽지 않음).

> "일주일 동안 펼쳐서 숨을 쉬게 했는데도 방 전체에 냄새가 진동한다" (Gaiam, 1★, R22ETK6EL0RYIL)

> "하루 꼬박 밖에 두어 바람을 쐬었더니 문제가 완전히 해결됐다" (Gaiam, 4★, R2H55F5G86GVA9)

**시사점**
- 바람을 쐬어 빠진 경우와 빠지지 않은 경우가 함께 있어, 출고 전 냄새 빼기 공정과 냄새 기준을 정하고 상자 안에 바람 쐬는 방법을 적는다.
- 쓰다 보니 생기는 땀 냄새는 처음 냄새와 다른 문제라 세척 안내와 겉면 흡수를 따로 본다.
- 원인 13(설계 결함), 화학 냄새: 화학, 플라스틱, 고무 냄새 135개 [m:std.odor.label.chemical_plastic_smell], 종류 말 없이 냄새가 심함 91개 [m:std.odor.label.bad_smell_unspecified]
- 원인 14(설계 결함), 빠지지 않는 냄새: 바람 쐬고 씻어도 안 빠짐 57개 [m:std.odor.label.smell_persists], 처음 냄새가 나서 바람 쐬기나 세척이 필요함 44개 [m:std.odor.label.initial_smell_aired_out]
- 원인 15(설계 결함), 사용 뒤 냄새와 이상한 냄새: 쓰다 보니 땀 냄새가 뱀 12개 [m:std.odor.label.smell_after_use], 생선이나 유황 냄새 11개 [m:std.odor.label.fishy_sulfur_smell]

### 안전
- 안전 부정 리뷰 107개: 두통 16개(가중 0.2%), 메스꺼움 14개(가중 0.1%), 호흡 7개(가중 0.2%), 어지럼 3개(가중 0.0%), 피부 9개(가중 0.1%), 이상 반응 없음 58개 [m:p.safety_text]
- 안전 부정 라벨: 발암 경고나 발암 성분 22개, 두통이나 어지러움 20개, 몸에 해로운 성분 우려 17개, 구역질이나 몸이 안 좋아짐 15개, 숨 막힘이나 눈, 코, 목 자극 10개, 미끄러지거나 넘어져 다칠 위험 10개, 피부 발진이나 쓸림 8개 [m:p.safety_labels]
- **몸 반응**: 두통 16개 [m:p.safety.두통], 메스꺼움 14개 [m:p.safety.메스꺼움]이 앞서고, 인용한 리뷰어는 매트의 화학 냄새를 이유로 든다.
- **호흡과 피부**: 호흡 7개 [m:p.safety.호흡], 피부 9개 [m:p.safety.피부]이고, 피부 인용은 발진이나 쓸림을 말한다.
- **발암 경고**: 발암 경고나 발암 성분 22개 [m:std.safety.label.cancer_warning]는 몸 반응이 아니라 상품 경고문이나 성분 표기를 보고 걱정한 말이다.
- **상품별**: 안전 불만이 가장 적은 상품은 CAP 0.6% [m:std.safety.best]이고, 안전을 좋게 말한 리뷰는 0개 [m:std.safety.pos]다.

> "몇 분 만에 매트의 화학 냄새 때문에 두통이 생겼다" (Gaiam, 3★, R32UI56DRSVY4X)

> "1군 발암물질인 아크릴로니트릴에 노출된다고 알려 준다" (Retrospec, 3★, R2MSLDVHIAKISK)

## 04 포지셔닝
**TL;DR** 포지션은 찢어지거나 윗층이 벗겨지지 않고, 너무 얇지 않은 두께에 끈을 빠짐없이 넣은 집 바닥 운동용 요가 매트다. 근거는 불만 1위 만듦새와 내구성 8.9% [m:head.topic_neg](다시 뽑기에서 1위로 남은 비율 99.2% [m:a.robust.head_first])와 너무 얇음 쪽 라벨 148개 [m:head.dir_high]이고, 디자인과 크기 6.2% [m:p.map.design], 끈과 휴대 구성품 5.0% [m:p.map.carry_strap]이 뒤를 잇는다. 값은 시장 매출 비중이 가장 큰 첫 가격 구간 안에서 정하고, 내구, 두께, 마찰, 냄새 시험을 통과한 뒤에만 그 주장을 상세페이지에 쓰는 것을 확인이 필요한 권고로 둔다.

### 한 줄 포지션
찢어지거나 벗겨지지 않는 겉면, 무릎을 받쳐 주되 균형을 흐트리지 않는 두께 단계, 상자마다 빠짐없이 든 끈을 갖추고, 냄새와 성분 시험 결과를 상세페이지와 상자에 적는 요가 매트 브랜드

### 이기는 이유
- **내구성 불만이 가장 큰 자리**: 만듦새와 내구성 부정 8.9% [m:head.topic_neg]가 불만 1위이고, 상품 하나씩 빼 보면 결론이 바뀐 경우는 6번 중 1번 [m:a.robust.loo_flips]이다(Gaiam Dry-Grip 매트를 빼면 끈과 휴대 구성품이 1위). 찢김과 인장 시험을 통과한 내구성을 차별 요소로 검토한다(확인 필요).
- **한 상품에 몰린 내구성 약점**: 가장 큰 약점이 만듦새와 내구성인 상품은 6개 중 1개(리뷰를 다시 뽑아 보면 1~3개) [m:head.topic_weakest]이고, 그 상품인 Gaiam Dry-Grip 매트의 내구성 부정은 17.3% [m:s.B0BYFLL1LV.topic_neg]다. 상품이 적어 가격이나 재질이 원인이라고 읽지 않는다.
- **두께 불만의 방향**: 너무 얇음 쪽 라벨 148개 [m:head.dir_high]가 너무 두껍거나 푹신함 쪽 33개 [m:head.dir_low]보다 많다.
- **상품마다 다른 두께 방향**: 방향이 분명한 상품 넷 가운데 Gaiam Classic Print 매트(+1.00 [m:s.B01MY5MZSQ.dir_index]), Gaiam Premium Print 매트, Gaiam Dry-Grip 매트는 너무 얇음 쪽이고 Retrospec Solana 매트(-0.87 [m:s.B092XTMNCC.dir_index])는 너무 두껍거나 푹신함 쪽이며, 나머지 둘은 비어 있다.
- **두께 사양과 나란히 본 방향**: 확인된 사양은 Gaiam Classic Print 매트 4 mm [m:spec.B01MY5MZSQ.thickness], Retrospec Solana 매트 1” [m:spec.B092XTMNCC.thickness]이다(상품이 적어 사양과 불만을 원인으로 잇지 않음). 한 두께가 아니라 두 단계에서 고르게 하는 것을 차별 요소로 검토한다(확인 필요).
- **끈 빠짐**: 들어 있어야 할 끈이 빠져 옴 132개 [m:std.strap.label.strap_missing]가 끈 불만 라벨 가운데 가장 많다. Retrospec Solana 1인치 [r:ind_23]와 CAP High Density Exercise Yoga Mat with Strap [r:ind_25]도 끈을 넣는 상품이라, 끈을 넣는 것보다 출고 검사로 빠짐을 막는 것을 차별 요소로 검토한다(확인 필요).
- **냄새 안내와 시험**: Gaiam Premium 2-Color 6mm는 처음 냄새를 상세페이지에 미리 적고 [r:ind_05] 펴서 바람을 쐰 뒤 쓰라고 안내한다 [r:ind_04]. 화학, 플라스틱, 고무 냄새 135개 [m:std.odor.label.chemical_plastic_smell]가 냄새 라벨 가운데 가장 많아, 안내에 더해 VOC 방출 시험 [r:tst_09] 결과를 적는 것을 차별 요소로 검토한다(확인 필요).

### 소비자 기준표
#### 기준 1: 찢어짐과 내구성(원인 1, 2, 3, 4 대응)
- 감점 기준: 내구성 불만 가중 8.7% [m:std.durability.neg_pct], 그중 찢어짐이나 구멍 111개 [m:std.durability.label.tears_holes]가 가장 많다.
- 만족 기준: 내구성 만족 리뷰 235개 [m:std.durability.pos]의 오래 써도 찢어지거나 벗겨지지 않는 수준이고, 부정이 가장 적은 상품은 Gaiam 2.3% [m:std.durability.best](Gaiam Premium Print 매트)다.
- 개발 기준: 재질을 고른 뒤 찢김 강도는 ASTM D624 [r:tst_07], 인장 물성은 ASTM D412 [r:tst_08]로 재고(가황 고무와 TPE 대상), 폼 재질이면 고무 폼(NBR 등)은 ASTM D1056 [r:tst_03], EVA나 PE 폼은 ASTM D3575 [r:tst_02], PU 폼은 ASTM D3574 [r:tst_01]을 쓴다. 손상까지 쓴 기간 중앙값이 30days [m:f.durability.durability_elapsed_days.median]라 첫 달을 넘는 반복 사용 조건으로 윗층 분리를 확인한다(목표값과 반복 방법은 확인 필요).
- 상세페이지 문구: "Tear-resistant surface that won't peel or flake" (찢김에 강하고 벗겨지거나 부스러지지 않는 겉면), 찢김과 인장 시험 통과 뒤에만.

#### 기준 2: 두께와 쿠션(원인 6, 7, 8 대응)
- 감점 기준: 두께와 쿠션 불만 가중 5.8% [m:std.thickness.neg_pct], 그중 너무 얇음 111개 [m:std.thickness.label.too_thin]가 가장 많다.
- 만족 기준: 두께 만족 리뷰 664개 [m:std.thickness.pos]의 무릎을 받쳐 주는 수준이고, 부정이 가장 적은 상품은 Gaiam 2.9% [m:std.thickness.best](Gaiam Essentials Thick 매트, 공식 페이지 이름 기준)다.
- 개발 기준: 너무 얇음과 쿠션 부족(원인 6)은 설계 결함으로 보고 첫 상품은 얇은 쪽을 피한다. 너무 두껍거나 딱딱함(원인 8)은 선호 차이라 두께 단계를 둘로 나눠 고르게 한다(단계 값은 확인 필요). 경도는 ASTM D2240 [r:tst_06]로 재고, 고무 폼이면 두께 단계의 단단함을 압축 처짐 [r:tst_04]으로 비교한다. 눌린 뒤 복원(원인 7)은 시험 방법 확인 필요(조사 근거 없음).
- 상세페이지 문구: "Cushions knees on hard floors" (딱딱한 바닥에서 무릎을 받쳐 줌), 경도 시험 통과 뒤에만. 두께가 유지된다는 문구는 복원 시험 근거가 생길 때까지 쓰지 않는다.

#### 기준 3: 그립과 미끄럼(원인 11, 12 대응)
- 감점 기준: 그립 불만 가중 5.9% [m:std.grip.neg_pct], 그중 표면이 미끄러움 191개 [m:std.grip.label.surface_slippery]가 가장 많다.
- 만족 기준: 그립 만족 리뷰 315개 [m:std.grip.pos]의 땀이 나도 손발이 잡히고 바닥에서 밀리지 않는 수준이고, 부정이 가장 적은 상품은 CAP 1.6% [m:std.grip.best](CAP Extra Thick 매트)다.
- 개발 기준: 정지 마찰과 미끄럼 마찰 계수를 ASTM D1894 [r:tst_05]로 마른 겉면, 젖은 겉면, 바닥 쪽 면에서 각각 잰다(요가 매트 전용 시험은 아님). 핫요가를 말한 리뷰가 9.0% [m:f.grip.activity.hot_yoga.w]라 젖은 조건을 빼지 않고, 그립이 떨어짐(원인 12)은 반복 사용 뒤 다시 잰다(목표값은 확인 필요).
- 상세페이지 문구: "Grips even when you sweat, stays put on hardwood" (땀이 나도 잡히고 마루에서 밀리지 않음), 마른 조건과 젖은 조건 마찰 시험 통과 뒤에만.

#### 기준 4: 균형과 늘어남(원인 9, 10 대응)
- 감점 기준: 균형과 늘어남 불만 가중 2.2% [m:std.stability.neg_pct], 그중 매트가 늘어남 34개 [m:std.stability.label.mat_stretches]가 가장 많다.
- 만족 기준: 만족 리뷰는 20개 [m:std.stability.pos]뿐이라 선 자세에서 발밑이 흔들리거나 늘어나지 않는 수준을 기준으로 두고, 부정이 가장 적은 상품은 Gaiam 0.2% [m:std.stability.best](Gaiam Classic Print 매트)다.
- 개발 기준: 늘어남(원인 9)은 인장 물성 ASTM D412 [r:tst_08]로 확인한다. 두꺼워서 균형이 어려움(원인 10)은 선호 차이라 두께 단계마다 균형 자세에 맞는지 안내하고, 선 자세와 균형 자세를 말한 리뷰 2.2% [m:f.thickness.activity.standing_balance.w]를 시제품 청취 대상에 넣는다(목표값은 확인 필요).
- 상세페이지 문구: "Firm footing for balance poses, no stretching underfoot" (균형 자세에서 단단히 받쳐 주고 발밑에서 늘어나지 않음), 인장 시험 통과 뒤에만.

#### 기준 5: 냄새(원인 13, 14, 15 대응)
- 감점 기준: 냄새 불만 가중 7.8% [m:std.odor.neg_pct], 그중 화학, 플라스틱, 고무 냄새 135개 [m:std.odor.label.chemical_plastic_smell]가 가장 많다.
- 만족 기준: 냄새 만족 리뷰 65개 [m:std.odor.pos]의 꺼냈을 때부터 냄새가 적거나 금방 빠지는 수준이고, 부정이 가장 적은 상품은 CAP 2.6% [m:std.odor.best]다.
- 개발 기준: VOC 방출을 ASTM D5116 [r:tst_09]으로 재거나 UL GREENGUARD 인증 [r:tst_10]을 검토하고, 출하 검사에 냄새 항목 [r:tst_13]을 넣는다. 리뷰어가 말한 냄새 기간 중앙값이 14days [m:f.odor.odor_duration_days.median]라 출고 전 바람 쐬기 공정과 상자 안 안내를 함께 정한다(공정 기간은 확인 필요).
- 상세페이지 문구: "Low odor out of the box, VOC emissions tested" (꺼냈을 때부터 냄새가 적음, VOC 방출 시험), 방출 시험 통과 뒤에만.

#### 기준 6: 성분과 안전(03 원인 밖)
- 감점 기준: 안전 부정 리뷰 107개 [m:std.safety.neg]이고, 그중 발암 경고나 발암 성분 22개 [m:std.safety.label.cancer_warning]가 가장 많다.
- 만족 기준: 긍정 리뷰가 0개 [m:std.safety.pos]라 몸 반응과 성분 걱정 언급이 없는 수준을 기준으로 두고, 부정이 가장 적은 상품은 CAP 0.6% [m:std.safety.best]다.
- 개발 기준: 캘리포니아 Prop 65 목록 물질에 노출시키면 경고해야 하고 [r:reg_06] 온라인 판매는 상품 페이지 방식으로 경고를 낸다 [r:reg_09]. PVC 운동 매트의 DINP를 문제 삼은 통지가 있었으므로 [r:reg_10] PVC를 쓰면 가소제 성분을 시험으로 확인하고, 유해물질 시험은 OEKO-TEX STANDARD 100 [r:tst_11]을 검토한다. PFAS를 일부러 넣지 않았는지도 확인한다 [r:reg_19].
- 상세페이지 문구: "Third-party tested for harmful substances" (제3자 유해물질 시험 통과), 시험 통과 뒤에만. "non-toxic"은 과학 근거와 한정 문구 없이 쓰지 않는다 [r:reg_12].

#### 기준 7: 크기, 무게, 휴대(03 원인 밖)
- 감점 기준: 크기와 휴대 불만 가중 6.8% [m:std.size.neg_pct], 그중 말면 부피가 커서 휴대나 보관이 불편함 49개 [m:std.size.label.bulky_to_carry_store]가 가장 많다.
- 만족 기준: 크기 만족 리뷰 119개 [m:std.size.pos]의 몸에 맞는 길이와 너비에 잘 말리는 수준이고, 부정이 가장 적은 상품은 Gaiam 0.5% [m:std.size.best](Gaiam Classic Print 매트)다.
- 개발 기준: 너비가 좁음 34개 [m:std.size.label.too_narrow], 길이가 짧음 26개 [m:std.size.label.too_short]라 출시 뒤 길이 단계를 검토한다. Manduka PRO는 85인치 긴 판을 따로 두고 [r:ind_12], JadeYoga Harmony Mat는 두 길이로 판다 [r:ind_17](단계 값은 확인 필요).
- 상세페이지 문구: "Room to stretch out, rolls up compact" (몸을 뻗을 만큼 넉넉하고 작게 말림), 실측 크기와 무게를 함께 적을 때만.

#### 기준 8: 끈과 구성품(03 원인 밖)
- 감점 기준: 끈과 구성품 불만 가중 4.7% [m:std.strap.neg_pct], 그중 들어 있어야 할 끈이 빠져 옴 132개 [m:std.strap.label.strap_missing]가 가장 많다.
- 만족 기준: 끈 만족 리뷰 42개 [m:std.strap.pos]의 끈이 들어 있고 매트를 단단히 잡는 수준이고, 부정이 가장 적은 상품은 Gaiam 0.8% [m:std.strap.best](Gaiam Classic Print 매트)다.
- 개발 기준: Retrospec Solana 1인치 [r:ind_23]와 CAP High Density Exercise Yoga Mat with Strap [r:ind_25]처럼 끈을 넣는다면 출고 검사에 끈 동봉과 끈 탄력을 넣는다. 검사 방법은 확인 필요(조사 근거 없음).
- 상세페이지 문구: "Carry strap included in every box" (모든 상자에 들고 다니는 끈 포함), 출고 검사를 둔 뒤에만.

#### 기준 9: 묻어남과 표면 마감(원인 5 대응)
- 감점 기준: 묻어남 불만 가중 1.0% [m:std.residue.neg_pct], 그중 색이 몸이나 옷에 물듦 35개 [m:std.residue.label.dye_color_transfer]가 가장 많다.
- 만족 기준: 긍정 리뷰가 0개 [m:std.residue.pos]라 몸과 옷, 바닥에 색이나 가루가 남지 않는 수준을 기준으로 두고, 부정이 가장 적은 상품은 CAP 0.0% [m:std.residue.best]다.
- 개발 기준: 확인 필요(조사 근거 없음).
- 상세페이지 문구: "No color transfer to skin or clothes" (피부나 옷에 색이 묻지 않음), 이염 시험 통과 뒤에만.

#### 기준 10: 설명과 실물(03 원인 밖)
- 감점 기준: 설명과 실물 불만 가중 2.2% [m:std.listing.neg_pct], 그중 설명과 달리 끈이 없음 40개 [m:std.listing.label.strap_missing_vs_listing]가 가장 많다.
- 만족 기준: 설명대로 왔다는 리뷰 36개 [m:std.listing.pos]처럼 두께, 색, 구성이 상세와 같은 수준이고, 부정이 가장 적은 상품은 Gaiam 0.8% [m:std.listing.best](Gaiam Classic Print 매트)다.
- 개발 기준: 표기보다 얇음 39개 [m:std.listing.label.thinner_than_listed]가 있어 출하 검사 목록의 두께와 그립 확인 항목 [r:tst_13]으로 표기와 실물을 맞춘다. 원산지를 표시하고 [r:reg_16], 한정 없는 친환경 주장은 쓰지 않는다 [r:reg_11].
- 상세페이지 문구: "Thickness checked on every production batch" (생산 묶음마다 두께 확인), 출하 검사 기록이 있을 때만.

#### 기준 11: 가격 대비 가치(03 원인 밖)
- 감점 기준: 가치 불만 가중 2.0% [m:std.value.neg_pct], 그중 값어치를 못 함, 돈 낭비 42개 [m:std.value.label.not_worth_money]가 가장 많다.
- 만족 기준: 가치 만족 리뷰 141개 [m:std.value.pos]의 값에 비해 오래 쓴다는 수준이고, 부정이 가장 적은 상품은 Gaiam 0.3% [m:std.value.best](Gaiam Premium Print 매트)다.
- 개발 기준: 확인 필요(조사 근거 없음). 값은 아래 가격 구조의 권고 구간 안에서 정한다.
- 상세페이지 문구: "Built to last at an everyday price" (매일 쓰기 좋은 값에 오래 가도록 만듦), 내구 시험 통과 뒤에만.

### 하위 카테고리별 출시 계획
- **첫 출시, Yoga Mats 노드의 요가 매트**: 조사 상품이 모두 이 노드에 있고, 노드 월 매출 칸은 9,116,723(월 매출 칸, 통화 미확인) [m:head.market_month], 1위 Gaiam 17.7% [m:m.top1_share_YM]다. 너무 얇지 않은 두께 단계와 끈을 넣은 구성으로 낸다(확인 필요).
- **다음 출시, Exercise Mats 노드의 두꺼운 운동 매트**: 상위 10개 브랜드 점유율 합 56.9% [m:m.top10_share_EM], 1위 BalanceFrom 13.9% [m:m.top1_share_EM]이다. ProsourceFit Extra Thick Yoga and Pilates Mat [r:ind_24]와 끈이 함께 오는 BalanceFrom GoYoga+ [r:ind_29]가 있는 자리라, 첫 상품의 두께 단계 반응을 본 뒤 연다.
- **그 뒤, 여행용 얇은 매트**: Gaiam Foldable Yoga Mat(2mm) [r:ind_09], Manduka PRO Travel Yoga Mat 2mm [r:ind_13], JadeYoga Voyager Mat [r:ind_19]가 있다. 여행과 차에 싣고 다님을 말한 리뷰는 1.2% [m:f.durability.use_location.travel_car.w]이고 너무 얇음 불만이 많아 뒤로 미룬다(확인 필요).

### 가격 구조
- **읽는 법**: 묶음 값은 상품 한 개의 개당 가격이고, 묶음마다 상품이 적다(낮음 2개 [m:price.band0.n], 높음 2개 [m:price.band2.n]). 가격과 불만은 나란히만 읽고 가격이 불만을 만든다고 보지 않는다.
- **낮음 묶음**: 21.55~22.64달러/개 [m:price.band0.range], 두께와 쿠션 부정 8.9% [m:price.band0.skin_neg]로 세 묶음 가운데 가장 높다(Gaiam Classic Print 매트와 Gaiam Premium Print 매트).
- **낮음 묶음의 내구성과 별점**: 만듦새와 내구성 부정 2.8% [m:price.band0.eff_neg], 별점 4.60★ [m:price.band0.star]이다.
- **중간 묶음**: 22.67~24.46달러/개 [m:price.band1.range], 만듦새와 내구성 부정 7.7% [m:price.band1.eff_neg]이다(CAP Extra Thick 매트와 Gaiam Essentials Thick 매트).
- **중간 묶음의 두께와 별점**: 두께와 쿠션 부정 1.8% [m:price.band1.skin_neg]로 세 묶음 가운데 가장 낮고, 별점은 4.61★ [m:price.band1.star]이다.
- **높음 묶음**: 39.99~48.98달러/개 [m:price.band2.range], 만듦새와 내구성 부정 12.5% [m:price.band2.eff_neg]로 세 묶음 가운데 가장 높다(Retrospec Solana 매트와 Gaiam Dry-Grip 매트).
- **높음 묶음의 별점과 두께**: 별점 4.38★ [m:price.band2.star], 두께와 쿠션 부정 2.8% [m:price.band2.skin_neg]이다.
- **시장 가격대와 기준 차이**: 시장 가격대 표는 브랜드 평균 가격으로 나눈 구간이라 단품의 개당 가격과 기준이 다르다. 첫 구간 20.68~41.93 [m:m.price_band1_range]의 매출 비중이 56.1% [m:m.price_band1_share]로 가장 크다.
- **시장의 둘째와 셋째 구간**: 둘째 구간 매출 비중 20.3% [m:m.price_band2_share], 셋째 구간 23.6% [m:m.price_band3_share]이다.
- **권고 가격대**: 첫 상품은 시장 첫 구간 안에서, 조사 상품의 중간 묶음 22.67~24.46달러/개 [m:price.band1.range] 언저리를 출발점으로 원가와 시험 비용을 맞춰 정한다(확인 필요).

### 메시지와 키워드
- **썸네일**: "Tear-resistant, won't peel" (찢김에 강하고 벗겨지지 않음)와 "Strap included" (끈 포함) 두 줄, 찢김 시험 통과와 출고 검사를 둔 뒤에만.
- **상세**: 두께 단계별 경도 시험 결과 [r:tst_06], 마른 조건과 젖은 조건의 마찰 시험 조건 [r:tst_05], VOC 방출 시험 결과 [r:tst_09], 실측 길이와 너비와 무게, 상자 구성(끈)을 적는다. Prop 65 경고가 필요하면 상품 페이지 방식으로 낸다 [r:reg_09].
- **박스 안**: 펴서 바람을 쐰 뒤 쓰라는 안내(Gaiam Premium 2-Color 6mm도 같은 안내를 함 [r:ind_04]), 세척 방법, 두께 단계별로 맞는 운동 안내, 끈이 빠졌을 때 연락할 곳을 넣는다.
- **키워드**: yoga mat, thick yoga mat, yoga mat thick, yoga mat non slip, hot yoga mat, exercise mat, pilates mat.

### 실행 순서
1. **P1 재질과 두께 단계 시제품**: 두께 단계 둘을 만들고 경도 ASTM D2240 [r:tst_06]로, 고무 폼이면 압축 처짐 [r:tst_04]으로도 단단함을 비교한다(단계 값은 확인 필요). 눌린 뒤 복원은 시험 방법 확인 필요(조사 근거 없음).
2. **P1 찢김과 인장 시험**: ASTM D624 [r:tst_07]와 ASTM D412 [r:tst_08]로 찢어짐, 윗층 분리, 늘어남을 확인한다.
3. **P1 마찰 시험**: ASTM D1894 [r:tst_05]로 마른 겉면, 젖은 겉면, 바닥 쪽 면을 잰다.
4. **P1 냄새와 방출 시험**: ASTM D5116 [r:tst_09] 또는 UL GREENGUARD [r:tst_10]을 정하고 출고 전 바람 쐬기 공정을 둔다.
5. **P1 성분과 경고 판단**: Prop 65 경고 필요 여부 [r:reg_06], PVC를 쓸 때 DINP 확인 [r:reg_10], PFAS 미사용 확인 [r:reg_19], 유해물질 시험 [r:tst_11].
6. **P1 출고 검사**: 끈 동봉, 두께, 그립, 냄새를 출하 검사 목록 [r:tst_13]에 넣는다.
7. **P1 표시 문구 점검**: non-toxic [r:reg_13], 친환경 [r:reg_11], 원산지 [r:reg_16] 표기를 근거와 맞춘다.
8. **P2 길이와 너비 단계**: 첫 상품의 크기 불만을 본 뒤 긴 판을 검토한다(Manduka PRO는 85인치 긴 판을 따로 둔다 [r:ind_12]).
9. **P2 이염 시험**: 색이 묻는 불만에 대응하는 시험 방법을 찾는다(확인 필요(조사 근거 없음)).
10. **P2 두꺼운 운동 매트**: Exercise Mats 노드용 두꺼운 판을 첫 상품의 두께 반응을 본 뒤 낸다(확인 필요).

### 개발 단계와 관문
- **재질과 두께 관문**: 두께 단계마다 경도 [r:tst_06] 결과(고무 폼이면 압축 처짐 [r:tst_04]으로 단단함 비교)가 있어야 하고, 눌린 뒤 복원은 시험 방법 확인 필요(조사 근거 없음)다(리뷰어가 말한 두께 중앙값 12.7mm [m:f.thickness.thickness_mm.median], 목표값은 확인 필요).
- **내구 관문**: 찢김 [r:tst_07]과 인장 [r:tst_08] 시험을 통과하고, 반복 사용 뒤 윗층 분리와 부스러짐이 없어야 한다(손상까지 쓴 기간 중앙값 30days [m:f.durability.durability_elapsed_days.median]).
- **그립 관문**: 마른 조건과 젖은 조건의 마찰 계수 [r:tst_05]를 재고, 반복 사용 뒤에도 다시 잰다(목표값은 확인 필요).
- **냄새와 성분 관문**: VOC 방출 시험 [r:tst_09], 유해물질 시험 [r:tst_11]을 통과하고, Prop 65 경고 [r:reg_06]와 PFAS 규정 [r:reg_20]을 확인한다.
- **출고 관문**: 출하 검사 목록 [r:tst_13]에 끈 동봉과 두께 표기 확인을 넣고 생산 묶음마다 기록한다.
- **표시 관문**: non-toxic 같은 주장은 한정 문구와 과학 근거가 있을 때만 쓰고 [r:reg_12], 원산지를 표시한다 [r:reg_16].

### 결론
- **무엇을**: 찢어지거나 벗겨지지 않고 너무 얇지 않은 두께 단계에 끈을 빠짐없이 넣은 요가 매트(불만 1위 만듦새와 내구성 8.9% [m:head.topic_neg]).
- **누구에게**: 집 안 딱딱한 바닥에서 바닥 운동, 스트레칭, 요가를 하는 사람(바닥 운동을 말한 리뷰 8.5% [m:f.thickness.activity.floor_fitness.w]).
- **얼마에**: 시장 매출 비중이 가장 큰 첫 가격 구간(56.1% [m:m.price_band1_share]) 안에서, 정확한 값은 원가와 시험 비용을 본 뒤 정한다(확인 필요).
- **무엇으로 이기는지**: 내구, 두께, 마찰, 냄새 시험 결과를 상세페이지에 적고 출고 검사로 끈 빠짐을 막는 것(끈이 빠져 옴 132개 [m:std.strap.label.strap_missing]).

## 05 한 장 요약
### 제품 해부도
1. **윗면 질감과 그립**: 마른 조건과 젖은 조건에서 모두 손발이 잡히는 질감, 마찰 계수는 ASTM D1894 [r:tst_05]로 잰다 (표면이 미끄러움 191개 [m:std.grip.label.surface_slippery], 핫요가를 말한 리뷰 9.0% [m:f.grip.activity.hot_yoga.w])
2. **윗층과 몸판 접착**: 반복 사용 뒤에도 벗겨지거나 부스러지지 않는 겉층, 찢김 ASTM D624 [r:tst_07]와 인장 ASTM D412 [r:tst_08]로 확인 (윗층 분리나 기포 77개 [m:std.durability.label.top_layer_peels], 찢어짐이나 구멍 111개 [m:std.durability.label.tears_holes])
3. **몸판 두께와 탄성**: 너무 얇지 않은 두께 단계 둘, 경도 ASTM D2240 [r:tst_06](고무 폼이면 압축 처짐 [r:tst_04]으로 단단함 비교), 늘어남은 인장 시험 [r:tst_08]으로 확인, 눌린 뒤 복원은 시험 방법 확인 필요(조사 근거 없음) (너무 얇음 111개 [m:std.thickness.label.too_thin], 매트가 늘어남 34개 [m:std.stability.label.mat_stretches])
4. **뒷면 바닥 접지**: 마루와 딱딱한 바닥에서 밀리지 않는 뒷면, 바닥 쪽 면의 마찰을 따로 잰다 [r:tst_05] (바닥에서 매트가 밀림 62개 [m:std.grip.label.slides_on_floor], 마루, 강화마루, 나무 바닥 39개 [m:f.grip.use_location.wood_floor])
5. **재질 성분과 냄새**: VOC 방출 ASTM D5116 [r:tst_09]과 출고 전 바람 쐬기 공정, PVC를 쓰면 DINP 확인 [r:reg_10] (화학, 플라스틱, 고무 냄새 135개 [m:std.odor.label.chemical_plastic_smell], 바람 쐬고 씻어도 안 빠짐 57개 [m:std.odor.label.smell_persists])
6. **겉면 색과 마감**: 몸과 옷, 바닥에 색이나 가루가 남지 않는 마감, 이염 시험 방법은 확인 필요(조사 근거 없음) (색이 몸이나 옷에 물듦 35개 [m:std.residue.label.dye_color_transfer], 겉면이 끈적이거나 녹아 붙음 24개 [m:f.durability.damage_type.sticky_melted])
7. **길이와 너비**: 첫 상품은 한 크기로 내고 실측 크기와 무게를 적는다. 길이 단계는 출시 뒤 검토하고, Manduka PRO는 85인치 긴 판을 따로 둔다 [r:ind_12] (너비가 좁음 34개 [m:std.size.label.too_narrow], 길이가 짧음 26개 [m:std.size.label.too_short])
8. **끈과 구성품**: 상자마다 끈을 넣고 출하 검사 목록 [r:tst_13]으로 동봉과 끈 탄력을 확인 (들어 있어야 할 끈이 빠져 옴 132개 [m:std.strap.label.strap_missing], 끈이 늘어나거나 헐거워 매트가 빠짐 27개 [m:std.strap.label.strap_loose_slips])

### 단계와 관문
- **재질과 두께**: P1 한 건(재질과 두께 단계 시제품), 관문은 두께 단계마다 경도 [r:tst_06] 결과(고무 폼이면 압축 처짐 [r:tst_04]으로 단단함 비교), 눌린 뒤 복원은 시험 방법 확인 필요(조사 근거 없음) (너무 얇음 쪽 라벨 148개 [m:head.dir_high])
- **내구**: P1 한 건(찢김과 인장 시험), 관문은 찢김 [r:tst_07]과 인장 [r:tst_08] 통과, 반복 사용 뒤 윗층 분리와 부스러짐 없음 (손상까지 쓴 기간 중앙값 30days [m:f.durability.durability_elapsed_days.median])
- **그립**: P1 한 건(마찰 시험), 관문은 마른 겉면, 젖은 겉면, 바닥 쪽 면의 마찰 계수 [r:tst_05]와 반복 사용 뒤 재측정, 목표값은 확인 필요 (쓰다 보니 그립이 떨어짐 28개 [m:std.grip.label.grip_wears_off])
- **냄새와 성분**: P1 두 건(냄새와 방출 시험, 성분과 경고 판단), 관문은 VOC 방출 시험 [r:tst_09], 유해물질 시험 [r:tst_11], Prop 65 경고 판단 [r:reg_06]과 PFAS 확인 [r:reg_19] (안전 부정 리뷰 107개 [m:std.safety.neg])
- **출고와 표시**: P1 두 건(출고 검사, 표시 문구 점검), 관문은 출하 검사 목록 [r:tst_13]에 끈 동봉과 두께 확인을 넣고, non-toxic 같은 주장은 한정 문구와 근거가 있을 때만 쓴다 [r:reg_12] (설명과 달리 끈이 없음 40개 [m:std.listing.label.strap_missing_vs_listing])
- **출시 뒤**: P2 세 건(길이와 너비 단계, 이염 시험, 두꺼운 운동 매트), 관문은 첫 상품의 크기와 두께 반응을 본 뒤 정한다(확인 필요) (너무 두껍거나 푹신함 33개 [m:std.thickness.label.too_thick_soft])

## A 데이터와 방법
### 출처
- 리뷰, 태그, 세부 이슈 라벨, 설계 정보, 시장 데이터(spd-amz-market), 웹 조사, 상품 사양의 파일과 건수는 아래 표에 있다.
- 웹 조사 주장은 78개 중 64개 [m:a.research_verified]를 다시 열어 원문 문장을 확인했고, 확인된 주장만 썼다. 확인되지 않은 주장(CDC 미국 성인 요가 참여율, CPSC 어린이 제품의 프탈레이트와 납 규정, FTC Made in USA 기준, Gaiam 공식몰 가격, JadeYoga Harmony 길이별 가격, Liforme 여행용 가격)은 쓰지 않았다.
- 미국만의 요가 매트 시장 금액과 요가 매트 전용 시험 표준은 웹 조사에서 찾지 못했다.
- 상품 사양은 공식 사이트(gaiam.com, retrospec.com, capbarbell.com)와 소매점 페이지(ayurveda101.com, yeswellness.com, zappos.com)를 다시 열어 확인한 값만 썼다. Gaiam Essentials Thick은 이름만 일치 [m:spec.B07H9PZDQW.match], Gaiam Dry-Grip은 찾지 못함 [m:spec.B0BYFLL1LV.match]이다.
- 정답 세트 기준 sonnet 태깅은 주제 F1 0.88 [m:acc.topic_f1], 감성 방향 일치 98.6% [m:acc.direction]이다.
- mixed 일치는 47.1% [m:acc.mixed], 감성 전체 일치는 89.0% [m:acc.sentiment]이고, mixed 일치는 기준 없이 적는다.
- 설계 정보 추출 감사는 표본 150개 중 FAIL 3개(2.0%) [m:a.detail_audit]다.

### 견고성 점검
- 리뷰를 2,000번 [m:a.robust.n] 다시 뽑으면 만듦새와 내구성이 불만 1위로 남은 비율은 99.2% [m:a.robust.head_first]다.
- 만듦새와 내구성 부정 언급 리뷰어 비율(머리 숫자)의 다시 뽑기 구간은 7.7%~10.2% [m:a.robust.head_neg_ci]이다.
- 가장 큰 약점이 만듦새와 내구성인 상품 수는 6개 중 1개(리뷰를 다시 뽑아 보면 1~3개) [m:a.robust.weakest]이고, 다시 뽑기 분포는 0개 0.2%, 1개 28.9%, 2개 44.6%, 3개 23.1%, 4개 3.1% [m:a.robust.weakest_dist]라 Gaiam Dry-Grip 한 상품의 일로 단정하지 않는다.
- 상품 하나씩 빼기에서 결론이 달라진 경우는 6번 중 1번 [m:a.robust.loo_flips]이다. Gaiam Dry-Grip을 빼면 불만 1위가 끈과 휴대 구성품으로 바뀌고 만듦새와 내구성 비율은 6.0% [m:a.robust.B0BYFLL1LV.head_neg]이 된다.
- 상품 하나씩 뺀 만듦새와 내구성 비율의 범위는 6.0%~9.8% [m:a.robust.loo_head_neg]이고, Gaiam Essentials Thick이나 Retrospec Solana를 빼면 불만 지도 상위 3개 순서만 바뀐다.
- 너무 두껍거나 푹신함 쪽 비율은 상품 하나씩 빼면 2.3%~28.4% [m:a.robust.loo_low_share]로 움직이고, Retrospec Solana를 빼면 2.3% [m:a.robust.B092XTMNCC.low_share]라 두꺼운 쪽 불만은 이 상품 리뷰에 몰려 있다.

### 주의 사항
- 리뷰는 공유 리뷰 DB 표본이라 낮은 별점이 실제보다 많고, 비율은 별점 묶음 가중으로 되돌렸다(표본 평균과 가중 평균 별점은 원문 목록).
- 자유 서술에서 뽑은 수치(손상까지 걸린 날, 리뷰어가 말한 두께, 냄새가 간 날)는 리뷰어가 적은 값이라 측정값이 아니고 방향과 분포로만 읽는다.
- 개발 기준의 사양 숫자는 웹 조사 출처를 근거로 한 시작점이고 시험으로 확인해야 한다.
- 상품이 적고 모두 한 하위 카테고리(Yoga Mats)라 상품끼리, 하위 카테고리끼리의 비교가 약하다. 가격 묶음도 묶음마다 상품이 적어 가격과 불만을 나란히만 읽는다.
- 시장 데이터(spd-amz-market)의 매출, 증감, 승률 칸은 문서에 단위가 없어 단위 미확인으로 적었고, 브랜드 점유율은 응답 값으로 매출 점유율임을 확인했다.
- 연 환산 시장 값 109,400,681(가정: 통화 미확인 월 매출 x 12, 계절 변동 미반영) [m:head.market_year]은 통화 미확인 월 매출 칸을 늘린 가정이라 머리 숫자나 SAM 확정 값으로 쓰지 않는다.
- 시장 가격대 표는 브랜드 평균 가격으로 나눈 구간이라 상품 한 개 가격과 기준이 다르다.
- 세계 시장 규모는 보고서마다 값이 크게 다르다(IMARC [r:mkt_01], The Insight Partners [r:mkt_06]).
- 상품은 카테고리 검색어의 매출 상위 후보 가운데 DB 리뷰 수 순으로 골라 상품 확인 관문에서 사람이 확인했고, 리뷰가 모자란 상품은 담당자 승인 상한 안에서 유료 수집한 리뷰를 더했다.
- 성장 배수 검색어는 기준 검색량 이상 검색어 121개 [m:m.growth_candidates] 가운데 두 기간 주간 이력이 있는 28개 [m:m.growth_ranked]에서만 골랐고, 이력이 없는 검색어는 견주지 못했다.
- 성장 배수의 비교 기간은 2026-09-13 ~ 2026-10-04(1년 전 2025-09-14 ~ 2025-10-05) [m:head.growth_weeks]이라 한 해의 같은 시기만 견준 값이다. 시장 데이터의 yoYChangePct 칸은 뜻과 단위가 확인되지 않아 쓰지 않는다.
- 방향 지수는 방향 라벨 리뷰가 기준보다 적은 상품에서 비워 두었고, 상품을 합친 값과 상품별 값의 방향이 다를 수 있다.
- 03장 원인 번호는 불만의 분류이지 인과가 아니고, 별점 격차도 함께 나온 값일 뿐 원인을 뜻하지 않는다.
