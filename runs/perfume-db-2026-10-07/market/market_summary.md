# 시장 데이터 요약: perfume-db-2026-10-07

spd-amz-market(무료)만 썼습니다. 마켓 US, 만든 때 2026-10-08T12:22:27+09:00. 숫자는 응답 값 그대로이고, 칸의 뜻이나 단위가 문서에 없으면 "단위 미확인"으로 적었습니다. 행마다 원본 파일은 market.json의 source에 있습니다.

## 1. 호출 목록

| # | 도구 | 입력 | 결과 | 행 수 | 비고 |
|---|---|---|---|---|---|
| 1 | products_byasin | {"asin": "B00021AJ5I"} | 성공 | - | 회차 raw/의 같은 날 응답을 복사(호출 없음) |
| 2 | products_variations | {"asin": "B0H62MKNTJ"} | 성공 | - | 회차 raw/의 같은 날 응답을 복사(호출 없음) |
| 3 | products_byasin | {"asin": "B0BZDZJDTG"} | 성공 | - | 회차 raw/의 같은 날 응답을 복사(호출 없음) |
| 4 | products_variations | {"asin": "B0HDT27STG"} | 성공 | - | 회차 raw/의 같은 날 응답을 복사(호출 없음) |
| 5 | products_byasin | {"asin": "B0009OAI8Q"} | 성공 | - | 회차 raw/의 같은 날 응답을 복사(호출 없음) |
| 6 | products_variations | {"asin": "B0FFPC31YQ"} | 성공 | - | 회차 raw/의 같은 날 응답을 복사(호출 없음) |
| 7 | products_byasin | {"asin": "B09X5BQ969"} | 성공 | - | 회차 raw/의 같은 날 응답을 복사(호출 없음) |
| 8 | products_variations | {"asin": "B0GFFVH9DV"} | 성공 | - | 회차 raw/의 같은 날 응답을 복사(호출 없음) |
| 9 | products_byasin | {"asin": "B08FBQWRYC"} | 성공 | - | 회차 raw/의 같은 날 응답을 복사(호출 없음) |
| 10 | products_variations | {"asin": "B0BGZWM1H6"} | 성공 | - | 회차 raw/의 같은 날 응답을 복사(호출 없음) |
| 11 | products_byasin | {"asin": "B0GFGL26JD"} | 성공 | - | 회차 raw/의 같은 날 응답을 복사(호출 없음) |
| 12 | products_variations | {"asin": "B0GPH36XYP"} | 성공 | - | 회차 raw/의 같은 날 응답을 복사(호출 없음) |
| 13 | subcategories_search | {} | 성공 | 31,479 |  |
| 14 | subcategories_category_competitors | {"sub_category_name": "Eau de Parfum", "start_row": 0, "end_row": 20} | 성공 | 20 |  |
| 15 | subcategories_relevant_search_terms | {"subcategory_name": "Eau de Parfum"} | 실패 | - | spd-amz-market tools/call: 500 Server Error: Internal Server Error for |
| 16 | subcategories_relevant_search_terms | {"subcategory_name": "Eau de Parfum"} | 실패 | - | spd-amz-market tools/call: 500 Server Error: Internal Server Error for |
| 17 | subcategories_category_competitors | {"sub_category_name": "Eau de Toilette", "start_row": 0, "end_row": 20} | 성공 | 20 |  |
| 18 | subcategories_relevant_search_terms | {"subcategory_name": "Eau de Toilette"} | 실패 | - | spd-amz-market tools/call: 500 Server Error: Internal Server Error for |
| 19 | subcategories_relevant_search_terms | {"subcategory_name": "Eau de Toilette"} | 실패 | - | spd-amz-market tools/call: 500 Server Error: Internal Server Error for |
| 20 | products_history | {"asin": "B00021AJ5I"} | 성공 | 26,450 |  |
| 21 | products_history | {"asin": "B0BZDZJDTG"} | 성공 | 7,713 |  |
| 22 | products_history | {"asin": "B0009OAI8Q"} | 성공 | 34,117 |  |
| 23 | products_history | {"asin": "B09X5BQ969"} | 성공 | 8,451 |  |
| 24 | products_history | {"asin": "B08FBQWRYC"} | 성공 | 15,337 |  |
| 25 | products_history | {"asin": "B0GFGL26JD"} | 성공 | 924 |  |
| 26 | search_terms_advertised_brands | {"search_term": "perfume for women", "start_row": 0, "end_row": 20} | 성공 | 20 |  |
| 27 | search_terms_trends_top_products | {"search_term": "perfume for women"} | 성공 | 5 |  |
| 28 | search_terms_ad_spy | {"brand_name": "Calvin Klein", "start_row": 0, "end_row": 20} | 성공 | 20 |  |
| 29 | search_terms_trends | {"keyword": "perfume for women", "months": 12} | 성공 | 100 |  |
| 30 | subcategories_category_competitors | {"sub_category_name": "Women's Eau de Parfum", "start_row": 0, "end_row": 20} | 성공 | 20 |  |
| 31 | subcategories_relevant_search_terms | {"subcategory_name": "Women's Eau de Parfum"} | 실패 | - | spd-amz-market tools/call: 500 Server Error: Internal Server Error for |
| 32 | subcategories_relevant_search_terms | {"subcategory_name": "Women's Eau de Parfum"} | 성공 | 37,624 | 두 번째 시도에 성공 |
| 33 | subcategories_category_competitors | {"sub_category_name": "Women's Eau de Toilette", "start_row": 0, "end_row": 20} | 성공 | 20 |  |
| 34 | subcategories_relevant_search_terms | {"subcategory_name": "Women's Eau de Toilette"} | 성공 | 15,736 |  |
| 35 | search_terms_trends | {"keyword": "now", "months": 12} | 성공 | 100 |  |
| 36 | search_terms_trends | {"keyword": "hair perfume", "months": 12} | 성공 | 100 |  |
| 37 | search_terms_trends | {"keyword": "perfumes for women", "months": 12} | 성공 | 100 |  |
| 38 | search_terms_trends | {"keyword": "gifts for women", "months": 12} | 성공 | 100 |  |
| 39 | search_terms_trends | {"keyword": "yellowstone", "months": 12} | 성공 | 100 |  |
| 40 | search_terms_trends | {"keyword": "the summer i turned pretty", "months": 12} | 성공 | 100 |  |
| 41 | search_terms_trends | {"keyword": "sol de janeiro", "months": 12} | 성공 | 100 |  |
| 42 | search_terms_trends | {"keyword": "blue", "months": 12} | 성공 | 100 |  |
| 43 | search_terms_trends | {"keyword": "cologne for men", "months": 12} | 성공 | 100 |  |
| 44 | search_terms_trends | {"keyword": "am", "months": 12} | 성공 | 100 |  |
| 45 | search_terms_trends | {"keyword": "mens cologne", "months": 12} | 성공 | 100 |  |
| 46 | search_terms_trends | {"keyword": "perfume", "months": 12} | 성공 | 100 |  |
| 47 | search_terms_trends | {"keyword": "lattafa", "months": 12} | 성공 | 100 |  |
| 48 | search_terms_trends | {"keyword": "valentino", "months": 12} | 성공 | 100 |  |
| 49 | search_terms_trends | {"keyword": "perfume for men", "months": 12} | 성공 | 100 |  |
| 50 | search_terms_trends | {"keyword": "cologne", "months": 12} | 성공 | 100 |  |
| 51 | search_terms_trends | {"keyword": "yara perfume", "months": 12} | 성공 | 75 |  |
| 52 | search_terms_trends | {"keyword": "perfume", "months": 24} | 성공 | 100 |  |
| 53 | search_terms_trends | {"keyword": "cologne", "months": 24} | 성공 | 100 |  |
| 54 | search_terms_trends | {"keyword": "lattafa", "months": 24} | 성공 | 100 |  |
| 55 | search_terms_trends | {"keyword": "versace", "months": 24} | 성공 | 100 |  |
| 56 | search_terms_trends | {"keyword": "dior", "months": 24} | 성공 | 100 |  |
| 57 | search_terms_trends | {"keyword": "fragrances", "months": 24} | 성공 | 100 |  |
| 58 | search_terms_trends | {"keyword": "body mist", "months": 24} | 성공 | 100 |  |
| 59 | search_terms_trends | {"keyword": "glossier", "months": 24} | 성공 | 100 |  |
| 60 | search_terms_trends | {"keyword": "chanel", "months": 24} | 성공 | 100 |  |
| 61 | search_terms_trends | {"keyword": "valentino", "months": 24} | 성공 | 100 |  |
| 62 | search_terms_trends | {"keyword": "tom ford", "months": 24} | 성공 | 100 |  |
| 63 | search_terms_trends | {"keyword": "armaf", "months": 24} | 성공 | 100 |  |
| 64 | search_terms_trends | {"keyword": "gucci", "months": 24} | 성공 | 100 |  |

