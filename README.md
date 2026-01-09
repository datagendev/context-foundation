# Context Foundation — Claude Code Operable GTM Context

This repo is a **GTM context starter kit** designed to be operated by **Claude Code**.

It combines:
- a predictable folder structure so an AI agent can navigate and find context effeciently
- scripts + DataGen MCP integrations to pull/push context from external systems
- agent specs (skills + commands) to orchestrate repeatable GTM actions end-to-end

## Folder Structure Overview

```
context-foundation/
├── TAM/                  # Lead sourcing - Total Addressable Market
├── company/              # Company research + scraped artifacts
├── use-cases/            # End-to-end workflow examples
├── playbooks/            # Company context and documentation
├── icp/                  # Customer personas and targeting
├── outreach/             # Messaging templates and campaigns
├── crm/                  # CRM integrations + call transcripts
├── synthesis/            # Canonical rollup docs (pain points, objections, etc.)
├── content-production/   # Automated content pipeline (RSS → briefings → publish)
├── agents/               # Specialized AI agents for GTM workflows
├── integration/          # Integration glue (scraping, mapping, sync helpers)
├── scripts/              # Local helpers (automation + maintenance)
├── training-data/        # Tone of voice, editing examples, copywriting principles
├── dashboards/           # Streamlit dashboards by schedule
├── intelligence/         # Intent signals, news monitoring, research
└── workflows/            # DataGen automation workflows
```

## How Claude Code Operates This Repo

Claude Code works best when context is:
- **where you expect it** (stable paths)
- **small and composable** (short docs you can link together)
- **action-oriented** (templates, checklists, and commands that turn context into output)

This repo is organized around that operating model:

1. **Context** land in predictable places:
   - ICP + targeting: `icp/`
   - Lead sources: `TAM/`
   - CRM + calls: `crm/` (including `crm/transcripts/`)
   - Research + competitive intel: `company/`, `intelligence/`
2. **Synthesis** turns raw inputs into “canonical truth”:
   - objections, pains, positioning, messaging: `synthesis/`
3. **Actions** are executed and tracked with reusable assets:
   - outreach templates + campaigns: `outreach/`
   - reporting dashboards: `dashboards/`
   - automations: `workflows/`
4. **Orchestration** lives in:
   - agent specs (prompts/skills/examples): `.claude/agents/`
   - integration glue code: `integration/`
   - local helper scripts: `scripts/`
   

## Agents, Skills, and Commands

Claude Code extensions live in `.claude/` and provide repeatable, specialized workflows.

### Agents (`.claude/agents/`)

Multi-step workflows for GTM research and automation:

| Agent | Description | Model |
|-------|-------------|-------|
| `map-company-website` | Maps company website URLs via Firecrawl, saves to `companies/<domain>/site-map/` | sonnet |
| `competitive-intelligence` | Research competitors, build profiles, save to `companies/<domain>/competitive-intelligence/` | sonnet |
| `icp-architect` | Build pain-based ICP segments with programmatic signals | opus |
| `tam-web-research` | TAM analysis and market intelligence, saves to `/TAM/` | sonnet |
| `deep-research-agent` | Deep research using OpenAI Deep Research workflow | sonnet |
| `slack-message-sender` | Send messages to Slack channels via DataGen MCP | sonnet |

### Skills (`.claude/skills/`)

