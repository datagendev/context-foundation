# HubSpot Companies

Organizations and accounts in your CRM - the businesses you're targeting.

## Schema

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Unique HubSpot company ID |
| `name` | string | Company name |
| `domain` | string | Primary website domain |
| `industry` | string | Industry classification |
| `type` | enum | PROSPECT, PARTNER, RESELLER, VENDOR, OTHER |
| `numberofemployees` | number | Employee count |
| `annualrevenue` | number | Annual revenue (USD) |
| `city` | string | City |
| `state` | string | State/Region |
| `country` | string | Country |
| `phone` | string | Main phone number |
| `description` | string | Company description |
| `hs_lead_status` | enum | Company-level lead status |
| `lifecyclestage` | enum | Company lifecycle stage |
| `createdate` | datetime | Record creation date |
| `lastmodifieddate` | datetime | Last update timestamp |

## Required Fields
- `name` OR `domain`

## Relationships
- **Contacts**: Multiple contacts can be associated with one company
- **Deals**: Multiple deals can be associated with one company
- **Parent Company**: Companies can have parent-child relationships

## MCP Integration

### Create Company
```python
mcp_Hubspot_create_company({
    "name": "Acme Corporation",
    "domain": "acme.com",
    "industry": "Software",
    "numberofemployees": 500,
    "annualrevenue": 50000000
})
```

### Search Companies
```python
mcp_Hubspot_search_companies({
    "query": "acme.com",
    "properties": ["name", "domain", "industry", "numberofemployees"]
})
```

### Get Company by ID
```python
mcp_Hubspot_get_company({
    "company_id": "12345",
    "properties": ["name", "domain", "industry", "annualrevenue"]
})
```

### Get Company by Domain
```python
mcp_Hubspot_search_companies({
    "filterGroups": [{
        "filters": [{
            "propertyName": "domain",
            "operator": "EQ",
            "value": "acme.com"
        }]
    }]
})
```

### Update Company
```python
mcp_Hubspot_update_company({
    "company_id": "12345",
    "properties": {
        "lifecyclestage": "customer",
        "type": "PARTNER"
    }
})
```

## Example Queries

### Find companies by industry
```python
companies = mcp_Hubspot_search_companies({
    "filterGroups": [{
        "filters": [{
            "propertyName": "industry",
            "operator": "EQ",
            "value": "Software"
        }]
    }]
})
```

### Find companies by employee count range
```python
companies = mcp_Hubspot_search_companies({
    "filterGroups": [{
        "filters": [
            {"propertyName": "numberofemployees", "operator": "GTE", "value": "100"},
            {"propertyName": "numberofemployees", "operator": "LTE", "value": "1000"}
        ]
    }]
})
```

### Find companies without deals
```python
# Query companies and check deal associations
companies = mcp_Hubspot_search_companies({
    "properties": ["name", "domain"],
    "associations": ["deals"]
})
no_deals = [c for c in companies if not c.get("associations", {}).get("deals")]
```

## Common Workflows

1. **Account Enrichment**: Enrich company with TAM data (employee count, revenue, tech stack)
2. **Account Scoring**: Score companies based on ICP fit
3. **Territory Assignment**: Assign companies to sales reps by region/industry
4. **Duplicate Detection**: Find and merge duplicate companies by domain
5. **Hierarchy Mapping**: Link parent and child company relationships
