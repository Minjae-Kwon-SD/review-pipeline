# 시장 데이터 요약: hairremoval-db-2026-10-08

spd-amz-market(무료)만 썼습니다. 마켓 US, 만든 때 2026-10-09T01:24:08+09:00. 숫자는 응답 값 그대로이고, 칸의 뜻이나 단위가 문서에 없으면 "단위 미확인"으로 적었습니다. 행마다 원본 파일은 market.json의 source에 있습니다.

## 1. 호출 목록

| # | 도구 | 입력 | 결과 | 행 수 | 비고 |
|---|---|---|---|---|---|
| 1 | products_byasin | {"asin": "B07WYY6KKC"} | 성공 | - | 회차 raw/의 같은 날 응답을 복사(호출 없음) |
| 2 | products_variations | {"asin": ""} | 실패 | - | spd-amz-market tools/call: 500 Server Error: Internal Server Error for |
| 3 | products_variations | {"asin": ""} | 실패 | - | spd-amz-market tools/call: 500 Server Error: Internal Server Error for |
| 4 | products_byasin | {"asin": "B0CV3ZJ2PN"} | 성공 | - | 회차 raw/의 같은 날 응답을 복사(호출 없음) |
| 5 | products_variations | {"asin": "B0HBX6NVQZ"} | 성공 | 2 |  |
| 6 | products_byasin | {"asin": "B0CWL9S4L1"} | 성공 | - | 회차 raw/의 같은 날 응답을 복사(호출 없음) |
| 7 | products_variations | {"asin": "B0HH2Z15SV"} | 성공 | 2 |  |
| 8 | products_byasin | {"asin": "B0G39WBP1S"} | 성공 | - | 회차 raw/의 같은 날 응답을 복사(호출 없음) |
| 9 | products_variations | {"asin": ""} | 실패 | - | spd-amz-market tools/call: 500 Server Error: Internal Server Error for |
| 10 | products_variations | {"asin": ""} | 실패 | - | spd-amz-market tools/call: 500 Server Error: Internal Server Error for |
| 11 | products_byasin | {"asin": "B0FGB2NS3C"} | 성공 | - | 회차 raw/의 같은 날 응답을 복사(호출 없음) |
| 12 | products_variations | {"asin": "B0HK5N2BCM"} | 성공 | 4 |  |
| 13 | subcategories_search | {} | 성공 | 31,476 |  |
| 14 | subcategories_category_competitors | {"sub_category_name": "Light Hair Removal Devices", "start_row": 0, "end_row": 20} | 성공 | 20 |  |
| 15 | subcategories_relevant_search_terms | {"subcategory_name": "Light Hair Removal Devices"} | 성공 | 2,097 |  |
| 16 | subcategories_category_competitors | {"sub_category_name": "Laser, Light & Electrolysis Hair Removal", "start_row": 0, "end_row": 20} | 성공 | 6 |  |
| 17 | subcategories_relevant_search_terms | {"subcategory_name": "Laser, Light & Electrolysis Hair Removal"} | 성공 | 2,153 |  |
| 18 | products_history | {"asin": "B07WYY6KKC"} | 성공 | 22,737 |  |
| 19 | products_history | {"asin": "B0CV3ZJ2PN"} | 성공 | 7,873 |  |
| 20 | products_history | {"asin": "B0CWL9S4L1"} | 성공 | 3,445 |  |
| 21 | products_history | {"asin": "B0G39WBP1S"} | 성공 | 1,107 |  |
| 22 | products_history | {"asin": "B0FGB2NS3C"} | 성공 | 2,587 |  |
| 23 | search_terms_advertised_brands | {"search_term": "laser hair removal", "start_row": 0, "end_row": 20} | 성공 | 8 |  |
| 24 | search_terms_trends_top_products | {"search_term": "laser hair removal"} | 성공 | 5 |  |
| 25 | search_terms_ad_spy | {"brand_name": "Braun", "start_row": 0, "end_row": 20} | 성공 | 20 |  |
| 26 | search_terms_trends | {"keyword": "laser hair removal", "months": 12} | 성공 | 100 |  |
| 27 | search_terms_trends | {"keyword": "wavytalk", "months": 12} | 성공 | 100 |  |
| 28 | search_terms_trends | {"keyword": "facial hair removal for women", "months": 12} | 성공 | 77 |  |
| 29 | search_terms_trends | {"keyword": "flawless facial hair removal for women", "months": 12} | 성공 | 6 |  |
| 30 | search_terms_trends | {"keyword": "nair hair remover", "months": 12} | 성공 | 30 |  |
| 31 | search_terms_trends | {"keyword": "phofay smooth hair removal", "months": 12} | 성공 | 4 |  |
| 32 | search_terms_trends | {"keyword": "braun series 9 pro", "months": 12} | 성공 | 60 |  |
| 33 | search_terms_trends | {"keyword": "laser", "months": 12} | 성공 | 100 |  |
| 34 | search_terms_trends | {"keyword": "hair removal device", "months": 12} | 성공 | 100 |  |
| 35 | search_terms_trends | {"keyword": "hair removal", "months": 12} | 성공 | 100 |  |
| 36 | search_terms_trends | {"keyword": "laser hair removal", "months": 24} | 성공 | 100 |  |
| 37 | search_terms_trends | {"keyword": "hair removal device", "months": 24} | 성공 | 100 |  |
| 38 | search_terms_trends | {"keyword": "ipl laser hair removal", "months": 24} | 성공 | 87 |  |
| 39 | search_terms_trends | {"keyword": "laser hair removal for women", "months": 24} | 성공 | 59 |  |
| 40 | search_terms_trends | {"keyword": "ulike air 10", "months": 24} | 성공 | 8 |  |
| 41 | search_terms_trends | {"keyword": "hair removal", "months": 24} | 성공 | 100 |  |