Reusable single-purpose capabilities (from [Anthropic skills repo](https://github.com/anthropics/skills)):

| Skill | Description |
|-------|-------------|
| `pptx` | Create and edit PowerPoint presentations |
| `docx` | Create and edit Word documents |
| `xlsx` | Create and edit Excel spreadsheets |
| `pdf` | PDF manipulation and form filling |
| `skill-creator` | Guide for creating new skills |
| `brand-guidelines` | Apply Anthropic brand styling |

### Commands (`.claude/commands/`)

Shortcut triggers for common workflows:

| Command | Description |
|---------|-------------|
| `/test-icp` | Test the ICP architect agent with a new company |

When adding a new agent, include:
- a clear trigger phrase
- the exact context files it should read (stable paths)
- the output file location(s) it should write
- human checkpoints for high-impact actions (publishing, CRM writes, sending outreach)

## Quick Start

1. Install Claude Code
   - Install + authenticate Claude Code on your machine, then open this repo in Claude Code.
   - macOS (Homebrew + npm):
     - `brew install node`
     - `npm install -g @anthropic-ai/claude-code`
   - Verify: `claude --help`

2. Install the Python venv with uv
   - Install Python 3.13+ (see `pyproject.toml`)
     - macOS (Homebrew): `brew install python@3.13`
     - Verify: `python3 --version`
   - Install uv
     - macOS (Homebrew): `brew install uv`
     - Verify: `uv --version`
   - Create/restore the venv: `uv sync`

3. Configure environment variables
   - `cp .env.example .env`
   - Fill in required values in `.env` (at minimum `DATAGEN_API_KEY`; others depend on which integrations/scripts you run)

### Next: Run the GTM Workflow with Agents

The recommended workflow uses specialized agents in sequence:

**Step 4: Map Your Target Company**
```
Use the map-company-website agent to create a sitemap inventory
→ Saves to: companies/<domain>/site-map/
```
Example: "Map the website for stripe.com focusing on enterprise and pricing pages"

**Step 5: Research Competitors**
```
Use the competitive-intelligence agent to build competitor profiles
→ Saves to: companies/<domain>/competitive-intelligence/
```
Example: "Research BrightEdge as a competitor with standard depth"

**Step 6: Define Your ICP**
```
Use the icp-architect agent to create pain-based customer segments
→ Saves to: icp-segments/<segment-name>/
```
Example: "Build ICP segments based on our company context"

**Step 7: Build Your TAM**
```
Use the tam-web-research agent to gather market intelligence
→ Saves to: TAM/
```
Example: "Research the market size for AI sales tools in the SMB segment"

**Step 8: Set up CRM Integration**
   - Configure `/crm/` mappings and connect MCP tools so Claude can read/write objects

**Step 9: Plan Campaigns**
   - Use `/outreach/` for templates, sequences, and results tracking

**Step 10: Monitor Performance**
   - Use `/dashboards/` for daily/weekly/monthly reporting

**Step 11: Build Automations**
   - Use `/workflows/` + `/integration/` to turn repeatable GTM tasks into scheduled runs

## Key Concepts

### TAM (Total Addressable Market)
All available leads matching your ICP. Sources include:

[Implemeted]
- Web Search (via Parallel, Exa)

[Roadmap]
- Web scraping (Firecrawl, Apify)
- B2B data platforms (Ocean.io, PandaMatch)

### ICP (Ideal Customer Profile)
Your target customer definition, expressed in a way an agent can act on:
- Pain segments (what’s breaking)
- Trigger moments (when urgency spikes)
- Priority prompts/topics (what buyers ask AI)
- “First win” outcomes (what to improve first)

### Dashboards
Monitoring and analytics by frequency:
- **Daily** - Daily metrics and health checks
- **Weekly** - Campaign performance
- **Monthly** - KPI reviews
- **Recurring** - Real-time monitoring
- **Manual** - On-demand analysis

## Workflow: From Leads to Revenue
End-to-end workflows:
- **Prospecting at Scale** - CSV enrichment with CRM
- **Lead Routing** - Real-time lead assignment
- **CRM Hygiene** - Data quality and deduplication

```
TAM Sources → ICP Filtering → Lead Enrichment → CRM → Outreach → Intelligence → Dashboards
   (Get leads)    (Target)      (Companies)    (Store)  (Campaign) (Signals)   (Monitor)
```

## Integration with DataGen

This repo is meant to be “live” when connected to DataGen:
- **MCP tool discovery**: `/searchTools` to find connectors/tools for your GTM stack
- **Execution**: `/executeCode` to transform data and write results back to systems
- **Workflows**: scheduled, multi-step automations under `/workflows/`
- **Integration glue**: helpers under `/integration/` and `/scripts/` to bridge context sources

## Examples

See `/use-cases/` for real-world examples:
- **prospecting-at-scale/** - How Scrunch.com sources B2B leads
- **lead-routing/** - Intelligent lead assignment
- **crm-hygiene/** - Data cleaning and deduplication

## Local Verification (no build system)

This repo is mostly Markdown. Typical checks are content-oriented:
- `rg -n "keyword" .` to find/edit related context quickly
- `git diff` / `git status` to review changes
- (optional) `markdownlint "**/*.md"` if you use markdownlint locally

## Next Steps

1. **Clone/fork** this repository
2. **Customize** ICP and company info
3. **Connect** TAM data sources
4. **Test** with sample leads
5. **Deploy** dashboards and workflows
6. **Scale** with DataGen automation

---

For more information:
- DataGen docs: https://docs.datagen.ai
- DataGen UI: https://app.datagen.ai
- MCP Documentation: https://modelcontextprotocol.io
