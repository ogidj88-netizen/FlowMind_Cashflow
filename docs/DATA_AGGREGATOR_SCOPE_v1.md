# DATA AGGREGATOR SCOPE v1
Status: LOCKED
Mode: CASHFLOW
Purpose: Define real data sources and metrics for FACT_PACK generation

------------------------------------------------------------
ACTIVE SOURCES (WHITELISTED)
------------------------------------------------------------

1. World Bank API
2. OECD Data API
3. FRED (Federal Reserve Economic Data)
4. IMF Data Portal
5. US Bureau of Labor Statistics (BLS)
6. Google Trends (read-only trend signals)
7. Our World in Data (verified statistics only)

No other sources allowed without version upgrade.

------------------------------------------------------------
PRIMARY NICHE: MONEY MISTAKES / INVISIBLE COSTS
------------------------------------------------------------

Core data categories:

A) Inflation & Purchasing Power
   - CPI
   - Real wage growth
   - Cost-of-living index

B) Debt & Credit
   - Household debt levels
   - Credit card interest rates
   - Mortgage rates

C) Subscriptions & Consumer Spending
   - Average monthly subscription spending
   - Streaming cost growth
   - Telecom cost changes

D) Insurance & Risk Costs
   - Auto insurance growth rate
   - Health insurance premium growth
   - Claim frequency statistics

E) Energy & Utilities
   - Electricity price index
   - Fuel price trends
   - Utility inflation

------------------------------------------------------------
FACT_PACK REQUIREMENTS
------------------------------------------------------------

Each generated FACT_PACK must:

- Pull at least 5 independent data points.
- Use minimum 2 different data sources.
- Include publication date.
- Include numeric_value.
- Include original URL.

------------------------------------------------------------
UPDATE FREQUENCY
------------------------------------------------------------

- Core economic indicators: Weekly refresh.
- Trend signals (Google Trends): Daily refresh.
- Insurance / niche stats: Monthly refresh.

------------------------------------------------------------
OUT OF SCOPE (v1)
------------------------------------------------------------

- Social media scraping
- Reddit mining
- News API scraping
- AI-generated statistics
- User-submitted data

------------------------------------------------------------
IMMUTABILITY
------------------------------------------------------------

Scope cannot change without:

- Version bump
- Git lock
