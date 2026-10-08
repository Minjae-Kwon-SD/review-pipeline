# 세부 이슈 목록 초안

상태: PASS. 주제마다 issue-labeler가 표본 인용(주제와 방향마다 최대 150개, ASIN과 별점 묶음을 고르게)을 읽고 제안한 목록입니다. 어림 개수는 표본에서 센 값이라 리포트에 쓰지 않습니다. 전체 만족도는 리뷰 단위 총평이라 나누지 않습니다.

## 가격 대비 가치 (price_value)

### 부정 이슈(부정, 혼합 인용): 인용 125개, 표본 125개

| id | 이름 | 영어 이름 | 포함 | 제외 | 대표 인용 | 어림 개수 |
|---|---|---|---|---|---|---|
| not_worth_money | 돈 낭비, 값어치 없음 | Waste of money | 돈 낭비다, 돈을 버렸다, 돈 아껴라, 값어치가 없다, 돈값을 못 한다는 판정만 있고 인용 안에 이유(효과, 고장)가 없는 말 | 인용 안에 효과가 없다는 이유가 붙으면 disappointing_for_price, 고장이나 짧은 수명이 붙으면 expensive_for_lifespan, 가격이 높다는 말만 있으면 too_expensive | "Waste of money." (R1WTL5624OGXU); "Not worth the money" (RI2SISRQKM0M2) | 59 |
| disappointing_for_price | 가격에 비해 효과나 성능이 실망스러움 | Disappointing results for the price | 가격을 들며 효과, 결과, 성능이 기대에 못 미친다, 이 값이면 더 나아야 한다, 이만큼 썼는데 실망이다는 말(효과가 없어 돈을 버렸다 포함) | 가격에 비해 빨리 고장 나거나 수명이 짧다는 말은 expensive_for_lifespan, 이유 없는 돈 낭비 판정은 not_worth_money | "For the price.. and zero results." (R18UY4HW9LQGON); "Given the price of this device, it was disappointing." (R28HE7BFJAEMNS) | 28 |
| expensive_for_lifespan | 비싼 값에 비해 빨리 고장 남 | Too costly for its short lifespan | 이 가격이면 더 오래 가야 한다, 몇 주나 몇 달 만에 고장 났다, 몇 번 못 쓰고 멈췄다처럼 가격과 고장, 내구성, 수명을 함께 말하는 것 | 가격과 함께 효과가 없다는 말은 disappointing_for_price, 가격 없이 고장만 말하는 것은 이 주제가 아님(quality) | "I would think for $350 this product would last longer than 4" (RTZ6KQ6T15U3J); "Way too expensive for its useful life" (R2JM1I6ZLDWZ00) | 17 |
| too_expensive | 가격 자체가 비쌈 | Too expensive | 비싸다, 너무 비싸다, 가격이 과하다, 다른 제품보다 몇 배 비싸다처럼 가격 수준 자체를 말하는 것(할인 없이는 실망했을 것이라는 말 포함) | 비싼데 효과가 없다는 말은 disappointing_for_price, 비싼데 고장 났다는 말은 expensive_for_lifespan, 비싸지만 값어치가 있다는 말은 positive 방향 | "Too expensive." (R1F3PPA88YT8QQ); "Very expensive and found others at less than 1/2 the price" (R1BW5S0JJO319S) | 14 |
| other | 기타 | Other | 위 라벨에 들지 않는 것 | - | - | 7 |

메모: 기타는 산 뒤 가격 인하 2, 교체 헤드나 충전기 추가 비용 2, 그 돈으로 면도기나 전기 제모, 전문 시술을 했어야 한다 3. "waste of time and money"의 시간 부분은 이 주제 밖. R2OEZ28614WRBE는 성능과 내구성을 함께 말해 disappointing_for_price와 expensive_for_lifespan 둘 다 될 수 있음

### 긍정 이슈(긍정, 혼합 인용): 인용 111개, 표본 111개

| id | 이름 | 영어 이름 | 포함 | 제외 | 대표 인용 | 어림 개수 |
|---|---|---|---|---|---|---|
| worth_the_money | 값어치가 있음 | Worth the money | worth it, worth every penny, 좋은 투자다, vale la pena처럼 쓴 돈만큼 값어치가 있다는 판정(비싸지만 값어치가 있다 포함) | 가격이 싸다, 가성비가 좋다, 할인으로 샀다는 말은 good_price, 살롱이나 전문 시술과 비교하면 saves_vs_salon | "Worth every penny!!" (R13MHEVNHMPLOI); "Yes, it’s on the expensive side, but for me it’s been comple" (R2WQNV39LKPB5G) | 45 |
| saves_vs_salon | 살롱이나 전문 레이저 시술보다 쌈 | Cheaper than salon treatments | 살롱, 클리닉, 전문 레이저 시술, estéticas에 드는 돈과 비교해 싸다, 돈을 아낀다(면도기와 함께 비교해도 여기) | 살롱 비교 없이 돈을 아낀다는 말은 saves_money_overall, 살롱에 안 가도 되는 편리함만 말하면 이 주제가 아님(ease_of_use) | "the cost is a lot lower compare to the salon" (R3V0MABRCY0HJC); "Definitely more cost effective them salon treatments" (R2KLY3J5B81QZS) | 28 |
| saves_money_overall | 길게 보면 돈을 아낌 | Saves money over time | 살롱 언급 없이 돈을 아낀다, 길게 보면 절약이다, 면도기나 면도 크림 같은 용품을 안 사도 된다 | 살롱이나 전문 시술과 비교하면 saves_vs_salon, 시간을 아낀다는 부분은 이 주제가 아님(treatment_time) | "it saves both time and money on razors and shaving cream" (R3GMJKYQ9OQT80); "save a lot of money in the long run" (R2WJT0O7RZ6EXV) | 13 |
| good_price | 가격이 착하고 가성비가 좋음 | Good value for the price | 저렴하다, affordable, 가격에 비해 좋다(for the price), great value, bang for your buck, 할인이나 프라임데이에 잘 샀다 | 가격 수준 언급 없이 값어치가 있다는 판정(worth it, 투자)은 worth_the_money, 살롱보다 싸다는 비교는 saves_vs_salon | "Great value for the price!" (R35JKDWHP2PZZ7); "Got on prime day, and what a deal" (R2VNEBLNFNGTZ1) | 24 |
| other | 기타 | Other | 위 라벨에 들지 않는 것 | - | - | 1 |

메모: worth_the_money와 good_price의 경계는 표현으로 가름(worth, investment는 값어치, value, affordable, for the price, deal은 가성비). 기타 1개는 R2527CST84MMJT(비용이 문제가 아니면 기능이 좋다는 혼합 인용)

## 브랜드 경험 (brand_experience)

### 부정 이슈(부정, 혼합 인용): 인용 64개, 표본 64개

| id | 이름 | 영어 이름 | 포함 | 제외 | 대표 인용 | 어림 개수 |
|---|---|---|---|---|---|---|
| not_recommend | 비추천이나 사지 말라는 경고 | Does not recommend or warns not to buy | 추천하지 않는다, 사지 마라, 돈 낭비하지 마라, Buyer beware처럼 다른 사람에게 이 제품을 권하지 않거나 사지 말라고 하는 말(이유가 같이 붙어도 포함) | 자기가 다시 사지 않겠다는 말만 있으면 no_repurchase, 대신 다른 브랜드나 제품을 사라는 말은 switch_brand, 대신 전문 시술을 받으라는 말은 go_professional | "I can not in good faith recommend this product to anyone" (R3FLHL10LKK79F); "Save your money, don't buy." (R1JUHDD7LBTKAK) | 37 |
| no_repurchase | 다시 사지 않음 | Would not buy again | 자기가 이 제품이나 모델을 다시 사지 않겠다, 같은 돈을 다시 쓰지 않겠다, 다시 사기 망설여진다는 말 | 다른 사람에게 사지 말라고 하면 not_recommend, 브랜드 전체를 다시 안 사겠다거나 회사에 실망했다는 말은 brand_disappointment | "I probably won’t rebuy this model when I run out of flashes" (R1NZEC16D5FOP4); "Will not buy again." (R20SYP9R1KMKDR) | 7 |
| switch_brand | 다른 브랜드나 제품이 나음 | Another brand or product is better | 다른 브랜드(Ulike, INIA, Braun 등)나 다른 제품을 사라, 그쪽을 살 걸 그랬다, 이전에 쓴 다른 브랜드가 더 나았다, 경쟁 제품과 비슷한 수준이라는 비교 | 대신 전문 시술이나 살롱을 권하면 go_professional, 대안 없이 사지 말라는 말만 있으면 not_recommend | "Get Ulike instead for better comfort." (RH6TJCI4IIG0W); "Go with a different brand." (R3R5LESPOYWCJZ) | 7 |
| go_professional | 전문 시술을 권함 | Recommends professional treatment instead | 집에서 쓰는 기기보다 전문 레이저나 살롱 시술을 받으라, 전문 시술만큼 세지 않다, 집에서 스스로 하는 시술을 권하지 않는다는 말 | 다른 가정용 브랜드나 제품을 권하면 switch_brand, 살롱 비용과의 돈 비교는 price_value(이 주제가 아님) | "I would recommend just going to a professional" (RR06PKULANNQ7); "don’t buy, go a professional places" (R3EGHJ3KA8QM68) | 5 |
| brand_disappointment | 브랜드나 광고에 실망 | Disappointed in the brand or its marketing | 브랜드 제품 전체를 사지 마라, 그 브랜드에서 사는 것은 이번이 마지막, 회사가 부끄럽다, 광고나 인플루언서에 끌려 샀다는 브랜드 자체에 대한 불만 | 이 모델 하나를 다시 안 사겠다는 말은 no_repurchase, 광고 내용과 실물이 다르다는 말은 trust(이 주제가 아님) | "Don’t buy ulike products." (R2W6NAVMEMCRIR); "I have purchased several items from Braun in the past but sa" (R26RQQHSAX8XYF) | 4 |
| other | 기타 | Other | 위 라벨에 들지 않는 것 | - | - | 4 |

메모: 추천을 미루거나 망설이는 말(R2ZKCTG5R8L6PV, R27D9PZ4ENRQ81, R2MBCDJ6VJPRMQ, 어림 3개)은 5% 미만이라 기타로 두었다. "don't buy, go a professional places"처럼 비추천과 대안이 한 문장이면 대안 라벨을 우선하고, 라벨 단계에서 1~2개를 함께 달 수 있다.

### 긍정 이슈(긍정, 혼합 인용): 인용 118개, 표본 118개