실제 호출 52번(한도 40번), 실패 5번.

## 2. 하위 카테고리(여성 향수 노드와 위 노드)

월 매출, 판매량은 칸 이름(totalMonthlyRevenue, totalNumberUnitsSold) 그대로이고 통화와 기간은 문서에 없어 단위 미확인. 증감(momGrowth, momGrowth12), azRevenuePct, sellerRevenuePct도 단위 미확인.

| 노드 id | 이름 | 월 매출 | 판매량 | 브랜드 수 | ASIN 수 | 평균 가격 | 평균 별점 | momGrowth | momGrowth12 | azRevenuePct | sellerRevenuePct |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 11056591 | Perfumes & Fragrances | 131,836,120 | 3,585,065 | 3,067 | 60,147 | 38.05 | 4.25 | 0.00 | 0.13 | 0.2730 | 0.7270 |
| 11056931 | Women's Fragrances | 72,057,467 | 2,110,645 | 2,184 | 33,815 | 43.22 | 4.22 | -0.03 | 0.08 | 0.2777 | 0.7223 |
| 11056761 | Men's Fragrances | 57,053,612 | 1,375,949 | 1,770 | 25,202 | 40.23 | 4.30 | 0.03 | 0.22 | 0.2669 | 0.7331 |
| 11057071 | Women's Eau de Parfum | 45,658,866 | 1,104,683 | 1,440 | 20,564 | 51.43 | 4.15 | 0.00 | 0.14 | 0.2645 | 0.7355 |
| 3783161 | Women's Body Sprays Fragrance | 10,834,875 | 536,494 | 409 | 3,333 | 25.42 | 4.30 | -0.14 | -0.16 | 0.2543 | 0.7457 |
| 11057081 | Women's Eau de Toilette | 8,174,930 | 188,786 | 635 | 4,231 | 58.14 | 4.36 | -0.04 | 0.03 | 0.4511 | 0.5489 |
| 11057111 | Women's Fragrance Sets | 3,411,822 | 102,492 | 321 | 1,616 | 47.98 | 4.31 | -0.15 | 0.38 | 0.2415 | 0.7585 |
| 11057051 | Women's Cologne | 1,969,740 | 80,361 | 438 | 3,515 | 40.24 | 4.05 | 0.07 | -0.10 | 0.2663 | 0.7337 |
| 16262036011 | Women's Eau Fraiche | 58,871 | 4,419 | 8 | 16 | 54.12 | 4.22 | -0.20 | 2.02 | 0.1484 | 0.8516 |

## 3. 브랜드 상위 20: Women's Eau de Parfum

marketshare, moMMktShareChange, adSpendShare는 응답 값 그대로(단위 미확인). revenue는 칸 이름 그대로(기간과 통화 단위 미확인).

| 순위 | 브랜드 | revenue | marketshare | moMMktShareChange | ASIN 수 | 판매량 | 평균 가격 | 평균 별점 | 리뷰 수 | adSpendShare |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Lattafa | 3,657,143 | 0.0801 | -0.0093 | 342 | 139,188 | 32.35 | 4.31 | 984,447 | 0.002 |
| 2 | Bella Vita Luxury | 1,666,120 | 0.0365 | 0.0081 | 21 | 83,685 | 21.61 | 4.08 | 83,117 | 0.092 |
| 3 | Yves Saint Laurent | 1,647,606 | 0.0361 | -0.0021 | 118 | 19,947 | 84.59 | 4.42 | 62,026 | - |
| 4 | Lancôme | 1,513,856 | 0.0332 | 0.0047 | 57 | 17,418 | 113.92 | 4.55 | 300,150 | 0.033 |
| 5 | Victoria's Secret | 1,080,440 | 0.0237 | -0.0005 | 194 | 22,958 | 58.59 | 4.58 | 171,410 | 0.044 |
| 6 | Estée lauder | 1,043,179 | 0.0228 | 0.0021 | 93 | 14,223 | 81.18 | 4.53 | 209,504 | 0.032 |
| 7 | Dossier | 966,950 | 0.0212 | 0.0039 | 49 | 26,567 | 41.05 | 4.19 | 64,294 | 0.039 |
| 8 | Gucci | 921,947 | 0.0202 | 0.0004 | 106 | 16,597 | 63.06 | 4.48 | 108,528 | - |
| 9 | ARMANI Beauty | 906,679 | 0.0199 | 0.0050 | 86 | 10,409 | 97.47 | 4.55 | 150,452 | 0.018 |
| 10 | Prada | 814,272 | 0.0178 | 0.0007 | 70 | 9,766 | 96.09 | 4.48 | 67,268 | - |
| 11 | Ariana Grande | 755,689 | 0.0166 | -0.0018 | 42 | 12,683 | 56.06 | 4.62 | 330,997 | - |
| 12 | Valentino | 722,536 | 0.0158 | -0.0036 | 67 | 9,106 | 80.88 | 4.45 | 54,969 | 0.001 |
| 13 | Carolina Herrera | 717,560 | 0.0157 | 0.0004 | 115 | 7,838 | 105.38 | 4.55 | 181,060 | 0.014 |
| 14 | ARMAF | 708,988 | 0.0155 | -0.0006 | 113 | 23,332 | 34.31 | 4.24 | 83,635 | - |
| 15 | Tom Ford | 684,468 | 0.0150 | 0.0007 | 114 | 7,588 | 164.08 | 4.31 | 44,733 | - |
| 16 | Glossier | 639,981 | 0.0140 | 0.0017 | 20 | 10,964 | 72.08 | 4.45 | 4,148 | 0.025 |
| 17 | Versace | 632,066 | 0.0138 | 0.0004 | 64 | 11,367 | 56.22 | 4.44 | 136,938 | - |
| 18 | Clinique | 606,538 | 0.0133 | 0.0027 | 18 | 8,696 | 62.34 | 4.59 | 144,503 | 0.027 |
| 19 | Calvin Klein | 562,321 | 0.0123 | 0.0024 | 48 | 5,872 | 89.12 | 4.49 | 159,264 | 0.019 |
| 20 | Mugler | 551,340 | 0.0121 | 0.0008 | 80 | 6,869 | 114.22 | 4.54 | 188,719 | 0.017 |

