# 세부 이슈 목록 초안

상태: PASS. 주제마다 issue-labeler가 표본 인용(주제와 방향마다 최대 150개, ASIN과 별점 묶음을 고르게)을 읽고 제안한 목록입니다. 어림 개수는 표본에서 센 값이라 리포트에 쓰지 않습니다. 전체 만족도는 리뷰 단위 총평이라 나누지 않습니다.

## 가격 대비 가치 (price_value)

### 부정 이슈(부정, 혼합 인용): 인용 71개, 표본 71개

| id | 이름 | 영어 이름 | 포함 | 제외 | 대표 인용 | 어림 개수 |
|---|---|---|---|---|---|---|
| too_expensive | 그냥 비쌈 | Too expensive | 용량이나 성능 같은 비교 대상 없이 가격 수준 자체가 비싸다, 조금 비싸다, 더 쌌으면 좋겠다는 말("Overpriced", "Pricey", "tan caro") | 병 크기나 용량에 비해 비싸다는 말은 small_for_price, 받은 제품이 값만큼 못하다는 말은 not_worth_price, 지속력에 비해 비싸다는 말은 not_lasting_for_price | "Overpriced" (R3OG30U20R3UNI); "very expensive though" (R1WLKECRSCRWPW) | 24 |
| small_for_price | 용량에 비해 비쌈 | Too small for the price | 병이 작다, 몇 ml밖에 안 된다는 말과 함께 그 값이 비싸다고 하는 말("tiny bottle for the price", "30 ml por este precio") | 가격 말 없이 병이 작다는 말은 bottle_design(이 주제 아님), 용량 언급 없이 비싸다는 말은 too_expensive | "Was way too expensive for the tiny bottle." (R2M38B7M76GHVM); "Demasiado caro, 30 ml por este precio" (R2RKARC8NRGUCQ) | 18 |
| not_worth_price | 값만큼 못함 | Not worth the price | 받은 제품(품질, 기대, 전반)이 낸 값에 못 미친다, 가격 대비 별로다, 할인해야 살 만하다는 말("Not worth the cost", "Preis-Leistung geht so", "$116.00 for NOTHING") | 못 미치는 이유가 지속력이면 not_lasting_for_price, 용량이면 small_for_price, 가격 수준만 말하면 too_expensive | "Not worth the cost" (R9ZEWAM020WG9); "a little basic in my opinion considering the price" (R28CUG81AXYYHI) | 17 |
| not_lasting_for_price | 지속력에 비해 비쌈 | Too expensive for how short it lasts | 이 값이면 더 오래가야 한다, 비싼데 금방 날아간다처럼 가격과 지속력을 함께 묶어 말하는 부분 | 가격 말 없이 금방 날아간다는 말은 longevity_projection(이 주제 아님), 이유 없는 값어치 불만은 not_worth_price | "Very expensive for it not to last" (RPK76O08CXYUS); "you spend $50 and you only smell good for an hour or two" (R26U67LD084EK3) | 4 |
| other | 기타 | Other | 위 라벨에 들지 않는 것 | - | - | 8 |

메모: 기타에는 가격 인상("The price was almost doubled", 같은 값에 양이 줄었다, 3개), 다른 매장이나 다른 제품이 더 싸다(Walmart, 정규 매장, Lattafa, 3개), "price was too good to be true"(가짜 의심 성격, trust 쪽), "$37 for 2 uses"(용량인지 분사 문제인지 불분명)가 있음. 가격 인상은 5% 미만이라 라벨로 만들지 않았지만 다음 회차에 늘면 따로 볼 만함.

### 긍정 이슈(긍정, 혼합 인용): 인용 83개, 표본 83개