| id | 이름 | 영어 이름 | 포함 | 제외 | 대표 인용 | 어림 개수 |
|---|---|---|---|---|---|---|
| recommend | 추천이나 사라는 권유 | Recommends or urges others to buy | 추천한다, 강력 추천, Lo recomiendo, Just buy it, Get it, 주변에 이미 추천했다, 모두에게 필요하다처럼 조건 없이 다른 사람에게 권하는 말 | 피부 유형, 꾸준함, 기대치 같은 조건을 붙인 추천은 conditional_recommend, 후회하지 않을 것이다는 no_regret, 다시 사겠다는 buy_again_or_upgrade | "I highly recommend it" (R15CPIXT574AA3); "do yourself a favour and buy it" (R3CVPCV0EQPFAQ) | 73 |
| buy_again_or_upgrade | 재구매나 상위 모델로 바꿈 | Would buy again or upgraded | 다시 사겠다, 두 번째로 샀다, 가족 몫으로 하나 더 사겠다, 같은 브랜드 상위 모델로 바꿨다 | 산 뒤 오래 계속 쓴다는 말은 keeps_using, 이전 모델보다 낫다는 비교만 있으면 favorable_comparison | "I had the U3 and it solved 70% of my problem, so I decided t" (R3F4KBJINTRL7F); "I would defiantly buy it again." (R1MIIGBSIUFT00) | 9 |
| no_regret | 후회 없는 구매 | No regrets about buying | 후회하지 않는다, 후회하지 않을 것이다, 돈 쓴 것이 아깝지 않다, 최고의 구매 중 하나라는 말 | 직접 사라고 권하는 말은 recommend, 다시 사겠다는 말은 buy_again_or_upgrade, 가격 대비 값어치 평가는 price_value(이 주제가 아님) | "I do not regret this purchase!" (R7IHM2Z8MJOFL); "no te vas arrepentir" (R22D42ASN75CAQ) | 8 |
| keeps_using | 오래 계속 씀 | Keeps using it long term | 몇 달, 1년, 3년째 쓰고 있다, 앞으로도 계속 쓸 것이다, 그만 쓸 수 없다, 써 보고 돌아보지 않았다는 말 | 오래 써도 고장이 없다는 내구성 평가는 quality(이 주제가 아님), 다시 샀다는 말은 buy_again_or_upgrade | "I’ve used it on and off for 3 years" (R2LZPF2047BAEK); "Impossible to stop using it." (R2TNKBB9DW6MXY) | 8 |
| favorable_comparison | 이전 기기나 다른 브랜드보다 만족 | Better than previous devices or other brands | 이전 모델이나 예전에 쓴 다른 브랜드, 무명 기기보다 낫다, 시장의 다른 제품보다 이것을 권한다, 경쟁 브랜드에 견줄 만하다, 같은 브랜드 이전 제품도 좋았다 | 그 기기로 상위 모델을 다시 샀다는 말은 buy_again_or_upgrade, 브랜드 이름만 믿을 만하다는 말은 기타 | "So much better compared to my old no-brand laser hair remove" (R13FFPKEUHQJ4V); "I’ve used Ulike products before and had a great experience" (R27C7U0ZYUMOEM) | 8 |
| conditional_recommend | 조건을 붙인 추천 | Recommends with conditions | 꾸준히 할 각오가 있으면, 밝은 피부라면, 일주일에 한 번 면도해도 괜찮다면, 전문 시술만큼 세지 않다는 것을 알면 추천한다처럼 조건을 걸고 권하는 말 | 조건 없는 추천은 recommend, 조건 때문에 결국 전문 시술을 받으라는 불만 부분은 부정 방향 go_professional | "I definitely recommend getting the product as long as you ar" (R3I65RNL68LQ79); "Recomendable si eres cumplido con los días de depilación" (RXBX1IOM03910) | 7 |
| other | 기타 | Other | 위 라벨에 들지 않는 것 | - | - | 5 |

메모: 브랜드 이름 자체에 대한 신뢰(R2YRR62H3ARYRY "A Trusted Brand", R2527CST84MMJT Philips, R32K12744AFVIO "German engineering", 어림 3개)는 5% 미만이라 기타로 두었다. R33AU9CUYNIANU의 칭찬 부분("happy for the most part")은 이유 없는 전체 평에 가까워 기타로 셌다.

## 신뢰 (trust)

### 부정 이슈(부정, 혼합 인용): 인용 40개, 표본 40개

| id | 이름 | 영어 이름 | 포함 | 제외 | 대표 인용 | 어림 개수 |
|---|---|---|---|---|---|---|
| misleading_claims | 과장 광고나 거짓 설명 | Misleading or false claims | 광고, 설명, 사진이 실제와 다르다, 과장이다, 오해하게 만든다, 거짓이다, 사기다라는 말(효과, 시간, 출력, 안전 주장 포함) | 피부색이나 털 색에 맞는다는 안내가 틀렸거나 없었다는 말은 suitability_misinformed, 설명에 적힌 구성품이 빠진 것은 missing_listed_items | "“full body in 10 mins” advertising is also misleading" (R253Q5MQJEFCR1); "Product is advertised as safe but this is the opposite!" (R1Q2O18BTENX2M) | 14 |
| arrived_used | 중고나 개봉 흔적 | Arrived used or opened | 새 제품으로 샀는데 쓴 흔적, 남의 털, 더러운 헤드, 열린 상자로 왔다, 반품된 것을 다시 판다는 말 | 설명에 적힌 구성품이 빠진 것만 말하면 missing_listed_items, 기기 고장이나 불량 자체는 quality(주제 밖) | "Arrived used" (R1B2B516LQUZCQ); "llego la caja abierta y se ve usado y los cabezales sucios" (R374GN9CX6ILYP) | 12 |
| missing_listed_items | 설명과 다른 구성품 | Listed items missing | 설명이나 설명서에 들어 있다고 한 헤드, 면도기, 보안경, 수건이 받은 상자에 없었다는 말 | 원래 구성에 없는 것을 아쉬워하는 말은 accessories(주제 밖), 중고 흔적과 함께 말하면 중고 흔적을 arrived_used로 | "The description says it comes with 2 heads and a razor but I" (R1EGVNMV7X8WQX); "El manual indica que incluye razor y goggles, pero no vinier" (RZH0ENS9J3SL) | 5 |
| suitability_misinformed | 피부색 적합성 안내 부족이나 잘못된 안내 | Skin tone suitability not disclosed or misstated | 어두운 피부에는 안 된다는 것을 알리지 않았다, 포장이나 협찬 홍보가 맞는다고 했는데 아니었다는 말 | 피부색 때문에 효과가 없거나 센서가 막는다는 경험 자체는 skin_hair_suitability(주제 밖), 피부색과 관계없는 과장 광고는 misleading_claims | "they never said it’s not for Black people or dark colored pe" (RL4CIP8VWPLYA); "You should make it clear that it is not for brown skin girls" (R3DXQ4VVNARZ78) | 4 |
| doubted_before_purchase | 협찬 리뷰나 반품 표시로 생긴 의심 | Doubt from paid reviews or return warnings | 반품이 잦은 상품 표시, 협찬과 유료 홍보, 평판 때문에 사기 전이나 쓰면서 의심했다는 말(혼합 인용의 의심 부분 포함) | 광고 내용이 실제와 다르다고 판단한 말은 misleading_claims | "It says this is a frequently returned item so I was hesitant" (R2KLY3J5B81QZS); "I think there is a lot of paid promotion with this product." (RKEMYTS0L15RN) | 3 |
| other | 기타 | Other | 위 라벨에 들지 않는 것 | - | - | 2 |

메모: R2LT3QNM94WMEI(사기라는 말이지만 이유가 배송 안 됨, shipping 쪽)와 R1LCIDY8581R4J(설명에 무엇이 없었는지 인용만으로 알 수 없음)는 기타로 셈. 안전하다는 광고가 거짓이라는 말(어림 2개)은 따로 두기엔 적어 misleading_claims에 합침.

### 긍정 이슈(긍정, 혼합 인용): 인용 8개, 표본 0개

인용이 20개 미만이거나 라벨이 없어 기타만 둡니다.

## 배송 (shipping)

### 부정 이슈(부정, 혼합 인용): 인용 4개, 표본 0개

인용이 20개 미만이거나 라벨이 없어 기타만 둡니다.

### 긍정 이슈(긍정, 혼합 인용): 인용 15개, 표본 0개

인용이 20개 미만이거나 라벨이 없어 기타만 둡니다.

## 고객 응대 (customer_service)

### 부정 이슈(부정, 혼합 인용): 인용 52개, 표본 52개

| id | 이름 | 영어 이름 | 포함 | 제외 | 대표 인용 | 어림 개수 |
|---|---|---|---|---|---|---|
| missed_return_window | 반품 기한이 지나 반품이나 환불 불가 | Past the return window | 반품 기한이나 환불 보장 기간(30일, 100일 등)이 지나 반품, 환불을 못 한다, 기한을 놓쳐 떠안았다는 말 | 효과가 나오기 전에 기한이 끝난다고 기한과 효과 시점을 비교하면 window_ends_before_results. 기한 안인데 거절당하면 refund_replace_refused | "I missed the window to return it so now I’m stuck with it." (R3SYQQVFXZOBU4); "Outside of the 100 day guarantee so I cannot get a refund." (R2UV6FE2VGLK51) | 17 |
| window_ends_before_results | 효과 확인 전에 반품 기한이 끝남 | Return window ends before results show | 효과를 알기까지 걸리는 기간보다 반품 기한이 짧아 판단하기 전에 반품할 수 없게 된다는 정책 불만 | 기한을 놓쳤다는 말만 있고 효과 시점과 비교하지 않으면 missed_return_window. 효과가 늦다는 말 자체는 hair_reduction | "You only have 4 weeks to return but yet it says you won’t se" (R3I8VU9TXZJ1N2); "I cannot return this because it takes so long to really find" (R1ZM15KT6ZURLE) | 4 |
| no_response | 고객센터 연락 불가나 무응답 | Unreachable or no response | 고객센터, 판매자, 제조사에 전화, 메시지, 채팅을 했는데 답이 없다, 사람과 연결이 안 된다, 여러 번 연락해야 했다는 말 | 연락은 닿았지만 환불, 교체를 거절당하면 refund_replace_refused. 답은 왔지만 성의 없거나 도움이 안 되면 unhelpful_service | "their customer service won’t answer the phone" (R29LTEY2ULGDKX); "The seller has refused to acknowledge any of my 5 messages." (R3AHPS52Z6NIVG) | 13 |
| refund_replace_refused | 환불이나 교체, 수리 거절 | Refund or replacement refused | 환불, 교체, 수리, 반품을 거절당했다, 사용자 과실로 돌렸다, 가격 차액이나 스토어 크레딧처럼 일부만 보상받았다는 말 | 거절 이유가 기한 경과뿐이면 missed_return_window. 답 자체가 없으면 no_response | "they declined to repair or replace it" (R1BT7Y43OAYIN7); "Best amazon could do after contacting them three times was a" (R2OHNX29MJBII3) | 7 |
| unhelpful_service | 응대가 성의 없거나 도움이 안 됨 | Unhelpful or poor service | 고객센터가 형편없다, 도와줄 수 있는 게 없다고 했다, 제품을 책임지지 않는다, 문제를 대수롭지 않게 넘겼다는 말 | 연락이 안 되거나 답이 없으면 no_response. 구체적으로 환불, 교체를 거절했으면 refund_replace_refused | "I reached out to customer service and they told me to not wo" (R1BRBOP254558S); "The customer service is also poor" (R30SXDQSJ7QM37) | 4 |
| slow_return_process | 반품이나 환불 절차가 느리고 번거로움 | Slow or tedious return process | 반품 절차가 길고 번거롭다, 환불이 몇 달째 안 들어왔다, 여러 번 시도한 끝에 겨우 환불받았다는 말 | 연락 자체가 안 되면 no_response. 결국 거절당했으면 refund_replace_refused | "Months later, I still have not received my refund." (R26NCNGHQU12WZ); "Amazon has changed their return process and makes that long " (R2JZND2LNQW1IF) | 3 |
| other | 기타 | Other | 위 라벨에 들지 않는 것 | - | - | 4 |

메모: 반품 기한 관련 인용이 절반 가까이 된다. R3LZWIQRKS8R3A처럼 "this also passes the return period"는 앞 문맥상 효과 확인 기간과 비교한 말로 보여 window_ends_before_results로 셌지만 인용만으로는 경계가 애매하다. 보증 기간이 1년뿐이다(R4I22WQC4FUKT), 돈을 돌려 달라(R97OX7XS8RVRJ)처럼 응대 경험 없는 말은 기타로 셌다.

### 긍정 이슈(긍정, 혼합 인용): 인용 20개, 표본 20개

