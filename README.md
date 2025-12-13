# Context Foundation - GTM Boilerplate

A comprehensive folder structure for building Go-To-Market workflows with DataGen.

## Folder Structure Overview

```
context-foundation/
├── TAM/              # Lead sourcing - Total Addressable Market
├── use-cases/        # End-to-end workflow examples
├── playbooks/        # Company context and documentation
├── icp/              # Customer personas and targeting
├── outreach/         # Messaging templates and campaigns
├── crm/              # CRM integrations (Hubspot, Supabase, etc.)
├── dashboards/       # Streamlit dashboards by schedule
├── intelligence/     # Intent signals and news monitoring
└── workflows/        # DataGen automation workflows
```

## Quick Start

### 1. Define Your ICP
Start in `/icp/`:
- Fill out `personas.md` with target customer profiles
- Document your company in `company-info-template.md`

### 2. Source Leads
Use `/TAM/`:
- Choose data sources (LinkedIn, Ocean.io, web scraping)
- Follow sourcing playbooks for your industry
- Export leads to CRM

### 3. Set Up CRM Integration
Configure `/crm/`:
- Choose your CRM (Hubspot, Supabase, Salesforce)
- Map lead data to CRM objects
- Set up MCP integrations

### 4. Plan Campaigns
Create `/outreach/` campaigns:
- Choose outreach platform (Instantly, Smartlead, Heyreach)
- Use templates and personalization
- Track results in dashboards

### 5. Monitor Performance
Set up `/dashboards/`:
- Create daily/weekly dashboards for campaign metrics
- Monitor lead velocity and conversion
- Track intelligence signals

### 6. Enhance with Intelligence
Configure `/intelligence/`:
- Set up news monitoring for intent signals
- Create real-time alerts for high-value prospects
- Enrich campaign targeting with intent data

### 7. Build Workflows
Automate with `/workflows/`:
- Create DataGen workflows for repeatable processes
- Automate lead enrichment and company profiling
- Schedule recurring data syncs

## Key Concepts

### TAM (Total Addressable Market)
All available leads matching your ICP. Sources include:
- LinkedIn (via crustData)
- B2B data platforms (Ocean.io, PandaMatch)
- Web scraping (Firecrawl, Apify)

### ICP (Ideal Customer Profile)
Your target customer definition:
- Industry, company size, revenue
- Job titles and roles
- Pain points and needs
- Buying signals and intent

### Use Cases
End-to-end workflows:
- **Prospecting at Scale** - CSV enrichment with CRM
- **Lead Routing** - Real-time lead assignment
- **CRM Hygiene** - Data quality and deduplication

### Dashboards
Monitoring and analytics by frequency:
- **Daily** - Daily metrics and health checks
- **Weekly** - Campaign performance
- **Monthly** - KPI reviews
- **Recurring** - Real-time monitoring
- **Manual** - On-demand analysis

## Workflow: From Leads to Revenue

```
TAM Sources → ICP Filtering → Lead Enrichment → CRM → Outreach → Intelligence → Dashboards
   (Get leads)    (Target)      (Companies)    (Store)  (Campaign) (Signals)   (Monitor)
```

## Integration with DataGen

This context folder works with DataGen's:
- **Tool discovery** - `/searchTools` finds TAM and CRM tools
- **Code execution** - `/executeCode` processes and enriches data
- **Workflows** - Automated multi-step processes
- **MCP servers** - OAuth-authenticated tool access

## Examples

See `/use-cases/` for real-world examples:
- **prospecting-at-scale/** - How Scrunch.com sources B2B leads
- **lead-routing/** - Intelligent lead assignment
- **crm-hygiene/** - Data cleaning and deduplication

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