## 3. 브랜드 상위 20: Women's Eau de Toilette

marketshare, moMMktShareChange, adSpendShare는 응답 값 그대로(단위 미확인). revenue는 칸 이름 그대로(기간과 통화 단위 미확인).

| 순위 | 브랜드 | revenue | marketshare | moMMktShareChange | ASIN 수 | 판매량 | 평균 가격 | 평균 별점 | 리뷰 수 | adSpendShare |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Versace | 737,229 | 0.0902 | 0.0027 | 115 | 16,478 | 54.30 | 4.58 | 390,164 | 0.006 |
| 2 | Dolce&Gabbana | 706,291 | 0.0864 | 0.0029 | 82 | 8,135 | 93.28 | 4.54 | 165,380 | 0.028 |
| 3 | Marc Jacobs | 417,711 | 0.0511 | 0.0023 | 87 | 4,767 | 81.89 | 4.60 | 149,191 | 0.066 |
| 4 | Dior | 307,530 | 0.0376 | 0.0043 | 105 | 3,567 | 114.08 | 4.39 | 92,790 | 0.003 |
| 5 | philosophy | 305,564 | 0.0374 | -0.0058 | 34 | 5,823 | 57.57 | 4.51 | 50,659 | 0.059 |
| 6 | Dime | 270,568 | 0.0331 | -0.0058 | 25 | 6,637 | 47.51 | 4.31 | 22,742 | 0.230 |
| 7 | CHANEL | 268,598 | 0.0329 | 0.0010 | 74 | 2,360 | 162.85 | 4.41 | 21,689 | 0.001 |
| 8 | Maison Margiela | 226,372 | 0.0277 | -0.0002 | 61 | 2,209 | 98.54 | 4.30 | 10,854 | 0.061 |
| 9 | Vera Wang | 209,678 | 0.0256 | -0.0010 | 34 | 11,370 | 35.18 | 4.50 | 189,177 | - |
| 10 | Calvin Klein | 206,986 | 0.0253 | -0.0051 | 27 | 2,330 | 79.02 | 4.43 | 168,718 | 0.066 |
| 11 | Givenchy | 193,519 | 0.0237 | -0.0004 | 39 | 3,272 | 76.48 | 4.43 | 31,978 | 0.004 |
| 12 | Yves Saint Laurent | 191,982 | 0.0235 | 0.0042 | 47 | 1,681 | 102.86 | 4.53 | 20,267 | - |
| 13 | GUESS | 183,024 | 0.0224 | 0.0005 | 66 | 10,275 | 25.70 | 4.39 | 148,956 | 0.045 |
| 14 | Tommy Hilfiger | 165,952 | 0.0203 | 0.0029 | 28 | 3,526 | 51.39 | 4.56 | 40,623 | 0.015 |
| 15 | RALPH LAUREN FRAGRANCES | 160,404 | 0.0196 | 0.0049 | 10 | 1,803 | 91.69 | 4.48 | 22,223 | 0.006 |
| 16 | BVLGARI | 148,786 | 0.0182 | -0.0020 | 60 | 1,764 | 86.98 | 4.49 | 50,371 | - |
| 17 | Guerlain | 128,653 | 0.0157 | -0.0014 | 62 | 1,347 | 88.10 | 4.34 | 23,600 | 0.001 |
| 18 | Elizabeth Taylor | 125,949 | 0.0154 | -0.0014 | 63 | 6,106 | 25.42 | 4.55 | 125,156 | 0.010 |
| 19 | Gucci | 115,057 | 0.0141 | 0.0012 | 74 | 2,550 | 65.30 | 4.45 | 36,735 | 0.001 |
| 20 | REVLON | 114,777 | 0.0140 | 0.0034 | 19 | 8,276 | 15.76 | 4.41 | 55,831 | - |

## 4. 검색어 상위 50: Women's Eau de Parfum