| id | 이름 | 영어 이름 | 포함 | 제외 | 대표 인용 | 어림 개수 |
|---|---|---|---|---|---|---|
| refund_granted | 환불이나 반품을 받아 줌 | Refund or return granted | 환불을 문제없이 받았다, 기한이 지났는데도 반품이나 전액 환불을 해 줬다, 판매자가 먼저 연락해 환불해 줬다는 말 | 돈이 아니라 새 제품으로 바꿔 줬으면 free_replacement. 구체적 결과 없이 응대 태도만 칭찬하면 helpful_service | "refund issued no problem" (R5A9JWD6G35F8); "The company reached out and offered full refund even though " (R1SDYJMPTO5X2D) | 7 |
| free_replacement | 무상 교체나 새 제품 발송 | Free replacement | 고장이나 문제가 생기자 새 제품으로 바꿔 줬다, 무상 교체를 제안했다, 새 기기를 보내 줬다는 말 | 환불을 받았으면 refund_granted. 고장 자체는 quality | "Braun is replacing it for free" (R2TAW3BLI22CBT); "the company responded quickly and replaced it with a brand-n" (RDEHKQF7X6P2P) | 5 |
| helpful_service | 응대가 친절하고 빠름 | Helpful and responsive service | 고객센터가 친절하다, 훌륭하다, 빨리 답했다, 해결 방법을 여러 가지 제시했다, 고객 만족에 힘쓴다는 말(환불, 교체 같은 구체적 결과 없이) | 환불이나 교체를 받았다는 결과가 있으면 refund_granted 또는 free_replacement | "Customer Service team was quick to respond and offered sever" (R10EBCR0NL97P2); "They were very pleasant and helpful." (R18XD7IXMDFRMP) | 8 |
| other | 기타 | Other | 위 라벨에 들지 않는 것 | - | - | 0 |

메모: 표본이 20개뿐이라 라벨마다 개수가 적다. 1,2★ 리뷰에서도 환불, 교체 칭찬이 나온다(R343EEURPQIXZ2, RGRI74CC8ENT0).

## 포장 (packaging)

### 부정 이슈(부정, 혼합 인용): 인용 3개, 표본 0개

인용이 20개 미만이거나 라벨이 없어 기타만 둡니다.

### 긍정 이슈(긍정, 혼합 인용): 인용 26개, 표본 26개

| id | 이름 | 영어 이름 | 포함 | 제외 | 대표 인용 | 어림 개수 |
|---|---|---|---|---|---|---|
| attractive_premium_box | 예쁘고 고급스러운 포장 | Attractive, premium-looking packaging | 상자나 포장이 예쁘다, 고급스럽다, 세련됐다, 보기 좋게 담겨 왔다, 선물하기 좋다는 말과 포장이 좋다, 마음에 든다는 전반적 호감 | 꼼꼼히 잘 포장되어 왔다(well packaged, bien empaquetado)는 말은 well_packed, 상자를 보관이나 정리에 쓴다는 말은 practical_storage_box, 기기와 함께 오는 보관 케이스나 파우치는 accessories | "The packaging is beautiful and feels very premium." (R2FH84S1LVI3LT); "This came beautifully boxed and presented" (R1E8UGOQ0TAQSW) | 18 |
| well_packed | 꼼꼼하게 잘 포장되어 옴 | Well packed | 잘 포장되어 왔다, 포장을 잘 했다(well packaged, well packed, bien empaquetado)처럼 포장 작업이나 보호 상태를 칭찬하는 말 | 포장의 겉모습이나 고급스러움을 칭찬하면 attractive_premium_box, 제품이 멀쩡하게 도착했다는 말은 shipping | "it came very well packaged" (R37BVWJW81QEP9); "súper bien empaquetado" (RQUQENL329XRW) | 5 |
| practical_storage_box | 보관에 쓰기 좋은 실용적인 상자 | Practical box for storage | 제품 상자가 튼튼하거나 실용적이어서 계속 보관하거나 구성품을 정리해 두기 좋다는 말 | 보기 좋다는 말만 있으면 attractive_premium_box, 기기와 함께 오는 보관 케이스, 파우치, 가방은 accessories | "I am keeping in the Ulike sturdy box for added care" (R2EDE4DS2YX5SP); "It comes in a very nice clampshell type box that keeps every" (R17Z3G31WY4J6A) | 3 |
| other | 기타 | Other | 위 라벨에 들지 않는 것 | - | - | 0 |

메모: "El empaque muy bien", "The packaging was nice"처럼 이유 없이 포장이 좋다는 말은 attractive_premium_box로 셌음. well_packed와는 '잘 포장해 보냈다'(동사형, 보호)인지 '포장이 좋다, 예쁘다'(겉모습, 호감)인지로 나눔

## 품질 (quality)

### 부정 이슈(부정, 혼합 인용): 인용 156개, 표본 150개

| id | 이름 | 영어 이름 | 포함 | 제외 | 대표 인용 | 어림 개수 |
|---|---|---|---|---|---|---|
| early_failure | 받자마자 또는 한 달 안에 고장 | Defective on arrival or failed within a month | 받았을 때부터 켜지지 않거나 불량, 손상된 채 왔다는 말, 또는 몇 번 쓰고, 몇 주에서 한 달 안에 기기 전체가 멈췄다는 말(충전기나 케이블 때문에 처음부터 못 쓴 경우 포함) | 한 달 넘게 쓴 뒤 고장은 failed_after_months, 시기를 말하지 않은 고장은 failure_unspecified, 특정 모드나 버튼, 센서만 안 되면 partial_failure | "Stopped working after 3 uses. Won’t even turn on." (RJLK2EL94UMYE); "The machine I received is faulty" (R3806RF3C4GFDU) | 30 |
| failed_after_months | 몇 달 쓴 뒤 고장이나 성능 저하 | Failed or weakened after months of use | 한 달 넘게(몇 달에서 몇 년) 쓴 뒤 기기 전체가 멈췄다는 말, 수명이 짧다, 오래 못 쓴다, 발광 횟수를 다 쓰기 전에 끝났다는 평가, 쓸수록 발광이 약해지거나 예전만큼 안 된다는 말(시기와 무관) | 한 달 안의 고장은 early_failure, 시기를 말하지 않은 고장은 failure_unspecified, 털이 덜 줄었다는 효과 이야기는 이 주제가 아님(hair_reduction) | "Stopped working after 4 months." (RTZ6KQ6T15U3J); "Barely works after a few months of use." (R2JM1I6ZLDWZ00) | 36 |
| failure_unspecified | 고장(시기 언급 없음) | Stopped working, timing not stated | 기기가 멈췄다, 켜지지 않는다, 발광이 안 된다, 오작동했다고만 하고 언제 그랬는지 말하지 않는 말 | 시기를 말하면 early_failure 또는 failed_after_months, 가끔만 안 되면 intermittent_malfunction, 일부 기능만 안 되면 partial_failure | "it just stopped working" (R2SZIVAO4SCY8R); "It turns on and cools, but the laser itself isn't working." (RPRSBLD7AE510) | 17 |
| partial_failure | 특정 모드나 버튼, 센서만 고장 | Specific mode, button, or sensor failed | 얼굴 모드, 자동 모드, SHR 모드, 세기 버튼, 전원 버튼, 피부 센서처럼 기기의 일부 기능만 계속 안 된다는 말(센서가 피부를 더는 읽지 못함 포함) | 가끔 되다 안 되다 하면 intermittent_malfunction, 기기 전체가 멈추면 시기에 따라 early_failure, failed_after_months, failure_unspecified, 피부색 때문에 센서가 막는 것은 이 주제가 아님(skin_hair_suitability) | "Face mode stopped functioning the 2nd time I used it" (R11JTE4QJDAYQR); "the sensor has stopped reading skin after less than a month " (R97OX7XS8RVRJ) | 11 |
| intermittent_malfunction | 가끔 발광 안 함이나 저절로 꺼짐 | Misfires, freezes, or shuts off randomly | 피부에 닿아도 가끔 발광하지 않는다, 헛발사, 멈춰서 다시 꽂아야 한다, 이유 없이 저절로 꺼지거나 재시작된다는 말 | 열 때문에 꺼진다고 하면 overheating, 한 기능이 계속 안 되면 partial_failure, 피부에 딱 붙여야 발광하는 사용 방식의 불편은 이 주제가 아님(ease_of_use) | "it misfires literally like 90% of the time" (R2C4TROJI0WAZI); "it just turns off automatically by itself for no reason" (RRJWFICVRDKH7) | 20 |
| overheating | 기기 과열 | Device overheats | 기기 몸체나 헤드가 뜨거워진다, 과열로 꺼진다, 식을 때까지 쉬어야 한다, 뜨거워지면서 냉각이 안 된다는 말 | 쏠 때 피부에 닿는 열감이나 탈 것 같은 감각은 이 주제가 아님(pain_comfort), 탄내나 연기는 scorch_marks_smell | "It gets super hot after a few minutes of use, and we're worr" (R3AHPS52Z6NIVG); "the unit gets hot and automatically powers off" (R2OYIIRT8H081A) | 16 |
| scorch_marks_smell | 조사창 얼룩이나 탄내, 연기 | Window scorch marks, burning smell, or smoke | 조사창이나 렌즈 안의 검은 얼룩과 그을음, 사파이어 창에 김이 서림, 탄내나 플라스틱 타는 냄새, 펑 소리와 불꽃, 연기가 났다는 말 | 그 때문에 무섭다, 위험하다는 안전 우려는 이 주제가 아님(safety), 냄새나 연기 없이 그냥 멈춘 것은 고장 라벨 | "The laser window has scorch marks on it" (R1KNHD542ODN3O); "weird, almost burning plastic like smell that comes from the" (R1O1Y1AMTALTUT) | 14 |
| fragile_build | 약한 만듦새나 부품 파손 | Flimsy build or broken parts | 재질이 약하다, 깨지기 쉽다, 헤드나 캡이 깨지거나 부식됐다, 버튼 느낌이 싸다, 가격에 비해 만듦새가 못하다는 말 | 작동이 멈춘 고장은 고장 라벨, 가격 대비 실망 자체는 이 주제가 아님(price_value), 무게나 모양은 design | "it’s extremely fragile" (RW52SEIQ8TX0B); "Not even a year the big laser head shattered!!" (RTQY6V0DQNOTE) | 9 |
| other | 기타 | Other | 위 라벨에 들지 않는 것 | - | - | 3 |

메모: 완전 고장이 표본의 절반 넘게 차지해 시기(한 달 안, 한 달 넘게, 언급 없음)로 나눴다. 시기 언급 없는 고장이 어림 17개라 따로 두었고, 한 인용에 시기와 탄내가 함께 있으면 두 라벨을 단다.

### 긍정 이슈(긍정, 혼합 인용): 인용 65개, 표본 65개

| id | 이름 | 영어 이름 | 포함 | 제외 | 대표 인용 | 어림 개수 |
|---|---|---|---|---|---|---|
| well_made | 잘 만든 느낌, 고급스러움 | Feels well made and premium | 품질이 좋다, 잘 만든 느낌이다, 고급스럽다, 비싸 보인다, 싸 보이지 않는다처럼 만듦새와 첫인상을 칭찬하는 말 | 튼튼하다, 오래 간다, 아직 잘 작동한다, 과열이 없다는 durable, 모양이나 색이 예쁘다는 이 주제가 아님(design) | "It feels well made" (R2JRF62JGQA1TY); "The device feels very well made and has a much more premium " (R18D1G0XPQQ91Y) | 57 |
| durable | 튼튼하고 오래 작동함 | Sturdy and durable | 튼튼하다, 내구성이 좋다, 견고하다, 아직도 잘 작동한다, 남들이 말한 과열을 겪지 않았다는 말 | 일반적인 품질 칭찬이나 고급스러운 느낌은 well_made | "very durable" (R2PH76S40PV5X1); "I have not experienced the overheating that some have report" (R2SC0RZYQYFC7C) | 7 |
| other | 기타 | Other | 위 라벨에 들지 않는 것 | - | - | 1 |

