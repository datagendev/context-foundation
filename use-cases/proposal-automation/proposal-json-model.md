# Proposal JSON Model (Canonical Contract)

Use a stable JSON contract between:
- data pulls (Notion)
- pricing/content logic
- PowerPoint rendering

This prevents “PowerPoint logic” and keeps the generator testable.

## Minimal Schema (Conceptual)

```json
{
  "meta": {
    "proposal_id": "prop_2025-12-15_student-be_v1",
    "generated_at": "2025-12-15T00:00:00Z",
    "generator_version": "0.1.0",
    "template_id": "ppt_template_v3"
  },
  "account": {
    "name": "Student.be",
    "website": "https://www.student.be/nl/",
    "industry": "Education / Student platform",
    "geo": ["BE"]
  },
  "opportunity": {
    "name": "Student.be — Q1 Growth + Hiring",
    "owner": "Rep Name",
    "term_months": 3,
    "start_date": "2026-01-12",
    "bundle": "Growth Launch Pack (Base)",
    "options": ["Recruitment Sprint (Add-on)", "Creative Rush (Add-on)"]
  },
  "line_items": [
    {
      "service_line": "Creative",
      "sku": "CR-VID-45",
      "name": "Brand Video (45s)",
      "unit": "each",
      "quantity": 1,
      "unit_price": 6000,
      "discount_pct": 0,
      "notes": "Script + edit + captions"
    }
  ],
  "pricing": {
    "currency": "EUR",
    "discounts": [
      {
        "name": "Term discount",
        "applies_to_skus": ["MG-MONTH"],
        "discount_pct": 10
      }
    ],
    "totals": {
      "subtotal": 0,
      "discount_total": 0,
      "grand_total": 0
    },
    "group_totals": [
      {"group": "Creative / Production", "total": 12600},
      {"group": "Management", "total": 11460},
      {"group": "Recruitment", "total": 5900}
    ]
  },
  "slides": {
    "cover": {"title": "Proposal", "subtitle": "Q1 Growth + Hiring"},
    "executive_summary": {"bullets": []},
    "scope_tables": [],
    "assumptions": [],
    "terms": []
  },
  "charts": [
    {
      "id": "budget_breakdown",
      "type": "stacked_bar",
      "title": "Budget Breakdown (3 months)",
      "categories": ["Month 1", "Month 2", "Month 3"],
      "series": [
        {"name": "Setup", "values": [1200, 0, 0]},
        {"name": "Production", "values": [9000, 3600, 0]},
        {"name": "Management", "values": [3800, 3800, 3800]},
        {"name": "Recruitment", "values": [5900, 0, 0]}
      ]
    }
  ],
  "assets": {
    "case_studies": [],
    "images": []
  }
}
```

## Notes

- Keep monetary values as integers (minor units) or floats consistently; pick one and stick to it.
- Keep “selection results” (copy blocks, case studies) inside the JSON so decks are reproducible.
- Store the exact priced snapshot, not only pointers to rate cards.