실제 호출 36번(한도 40번), 실패 4번.

## 2. 하위 카테고리(카테고리 노드와 위 노드)

월 매출, 판매량은 칸 이름(totalMonthlyRevenue, totalNumberUnitsSold) 그대로이고 통화와 기간은 문서에 없어 단위 미확인. 증감(momGrowth, momGrowth12), azRevenuePct, sellerRevenuePct도 단위 미확인.

| 노드 id | 이름 | 월 매출 | 판매량 | 브랜드 수 | ASIN 수 | 평균 가격 | 평균 별점 | momGrowth | momGrowth12 | azRevenuePct | sellerRevenuePct |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 3778591 | Shaving & Hair Removal Products | 174,201,217 | 7,995,832 | 5,667 | 32,057 | 31.36 | 4.20 | -0.06 | 0.16 | 0.4974 | 0.5026 |
| 13269990011 | Women's Shaving & Hair Removal Products | 63,134,269 | 3,588,530 | 2,650 | 11,515 | 35.05 | 4.15 | -0.13 | 0.21 | 0.4358 | 0.5642 |
| 13406780011 | Laser, Light & Electrolysis Hair Removal | 8,196,134 | 38,486 | 89 | 235 | 174.57 | 4.03 | -0.43 | 0.16 | 0.5019 | 0.4981 |
| 7676395011 | Light Hair Removal Devices | 7,815,692 | 36,752 | 85 | 222 | 160.46 | 4.09 | -0.44 | 0.18 | 0.4789 | 0.5211 |

## 3. 브랜드 상위 20: Light Hair Removal Devices

marketshare, moMMktShareChange, adSpendShare는 응답 값 그대로(단위 미확인). revenue는 칸 이름 그대로(기간과 통화 단위 미확인).

| 순위 | 브랜드 | revenue | marketshare | moMMktShareChange | ASIN 수 | 판매량 | 평균 가격 | 평균 별점 | 리뷰 수 | adSpendShare |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Braun | 2,977,059 | 0.3809 | 0.0870 | 9 | 7,507 | 372.70 | 4.17 | 11,125 | 0.183 |
| 2 | Ulike | 1,315,825 | 0.1684 | -0.0597 | 8 | 3,840 | 315.01 | 4.24 | 9,948 | 0.202 |
| 3 | INNZA | 1,176,360 | 0.1505 | -0.0323 | 3 | 12,897 | 94.64 | 4.30 | 6,603 | 0.123 |
| 4 | PHILIPS | 747,752 | 0.0957 | 0.0229 | 5 | 1,286 | 525.96 | 4.24 | 1,000 | 0.126 |
| 5 | Nood | 717,750 | 0.0918 | 0.0042 | 7 | 2,433 | 289.23 | 4.15 | 1,545 | 0.152 |
| 6 | wavytalk | 229,022 | 0.0293 | -0.0035 | 9 | 1,155 | 161.59 | 4.44 | 1,484 | 0.067 |
| 7 | Ubroo | 142,192 | 0.0182 | -0.0046 | 14 | 1,735 | 88.14 | 4.37 | 4,552 | 0.018 |
| 8 | Oreeth | 129,503 | 0.0166 | 0.0097 | 20 | 1,615 | 111.36 | 4.12 | 1,405 | 0.004 |
| 9 | AMOTAOS | 47,458 | 0.0061 | -0.0126 | 7 | 590 | 99.28 | 3.66 | 198 | 0.001 |
| 10 | DermRays | 38,260 | 0.0049 | 0.0006 | 3 | 88 | 572.23 | 3.60 | 231 | 0.067 |
| 11 | INIA | 36,918 | 0.0047 | 0.0002 | 1 | 316 | 116.83 | 4.50 | 574 | 0.008 |
| 12 | BoSidin | 24,190 | 0.0031 | -0.0003 | 2 | 121 | 199.84 | 4.50 | 664 | 0.007 |
| 13 | MICHAEL TODD | 23,542 | 0.0030 | 0.0009 | 2 | 158 | 149.00 | 4.30 | 104 | 0.008 |
| 14 | TAKSOME | 21,880 | 0.0028 | -0.0078 | 2 | 241 | 60.38 | 4.05 | 182 | - |
| 15 | Vitaly | 16,162 | 0.0021 | -0.0012 | 1 | 196 | 82.46 | 4.40 | 60 | 0.003 |
| 16 | SmoothSkin | 16,059 | 0.0021 | -0.0001 | 7 | 64 | 207.96 | 3.66 | 842 | - |
| 17 | Zjyufy | 12,223 | 0.0016 | 0.0006 | 1 | 440 | 27.78 | 3.60 | 341 | - |
| 18 | LYSMOSKI | 10,017 | 0.0013 | 0.0003 | 6 | 130 | 80.54 | 4.25 | 1,791 | - |
| 19 | MEUKPE | 9,762 | 0.0012 | -0.0007 | 1 | 252 | 38.74 | 4.00 | 364 | - |
| 20 | BLHVSINO1 | 9,148 | 0.0012 | -0.0002 | 1 | 183 | 49.99 | 4.10 | 26 | - |