| 순위 | 검색어 | 30일 검색량 | 최근 4주 | 작년 같은 4주 | yoYChange | yoYChangePct | relevancy |
|---|---|---|---|---|---|---|---|
| 1 | hair perfume | 330,109 | 210,700 | 62,970 | 147,730 | 2.3460 | 66 |
| 2 | perfumes for women | 270,398 | 266,044 | 244,656 | 21,388 | 0.0874 | 82 |
| 3 | cologne for men | 206,595 | 200,007 | 198,781 | 1,226 | 0.0062 | 56 |
| 4 | mens cologne | 194,526 | 188,669 | 191,533 | -2,864 | -0.0150 | 56 |
| 5 | perfume | 177,366 | 172,199 | 215,420 | -43,221 | -0.2006 | 74 |
| 6 | lattafa | 133,200 | 129,660 | 138,622 | -8,962 | -0.0647 | 74 |
| 7 | valentino | 127,181 | 121,069 | 59,709 | 61,360 | 1.0277 | 74 |
| 8 | perfume for men | 123,522 | 125,623 | 120,818 | 4,805 | 0.0398 | 56 |
| 9 | cologne | 113,368 | 106,884 | 130,111 | -23,227 | -0.1785 | 56 |
| 10 | yara perfume | 108,641 | 107,411 | 59,806 | 47,605 | 0.7960 | 77 |
| 11 | versace eros | 107,083 | 105,038 | 102,046 | 2,992 | 0.0293 | 56 |
| 12 | voyage nova perfume | 106,861 | 88,531 | - | - | - | 75 |
| 13 | fragrances | 104,622 | 84,353 | 50,737 | 33,616 | 0.6626 | 68 |
| 14 | goda perfume for women | 101,571 | 106,493 | 106,121 | 372 | 0.0035 | 71 |
| 15 | victoria secret perfume | 98,128 | 90,881 | 117,944 | -27,063 | -0.2295 | 71 |
| 16 | vanilla perfume | 94,475 | 95,925 | 130,502 | -34,577 | -0.2650 | 69 |
| 17 | bella vita perfume | 91,817 | 95,277 | 13,067 | 82,210 | 6.2914 | 73 |
| 18 | lattafa perfumes for women | 87,313 | 81,448 | 141,605 | -60,157 | -0.4248 | 75 |
| 19 | billie eilish perfume | 76,748 | 73,363 | 105,031 | -31,668 | -0.3015 | 75 |
| 20 | lattafa khamrah | 69,926 | 64,930 | 73,959 | -9,029 | -0.1221 | 61 |
| 21 | jean paul gaultier | 69,664 | 67,699 | 102,956 | -35,257 | -0.3424 | 42 |
| 22 | valentino cologne for men | 66,876 | 65,322 | 82,702 | -17,380 | -0.2102 | 42 |
| 23 | ariana grande perfume | 64,624 | 64,577 | 84,901 | -20,324 | -0.2394 | 74 |
| 24 | sand and fog perfume oil | 64,234 | 59,484 | 56,972 | 2,512 | 0.0441 | 73 |
| 25 | calvin klein | 61,733 | 59,328 | 63,255 | -3,927 | -0.0621 | 33 |
| 26 | 9pm cologne for men | 61,636 | 58,802 | 41,645 | 17,157 | 0.4120 | 62 |
| 27 | armaf | 61,427 | 60,404 | 53,474 | 6,930 | 0.1296 | 60 |
| 28 | men cologne | 60,534 | 62,996 | 66,041 | -3,045 | -0.0461 | 40 |
| 29 | ysl cologne for men | 60,056 | 62,981 | 62,449 | 532 | 0.0085 | 62 |
| 30 | haiku perfume for women | 58,776 | 20,971 | 10,227 | 10,744 | 1.0506 | 67 |
| 31 | valentino perfume for women | 58,386 | 58,750 | 104,229 | -45,479 | -0.4363 | 74 |
| 32 | guess | 57,680 | 56,057 | 58,610 | -2,553 | -0.0436 | 56 |
| 33 | pheromones perfumes for women | 56,890 | 57,542 | 91,570 | -34,028 | -0.3716 | 68 |
| 34 | versace bright crystal | 56,628 | 56,860 | 11,200 | 45,660 | 4.0768 | 62 |
| 35 | dior | 55,621 | 55,904 | 51,012 | 4,892 | 0.0959 | 64 |
| 36 | kayali perfume | 55,482 | 51,306 | 51,801 | -495 | -0.0096 | 74 |
| 37 | carolina herrera perfume for women | 54,428 | 56,653 | 57,383 | -730 | -0.0127 | 72 |
| 38 | perfumes | 51,189 | 48,729 | 41,739 | 6,990 | 0.1675 | 65 |
| 39 | ycz cologne for men | 49,061 | 48,737 | 59,209 | -10,472 | -0.1769 | 34 |
| 40 | versace cologne for men | 46,518 | 47,028 | 106,458 | -59,430 | -0.5582 | 35 |
| 41 | goda pheromone perfume for women | 43,884 | 39,345 | - | - | - | 66 |
| 42 | sauvage dior for men | 43,806 | 46,165 | 58,397 | -12,232 | -0.2095 | 30 |
| 43 | perfume oil | 43,653 | 43,071 | 43,198 | -127 | -0.0029 | 64 |
| 44 | perfumes for men | 43,641 | 43,439 | 43,461 | -22 | -0.0005 | 49 |
| 45 | womens perfume | 43,577 | 45,798 | 52,400 | -6,602 | -0.1260 | 66 |
| 46 | men's cologne | 43,510 | 46,351 | 46,880 | -529 | -0.0113 | 35 |
| 47 | armaf club de nuit intense man | 43,299 | 43,038 | 36,290 | 6,748 | 0.1859 | 37 |
| 48 | aqua di gio parfum for men | 43,064 | 41,796 | 34,167 | 7,629 | 0.2233 | 27 |
| 49 | body mist | 43,007 | 42,065 | 36,792 | 5,273 | 0.1433 | 29 |
| 50 | dossier perfume | 42,894 | 41,901 | 53,561 | -11,660 | -0.2177 | 71 |

## 4. 검색어 상위 50: Women's Eau de Toilette