메모: 고급스러움(premium, looks expensive)은 어림 5개로 품질 칭찬과 경계가 흐려 well_made에 합쳤다. "build quality feels solid"처럼 solid는 느낌 칭찬이라 well_made, sturdy, durable, robustly built는 durable로 본다.

## 제모 효과 (hair_reduction)

### 부정 이슈(부정, 혼합 인용): 인용 286개, 표본 150개

| id | 이름 | 영어 이름 | 포함 | 제외 | 대표 인용 | 어림 개수 |
|---|---|---|---|---|---|---|
| no_effect | 효과 없음 | No visible effect | 써 봐도 털에 변화가 없거나 아주 적다는 말, 기대나 광고, 다른 리뷰만큼 효과가 없다는 말(줄었다는 인정 없이) | 줄거나 가늘어졌다고 인정하면 partial_reduction, 일부 부위만 안 되면 uneven_by_area, 아직 기다리는 중이라며 늦다고 하면 slow_results | "Absolutely zero results" (R2DXIC5NR8A970); "I have been using it for 4 months with no change" (R1ZM15KT6ZURLE) | 68 |
| partial_reduction | 줄었지만 다 없어지지 않음 | Reduced but not gone | 털이 줄거나 느리게, 가늘게 자란다고 인정하면서 다 없어지지 않았다, 여전히 면도나 뽑기를 해야 한다, 완전히 없애 주지는 못한다는 말 | 사용을 멈춘 뒤 다시 자란다, 영구적이지 않다는 말은 not_lasting, 부위를 나눠 되고 안 되고를 말하면 uneven_by_area | "my hair growth is less but certainly not gone" (R2X5WAT77HEGQH); "It's definitely slows the grow after consistent use. But I s" (R220YD40R0TEWH) | 29 |
| uneven_by_area | 부위마다 효과 차이 | Uneven results across body areas | 어떤 부위(겨드랑이, 다리)는 되는데 다른 부위(얼굴, 비키니, 음모)는 안 되거나 덜 된다는 말, 특정 부위에서만 효과가 없다는 말 | 피부색, 털 색 때문에 갈린다는 말은 이 주제 밖(skin_hair_suitability), 부위 구분 없이 전체가 덜 줄었다는 말은 partial_reduction | "It worked very well for my underarms. But hasn't done much f" (R1UI82S8I64AUB); "Buena para el cuerpo pero no sirve en la cara" (R1WAF4RFXZ6I6S) | 25 |
| slow_results | 효과가 늦게 나타남 | Results take too long | 효과가 아주 천천히 나온다, 광고보다 오래 걸린다, 생각보다 늦다, 아직 큰 변화가 없어 더 오래 써야 할 것 같다는 말 | 충분히 썼는데 변화가 없다고 결론 내리면 no_effect, 일정을 지키는 시간 부담은 이 주제 밖(treatment_time) | "It works but it takes longer than advertised." (R1LS0E4XTPW5B3); "If you expect quick hair removal, you may be disappointed be" (RYNUARHCQ2I8S) | 10 |
| not_lasting | 멈추면 다시 나고 영구적이지 않음 | Regrows after stopping, not permanent | 사용을 멈추면 털이 다시 자란다, 효과가 오래 가지 않는다, 영구 제모가 아니다, 계속 관리해야 유지된다는 말 | 사용하는 동안에도 다 없어지지 않았다는 말은 partial_reduction | "the hair still growing back after you stop using it for a mo" (R3P4S1IA50BL9G); "Noticed difference but results are not permanent at all" (R1NX4O5T45E2TY) | 10 |
| other | 기타 | Other | 위 라벨에 들지 않는 것 | - | - | 8 |

메모: 오히려 털이 더 나거나 굵어졌다는 말(R7MKP02LZBEEJ, RPVH9XL7JMHEX, R3EGHJ3KA8QM68 등 4개)은 5% 미만이라 기타로 셈. 기타에는 단계(세기)에 따라 효과가 갈린다는 말, 놓친 곳(hot spots), 먼저 면도해야 한다는 말, 흰 피부라 안 된다는 유형 이야기(skin_hair_suitability에 가까움)도 있음.

### 긍정 이슈(긍정, 혼합 인용): 인용 444개, 표본 150개

| id | 이름 | 영어 이름 | 포함 | 제외 | 대표 인용 | 어림 개수 |
|---|---|---|---|---|---|---|
| works_general | 효과가 있음 | It works | 털이 어떻게 변했는지 구체적으로 말하지 않고 효과가 있다, 잘 된다, 결과가 보인다는 말 | 털이 줄거나 느리게 자란다고 구체적으로 말하면 reduced_regrowth, 부위를 들어 말하면 works_on_areas, 꾸준히 써야 한다는 조건이 붙으면 works_with_consistency | "really works well" (R5A9JWD6G35F8); "it really works" (R2ZL2O4HNXMEWG) | 56 |
| reduced_regrowth | 털이 줄고 느리게 자람 | Less and slower regrowth | 털의 양이 줄었다, 다시 자라는 속도가 느려졌다, 수염 자국이 늦게 올라온다는 말 | 가늘고 옅어진 질감 변화가 중심이면 finer_lighter, 거의 없어졌거나 면도를 거의 안 한다면 nearly_gone_less_shaving | "it has significantly reduced the hair growth on my legs and " (R1NE4QCL8NG603); "I started noticing slower hair regrowth" (RZWG7C67I26NH) | 25 |
| finer_lighter | 털이 가늘고 옅어짐 | Finer and lighter hair | 털이 가늘어졌다, 옅어졌다, 부드러워졌다, 성기게 났다는 말 | 털의 양이나 속도만 말하면 reduced_regrowth | "noticed my hair growing back way slower and in some areas th" (R2VNEBLNFNGTZ1); "it is much slower and much thinner" (RDP6VFH1J365D) | 11 |
| nearly_gone_less_shaving | 거의 없어지거나 면도가 줄어듦 | Nearly hair-free, less shaving | 털이 거의 다 없어졌다, 어떤 부위는 아예 안 난다, 면도나 뽑기를 거의 안 하게 됐다, 며칠에서 몇 주씩 면도 없이 지낸다, 피부가 매끈해졌다는 말 | 줄었다는 정도만 말하면 reduced_regrowth | "My legs are much smoother and I can go 2 weeks without shavi" (R1CW4J5AG5XQYJ); "I didn't have to pluck my chin hairs or remove my mustache a" (R3TZKM2YDQ6CJZ) | 16 |
| works_on_areas | 특정 부위에 잘 됨 | Works well on specific areas | 겨드랑이, 다리, 윗입술, 비키니 등 부위를 들어 그곳에 효과가 있다는 말(다른 부위는 안 된다는 혼합 인용의 칭찬 부분 포함) | 부위 언급 없이 효과가 있다는 말은 works_general | "It has worked really well on the under arm and the upper lip" (R3EX80CEESZ3VQ); "It works well - like professional grade on the bikini line a" (R25K2A8S4MLZQH) | 20 |
| quick_results | 빨리 효과가 보임 | Quick visible results | 몇 번, 몇 주 만에(이미, 벌써) 효과가 보였다는 말 | 오래 걸렸지만 결국 됐다는 말은 works_general이나 해당 변화 라벨 | "super large reduction by just 3 treatments" (R135IHQ3F4GVSS); "We could see a difference after a couple of uses" (RW52SEIQ8TX0B) | 12 |
| works_with_consistency | 꾸준히 쓰면 효과가 남 | Works with consistent use | 꾸준히, 규칙적으로, 참을성 있게 쓰면 효과가 있다는 조건을 붙인 칭찬 | 일정을 지키는 시간 부담 평가는 이 주제 밖(treatment_time) | "This really works, but you have to be consistent." (R1J63SGER4AU6O); "IPL technology can greatly reduce hair growth with constant " (R21FD6E2B6LEB7) | 8 |
| other | 기타 | Other | 위 라벨에 들지 않는 것 | - | - | 7 |

메모: 살롱 레이저 뒤 유지용으로 좋다는 말(R3RK6KXOETTEWH, R35BI1HBVKI1R, R1VFPBIS4Y1VID 3개)은 5% 미만이라 기타. 거의 없어짐과 면도 줄어듦은 따로 두면 각각 5% 미만이라 하나로 합침. reduced_regrowth와 quick_results는 "이미 줄었다"처럼 함께 달릴 수 있음.

## 통증과 시술 편안함 (pain_comfort)

### 부정 이슈(부정, 혼합 인용): 인용 64개, 표본 64개

| id | 이름 | 영어 이름 | 포함 | 제외 | 대표 인용 | 어림 개수 |
|---|---|---|---|---|---|---|
| strong_pain | 심하게 아픔 | Strong pain | 쏠 때 많이 아프다, 감전된 것 같다, 못 참겠다처럼 통증을 세게 말하는 말(부위, 단계, 열감 언급 없이) | 조금, 약간, 참을 만하다는 단서가 붙으면 mild_sting. 특정 부위를 말하면 sensitive_area_pain, 뜨겁다거나 타는 느낌이면 hot_burning_sensation | "Hurts like crazy!!" (R1MF4HYB0A1PZ4); "it feels like you getting electrocuted" (R2MTD56P6QYOUV) | 15 |
| mild_sting | 약간 따끔함, 기대만큼 무통은 아님 | Mild sting, not fully painless | 조금 아프다, 가끔 따끔하다, 고무줄 튕기는 느낌이다, 참을 만하지만 무통은 아니다, 광고나 기대만큼 무통은 아니다, 처음 몇 번 조금 아팠다 | 통증을 세게 말하면 strong_pain. 특정 부위를 말하면 sensitive_area_pain, 높은 단계 때문이라고 하면 high_setting_too_strong | "it hurts a bit, but I can tolerate it" (R54TAWF3OMWUZ); "It was not as painless as I expected." (R71QMDUFW94NP) | 17 |
| sensitive_area_pain | 민감한 부위나 특정 지점에서 아픔 | Pain on sensitive areas or spots | 비키니, 겨드랑이, 허벅지 안쪽, 은밀한 부위, 문신이나 주근깨 위, 몇몇 지점처럼 부위를 짚어 그곳이 아프다는 말 | 부위 언급 없이 아프다는 말은 strong_pain이나 mild_sting. 그 부위 때문에 단계를 낮춰야 한다는 말이 함께 있으면 high_setting_too_strong을 두 번째로 단다 | "I tried the bikini line, but it was too painful" (RITH3PKTVCDLZ); "it hurt especially in the underarm area" (RH6TJCI4IIG0W) | 13 |
| hot_burning_sensation | 쏠 때 뜨겁거나 타는 느낌 | Hot or burning sensation during flash | 발광할 때 뜨겁다, 타는 듯하다, 피부 온도가 오른다(quema, burn sensation)처럼 쏘는 순간의 열감 | 오래 쓸수록 뜨거워진다는 말은 heats_up_with_use. 냉각이 소용없다는 말이 함께 있으면 cooling_insufficient. 화상 상처처럼 남는 피부 손상은 주제 밖(safety) | "extremely hot during the flash" (R4FJL7WTJVD4I); "quema al contacto con la piel" (RXVJQ54HKI82D) | 12 |
| heats_up_with_use | 오래 쓸수록 뜨거워지고 더 아픔 | Gets hotter and more painful during a session | 한 번 시술하는 도중 시간이 지나면 창이 뜨거워진다, 오래 대고 있을수록 더 아프다 | 처음부터 쏠 때 뜨겁다는 말은 hot_burning_sensation. 기기 몸체가 과열돼 멈추는 고장은 주제 밖(quality) | "this gets so hot & hurts so bad after awhile" (R7SOJ6E4622H6); "It doesn't hurt at all but can get hot if you're using it fo" (R1S9BDFJ2QUC6U) | 4 |
| cooling_insufficient | 냉각 기능이 약하거나 없음 | Cooling ineffective or missing | 냉각 기능이 차이를 못 만든다, 기대보다 약하다, 높은 단계에서는 덜 듣는다, 냉각이 있는데도 뜨겁다, 냉각 기능이 없다 | 냉각 언급 없이 뜨겁다는 말은 hot_burning_sensation | "I don't think the cooling makes a difference." (R2WKT4WSARV4ZP); "The cooling function is also not as effective as I expected" (RI2SISRQKM0M2) | 6 |
| high_setting_too_strong | 높은 단계가 세서 낮춰야 함 | Higher settings too strong | 높은 단계(레벨 9, SHR 등)가 세다, 한 단계 낮춰야 편하다, 낮게 시작하라, 가장 낮은 단계에서도 아프다 | 단계 언급 없이 아프다는 말은 strong_pain이나 mild_sting | "I use level 9 but have a high tolerance. However, sometimes " (R2OFSAFX7C3B4C); "It isnt as painless as I had hoped, it always felt like it w" (R1ZBU72UNF0W78) | 6 |
| other | 기타 | Other | 위 라벨에 들지 않는 것 | - | - | 2 |