## 3. 브랜드 상위 20: Laser, Light & Electrolysis Hair Removal

marketshare, moMMktShareChange, adSpendShare는 응답 값 그대로(단위 미확인). revenue는 칸 이름 그대로(기간과 통화 단위 미확인).

| 순위 | 브랜드 | revenue | marketshare | moMMktShareChange | ASIN 수 | 판매량 | 평균 가격 | 평균 별점 | 리뷰 수 | adSpendShare |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Braun | 370,594 | 0.9741 | 0.0058 | 3 | 872 | 301.52 | 4.23 | 1,567 | 0.981 |
| 2 | RoseVee | 7,444 | 0.0196 | -0.0047 | 1 | 829 | 8.98 | 4.40 | 3,518 | 0.002 |
| 3 | Gransumr | 1,787 | 0.0047 | 0.0004 | 1 | 10 | 178.72 | 4.30 | 740 | - |
| 4 | TKSHINY | 347 | 0.0009 | -0.0013 | 1 | 22 | 15.79 | 3.90 | 39 | 0.004 |
| 5 | Ulike | 269 | 0.0007 | -0.0002 | 1 | 1 | 269.00 | - | 188 | 0.013 |
| 6 | Tria Beauty | 0 | 0.0000 | 0.0000 | 1 | 0 | 449.00 | 3.80 | 209 | - |

## 4. 검색어 상위 50: Light Hair Removal Devices

