# 고치지 않고 남긴 의심 태그 (hairremoval-db-2026-10-08)

출처: 04_tag_audit.yaml(stage: tags, 표본 150개 중 FAIL 23개).
결정: 06_tag_check needs_human에서 담당자 위임(2026-10-08 21:54:40 KST "너가 판단가능한거는 일단해봐")에 따라 Claude가 "이대로 진행"으로 정함. 다시 태깅하지 않았고 재시도 상한은 바꾸지 않았다. 04_tags.jsonl은 그대로다.
원인: 20개는 총평이 없는 리뷰에 overall을 단 것(이유 속성만 말하는 인용을 overall로 달아 이유 주제와 두 번 집계, 스키마 overall exclude와 confusions 충돌), 3개는 개별 실수(R2Z9MITKBORPPL, R3OKWM306XWINV, R12DL2XYKNVTLP).

| review_id | 주제 | 이유 |
|---|---|---|
| R2A9JP5INWC1G7 | overall | 'Easy to use and effective too'는 사용 편의와 효과 속성뿐이고 둘 다 ease_of_use, hair_reduction에 따로 있음 |
| R67FII42ZG841 | overall | 'No change'는 효과 이야기로 hair_reduction(이미 있음) |
| R3APZ6JWV7H4XD | overall | 'No results'는 효과 이야기로 hair_reduction(이미 있음) |
| R34MDGSMXQ8YWH | overall | 문신 위 화상 인용으로 safety가 이미 같은 인용으로 있음 |
| R3CXU474QJCRGR | overall | 'Don't waste your money'는 스키마상 price_value(이미 있음), 이유는 quality에 있음 |
| RH6TJCI4IIG0W | overall | 'Works but it hurts.'는 효과와 통증뿐이고 둘 다 따로 있음 |
| R1LY9NEVXGJBWW | overall | 'it works! Just keep up with it!'는 효과와 효과 조건으로 hair_reduction(이미 있음) |
| R5SJYXEK6GLD6 | overall | 'Semi-permanent at best... NOT permanent.'는 hair_reduction 이야기(mixed 이미 있음) |
| R17X5OGFX3L1Q4 | overall | 'This thing works!'는 효과 이야기로 hair_reduction(이미 있음) |
| R2MZ9ZWPKOLRZQ | overall | 'is a little annoying'은 매번 면도해야 하는 불편(ease_of_use, 이미 있음)에서 잘라 온 말 |
| R3LZWIQRKS8R3A | overall | 제목 'Don't waste your money'는 price_value(이미 있음), 이유는 hair_reduction에 있음 |
| R2333Y60LJ8Y8B | overall | 'Súper fácil de usar y funciona'는 사용 편의와 효과뿐이고 둘 다 따로 있음 |
| R2Z9MITKBORPPL | treatment_time | 효과가 나기까지 걸리는 기간 안내라 hair_reduction 쪽이고 negative 근거도 없음 |
| RUOAHQVG9XL2W | overall | 'Manchas raras'(기기 얼룩)은 quality 이야기(이미 있음) |
| RMQNDNZ0FACDR | overall | 'sirve bien'은 효과 이야기로 같은 인용의 hair_reduction과 두 번 집계 |
| R2GZ6MHPUO6SY2 | overall | 'Yo no noto nada'는 효과 이야기로 hair_reduction(negative 이미 있음), mixed 근거 없음 |
| R9C46AH6450H7 | overall | 효과와 렌즈 손상뿐이고 hair_reduction, quality에 따로 있음 |
| R2V5RNF586IBAW | overall | 'Humongous'는 크기 이야기로 design(negative 이미 있음) |
| R3OKWM306XWINV | safety | 면도 때 생기던 자극이 사라졌다는 말로 스키마상 hair_reduction이고 safety exclude에 해당 |
| R3UFI10NZBE0BU | overall | 'Works better than salon'은 살롱과 비교한 효과 이야기, mixed 근거 없음 |
| R12DL2XYKNVTLP | safety | 인용이 'the irritation'에서 끊겨 '줄었다'가 빠짐, 인용만으로 mixed 근거가 없음 |
| R2H56B7VCISJG6 | overall | 'Muy estético'는 외관이라 design(같은 인용으로 이미 있음) |
| R17Z3G31WY4J6A | overall | 'Finally an IPL that WORKS!!'는 효과 이야기, 본문에 총평 문장이 따로 있음 |