| id | 이름 | 영어 이름 | 포함 | 제외 | 대표 인용 | 어림 개수 |
|---|---|---|---|---|---|---|
| good_price | 가격이 좋음 | Good or affordable price | 가격 자체가 싸다, 적당하다, 좋은 가격이다, 좋은 딜이다는 말("Great price", "Very affordable", "Buen precio", "only $30") | 가격에 비해 제품이 좋다, 값어치를 한다는 말은 good_value, 용량 대비 값은 size_for_price, 원조 향수나 다른 매장보다 싸다는 비교는 cheaper_than_alternatives | "Very affordable" (R553UQ8LUZP0O); "Great price." (RZL9EL6VC8P7Y) | 42 |
| good_value | 값어치를 함 | Worth the money | 낸 값에 비해 제품(품질, 향, 세기, 전반)이 좋다, 돈값을 한다는 말("Good value for the money", "worth my money", "for the price it's a decent product", "Bom custo benefício") | 가격 수준만 칭찬하면 good_price, 용량 대비 값이면 size_for_price | "Good value for the money" (R22KP4UHOX1JCN); "For the price point, that's genuinely impressive." (RI6ECRUKWAGQU) | 23 |
| cheaper_than_alternatives | 원조나 다른 곳보다 쌈 | Cheaper than the original or other stores | 원조 향수(듀프 대상)나 다른 매장(Macy's 등)보다 훨씬 싸다는 비교("at a fraction of the cost", "under $40 vs $100 plus") | 비교 대상 없이 싸다는 말은 good_price | "the under $40 vs $100 plus was to tempting" (R1ZD5J2BF3RTMC); "looks real.. not sure why Macy's is more expensive" (R3T4C0OHINQFYF) | 7 |
| size_for_price | 용량 대비 값이 좋음 | Good size for the price | 병 크기나 용량에 비해 값이 좋다는 말("Great size for the price", "Big size for an affordable price") | 가격 말 없이 병 크기가 좋다는 말은 bottle_design(이 주제 아님), 용량 언급 없는 가격 칭찬은 good_price | "it was a great price for the size" (R297F9WD8P3TY9); "Big size for an affordable price" (R3R6ZPYXB9A5CA) | 5 |
| pricey_but_acceptable | 비싸지만 감수할 만함 | Pricey but acceptable | 비싸다고 인정하면서 조금 비싼 정도다, 어디서나 그 값이다, 가끔은 써도 된다처럼 받아들이는 말(주로 mixed 인용의 받아들이는 부분) | 받아들인다는 말 없이 비싸다고만 하면 부정 방향 too_expensive, 비싸지만 제품이 값을 한다고 하면 good_value | "Pricey, but not terribly!" (R3RMC5DQ1R25C9); "Price for this item is high but it's high in every store." (R27AB5RGDGPQDQ) | 5 |
| other | 기타 | Other | 위 라벨에 들지 않는 것 | - | - | 1 |

메모: good_price와 good_value 경계는 가격 수준 자체를 칭찬하는지("Great Price for this product!"는 good_price), 제품이 값을 한다고 하는지("Great product for the price"는 good_value)로 나눔. 기타 1개는 "I can't exactly say they're worth the price"(mixed지만 칭찬 부분이 드러나지 않음). 부정 표본과 긍정 표본에 같은 mixed 인용 9개가 함께 들어 있음.

## 브랜드 경험 (brand_experience)

### 부정 이슈(부정, 혼합 인용): 인용 83개, 표본 83개

| id | 이름 | 영어 이름 | 포함 | 제외 | 대표 인용 | 어림 개수 |
|---|---|---|---|---|---|---|
| no_repurchase | 다시 사지 않겠다 | Will not repurchase | 리뷰어 본인이 이 제품을 다시 사지 않겠다, 다시 살지 망설인다는 말(이 향은 다시 안 산다 포함). "won't buy again", "Não compraria novamente", "dudo mucho volverlo adquirir", "次は買わない" | 남에게 사지 말라, 추천하지 않는다고 권하는 말은 advise_against(본인 재구매 거부와 비추천이 한 인용에 같이 있으면 advise_against). 브랜드 전체나 회사와 거래를 끊겠다는 말은 기타 | "will not purchase again" (R1GC4SWKII954O); "Would not purchase again" (RD7OK6GNPNWWW) | 26 |
| advise_against | 비추천, 사지 말라 | Advises others against buying | 다른 사람에게 추천하지 않는다, 사지 말라고 권하는 말. "Don't recommend", "Do not buy", "no lo compren", "Não recomendo", "keine Kaufempfehlung", 대신 다른 향이나 다른 제품을 사라는 권유("get a different scent", "buy the YSL version instead") | 본인만 다시 사지 않겠다는 말은 no_repurchase. 이 판매자에게서 사지 말라는 말은 주제 밖(trust) | "Don't recommend" (R2ZQPSM4V7AB2P); "Do not buy" (RU1F1TZKEIBMI) | 50 |
| other | 기타 | Other | 위 라벨에 들지 않는 것 | - | - | 7 |

메모: 기타 7개는 브랜드나 회사 전체와 끊겠다는 말 5개(R3SY7CRYQGRIJR, RE2KNU3LPS61F, R3DSZM9BOJ9YFF, R3OJWNUWQ3ZJOB, R1TQHZSI3LSOPN)와 브랜드의 다른 향을 써 보고 싶지만 망설인다는 혼합 2개. 브랜드 이탈은 확실한 것이 3개(약 4%)로 5%에 못 미쳐 라벨로 만들지 않았다. "their products", "this particular company"는 판매자를 가리킬 수도 있어(그러면 trust) 원문 확인이 필요하고, "I hate them"은 무엇을 가리키는지 인용만으로는 알 수 없다. "Dudo en volverlo a comprar por aquí"(RYM1IVFLQVFSK)는 '여기서' 다시 사기를 망설인다는 말이라 판매자 이야기에 가깝지만 재구매 표현이라 no_repurchase로 셌다. advise_against는 "추천 안 함"과 "사지 마라"를 합친 것이다. 표현만 다르고 내용이 같아서 합쳤고, 나눠 보고 싶으면 각각 어림 25개 정도.

### 긍정 이슈(긍정, 혼합 인용): 인용 159개, 표본 150개

| id | 이름 | 영어 이름 | 포함 | 제외 | 대표 인용 | 어림 개수 |
|---|---|---|---|---|---|---|
| recommends | 추천, 사라고 권함 | Recommends to others | 남에게 추천한다, 사 보라고 권하는 말. "highly recommend", "lo recomiendo", "Buy it!!", "Must buy", "give this one a try", "recommended it to several friends" | 본인이 다시 사겠다는 말은 will_repurchase(추천과 재구매가 한 인용에 같이 있으면 recommends). 브랜드 제품 전반을 추천하는 말은 brand_affinity | "would definitely recommend" (R1M2HDZ8ML591D); "Buy it" (R2DR2FD2ZM7NB3) | 35 |
| will_repurchase | 다시 사겠다 | Will repurchase | 앞으로 다시 사겠다, 곧 또 산다, 예비로 하나 더 주문했다, 늘 갖춰 두겠다, 계속 쓰겠다는 미래 의향. "Will repurchase again.", "I have already ordered a back up.", "Will always have on hand", "I'll continue to wear it" | 이미 여러 병 샀다, 수년째 쓴다는 과거 행동은 repeat_long_time_user(과거와 미래가 같이 있으면 repeat_long_time_user). 같은 브랜드의 다른 향을 사겠다는 말은 brand_affinity | "would definitely buy it again" (R251EFH6XL865Y); "I have already ordered a back up." (R3KIT5CR5UKBES) | 23 |
| repeat_long_time_user | 여러 병째, 수년째 애용 | Repeat or long-time user | 이미 여러 번 샀다, 두 번째 병이다, 늘 산다, 몇 년째(수십 년째) 써 왔다는 과거 행동. 가족이 오래 써 왔다는 말 포함. "On My second bottle.", "Lo he comprado varias veces", "Eu uso esse perfume há muitos anos ja", "My wife has used this for 50 years" | 기간이나 횟수 없이 최애, 시그니처, 매일 쓴다는 말만 있으면 favorite_signature. 앞으로 사겠다는 말만 있으면 will_repurchase | "I have went through many bottles" (RYCJDMO5YJZ3F); "On My second bottle." (R543VC5C5UZ9M) | 25 |
| favorite_signature | 최애, 시그니처 향 | Favorite or signature scent | 내(가족의) 최애 향수다, 시그니처 향이다, 매일이나 자주 쓰는 주력 향이다(go-to, every day, only perfume I will wear, staple in my purse). "My favorite perfume!", "Es mi perfume favorito", "Its my signature scent" | 몇 년째, 여러 병째처럼 기간이나 구매 횟수가 같이 있으면 repeat_long_time_user. 브랜드를 좋아한다는 말은 brand_affinity | "This is my favorite perfume" (R2IZYYF40BLYCN); "Its my signature scent" (R1CW6KMXZ5DMK7) | 49 |
| brand_affinity | 브랜드 호감, 다른 향도 좋다 | Brand affinity | 브랜드 자체를 좋아한다, 브랜드의 다른 향도 좋다, 다른 향도 써 보겠다, 이 브랜드에서 또 사겠다는 말(이 향은 별로라는 혼합 포함). "Love this brand so much!!!", "Love Dossier fragrances.", "Will try other blends from this maker", "Dossier has themselves a new fan!" | 이 제품을 두고 한 추천, 재구매, 애용은 recommends, will_repurchase, repeat_long_time_user, favorite_signature(브랜드명이 있어도 이 제품을 가리키면 그쪽). 브랜드와 이 제품을 함께 칭찬하면 brand_affinity | "Love this brand so much!!!" (RC124KI4VXNEV); "All my other fragrances from Dossier are amazing" (R51AHLN091QG2) | 17 |
| other | 기타 | Other | 위 라벨에 들지 않는 것 | - | - | 1 |

메모: 기타 1개는 "I wear this in memory of my husband."(R250YQNVQ4FP3G, 추억 때문에 쓴다는 정서적 애착). favorite_signature와 repeat_long_time_user는 기간이나 횟수를 말했는지로 가른다("an old favorite"처럼 오래됐음을 암시만 하면 favorite_signature, "My favorite, have been using it for years"는 repeat_long_time_user). brand_affinity에는 같은 브랜드의 다른 향을 좋아한다는 말이 들어 있다(스키마 공통 규칙상 brand_experience). 망설임이 섞인 혼합 2개(R3HKWF5VN6K5KG, R3TKPOTESXG4F8)도 칭찬 부분으로 여기 셌다.

## 신뢰 (trust)

### 부정 이슈(부정, 혼합 인용): 인용 172개, 표본 150개

| id | 이름 | 영어 이름 | 포함 | 제외 | 대표 인용 | 어림 개수 |
|---|---|---|---|---|---|---|
| fake_asserted | 가짜라고 단정 | Asserted fake | 근거나 망설임 없이 가짜, 정품 아님, 사기, 복제품이라고 잘라 말함("Fake", "No es original", "Scam", "knock off", "Not Eternity") | maybe, not sure, creo, sospecho, dúvida처럼 망설이며 말하면 authenticity_doubt. 향(smell, scent, fragrance, olor, cheiro, Duft)이 다르다고 비교하면 differs_from_genuine. 물 탔다, 손댔다는 말은 diluted_or_tampered | "knew instantly this was a fake" (R15HIDYPL5720F); "No es original" (RRQTBBAMWACKD) | 35 |
| authenticity_doubt | 정품인지 의심 | Doubts authenticity | 정품인지 확신하지 못하고 의심함(maybe, may not, not sure, I think, I don't believe, seems, creo, sospecho, parece, dúvida, Suspicious) | 망설임 없이 가짜라고 단정하면 fake_asserted. 의심의 근거로 향이나 세기 비교, 희석을 말하면 그 라벨(differs_from_genuine, weaker_than_genuine, diluted_or_tampered) | "May not be the real thing" (R1YDXT5P13GTSC); "I'm questioning the authenticity of the product." (R2XAQXLR0QWVH5) | 31 |
| differs_from_genuine | 정품이나 늘 쓰던 것과 향이 다름 | Smells different from genuine | 정품, 매장에서 맡거나 산 것, 갖고 있는 병, 늘 사던 같은 제품과 향이나 제품이 다르다(무엇이 다른지 말이 없는 "IT IS NOT THE SAME."도 포함) | 세기나 지속력이 다르다는 비교는 weaker_than_genuine. 예전보다 바뀌었다, 제조법이 바뀌었다처럼 시간에 따른 변화는 formula_changed. 향 언급 없이 정품이 아니라고만 하면 fake_asserted | "It is not the same as what I smelled in the store." (R18BLPFIGWE423); "I have the big bottle and this one smells nothing like it" (R1FNK1M1D36AK9) | 29 |
| formula_changed | 예전과 달라짐(제조법 변경 의심) | Changed from before (reformulation) | 제품이 예전과 달라졌다, 제조사가 제조법이나 성분을 바꾼 것 같다(formula, ingredients, used to be, anymore, now, of the past, 20 yrs ago, hace unos años) | 세기나 지속력이 예전보다 약해졌다는 말은 weaker_than_genuine. 시간 비교 없이 정품, 매장 것, 갖고 있는 병과 다르다는 말은 differs_from_genuine | "they've changed the formula" (R29AJ7AM4NWRLK); "Not as it used to be." (R1ISNSZNBCFYTZ) | 16 |
| diluted_or_tampered | 희석되거나 손댄 것 같음 | Diluted or tampered | 물이나 알코올을 탔다, 희석됐다, 누가 열어서 손댔다, 변조됐다("watered down", "Mostly water", "tampered", "adulterado", "薄めている") | 희석 의심 없이 정품보다 약하다, 금방 날아간다는 비교는 weaker_than_genuine. 오래돼 변질된 것 같다는 말만 있으면 quality(이 주제 아님) | "Watered down version" (R31TRJEEWBZVEB); "someone may have opened or tampered with the perfume before " (R3U8G2B77HUP9O) | 14 |
| weaker_than_genuine | 정품이나 예전 것보다 약하고 짧음 | Weaker than genuine or before | 매장(Walmart, Macy's, Sephora, Target) 제품, 예전에 산 같은 제품, 갖고 있는 같은 향보다 향이 약하거나 지속력이 짧다, 세기가 바뀌었다 | 비교 대상 없이 약하다, 금방 날아간다는 말은 longevity_projection(이 주제 아님). 물이나 알코올을 탔다는 말은 diluted_or_tampered | "Walmart perfume is way more stronger then Amazon" (R24ZECLLTT3C7B); "The smell is so faint compared to the exact bottle I bought " (R1EOXLERGBKDOC) | 13 |
| other | 기타 | Other | 위 라벨에 들지 않는 것 | - | - | 12 |

메모: 기타 12개 중 이 판매자에게서 사지 마라(어림 5개), 병 색이나 겉모양이 다르다(어림 3개), 원산지 표기 불만(어림 2개)은 5% 미만이라 라벨로 만들지 않음. "fake, don't buy from here"처럼 판매자 비추천에 가짜 단정이 붙으면 fake_asserted로 셈. R1HVR0C5JIW50O("seem like the real stuff")는 negative로 태깅됐지만 내용은 정품 같다는 말이라 태그 감성 확인이 필요하고, R2JMS6R5PPXRO6("the scent is off")은 변질(quality)일 수도 있어 기타로 둠.

### 긍정 이슈(긍정, 혼합 인용): 인용 23개, 표본 23개

| id | 이름 | 영어 이름 | 포함 | 제외 | 대표 인용 | 어림 개수 |
|---|---|---|---|---|---|---|
| authentic_confirmed | 정품이다, 정품 같다 | Authentic | 정품이다, 진짜다, 가짜가 아니다, 정품 같아 보인다("It is the real deal.", "es original", "no knock off", "looks real", "Authentic looking bottle") | 원래 제품, 매장 제품, 기억하는 향과 같다고 비교하면 same_as_original | "It is the real deal." (R3GH6I54IBDV3J); "this is definitely not fake" (R3UD73SOIQ7BG2) | 17 |
| same_as_original | 원래 것, 매장 것과 같음 | Same as original or store | 원래 제품, 매장(소매점, 미국 매장) 제품, 예전에 쓰던 것과 향이나 제품이 같다("Same as original", "smells as I remember", "Same as retail stores") | 비교 없이 정품이다, 정품 같다고만 하면 authentic_confirmed | "Same as original" (R1U2ZZ3REP6M9Q); "Same as retail stores" (R1C9LFWKV03B2T) | 6 |
| other | 기타 | Other | 위 라벨에 들지 않는 것 | - | - | 0 |

메모: 혼합 인용 R18H8U3BEZGOZA("todo parece ser original, solo la duración es lo que me extraño")는 칭찬 부분으로 authentic_confirmed, 불만 부분(지속력이 이상함)으로 부정 쪽 weaker_than_genuine에 셈.

## 배송 (shipping)

### 부정 이슈(부정, 혼합 인용): 인용 65개, 표본 65개

| id | 이름 | 영어 이름 | 포함 | 제외 | 대표 인용 | 어림 개수 |
|---|---|---|---|---|---|---|
| arrived_broken | 깨지거나 부서져 도착 | Arrived broken or damaged | 받았을 때 병, 뚜껑, 분사구가 깨지거나 금 가거나 부러져 있었다, 상품이나 소포가 손상돼 왔다는 말("Broken", "Came damaged", "Llegó roto"). 시점 없는 "Broken"도 여기 | 새거나 흘렀다는 말이 함께 있으면 leaked_in_transit. 겉 부서짐 없이 분사기가 작동하지 않는 것은 quality(이 주제 아님). 겉상자만 찌그러진 것은 packaging | "The bottle was delivered cracked." (RYXW6V35RZ6TV); "Llegó roto" (R3OF64V1YOE64B) | 23 |
| leaked_in_transit | 새거나 흘러서 도착 | Leaked or spilled in transit | 받았을 때 향수가 새고 있었다, 상자나 소포가 향수에 젖었다, 상자 안에 쏟아졌다는 말. 시점 없는 "Leaking"도 여기. 새서 양이 줄었다는 말, 깨져서 샌다는 말도 여기 | 샌 이야기 없이 양만 덜 들어 있으면 arrived_underfilled. 새는 말 없이 깨짐만 있으면 arrived_broken. 여행이나 들고 다닐 때 샌다는 말은 bottle_design(이 주제 아님) | "was leaking when I received it" (R3AOLDFQH1SQI9); "Casi la mitad del perfume se derramó en la caja." (R2JKQ4KZTJS527) | 21 |
| arrived_underfilled | 내용물이 덜 든 채 도착 | Arrived partly empty | 받았을 때 병이 반쯤 비었다, 거의 비었다, 일부(1/5, 1/4)가 없었다는 말 | 샜다, 흘렀다는 말이 함께 있으면 leaked_in_transit. 주문한 것보다 작은 용량의 병이 온 것은 wrong_or_opened_item | "bottle was half empty" (R95G0ZJBYOR7O); "my spray arrived with 1/5th of the product gone" (R19Q1I5RT9RW9D) | 6 |
| wrong_or_opened_item | 주문과 다른 상품이나 개봉된 상품 | Wrong item or opened/used item | 주문하지 않은 상품이나 다른 용량의 병이 왔다, 이미 열렸거나 쓰던 상품이 왔다는 말 | 가짜나 정품 의심이 근거로 붙으면 trust(이 주제 아님). 같은 제품인데 내용물만 덜 들었으면 arrived_underfilled | "Diesen Artikel habe ich nicht bestellt." (R29H861VW9PEE1); "I received an opened and used bottle" (R2K27HLM5BUOS7) | 6 |
| slow_delivery | 배송이 느림 | Slow or late delivery | 배송이 늦었다, 느렸다, 한참 만에 겨우 왔다는 말 | 배달 위치나 기사 처리 불만은 기타. 도착 상태 불만은 위 라벨들 | "Delivery was very slow." (R2O45DJB4MICJI); "llego tarde" (R35P17YBF43WOE) | 6 |
| other | 기타 | Other | 위 라벨에 들지 않는 것 | - | - | 3 |

메모: 깨짐과 누출이 같이 나오면 누출(leaked_in_transit)로 센다. 기타는 배달 위치와 기사 처리(문 밖 나무 뒤, 우편함에 쑤셔 넣음, 2개, 5% 미만이라 라벨 안 만듦)와 뜻이 애매한 "delivered without the product, being broken"(R1CAOA6U7EFP8O) 1개. 다른 상품과 개봉 상품은 각각 3개(5% 미만)라 한 라벨로 합침. 인용 41개가 B08FBQWRYC에서 나와 파손과 누출이 이 ASIN에 몰려 있음

### 긍정 이슈(긍정, 혼합 인용): 인용 26개, 표본 26개

| id | 이름 | 영어 이름 | 포함 | 제외 | 대표 인용 | 어림 개수 |
|---|---|---|---|---|---|---|
| fast_delivery | 빠르거나 제때 배송 | Fast or on-time delivery | 배송이 빨랐다, 제때 왔다, 예정보다 일찍 왔다는 말 | 도착 상태(멀쩡하다, 제대로 왔다)만 말하면 arrived_intact | "fast shipping" (R2LQGD37514J9F); "llegó un día antes de lo esperado" (R18H8U3BEZGOZA) | 15 |
| arrived_intact | 멀쩡하고 제대로 도착 | Arrived intact and as ordered | 깨지거나 새지 않고 좋은 상태로 왔다, 빠진 것 없이 주문대로 제대로 왔다, 판매자가 잘 보내 줬다는 말 | 속도만 말하면 fast_delivery. 정품 같다는 말은 trust(이 주제 아님). 상자 디자인이나 보호력 칭찬은 packaging(이 주제 아님) | "It arrived in great condition" (R2BTMJDX2GACW6); "Todo llegó perfecto sin falta de producto" (R3BCD96QKPFUIE) | 12 |
| other | 기타 | Other | 위 라벨에 들지 않는 것 | - | - | 1 |

메모: "Package came on time with no damage."(RFKZ7EJ1U4UYQ)와 "El producto llego bien y la mensajería entrego bien en la fecha acordada."(R14YS8XFVTOZTS)는 속도와 상태를 함께 칭찬해 두 라벨에 모두 셌다(approx_count 합이 표본 수보다 2 많음). 기타는 무엇이 좋았는지 없는 "Good delivery" 1개

## 고객 응대 (customer_service)

### 부정 이슈(부정, 혼합 인용): 인용 85개, 표본 85개

| id | 이름 | 영어 이름 | 포함 | 제외 | 대표 인용 | 어림 개수 |
|---|---|---|---|---|---|---|
| not_returnable | 반품·환불 불가 | Not returnable | 향수라서, 아마존 규정이나 위험물이라서, 반품 옵션이 없어서 반품이나 환불을 할 수 없다는 말. "they won't let me return", "If I could return it, I would"처럼 반품을 못 해 아쉽다는 말, 반품이 안 돼 남에게 줬다는 말도 포함 | 반품 기간이 지났거나 이미 개봉해서 못 돌려보낸다는 말은 return_window_missed. 판매자 태도, 연락 불가, 처리 과정이 어렵다, 교체를 거절했다는 말은 seller_unhelpful. 반품, 환불, 교체를 해 달라는 요청만 있으면 refund_request | "this type of purchase cannot be returned because it is a per" (R2AJYI0V67WG2L); "It is not returnable" (R1YXB7CP917VN9) | 57 |
| refund_request | 환불·교체 요청 | Requests refund or replacement | 리뷰 안에서 환불, 반품, 교체, 주문 취소를 해 달라고 요청하는 말("I want a TOTAL Refund", "Can you send a replacement?", "want my money back") | 반품이 안 된다는 사실을 말하면 not_returnable. 요청했는데 판매자가 거절하거나 응대가 나빴다는 말은 seller_unhelpful | "I want a TOTAL Refund" (R36SSTLD7LC0WN); "Can you send a replacement?" (RUMISBOJKGJG5) | 11 |
| seller_unhelpful | 판매자 응대 불만 | Unhelpful seller support | 판매자나 회사의 불친절, 무성의한 답변, 연락할 길이 없음, 반품·교환 처리 과정이 어렵다, 문제를 말했는데 교체나 조치를 해 주지 않았다("would not replace", "seller has been impossible to deal with") | 상품 규정상 반품이 안 된다는 말만 있으면 not_returnable. 기간이 지나 조치를 못 받았다는 말은 return_window_missed | "seller has been impossible to deal with" (R1IGZ4P4BM2BRJ); "there is absolutely no support or way to contact the seller" (R1TDEV9S3R58C2) | 10 |
| return_window_missed | 반품 기간 놓침 | Missed return window | 반품 기한이 지나서(또는 이미 개봉해서) 돌려보낼 수 없게 됐다는 말("my return window closed", "past 30 days since purchase") | 기간과 상관없이 향수라서, 규정상 반품이 안 된다는 말은 not_returnable | "my return window closed about 10 days ago" (R2WS73M76T1F87); "Just missed the return deadline by 2 days" (R1LAZX7YC5SB5V) | 5 |
| other | 기타 | Other | 위 라벨에 들지 않는 것 | - | - | 2 |

메모: 반품 불가가 표본의 약 3분의 2라 대부분이 not_returnable에 몰림. "they won't allow me to return"처럼 판매자 거절인지 상품 규정인지 알 수 없는 말은 not_returnable로 셈. return_window_missed는 기간 경과 4개에 개봉해서 못 돌려보낸 1개(R2I1J1CTT4XFQV)를 더해 5% 경계를 겨우 넘김. 구매 전에 반품 불가를 몰랐다는 말(R22BUJ1Q76GCH8, R3NNE65IW8H752 등 어림 3개)은 따로 나누기에 적어 not_returnable에 넣음. 기타는 "返品しました"(반품함), "A REFUND WAS GIVEN"(환불받았는데 부정으로 태깅됨).

### 긍정 이슈(긍정, 혼합 인용): 인용 6개, 표본 0개

인용이 20개 미만이거나 라벨이 없어 기타만 둡니다.

## 포장 (packaging)

### 부정 이슈(부정, 혼합 인용): 인용 17개, 표본 0개

인용이 20개 미만이거나 라벨이 없어 기타만 둡니다.

### 긍정 이슈(긍정, 혼합 인용): 인용 23개, 표본 23개

| id | 이름 | 영어 이름 | 포함 | 제외 | 대표 인용 | 어림 개수 |
|---|---|---|---|---|---|---|
| pretty_presentation | 상자와 포장이 예쁨 | Attractive box and presentation | 상자나 포장의 겉모양을 칭찬하는 말(cute, pretty, elegant, classy, clean, beautifully packaged, presentation, 설명 카드가 예쁨, Linda presentación) | 병 자체의 모양이나 색은 bottle_design. 병을 잘 지켜 준다, 안전하게 왔다는 well_protected. 원래 것과 같다는 matches_original. 무엇이 좋은지 없이 nice, good만 있으면 기타 | "The packaging is so cute." (R2MWXQTV4OA6W8); "The packaging is cute too and looks elegant" (R1CX3R6UQLOFAJ) | 12 |
| well_protected | 꼼꼼하게 포장되어 병을 잘 보호함 | Well packed and protective | 포장이 꼼꼼하다, 상자가 병을 잘 보호한다, 상자 상태가 멀쩡하게 왔다, 여행할 때도 상자가 병을 지켜 준다(packed well, packaged nicely, gut verpackt, keeps it secure for travel) | 배송 속도나 병이 깨지지 않고 왔다는 말 자체는 shipping. 상자의 겉모양 칭찬은 pretty_presentation | "packed well" (R1VKEB92N0AEHH); "box that comes with keeps it secure for travel" (R22HEPSREDBHOA) | 6 |
| matches_original | 포장이 원래 것과 같음 | Packaging matches the original | 상자나 포장이 정품, 예전에 받던 것과 같다는 말 | 포장을 가짜나 정품 의심의 근거로만 쓰면 trust(스키마 기준). 포장이 예쁘다는 말만 있으면 pretty_presentation | "embalagem tava perfeito como original" (R3QMZJEPSF4PJW); "the packaging appears consistent with the original" (R3E3IWV1CXIFEY) | 2 |
| other | 기타 | Other | 위 라벨에 들지 않는 것 | - | - | 4 |

메모: 기타 4개는 무엇이 좋은지 없는 포장 칭찬(Nice packaging though, 5 stars for their packaging 등)이라 겉모양과 보호 중 어느 쪽인지 정하지 못함. R2BG8L01VQAU1S는 예쁨과 보호를 함께 말해 두 라벨에 모두 셈. Linda presentación은 상자인지 병인지 불분명하지만 packaging으로 태깅되어 있어 pretty_presentation에 셈

## 품질 (quality)

### 부정 이슈(부정, 혼합 인용): 인용 64개, 표본 64개

| id | 이름 | 영어 이름 | 포함 | 제외 | 대표 인용 | 어림 개수 |
|---|---|---|---|---|---|---|
| old_or_spoiled | 오래됐거나 변질됨 | Old, expired or spoiled | 내용물이 오래됐다, 유통기한이 지난 것 같다, 상했다, 오래된 냄새가 난다, 색이 변했다는 말(old, old stock, expired, off, vencido, tainted, changed colors) | 가짜라는 의심만 있으면 이 라벨이 아님(trust 주제). 알코올이나 화학약품 냄새 묘사만 있으면 이 라벨이 아님(scent 주제) | "Old stock" (R3X87B0BDVYAE); "it smelled expired" (RSXO66KNMLOM3) | 18 |
| sprayer_stopped_working | 쓰다가 분사기 고장 | Sprayer stopped working after use | 처음에는 됐는데 쓰다가 분사기, 펌프, 노즐이 멈추거나 고장 났다는 말. stopped, now, after a month, after 5 uses, half a bottle remaining처럼 쓴 뒤라는 신호가 있을 때 | 쓴 뒤라는 신호 없이 분사가 안 된다, 고장 났다는 말만 있으면 sprayer_defective. 분사기가 아예 없으면 missing_parts | "The spray nozzle stopped working after a month." (R2FOFANNV4XRG2); "I literally got 2 sprays before it stopped working" (R2WNX9YRXPE699) | 12 |
| sprayer_defective | 분사기 불량 | Defective sprayer | 분사기, 펌프, 노즐이 처음부터 또는 시점 말 없이 작동하지 않거나 제대로 뿜지 않는다는 말(안 눌린다, 걸린다, 분사하면 흘러내린다, 새어 나온다 포함) | 쓰다가 멈췄다는 신호가 있으면 sprayer_stopped_working. 분사기나 튜브가 빠져 있으면 missing_parts. 여행이나 들고 다닐 때 병이 샌다는 말은 이 라벨이 아님(bottle_design 주제) | "had a defective spray pump" (R1TDEV9S3R58C2); "the nozzle won't even press down" (R2XPLAM5OFOU16) | 13 |
| missing_parts | 부품 빠짐 | Missing parts | 받았을 때 튜브(빨대), 뚜껑, 캡, 분사기 같은 부품이 처음부터 빠져 있었다는 말 | 부품이 있는데 작동하지 않으면 sprayer_defective 또는 sprayer_stopped_working. 상품 자체가 빠진 채 배달된 것은 이 라벨이 아님(shipping 주제) | "the bottle came without the tube/straw" (R3NB2WLRZ7KIF5); "The bottles did not come with lids" (R1YNRPFUOKI9PC) | 9 |
| poor_quality_general | 품질이 나쁨(구체 없음) | Poor quality in general | 무엇인지 밝히지 않고 품질이 나쁘다, 싸게 만들었다는 말(poor quality, not good quality, cheap made, 3rd class quality) | 변질, 분사기, 부품처럼 구체적인 불량을 말하면 그 라벨. calidad 뒤에 지속력 설명이 이어지면 이 라벨이 아님(longevity_projection 주제) | "Poor product quality" (R1IGZ4P4BM2BRJ); "Cheap made" (R2062UHONDUTUM) | 7 |
| other | 기타 | Other | 위 라벨에 들지 않는 것 | - | - | 5 |

메모: 기타 5개는 분사기 아닌 장식, 뚜껑 파손(Clip broke, top broke off, 장식 고리 veio quebrado) 3개와 두꺼운 유리 1개, 향수와 무관해 보이는 R1T7FSK04S0DMQ(collar wouldn't hold a charge) 1개. R3IY6PHSEQCN23(veio quebrado)은 받았을 때 깨져 온 것이라 shipping일 수도 있음. R1KW75H6XHEF5N(authenticity or age)은 old_or_spoiled로 셌고 trust와 함께 붙는 경우

### 긍정 이슈(긍정, 혼합 인용): 인용 7개, 표본 0개

인용이 20개 미만이거나 라벨이 없어 기타만 둡니다.

## 지속력과 향의 세기 (longevity_projection)

### 부정 이슈(부정, 혼합 인용): 인용 364개, 표본 150개

| id | 이름 | 영어 이름 | 포함 | 제외 | 대표 인용 | 어림 개수 |
|---|---|---|---|---|---|---|
| fades_fast | 금방 날아감 | Fades quickly | 향이 오래 가지 않는다고 잘라 말함. 몇 분이나 한두 시간 만에 사라진다, 전혀 안 간다, 시간 없이 "doesn't last (long)", fijación/fixação가 약하거나 없다, dura poco 같은 말 | 일정 시간은 간다고 인정하면서 하루 종일이나 기대만큼은 못 간다는 완곡한 아쉬움은 shorter_than_hoped. 처음부터 향이 약하거나 거의 안 난다는 말은 weak_scent(둘 다 말하면 둘 다) | "the scent only lasts about 10 minutes on the skin, hair and " (R38FLXFQ85RK5L); "No dura ni tres hora!!" (RM6MQCJ7NWE7B) | 78 |
| shorter_than_hoped | 기대보다 짧음 | Shorter than hoped | 어느 정도는 가지만 하루 종일, 8시간, 가격이나 EDP에 기대한 만큼은 못 간다는 말. 지속력이 보통이다, 그저 그렇다, 아주 오래가지는 않는다처럼 완곡한 아쉬움("not super long lasting", "Longevity is moderate", "doesn't last all day") | 시간 없이 단정하는 "doesn't last (long)", "no longevity"나 몇 분에서 두 시간 이하라는 말은 fades_fast. 세기나 확산이 아쉽다는 말은 weak_scent | "it lasts a decent time but obviously not extremely long" (RRAOPUZKGKPVN); "it doesn't last whole day" (RSDJ5EOJJ774J) | 15 |
| weak_scent | 처음부터 약함 | Weak or barely there | 뿌렸을 때부터 향이 약하다, 희미하다, 거의 또는 전혀 안 난다("very very faint", "No smell", "nada de olor", "no se siente"), 충분히 세지 않다, 주변으로 퍼지지 않는다, 피부 가까이만 난다, 남이 못 맡는다 | 처음엔 나다가 금방 사라진다는 시간 이야기는 fades_fast 또는 shorter_than_hoped. 향이 너무 세다는 반대 불만은 too_strong | "very very faint smell" (R1AIGEESVTE4DR); "The scent does last, but like I said it never projects like " (R3T9W3N67O0TFQ) | 33 |
| too_strong | 너무 셈 | Too strong | 향이 너무 세다, 과하다, 압도한다, 코를 찌른다("Too Strong.", "over powering", "so overwhelming", "it burns my nose", "demasiado fuerte"), 더 은은하길 바랐다 | 세다는 말을 칭찬으로 쓰면 positive 방향 strong_presence. 향의 성격이 싫다(달다, 독한 꽃향 등)는 말은 scent 주제. 실제 두통이나 메스꺼움 같은 몸 증상은 safety 주제 | "It is strong, over powering" (R1YXB7CP917VN9); "the smell is too strong for my liking" (R3CWIRDF2SHU59) | 20 |
| other | 기타 | Other | 위 라벨에 들지 않는 것 | - | - | 4 |

메모: 정품이나 예전 제품, 다른 매장 병보다 약하다 또는 짧다는 비교 인용이 8개 정도 있다(Sephora, Macy's, dept store, "now seems weak" 등). 스키마상 trust와 겹치는 내용이라 따로 라벨로 만들지 않고 약함과 짧음 라벨로 셌다. 확산 불만(안 퍼짐, 피부 가까이만)은 6개쯤으로 5%에 못 미쳐 weak_scent에 넣었다. 피부보다 옷에 오래 남는다는 혼합 인용 2개와 칭찬인데 부정 쪽에 들어온 인용 1개(R2XHXVVZ19TC9J "has staying power")는 기타로 셌다. 한 인용이 약함과 짧음을 함께 말하면 두 라벨 모두에 센다.

### 긍정 이슈(긍정, 혼합 인용): 인용 144개, 표본 144개

| id | 이름 | 영어 이름 | 포함 | 제외 | 대표 인용 | 어림 개수 |
|---|---|---|---|---|---|---|
| long_lasting | 오래감 | Long-lasting | 하루 종일, 몇 시간, 다음 날까지 간다, 덧뿌릴 필요가 없다, 적당히 오래 간다, 옷에 오래 남는다 ("lasts all day", "Long lasting", "dura muchísimo", "boa fixação", "sticks to clothes well") | 한두 번만 뿌려도 충분하다는 사용량 칭찬은 little_goes_far(같이 말하면 둘 다). 세게 퍼진다는 칭찬은 strong_presence | "I sprayed it about 11 in the morning and could smell it at 8" (R1BPS6WJ0CYY8J); "Scent lasts all day and sticks to clothes well" (RFKZ7EJ1U4UYQ) | 105 |
| not_overpowering | 과하지 않은 세기 | Not overpowering | 향이 독하지 않다, 과하지 않다, 은은하게 적당히 난다는 세기 칭찬("not too strong", "Not overbearing", "noticeable without being obnoxiously loud", "No es tan fuerte") | 세다는 것을 칭찬하면 strong_presence. 약해서 아쉽다는 말은 negative 방향 weak_scent. soft, light가 향의 분위기 묘사로만 쓰이면 scent 주제 | "Long-lasting without being overpowering." (R2LP5UYPZD2M8N); "noticeable without being obnoxiously loud" (R1E12UKLVMMO4A) | 16 |
| strong_presence | 진하고 잘 퍼짐 | Strong presence | 향이 세다, 진하다, 주변에서 알아챌 만큼 퍼진다는 것을 좋게 말함("Its really strong", "big aura", "se hace notar a donde sea que llegas", "Strong Perfume but not a bad thing") | 세서 싫다는 말은 negative 방향 too_strong. 독하지 않아 좋다는 말은 not_overpowering | "Its really strong" (R3W3FAYLHBYMFC); "me gusta lo q es muy fuerte el perfume" (RAVH5AMZTCM20) | 13 |
| little_goes_far | 조금만 써도 충분 | A little goes a long way | 한두 번만 뿌려도, 한 방울만 발라도 충분하다, 아껴 쓰게 된다("a little goes a long way", "Takes very little", "only need a drop on wrists", "All you need is 1 spray") | 사용량 언급 없이 오래간다는 말만 있으면 long_lasting. 병 용량을 오래 쓴다는 말은 bottle_design 주제 | "All you need is 1 spray, it lasts all day" (R17HE9MOSZI23R); "a little goes a long way" (R3LMWPBKHW9JSQ) | 9 |
| other | 기타 | Other | 위 라벨에 들지 않는 것 | - | - | 3 |

메모: 혼합 인용 중 칭찬 부분이 없는 것(R1VOECBP3FKNSC 확산 아쉬움, R3GLZVNE1IAC47 세서 부담)은 기타로 셌다. 옷에 오래 남는다는 칭찬은 4개쯤이라 long_lasting에 넣었다. 한 인용이 오래감과 세기 칭찬을 함께 말하면 두 라벨 모두에 센다.

## 안전 (safety)

### 부정 이슈(부정, 혼합 인용): 인용 18개, 표본 0개

인용이 20개 미만이거나 라벨이 없어 기타만 둡니다.

### 긍정 이슈(긍정, 혼합 인용): 인용 4개, 표본 0개

인용이 20개 미만이거나 라벨이 없어 기타만 둡니다.

## 병 디자인과 용량 (bottle_design)

### 부정 이슈(부정, 혼합 인용): 인용 35개, 표본 35개

| id | 이름 | 영어 이름 | 포함 | 제외 | 대표 인용 | 어림 개수 |
|---|---|---|---|---|---|---|
| bottle_too_small | 병이 작음 | Bottle too small | 병이나 용량이 작다, 생각보다(사진보다, 다른 것보다) 작다, 미니 크기라는 말(es "pequeño", "tamaño mini" 포함) | 분사 불만은 sprayer_problem, 새는 병은 bottle_leaks. 값 대비 양이 적다는 말은 price_value 주제 | "It was a tiny little bottle of perfume." (R2M38B7M76GHVM); "MUCH, MUCH smaller than depicted." (RZIM7LW20AGAT) | 27 |
| sprayer_problem | 분사기 불만 | Poor sprayer | 분사 방식이나 분사구 설계가 나쁘다(물줄기처럼 나간다, 누를 때 머리가 돈다, 노즐이 형편없다) | 쓰다가 고장 난 분사기나 받았을 때 작동하지 않는 분사기는 quality 주제. 병이 새는 것은 bottle_leaks | "The spray nozzle absolutely SUCKS." (R2C8OYSB7YQ5WR); "The sprayer on the bottle (at least on mine) is a straight s" (R20IVONJMW9MXU) | 3 |
| bottle_leaks | 병이 샘 | Bottle leaks | 쓰거나 들고 다닐 때 뚜껑 주변이나 병에서 향수가 샌다는 말 | 받았을 때 이미 새서 온 것은 shipping 주제. 분사 방식 불만은 sprayer_problem | "High leakage around cap on some bottles near diamond accents" (RJX4Z0KAFKUZW); "Bottle leaks all over" (RSKN6VFI7IWZF) | 2 |
| other | 기타 | Other | 위 라벨에 들지 않는 것 | - | - | 3 |

메모: 부정 표본의 대부분(약 27/35)이 '작다'라서 '생각보다 작음'(기대 불일치, 약 5개)과 '그냥 작음'을 나누지 않고 하나로 합쳤음. 기타는 디자인 총평(Terrible bottle design), 얇은 유리, 리필 불가 각 1개. R8Z2XMV0DR9CI("Way too small for $80")는 값 이야기가 섞여 price_value에 더 가까움.

### 긍정 이슈(긍정, 혼합 인용): 인용 78개, 표본 78개

| id | 이름 | 영어 이름 | 포함 | 제외 | 대표 인용 | 어림 개수 |
|---|---|---|---|---|---|---|
| pretty_bottle | 병이 예쁨 | Attractive bottle | 병 모양, 외관, 디자인이 예쁘다, 귀엽다, 멋지다, 미니멀하다, 겉모양 인상이 좋다(presentación, presencia 포함). 평가 대상이 병인 "Nice bottle"도 여기 | 재질, 만듦새, 견고함을 칭찬하면 build_quality. 자석 뚜껑 칭찬이 중심이면 magnetic_cap | "the bottle is gorgeous" (R2F8LJRFIL2S2K); "Pretty bottle" (R2T839DONCWG3M) | 27 |
| good_size | 용량이 알맞거나 넉넉함 | Good size | 크기가 딱 좋다, 생각보다 크다, 넉넉한 크기다, 작은 크기라 향을 바꿔 쓰기 좋다 | 핸드백이나 여행에 들고 다니기 좋다는 말은 purse_portable. 양이 오래 간다(몇 년 쓴다)는 말은 기타 | "the size is larger than expected" (R22KP4UHOX1JCN); "It's the perfect size" (R297F9WD8P3TY9) | 14 |
| purse_portable | 휴대하기 좋음 | Portable for purse or travel | 핸드백, 가방, 책상, 여행에 넣어 다니기 좋다, 작고 가볍다, 들고 다녀도 새지 않는다 | 휴대 언급 없이 크기만 좋다면 good_size | "Perfect to carry in your purse!" (R1BDJCZSNXV4KX); "I like having the smaller 0.34-ounce atomizer for travel" (R2P1Y45BWYDE9B) | 11 |
| magnetic_cap | 자석 뚜껑이 좋음 | Magnetic cap | 자석 뚜껑(magnetic cap, top, lid)이 좋다, 편하다, 닫는 느낌이 좋다 | 분사 칭찬은 sprayer_good. 뚜껑 언급 없이 병 외관만 칭찬하면 pretty_bottle | "I do like the magnetic top" (R27ZKX1A9GF3UM); "The lid is magnetic, which is oddly satisfying to close." (R21IFXQ51DU8CY) | 10 |
| sprayer_good | 분사가 잘 됨 | Sprays well | 분사기, 아토마이저가 좋다, 잘 뿌려진다, 쓰기 쉽다, 분사에 문제없다 | 뚜껑 칭찬은 magnetic_cap | "Sprays well." (R1A6XJF2CHWETX); "I also really like the way it sprays." (R2BG8L01VQAU1S) | 8 |
| build_quality | 병 만듦새가 좋음 | Well-made bottle | 병의 품질, 구조, 무게감, 견고함을 칭찬(quality of the bottle, well constructed, construction) | 모양이나 외관만 칭찬하면 pretty_bottle. 크기 칭찬은 good_size | "the quality of the bottle is great" (RR8UK6F5H31KU); "Bottle construction is nice though" (R3LV4MM4947LDI) | 6 |
| other | 기타 | Other | 위 라벨에 들지 않는 것 | - | - | 3 |

메모: 병 외관, 자석 뚜껑, 분사를 한 문장에 함께 칭찬한 인용이 많아(예 "nice sprayer and magnetic top") 라벨이 여러 개 걸칠 수 있음. '작은 병을 오래 쓴다'(2개)는 5% 미만이라 기타. RCVEIIQRM7XWQ(mixed, "the bottle size is a little small")는 칭찬 부분이 인용에 없어 기타.

## 향 (scent)

### 부정 이슈(부정, 혼합 인용): 인용 318개, 표본 150개

| id | 이름 | 영어 이름 | 포함 | 제외 | 대표 인용 | 어림 개수 |
|---|---|---|---|---|---|---|
| dislike_general | 향이 싫음(이유 없음) | Dislikes the scent (no specifics) | 노트나 비유 없이 향이 싫다, 별로다, 끔찍하다, 내 취향이 아니다는 말("Not a fan", "smells terrible", "not my preference") | 싫은 이유로 노트나 성격을 말하면 disliked_note_profile, 나이 이미지는 old_lady_mature, 알코올은 alcohol_smell, 다른 물건에 빗대면 unpleasant_likeness | "Do not like the scent!" (R2T839DONCWG3M); "Smells awful" (R1EYTLO94WC366) | 44 |
| differs_from_original | 원래 알던 향과 다름 | Smells different from the original | 예전에 쓰던 같은 제품, 원래 향과 다르다, 냄새가 이상하다(not right, off, 알아볼 수 없다) | 상품 설명이나 이름의 노트가 안 난다는 말은 missing_described_notes | "it doesn't smell like Eternity of the past" (R9ZEWAM020WG9); "My recent order of white diamonds has a different smell" (R1KW75H6XHEF5N) | 21 |
| missing_described_notes | 설명한 노트가 안 남 | Advertised notes missing | 상품 이름이나 설명, 광고의 노트(주로 바닐라, 앰버, 꿀)가 안 나거나 약하다, 설명과 실제 향이 다르다 | 예전 제품이나 정품과 비교해 다르다는 말은 differs_from_original | "Doesn’t smell like vanilla at all" (RR8UK6F5H31KU); "I don’t think the description fits the actual scent." (R2FZEJT891KVQW) | 17 |
| old_lady_mature | 나이 든 사람 향 | Old-lady or mature scent | 할머니, 노부인, 나이 든 사람 향이다, 너무 성숙하다, 젊지 않다("old lady", "grandma", "too mature", "no es juvenil") | 나이 이미지 없이 꽃향, 파우더리가 싫다는 말은 disliked_note_profile | "Smells old Ladyish" (R29XSCHHMVVP4B); "I think it's a scent for an elderly woman" (RC8UZZ9TT4LH8) | 17 |
| alcohol_smell | 알코올 냄새 | Smells of alcohol | 알코올 냄새만 난다, 소독용 알코올 같다, 뿌린 직후 알코올 냄새("puro alcohol", "rubbing alcohol") | 화학약품, 인공적, 플라스틱 냄새는 cheap_artificial | "Just smells like rubbing alcohol" (R1T8ST53B96R3E); "This perfume smells like straight alcohol." (R269IL84GKMM0N) | 12 |
| disliked_note_profile | 특정 노트나 성격이 싫음 | Dislikes a specific note or character | 특정 노트나 성격 때문에 싫다(너무 꽃향, 파우더리, 머스크, 우디, 후추, 너무 달다, 남성적이다) | 나이 이미지는 old_lady_mature, 설명한 노트가 없다는 말은 missing_described_notes, 향수가 아닌 물건에 빗대면 unpleasant_likeness | "A little too floral for my tastes" (R2987HKSLHIOML); "This has a powder smell that I hate." (RPOLF839J7L2Q) | 12 |
| unpleasant_likeness | 불쾌한 물건 냄새 | Smells like an unpleasant non-perfume thing | 향수가 아닌 물건에 빗댄 불쾌한 냄새(엔진오일, 벌레 퇴치제, 쓰레기, 담배, 약, 양념, 헤어 제품, 비누, 선탠오일, 연필깎은 냄새) | 알코올은 alcohol_smell, 화학약품, 인공적, 플라스틱은 cheap_artificial | "smells like bug spray" (R2C8YTC48CJE33); "smells like garbage" (R3SC6U5UDFIGM5) | 11 |
| cheap_artificial | 싸구려, 인공적인 냄새 | Cheap or artificial smell | 싸구려 냄새, 값싼 향수 같다, 화학약품, 인공적, 플라스틱 같은 냄새("Smells cheap", "chemical", "künstlich") | 알코올 냄새는 alcohol_smell, 가격 이야기는 이 주제가 아님 | "Smells cheap" (R1AG3QA8RNZUOA); "very chemical and artificial" (R2WLZEYU4QJSNX) | 8 |
| other | 기타 | Other | 위 라벨에 들지 않는 것 | - | - | 9 |

메모: differs_from_original 인용은 스키마상 trust에도 함께 태깅되는 내용이라 리포트에서 trust와 겹쳐 읽힐 수 있음. "does not smell right", "Scent was definitely off"처럼 비교 대상이 없는 이상함도 differs_from_original에 넣었는데 경계가 애매함. 기타는 첫 향과 잔향이 다르다(처음엔 별로였다가 괜찮아짐, 처음엔 좋다가 아님), 내 체취와 안 맞음, 칭찬을 못 받음, 불만 없는 혼합 인용 등.

### 긍정 이슈(긍정, 혼합 인용): 인용 488개, 표본 150개

| id | 이름 | 영어 이름 | 포함 | 제외 | 대표 인용 | 어림 개수 |
|---|---|---|---|---|---|---|
| smells_good_general | 향이 좋음(이유 없음) | Smells good (no specifics) | 노트나 성격 묘사 없이 향이 좋다, 사랑한다("Smells good", "Love the scent", "Great fragrance", "Huele bien"). 혼합 인용의 좋다는 부분도 여기 | 노트, 분위기, 인상을 말하면 appealing_character, 남의 반응은 compliments | "Smells amazing!!" (R2JL60OKVAL8YM); "It's a gorgeous, wonderful scent" (R4HVFOK3EB74D) | 115 |
| appealing_character | 노트나 분위기가 좋음 | Likes the notes or character | 좋아하는 노트, 분위기, 인상을 말함(따뜻하다, 달다, 크리미하다, 깨끗하다, 상쾌하다, 가볍다, 무겁지 않다, 꽃향, 바닐라, 남성적이다, 여성스럽다, 섹시하다, 비싸 보인다, 싸 보이지 않는다) | 묘사 없는 칭찬은 smells_good_general, 지속력이나 세기 평가는 이 주제가 아님 | "warm, sweet and creamy" (R1OKZ4D3AZRATQ); "The scent is warm, smooth, and distinctly masculine" (R1E12UKLVMMO4A) | 21 |
| compliments | 남에게 칭찬받음 | Gets compliments | 주변 사람이 향을 칭찬했다, 제품 이름을 물었다, 배우자나 받은 사람이 향을 좋아했다("Head turner") | 본인만 좋다고 하면 smells_good_general | "Have received the most amount of compliments I’ve ever recei" (R3HUTCGBNSP6M7); "I get compliments every time I wear it!" (R2QZ85R9X7DX6F) | 9 |
| other | 기타 | Other | 위 라벨에 들지 않는 것 | - | - | 5 |

메모: 긍정 인용의 대부분(어림 77%)이 묘사 없는 "Smells good"류라 더 나눌 근거가 표본에 없음. 기타는 원래 알던 향과 같다, 거의 완벽한 듀프(3개, trust 쪽 내용), 칭찬 부분이 없는 혼합 인용(2개).