| 순위 | 검색어 | 30일 검색량 | 최근 4주 | 작년 같은 4주 | yoYChange | yoYChangePct | relevancy |
|---|---|---|---|---|---|---|---|
| 1 | wavytalk | 129,382 | 127,645 | 85,991 | 41,654 | 0.4844 | 58 |
| 2 | facial hair removal for women | 116,098 | 115,375 | 101,372 | 14,003 | 0.1381 | 60 |
| 3 | laser hair removal | 94,410 | 93,071 | 91,922 | 1,149 | 0.0125 | 77 |
| 4 | flawless facial hair removal for women | 82,954 | 82,077 | 38,168 | 43,909 | 1.1504 | 35 |
| 5 | nair hair remover | 72,165 | 75,239 | 80,254 | -5,015 | -0.0625 | 52 |
| 6 | phofay smooth hair removal | 49,114 | 53,408 | - | - | - | 64 |
| 7 | braun series 9 pro | 48,085 | 47,162 | 38,247 | 8,915 | 0.2331 | 44 |
| 8 | laser | 39,084 | 38,246 | 43,243 | -4,997 | -0.1156 | 62 |
| 9 | hair removal device | 38,559 | 39,233 | 40,305 | -1,072 | -0.0266 | 60 |
| 10 | hair removal | 37,895 | 40,426 | 34,964 | 5,462 | 0.1562 | 56 |
| 11 | ipl laser hair removal | 36,306 | 36,132 | 31,536 | 4,596 | 0.1457 | 69 |
| 12 | michael todd beauty dermaplaning | 32,850 | 37,542 | 17,970 | 19,572 | 1.0891 | 30 |
| 13 | veet hair removal cream for women | 32,715 | 36,684 | 40,655 | -3,971 | -0.0977 | 56 |
| 14 | braun | 29,119 | 28,962 | 27,827 | 1,135 | 0.0408 | 50 |
| 15 | laser hair removal for women | 27,557 | 27,376 | 33,651 | -6,275 | -0.1865 | 66 |
| 16 | ulike air 10 | 27,378 | 26,473 | 14,873 | 11,600 | 0.7799 | 67 |
| 17 | braun ipl | 25,973 | 25,719 | 16,207 | 9,512 | 0.5869 | 67 |
| 18 | philips lumea | 22,493 | 19,031 | 23,003 | -3,972 | -0.1727 | 66 |
| 19 | face hair removal for women | 22,164 | 24,138 | 19,895 | 4,243 | 0.2133 | 52 |
| 20 | facial hair remover | 21,041 | 20,865 | 20,468 | 397 | 0.0194 | 52 |
| 21 | braun silk expert pro 5 | 19,275 | 24,081 | 16,667 | 7,414 | 0.4448 | 61 |
| 22 | lazer hair removal for women | 19,238 | 18,796 | 17,643 | 1,153 | 0.0654 | 64 |
| 23 | braun series 7 | 18,672 | 16,784 | 15,668 | 1,116 | 0.0712 | 47 |
| 24 | hair remover | 16,976 | 19,747 | 18,896 | 851 | 0.0450 | 48 |
| 25 | innza laser hair removal | 15,923 | 13,179 | 11,586 | 1,593 | 0.1375 | 62 |
| 26 | braun nevo | 15,553 | 15,490 | - | - | - | 48 |
| 27 | ulike laser hair removal for women | 15,338 | 15,230 | - | - | - | 60 |
| 28 | braun epilator | 15,053 | 17,411 | 11,096 | 6,315 | 0.5691 | 18 |
| 29 | ipl | 15,024 | 15,391 | 13,667 | 1,724 | 0.1261 | 63 |
| 30 | inia | 14,989 | 15,159 | 11,093 | 4,066 | 0.3665 | 36 |
| 31 | ulike | 14,614 | 14,675 | 14,791 | -116 | -0.0078 | 60 |
| 32 | fay hair remover | 14,587 | 13,069 | - | - | - | 40 |
| 33 | philips | 14,282 | 14,567 | 15,035 | -468 | -0.0311 | 45 |
| 34 | lumea philips laser | 14,129 | 13,463 | 7,064 | 6,399 | 0.9059 | 62 |
| 35 | inza laser hair removal | 13,811 | 9,794 | 6,285 | 3,509 | 0.5583 | 62 |
| 36 | chin hair removal for women | 13,787 | 12,939 | 11,488 | 1,451 | 0.1263 | 46 |
| 37 | inzza laser hair removal | 13,700 | 11,773 | 7,538 | 4,235 | 0.5618 | 60 |
| 38 | tattoo removal laser | 13,388 | 14,081 | 10,665 | 3,416 | 0.3203 | 22 |
| 39 | nair bikini area hair remover | 13,163 | 14,065 | - | - | - | 12 |
| 40 | braun series 5 | 12,986 | 12,960 | 10,702 | 2,258 | 0.2110 | 43 |
| 41 | nood | 12,607 | 14,043 | 12,500 | 1,543 | 0.1234 | 28 |
| 42 | hair remover for women | 12,393 | 13,331 | 9,140 | 4,191 | 0.4585 | 50 |
| 43 | innza | 12,213 | 10,944 | 7,255 | 3,689 | 0.5085 | 61 |
| 44 | botane man hair removal | 11,900 | 11,913 | 19,339 | -7,426 | -0.3840 | 44 |
| 45 | phofay cloud sense hair removal spray | 11,507 | 13,262 | - | - | - | 48 |
| 46 | inia fascior body sculpting & recovery device | 11,488 | 10,022 | - | - | - | 21 |
| 47 | face hair remover | 11,204 | 11,170 | 10,355 | 815 | 0.0787 | 41 |
| 48 | facial hair removal cream | 11,203 | 10,920 | 13,187 | -2,267 | -0.1719 | 23 |
| 49 | braun laser hair removal | 11,182 | 11,246 | 12,530 | -1,284 | -0.1025 | 60 |
| 50 | depiladora laser | 11,068 | 11,118 | 10,070 | 1,048 | 0.1041 | 60 |

## 4. 검색어 상위 50: Laser, Light & Electrolysis Hair Removal

