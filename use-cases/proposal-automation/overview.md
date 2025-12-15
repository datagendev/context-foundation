# Proposal Automation (Notion → PowerPoint)

Generate a complete, client-ready proposal deck from structured deal data in Notion.

## Problem This Solves

For small B2B sales teams with **mixed offers** (creative/media + recruiting/job postings), proposals tend to be:
- Custom-scoped per deal (no “standard package”)
- Slow to produce due to **pricing page edits** and **PowerPoint charts/tables**
- Inconsistent (scope creep, wrong assumptions, outdated pricing, mismatched terms)

## Target Users

- 5 sales reps creating proposals weekly
- A pricing/revops owner maintaining rate cards and packaging
- Delivery leads who review scope feasibility (turnaround, capacity)

## Inputs (Source of Truth)

Store structured data in Notion (databases, not freeform pages):

- **Accounts**: company profile (industry, geo, ICP tags)
- **Opportunities**: deal context (stage, close date, owner, goals)
- **Line Items**: scoped deliverables (quantity, unit, price source)
- **Rate Cards**: current pricing tables, tiers, minimums
- **Bundles**: reusable packages and optional add-ons
- **Copy Blocks**: approved narrative paragraphs (tagged by service line)
- **Case Studies**: proof assets, metrics, and slides
- **Terms Library**: clauses and commercial terms by scenario

## Outputs

- PowerPoint deck (`.pptx`) generated from a template
- Optional PDF export for sharing and e-sign
- A “proposal record” written back to Notion (who generated, when, version, total)

## Reference Docs

- `use-cases/proposal-automation/proposal-json-model.md`
- `use-cases/proposal-automation/pipeline.md`
- `use-cases/proposal-automation/ppt-generation-flow.md`
- `use-cases/proposal-automation/examples/2025-12-15_student-be_proposal-mock.md`

## High-Level Flow

1. Sales rep opens a deal in Notion and selects a bundle + options.
2. Generator pulls data from Notion, validates required inputs, and prices the scope.
3. Generator selects matching copy blocks + case studies.
4. Generator fills a PowerPoint template:
   - Cover, agenda, problem/solution
   - Scope tables
   - Pricing table
   - Charts (timeline, budget breakdown)
   - Terms + next steps
5. The deck is uploaded to SharePoint/OneDrive (or attached back to Notion) and optionally sent for e-sign.

## What “One Click” Really Means

The click should only choose:
- Client / opportunity
- Bundle (base package)
- Options (add-ons)

Everything else should be derived:
- Prices from rate cards and pricing rules
- Content from approved blocks and case study tags
- Slides from a locked template
