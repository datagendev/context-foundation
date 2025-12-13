# Outreach

Email and messaging templates, campaign management, and results tracking.

## Folders

### templates/
Outreach message templates for different platforms:
- **instantly.md** - Instantly campaign templates and best practices
- **smartlead.md** - Smartlead sequences and follow-ups
- **heyreach.md** - Heyreach messaging templates

### campaigns/
Campaign management and examples
- **examples.md** - Real campaign setups and configurations

### results/
Campaign performance tracking
- **metrics.md** - KPIs, conversion rates, response rates

## Outreach Workflow

1. **Get leads** from `/TAM/` (LinkedIn, web scraping, etc.)
2. **Filter by ICP** using `/icp/` definitions
3. **Enrich with context** from `/intelligence/` (news, intent signals)
4. **Choose template** from `/outreach/templates/`
5. **Launch campaign** on Instantly/Smartlead/Heyreach
6. **Track results** in `/outreach/results/`
7. **Monitor with dashboards** in `/dashboards/`

## Key Integrations
- **Lead sources**: `/TAM/`
- **Personalization context**: `/playbooks/` (Llama Index for company docs)
- **Campaign tracking**: `/dashboards/` (Weekly/daily results dashboards)
- **CRM integration**: `/crm/` (Log interactions and outcomes)