| 순위 | 검색어 | 30일 검색량 | 최근 4주 | 작년 같은 4주 | yoYChange | yoYChangePct | relevancy |
|---|---|---|---|---|---|---|---|
| 1 | wavytalk | 129,382 | 127,645 | 85,991 | 41,654 | 0.4844 | 58 |
| 2 | facial hair removal for women | 116,098 | 115,375 | 101,372 | 14,003 | 0.1381 | 60 |
| 3 | laser hair removal | 94,410 | 93,071 | 91,922 | 1,149 | 0.0125 | 77 |
| 4 | flawless facial hair removal for women | 82,954 | 82,077 | 38,168 | 43,909 | 1.1504 | 35 |
| 5 | nair hair remover | 72,165 | 75,239 | 80,254 | -5,015 | -0.0625 | 52 |
| 6 | phofay smooth hair removal | 49,114 | 53,408 | - | - | - | 64 |
| 7 | braun series 9 pro | 48,085 | 47,162 | 38,247 | 8,915 | 0.2331 | 44 |
| 8 | laser | 39,084 | 38,246 | 43,243 | -4,997 | -0.1156 | 62 |
| 9 | hair removal device | 38,559 | 39,233 | 40,305 | -1,072 | -0.0266 | 60 |
| 10 | hair removal | 37,895 | 40,426 | 34,964 | 5,462 | 0.1562 | 56 |
| 11 | ipl laser hair removal | 36,306 | 36,132 | 31,536 | 4,596 | 0.1457 | 69 |
| 12 | michael todd beauty dermaplaning | 32,850 | 37,542 | 17,970 | 19,572 | 1.0891 | 30 |
| 13 | veet hair removal cream for women | 32,715 | 36,684 | 40,655 | -3,971 | -0.0977 | 56 |
| 14 | braun | 29,119 | 28,962 | 27,827 | 1,135 | 0.0408 | 53 |
| 15 | laser hair removal for women | 27,557 | 27,376 | 33,651 | -6,275 | -0.1865 | 66 |
| 16 | ulike air 10 | 27,378 | 26,473 | 14,873 | 11,600 | 0.7799 | 68 |
| 17 | braun ipl | 25,973 | 25,719 | 16,207 | 9,512 | 0.5869 | 68 |
| 18 | philips lumea | 22,493 | 19,031 | 23,003 | -3,972 | -0.1727 | 66 |
| 19 | face hair removal for women | 22,164 | 24,138 | 19,895 | 4,243 | 0.2133 | 52 |
| 20 | facial hair remover | 21,041 | 20,865 | 20,468 | 397 | 0.0194 | 52 |
| 21 | braun silk expert pro 5 | 19,275 | 24,081 | 16,667 | 7,414 | 0.4448 | 61 |
| 22 | lazer hair removal for women | 19,238 | 18,796 | 17,643 | 1,153 | 0.0654 | 65 |
| 23 | braun series 7 | 18,672 | 16,784 | 15,668 | 1,116 | 0.0712 | 47 |
| 24 | hair remover | 16,976 | 19,747 | 18,896 | 851 | 0.0450 | 48 |
| 25 | innza laser hair removal | 15,923 | 13,179 | 11,586 | 1,593 | 0.1375 | 63 |
| 26 | braun nevo | 15,553 | 15,490 | - | - | - | 51 |
| 27 | ulike laser hair removal for women | 15,338 | 15,230 | - | - | - | 60 |
| 28 | braun epilator | 15,053 | 17,411 | 11,096 | 6,315 | 0.5691 | 18 |
| 29 | ipl | 15,024 | 15,391 | 13,667 | 1,724 | 0.1261 | 63 |
| 30 | inia | 14,989 | 15,159 | 11,093 | 4,066 | 0.3665 | 36 |
| 31 | ulike | 14,614 | 14,675 | 14,791 | -116 | -0.0078 | 61 |
| 32 | fay hair remover | 14,587 | 13,069 | - | - | - | 40 |
| 33 | philips | 14,282 | 14,567 | 15,035 | -468 | -0.0311 | 45 |
| 34 | lumea philips laser | 14,129 | 13,463 | 7,064 | 6,399 | 0.9059 | 63 |
| 35 | inza laser hair removal | 13,811 | 9,794 | 6,285 | 3,509 | 0.5583 | 62 |
| 36 | chin hair removal for women | 13,787 | 12,939 | 11,488 | 1,451 | 0.1263 | 46 |
| 37 | inzza laser hair removal | 13,700 | 11,773 | 7,538 | 4,235 | 0.5618 | 61 |
| 38 | tattoo removal laser | 13,388 | 14,081 | 10,665 | 3,416 | 0.3203 | 22 |
| 39 | nair bikini area hair remover | 13,163 | 14,065 | - | - | - | 12 |
| 40 | braun series 5 | 12,986 | 12,960 | 10,702 | 2,258 | 0.2110 | 48 |
| 41 | nood | 12,607 | 14,043 | 12,500 | 1,543 | 0.1234 | 28 |
| 42 | hair remover for women | 12,393 | 13,331 | 9,140 | 4,191 | 0.4585 | 50 |
| 43 | innza | 12,213 | 10,944 | 7,255 | 3,689 | 0.5085 | 61 |
| 44 | botane man hair removal | 11,900 | 11,913 | 19,339 | -7,426 | -0.3840 | 44 |
| 45 | phofay cloud sense hair removal spray | 11,507 | 13,262 | - | - | - | 48 |
| 46 | inia fascior body sculpting & recovery device | 11,488 | 10,022 | - | - | - | 21 |
| 47 | face hair remover | 11,204 | 11,170 | 10,355 | 815 | 0.0787 | 41 |
| 48 | facial hair removal cream | 11,203 | 10,920 | 13,187 | -2,267 | -0.1719 | 23 |
| 49 | braun laser hair removal | 11,182 | 11,246 | 12,530 | -1,284 | -0.1025 | 60 |
| 50 | depiladora laser | 11,068 | 11,118 | 10,070 | 1,048 | 0.1041 | 60 |

## 5. 검색어 추이(search_terms_trends, 12개월)

growth 칸은 응답 값 그대로(estimateSearchesGrowth1Month 등, 단위 미확인). 카테고리 검색어 표시가 아니오인 것은 처음 고른 규칙(relevancy만)으로 잘못 고른 검색어라 해석에 쓰지 않습니다.