메모: 부위, 단계, 냉각, 열감 언급이 세기 표현(심함, 약간)과 한 인용에 함께 나오는 일이 많아, 원인(부위, 단계, 냉각, 열감)을 먼저 달고 세기 라벨은 원인 언급이 없을 때만 다는 순서가 필요함. 털이 남아 따끔하다(R1E3UY1UREFRJ5)는 2개뿐이라 mild_sting에 넣음. 'it burned so bad'(RK36OGAJTBQZI, 문신 위)처럼 감각인지 피부 손상인지 애매한 인용이 있음.

### 긍정 이슈(긍정, 혼합 인용): 인용 201개, 표본 150개

| id | 이름 | 영어 이름 | 포함 | 제외 | 대표 인용 | 어림 개수 |
|---|---|---|---|---|---|---|
| painless_comfortable | 아프지 않고 편함 | Painless and comfortable | 아프지 않다, 무통이다, 전혀 못 느끼겠다, 편하다, 부드럽다(no duele, sans douleur 포함) | 거의, 조금, 참을 만하다는 단서나 따뜻한 느낌이 붙으면 mild_tolerable. 냉각 덕분이라고 하면 cooling_comfort, 다른 제모 방법과 비교하면 less_painful_than_alternatives | "doesnt hurt at all" (R2CS77XLUVIHJ1); "no duele para nada" (R1R8M6N2N5OPF) | 65 |
| mild_tolerable | 거의 무통이거나 참을 만함 | Nearly painless or tolerable | 거의 아프지 않다, 통증이 적다, 그렇게 나쁘지 않다, 따끔하지만 참을 만하다, 따뜻한 느낌 정도다(gentle warmth, sensación leve de calor) | 단서 없이 아프지 않다는 말은 painless_comfortable. 높은 단계나 민감한 부위에서도 괜찮다는 말은 fine_on_high_setting_or_sensitive_area | "minimal pain" (RKY1PUP3AY62W); "the mild stinging is tolerable" (R1P2GZ35WDN7RQ) | 30 |
| cooling_comfort | 냉각 기능 덕분에 편함 | Cooling makes it comfortable | 냉각 기능, 차가운 느낌, 아이스 쿨링 덕분에 편하다, 덜 아프다, 냉각 기능이 좋다(se siente frío 포함) | 냉각 언급 없이 아프지 않다는 말은 painless_comfortable | "The cooling mechanisms are great, making the removal much le" (R21RTTZMPSBND7); "no duele, se siente frío" (R1YD46GOLUQL4B) | 36 |
| less_painful_than_alternatives | 왁싱이나 병원 레이저보다 덜 아픔 | Less painful than waxing or salon laser | 왁싱, 피부과나 살롱 레이저, 전에 쓴 다른 제모기보다 덜 아프다, 걱정했던 것보다 아프지 않다며 다른 기기 경험과 비교 | 비교 대상 없이 아프지 않다는 말은 painless_comfortable. 다른 기기와 비교하며 냉각 덕분이라고 하면 cooling_comfort를 함께 단다 | "waayyyyyy more comfortable than professional laser hair remo" (R8Y3GAPALYC2D); "no duele para nada a comparación de la depilación con cera" (R25ARWS7R12PWW) | 10 |
| fine_on_high_setting_or_sensitive_area | 높은 단계나 민감한 부위에서도 괜찮음 | Fine even on high settings or sensitive areas | 가장 높은 단계에서도 아프지 않다, 비키니나 민감한 피부에도 참을 만하다, 다리와 팔은 최대 단계로 쓴다 | 단계나 부위 언급 없이 아프지 않다는 말은 painless_comfortable이나 mild_tolerable | "The pain is super minor on the highest setting (2/10)" (R2SGB5RDA6XE9); "the sting from the razor is very tolerable, even on bikini r" (R9M2I2AM5KP6S) | 8 |
| other | 기타 | Other | 위 라벨에 들지 않는 것 | - | - | 2 |

메모: fine_on_high_setting_or_sensitive_area는 표본의 5% 언저리(어림 8개)라 합칠지 판단이 필요함. painless_comfortable과 mild_tolerable은 '거의', '조금' 같은 단서 유무로만 갈려 경계가 얇음. 쓰다 보면 익숙해진다(R3TZKM2YDQ6CJZ, R1NJL66X5FEMYR)는 2개뿐이라 기타.

## 안전 (safety)

### 부정 이슈(부정, 혼합 인용): 인용 84개, 표본 84개

| id | 이름 | 영어 이름 | 포함 | 제외 | 대표 인용 | 어림 개수 |
|---|---|---|---|---|---|---|
| skin_burns | 화상이나 물집 | Burns or blisters | 기기 때문에 피부가 데었다, 화상, 화상 자국, 물집이 생겼다는 말(설명서대로 했는데도, 문신 위, 패치 테스트에서 등). 화상 뒤 남은 자국이나 반점도 화상을 함께 말하면 여기 | 화상이라는 말 없이 검은 반점, 색이 빠짐, 흉터만 말하면 pigment_scars. 화상을 입을까 무섭다는 걱정만 있으면 safety_worry. 쏘는 순간 뜨겁다, 따갑다는 감각은 주제 밖(pain_comfort) | "I followed the instructions and this left blisters on my leg" (R2XB776KKIF8N9); "by the next day it was clear my legs were covered in 1st deg" (RELGENLC93HHW) | 22 |
| irritation_redness | 자극, 붉음, 가려움 | Irritation, redness or itching | 시술 뒤 피부가 자극받았다, 붉어졌다, 가렵다, 건조해졌다, 민감한 피부에는 맞지 않는다는 말(눈에 띄는 돋음이나 발진 없이 느낌과 붉음만) | 발진, 뾰루지, 여드름 같은 돋음, 모낭염, 인그로운 헤어, 알레르기 반응을 말하면 rash_bumps_allergy. 데었다는 말은 skin_burns | "the skin irritation is massive" (R1EO3673L9E28J); "the skin became red" (R2A2KTRD9JXJMV) | 11 |
| rash_bumps_allergy | 발진, 뾰루지, 알레르기 반응 | Rash, bumps or allergic reaction | 시술 뒤 발진, 두드러기 같은 돋음, 여드름이나 뾰루지, 모낭염, 인그로운 헤어가 늘었다, 알레르기(히스타민) 반응이 났다는 말. 가려운 발진처럼 가려움과 함께 나와도 돋음이 있으면 여기 | 돋음 없이 자극, 붉음, 가려움만이면 irritation_redness. 면도 트러블(인그로운 헤어)이 줄었다는 좋은 변화는 주제 밖(hair_reduction) | "Gave me horrible folliculitis." (R3FCCN4LLKDHW9); "had an allergic reaction the second time" (R395GW5N4JJ51A) | 17 |
| pigment_scars | 색소 변화나 흉터 | Pigment change or scarring | 피부에 검은 반점이나 자국이 생겼다, 색이 빠지거나 하얗게 됐다, 변색, 흉터가 남았다, 이상한 점이 생겼다는 말(화상이라는 말 없이) | 데었다, 화상 자국이라고 말하면 skin_burns. 발진이나 뾰루지는 rash_bumps_allergy | "ended up with dark spots on my shins" (R1JRAFD7P6L9RA); "it removed pigment from my skin" (R7MKP02LZBEEJ) | 11 |
| eye_flash_glare | 눈부심이나 눈 안전 | Flash glare or eye safety | 섬광이 너무 밝다, 보안경을 써도 빛이 들어온다, 눈에 해롭다, 두통이나 편두통, 시야 이상이 생겼다, 광고에 보안경 없이 쓰는 모습이 나온다는 말 | 보안경이 구성에 들어 있는지는 주제 밖(accessories). 빛이 창 가장자리나 피부 밖으로 새어 다른 곳에 닿는다는 말은 기타 | "The flash is still bright even with glasses on and sometimes" (R30MIFDD6J1ZO9); "the light is so harmful for the eyes" (R300NO6N06MI3R) | 11 |
| safety_worry | 안전 불안이나 쓰기 무서움 | Safety doubts or fear of use | 실제 피부 반응을 말하지 않고 안전한지 의심된다, 위험하다, 쓰기 무섭다, 데일까 겁났다, 민감한 부위에 안전하지 않다, 상자에 경고 문구가 없다는 말 | 실제로 데었거나 반응이 났다는 말이 같은 인용에 있으면 그 반응 라벨(예 데고 나서 무섭다는 skin_burns). 눈에 대한 걱정은 eye_flash_glare | "Is this safe? I have my doubts" (RL9O9OQ9H76YI); "me da miedo seguir usándola" (RUOAHQVG9XL2W) | 9 |
| other | 기타 | Other | 위 라벨에 들지 않는 것 | - | - | 3 |

메모: 기타는 빛이 창 가장자리나 피부 밖으로 새어 나감(R371G2D4TFMWP7, R1NZEC16D5FOP4, 2개로 5% 미만)과 뜻이 불분명한 인용(R2822A4GNWEGMX). "it burns", "my skin started to burn"처럼 쏘는 순간 감각(pain_comfort)인지 화상인지 애매한 인용이 몇 개 있어 skin_burns로 셌다.

### 긍정 이슈(긍정, 혼합 인용): 인용 37개, 표본 37개

