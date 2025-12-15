# CRM Integration (Using Notion as the Source of Truth)

This use case assumes Notion is your primary “CRM-like” store for proposal data, even if you also have HubSpot/Salesforce.

## Notion Databases (Recommended)

### Accounts

**Goal:** company profile used for personalization and case study matching.

Suggested properties:
- `Name` (title)
- `Website` (url)
- `Industry` (select)
- `Geo` (multi-select)
- `ICP Tags` (multi-select)
- `Primary Contact` (relation → Contacts)
- `Notes` (rich text)

### Contacts

Suggested properties:
- `Name` (title)
- `Email` (email)
- `Role` (select)
- `Account` (relation → Accounts)

### Opportunities

**Goal:** the unit of proposal generation.

Suggested properties:
- `Name` (title) — e.g., `Student.be — Q1 Growth + Hiring`
- `Account` (relation → Accounts)
- `Owner` (people)
- `Stage` (select)
- `Target Start` (date)
- `Term (Months)` (number)
- `Bundle` (relation → Bundles)
- `Options` (relation → Bundles) — add-ons
- `Line Items` (relation → Line Items)
- `Commercial Terms` (relation → Terms Library)
- `Proposal Version` (number)

### Line Items

**Goal:** granular scope items used to build scope tables and pricing.

Suggested properties:
- `Name` (title) — e.g., `LinkedIn Post (x12)`
- `Opportunity` (relation → Opportunities)
- `Service Line` (select) — `Marketing`, `Creative`, `Recruitment`
- `SKU` (text)
- `Unit` (select) — `each`, `month`, `role`, `hour`
- `Quantity` (number)
- `Price Source` (select) — `Rate Card`, `Custom`
- `Rate Card Item` (relation → Rate Cards)
- `Unit Price` (number)
- `Discount %` (number)
- `Notes / Assumptions` (rich text)

### Rate Cards

Suggested properties:
- `SKU` (title)
- `Service Line` (select)
- `Unit` (select)
- `List Price` (number)
- `Min Qty` (number)
- `Tier Rules` (rich text or JSON-in-codeblock)
- `Active` (checkbox)

### Bundles (Packages + Add-ons)

Suggested properties:
- `Name` (title)
- `Type` (select) — `Base`, `Add-on`
- `Default Line Items` (relation → Rate Cards) or a “bundle items” database
- `Eligibility Tags` (multi-select) — used to show/hide options

### Copy Blocks

Suggested properties:
- `Name` (title)
- `Section` (select) — `Intro`, `Approach`, `Deliverables`, `Why Us`
- `Service Line` (select)
- `Tags` (multi-select)
- `Copy` (rich text)

### Case Studies

Suggested properties:
- `Name` (title)
- `Industry` (multi-select)
- `Service Line` (multi-select)
- `Outcome Metrics` (rich text)
- `Slides` (files or link to a PPT slide snippet)

### Terms Library

Suggested properties:
- `Name` (title)
- `Type` (select) — `Payment`, `SLA`, `Recruitment`, `Media`
- `Clause` (rich text)
- `When To Use` (multi-select)

## Joining Data

You’ll typically generate a proposal by pulling:
- `Opportunity` → `Account` + `Contacts`
- `Opportunity` → `Line Items` (+ related `Rate Card` items)
- `Opportunity` → `Copy Blocks` (selected by service line + tags)
- `Opportunity` → `Case Studies` (matched by industry/service)
- `Opportunity` → `Terms Library` (selected clauses)

## MCP/API Notes (Practical)

Depending on your tooling:
- **Notion API** supplies the structured deal data.
- **Microsoft Graph API** stores the PPT template and uploads the generated deck.

If you have a “proposal generator” service, treat Notion as the authoritative store and write back:
- proposal URL (PPT/PDF)
- totals (subtotal/discount/total)
- timestamp + generator version

