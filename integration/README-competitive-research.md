# Competitive Research Workflow

This document describes the end-to-end workflow for researching competitors and maintaining competitive intelligence.

## Quick Start

### Automated Research (Recommended)

```bash
# Quick reconnaissance (5-10 min)
uv run python integration/research-competitor.py \
  --domain peec.ai \
  --company-name "Peec.ai" \
  --depth quick

# Standard competitive profile (20-30 min, default)
uv run python integration/research-competitor.py \
  --domain brightedge.com \
  --company-name "BrightEdge"

# Comprehensive analysis (1-2 hours)
uv run python integration/research-competitor.py \
  --domain conductor.com \
  --company-name "Conductor" \
  --depth comprehensive
```

This will:
1. Create folder structure
2. Run deep research queries (count depends on depth)
3. Save research outputs as JSON
4. Create placeholder profile
5. (Optional) Scrape key website pages

**Depth Options:**
- `quick`: 1 broad query, 5-10 min
- `standard`: 3 focused queries (product, customers, positioning), 20-30 min
- `comprehensive`: 5 queries (adds technology, team), 1-2 hours

**Focus Options:**
Use `--research-focus` to target specific areas:
- `product,customers,positioning` (standard default)
- `product` (pricing and features only)
- `positioning,team` (GTM strategy and company info)
- `all` (comprehensive default)

### Manual Research

Follow the steps below for full control over the research process.

## Step-by-Step Workflow

### Step 1: Identify Competitor

Determine which competitor to research based on priority:
- **Tier 1**: Direct AI search optimization competitors (BrightEdge, Otterly.AI, Peec.ai, Conductor, SearchAtlas)
- **Tier 2**: Adjacent competitors pivoting to AI (MarketMuse, Semrush, Ahrefs)

### Step 2: Create Folder Structure

```bash
# Create base company folder
mkdir -p company/{domain}

# Create competitive intelligence subfolders
mkdir -p company/{domain}/competitive-intelligence/research
mkdir -p company/{domain}/competitive-intelligence/analysis
```

### Step 3: Create Base README

```bash
cat > company/{domain}/README.md <<EOF
# {Company Name}

- **Website:** https://{domain}
- **Category:** {Category}
- **Status:** Competitor in AI search optimization

## Overview

{Brief description of what the company does}

## Contents

- \`competitive-intelligence/\`: Competitive analysis and research
- \`site-map/\`: URL inventory (if scraped)
- \`pages/\`: Scraped website pages (if applicable)
EOF
```

### Step 4: Run Deep Research Queries

Execute three deep research queries using OpenAI's o3-deep-research model:

#### Query 1: Product Analysis

```bash
uv run python integration/openai-deep-research.py \
  --query "What products and features does {Company Name} offer for AI search optimization? Include pricing tiers, core capabilities, and key differentiators compared to competitors in AI SEO/LLM visibility space. How do they help brands appear in ChatGPT, Perplexity, and other AI platforms?" \
  --output-dir company/{domain}/competitive-intelligence/research \
  --model o3-deep-research-2025-06-26
```

#### Query 2: Customer Segments

```bash
uv run python integration/openai-deep-research.py \
  --query "Who are {Company Name}'s customers? What customer segments do they target? Include case studies, testimonials, and examples of companies using their AI search optimization platform. What industries and company sizes do they serve?" \
  --output-dir company/{domain}/competitive-intelligence/research \
  --model o3-deep-research-2025-06-26
```

#### Query 3: Market Positioning

```bash
uv run python integration/openai-deep-research.py \
  --query "How does {Company Name} position itself in the AI search optimization market? What is their messaging strategy, value proposition, and competitive differentiation? What do they emphasize in their marketing and sales materials?" \
  --output-dir company/{domain}/competitive-intelligence/research \
  --model o3-deep-research-2025-06-26
```

**Note:** Each query takes ~2-5 minutes to complete. You can run them in parallel by adding `--no-poll` and polling later with `--poll-id`.

### Step 5: Convert Research Outputs to Markdown

```bash
uv run python integration/convert-research-outputs.py \
  --research-dir company/{domain}/competitive-intelligence/research \
  --output-dir company/{domain}/competitive-intelligence/research
```

This converts JSON outputs to markdown with YAML frontmatter.

### Step 6: Scrape Key Website Pages (Optional)

