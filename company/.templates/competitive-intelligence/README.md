# Competitive Intelligence Templates

This folder contains templates for conducting competitive intelligence research on companies in Scrunch's market.

## Templates Available

### profile-template.md

Comprehensive competitive profile template covering:
- Company overview & funding
- Product offerings & pricing
- Customer segments & case studies
- Market positioning & messaging
- Competitive analysis vs Scrunch (SWOT)
- Research sources & next actions

## How to Use

### 1. Create Competitor Folder Structure

```bash
# For a new competitor
mkdir -p companies/{domain}/competitive-intelligence/{research,analysis}
```

### 2. Copy Template

```bash
# Copy the profile template
cp companies/.templates/competitive-intelligence/profile-template.md \
   companies/{domain}/competitive-intelligence/profile.md
```

### 3. Run Deep Research

Use the automated research script or run queries manually:

```bash
# Automated (recommended)
uv run python integration/research-competitor.py \
  --domain {competitor-domain} \
  --company-name "{Company Name}"

# Manual
uv run python integration/openai-deep-research.py \
  --query "What products and features does {Company} offer for AI search optimization?..." \
  --output-dir companies/{domain}/competitive-intelligence/research
```

### 4. Scrape Key Pages (Optional)

```bash
python integration/company-scrape-url.py \
  --url https://{domain}/product \
  --url https://{domain}/pricing \
  --url https://{domain}/customers \
  --only-main-content
```

### 5. Fill In Template

- Replace all `{placeholders}` with actual data
- Use research outputs from `research/` folder
- Add scraped content references from `../pages/` folder
- Synthesize findings into competitive analysis sections

### 6. Update Comparison Matrix

Add the competitor to `companies/competitive-landscape/comparison-matrix.md`

## Research Workflow

The complete research workflow is documented in `integration/README-competitive-research.md`.

Quick overview:

1. **Identify** competitor
2. **Create** folder structure
3. **Research** using deep research agent (3 queries)
4. **Scrape** key website pages
5. **Synthesize** into competitive profile
6. **Update** comparison matrix

## Best Practices

- **Be objective**: Focus on facts, not opinions
- **Cite sources**: Link to research files and scraped pages
- **Update regularly**: Quarterly refresh for active competitors
- **Quantify when possible**: Use metrics, pricing, customer counts
- **Focus on differentiation**: Highlight what makes them unique vs Scrunch
