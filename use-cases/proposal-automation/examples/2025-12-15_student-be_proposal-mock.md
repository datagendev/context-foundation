# Mock Proposal Example: Student.be (Notion → PowerPoint)

This is a realistic *demo* deal you can showcase to stakeholders to explain the “one click → full proposal” experience.

## Prospect Snapshot (from Notion `Accounts`)

- **Account:** Student.be
- **Website:** https://www.student.be/nl/
- **Type (assumption):** student-focused portal with jobs/housing content
- **Primary buyer persona:** Head of Growth / Partnerships
- **Deal name:** `Student.be — Q1 Growth + Hiring`

## Why This Deal Is “Complex”

It mixes:
- **Creative / media production** (banners, posts, video)
- **Ongoing campaign management** (monthly retainer)
- **Recruitment support** (job postings + screening for key hires)

Each part uses different units, timing, and pricing logic.

## Proposal Config (from Notion `Opportunities`)

- `Target Start`: 2026-01-12
- `Term (Months)`: 3
- `Bundle`: `Growth Launch Pack (Base)`
- `Options`:
  - `Recruitment Sprint (Add-on)`
  - `Creative Rush (Add-on)`
- `Commercial Terms`:
  - `Net 15`
  - `2 revision rounds included`

## Line Items (from Notion `Line Items`)

### Marketing / Creative

| SKU | Item | Unit | Qty | Unit Price | Notes |
|---|---|---:|---:|---:|---|
| CR-BNR-SET | Banner Set (IAB + Social variants) | each | 1 | €1,500 | Includes 6 sizes + 2 iterations |
| CR-SOC-POST | Social Posts (LinkedIn/IG) | each | 20 | €120 | Copy + design |
| CR-VID-45 | Brand Video (45s) | each | 1 | €6,000 | Script + edit + captions |
| CR-VID-CUT | Video Cutdowns (15s) | each | 3 | €900 | Derived from main video |

### Media / Growth Management (Recurring)

| SKU | Item | Unit | Qty | Unit Price | Notes |
|---|---|---:|---:|---:|---|
| MG-SETUP | Tracking + Campaign Setup | each | 1 | €1,200 | Pixel, UTMs, dashboards |
| MG-MONTH | Campaign Management Retainer | month | 3 | €3,800 | Weekly optimization + reporting |

### Recruitment (Add-on)

| SKU | Item | Unit | Qty | Unit Price | Notes |
|---|---|---:|---:|---:|---|
| RC-ROLE-PACK | Hiring Sprint (per role) | role | 2 | €2,500 | Posting + screening + shortlist |
| RC-JB-FEES | Job Board Fees (pass-through) | each | 1 | €900 | At cost, no markup |

## Pricing Logic (what the generator computes)

### Discounts

- 10% off `MG-MONTH` for 3-month term commitment

### Totals (example output)

- **Creative / Production subtotal:** €1,500 + (20×€120) + €6,000 + (3×€900) = **€12,600**
- **Management subtotal:** €1,200 + (3×€3,800) = €12,600  
  - **Term discount (10% on retainer only):** 10% × (3×€3,800) = **€1,140**
  - **Management total:** €12,600 − €1,140 = **€11,460**
- **Recruitment subtotal:** (2×€2,500) + €900 = **€5,900**
- **Grand total:** €12,600 + €11,460 + €5,900 = **€29,960**

## PowerPoint Slides (Template Fill)

Minimum “showcase” deck outline:

1. **Cover**: `{{account_name}}`, `{{opportunity_name}}`, date
2. **Executive Summary**: goals, approach, what’s included
3. **Scope Overview**: 3-column blocks (Creative / Management / Recruitment)
4. **Deliverables Table**: auto-generated from line items
5. **Timeline**: 3-month plan (by week or month)
6. **Pricing**: group totals + deal total
7. **Budget Breakdown Chart**: stacked bars by month (computed)
8. **Assumptions**: pulled from line item notes + terms
9. **Terms**: selected clauses
10. **Next Steps**: signature, kickoff, intake checklist

## Chart Data (Budget Breakdown)

Example series for a stacked bar chart:

- Categories: `Month 1`, `Month 2`, `Month 3`
- Series:
  - `Setup`: Month 1 = 1200, Month 2 = 0, Month 3 = 0
  - `Production`: Month 1 = 9000, Month 2 = 3600, Month 3 = 0
  - `Management`: Month 1 = 3800, Month 2 = 3800, Month 3 = 3800 (apply discount in totals)
  - `Recruitment`: Month 1 = 5900, Month 2 = 0, Month 3 = 0

## What This Demo Proves

- A rep only selects **bundle + options**.
- Notion provides scope + pricing inputs.
- The generator outputs tables + charts without manual PowerPoint edits.

