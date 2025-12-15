# CRM Integrations

Comprehensive documentation for connecting DataGen to your CRM systems.

## Core CRM Entities

| Entity | HubSpot | Salesforce | Purpose |
|--------|---------|------------|---------|
| **Contacts** | `contacts.md` | `contacts.md` | Individual people/leads |
| **Companies** | `companies.md` | `accounts.md` | Organizations/businesses |
| **Deals** | `deals.md` | `opportunities.md` | Sales pipeline tracking |

## CRM Platforms

### hubspot/
HubSpot CRM platform - core sales entities:
- **contacts.md** - People you're selling to (schema, MCP examples, queries)
- **companies.md** - Organizations and accounts
- **deals.md** - Sales opportunities and pipeline

### salesforce/
Salesforce CRM platform - core sales entities:
- **setup.md** - Configuration and authentication
- **contacts.md** - Qualified people associated with accounts
- **accounts.md** - Companies and organizations
- **opportunities.md** - Sales deals and pipeline

### supabase/
Supabase (PostgreSQL + Auth/Storage) as an application database and/or operational data layer.

See: `crm/supabase/README.md`

### neon/
Neon (serverless Postgres) as a Postgres backend for warehouses, environments, or sync targets.

See: `crm/neon/README.md`

### file-metadata/
Additional CRM data sources and metadata enrichment

## Entity Relationship Overview

```
                    ┌─────────────┐
                    │  COMPANY    │
                    │  (Account)  │
                    └──────┬──────┘
                           │
              ┌────────────┼────────────┐
              │            │            │
              ▼            ▼            ▼
        ┌──────────┐ ┌──────────┐ ┌──────────┐
        │ CONTACT  │ │  DEAL    │ │ ACTIVITY │
        │ (Person) │ │ (Opp)    │ │ (Tasks)  │
        └──────────┘ └──────────┘ └──────────┘
```

## Getting Started

1. **Choose your CRM platform** (HubSpot or Salesforce)
2. **Read the entity docs** for schema and field definitions
3. **Map your TAM data** (see `/TAM/`) to CRM objects
4. **Use MCP examples** to create, query, and update records
5. **Monitor data quality** (see `/intelligence/`)

## Common Workflows

### Lead → Contact → Deal Flow
1. Source leads from `/TAM/` (LinkedIn, web scraping)
2. Create **Contact** record with enriched data
3. Associate with **Company/Account** (create if needed)
4. Create **Deal/Opportunity** when qualified
5. Track pipeline progression through stages

### Data Enrichment Flow
1. Get company domain from TAM source
2. Search CRM for existing Company/Account
3. Create or update with enriched data
4. Link associated Contacts
5. Update deal associations if applicable
