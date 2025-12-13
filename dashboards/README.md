# Dashboards

Vibe-coded Streamlit dashboards for monitoring and analytics across your GTM workflow.

## Dashboard Organization

Dashboards are organized by execution frequency:

- **recurring/** - Continuous or event-triggered dashboards
- **daily/** - Dashboards that run once per day
- **weekly/** - Weekly snapshots and reports
- **monthly/** - Monthly KPI tracking and reviews
- **quarterly/** - Quarterly business reviews
- **specific-datetime/** - One-time scheduled runs at specific dates/times
- **manual-oneoff/** - On-demand, manually triggered dashboards

## Dashboard Metadata

Each dashboard includes metadata:
- **Summary** - What does this dashboard show?
- **Date Created/Modified** - Tracking history
- **Data Sources** - Which TAM, CRM, intelligence sources does it use?
- **Related Business Areas** - Prospecting, lead routing, CRM hygiene, etc.
- **Dependencies** - Required tools, APIs, database tables
- **Configuration** - Refresh rate, filters, access controls
- **Code Location** - Where the Streamlit app and data pipeline live

## Creating a New Dashboard

1. Copy the `dashboard-template.md` from the appropriate frequency folder
2. Fill in all metadata sections
3. Create your Streamlit app (`.py` file)
4. Link to data sources in TAM, CRM, or intelligence folders
5. Document the data pipeline
6. Update the metadata with actual implementation details

## Dashboard Template

See `[frequency]/dashboard-template.md` for the complete metadata template structure.