| 순위 | 검색어 | 30일 검색량 | 최근 4주 | 작년 같은 4주 | yoYChange | yoYChangePct | relevancy |
|---|---|---|---|---|---|---|---|
| 1 | perfumes for women | 270,398 | 266,044 | 244,656 | 21,388 | 0.0874 | 73 |
| 2 | perfume | 177,366 | 172,199 | 215,420 | -43,221 | -0.2006 | 66 |
| 3 | versace eros | 107,083 | 105,038 | 102,046 | 2,992 | 0.0293 | 27 |
| 4 | voyage nova perfume | 106,861 | 88,531 | - | - | - | 49 |
| 5 | fragrances | 104,622 | 84,353 | 50,737 | 33,616 | 0.6626 | 58 |
| 6 | goda perfume for women | 101,571 | 106,493 | 106,121 | 372 | 0.0035 | 35 |
| 7 | vanilla perfume | 94,475 | 95,925 | 130,502 | -34,577 | -0.2650 | 50 |
| 8 | bella vita perfume | 91,817 | 95,277 | 13,067 | 82,210 | 6.2914 | 37 |
| 9 | ariana grande perfume | 64,624 | 64,577 | 84,901 | -20,324 | -0.2394 | 23 |
| 10 | haiku perfume for women | 58,776 | 20,971 | 10,227 | 10,744 | 1.0506 | 47 |
| 11 | guess | 57,680 | 56,057 | 58,610 | -2,553 | -0.0436 | 58 |
| 12 | hair perfume spray | 57,388 | 132,502 | 2,831 | 129,671 | 45.8040 | 42 |
| 13 | versace bright crystal | 56,628 | 56,860 | 11,200 | 45,660 | 4.0768 | 71 |
| 14 | dior | 55,621 | 55,904 | 51,012 | 4,892 | 0.0959 | 57 |
| 15 | carolina herrera perfume for women | 54,428 | 56,653 | 57,383 | -730 | -0.0127 | 52 |
| 16 | perfumes | 51,189 | 48,729 | 41,739 | 6,990 | 0.1675 | 55 |
| 17 | goda pheromone perfume for women | 43,884 | 39,345 | - | - | - | 47 |
| 18 | womens perfume | 43,577 | 45,798 | 52,400 | -6,602 | -0.1260 | 60 |
| 19 | aqua di gio parfum for men | 43,064 | 41,796 | 34,167 | 7,629 | 0.2233 | 35 |
| 20 | body mist | 43,007 | 42,065 | 36,792 | 5,273 | 0.1433 | 38 |
| 21 | soft perfume | 42,798 | 16,214 | 10,216 | 5,998 | 0.5871 | 33 |
| 22 | women perfume | 42,507 | 41,994 | 42,831 | -837 | -0.0195 | 61 |
| 23 | burberry perfume for women | 42,481 | 42,002 | 39,638 | 2,364 | 0.0596 | 56 |
| 24 | jimmy choo perfume for women | 42,359 | 42,463 | 44,222 | -1,759 | -0.0398 | 53 |
| 25 | gucci guilty for men | 42,232 | 42,720 | 42,185 | 535 | 0.0127 | 49 |
| 26 | dime perfume | 41,533 | 39,003 | 33,765 | 5,238 | 0.1551 | 65 |
| 27 | ysl perfume for women | 41,425 | 40,838 | 40,670 | 168 | 0.0041 | 50 |
| 28 | gucci flora perfume | 41,232 | 39,005 | 46,431 | -7,426 | -0.1599 | 42 |
| 29 | perfume for women | 41,067 | 41,332 | 51,965 | -10,633 | -0.2046 | 61 |
| 30 | glossier you | 39,969 | 39,799 | 21,739 | 18,060 | 0.8308 | 48 |
| 31 | salt and stone perfume | 39,735 | 38,974 | 23,782 | 15,192 | 0.6388 | 34 |
| 32 | miss dior | 38,637 | 39,692 | 28,643 | 11,049 | 0.3857 | 61 |
| 33 | good girl perfume | 38,566 | 38,042 | 40,648 | -2,606 | -0.0641 | 31 |
| 34 | venom scents pheromones for women | 37,713 | 38,413 | 36,095 | 2,318 | 0.0642 | 29 |
| 35 | mini perfume | 37,436 | 38,226 | 38,877 | -651 | -0.0167 | 52 |
| 36 | gucci | 36,453 | 37,976 | 44,355 | -6,379 | -0.1438 | 55 |
| 37 | marc jacobs perfume | 36,344 | 37,282 | 33,585 | 3,697 | 0.1101 | 66 |
| 38 | salt and stone body mist | 36,187 | 38,307 | 40,093 | -1,786 | -0.0445 | 42 |
| 39 | hawas cologne for men | 35,764 | 34,430 | 36,726 | -2,296 | -0.0625 | 39 |
| 40 | travel perfume | 34,634 | 33,286 | 30,401 | 2,885 | 0.0949 | 49 |
| 41 | chanel | 34,203 | 38,103 | 43,031 | -4,928 | -0.1145 | 54 |
| 42 | paris hilton perfume | 33,649 | 33,803 | 36,503 | -2,700 | -0.0740 | 51 |
| 43 | pink blush perfume | 33,356 | 35,200 | 57,592 | -22,392 | -0.3888 | 36 |
| 44 | yves saint laurent | 33,045 | 38,076 | 19,315 | 18,761 | 0.9713 | 37 |
| 45 | finery perfume | 32,884 | 31,363 | 15,114 | 16,249 | 1.0751 | 33 |
| 46 | juliette has a gun not a perfume | 32,309 | 31,929 | 31,862 | 67 | 0.0021 | 24 |
| 47 | tom ford | 32,018 | 29,991 | 29,648 | 343 | 0.0116 | 22 |
| 48 | ariana grande cloud perfume | 31,989 | 30,884 | 37,410 | -6,526 | -0.1744 | 29 |
| 49 | coach perfume | 31,540 | 28,077 | 14,946 | 13,131 | 0.8786 | 46 |
| 50 | bleu de chanel for men | 30,913 | 32,121 | 39,550 | -7,429 | -0.1878 | 43 |

## 5. 검색어 추이(search_terms_trends, 12개월)

growth 칸은 응답 값 그대로(estimateSearchesGrowth1Month 등, 단위 미확인). 향수 검색어 표시가 아니오인 것은 처음 고른 규칙(relevancy만)으로 잘못 고른 검색어라 해석에 쓰지 않습니다.

| 검색어 | 향수 검색어 | 추정 검색 수 | 1개월 | 3개월 | 6개월 | 12개월 | 이력 기간 | 주 수 | 첫 주 | 마지막 주 |
|---|---|---|---|---|---|---|---|---|---|---|
| perfume for women | 예 | 41,067 | 2,151 | 1,353 | 4,322 | -9,978 | 2025-09-21 ~ 2026-09-27 | 54 | 51,045 | 41,067 |
| now | 아니오 | 374,117 | 286,568 | 312,378 | 315,447 | 353,085 | 2025-09-21 ~ 2026-09-27 | 54 | 21,032 | 374,117 |
| hair perfume | 예 | 330,109 | 180,948 | 259,109 | -124,816 | 267,193 | 2025-09-21 ~ 2026-09-27 | 54 | 62,916 | 330,109 |
| perfumes for women | 예 | 270,398 | 16,805 | 62,436 | 52,095 | 29,638 | 2025-09-21 ~ 2026-09-27 | 54 | 240,760 | 270,398 |
| gifts for women | 아니오 | 242,441 | 68,517 | 91,795 | 16,041 | 10,694 | 2025-09-21 ~ 2026-09-27 | 54 | 231,747 | 242,441 |
| yellowstone | 아니오 | 233,733 | -21,082 | -66,999 | -38,499 | 26,384 | 2025-09-21 ~ 2026-09-27 | 54 | 207,349 | 233,733 |
| the summer i turned pretty | 아니오 | 222,428 | -91,454 | -117,193 | -160,912 | -590,412 | 2025-09-21 ~ 2026-09-27 | 54 | 812,840 | 222,428 |
| sol de janeiro | 아니오 | 219,219 | 9,607 | -247,902 | -123,480 | -92,984 | 2025-09-21 ~ 2026-09-27 | 54 | 312,203 | 219,219 |
| blue | 아니오 | 214,178 | 21,491 | 133,306 | 158,702 | 160,340 | 2025-09-21 ~ 2026-09-27 | 54 | 53,838 | 214,178 |
| cologne for men | 예 | 206,595 | 6,129 | -2,357 | -36,151 | 6,506 | 2025-09-21 ~ 2026-09-27 | 54 | 200,089 | 206,595 |
| am | 아니오 | 204,285 | 83,998 | 146,725 | 164,363 | 151,972 | 2025-09-21 ~ 2026-09-27 | 54 | 52,313 | 204,285 |
| mens cologne | 예 | 194,526 | 17,585 | 28,236 | 22,346 | 3,017 | 2025-09-21 ~ 2026-09-27 | 54 | 191,509 | 194,526 |
| perfume | 예 | 177,366 | 16,856 | -32,199 | -27,155 | -43,076 | 2025-09-21 ~ 2026-09-27 | 54 | 220,442 | 177,366 |
| lattafa | 예 | 133,200 | 19,924 | 24,022 | 6,655 | -5,462 | 2025-09-21 ~ 2026-09-27 | 54 | 138,662 | 133,200 |
| valentino | 예 | 127,181 | 26,474 | 68,491 | 48,103 | 67,306 | 2025-09-21 ~ 2026-09-27 | 54 | 59,875 | 127,181 |
| perfume for men | 예 | 123,522 | -79 | 20,654 | 12,367 | 1,220 | 2025-09-21 ~ 2026-09-27 | 54 | 122,302 | 123,522 |
| cologne | 예 | 113,368 | 19,587 | 13,551 | -14,927 | -16,729 | 2025-09-21 ~ 2026-09-27 | 54 | 130,097 | 113,368 |
| yara perfume | 예 | 108,641 | -7,563 | 41,045 | -9,525 | 46,838 | 2025-09-21 ~ 2026-09-27 | 54 | 61,803 | 108,641 |
| versace | 예 | 응답에 그 검색어 행 없음 | | | | | | | | |
| dior | 예 | 응답에 그 검색어 행 없음 | | | | | | | | |
| fragrances | 예 | 응답에 그 검색어 행 없음 | | | | | | | | |
| body mist | 예 | 응답에 그 검색어 행 없음 | | | | | | | | |
| glossier | 예 | 응답에 그 검색어 행 없음 | | | | | | | | |
| chanel | 예 | 응답에 그 검색어 행 없음 | | | | | | | | |
| tom ford | 예 | 응답에 그 검색어 행 없음 | | | | | | | | |
| armaf | 예 | 응답에 그 검색어 행 없음 | | | | | | | | |
| gucci | 예 | 응답에 그 검색어 행 없음 | | | | | | | | |

