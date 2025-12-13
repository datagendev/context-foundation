# Workflows

DataGen workflows that automate GTM processes.

## Files

### create-company-info.md
Workflow for generating `/create_company_info` endpoint:
- Automatically create company information from various sources
- Enrich company records with TAM data
- Generate ICP-matched company profiles
- Feed output to CRM

## Available Workflows

- **create-company-info** - Generate company profiles with enrichment
- [Add more as you build them]

## How to Create Workflows

1. Define the workflow trigger and input variables
2. Specify which DataGen tools to use
3. Map output to CRM or dashboards
4. Test with sample data
5. Document in this folder

## Integration Points

- **TAM sources**: Use for lead and company data
- **CRM**: Write enriched records
- **Dashboards**: Track workflow execution and results
- **Playbooks**: Reference company context