For competitors with accessible websites, scrape key pages:

```bash
# Get site map first
uv run python integration/company-site-map.py \
  --url https://{domain} \
  --sitemap include

# Scrape key pages
uv run python integration/company-scrape-url.py \
  --url https://{domain}/ \
  --url https://{domain}/product \
  --url https://{domain}/pricing \
  --url https://{domain}/customers \
  --only-main-content \
  --remove-base64-images
```

### Step 7: Create Competitive Profile

```bash
# Copy template
cp company/.templates/competitive-intelligence/profile-template.md \
   company/{domain}/competitive-intelligence/profile.md
```

Then fill in the template using:
- Deep research outputs from `research/*.md`
- Scraped pages from `pages/*.md`
- Your own analysis and synthesis

**Key Sections to Complete:**
1. Company Overview (funding, team, founding)
2. Product Offerings (features, pricing, tiers)
3. Customer Segments (who uses it, case studies)
4. Market Positioning (value prop, messaging)
5. Competitive Analysis vs Scrunch (strengths, weaknesses, opportunities)

### Step 8: Update Comparison Matrix

Add the competitor to `company/competitive-landscape/comparison-matrix.md`:

```markdown
| Feature | Scrunch | {Competitor} | ... |
|---------|---------|--------------|-----|
| AI Platform Monitoring | ✅ | {✅/❌/?} | ... |
| AXP / AI-friendly site | ✅ | {✅/❌/?} | ... |
| ChatGPT visibility | ✅ | {✅/❌/?} | ... |
```

### Step 9: Update Competitive Landscape README

Update `company/competitive-landscape/README.md`:
- Add competitor to appropriate tier
- Update research status table
- Note any key insights or market gaps discovered

## File Naming Conventions

### Research Outputs

Deep research outputs are saved with timestamp:
```
research_YYYY-MM-DDTHHMMSSZ_{query-slug}.json
research_YYYY-MM-DDTHHMMSSZ_{query-slug}.md
```

Rename for clarity in CI folder:
```
product-analysis_2025-12-15.md
customer-segments_2025-12-15.md
market-positioning_2025-12-15.md
```

### Scraped Pages

Scraped pages follow existing convention:
```
{page-slug}__{url-hash}.md
{page-slug}__{url-hash}.json
```

## Tools Reference

### openai-deep-research.py

Submit and poll deep research queries to OpenAI.

**Key Options:**
- `--query`: Research question
- `--model`: Model to use (default: o3-deep-research-2025-06-26)
- `--output-dir`: Where to save results
- `--no-poll`: Submit without waiting
- `--poll-id`: Resume polling existing query
- `--max-wait`: Maximum wait time (default: 3600s)

### convert-research-outputs.py

Convert research JSON outputs to markdown with frontmatter.

**Key Options:**
- `--research-dir`: Source directory (default: research-outputs)
- `--output-dir`: Destination directory (default: research-markdown)

### company-scrape-url.py

Scrape specific URLs to markdown via Firecrawl.

**Key Options:**
- `--url`: URL to scrape (repeatable)
- `--urls-file`: File with URLs (one per line)
- `--only-main-content`: Extract main content only
- `--remove-base64-images`: Strip base64 images
- `--max-workers`: Parallel workers (default: 4)

### company-site-map.py

Generate URL inventory via Firecrawl map.

**Key Options:**
- `--url`: Website URL
- `--sitemap`: include/skip/only (default: include)
- `--search`: Filter URLs by keyword
- `--limit`: Max URLs to discover (default: 200)

### research-competitor.py

Automated workflow combining all steps above with configurable depth and focus.

**Essential Options:**
- `--domain`: Competitor domain (required)
- `--company-name`: Company name (required)

**Research Configuration:**
- `--research-focus`: Research areas (default: all)
  - Options: `product`, `customers`, `positioning`, `technology`, `team`, or `all`
  - Can specify multiple: `--research-focus product,customers,positioning`
- `--depth`: Research intensity (default: standard)
  - `quick`: Single broad query, no scraping (5-10 min)
  - `standard`: 3 focused queries, key page scraping (20-30 min)
  - `comprehensive`: 5+ queries, full site mapping (1-2 hours)
- `--comparison-context`: Who to compare against (default: Scrunch)