| id | 이름 | 영어 이름 | 포함 | 제외 | 대표 인용 | 어림 개수 |
|---|---|---|---|---|---|---|
| no_irritation | 자극이나 피부 반응 없음 | No irritation or skin reaction | 시술 뒤 자극, 붉음, 뾰루지, 건조함, 색소 침착 같은 피부 반응이 전혀 없었다, 피부에 순하다는 말 | 민감한 피부인데도 괜찮다고 하면 sensitive_skin_ok. 반응이 조금 있었지만 가라앉았다, 심하지 않았다면 mild_transient. 통증이 없다는 부분은 주제 밖(pain_comfort) | "no skin irritation" (R3BL6AS4FEBLLB); "I had no discomfort, redness, or irritation at all after usi" (R1FJKJ53PU9AIM) | 20 |
| mild_transient | 반응이 가볍거나 금방 가라앉음 | Mild or short-lived reaction | 자극이나 돋음이 있었지만 가벼웠다, 하루 만에 또는 회차를 거듭하며 가라앉았다는 말(혼합 인용의 칭찬 부분) | 반응이 전혀 없었다는 말만 있으면 no_irritation. 가라앉았다는 말 없이 반응만 있으면 칭찬이 아니므로 기타 | "I did get some stippling on the back of my legs where I used" (R3AL97KPZJMJ8N); "I had minor irritation when going over a specific area more " (R3OHPHFT97EWOM) | 4 |
| sensitive_skin_ok | 민감한 피부에도 괜찮음 | Fine for sensitive skin | 민감한 피부에 맞다, 민감한 피부인데도 문제없었다, 민감한 피부에도 안전하다는 말 | 민감한 피부 언급 없이 반응이 없었다는 말은 no_irritation | "perfect for sensitive skin" (R1CKMAYZ81JWU); "I have sensitive skin but have zero issues using on highest " (R2VNEBLNFNGTZ1) | 3 |
| safety_feature | 피부 센서 같은 안전 기능 덕에 안심 | Reassured by safety features | 피부 센서, 피부에 완전히 닿아야 발광하는 기능 같은 기기 기능 덕분에 더 안전하다, 안심된다는 말. 무엇 덕분인지 인용 안에 다 나오지 않아도 어떤 것이 더 안전하게 만든다(makes it feel safer)는 말이면 여기 | 이유 없이 안전하다고만 하면 feels_safe. 센서가 어두운 부위에서 발광을 막는 불만은 주제 밖(skin_hair_suitability) | "The built-in skin sensor adds peace of mind" (R3I3HAIAL07C08); "only goes off when fully on skin so it’s safe to use" (R2W8VLAJW7Q7LS) | 6 |
| feels_safe | 쓰기에 안전하다는 느낌 | Feels safe to use | 이유나 기능을 말하지 않고 안전하다, 안심하고 쓴다는 말 | 기기 기능이 이유로 붙으면 safety_feature. 피부 반응이 없었다는 구체적인 말은 no_irritation | "Safe and effective" (R2JZ3KC3BU5VN8); "I feel safe using this as well" (R3INSXQHFCICQI) | 3 |
| other | 기타 | Other | 위 라벨에 들지 않는 것 | - | - | 1 |

메모: 기타 1개는 칭찬 부분이 없는 혼합 인용(R2EAVV0BSKGP5V, 인그로운 헤어 흉터). R1CW4J5AG5XQYJ(반응 없었지만 비키니 부위만 하루 자극)는 mild_transient로 셌고 no_irritation과 경계가 가깝다.

## 디자인과 형태 (design)

### 부정 이슈(부정, 혼합 인용): 인용 47개, 표본 47개

| id | 이름 | 영어 이름 | 포함 | 제외 | 대표 인용 | 어림 개수 |
|---|---|---|---|---|---|---|
| bulky_heavy | 크고 무거움 | Bulky or heavy | 기기가 크다, 부피가 크다, 무겁다, 커서 다루기 힘들다, 오래 들고 있으면 지친다는 말(크기나 무게 단어가 있을 때) | 크기나 무게 말 없이 모양, 손잡이, 각도, 버튼 위치 때문에 쥐기 불편하다는 말은 awkward_grip. 조사창이 작다는 말은 small_window | "The design of this Ulike IPL is definitely on the bulky and " (R6YW7XS4EI7QZ); "It is bulky and heavy to hold for extended sessions." (RYFKQTK5JPNJS) | 15 |
| awkward_grip | 모양이 쥐기 불편함 | Awkward shape or grip | 모양, 손잡이, 인체공학이 어색하다, 각도를 바꿀 때 불편하다, 쥐는 곳에 버튼이 있다, 디자인이 이상해 조작하기 어렵다는 말 | 크거나 무거워서 다루기 힘들다는 말은 bulky_heavy(크기, 무게와 모양을 함께 말하면 둘 다). 조작 방법, 모드, 설명서는 ease_of_use라 이 주제가 아님 | "the hairdryer-style hand grip design is awkward when you’re " (R1W4CHDH2UJAL2); "Awkward to hold, some buttons are where you hold." (R3O6K913ALP80R) | 11 |
| not_cordless | 무선이 아니라 꽂아 써야 함 | Not cordless | 무선인 줄 알았다, 충전식이었으면 좋겠다, 꽂아야만 켜진다, 들고 다닐 수 없다는 말 | 코드가 짧다, 어댑터가 크다는 말은 cord_adapter. 배터리가 금방 닳는다는 말은 기타 | "Must stay plugged in, not portable at all." (R2MI0HOHIKSDB6); "was expecting cordless, unfortunately I could not find cordl" (R2R1PSHBBGVQA5) | 7 |
| cord_adapter | 코드가 짧거나 어댑터가 큼 | Short cord or bulky power adapter | 전원 코드가 짧다, 전원 어댑터가 크고 무겁다는 말 | 무선이 아니라는 불만 자체는 not_cordless | "I found the cable to be a bit short" (RMZHMMCWOCAS9); "Its power supply is about as large as unit itself, and defin" (R2MBCDJ6VJPRMQ) | 3 |
| noisy | 작동 소음이 큼 | Loud operating noise | 팬 소리가 크다, 발광할 때 나는 소리가 거슬린다는 말 | 발광이 느리다, 빠르다는 말은 treatment_time | "there is a loud fan noise so you can't really do while you w" (R2EDE4DS2YX5SP); "a fan comes on and it is noticeably loud" (R1E8UGOQ0TAQSW) | 5 |
| small_window | 조사창이 작음 | Treatment window too small | 조사창이나 헤드가 작다, 넓은 부위용으로 더 큰 헤드가 있었으면 한다는 말 | 헤드가 작아 시간이 오래 걸린다는 시간 불만은 treatment_time. 작은 부위용으로 더 작은 헤드를 원하는 말은 기타. 기기 몸체가 크다는 말은 bulky_heavy | "I wish it was bigger to treat large areas" (R2SGB5RDA6XE9); "I wish the laser head was a tad bit bigger" (R35T6O9HV1N4EB) | 6 |
| other | 기타 | Other | 위 라벨에 들지 않는 것 | - | - | 4 |

메모: 크기, 무게와 모양을 함께 말한 인용(heavy and awkward to hold 등 3개)은 bulky_heavy와 awkward_grip 둘 다 붙는다. 기타는 작은 부위용 더 작은 헤드 요구 2개, 조사면이 평평해 몸 곡선에 안 맞음 1개, 배터리가 중간에 닳음 1개.

### 긍정 이슈(긍정, 혼합 인용): 인용 55개, 표본 55개

| id | 이름 | 영어 이름 | 포함 | 제외 | 대표 인용 | 어림 개수 |
|---|---|---|---|---|---|---|
| looks_good | 예쁘고 고급스러운 외관 | Attractive, premium look | 예쁘다, 세련됐다, 고급스러워 보인다, 색(보라색 등)이 예쁘다, 디자인이 좋다는 말 | 손에 쥐는 느낌과 무게는 light_easy_grip. 만듦새, 튼튼함 자체는 quality라 이 주제가 아님 | "The device itself is very sleek and beautiful." (R2IBA63SK8LQIJ); "the purple color is beautiful too" (R2PNK8AF14NNHH) | 23 |
| light_easy_grip | 가볍고 쥐기 편함 | Lightweight and easy to hold | 가볍다, 무겁지 않다, 손에 잘 맞는다, 쥐기 편하다, 다루기 쉽다, 인체공학적이다는 말 | 작아서 자리를 덜 차지하거나 들고 다니기 좋다는 말은 compact_portable. 조작 방법이 쉽다는 말은 ease_of_use라 이 주제가 아님 | "It is lightweight and easy to hold." (RSUV6NFE2R8FB); "The device is lightweight, comfortable to hold" (R3NJ191QCXHU60) | 18 |
| compact_portable | 작고 휴대하기 좋음 | Compact and portable | 작다, 자리를 덜 차지한다, 여행에 들고 가기 좋다, 휴대성이 좋다, 크기가 작아 겨드랑이나 얼굴 같은 부위에 좋다는 말 | 무게와 쥐는 느낌은 light_easy_grip(작아서 쥐기 쉽다면 둘 다) | "It’s compact and doesn’t take up much space, so I can easily" (RNCOGXWS6VCM2); "very portable" (R1CY0LPVYGLF0R) | 7 |
| long_cord | 전원 코드가 넉넉함 | Long enough power cord | 전원 코드가 길다, 충분히 길어 움직이기 편하다는 말 | 무선이 아니라는 불만은 부정 방향 | "Plugs in and cord is long enough to use the tool with plenty" (R11D1ULS8PBPOD); "The 6ft cord a nice length" (R17Z3G31WY4J6A) | 4 |
| attachments_versatile | 부위별 교체 헤드 | Interchangeable heads for body areas | 부위별 교체 헤드가 여럿 들어 있어 여러 부위에 쓸 수 있다는 말 | 보안경, 면도기, 케이스 같은 구성품은 accessories라 이 주제가 아님 | "The multiple attachments make it versatile for different bod" (R2527CST84MMJT); "I like that it has a broad area head and a smaller area head" (R3AL97KPZJMJ8N) | 4 |
| other | 기타 | Other | 위 라벨에 들지 않는 것 | - | - | 2 |

메모: 기타는 생각보다 컸지만 괜찮다는 혼합 인용 1개와 커서 넓은 부위가 빨랐다는 인용 1개(시간 이야기에 가까움).

## 사용 편의 (ease_of_use)

### 부정 이슈(부정, 혼합 인용): 인용 44개, 표본 44개

| id | 이름 | 영어 이름 | 포함 | 제외 | 대표 인용 | 어림 개수 |
|---|---|---|---|---|---|---|
| hard_to_trigger_flash | 피부에 붙여도 발광이 잘 안 됨 | Hard to get it to flash on contact | 피부 접촉 센서가 접촉을 못 읽어 계속 옮기고 눌러야 발광한다, 턱, 무릎, 굴곡진 부위에서 발광이 안 된다, 처음 몇 번은 발광시키기 어려웠다는 말 | 피부색이나 어두운 부위 때문에 센서가 막는 것은 skin_hair_suitability, 기기 고장으로 발광이 멈춘 것은 quality, 센서가 세기를 멋대로 낮추는 것은 sensor_auto_adjust | "It can be REALLY hard to get the sensors to flash, even when" (R1NZEC16D5FOP4); "Has trouble activating around more uneven body parts, such a" (RLH6WCEL9CZ4C) | 14 |
| sensor_auto_adjust | 센서 자동 조절이 거슬림 | Annoying automatic sensor adjustment | 피부 센서가 세기를 자동으로 낮추거나 판정을 지나치게 조심스럽게 해서 짜증 난다, 자동 조절을 끌 수 없다는 말 | 피부 접촉을 못 읽어 발광이 안 되는 것은 hard_to_trigger_flash, 피부색이 어두워 쓸 수 없다는 것은 skin_hair_suitability | "Air 10's overly cautious skin sensor frequently reduces inte" (RRHU7A16IHWSW); "If it didn't auto adjust the sensitivity or I had the option" (R2I474SRDNJLW9) | 5 |
| unclear_instructions | 설명서가 부족하거나 불분명함 | Unclear or lacking instructions | 설명서에 사용법, 설정, 자동 모드 켜는 법, 한 부위에 몇 번 쏘는지, 시술 뒤 관리 정보가 없다, 번역이 어색하다, 영상을 찾아봐야 했다는 말 | 설명서 언급 없이 기기 조작 자체가 복잡하다는 말은 complicated_operation | "the directions to use the device were lacking much needed in" (R1NE4QCL8NG603); "The instructions could be better on how to set it up." (RD0ZNS0BJ5RSM) | 9 |
| complicated_operation | 조작이 복잡하고 어려움 | Complicated to operate | 기기가 복잡하다, 기능을 어떻게 쓰는지 알기 어렵다, 생각보다 쉽지 않다, 사용자 친화적이지 않다는 전반적인 말 | 설명서 탓을 말하면 unclear_instructions, 특정 모드나 버튼을 지목한 불만은 mode_button_gripes, 발광이 잘 안 되는 것은 hard_to_trigger_flash | "This is a complicated device that requires a lot of patience" (RWTBVMS6K6M9P); "It is difficult to figure out how to work the various featur" (R39LEEA7D1DVP8) | 4 |
| mode_button_gripes | 모드나 버튼 구성이 불편함 | Inconvenient modes or buttons | 자동이나 연속 발광 모드가 없어 매번 버튼을 눌러야 한다, 연속 발광 설정이 싫다, 세기 버튼이 실수로 눌린다, 단계 선택지가 부족하다는 말 | 센서가 세기를 자동으로 바꾸는 것은 sensor_auto_adjust, 발광 속도나 걸리는 시간은 treatment_time | "does not have auto glide function thus you have constantly p" (R30SXDQSJ7QM37); "the power level button is so easy to hit accidentally" (RJ70XYUA71OQC) | 6 |
| shaving_prep | 쓸 때마다 면도해야 하는 번거로움 | Need to shave before each use | 사용 전에 매번, 자주 면도해야 해서 번거롭다는 말 | 면도 횟수가 줄었다는 효과 이야기는 hair_reduction, 면도 안 한 털 때문에 아프다는 말은 pain_comfort | "the fact that i have to shave before every use is a little a" (R2MZ9ZWPKOLRZQ); "You also have to shave a lot." (R1E37CQXV0TSOA) | 3 |
| other | 기타 | Other | 위 라벨에 들지 않는 것 | - | - | 3 |

