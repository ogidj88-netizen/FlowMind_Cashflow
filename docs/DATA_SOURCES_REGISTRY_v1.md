# DATA SOURCES REGISTRY v1
Status: LOCKED
Layer: VERIFIED DATA
Purpose: Whitelisted verified data sources only

------------------------------------------------------------
CORE RULE
------------------------------------------------------------

Only sources listed in this registry are allowed
for FACT_PACK generation.

No external opinion blogs.
No AI-generated citations.
No unverified aggregators.
No random finance sites.

If source not listed → REJECT.

------------------------------------------------------------
CATEGORY 1 — GOVERNMENT & OFFICIAL ECONOMIC DATA
------------------------------------------------------------

Federal Reserve (FRED)
Bureau of Labor Statistics (BLS)
U.S. Census Bureau
Internal Revenue Service (IRS Statistics)
SEC Filings (EDGAR)
World Bank Open Data
OECD Data
International Monetary Fund (IMF Data)

------------------------------------------------------------
CATEGORY 2 — CONSUMER & FINANCIAL REGULATION
------------------------------------------------------------

Federal Trade Commission (FTC Reports)
Consumer Financial Protection Bureau (CFPB)
Consumer Complaint Databases (official only)

------------------------------------------------------------
CATEGORY 3 — TIER-1 NEWS (FACTUAL REPORTING ONLY)
------------------------------------------------------------

Reuters
Associated Press (AP News)
Bloomberg (data-based reporting only)
Financial Times (data-based reporting only)
Wall Street Journal (data-based reporting only)

Opinion articles are not valid sources.

------------------------------------------------------------
CATEGORY 4 — TREND DATA
------------------------------------------------------------

Google Trends
YouTube Search Suggest API
Reddit (whitelisted subreddits only)

------------------------------------------------------------
STRICT VALIDATION RULES
------------------------------------------------------------

1. Every fact must contain:
   - numeric value
   - source name
   - publication date
   - URL

2. If numeric anchor is missing → reject fact.

3. If source is not in whitelist → reject fact.

4. If publication date older than acceptable threshold
   (defined per topic) → mark as low-confidence.

------------------------------------------------------------
IMMUTABILITY RULE
------------------------------------------------------------

This registry is immutable under v1.
Changes require explicit version upgrade (v2).