**Advanced Options:**
- `--category`: Industry/category (default: "AI Search Optimization Platform")
- `--model`: Deep research model (default: o3-deep-research-2025-06-26)
- `--custom-queries`: Additional custom questions (repeatable)
- `--skip-scraping`: Don't scrape website
- `--skip-profile`: Don't create profile template
- `--update-matrix`: Prompt to update comparison matrix

**Examples:**
```bash
# Quick reconnaissance (5-10 min)
uv run python integration/research-competitor.py \
  --domain peec.ai \
  --company-name "Peec.ai" \
  --depth quick

# Standard research (default, 20-30 min)
uv run python integration/research-competitor.py \
  --domain brightedge.com \
  --company-name "BrightEdge"

# Focused on product and pricing
uv run python integration/research-competitor.py \
  --domain otterly.ai \
  --company-name "Otterly.AI" \
  --research-focus product,customers \
  --skip-scraping

# Comprehensive with custom queries (1-2 hrs)
uv run python integration/research-competitor.py \
  --domain conductor.com \
  --company-name "Conductor" \
  --depth comprehensive \
  --comparison-context "Scrunch and other AI SEO platforms" \
  --custom-queries "What is their enterprise pricing model?" \
  --custom-queries "Which Fortune 500 companies use Conductor?"
```

## Research Best Practices

### 1. Start with Public Information

Use deep research to gather:
- Product features and capabilities
- Public pricing information
- Customer testimonials and case studies
- Market positioning and messaging

### 2. Validate with Website Scraping

Cross-reference deep research with actual website content:
- Product pages for feature accuracy
- Pricing pages for current tiers
- Customer pages for logos and case studies

### 3. Look for Signals

Pay attention to:
- Job postings (product direction)
- Recent blog posts (feature launches)
- Partnerships (GTM strategy)
- Customer testimonials (use cases)

### 4. Focus on Differentiation

Always answer:
- How are they different from Scrunch?
- What can Scrunch learn from their approach?
- Where are the market gaps Scrunch can fill?

### 5. Update Regularly

- **Quarterly**: Refresh profiles for Tier 1 competitors
- **Bi-annually**: Update Tier 2 competitors
- **Ad-hoc**: When major news/product launches occur

## Common Queries

### Run Research in Parallel

```bash
# Submit all queries without polling
uv run python integration/openai-deep-research.py \
  --query "Query 1..." --no-poll

uv run python integration/openai-deep-research.py \
  --query "Query 2..." --no-poll

uv run python integration/openai-deep-research.py \
  --query "Query 3..." --no-poll

# Poll for results later
uv run python integration/openai-deep-research.py --poll-id resp_xxx1
uv run python integration/openai-deep-research.py --poll-id resp_xxx2
uv run python integration/openai-deep-research.py --poll-id resp_xxx3
```

### Batch Scrape Multiple Competitors

```bash
# Create urls.txt with all competitor URLs
cat > urls.txt <<EOF
https://brightedge.com/product
https://otterly.ai/product
https://peec.ai/features
EOF

uv run python integration/company-scrape-url.py --urls-file urls.txt --max-workers 3
```

### Re-run Research with Updated Query

```bash
# Research evolves - update queries as needed
uv run python integration/openai-deep-research.py \
  --query "Updated query with more specific requirements..." \
  --output-dir company/{domain}/competitive-intelligence/research
```

## Troubleshooting

### Research Query Times Out

Increase wait time or use polling:
```bash
uv run python integration/openai-deep-research.py \
  --query "..." \
  --max-wait 7200  # 2 hours
```

### Scraping Fails (403/Blocked)

Some sites block automated scraping:
1. Try `--wait-for 3000` (wait 3 seconds before scraping)
2. Use `--mobile` flag for mobile user agent
3. Manual research as fallback

### Research Output is Too Generic

Make queries more specific:
- Include competitor name explicitly
- Reference specific products/features
- Ask for quantifiable metrics
- Specify comparison to "AI search optimization" or "LLM visibility"

## Next Steps

After completing research workflow:

1. **Share with team**: Competitive profile can inform positioning
2. **Update sales battlecards**: Strengths/weaknesses feed into objection handling
3. **Track feature parity**: Monitor when competitors add Scrunch-like features
4. **Monitor pricing changes**: Set up quarterly checks for pricing updates
5. **Expand coverage**: Move to Tier 2 competitors once Tier 1 is complete