메모: 기타는 쏜 자리를 알기 어렵다(2개), 교체 부품 세척이 어렵다(1개). R3D6Y9OCRHDR0X "the skin sensor is too sensitive"와 R2HTPKGOEZ3WN7 "won't flash because it is reading red"는 접촉 센서인지 피부색 센서인지 애매해 sensor_auto_adjust로 셌다(피부색으로 막는 것이면 skin_hair_suitability 쪽). shaving_prep은 주제 정의에 직접 적혀 있지 않은 사전 준비 부담이라 treatment_time(관리 부담)으로 옮길지 정해 주세요.

### 긍정 이슈(긍정, 혼합 인용): 인용 176개, 표본 150개

| id | 이름 | 영어 이름 | 포함 | 제외 | 대표 인용 | 어림 개수 |
|---|---|---|---|---|---|---|
| easy_to_use | 쓰기 쉽고 간단함 | Easy and simple to use | 쓰기 쉽다, 간단하다, 처음 써도 된다, 꽂고 켜서 바로 쓴다, 설정이 쉽다, 편하게 쓴다는 전반적인 말 | 설명서를 칭찬하면 clear_instructions, 집에서 할 수 있다는 편리함은 home_convenience, 자동 모드나 단계 조절 기능을 지목하면 handy_modes | "The device itself is also very easy to use, even as a beginn" (RAUDHBMFX7194); "This device is very easy to use, plug, turn on and go." (R25H686ZWIWEWC) | 115 |
| clear_instructions | 설명서가 분명함 | Clear instructions | 설명서가 분명하다, 간단하다, 알아보기 쉽다는 말 | 설명서 언급 없이 쓰기 쉽다는 말은 easy_to_use | "Instructions are clear and straightforward making the produc" (R3EVC73JWUDCAY); "The instructions were straightforward" (R18D1G0XPQQ91Y) | 13 |
| home_convenience | 집에서 할 수 있어 편함 | Convenient to do at home | 살롱에 가지 않고 집에서, 혼자 편하게 할 수 있어 좋다는 말 | 살롱보다 돈을 아낀다는 말은 price_value, 집 언급 없이 편하다는 말은 easy_to_use | "It has been especially convenient to be able to use it at ho" (RDEHKQF7X6P2P); "la comodidad de poder usarla en casa" (R2SZDL813OQQ0C) | 10 |
| handy_modes | 자동 모드와 단계 조절이 편함 | Handy auto mode and settings | 자동 모드 덕에 버튼을 계속 누르지 않아도 된다, 세기를 원하는 대로 조절할 수 있다, 모드가 여러 개다, 화면이나 터치스크린으로 설정 바꾸기가 쉽다는 말 | 자동 모드가 빨라서 시간이 준다는 말은 treatment_time, 피부 센서 칭찬은 기타 | "It comes with different levels of intensity and auto so no n" (RLK89470RDJIH); "It’s easy to use, and the touchscreen makes switching settin" (R65FSNN1S9RE3) | 11 |
| other | 기타 | Other | 위 라벨에 들지 않는 것 | - | - | 9 |

메모: 표본 대부분이 "easy to use" 한마디라 easy_to_use가 4분의 3을 넘는다. 기타는 세척과 관리가 쉽다(3개), 피부 센서가 잘 된다(2개), 앱(2개), 가볍고 다루기 쉽다(R7SFT1B4QUIDU, 무게는 design 쪽), 교체 헤드 덕에 쉽다(RRCG4FZAZP9UC, 헤드는 design 쪽). "easy to use, instructions are clear"처럼 두 칭찬이 한 인용에 있으면 easy_to_use와 clear_instructions 둘 다 셌다.

## 시술 시간과 관리 부담 (treatment_time)

### 부정 이슈(부정, 혼합 인용): 인용 79개, 표본 79개

| id | 이름 | 영어 이름 | 포함 | 제외 | 대표 인용 | 어림 개수 |
|---|---|---|---|---|---|---|
| long_session | 한 번 시술이 오래 걸림 | Sessions take a long time | 시간이 많이 든다, 오래 걸린다, 몇 시간 걸린다는 말 중 부위, 원인, 비교 대상, 횟수를 말하지 않는 것(time consuming, takes forever, 시술 한 번에 30분) | 다리나 몸 전체 같은 넓은 부위를 말하면 large_area_slow, 발광 간격이 원인이면 slow_flash, 작은 조사창이나 반복 조사가 원인이면 small_window_passes, 광고나 기대, 면도와 비교하면 longer_than_expected, 자주 오래 해야 하는 일정이면 demanding_schedule | "Time consuming treatments." (R2T3HFTC3IYYEJ); "This takes forever to do a treatment." (R217CA2CSB1IWD) | 26 |
| large_area_slow | 다리나 몸 전체 같은 넓은 부위가 오래 걸림 | Large areas take too long | 다리, 몸 전체, 가슴과 등처럼 넓은 부위를 하는 데 오래 걸린다, 몇 시간 걸린다, 오래 걸려 다리는 포기했다는 말(원인은 말하지 않음) | 작은 조사창이나 여러 번 덧대야 해서라는 원인을 말하면 small_window_passes, 발광 간격 때문이라고 하면 slow_flash, 부위 언급 없이 오래 걸린다는 말은 long_session | "It took me an hour and a half to do both legs plus bikini li" (R16RHLDXFP7HCJ); "the device takes quite a while to treat larger areas like th" (RI2SISRQKM0M2) | 14 |
| slow_flash | 발광 간격이 길거나 기기가 느림 | Slow flash rate or recharge wait | 발광 속도가 느리다, 쏘고 나서 다음 발광까지 몇 초 기다려야 한다, 다시 데워지거나 식기를 기다려야 한다, 자동 모드가 빠르지 않다, 기기 자체가 느리다(slow, lenta) | 조사창 크기나 반복 조사가 원인이면 small_window_passes, 원인 없이 시술이 오래 걸린다는 말은 long_session | "the flashing speed is slow" (R2ZW83BMFS2C92); "It takes forever to reheat in between each time push the but" (R3SYQQVFXZOBU4) | 10 |
| small_window_passes | 작은 조사창이나 반복 조사 때문에 오래 걸림 | Small window or repeat passes slow it down | 헤드나 조사창, 기기가 작아 오래 걸린다, 한 곳을 두세 번 덧대야 한다, 굴곡진 부위는 천천히 조심스럽게 지나가야 한다 | 발광 사이 대기 시간은 slow_flash(둘 다 말하면 두 라벨), 원인 없이 넓은 부위가 오래 걸린다는 말은 large_area_slow, 큰 헤드가 있어야 한다는 요구만 있으면 이 주제가 아님(design) | "el cabezal pequeño hace que la depilación de zonas grandes s" (RXBX1IOM03910); "time consuming especially on large areas like legs since you" (RKY1PUP3AY62W) | 6 |
| demanding_schedule | 자주, 오래 지켜야 하는 일정이 부담 | Demanding treatment schedule | 이틀마다, 주 2~3회, 매일, 몇 달에서 1년, 평생 매주 해야 한다는 부담, 일정을 따를 시간이 없다, 계속 챙기기 힘들다, 세션이 많이 필요하다 | 한 번 시술 시간만 말하면 long_session이나 large_area_slow, 효과가 보이기까지의 기간 자체나 꾸준함을 효과 조건으로만 말하면 이 주제가 아님(hair_reduction) | "Having to do this 2 times a week for 5 months" (R2FA3ODX0DHYD8); "It's definitely a time investment to have to use this every " (R2R2920RW4FYD8) | 19 |
| longer_than_expected | 광고나 기대보다 오래 걸림 | Takes longer than advertised or expected | 광고한 10분보다 오래 걸린다, 예상보다 오래 걸린다, 면도나 다른 기기보다 오래 걸리거나 시간이 줄지 않았다 | 비교 대상 없이 오래 걸린다는 말은 long_session, 효과가 광고보다 늦게 나온다는 말은 이 주제가 아님(hair_reduction) | "it takes way longer than 10 mins like advertised" (R3DS39VF4SYRUU); "much more time consuming than they advertise" (R3TBTATZWLRUQN) | 6 |
| other | 기타 | Other | 위 라벨에 들지 않는 것 | - | - | 2 |

메모: "This increases the amount of time", "drag my session from minutes to hours"처럼 원인이 인용 밖(앞 문장)에 있어 보이는 말은 원인을 알 수 없어 long_session으로 셌다. "se necesitan muchas sesiones"는 일정 부담으로 셌지만 효과 기간(hair_reduction)과 경계가 가깝다.

### 긍정 이슈(긍정, 혼합 인용): 인용 47개, 표본 47개

