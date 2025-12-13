# Synthesis Documents

Canonical rollup documents that synthesize insights across all calls, content, and data sources.

## Purpose

These are the **foundational documents** that represent your accumulated knowledge. They get updated automatically from raw sources (transcripts, research, etc.) and serve as the single source of truth for the AI system.

## Core Synthesis Documents

### Customer Intelligence
- **pain-points.md** - All pain points across all calls, ranked by frequency
- **objections.md** - Common objections and effective responses
- **buying-signals.md** - Indicators of intent and readiness
- **tool-stacks.md** - Technologies mentioned by prospects/customers

### Market Intelligence
- **competitive-landscape.md** - How prospects compare you to alternatives
- **industry-trends.md** - Themes emerging from conversations
- **vertical-analysis.md** - Insights by industry vertical

### Product Intelligence
- **feature-requests.md** - What customers are asking for
- **use-cases.md** - How customers actually use the product
- **integration-needs.md** - What tools they want to connect

## How Synthesis Works

```
Raw Sources                    Synthesis Docs              Foundational
─────────────                  ──────────────              ────────────
/crm/transcripts/    ───┐
                        ├───►  pain-points.md    ───┐
/intelligence/       ───┤                          ├───►  positioning.md
                        ├───►  objections.md     ───┤
/TAM/ research       ───┘                          ├───►  messaging.md
                               competitive.md    ───┘
```

## Update Frequency

| Document | Update Trigger |
|----------|----------------|
| pain-points.md | After each call transcript |
| objections.md | After each call transcript |
| competitive.md | Weekly from intelligence feeds |
| vertical-analysis.md | Monthly rollup |

## Template

```markdown
# [Synthesis Topic]

## Last Updated
YYYY-MM-DD (auto-updated)

## Summary
[2-3 sentence overview of key findings]

## Key Insights

### [Category 1]
- **[Insight]**: [Evidence/source]
- **[Insight]**: [Evidence/source]

### [Category 2]
- **[Insight]**: [Evidence/source]

## Source Documents
- /crm/transcripts/2024-03-15_acme.md
- /crm/transcripts/2024-03-10_globex.md
- [etc.]

## Trends Over Time
[How this has evolved]
```
