# Signal: Hiring + content about AI accuracy / GEO / AI search

## What it indicates
They’re allocating budget/headcount or narrative energy to AI visibility and accuracy.
This is usually a **care/priority** signal; combine with SERP or trust-page signals for higher precision.

## How to detect (programmatic)

### 1) Jobs
Scrape job boards and search for keywords in role descriptions:
- `GEO`, `generative engine optimization`, `AI search`, `LLM`, `schema markup`, `knowledge graph`
- `brand integrity`, `reputation`, `misinformation`, `comms`

### 2) Content
Search site + blog for:
- `ChatGPT`, `Claude`, `Perplexity`, `hallucinations`, `AI misinformation`, `AI search visibility`

### Scoring suggestions
- **1:** one-off mention (blog post or a role)
- **2:** multiple roles + a consistent content theme (PMM/SEO/Comms)

## Output fields (recommended)
- `jobs_ai_keywords_hits` (int)
- `content_ai_keywords_hits` (int)
- `ai_keywords_top` (string[])

## Caveats / false positives
- SEO agencies and AI-forward brands may publish about AI without having a specific brand-accuracy incident.

