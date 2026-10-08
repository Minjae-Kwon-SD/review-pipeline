# 연결된 MCP 도구 목록

.mcp.json에 등록된 MCP 서버 3개(amz-review, spd-amz-market, spd-amz-rank)의 도구 이름, 설명, 입력값이다.
설명과 입력값은 MCP 서버가 준 그대로 옮겼다(도구는 호출하지 않았다). 2026-10-07 기준.

| 서버 | 주소 | 도구 수 |
|---|---|---|
| amz-review | https://backend-v060-production.up.railway.app/mcp/ (Bearer ${AMZ_REVIEW_TOKEN}) | 3 |
| spd-amz-market | https://mcp-spd-amz-market.up.railway.app/mcp | 39 |
| spd-amz-rank | https://mcp-spd-amz-rank.up.railway.app/mcp | 2 |

---

## 1. amz-review

### get_review_stats

설명:

```text
DB 에 저장된 리뷰의 집계 통계를 반환한다.

    Apify 를 호출하지 않으므로 비용이 0 이다.

    ⚠️ `asin` 은 **부분일치(ILIKE)** 이다. 예를 들어 "B0ABC" 로 조회하면 그 문자열을
    포함하는 *모든* ASIN 의 리뷰가 하나로 합산된다. 응답의 `asin_count` 가 1보다 크면
    여러 상품이 합쳐진 결과이므로, 단일 상품 통계를 원했다면 반드시 확인하고
    전체 ASIN 을 정확히 지정해 다시 조회할 것.

    Args:
        asin: ASIN 부분일치 필터. 생략하면 DB 전체를 집계한다.

    Returns:
        total_reviews, average_rating, rating_distribution(별점별 건수),
        rating_percentage(별점별 비율), verified_count, asin_count,
        date_range(earliest/latest).
```

입력값:

```json
{"properties": {"asin": {"anyOf": [{"type": "string"}, {"type": "null"}], "default": null, "title": "Asin"}}, "title": "get_review_statsArguments", "type": "object"}
```

### scrape_reviews

설명:

```text
아마존 리뷰를 Apify 로 새로 수집하여 DB 에 저장한다.

    수집된 리뷰는 **전부 DB 에 저장**되고, 응답에는 `limit` 건의 축약 샘플만 담긴다.
    전체 결과를 보려면 저장 후 `search_reviews` 로 조회할 것.

    ⚠️ 소요 시간: 별점 × 국가 조합마다 Apify 를 한 번씩 호출한다.
    ratings 5개 × regions 5개 = 25회 호출이 되어 수 분이 걸리고 타임아웃 위험이 있다.
    조합을 보수적으로(예: 별점 1~2개, 국가 1개) 시작할 것.

    ⚠️ 비용: 호출 시 Apify 크레딧이 실제로 소모된다.

    Args:
        asins: 수집 대상 아마존 ASIN 목록. 필수.
        ratings: 수집할 별점(1~5 정수) 목록. 필수.
        regions: 아마존 도메인 코드 목록. 유효값:
            com(US), co.uk(UK), de, fr, it, es, ca, co.jp(JP), in,
            com.mx(MX), com.br(BR), com.au(AU), nl, se, pl
        max_pages: ASIN·별점·국가 조합당 수집할 리뷰 페이지 수 (1~10).
        sort: 정렬 기준. "helpful"(도움순) 또는 "recent"(최신순).
        limit: 응답에 포함할 샘플 리뷰 건수. DB 저장 건수와는 무관.

    Returns:
        collected(수집 건수), inserted(신규 저장), skipped(중복 제외),
        returned(응답에 담긴 건수), reviews(축약 리뷰 샘플).
```

입력값:

```json
{"properties": {"asins": {"items": {"type": "string"}, "title": "Asins", "type": "array"}, "limit": {"default": 20, "title": "Limit", "type": "integer"}, "max_pages": {"default": 1, "title": "Max Pages", "type": "integer"}, "ratings": {"items": {"type": "integer"}, "title": "Ratings", "type": "array"}, "regions": {"default": ["com"], "items": {"type": "string"}, "title": "Regions", "type": "array"}, "sort": {"default": "helpful", "title": "Sort", "type": "string"}}, "required": ["asins", "ratings"], "title": "scrape_reviewsArguments", "type": "object"}
```

