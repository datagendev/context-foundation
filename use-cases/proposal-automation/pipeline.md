# Pipeline (Notion → Proposal JSON → PowerPoint)

This describes a practical integration plan using APIs/MCP tools.

## Data Pulls (Notion API)

From Notion, fetch:

1. `Opportunity` record (bundle/options, term, start date)
2. Related `Account` + `Contacts`
3. Related `Line Items`
4. `Rate Cards` referenced by line items (when `Price Source = Rate Card`)
5. Selected `Terms Library` clauses
6. Optional: `Copy Blocks` + `Case Studies` using tags (industry/service line)

Output: a fully-resolved `proposal.json` (see `use-cases/proposal-automation/proposal-json-model.md`).

## Document Generation (PowerPoint)

There are two common approaches:

### A) Template fill (fastest to implement)

- Keep a master `.pptx` template with placeholder tokens like `{{account_name}}`.
- Generate:
  - tables (scope + pricing)
  - chart data (budget breakdown, timeline)
- Render:
  - tables as PPT tables, or as images (for consistent formatting)
  - charts as images (generated from the canonical chart model)

### B) “Native” PowerPoint chart updates (best fidelity, more effort)

- Update embedded chart data in the `.pptx` (Excel worksheet parts inside PPTX).
- Preserves native PowerPoint chart styling and editability.

## Storage + Sharing (Microsoft 365)

If your team works in SharePoint/OneDrive:

- Use **Microsoft Graph API** to:
  - copy the template to a new file (per proposal version)
  - upload the generated `.pptx`
  - export to PDF when needed
  - set sharing permissions for the buyer

## Optional: E-sign + Tracking

- Use an e-sign API (DocuSign/Dropbox Sign/PandaDoc) to send the PDF.
- Use webhooks to write status back to Notion (`Sent`, `Viewed`, `Signed`).

## Where MCP Helps

If you have MCP servers for these services, the generator can call:

- **Notion MCP**: query/update databases without hardcoding HTTP calls
- **Microsoft 365 MCP** (or Graph wrapper): upload/export/share files
- **CRM MCP** (optional): pull the deal context if Notion is not the CRM

The key design choice: keep the **proposal JSON** as the stable interface so you can swap tools (MCP vs direct API) without rewriting PowerPoint logic.