| 검색어 | 카테고리 검색어 | 추정 검색 수 | 1개월 | 3개월 | 6개월 | 12개월 | 이력 기간 | 주 수 | 첫 주 | 마지막 주 |
|---|---|---|---|---|---|---|---|---|---|---|
| laser hair removal | 예 | 94,410 | -5,001 | -62,785 | -25,453 | 3,810 | 2025-09-21 ~ 2026-09-27 | 54 | 90,600 | 94,410 |
| wavytalk | 예 | 129,382 | 4,906 | -4,958 | 17,913 | 33,454 | 2025-09-21 ~ 2026-09-27 | 54 | 95,928 | 129,382 |
| facial hair removal for women | 예 | 116,098 | -7,663 | 15,024 | 4,406 | 18,520 | 2025-09-21 ~ 2026-09-27 | 54 | 97,578 | 116,098 |
| flawless facial hair removal for women | 예 | 82,954 | -9,701 | 7,686 | -5,237 | 45,553 | 2025-09-21 ~ 2026-09-27 | 54 | 37,401 | 82,954 |
| nair hair remover | 예 | 72,165 | -26,146 | -8,903 | -16,536 | -7,830 | 2025-09-21 ~ 2026-09-27 | 54 | 79,995 | 72,165 |
| phofay smooth hair removal | 예 | 49,114 | -15,702 | 14,117 | 20,283 | 44,424 | 2025-09-21 ~ 2026-09-27 | 54 | 0 | 49,114 |
| braun series 9 pro | 예 | 48,085 | -3,319 | -13,835 | -1,307 | 9,507 | 2025-09-21 ~ 2026-09-27 | 54 | 38,578 | 48,085 |
| laser | 예 | 39,084 | 736 | -4,814 | -13,082 | -4,415 | 2025-09-21 ~ 2026-09-27 | 54 | 43,499 | 39,084 |
| hair removal device | 예 | 38,559 | -3,324 | -3,010 | -131 | -985 | 2025-09-21 ~ 2026-09-27 | 54 | 39,544 | 38,559 |
| hair removal | 예 | 37,895 | -217 | -15,481 | -12,927 | 2,531 | 2025-09-21 ~ 2026-09-27 | 54 | 35,364 | 37,895 |
| ipl laser hair removal | 예 | 응답에 그 검색어 행 없음 | | | | | | | | |
| laser hair removal for women | 예 | 응답에 그 검색어 행 없음 | | | | | | | | |
| ulike air 10 | 예 | 응답에 그 검색어 행 없음 | | | | | | | | |

## 6. 우리 상품 6개(products_byasin, products_history)

monthlyRevenueEstimate, monthlyUnitsSold, amzMonthlySold는 칸 이름 그대로(단위 미확인). 가격 이력(amazon, buyBoxShipping)과 순위 이력(salesRank)의 값 단위는 문서에 없어 단위 미확인이고, 같은 날의 buyBoxPrice와 나란히 적었습니다.

| ASIN | 브랜드 | 용량 | buyBoxPrice | 월 매출 추정 | 월 판매량 | amzMonthlySold | 별점 | 리뷰 수 | 하위 카테고리 | 카테고리 순위 | 판매자 수 | 등록일 | A+ | itemHighlights |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| B07WYY6KKC | Braun | 1 Count (Pack of 1) | 377.16 | 1,741,725 | 4,618 | 4,000 | 4.2 | 7,329 | Light Hair Removal Devices | 2 | 1 | 2019-10-03 | 예 | 비어 있음 |
| B0CV3ZJ2PN | Ulike | Air 10 | 349.00 | 686,832 | 1,968 | 1,000 | 4.3 | 2,991 | Light Hair Removal Devices | 4 | 1 | 2024-02-06 | 예 | 비어 있음 |
| B0CWL9S4L1 | INNZA | None | 90.42 | 866,314 | 9,581 | 9,000 | 4.4 | 3,290 | Light Hair Removal Devices | 1 | 1 | 2024-02-27 | 예 | 있음 |
| B0G39WBP1S | Ulike | None | 347.08 | 387,688 | 1,117 | 1,000 | 4.5 | 228 | Light Hair Removal Devices | 8 | 1 | 2025-11-21 | 예 | 비어 있음 |
| B0FGB2NS3C | PHILIPS | Body+Face+Bikini+Underarm | 579.97 | 365,381 | 630 | 600 | 4.3 | 245 | Light Hair Removal Devices | 23 | 1 | 2025-07-01 | 예 | 있음 |

itemHighlights(응답 원문 그대로, 한 줄 요약):

- B07WYY6KKC Braun: 비어 있음
- B0CV3ZJ2PN Ulike: 비어 있음
- B0CWL9S4L1 INNZA: Long-Lasting Results,999,999 Flashes Painless Hair Removal, for Armpits Legs Arms Bikini Line,Corded, White
- B0G39WBP1S Ulike: 비어 있음
- B0FGB2NS3C PHILIPS: Laser Hair Removal Alternative, Easy Home Use, Medical Grade Safety, 4 Attachments (Body, Face, Bikini & Armpits), BRI984/03

