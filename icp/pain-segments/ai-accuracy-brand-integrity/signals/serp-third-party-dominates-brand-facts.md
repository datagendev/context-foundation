# Signal: Third parties dominate brand-fact queries (SERP takeover risk)

## What it indicates
If third-party sites rank for brand “facts” (pricing, compliance, integrations), AI systems are more likely to ingest and repeat third-party summaries—often stale or wrong. This is one of the strongest at-scale predictors of “AI is saying the wrong thing.”

## How to detect (programmatic)

### 1) Query set (per brand)
Run a SERP API for:
- `{brand} pricing`
- `{brand} SOC 2` / `{brand} ISO 27001` / `{brand} HIPAA`
- `{brand} GDPR` / `{brand} DPA` / `{brand} subprocessors`
- `{brand} integrations`
- `{brand} security`

### 2) Score “canonical ownership”
For each query:
- Extract top N organic results (e.g., N=10).
- Compute:
  - `first_party_share = count(results where domain == brand_domain) / N`
  - `third_party_share = 1 - first_party_share`
- Flag if the first-party result is missing or below rank K (e.g., K=3).

### 3) Identify risky third-party sources
Tag common fact-repackagers:
- Review sites, directories, resellers, scraped pricing pages, old PDFs, aggregator wikis.

### Scoring suggestions
- **2:** third-party share high for 3+ brand-fact queries
- **3:** third-party share high + snippets include explicit facts (prices, certifications) not from first-party

## Output fields (recommended)
- `serp_queries_run` (string[])
- `serp_first_party_share_avg` (float)
- `serp_first_party_missing_count` (int)
- `serp_third_party_domains_top` (string[])

## Caveats / false positives
- Brands with very new sites may naturally have weaker first-party ownership; normalize by company age/traffic.

