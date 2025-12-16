# HubSpot Deals

Sales opportunities and pipeline tracking - revenue you're working to close.

## Schema

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Unique HubSpot deal ID |
| `dealname` | string | Deal/opportunity name |
| `amount` | number | Deal value (USD) |
| `dealstage` | enum | Pipeline stage ID |
| `pipeline` | string | Pipeline ID |
| `closedate` | date | Expected close date |
| `hs_deal_stage_probability` | number | Win probability (0-1) |
| `hubspot_owner_id` | string | Assigned sales rep |
| `dealtype` | enum | newbusiness, existingbusiness |
| `hs_priority` | enum | low, medium, high |
| `description` | string | Deal notes/description |
| `createdate` | datetime | Record creation date |
| `hs_lastmodifieddate` | datetime | Last update timestamp |

## Required Fields
- `dealname`
- `pipeline` (defaults to default pipeline)
- `dealstage`

## Default Pipeline Stages
| Stage | Probability | Description |
|-------|-------------|-------------|
| appointmentscheduled | 20% | Discovery call scheduled |
| qualifiedtobuy | 40% | Budget, authority, need confirmed |
| presentationscheduled | 60% | Demo/presentation scheduled |
| decisionmakerboughtin | 80% | Decision maker engaged |
| contractsent | 90% | Proposal/contract sent |
| closedwon | 100% | Deal won |
| closedlost | 0% | Deal lost |

## Relationships
- **Company**: Deal associated with one company
- **Contacts**: Deal can have multiple associated contacts
- **Line Items**: Products/services included in deal
- **Activities**: Calls, emails, meetings related to deal

## MCP Integration

### Create Deal
```python
mcp_Hubspot_create_deal({
    "dealname": "Acme Corp - Enterprise License",
    "amount": 50000,
    "dealstage": "appointmentscheduled",
    "closedate": "2024-06-30",
    "pipeline": "default"
})
```

### Search Deals
```python
mcp_Hubspot_search_deals({
    "query": "Acme",
    "properties": ["dealname", "amount", "dealstage", "closedate"]
})
```

### Get Deal by ID
```python
mcp_Hubspot_get_deal({
    "deal_id": "12345",
    "properties": ["dealname", "amount", "dealstage", "closedate", "hubspot_owner_id"]
})
```

### Update Deal Stage
```python
mcp_Hubspot_update_deal({
    "deal_id": "12345",
    "properties": {
        "dealstage": "qualifiedtobuy",
        "amount": 75000
    }
})
```

### Associate Deal with Company
```python
mcp_Hubspot_associate_deal({
    "deal_id": "12345",
    "company_id": "67890"
})
```

## Example Queries

### Get pipeline by stage
```python
deals = mcp_Hubspot_search_deals({
    "filterGroups": [{
        "filters": [{
            "propertyName": "dealstage",
            "operator": "EQ",
            "value": "presentationscheduled"
        }]
    }],
    "properties": ["dealname", "amount", "closedate", "hubspot_owner_id"]
})
```

### Get deals closing this month
```python
deals = mcp_Hubspot_search_deals({
    "filterGroups": [{
        "filters": [
            {"propertyName": "closedate", "operator": "GTE", "value": "2024-03-01"},
            {"propertyName": "closedate", "operator": "LTE", "value": "2024-03-31"},
            {"propertyName": "dealstage", "operator": "NOT_IN", "value": ["closedwon", "closedlost"]}
        ]
    }],
    "sorts": [{"propertyName": "amount", "direction": "DESCENDING"}]
})
```

### Calculate pipeline value by stage
```python
deals = mcp_Hubspot_search_deals({
    "filterGroups": [{
        "filters": [{
            "propertyName": "dealstage",
            "operator": "NOT_IN",
            "value": ["closedwon", "closedlost"]
        }]
    }],
    "properties": ["dealstage", "amount"]
})
# Group and sum by stage
```

## Common Workflows

1. **Deal Creation**: Create deal from qualified lead
2. **Stage Progression**: Move deal through pipeline stages
3. **Forecasting**: Calculate weighted pipeline value
4. **Deal Alerts**: Notify on stale deals or approaching close dates
5. **Win/Loss Analysis**: Track closed deals for reporting
