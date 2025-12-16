# Signal: High-stakes “facts” pages exist + are indexable

## What it indicates
Companies with lots of **high-stakes, factual claims** (pricing, compliance, policies, integrations) are more likely to experience damaging wrong AI answers—especially if the canonical page is missing, hidden, or inconsistent.

## How to detect (programmatic)

### 1) Find candidate pages (crawl + sitemap)
- Fetch `https://{domain}/sitemap.xml` (and nested sitemaps).
- Crawl top navigation + common paths.

### 2) Score page presence by intent keywords
Look for URLs and page content that match:
- Trust/security: `security`, `trust`, `compliance`, `privacy`, `subprocessors`, `DPA`, `SOC 2`, `ISO 27001`
- Commercial: `pricing`, `plans`, `billing`
- Product truth: `docs`, `api`, `integrations`, `features`, `status`, `sla`

### 3) Check indexability + canonicalization
For each candidate page:
- HTTP status `200`
- Not blocked by `robots` meta (or `x-robots-tag`)
- Canonical tag points to the expected canonical URL

### Scoring suggestions
- **2:** canonical trust/pricing pages exist and are indexable
- **3:** canonical pages exist but SERP is dominated by third-party (pair with SERP signal)

## Output fields (recommended)
- `has_pricing_page` (bool)
- `has_security_or_trust_page` (bool)
- `has_compliance_keywords` (string[])
- `canonical_mismatches_count` (int)
- `indexability_issues_count` (int)

## Caveats / false positives
- Presence alone doesn’t mean pain; the pain emerges when **AI cites the wrong sources** or the canonical sources are stale/hidden.

