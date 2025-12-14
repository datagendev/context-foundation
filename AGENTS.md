# Repository Guidelines

## Project Structure & Module Organization
This repo is a **GTM context “starter kit”**: mostly Markdown docs and templates organized by workflow area.

- `icp/` ICP definitions and `company-info-template.md`
- `TAM/` lead sourcing notes (LinkedIn, scraping, data vendors)
- `crm/` CRM schemas + integrations; call transcripts live in `crm/transcripts/`
- `outreach/` templates, campaigns, and results tracking
- `dashboards/` dashboard metadata templates by cadence (daily/weekly/monthly/etc.)
- `intelligence/` monitoring and research notes
- `synthesis/` canonical rollups (pain points, objections, trends)
- `agents/` agent specifications (prompts/skills/examples)
- `use-cases/`, `workflows/`, `playbooks/`, `training-data/`, `content-production/` for end-to-end examples and writing quality systems

Empty folders are tracked with `.gitkeep`. Prefer adding new content as Markdown under the most relevant area instead of creating new top-level folders.

## Build, Test, and Development Commands
There is **no build system** in this repo (no app to compile). Typical local checks are content-oriented:

- `rg -n "keyword" .` search across docs quickly
- `git status` / `git diff` review changes before pushing
- (optional) `markdownlint "**/*.md"` if you use `markdownlint` locally

## Coding Style & Naming Conventions
- Markdown: use clear `#`/`##` headings, short paragraphs, and bulleted lists; keep templates copy-pastable.
- Paths: prefer stable, predictable locations so other docs can link to them (e.g., `/crm/hubspot/contacts.md`).
- Naming:
  - General docs/directories: `kebab-case` (e.g., `serp-firecrawl/`, `company-info-template.md`).
  - Call transcripts: `YYYY-MM-DD_company-name_call-type.md` (example: `2024-03-15_acme-corp_discovery.md`).
  - Use cases: `overview.md`, `crm-integration.md`, `business-logic.md`, plus `examples/`.

## Testing Guidelines
Treat “tests” as **verification**:
- Ensure internal links and referenced paths exist.
- For templates, sanity-check that a new contributor can follow the steps without extra context.

## Commit & Pull Request Guidelines
- Commits: use short, imperative subjects consistent with history (e.g., `Add CRM entity docs`, `Update dashboards template`).
- PRs: describe *what changed* and *why*, list key paths touched, and include an example snippet/screenshot when adding dashboard specs or outreach templates.

## Security & Configuration Tips
- Do not commit API keys, OAuth tokens, or customer data; keep credentials in your secrets manager (or DataGen UI).
- Avoid placing secrets in assistant config (e.g., `.claude/settings.local.json`).