## 6. 우리 상품 6개(products_byasin, products_history)

monthlyRevenueEstimate, monthlyUnitsSold, amzMonthlySold는 칸 이름 그대로(단위 미확인). 가격 이력(amazon, buyBoxShipping)과 순위 이력(salesRank)의 값 단위는 문서에 없어 단위 미확인이고, 같은 날의 buyBoxPrice와 나란히 적었습니다.

| ASIN | 브랜드 | 용량 | buyBoxPrice | 월 매출 추정 | 월 판매량 | amzMonthlySold | 별점 | 리뷰 수 | 하위 카테고리 | 카테고리 순위 | 판매자 수 | 등록일 | A+ | itemHighlights |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| B00021AJ5I | Calvin Klein | 3.3 Fl Oz (Pack of 1) | 115.54 | 274,061 | 2,372 | 2,000 | 4.5 | 11,648 | Women's Eau de Parfum | 126 | 1 | 2015-03-19 | 아니오 | 비어 있음 |
| B0BZDZJDTG | Dossier | 1.7 Fl Oz (Pack of 1) | 26.12 | 133,865 | 5,125 | 4,000 | 4.4 | 4,196 | Women's Eau de Parfum | 4 | 4 | 2023-04-04 | 예 | 있음 |
| B0009OAI8Q | Elizabeth Taylor | 3.3 Fl Oz (Pack of 1) | 25.73 | 213,893 | 8,313 | 7,000 | 4.6 | 30,049 | Women's Fragrance Sets | 1 | 74 | 2020-01-01 | 예 | 있음 |
| B09X5BQ969 | Bella Vita Luxury | 3.38 Fl Oz (Pack of 1) | 20.99 | 1,133,418 | 53,998 | 50,000 | 3.8 | 18,370 | Women's Eau de Parfum | 39 | 2 | 2022-07-29 | 예 | 비어 있음 |
| B08FBQWRYC | Jean Paul Gaultier | 4.2 Fl Oz (Pack of 1) | 153.10 | 153,866 | 1,005 | 900 | 4.7 | 8,356 | Men's Eau de Parfum | 38 | 1 | 2020-08-06 | 예 | 있음 |
| B0GFGL26JD | Glossier | 1.7 Fl Oz (Pack of 1) | 82.00 | 221,646 | 2,703 | 2,000 | 4.5 | 572 | Women's Eau de Parfum | 13 | 1 | 2026-01-07 | 예 | 있음 |

itemHighlights(응답 원문 그대로, 한 줄 요약):

- B00021AJ5I Calvin Klein: 비어 있음
- B0BZDZJDTG Dossier: 1.7 fl oz (50ml) - Vanilla Perfume - Ambery Vanilla Eau de Parfum for Women - Vanilla Body Spray, Long-Lasting, Vegan
- B0009OAI8Q Elizabeth Taylor: Women's floral chypre eau de toilette. Perfume with notes of lily, neroli, warm amber, and sandalwood.
- B09X5BQ969 Bella Vita Luxury: 비어 있음
- B08FBQWRYC Jean Paul Gaultier: Amber Woody Eau de Parfum Intense for Men Fragrance - Cardamom, Lavender & Iris, Vanilla - Men's Perfume Spray
- B0GFGL26JD Glossier: Warm, Musky & Spicy, Pink Pepper, Iris & Ambrox Base Notes, Smells Different on Everyone, Layer & Mix to Match Your Mood

| ASIN | 이력 | 점 수 | 기간 | 처음 값 | 마지막 값 | 최소 | 최대 |
|---|---|---|---|---|---|---|---|
| B00021AJ5I | amazon | 773 | 2016-10-24 ~ 2026-10-07 | 86.00 | 123.00 | 35.98 | 123.00 |
| B00021AJ5I | buyBoxShipping | 843 | 2017-03-31 ~ 2026-10-07 | 86.00 | 123.00 | 36.00 | 123.00 |
| B00021AJ5I | salesRank | 26,450 | 2016-10-24 ~ 2026-10-07 | 26,099.00 | 13,076.00 | 1,262.00 | 94,179.00 |
| B00021AJ5I | reviewCount | 5,352 | 2017-01-26 ~ 2026-10-07 | 192.00 | 11,781.00 | 1.00 | 11,781.00 |
| B0BZDZJDTG | amazon | 8 | 2026-01-11 ~ 2026-06-01 | 25.97 | 28.94 | 22.62 | 29.00 |
| B0BZDZJDTG | buyBoxShipping | 501 | 2023-04-26 ~ 2026-10-06 | 39.00 | 20.00 | 20.00 | 48.00 |
| B0BZDZJDTG | salesRank | 7,713 | 2023-04-26 ~ 2026-10-07 | 55,622.00 | 1,295.00 | 169.00 | 109,542.00 |
| B0BZDZJDTG | reviewCount | 3,556 | 2023-04-28 ~ 2026-10-07 | 1.00 | 4,296.00 | 1.00 | 8,800.00 |
| B0009OAI8Q | amazon | 4,928 | 2012-05-19 ~ 2026-10-07 | 31.81 | 19.94 | 9.17 | 38.99 |
| B0009OAI8Q | buyBoxShipping | 6,414 | 2017-03-05 ~ 2026-10-07 | 24.00 | 20.00 | 9.00 | 70.00 |
| B0009OAI8Q | salesRank | 34,117 | 2015-02-01 ~ 2026-10-07 | 2,404.00 | 2,126.00 | 116.00 | 29,427.00 |
| B0009OAI8Q | reviewCount | 14,825 | 2017-01-21 ~ 2026-10-07 | 1,252.00 | 30,094.00 | 1.00 | 30,868.00 |
| B09X5BQ969 | amazon | 100 | 2025-04-23 ~ 2026-10-06 | 22.70 | 20.99 | 18.00 | 26.99 |
| B09X5BQ969 | buyBoxShipping | 203 | 2023-10-06 ~ 2026-10-07 | 25.00 | 21.00 | 17.00 | 30.00 |
| B09X5BQ969 | salesRank | 5,912 | 2023-10-31 ~ 2026-10-07 | 291,417.00 | 250.00 | 108.00 | 473,254.00 |
| B09X5BQ969 | reviewCount | 8,451 | 2022-08-23 ~ 2026-10-07 | 8.00 | 18,435.00 | 8.00 | 44,603.00 |
| B08FBQWRYC | amazon | 827 | 2022-05-17 ~ 2026-08-08 | 79.99 | 160.00 | 79.99 | 160.00 |
| B08FBQWRYC | buyBoxShipping | 14,252 | 2020-11-09 ~ 2026-10-07 | 99.00 | 160.00 | 55.00 | 215.00 |
| B08FBQWRYC | salesRank | 15,337 | 2020-11-10 ~ 2026-10-07 | 160,597.00 | 9,892.00 | 1,184.00 | 372,111.00 |
| B08FBQWRYC | reviewCount | 5,835 | 2020-11-10 ~ 2026-10-07 | 20.00 | 8,365.00 | 20.00 | 8,365.00 |
| B0GFGL26JD | buyBoxShipping | 3 | 2026-02-23 ~ 2026-10-07 | 82.00 | 82.00 | 82.00 | 82.00 |
| B0GFGL26JD | salesRank | 924 | 2026-02-23 ~ 2026-10-07 | 314,115.00 | 4,039.00 | 1,345.00 | 314,115.00 |
| B0GFGL26JD | reviewCount | 416 | 2026-02-23 ~ 2026-10-07 | 8.00 | 600.00 | 8.00 | 600.00 |

