# Prudential Hong Kong Competitive Intelligence Monitor: technical documentation

Generated from the live database by `tools/make_tech_doc.py`. Window 1 Nov 2025 to 31 Oct 2026; reference brand Prudential Hong Kong; competitors AIA, Manulife and AXA (Hong Kong).

Database totals: 5,695 source-level records (AIA 2,001, AXA 1,259, Manulife 1,372, Prudential 1,063); 1,259 records excluded with a reason (not Hong Kong, out of window or noise); 1,048 analytical rows.

## 1. Source inventory

| Source | Tool or method | Fields collected | Historical coverage | Access constraints and known limits | Records | Modules |
|---|---|---|---|---|---|---|
| Official newsrooms and press releases (EN; Chinese editions checked) | pipeline/collectors/newsrooms.py, official_pages.py; tools/scrape_prudential_newsroom.py | Title, date, full text, URL, language | Full 12-month window | Manulife site returns HTTP 403 to automated requests: read from Internet Archive snapshots (manulife_archive.py); releases after the latest snapshot can be missing | 192 | M1, M3, M4 |
| Official website content and product pages | pipeline/collectors/digital_features.py, excel_imports.py (Exa / Tavily extracts) | Page text, product names, features, URL | Current pages (point in time) | Manulife website blocked (403); features requiring policyholder login are out of scope | 83 | M3, M4 |
| Industry news and media (InsuranceAsia News, SCMP, RTHK, The Standard, Google News discovery) | pipeline/collectors/media_feeds.py, google_news.py, excel_imports.py | Headline, publisher, date, text or summary, URL | Full window | Labelled third-party coverage; Google News links resolved to the publisher where possible; syndicated copies clustered | 1,676 | M1, M3, M5 |
| Facebook pages (official HK accounts) | Apify actors facebook-posts-scraper + facebook-pages-scraper (tools/apify_social.py) | Post text, date, URL, reactions, shares, comments (often missing), video flag, page followers | Full window (posts back to 1 Nov 2025) | Comment counts missing on most posts, so the Facebook rate uses reactions + shares; followers are capture-day only | 822 | M2 |
| Instagram accounts (official HK accounts; AIA from its official-platforms page) | Apify actors instagram-post-scraper + instagram-profile-scraper | Caption, date, URL, likes, comments, video views, type (image / carousel / video), followers | Full window | Shares not exposed; posts with hidden likes excluded from rates; collaboration posts owned by partners excluded | 885 | M2 |
| LinkedIn company pages | LinkedIn company-posts export (Apify dataset, 11 Nov 2026), loaded by report_app/prudential/linkedin.py | Post text, date, URL, reactions, comments, reposts, format, followers | Full window | Brand-authored originals only; reposts excluded; followers capture-day only | 598 posts (plus 164 records from an earlier licensed extract, kept for provenance) | M2, M5 |
| YouTube official channels + HK-media search | pipeline/collectors/youtube_public.py (public metadata); transcript datasets | Title, date, URL, views, subscribers, duration | Full window | Views include paid ad plays; likes hidden on some videos | 252 | M2 |
| Meta Ad Library (Hong Kong) | Apify actor facebook-ads-scraper, by Ad Library page id | Ad text, creative format, start date, end/last-seen date, platforms, call to action, ad library URL | Ads running on 11 Nov 2026 only | The HK library lists only active ads, so ended ads cannot be retrieved; spend not disclosed (never estimated) | 799 | M2 |
| Google Ads Transparency Center (Hong Kong) | pipeline/collectors/ads_transparency.py (Playwright, public pages) | Advertiser, creative format, first / last shown, image or preview URL, landing URL | Creatives shown in the window | No spend or impressions; advertiser names verified per brand (table ad_library) | 2,094 (table ad_library) | M2 |
| App stores (Apple App Store HK, Google Play HK) | pipeline/collectors/apps.py | App name, developer, version, update date, rating, rating count, release notes, reviews (iOS) | Point in time; iOS reviews within the window | Version history and download volumes not reliably available; Android reviews not collected; ratings are signals, not satisfaction measures | 231 | M4 |
| Google Trends (HK) | pipeline/collectors/context_stats.py | Monthly search-interest index per brand name (English and Chinese) | Full window | Keyword not topic; relative within one comparison; not a measure of sales | 96 rows (context_stats) | M2 context |
| HKFI Monthly Brief, MPFA statistical digest | pipeline/collectors/context_stats.py | Awards, membership, MPF statistics | Latest editions | Context only; not attributed to a brand unless the source names it | 47 rows (context_stats) | Context |
| Hong Kong company disclosures (risk-based capital disclosure statements, audited accounts) | tools/hk_investor_collect.py (insurers' Hong Kong regulatory pages; robots.txt respected) | Capital strength ratio, capital held, regulatory minimum, total assets | FY2024 and FY2025 | Prudential (2 companies) and AXA collected; AIA's not found online; Manulife's site blocks automated downloads | 14 PDFs | Context (M1) |
| HKEX filings (Prudential 2378, AIA 1299, Manulife 945) | tools/hk_investor_collect.py (HKEXnews title search) | Date, title, category, PDF link; substantive filings downloaded | 1 Nov 2025 to 11 Nov 2026 | Routine returns (buy-back reports, monthly returns) listed only; AXA not listed in Hong Kong | 702 listed, 96 downloaded | Context (M1) |
| HKEX market lists (board meetings, dividends and entitlements, trading arrangements; Main Board and GEM) | tools/hkex_market_lists.py (live pages plus Internet Archive copies) | All rows; rows for the three listed insurers flagged | Archived copies across the window plus 10 Nov 2026 | Pages show upcoming items only; history depends on archived copies | about 2,400 rows | Context |
| Daily share prices (HK lines, London, Toronto, Paris, Hang Seng Index) | tools/hk_investor_collect.py (public daily price feed) | Close and volume per trading day | 1 Oct 2025 to 10 Nov 2026 | Group-level prices, not Hong Kong-only; context only | 7 series | Context |
| Manulife HK newsroom (EN, Chinese index checked) | tools/manulife_newsroom_export.py (Internet Archive copies; live site 403 not bypassed) | Date, title, lead, full text where archived | 1 Nov 2025 to the latest archived copy (22 Sep 2026) | Releases after the latest archived copy are not visible | 47 releases | M1 |
| Insurance Authority statistics, complaints, register; Insurance Complaints Bureau | Not collected automatically | - | - | ia.org.hk blocks automated requests; ICB robots.txt disallows. Needs a manual download of the quarterly and annual statistics | 0 | Context |
| Licensed company data (employees, technology, workforce) | Licensed data provider extracts (xlsx), loaded by report_app/prudential/build.py | Employee range, technology detected, hiring intent | Snapshot 1 Nov 2026 | Some fields wrong for these entities (parent company, revenue range); those fields are not used | 4 company files | M4, M5 |
| Xiaohongshu | tools/xhs_collect.py (local logged-in browser session) | Notes, likes, collects, comments | - | Needs a user login; not yet run | 0 | M2 |
| WeChat, TikTok, Threads | Not collected | - | - | WeChat content not public; TikTok does not operate in Hong Kong; only AIA lists a Threads profile (recorded, posts not collected) | 0 | M2 |

Per-brand, per-platform availability is kept in the `source_coverage` table and shown in the report's channel coverage table, so missing data is never read as missing activity.

## 2. Collection approach

1. **Collect** (`pipeline/collect.py`, `tools/apify_social.py`): only the verified official accounts and pages in `pipeline/config/companies.json`, plus targeted media and ad-library searches using brand + Hong Kong + category keywords (English and Hong Kong Traditional Chinese). No whole-platform crawling. Raw exports and HTML snapshots are kept as evidence.
2. **Extract and classify** (`pipeline/classify.py`): activity type, product category, theme and digital capability from the configurable keyword taxonomy (`taxonomy.json`; add keywords without code changes); Hong Kong relevance with its basis; out-of-window and non-Hong Kong items moved to `excluded_records`.
3. **De-duplicate**: syndicated and repeated coverage is clustered; one primary record per cluster, other copies kept as provenance.
4. **Store** (`pipeline/build.py`, `tools/ingest_social.py`): one shared SQLite database with the Company Master; no per-brand or per-module databases.
5. **Translate** (`tools/translate_zh.py`): English summaries for Chinese records; originals are always kept.
6. **Analyse and publish** (`report_app/prudential/build.py`, `tools/sync_insights.py`): metrics, charts and insights for the dashboard; every number and insight links back to source records.

Run order: `collect.py` → `classify.py` → `build.py` → `tools/ingest_social.py` → `tools/translate_zh.py` → `report_app/prudential/build.py` → `tools/sync_insights.py` → `tools/make_tech_doc.py`.

Keys (`APIFY_TOKEN`, `GEMINI_API_KEY`) are read from `.env` at run time, sent only in request headers and never written to logs, data or the published site.

## 3. Data fields

| Field or table | Definition |
|---|---|
| `record_id` | Unique id. SOC-* = Facebook / Instagram / LinkedIn posts, ADM-* = Meta ads; others from the pipeline |
| `company_id` | Link to the Company Master (companies): PRU_HK, AIA_HK, MFC_HK, AXA_HK |
| `record_type` | announcement, news_article, content_article, social_post, advertisement, app_snapshot, app_review, web_feature |
| `activity_type` | Classified activity (taxonomy.activity_types), e.g. product_launch, partnership, campaign |
| `title / description / original_content` | As published; original language kept |
| `language` | en or zh |
| `english_summary` | English summary; for Chinese records a machine-generated summary (translation_status='machine_summary') |
| `translation_status` | not_required, machine_summary, done (analyst), pending |
| `publication_date` | Date the source published the item (YYYY-MM-DD) |
| `capture_ts` | When we collected it (UTC ISO timestamp), kept separate from publication_date |
| `source_name / source_category` | Publisher or account; official, media, social, app_store, ad_library |
| `source_url` | Original URL (proof link) |
| `evidence_ref` | Pointer to the stored raw export or HTML snapshot |
| `hk_relevance / hk_relevance_basis` | explicit / implicit / none, and why (e.g. official HK domain or account) |
| `platform / content_format` | website, news, facebook, instagram, linkedin, youtube, meta_ads, ios, android; format such as video, image, carousel |
| `product_name / campaign_name` | Where the record names one |
| `cluster_id / is_primary / cluster_size` | De-duplication: syndicated copies share a cluster; one primary record per cluster; others keep their URLs as provenance |
| `extra` | JSON with source-specific detail (e.g. ad call to action, active dates) |
| `observation_modules` | Module(s) M1-M5 per record |
| `observation_tags` | tag_type product_category / theme / digital_capability |
| `observation_metrics` | metric, value and its written definition (reactions, comments, shares, views, engagement_rate_pct, followers, rating, ...). Unavailable metrics are absent, never zero |
| `fact_metrics` | Analytical dataset: month x company x module x platform x category x metric, with record_ids back to the source rows |
| `source_coverage / context_coverage` | What each source and platform holds per brand, including what is unavailable and why |
| `clients / client_competitors / client_insights / client_insight_evidence` | Client lens: reference brand, competitor set, ranked insights and their evidence record ids |

## 4. Metric definitions

| Metric | Definition | Notes |
|---|---|---|
| Facebook engagement rate | (reactions + shares) / page followers at capture x 100 | Comment counts missing on most posts, so not used |
| Instagram engagement rate | (likes + comments) / account followers at capture x 100 | Shares not exposed; hidden-like posts excluded |
| LinkedIn engagement rate | (reactions + comments + reposts) / company followers at capture x 100 | |
| Engagement comparisons | Medians per brand, platform, month or theme; only within one platform | Rates shown only where at least 3 posts |
| YouTube views | Public view count at capture | Includes paid ad plays |
| Google ads | Creatives shown in Hong Kong in the window, by format | No spend or impressions |
| Meta ads | Ads running in Hong Kong on 11 Nov 2026, by start month | Ended ads not available |
| App rating | Store rating and rating count at capture; review stars | A signal, not a satisfaction measure |
| Google search interest | Index 0-100 relative within one four-term comparison, monthly mean of weekly values | Not comparable across requests |

Followers are audience-size context only, never the headline performance signal. Reach-based rates are not calculated because reach and impressions are not exposed for organic posts.

## 5. Classification taxonomy

- **activity types**: product_launch, product_enhancement, partnership, campaign, sponsorship_community, award_recognition, corporate_announcement, service_enhancement
- **product categories**: health_medical, critical_illness, life_protection, retirement, savings_wealth, sme_corporate, wellness, general_travel
- **themes**: health_wellness, medical_hospitalisation, critical_illness, life_protection, retirement_wealth, family_lifestyle, customer_education, corporate_sme, brand_awareness, digital_innovation
- **digital capabilities**: online_purchase, quotation_tool, customer_portal, digital_claims, claims_tracking, ehealth_card, telemedicine, wellness_programme, chatbot_ai, financial_planning, agent_finder, whatsapp_support
- **Hong Kong terms**: hong kong, hk, 香港, gba, greater bay, 大灣區, macau, 澳門

## 6. Translation status

| Language | Status | Records |
|---|---|---|
| en | not_required | 2,097 |
| zh | machine_summary | 2,799 |
| zh | pending | 799 |

## 7. Validation checklist (brief s14.3)

| Area | Result |
|---|---|
| Scraping tools | Apify actors cover Facebook, Instagram, Meta Ad Library and Threads profiles; LinkedIn via the company-posts dataset; public pages via Playwright and HTTP. Bright Data not needed |
| Social media | Post-level reactions, shares and views available; Facebook comments mostly missing; Instagram shares not exposed (see metric definitions) |
| Engagement calculations | Follower-based rates per platform with written definitions; never mixed across platforms |
| Chinese content | Original kept; English summaries generated and stored per record |
| Historical data | Full 12-month history for Facebook, Instagram, LinkedIn, YouTube and newsrooms; Meta Ad Library only current ads |
| Mobile apps | Current version, update date, rating, rating count and iOS reviews; version history and downloads not reliable |
| Data architecture | One database for all modules; client layer separate (clients, client_insights) for future subscribers |
| Evidence | Every record keeps its URL; fact_metrics and insights hold record_ids back to the sources |
| Dashboard | Brand, month, module, category and platform filters with drill-down to source records |
