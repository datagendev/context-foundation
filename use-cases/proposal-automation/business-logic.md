# Business Logic

This page outlines the minimum logic you need for reliable “one click → full proposal”.

## 1) Pricing Rules (Common for Mixed Offers)

### Line item price calculation

Inputs (per line item):
- `unit_price` (from rate card or custom override)
- `quantity`
- `discount_pct` (optional)

Outputs:
- `line_subtotal = unit_price * quantity`
- `line_discount = line_subtotal * discount_pct`
- `line_total = line_subtotal - line_discount`

### Deal-level pricing rules

Typical rules for mixed offers:
- **Minimums**: e.g., campaign management minimum monthly fee
- **Term discounts**: e.g., 10% off retainers for 3+ month commitment
- **Bundled discounts**: when buyer selects both Marketing + Recruitment
- **Pass-through costs**: ad spend / job board fees (at cost or marked up)
- **Rounding**: round to nearest €10 / €50 for clean tables

### Validation checks (stop the “one click”)

Fail fast if:
- a line item is missing `unit_price` or `quantity`
- a “monthly” item is used but `term_months` is missing
- a bundle is selected but required line items are missing
- discount exceeds a configured max (e.g., 25%) without approval

## 2) Content Selection (Copy + Proof)

The generator should only use **approved** content blocks.

Example rules:
- Select intro blocks by `industry` + `service_line`
- Select 2–3 case studies matching `industry` and at least one `service_line`
- If no match, fall back to “general” case studies with strongest metrics

## 3) PowerPoint Data Outputs

To avoid manually editing tables and charts, generate these as data structures:

### Pricing table model

- Rows: each service group (Creative, Media Mgmt, Recruitment)
- Columns: description, qty, unit price, subtotal, discount, total
- Footer: subtotal, discounts, total, payment schedule

### Chart model (budget breakdown)

Keep a single canonical series format the PPT engine can render:
- categories: months or phases (e.g., `Month 1`, `Month 2`, `Month 3`)
- series: `Setup`, `Production`, `Management`, `Recruitment`, `Pass-through`

## 4) Proposal Versioning

Treat proposals as immutable snapshots:
- `proposal_version` increments each generation
- store the exact line items and prices used (not just pointers)
- store the template version (so you can reproduce decks)