### search_reviews

설명:

```text
이미 DB 에 저장된 리뷰를 조건으로 검색한다.

    Apify 를 호출하지 않으므로 **비용이 0 이고 빠르다**. 새 리뷰를 수집하려면
    `scrape_reviews` 를 쓸 것.

    Args:
        asin: ASIN 부분일치(ILIKE) 필터.
        ratings: 별점(1~5) 목록 필터. 지정한 별점만 반환.
        keyword: 리뷰 제목 또는 본문 부분일치 필터.
        verified: True 이면 구매 확인(verified purchase) 리뷰만 반환.
        start_date: 리뷰 작성일 하한. YYYY-MM-DD 형식.
        end_date: 리뷰 작성일 상한. YYYY-MM-DD 형식.
        limit: 반환할 최대 건수 (SQL LIMIT).
        offset: 건너뛸 건수 (SQL OFFSET). 페이지네이션용.

    Returns:
        count(반환 건수)와 reviews(리뷰 목록). 리뷰의 원본 raw JSON 은 제외된다.
```

입력값:

```json
{"properties": {"asin": {"anyOf": [{"type": "string"}, {"type": "null"}], "default": null, "title": "Asin"}, "end_date": {"anyOf": [{"type": "string"}, {"type": "null"}], "default": null, "title": "End Date"}, "keyword": {"anyOf": [{"type": "string"}, {"type": "null"}], "default": null, "title": "Keyword"}, "limit": {"default": 20, "title": "Limit", "type": "integer"}, "offset": {"default": 0, "title": "Offset", "type": "integer"}, "ratings": {"anyOf": [{"items": {"type": "integer"}, "type": "array"}, {"type": "null"}], "default": null, "title": "Ratings"}, "start_date": {"anyOf": [{"type": "string"}, {"type": "null"}], "default": null, "title": "Start Date"}, "verified": {"anyOf": [{"type": "boolean"}, {"type": "null"}], "default": null, "title": "Verified"}}, "title": "search_reviewsArguments", "type": "object"}
```

---

## 2. spd-amz-market

### brandcoverage_search

설명:

```text
Use when user wants to see which Amazon sellers carry a specific brand, brand coverage by seller, seller share of a brand, or brand distribution across sellers (brand coverage, seller coverage, brand sellers, brand market share, seller penetration). DO NOT TRIGGER for brand-level metrics without seller breakdown.
```

입력값:

```json
{"properties": {"brand_name": {"description": "Brand name", "type": "string"}, "marketplace": {"description": "Marketplace code", "type": "string"}}, "required": ["brand_name"], "type": "object"}
```

### brands_by_brand_marketplaces

설명:

```text
Use when user wants brand performance data across multiple Amazon marketplaces for a specific brand (brand marketplaces, cross-marketplace comparison, brand revenue by marketplace, brand score by country). DO NOT TRIGGER for browsing or paginating all brands — use brands_search instead.
```

입력값:

```json
{"properties": {"brand_name": {"description": "Brand name", "type": "string"}, "marketplace": {"description": "Marketplace code", "type": "string"}}, "required": ["brand_name"], "type": "object"}
```

### brands_relevant_keywords

설명:

```text
Use when user wants to find keywords associated with a specific brand on Amazon (brand keywords, search terms for brand, keyword search volume for brand, brand keyword ranking, brand SEO). DO NOT TRIGGER for general keyword research not tied to a specific brand.
```

입력값:

```json
{"properties": {"brand_name": {"description": "Brand name", "type": "string"}, "marketplace": {"description": "Marketplace code", "type": "string"}}, "required": ["brand_name"], "type": "object"}
```

### brands_search

설명:

```text
Use when user wants to list, browse, paginate, or filter Amazon brands (brand list, top brands, brand ranking, brand revenue ranking, brand pagination). DO NOT TRIGGER for a single named brand summary — use brands_summary instead.
```

입력값:

```json
{"properties": {"brand_filter": {"description": "Brand name filter", "type": "string"}, "end_row": {"description": "End row for pagination", "type": "integer"}, "marketplace": {"description": "Marketplace code", "type": "string"}, "start_row": {"description": "Start row for pagination", "type": "integer"}}, "required": [], "type": "object"}
```