## 7. 광고와 상위 상품("perfume for women")

### 이 검색어에 광고하는 브랜드(search_terms_advertised_brands)

| 브랜드 | sponsoredProducts | sponsoredBrandWinRate | topGroupWinRate | topSpotWinRate |
|---|---|---|---|---|
| Clinique | 11 | 0.367 | 0.033 | 0.000 |
| Maison Margiela | 2 | 0.167 | 0.000 | 0.000 |
| Cacharel | 5 | 0.133 | 0.000 | 0.000 |
| NovoGlow | 8 | 0.133 | 0.000 | 0.000 |
|  | 9 | 0.133 | 0.133 | 0.033 |
| Calvin Klein | 10 | 0.100 | 0.000 | 0.000 |
| Victoria's Secret | 24 | 0.100 | 0.300 | 0.100 |
| Nest New York | 11 | 0.067 | 0.000 | 0.000 |
| Urban Collection | 10 | 0.067 | 0.067 | 0.000 |
| Ajmal | 7 | 0.033 | 0.000 | 0.033 |
| Elizabeth Arden | 1 | 0.033 | 0.000 | 0.000 |
| GUESS | 8 | 0.033 | 0.067 | 0.000 |
| Viktor&Rolf | 3 | 0.033 | 0.000 | 0.000 |
| ALT. FRAGRANCES | 3 | 0.033 | 0.000 | 0.000 |
| HOUSE OF TWIST | 10 | 0.033 | 0.000 | 0.000 |
| DKNY | 1 | 0.000 | 0.000 | 0.033 |
| Elizabeth Taylor | 3 | 0.000 | 0.067 | 0.000 |
| Estée lauder | 15 | 0.000 | 0.000 | 0.033 |
| Generic | 2 | 0.000 | 0.033 | 0.033 |
| Glossier | 2 | 0.000 | 0.033 | 0.000 |

승률 칸은 응답 값 그대로(단위 미확인).

### 브랜드 광고 검색어(search_terms_ad_spy)

search_terms_ad_spy는 입력이 브랜드 이름이라 검색어로는 부를 수 없어, 우리 6개 중 첫 브랜드(Calvin Klein)로 한 번 불렀습니다. estimatedCpc, totalAdSpend는 단위 미확인.

| 브랜드 | 검색어 | 추정 검색 수 | estimatedCpc | totalAdSpend | sponsoredProducts | topGroupWinRate | topSpotWinRate |
|---|---|---|---|---|---|---|---|
| Calvin Klein | obsession | 313,042 | 1.37 | 44,446.84 | 10 | 0.576 | 0.037 |
| Calvin Klein | calvin klein | 61,733 | 1.52 | 28,056.36 | 87 | 0.667 | 0.600 |
| Calvin Klein | perfume | 177,366 | 1.23 | 13,089.60 | 13 | 0.000 | 0.000 |
| Calvin Klein | fragrances | 104,622 | 1.62 | 11,605.06 | 19 | 0.000 | 0.000 |
| Calvin Klein | calvin klein underwear for men | 143,646 | 1.86 | 11,488.74 | 16 | 0.133 | 0.133 |
| Calvin Klein | cologne | 113,368 | 1.24 | 9,752.46 | 14 | 0.000 | 0.000 |
| Calvin Klein | mens underwear | 325,073 | 2.88 | 9,206.10 | 65 | 0.098 | 0.033 |
| Calvin Klein | eternity | 46,357 | 1.69 | 8,696.10 | 15 | 0.033 | 0.000 |
| Calvin Klein | calvin klein boxer briefs | 29,832 | 1.99 | 8,489.35 | 44 | 0.333 | 0.367 |
| Calvin Klein | boxers for men | 169,304 | 2.36 | 8,390.70 | 3 | 0.000 | 0.000 |
| Calvin Klein | calvin klein men | 26,863 | 1.31 | 7,530.71 | 68 | 0.367 | 0.333 |
| Calvin Klein | euphoria | 58,484 | 1.75 | 7,368.97 | 12 | 0.133 | 0.000 |
| Calvin Klein | ck one | 13,677 | 5.11 | 6,900.43 | 13 | 0.033 | 0.033 |
| Calvin Klein | ariana grande perfume | 64,624 | 1.81 | 5,789.99 | 14 | 0.100 | 0.000 |
| Calvin Klein | calvin klein bra | 40,227 | 1.54 | 5,761.31 | 12 | 0.033 | 0.100 |
| Calvin Klein | polo calvin klein para hombre | 3,933 | 12.58 | 5,590.91 | 9 | 0.067 | 0.867 |
| Calvin Klein | perfumes | 51,189 | 1.23 | 5,288.87 | 13 | 0.000 | 0.000 |
| Calvin Klein | juicy couture perfume | 29,119 | 3.04 | 5,173.74 | 14 | 0.233 | 0.000 |
| Calvin Klein | calvin klein underwear women | 60,918 | 1.16 | 5,158.53 | 8 | 0.033 | 0.033 |
| Calvin Klein | dress socks | 45,617 | 2.18 | 4,872.77 | 18 | 0.333 | 0.133 |

### 이 검색어의 상위 상품(search_terms_trends_top_products)

