# HubSpot Contacts

Individual people/leads in your CRM - the people you're selling to.

## Schema

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Unique HubSpot contact ID |
| `email` | string | Primary email address |
| `firstname` | string | First name |
| `lastname` | string | Last name |
| `phone` | string | Phone number |
| `jobtitle` | string | Job title/role |
| `company` | string | Company name (text) |
| `associatedcompanyid` | string | Link to Company record |
| `lifecyclestage` | enum | subscriber, lead, marketingqualifiedlead, salesqualifiedlead, opportunity, customer, evangelist, other |
| `hs_lead_status` | enum | Lead status (New, Open, In Progress, etc.) |
| `createdate` | datetime | Record creation date |
| `lastmodifieddate` | datetime | Last update timestamp |

## Required Fields
- `email` OR (`firstname` + `lastname`)

## Relationships
- **Company**: `associatedcompanyid` links to `/crm/hubspot/companies.md`
- **Deals**: Contact can be associated with multiple deals
- **Activities**: Emails, calls, meetings logged against contact

## MCP Integration

### Create Contact
```python
mcp_Hubspot_create_contact({
    "email": "jane@example.com",
    "firstname": "Jane",
    "lastname": "Doe",
    "jobtitle": "VP Sales",
    "company": "Acme Corp"
})
```

### Search Contacts
```python
mcp_Hubspot_search_contacts({
    "query": "jane@example.com",
    "properties": ["email", "firstname", "lastname", "jobtitle", "company"]
})
```

### Get Contact by ID
```python
mcp_Hubspot_get_contact({
    "contact_id": "12345",
    "properties": ["email", "firstname", "lastname", "lifecyclestage"]
})
```

### Update Contact
```python
mcp_Hubspot_update_contact({
    "contact_id": "12345",
    "properties": {
        "lifecyclestage": "salesqualifiedlead",
        "hs_lead_status": "In Progress"
    }
})
```

## Example Queries

### Find all contacts from a company domain
```python
contacts = mcp_Hubspot_search_contacts({
    "filterGroups": [{
        "filters": [{
            "propertyName": "email",
            "operator": "CONTAINS_TOKEN",
            "value": "@acme.com"
        }]
    }]
})
```

### Get recently created contacts
```python
contacts = mcp_Hubspot_search_contacts({
    "filterGroups": [{
        "filters": [{
            "propertyName": "createdate",
            "operator": "GTE",
            "value": "2024-01-01"
        }]
    }],
    "sorts": [{"propertyName": "createdate", "direction": "DESCENDING"}]
})
```

## Common Workflows

1. **Lead Capture**: Create contact from form submission or enrichment
2. **Lead Scoring**: Update `lifecyclestage` based on engagement
3. **Lead Routing**: Assign owner based on territory or round-robin
4. **Deduplication**: Merge duplicate contacts by email domain