### brands_summary

설명:

```text
Use when user wants a summary overview of a specific named Amazon brand (brand summary, brand profile, brand overview, brand revenue, brand score for one brand). DO NOT TRIGGER for browsing multiple brands — use brands_search instead.
```

입력값:

```json
{"properties": {"brand_name": {"description": "Brand name", "type": "string"}, "marketplace": {"description": "Marketplace code", "type": "string"}}, "required": ["brand_name"], "type": "object"}
```

### brands_total_brand_info

설명:

```text
Use when user wants pre-aggregated brand metrics from the internal database (total brand info, all brands database, brand dataset, brand info table, bulk brand data). DO NOT TRIGGER for live per-brand lookups by name — use brands_summary or brands_search instead.
```

입력값:

```json
{"properties": {}, "required": [], "type": "object"}
```

### categories

설명:

```text
Use when user wants top-level Amazon categories, root category names, category IDs or node IDs, or category tree roots. DO NOT TRIGGER for leaf subcategory data — use subcategories_leaf_nodes or subcategories_search instead.
```

입력값:

```json
{"properties": {"marketplace": {"description": "Marketplace code", "type": "string"}}, "required": [], "type": "object"}
```

### products_brand_search

설명:

```text
Use when user wants to list or paginate all products for a specific brand on Amazon (brand product list, products by brand, brand catalog, brand ASIN list). DO NOT TRIGGER for brand promotions — use products_get_promotions instead.
```

입력값:

```json
{"properties": {"brand_filter": {"description": "Brand name to filter products", "type": "string"}, "end_row": {"description": "End row for pagination", "type": "integer"}, "marketplace": {"description": "Marketplace code", "type": "string"}, "start_row": {"description": "Start row for pagination", "type": "integer"}}, "required": ["brand_filter"], "type": "object"}
```

### products_byasin

설명:

```text
Use when user wants to look up a single Amazon product by ASIN (product details, ASIN lookup, product data, buy box price, review count, monthly revenue). DO NOT TRIGGER for cross-marketplace ASIN data — use products_byasin_marketplaces instead.
```

입력값:

```json
{"properties": {"asin": {"description": "Amazon Standard Identification Number", "type": "string"}, "marketplace": {"description": "Marketplace code", "type": "string"}}, "required": ["asin"], "type": "object"}
```

### products_byasin_marketplaces

설명:

```text
Use when user wants to see a product across multiple marketplaces (cross-marketplace comparison, international product data, ASIN marketplaces, multi-country). DO NOT TRIGGER for single-marketplace product details — use products_byasin instead.
```

입력값:

```json
{"properties": {"asin": {"description": "Amazon Standard Identification Number", "type": "string"}, "marketplace": {"description": "Marketplace code", "type": "string"}}, "required": ["asin"], "type": "object"}
```

### products_category_products

설명:

```text
Use when user wants to list or paginate products within an Amazon category (category product list, products in category, category browse, niche products). DO NOT TRIGGER for brand-filtered product lists — use products_brand_search instead.
```

입력값:

```json
{"properties": {"category_name": {"description": "Category name", "type": "string"}, "end_row": {"description": "End row for pagination", "type": "integer"}, "marketplace": {"description": "Marketplace code", "type": "string"}, "start_row": {"description": "Start row for pagination", "type": "integer"}}, "required": ["category_name"], "type": "object"}
```

### products_get_promotions

설명:

```text
Use when user wants to find active promotions or deals for a brand on Amazon (brand promotions, coupons, product deals, promotional offers). DO NOT TRIGGER for general product search by brand name — use products_brand_search instead.
```

입력값:

```json
{"properties": {"brand_name": {"description": "Brand name", "type": "string"}, "marketplace": {"description": "Marketplace code", "type": "string"}}, "required": ["brand_name"], "type": "object"}
```

### products_history

설명:

```text
Use when user wants historical time-series data for a product (price history, sales rank history, buy box history, FBA price trends, offer count over time). DO NOT TRIGGER for rank score history — use products_rank_history instead.
```

입력값:

```json
{"properties": {"asin": {"description": "Amazon Standard Identification Number", "type": "string"}, "marketplace": {"description": "Marketplace code", "type": "string"}}, "required": ["asin"], "type": "object"}
```

### products_organic_ranks

설명:

```text
Use when user wants organic search term rankings for a product ASIN (keyword rank, search term position, organic rank, daily rank tracking, keyword performance). DO NOT TRIGGER for rank score trends — use products_rank_history instead.
```

입력값:

```json
{"properties": {"asin": {"description": "Amazon Standard Identification Number", "type": "string"}, "marketplace": {"description": "Marketplace code", "type": "string"}, "parent_asin": {"description": "Parent ASIN", "type": "string"}}, "required": ["asin"], "type": "object"}
```

### products_rank_history

설명:

```text
Use when user wants daily rank score or smart score history for a product ASIN (rank score trend, smart score history, daily ranking timeline, score over time). DO NOT TRIGGER for keyword-level rank tracking — use products_organic_ranks instead.
```

입력값:

```json
{"properties": {"asin": {"description": "Amazon Standard Identification Number", "type": "string"}, "marketplace": {"description": "Marketplace code", "type": "string"}}, "required": ["asin"], "type": "object"}
```

### products_search

설명:

```text
Use when user wants to browse, list, or paginate Amazon products broadly (product list, top products, product ranking, catalog browse, all products). DO NOT TRIGGER for brand-specific product lists — use products_brand_search instead.
```

입력값:

```json
{"properties": {"asin": {"description": "ASIN filter", "type": "string"}, "end_row": {"description": "End row for pagination", "type": "integer"}, "marketplace": {"description": "Marketplace code", "type": "string"}, "start_row": {"description": "Start row for pagination", "type": "integer"}}, "required": [], "type": "object"}
```

### products_search_terms_comparison

설명:

```text
Use when user wants to compare keyword overlap between multiple ASINs (keyword overlap, common search terms, competitor comparison, shared keywords). DO NOT TRIGGER for single product organic rank lookup — use products_organic_ranks instead.
```

입력값:

```json
{"properties": {"asins": {"description": "ASINs (comma-separated)", "items": {"type": "string"}, "type": "array"}, "marketplace": {"description": "Marketplace code", "type": "string"}}, "required": ["asins"], "type": "object"}
```

### products_top_new_products

설명:

```text
Use when user wants to discover newly listed or trending products on Amazon (new products, recently listed, top new ASINs, new arrivals, emerging products). DO NOT TRIGGER for existing product catalog browsing — use products_search instead.
```

입력값:

```json
{"properties": {"asin": {"description": "ASIN filter", "type": "string"}, "end_row": {"description": "End row for pagination", "type": "integer"}, "marketplace": {"description": "Marketplace code", "type": "string"}, "start_row": {"description": "Start row for pagination", "type": "integer"}}, "required": [], "type": "object"}
```

### products_variations

설명:

```text
Use when user wants to list all variations of an Amazon product (product variants, ASIN variations, sizes colors, parent ASIN children, variation tree). DO NOT TRIGGER for cross-marketplace product data — use products_byasin_marketplaces instead.
```

입력값:

```json
{"properties": {"asin": {"description": "Amazon Standard Identification Number", "type": "string"}, "marketplace": {"description": "Marketplace code", "type": "string"}}, "required": ["asin"], "type": "object"}
```

### relevancy_products

설명:

```text
Use when user wants to find competitor or related products for a given ASIN (product relevancy, related products, ASIN competitors, similar listings, relevancy score). DO NOT TRIGGER for search term/keyword relevancy — use relevancy_quadrant instead.
```

입력값:

```json
{"properties": {"asin": {"description": "Amazon Standard Identification Number", "type": "string"}, "marketplace": {"description": "Marketplace code", "type": "string"}}, "required": ["asin"], "type": "object"}
```

### relevancy_quadrant

설명:

```text
Use when user wants to find search terms or keywords relevant to a given ASIN (keyword relevancy, search term relevancy, ASIN keywords, relevancy quadrant, search intent). DO NOT TRIGGER for competitor product discovery — use relevancy_products instead.
```

입력값:

```json
{"properties": {"asin": {"description": "Amazon Standard Identification Number", "type": "string"}, "marketplace": {"description": "Marketplace code", "type": "string"}}, "required": ["asin"], "type": "object"}
```

### search_terms_ad_spy

설명:

```text
Use when user wants to spy on a brand\'s ad keywords or which terms a brand advertises on (ad spy, brand keyword targeting, competitor ads, brand ad spend). DO NOT TRIGGER for brands advertising on a given term — use search_terms_advertised_brands.
```

입력값:

```json
{"properties": {"brand_name": {"description": "Brand name", "type": "string"}, "end_row": {"description": "End row for pagination", "type": "integer"}, "marketplace": {"description": "Marketplace code", "type": "string"}, "start_row": {"description": "Start row for pagination", "type": "integer"}}, "required": ["brand_name"], "type": "object"}
```

### search_terms_advertised_brands

설명:

```text
Use when user wants which brands advertise on a keyword, brand ad win-rates, or top bidding brands (advertised brands, brand competition, sponsored brand). DO NOT TRIGGER for a brand\'s own keyword list — use search_terms_brand_search_term.
```

입력값:

```json
{"properties": {"end_row": {"description": "End row for pagination", "type": "integer"}, "marketplace": {"description": "Marketplace code", "type": "string"}, "search_term": {"description": "Search term", "type": "string"}, "sort_col": {"description": "Sort column", "type": "string"}, "sort_order": {"description": "Sort order", "type": "string"}, "start_row": {"description": "Start row for pagination", "type": "integer"}}, "required": ["search_term"], "type": "object"}
```

### search_terms_brand_search_term

설명:

```text
Use when user wants all keywords a brand targets with ads or a brand\'s keyword portfolio (brand keyword portfolio, brand ad keywords, keyword strategy). DO NOT TRIGGER for brands competing on a given term — use search_terms_advertised_brands.
```

입력값:

```json
{"properties": {"brand_name": {"description": "Brand name filter", "type": "string"}, "end_row": {"description": "End row for pagination", "type": "integer"}, "marketplace": {"description": "Marketplace code", "type": "string"}, "sort_col": {"description": "Sort column", "type": "string"}, "sort_order": {"description": "Sort order", "type": "string"}, "start_row": {"description": "Start row for pagination", "type": "integer"}}, "required": ["brand_name"], "type": "object"}
```

### search_terms_keyword_to_keywords

설명:

```text
Use when user wants related keywords, keyword expansion, or sibling search terms for a seed keyword (keyword research, related terms, search term expansion, keyword ideas). DO NOT TRIGGER for trend data or volume history.
```

입력값:

```json
{"properties": {"marketplace": {"description": "Marketplace code", "type": "string"}, "target_keyword": {"description": "Target keyword", "type": "string"}}, "required": ["target_keyword"], "type": "object"}
```

### search_terms_organic_ranks

설명:

```text
Use when user wants products organically ranking for a search term, daily rank history, or ASIN rank tracking by keyword (organic rank, keyword rank, product ranking). DO NOT TRIGGER for sponsored ad win-rate data — use search_terms_products.
```

입력값:

```json
{"properties": {"marketplace": {"description": "Marketplace code", "type": "string"}, "search_term": {"description": "Search term", "type": "string"}}, "required": ["search_term"], "type": "object"}
```

### search_terms_products

설명:

```text
Use when user wants products competing for a keyword with ad win-rates or ASIN competitiveness (keyword ad products, sponsored competition, top-spot win-rate). DO NOT TRIGGER for organic rank history — use search_terms_organic_ranks.
```

입력값:

```json
{"properties": {"end_row": {"description": "End row for pagination", "type": "integer"}, "marketplace": {"description": "Marketplace code", "type": "string"}, "search_term": {"description": "Search term", "type": "string"}, "start_row": {"description": "Start row for pagination", "type": "integer"}}, "required": ["search_term"], "type": "object"}
```

### search_terms_search

설명:

```text
Use when user wants to filter or browse the keyword catalog by phrase (keyword lookup, search term filter, keyword catalog, browse terms). DO NOT TRIGGER for related keyword expansion from a seed — use search_terms_keyword_to_keywords.
```

입력값:

```json
{"properties": {"end_row": {"description": "End row for pagination", "type": "integer"}, "filter_type": {"description": "Filter type (contains, equals, starts_with)", "type": "string"}, "filter_value": {"description": "Search filter value", "type": "string"}, "marketplace": {"description": "Marketplace code", "type": "string"}, "start_row": {"description": "Start row for pagination", "type": "integer"}}, "required": ["filter_value"], "type": "object"}
```

### search_terms_trends

설명:

```text
Use when user wants search volume trend history, trending keywords by growth, or weekly volume data for a keyword (keyword trends, trend analysis, volume history). DO NOT TRIGGER for related keyword expansion — use search_terms_keyword_to_keywords.
```

입력값:

```json
{"properties": {"include_negatives": {"description": "Include negative growth terms (upstream currently ignores this)", "type": "boolean"}, "keyword": {"description": "Keyword to search", "type": "string"}, "marketplace": {"description": "Marketplace code", "type": "string"}, "months": {"description": "Number of months (1, 3, 6, 12, 24)", "enum": [1, 3, 6, 12, 24], "type": "integer"}, "sort": {"description": "Sort type", "type": "string"}, "subcategories": {"description": "Category names (comma-separated)", "items": {"type": "string"}, "type": "array"}}, "required": ["keyword"], "type": "object"}
```

### search_terms_trends_related

설명:

```text
Use when user wants trend data for keywords related to a term, sibling volume trends, or adjacent keyword growth history (related keyword trends, sibling trends). DO NOT TRIGGER for trend data of the seed keyword itself — use search_terms_trends.
```

입력값:

```json
{"properties": {"marketplace": {"description": "Marketplace code", "type": "string"}, "months": {"description": "Number of months (1, 3, 6, 12, 24)", "enum": [1, 3, 6, 12, 24], "type": "integer"}, "search_term": {"description": "Search term", "type": "string"}}, "required": ["search_term"], "type": "object"}
```

### search_terms_trends_top_products

설명:

```text
Use when user wants top-ranked products for a keyword with daily rank history or ASIN rank trends over time (top products by keyword, rank history, trending rankings). DO NOT TRIGGER for brand ad win-rates — use search_terms_advertised_brands.
```

입력값:

```json
{"properties": {"marketplace": {"description": "Marketplace code", "type": "string"}, "search_term": {"description": "Search term", "type": "string"}}, "required": ["search_term"], "type": "object"}
```

### sellers_search

설명:

```text
Use when user wants to list, browse, or paginate Amazon sellers (seller list, top sellers, seller ranking, seller pagination). DO NOT TRIGGER for specific seller offers/products by ID.
```

입력값:

```json
{"properties": {"end_row": {"description": "End row for pagination", "type": "integer"}, "marketplace": {"description": "Marketplace code", "type": "string"}, "start_row": {"description": "Start row for pagination", "type": "integer"}}, "required": [], "type": "object"}
```

### sellers_searchoffers

설명:

```text
Use when user wants to see offers or products listed by a specific Amazon seller ID (seller offers, seller products, what a seller sells, seller ASIN list, seller inventory). DO NOT TRIGGER for paginated seller list — use sellers_search instead.
```

입력값:

```json
{"properties": {"marketplace": {"description": "Marketplace code", "type": "string"}, "seller_id": {"description": "Seller ID", "type": "integer"}}, "required": ["seller_id"], "type": "object"}
```

### subcategories_brand_category_performance

설명:

```text
Use when user wants brand performance by subcategory, brand market share, brand revenue per category, or subcategory brand ranking. DO NOT TRIGGER for competitor analysis in a category — use subcategories_category_competitors instead.
```

입력값:

```json
{"properties": {"brand_name": {"description": "Brand name", "type": "string"}, "end_row": {"description": "End row for pagination", "type": "integer"}, "marketplace": {"description": "Marketplace code", "type": "string"}, "start_row": {"description": "Start row for pagination", "type": "integer"}}, "required": ["brand_name"], "type": "object"}
```

### subcategories_category_competitors

설명:

```text
Use when user wants competing brands in a subcategory, top brands by category, brand market share, or category brand landscape. DO NOT TRIGGER for one brand across subcategories — use subcategories_brand_category_performance instead.
```