| ASIN | 이력 | 점 수 | 기간 | 처음 값 | 마지막 값 | 최소 | 최대 |
|---|---|---|---|---|---|---|---|
| B07WYY6KKC | amazon | 943 | 2019-10-06 ~ 2026-10-08 | 329.94 | 399.99 | 239.99 | 536.14 |
| B07WYY6KKC | buyBoxShipping | 2,810 | 2019-10-12 ~ 2026-10-08 | 330.00 | 400.00 | 240.00 | 469.00 |
| B07WYY6KKC | salesRank | 22,737 | 2019-10-15 ~ 2026-10-08 | 291,456.00 | 2,284.00 | 199.00 | 1,267,348.00 |
| B07WYY6KKC | reviewCount | 8,775 | 2020-01-03 ~ 2026-10-08 | 54.00 | 7,335.00 | 18.00 | 7,335.00 |
| B0CV3ZJ2PN | buyBoxShipping | 288 | 2024-03-28 ~ 2026-10-08 | 399.00 | 349.00 | 244.00 | 399.00 |
| B0CV3ZJ2PN | salesRank | 7,873 | 2024-04-08 ~ 2026-10-08 | 258,942.00 | 3,123.00 | 703.00 | 491,895.00 |
| B0CV3ZJ2PN | reviewCount | 3,363 | 2024-04-16 ~ 2026-10-08 | 4.00 | 3,011.00 | 4.00 | 3,011.00 |
| B0CWL9S4L1 | buyBoxShipping | 146 | 2024-04-19 ~ 2026-10-08 | 86.00 | 100.00 | 61.00 | 100.00 |
| B0CWL9S4L1 | salesRank | 3,445 | 2024-04-20 ~ 2026-10-08 | 667.00 | 403.00 | 329.00 | 1,771,486.00 |
| B0CWL9S4L1 | reviewCount | 1,470 | 2024-04-19 ~ 2026-10-08 | 61.00 | 3,327.00 | 1.00 | 3,327.00 |
| B0G39WBP1S | buyBoxShipping | 26 | 2025-12-13 ~ 2026-10-08 | 399.00 | 299.00 | 279.00 | 399.00 |
| B0G39WBP1S | salesRank | 1,107 | 2026-01-23 ~ 2026-10-08 | 123,985.00 | 24,319.00 | 5,831.00 | 200,872.00 |
| B0G39WBP1S | reviewCount | 333 | 2026-01-25 ~ 2026-10-08 | 2.00 | 276.00 | 2.00 | 276.00 |
| B0FGB2NS3C | amazon | 34 | 2025-08-03 ~ 2026-10-08 | 579.99 | 579.95 | 399.99 | 579.99 |
| B0FGB2NS3C | buyBoxShipping | 36 | 2025-08-03 ~ 2026-10-08 | 580.00 | 580.00 | 400.00 | 580.00 |
| B0FGB2NS3C | salesRank | 2,587 | 2025-08-08 ~ 2026-10-08 | 143,017.00 | 7,160.00 | 4,099.00 | 143,017.00 |
| B0FGB2NS3C | reviewCount | 473 | 2025-08-30 ~ 2026-10-08 | 1.00 | 253.00 | 1.00 | 587.00 |

## 7. 광고와 상위 상품("laser hair removal")

### 이 검색어에 광고하는 브랜드(search_terms_advertised_brands)

| 브랜드 | sponsoredProducts | sponsoredBrandWinRate | topGroupWinRate | topSpotWinRate |
|---|---|---|---|---|
| Braun | 6 | 0.867 | 0.167 | 0.000 |
| Ulike | 8 | 0.433 | 0.300 | 0.533 |
| PHILIPS | 3 | 0.267 | 0.067 | 0.000 |
|  | 10 | 0.200 | 0.167 | 0.000 |
| INNZA | 2 | 0.000 | 0.400 | 0.100 |
| wavytalk | 2 | 0.000 | 0.367 | 0.000 |
| Nood | 3 | 0.000 | 0.200 | 0.000 |
| Ubroo | 4 | 0.000 | 0.133 | 0.000 |

승률 칸은 응답 값 그대로(단위 미확인).

### 브랜드 광고 검색어(search_terms_ad_spy)

search_terms_ad_spy는 입력이 브랜드 이름이라 검색어로는 부를 수 없어, 우리 상품의 첫 브랜드(Braun)로 한 번 불렀습니다. estimatedCpc, totalAdSpend는 단위 미확인.

