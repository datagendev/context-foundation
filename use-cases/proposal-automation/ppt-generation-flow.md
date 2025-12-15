# PowerPoint Generation Flow

This is a practical way to “industrialize” proposals while keeping PowerPoint as the output format.

## 1) Maintain a Locked Template Deck

Create a single source `.pptx` template with:
- slide layouts already designed (fonts, spacing, brand)
- placeholders for dynamic fields (tokens)
- reserved areas for tables and charts

## 2) Placeholder Conventions (Tokens)

Use simple tokens that are easy to replace:
- `{{account_name}}`
- `{{opportunity_name}}`
- `{{proposal_date}}`
- `{{term_months}}`

Avoid doing logic in PowerPoint. All decisions happen before render (in `proposal.json`).

## 3) Slide-to-Data Mapping (Example)

Recommended mapping between slide types and `proposal.json`:

- **Cover** → `account.name`, `opportunity.name`, `meta.generated_at`
- **Executive Summary** → `slides.executive_summary.bullets`
- **Scope** → `line_items` grouped by `service_line`
- **Pricing** → `pricing.group_totals` + `pricing.totals`
- **Budget Chart** → `charts[id="budget_breakdown"]`
- **Assumptions** → `slides.assumptions` + line item notes
- **Terms** → `slides.terms` (selected clauses)

## 4) Tables and Charts: Choose Your Rendering Strategy

### Option A (recommended for speed): render as images

- Build tables/charts from the canonical models.
- Render to images (consistent formatting).
- Insert images into the reserved areas on the slide.

Pros: easiest and most reliable.  
Cons: charts aren’t editable inside PowerPoint.

### Option B: native PPT tables + native charts

- Create PPT tables programmatically.
- Update chart data inside the PPTX.

Pros: editable charts/tables.  
Cons: more engineering effort and edge cases.

## 5) Output Artifacts

Generate and store:
- `.pptx` (internal editable version)
- `.pdf` (buyer-safe sharing)
- a `proposal.json` snapshot for reproducibility

