# Content Production

Automated content pipeline from research to publication.

## Workflow Overview

```
RSS Feeds → Classification → Weekly Briefing → Content Ideas → Draft → Edit → Publish
```

## Folders

### rss-feeds/
Configuration for automated content ingestion:
- Industry news sources
- Competitor blogs
- Influencer newsletters
- Reddit/social monitoring

### briefings/
Weekly intelligence briefings generated from ingested content:
- Top stories and why they matter
- Suggested content angles
- Competitive moves
- Market trends

### editorial-training/
Training data to improve content quality:
- Before/after editing examples
- Style corrections
- Tone adjustments

## Content Pipeline

### 1. Daily Ingestion (Automated)
- Fetch 100-200 articles from RSS feeds
- Classify by relevance to ICP and product
- Store in database with metadata
- Filter noise, keep signal

### 2. Weekly Briefing (Automated + Human Review)
- Synthesize week's articles into internal brief
- Surface top 3-5 themes
- Suggest content angles tied to current events
- Generate draft newsletter

### 3. Content Production (Human + AI)
- Select angle from briefing
- Run through content agents:
  1. Topic selection
  2. Angle/hook development
  3. Headline options
  4. Outline creation
  5. Draft writing
  6. SEO optimization
  7. Editorial polish
  8. Final review

### 4. Distribution
- Push to CMS
- Generate email HTML
- Schedule social posts

## Integration Points

- **Intelligence**: `/intelligence/` for market monitoring
- **ICP**: `/icp/` for audience targeting
- **Training**: `/training-data/` for quality improvement
- **Outreach**: `/outreach/` for email campaigns