| 브랜드 | 검색어 | 추정 검색 수 | estimatedCpc | totalAdSpend | sponsoredProducts | topGroupWinRate | topSpotWinRate |
|---|---|---|---|---|---|---|---|
| Braun | foil shaver | 128,003 | 2.65 | 67,841.54 | 14 | 0.467 | 0.367 |
| Braun | electric razor for men | 145,317 | 3.08 | 58,184.92 | 14 | 0.333 | 0.333 |
| Braun | electric shavers for men | 90,430 | 2.28 | 41,236.13 | 13 | 0.500 | 0.567 |
| Braun | laser hair removal | 94,410 | 3.64 | 32,990.62 | 6 | 0.167 | 0.000 |
| Braun | shavers for men | 70,542 | 2.16 | 25,598.29 | 13 | 0.433 | 0.400 |
| Braun | trimmer for men | 84,839 | 2.05 | 24,000.96 | 11 | 0.367 | 0.400 |
| Braun | electric razor | 60,223 | 2.15 | 22,140.96 | 12 | 0.467 | 0.400 |
| Braun | mens electric razor | 33,779 | 3.00 | 19,254.04 | 13 | 0.433 | 0.533 |
| Braun | electric shaver | 43,805 | 2.03 | 19,029.78 | 13 | 0.533 | 0.633 |
| Braun | immersion blender | 233,427 | 1.23 | 18,057.08 | 6 | 0.145 | 0.181 |
| Braun | braun series 9 | 15,534 | 3.96 | 17,162.60 | 15 | 0.600 | 0.600 |
| Braun | philips lumea | 22,493 | 10.38 | 16,343.41 | 5 | 0.333 | 0.133 |
| Braun | hair removal device | 38,559 | 3.26 | 15,838.48 | 6 | 0.267 | 0.200 |
| Braun | beard trimmer | 103,535 | 2.41 | 15,719.72 | 4 | 0.233 | 0.300 |
| Braun | beard trimmer for men | 209,518 | 2.69 | 15,535.46 | 10 | 0.188 | 0.118 |
| Braun | braun series 9 pro | 48,085 | 2.05 | 15,279.00 | 21 | 0.300 | 0.367 |
| Braun | braun | 29,119 | 2.00 | 15,141.86 | 21 | 0.567 | 0.467 |
| Braun | shaver | 57,766 | 2.05 | 14,447.31 | 14 | 0.333 | 0.367 |
| Braun | ipl laser hair removal | 36,306 | 3.58 | 11,567.82 | 6 | 0.100 | 0.067 |
| Braun | braun silk expert pro 5 ipl | 4,606 | 8.12 | 11,328.79 | 8 | 0.806 | 0.710 |

### 이 검색어의 상위 상품(search_terms_trends_top_products)

| 브랜드 | ASIN | 제목 | avgRank | latestRank | 일별 기록 수 |
|---|---|---|---|---|---|
| INNZA | B0CWL9S4L1 | INNZA IPL Hair Removal with Ice Cooling Care Function for Women and me | 1.0 | 1 | 602 |
| Braun | B07WYY6KKC | Braun IPL, Silk·Expert Pro 5, IPL Hair Removal for Women and Men, Perm | 2.7 | 2 | 602 |
| Ulike | B0CV3ZJ2PN | Ulike Laser Hair Removal Device Air 10 Ipl Gift for Women and Men, Ice | 8.6 | 3 | 602 |
| Braun | B0CMW1N2WC | Braun Skin i-Expert Smart IPL PL7219 at Home Laser Hair Removal for Wo | 5.3 | 4 | 602 |
| INNZA | B0BKKYPP9S | INNZA IPL Hair Removal with Ice Cooling Care Function for Women | 2.5 | 5 | 602 |

## 8. 받지 못한 것

- 검색어별 CPC: 카테고리 검색어에는 없음. search_terms_ad_spy(브랜드 하나의 광고 검색어)에만 estimatedCpc가 있어, 이번에는 Braun 광고 검색어 20개만 받음(단위 미확인).
- 광고비 비중(검색 결과 중 스폰서 비율): 없음. 브랜드별 adSpendShare(경쟁 브랜드 표)와 검색어별 광고 승률만 있음(뜻과 단위 미확인).
- 전체 시장 규모: 아마존 US 노드 월매출(totalMonthlyRevenue)만 있음. 아마존 밖 시장이나 연간 공식 수치는 없음(웹 조사 단계).
- 아마존 직판(1P) 비중: azRevenuePct, sellerRevenuePct 칸은 있으나 뜻을 설명한 문서가 없음(단위 미확인).
- 상품 bullet 전체와 성분표: 칸이 없음. itemHighlights(한 줄 요약)만 5개 중 2개에 있고, 비어 있는 것은 B07WYY6KKC, B0CV3ZJ2PN, B0G39WBP1S.
- 실패한 호출: products_variations, products_variations, products_variations, products_variations

## 9. 메모

- Light Hair Removal Devices 관련 검색어 2,097개 중 카테고리 낱말(ipl, laser, hair removal, hair remover, light hair, permanent hair)이나 브랜드 이름(상위 20 브랜드와 우리 6개)이 든 것 1,767개를 30일 검색량 순으로 50개. 응답의 relevancy만으로는 "now", "yellowstone" 같은 검색어가 남아 이 규칙을 씀.
- Laser, Light & Electrolysis Hair Removal 관련 검색어 2,153개 중 카테고리 낱말(ipl, laser, hair removal, hair remover, light hair, permanent hair)이나 브랜드 이름(상위 20 브랜드와 우리 6개)이 든 것 1,806개를 30일 검색량 순으로 50개. 응답의 relevancy만으로는 "now", "yellowstone" 같은 검색어가 남아 이 규칙을 씀.

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