| 브랜드 | ASIN | 제목 | avgRank | latestRank | 일별 기록 수 |
|---|---|---|---|---|---|
| Elizabeth Taylor | B0009OAI8Q | Elizabeth Taylor White Diamonds Eau de Toilette for Women, 3.3 fl oz | 3.7 | 1 | 595 |
| Vera Wang | B000JL7WQK | Vera Wang Princess Eau de Toilette Spray, Women's Fragrance, 3.4 fl oz | 3.0 | 2 | 595 |
| Versace | B000IEQQCE | Versace Bright Crystal by Versace for Women 1.7 oz Eau de Toilette Spr | 12.2 | 3 | 595 |
| Gucci | B00ZCIHYRM | Gucci Bamboo by Gucci for Women 2.5 oz Eau de Parfum Spray | 4.0 | 4 | 595 |
| GODA | B0F1G3VSLZ | GODA Pheromones Perfume for Women – The Original – Long-Lasting Women' | 5.3 | 5 | 595 |

## 8. 받지 못한 것

- 검색어별 CPC: 카테고리 검색어에는 없음. search_terms_ad_spy(브랜드 하나의 광고 검색어)에만 estimatedCpc가 있어, 이번에는 Calvin Klein 광고 검색어 20개만 받음(단위 미확인).
- 광고비 비중(검색 결과 중 스폰서 비율): 없음. 브랜드별 adSpendShare(경쟁 브랜드 표)와 검색어별 광고 승률만 있음(뜻과 단위 미확인).
- 전체 시장 규모: 아마존 US 노드 월매출(totalMonthlyRevenue)만 있음. 아마존 밖 시장이나 연간 공식 수치는 없음(웹 조사 단계).
- 아마존 직판(1P) 비중: azRevenuePct, sellerRevenuePct 칸은 있으나 뜻을 설명한 문서가 없음(단위 미확인).
- 상품 bullet 전체와 성분표: 칸이 없음. itemHighlights(한 줄 요약)만 6개 중 4개에 있고, 비어 있는 것은 B00021AJ5I, B09X5BQ969.
- subcategories_relevant_search_terms: 첫 시도들이 서버 오류(500), 이름만으로 부른 2번은 두 번 다 실패, 맥락 이름으로 다시 불러 받음.

## 9. 메모

- subcategories_category_competitors를 노드 이름만("Eau de Parfum", "Eau de Toilette")으로 부르면 두 결과가 같고 1위가 Apple(평균 가격 1,364)라 향수 카테고리가 아님. 버리고 subcategoryContextName("Women's Eau de Parfum")으로 다시 부른 결과만 씀.
- Women's Eau de Parfum 관련 검색어 37,624개 중 카테고리 낱말(perfume, parfum, fragrance, cologne, scent, eau de, body mist, mist, edp, edt, toilette)이나 브랜드 이름(상위 20 브랜드와 우리 6개)이 든 것 27,495개를 30일 검색량 순으로 50개. 응답의 relevancy만으로는 "now", "yellowstone" 같은 검색어가 남아 이 규칙을 씀.
- Women's Eau de Toilette 관련 검색어 15,736개 중 카테고리 낱말(perfume, parfum, fragrance, cologne, scent, eau de, body mist, mist, edp, edt, toilette)이나 브랜드 이름(상위 20 브랜드와 우리 6개)이 든 것 12,334개를 30일 검색량 순으로 50개. 응답의 relevancy만으로는 "now", "yellowstone" 같은 검색어가 남아 이 규칙을 씀.

## 10. 도구마다 응답 칸 이름

- subcategories_search: momGrowth, momGrowth12, parentId, id, subcategoryName, totalMonthlyRevenue, totalBrands, totalAsins, avgPrice, avgReviews, avgRating, avgNumberSellers, avgPageScore, avgVolume, totalNumberUnitsSold, totalReviews, subcategoryContextName, sellerRevenuePct, azRevenuePct, avgListedSinceDays, ttm, isParent, level
- subcategories_category_competitors: numberASINs, revenue, totalReviews, reviewRating, avgPrice, avgNumberSellers, avgPageScore, avgVolume, avgReviews, totalNumberUnitsSold, brandName, brandId, marketshare, moMMktShareChange, adSpendShare
- subcategories_relevant_search_terms: searchTermId, searchTermValue, volume30Day, numRelatedProducts, relevancy, current4WkVolume, priorYear4WkVolume, yoYChange, yoYChangePct
- search_terms_trends: searchTerm, estimateSearches, estimateSearchesGrowth12Months, estimateSearchesGrowth6Months, estimateSearchesGrowth3Months, estimateSearchesGrowth1Month, history
- products_byasin: note, category, brand, subcategory, dominantSeller, marketplaceId, variationDimensions, productHistories, trafficSourceCount, trafficLast30Days, variationCount, collectionExcluded, periodRevenue, periodUnitSales, previousPeriodRevenue, previousPeriodUnitSales, periodGrowth, ttmStartDate, ttmEndDate, storefrontUrl, productSummary, productScrapingStat, isSolicitationEnabled, sendAfterDays, amazonAccountTtm, amazonAccountMonthlyRevenue, comparisonPeriodRevenue, amazonAccountComparisonRevenue, id, brandName, categoryId, brandId, dateSeen, ttm, ttmPrev, ttmUnits, momGrowth, momGrowth12, rankScore, rankScoreGrowth, smartScore, smartScoreGrowth, opportunityScore, salesRankDrops30Day, outOfStockRate30Day, priceDrops30Day, businessDiscount, returnRate, inStockRate90Day, buyBoxSuppression45Day, hasVideo, hasAPlus, ttmChange, isParentAsin, amzMonthlySold, competitivePriceThreshold, isSns, unitValue, unitType, eachUnitCount, itemHighlights, hiddenReasonId, subcategoryId, asin, rank, subcategoryRank, numberOfSellers, buyBoxPrice, averageBuyBoxPrice, reviewCount, reviewRating, numberFbaSellers, amazonIsr, monthlyRevenueEstimate, monthlyUnitsSold, outOfStockNow, productPageScore, isVariation, parentAsin, imageCount, imageUrl, title, buyBoxEquity, revenueEquity, marginEquity, partNumber, model, upc, manufacturer, numberOfItems, totalRatings, packageQuantity, size, color, length, height, width, weight, listedSince
- products_history: newFbmShipping, newFba, salesRank, buyBoxShipping, reviewCount, newOfferCount, amazon, firstScrapingDate
- search_terms_advertised_brands: name, sponsoredProducts, sponsoredBrandWinRate, topGroupWinRate, topSpotWinRate
- search_terms_ad_spy: searchTermValue, estimateSearches, estimatedCpc, sponsoredProducts, sponsoredBrandWinRate, sponsoredVideoWinRate, topGroupWinRate, topSpotWinRate, sponsoredBrandSpend, sponsoredVideoSpend, topSpotSpend, topGroupSpend, totalAdSpend
- search_terms_trends_top_products: searchTermValue, brandName, asin, parentAsin, imageUrl, title, avgRank, latestRank, searchTermProductRanksDailies
