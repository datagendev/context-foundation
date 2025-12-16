# Signal: Public chatter about wrong AI answers (brand accuracy incidents)

## What it indicates
Public posts that reference a specific wrong AI answer (with prompt/model/screenshot) are a strong proxy for urgency—often the same artifacts that later show up in internal escalations.

## How to detect (programmatic)

### 1) Query pack (web + social)
Use a web/social search API with:
- `"{brand}" ("ChatGPT" OR "Claude" OR "Perplexity") ("wrong" OR "incorrect" OR hallucinat* OR "not true")`
- `"{brand}" ("ChatGPT said" OR "Claude said" OR "Perplexity said")`
- `site:reddit.com "{brand}" ("ChatGPT" OR "Claude" OR "Perplexity")`

### 2) Score specificity
Score higher when content includes:
- Model name + prompt text + screenshot/link
- A high-stakes claim (pricing, compliance, integrations, policies)
- Mentions of deal loss, churn, PR risk

## Output fields (recommended)
- `public_ai_chatter_hits_90d` (int)
- `public_ai_chatter_sources_top` (string[])
- `public_ai_chatter_has_screenshots` (bool)
- `public_ai_chatter_mentions_pricing_or_compliance` (bool)

## Caveats / false positives
- Some brands get “AI drama” posts that are unrelated to buying decisions; filter by claim type + business context.