| id | 이름 | 영어 이름 | 포함 | 제외 | 대표 인용 | 어림 개수 |
|---|---|---|---|---|---|---|
| quick_session | 시술이 빠르고 오래 안 걸림 | Quick sessions | 빠르다, 금방 끝난다, 오래 안 걸린다, 시간이 많이 들지 않는다, 한 번에 2분, 5분, 10분이면 된다(부위 언급 없거나 겨드랑이처럼 작은 부위) | 다리나 몸 전체를 짧게 끝낸다는 말은 large_area_quick, 발광 속도나 자동 모드, 이중 발광 덕분이라고 하면 fast_flash_mode, 주당 횟수나 주 단위 시간은 light_schedule | "a full session only takes about 10 minutes" (R3I3HAIAL07C08); "the process is quick and convenient" (R6HJL2H1R3J9U) | 28 |
| fast_flash_mode | 발광이 빠르거나 자동 모드, 이중 발광으로 빨라짐 | Fast flash or auto and double flash modes | 발광 주기가 빠르다, 자동 모드(Auto-Glide)가 빠르다, 이중 발광 덕에 빨리 끝난다 | 원인 없이 빠르다는 말은 quick_session, 자동 모드의 조작 편리함(버튼을 안 눌러도 된다)은 이 주제가 아님(ease_of_use) | "The double flash of the Ulike makes the process pretty quick" (R371G2D4TFMWP7); "Treatment sessions are super fast with the Auto-Glide mode" (R45A68G8D9H22) | 5 |
| large_area_quick | 다리나 몸 전체도 짧게 끝남 | Large areas done quickly | 다리, 종아리, 머리부터 발끝까지 같은 넓은 부위를 몇 분에서 30분 안에 끝낸다, 다리도 비교적 빨리 된다 | 겨드랑이처럼 작은 부위나 부위 언급 없이 빠르다는 말은 quick_session | "It’s quick to use, and I can treat larger areas like my legs" (R1UMNQC5X9R7VI); "it only takes me about 10 minutes total to do the lower sect" (R2IW5AKUW2LVDH) | 4 |
| light_schedule | 일정이 가볍고 생활에 맞추기 쉬움 | Light, easy-to-keep schedule | 주 2회, 몇 주에 한 번만 하면 된다, 일주일에 20분 이하, 주간 루틴에 넣기 쉽다, 일정을 지키기 쉬웠다 | 한 번 시술이 빠르다는 말만 있으면 quick_session, 효과가 몇 주 만에 보였다는 말은 이 주제가 아님(hair_reduction) | "you only have to use it 2 times a week to start seeing resul" (R17Z3G31WY4J6A); "I also love that you only need to use it every couple of wee" (R2D5BIKVEMGFGD) | 6 |
| time_worth_it | 시간이 들지만 견딜 만하거나 그만한 가치가 있음 | Time is acceptable or worth it | 시간이 좀 들고 지루하지만 나쁘지 않다, 효과가 있으니 발광 간격도 신경 쓰이지 않는다, 시간이 들어도 결과가 그만한 가치가 있다(혼합 인용의 칭찬 부분) | 시간이 오래 걸린다는 불만만 있으면 negative 쪽 라벨, 빠르다는 칭찬은 quick_session | "It is a little time consuming for the results have been wort" (R380XCNEXZQ8JX); "It will take a little time and feel tedious, but it isn't to" (R1KWW1ZMRJ0A1O) | 3 |
| other | 기타 | Other | 위 라벨에 들지 않는 것 | - | - | 2 |

메모: "ahorra mucho tiempo y dinero", "It saves me time and salon trips"처럼 살롱이나 면도 대비 시간을 아낀다는 말은 2개(5% 미만)라 기타로 셌다.

## 피부색과 털 색 적합성 (skin_hair_suitability)

### 부정 이슈(부정, 혼합 인용): 인용 65개, 표본 65개

| id | 이름 | 영어 이름 | 포함 | 제외 | 대표 인용 | 어림 개수 |
|---|---|---|---|---|---|---|
| dark_skin_tone | 어두운 피부색에는 못 씀 | Not for darker skin tones | 사람의 피부색 자체(태닝, 갈색, 올리브, 어두운 피부, 멜라닌)가 어둡거나 중간 톤이라 기기가 안 되거나, 센서가 피부색을 너무 어둡다고 읽어 못 쓴다는 말. 밝은 피부에만 맞는다는 말 포함 | 피부색은 대상인데 비키니, 겨드랑이처럼 몸의 일부 어두운 부위에서만 막히거나 안 듣는다는 말은 dark_body_areas | "does not work on tanned or darker skin" (R29W8ON8A13KN7); "This item is not for dark skinned women." (R1T9EUE1DCTJRE) | 20 |
| dark_body_areas | 비키니나 겨드랑이처럼 어두운 부위에서 안 됨 | Blocked or weak on darker body areas | 비키니, 겨드랑이, 은밀한 부위, 허벅지 안쪽처럼 몸에서 색이 더 짙은 부위에서 센서가 발광을 막거나, 효과가 없거나 더 오래 걸린다는 말 | 사람의 피부색 전체가 어두워 못 쓴다는 말은 dark_skin_tone. 피부색 언급 없이 부위마다 효과가 다르다는 말은 이 주제가 아님(hair_reduction) | "the sensor would never light up in my bikini area" (RSE01I2TC1E64); "it doesn't work well on areas where my skin is too dark" (R3TZKM2YDQ6CJZ) | 11 |
| light_fine_hair | 금발이나 옅은 털, 가는 솜털에는 안 들음 | Weak on blonde, light or fine hair | 금발, 옅은 갈색, 붉은 갈색처럼 옅은 털이나 가는 솜털에는 효과가 없다, 진한 털이 아니면 사지 마라, 털이 가늘면 살 필요가 없다는 말 | 흰 털, 회색 털은 gray_white_hair. 굵은 털에 안 듣는다는 말은 thick_coarse_hair | "Does not work for blonde or light brown hair." (R1BICTURUAEEBJ); "does not help with light colored hair" (R2W2I33M3721W2) | 11 |
| gray_white_hair | 흰 털이나 회색 털에는 안 들음 | Does not work on gray or white hair | 흰 털, 회색 털, 나이 들며 생긴 흰 수염 같은 털에는 효과가 없다는 말 | 금발이나 옅은 색 털만 말하면 light_fine_hair(금발과 회색을 함께 말하면 두 라벨 모두) | "Doesn’t work on white hair." (REG0KPBJPIX8G); "Does not work on gray whisker hairs of an aging woman." (R3NZXB8W5SMK1Z) | 6 |
| thick_coarse_hair | 굵고 억센 털에는 덜 들음 | Weak on thick or coarse hair | 굵은 털, 억센 털, 질긴 털에는 효과가 없거나 느리다, 굵은 털이면 다른 제품을 찾으라는 말 | 가는 털이라 살 필요가 없다는 말은 light_fine_hair. 털 굵기 언급 없이 효과가 없다는 말은 이 주제가 아님(hair_reduction) | "Doesn't work good on thicker hairs" (R9TSKT8GTJAHE); "Do not buy for coarser hair." (R18W4UM9JN0TUP) | 13 |
| other | 기타 | Other | 위 라벨에 들지 않는 것 | - | - | 6 |

메모: 센서가 발광을 막는다는 말은 따로 라벨을 두지 않고 피부색 전체(dark_skin_tone)인지 몸의 어두운 부위(dark_body_areas)인지로 나눴습니다. 기타에는 맞는 유형인데도 안 됐다는 배경 언급(R2DVO9V4IS6M9K, R1FZ8Q4JKOG31O)처럼 스키마상 hair_reduction에 가까운 인용과, 무엇이 문제인지 불분명한 인용(R3VS4576GY70LY, R18UY4HW9LQGON, R1H1B6Y8QUCDUM, R2T2JDN7PVVK4G)이 들어 있습니다.

### 긍정 이슈(긍정, 혼합 인용): 인용 14개, 표본 0개

인용이 20개 미만이거나 라벨이 없어 기타만 둡니다.

## 구성품과 보관 케이스 (accessories)

### 부정 이슈(부정, 혼합 인용): 인용 20개, 표본 20개

| id | 이름 | 영어 이름 | 포함 | 제외 | 대표 인용 | 어림 개수 |
|---|---|---|---|---|---|---|
| goggles_missing | 보안경이 없거나 빠져 옴 | Goggles not included or missing | 보안경(glasses, goggles, lentes, gafas)이 구성에 없거나 받은 상자에 빠져 있었다, 따로 사야 했다, 들어 있어야 한다는 말 | 들어 있는 보안경이 잘 안 맞거나 빛을 못 막는다는 말은 goggles_poor_fit, 보관 케이스가 없다는 말은 case_lacking | "You have to purchase your goggle separately." (R300NO6N06MI3R); "faltaron los lentes" (R5SZEZK6R7OAM) | 11 |
| goggles_poor_fit | 보안경 착용감이나 품질 불만 | Goggles fit poorly or protect poorly | 들어 있는 보안경이 안경 위에 안 맞는다, 허술하다, 빛을 잘 막지 못한다는 말 | 보안경이 아예 없거나 빠져 왔다는 말은 goggles_missing, 섬광이 눈에 해롭다는 안전 우려 자체는 safety 주제 | "the safety glasses that come with this product are not well " (R30ODGD4OXKWUU); "Glasses didn’t offer much help against laser light" (R2V5RNF586IBAW) | 4 |
| case_lacking | 보관 케이스가 없거나 아쉬움 | Storage case missing or unappealing | 보관 케이스나 파우치가 없어 아쉽다, 있었으면 좋겠다, 케이스 색이나 모양이 마음에 들지 않는다는 말 | 제품 상자(배송 온 상자)의 상태나 외관은 packaging 주제, 보안경이나 면도기가 빠진 것은 goggles_missing 또는 기타 | "Me encantó! Me ubuera gustado tener un estuche :D" (R1YD46GOLUQL4B); "the case it came with is a pinkish/coral color, which is a l" (RJ70XYUA71OQC) | 3 |
| other | 기타 | Other | 위 라벨에 들지 않는 것 | - | - | 2 |

메모: 면도기가 빠졌다는 말은 2개(R34MFAS0SGKRBD, R2LT3QNM94WMEI의 보안경과 함께 빠진 경우)뿐이라 라벨로 두지 않음. R3LDIX6PWLVIRZ("said was included")는 스키마상 설명과 다른 구성이라 trust에 가까움. 보안경이 원래 구성에 없는 것(B07WYY6KKC)과 받은 상자에서 빠진 것(B0CV3ZJ2PN)은 인용만으로 가르기 어려워 goggles_missing 하나로 합침. R2QV46JTGZRGAW, R2IBA63SK8LQIJ는 인용에 불만 내용이 거의 없거나 무엇이 문제인지 없어 기타.

### 긍정 이슈(긍정, 혼합 인용): 인용 41개, 표본 41개

| id | 이름 | 영어 이름 | 포함 | 제외 | 대표 인용 | 어림 개수 |
|---|---|---|---|---|---|---|
| case_nice | 보관 케이스나 파우치가 좋음 | Nice storage case or pouch | 함께 오는 보관 케이스, 파우치, 가방이 예쁘다, 튼튼하다, 고급스럽다, 정리가 잘 된다는 말 | 필요한 것이 다 들어 있다는 구성 전체 평은 complete_kit, 제품 상자의 포장 상태는 packaging 주제 | "It comes in a nice, heavy duty case with specific cavities f" (RDP6VFH1J365D); "the storage case is beautiful" (R4BPUJN9EOB08) | 22 |
| goggles_included | 보안경이 들어 있음 | Protective goggles included | 보안경이 함께 들어 있어 좋다, 안경 위에도 맞는다, 착용감이 편하다는 말 | 보안경을 여러 구성품 중 하나로 나열하며 다 들어 있다고만 하면 complete_kit | "love that it comes with the sunglasses to protect your eyes" (R3INSXQHFCICQI); "the glasses fit over my prescription ones so it’s easy to pr" (RJ86SS9SV6XB0) | 9 |
| complete_kit | 필요한 구성품이 다 들어 있음 | Complete kit with everything needed | 필요한 것이 다 들어 있다, 완전한 구성이다, 빠진 것 없이 왔다(viene con todos sus artículos)는 말이나 구성품을 세 가지 이상 나열하며 갖춰졌다고 하는 말 | 케이스 하나의 모양이나 튼튼함을 칭찬하면 case_nice, 보안경 하나를 짚어 칭찬하면 goggles_included | "comes with everything you need to get started" (R9H5CZX785L9U); "includes everything—charger, goggles, blades, manual" (R2TNKBB9DW6MXY) | 9 |
| other | 기타 | Other | 위 라벨에 들지 않는 것 | - | - | 2 |

메모: 면도기 포함을 칭찬하는 말은 케이스나 보안경과 함께 나오는 경우가 대부분이라 따로 두지 않음. R2IBA63SK8LQIJ, R1YD46GOLUQL4B(혼합)는 인용에 구성품 칭찬이 없어 기타. B0G39WBP1S 인용이 18개로 표본의 절반 가까이를 차지함.