입력값:

```json
{"properties": {"end_row": {"description": "End row for pagination", "type": "integer"}, "marketplace": {"description": "Marketplace code", "type": "string"}, "start_row": {"description": "Start row for pagination", "type": "integer"}, "sub_category_name": {"description": "Sub category name", "type": "string"}}, "required": ["sub_category_name"], "type": "object"}
```

### subcategories_leaf_nodes

설명:

```text
Use when user wants leaf-level subcategory nodes, deepest subcategory metrics, subcategory revenue and brand counts, or subcategory node details. DO NOT TRIGGER for top-level root category list — use subcategories-categories instead.
```

입력값:

```json
{"properties": {"marketplace": {"description": "Marketplace code", "type": "string"}}, "required": [], "type": "object"}
```

### subcategories_relevant_search_terms

설명:

```text
Use when user wants keywords for a subcategory, relevant search terms by category name, keyword search volume, or YoY keyword trends. DO NOT TRIGGER for seller or product keyword search — use search-terms endpoints instead.
```

입력값:

```json
{"properties": {"marketplace": {"description": "Marketplace code", "type": "string"}, "subcategory_name": {"description": "Subcategory name", "type": "string"}}, "required": ["subcategory_name"], "type": "object"}
```

### subcategories_search

설명:

```text
Use when user wants all Amazon subcategories, subcategory metrics, revenue or growth data, or full subcategory catalog. DO NOT TRIGGER for brand competitors in a named subcategory — use subcategories_category_competitors instead.
```

입력값:

```json
{"properties": {"marketplace": {"description": "Marketplace code", "type": "string"}}, "required": [], "type": "object"}
```

### traffics_graph

설명:

```text
Use when user wants to explore traffic flow, traffic graph, ASIN traffic sources, keyword traffic relationships, or product traffic connections (traffic graph, traffic sources, asin traffic, keyword traffic, traffic flow). DO NOT TRIGGER for keyword search volume trends or seller-level traffic — use search_terms_trends or sellers_search instead.
```

입력값:

```json
{"properties": {"keyword_or_asin": {"description": "Keyword or ASIN", "type": "string"}, "marketplace": {"description": "Marketplace code", "type": "string"}}, "required": ["keyword_or_asin"], "type": "object"}
```

---

## 3. spd-amz-rank

### asin_search_terms_rank_trends_daily

설명:

```text
Use when user wants the daily-granularity Amazon search result rank history (page, pageRank, totalRank) for a specific ASIN + search term combination, defaulting to the last 30 days when dates are omitted. DO NOT TRIGGER for hourly/intraday rank movement — use asin_search_terms_rank_trends_hourly instead.
```

입력값:

```json
{"properties": {"asin": {"description": "Amazon ASIN (e.g. B08N5WRWNW)", "type": "string"}, "country": {"description": "Marketplace country code", "type": "string"}, "end_date": {"description": "End date YYYY-MM-DD, auto-calculated if omitted", "type": "string"}, "search_term": {"description": "Search term (e.g. echo dot)", "type": "string"}, "start_date": {"description": "Start date YYYY-MM-DD, auto-calculated if omitted", "type": "string"}}, "required": ["asin", "search_term"], "type": "object"}
```

### asin_search_terms_rank_trends_hourly

설명:

```text
Use when user wants the hourly-granularity Amazon search result rank history for a specific ASIN + search term combination, defaulting to the last 6 days when dates are omitted. The date range must not exceed 6 days or the upstream API returns a SelectTimeOverLimit error. DO NOT TRIGGER for daily-granularity or long-range rank trends — use asin_search_terms_rank_trends_daily instead.
```

입력값:

```json
{"properties": {"asin": {"description": "Amazon ASIN (e.g. B08N5WRWNW)", "type": "string"}, "country": {"description": "Marketplace country code", "type": "string"}, "end_date": {"description": "End date YYYY-MM-DD, auto-calculated if omitted", "type": "string"}, "search_term": {"description": "Search term (e.g. echo dot)", "type": "string"}, "start_date": {"description": "Start date YYYY-MM-DD, auto-calculated if omitted", "type": "string"}}, "required": ["asin", "search_term"], "type": "object"}
```
