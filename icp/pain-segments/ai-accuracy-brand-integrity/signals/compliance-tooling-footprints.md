# Signal: Compliance / trust tooling footprints on-site

## What it indicates
If they run compliance-heavy workflows, wrong AI claims about “SOC 2 / ISO / HIPAA / GDPR” tend to be especially damaging.
Tooling footprints are a proxy for “this topic matters internally.”

## How to detect (programmatic)

### 1) Crawl likely pages
- `/security`, `/trust`, `/compliance`, `/privacy`, `/legal`, `/subprocessors`, `/dpa`, `/terms`

### 2) Detect common vendors / scripts / badges
Search HTML for brand strings or embed domains like:
- Trust centers: Vanta, Drata, Secureframe
- Consent/privacy: OneTrust, TrustArc, Cookiebot
- Status pages: Atlassian Statuspage (sometimes used as a “reliability truth source”)

### 3) Extract claims
Look for text patterns that are frequently hallucinated or misquoted:
- `SOC 2 Type II`, `ISO 27001`, `HIPAA`, `BAA`, `GDPR`, `DPA`, `subprocessors`

### Scoring suggestions
- **1:** tooling detected (care signal)
- **2:** tooling + explicit certifications/claims present (high-stakes facts)

## Output fields (recommended)
- `trust_tooling_detected` (string[])
- `compliance_claims_detected` (string[])
- `trust_pages_count` (int)

## Caveats / false positives
- Vendors change; use fuzzy matching + update the detector list quarterly.

