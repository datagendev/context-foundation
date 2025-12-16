# Salesforce Opportunities

Sales deals and pipeline tracking - revenue you're working to close.

## Schema

| Field | Type | Description |
|-------|------|-------------|
| `Id` | string | Unique Salesforce opportunity ID |
| `Name` | string | Opportunity name (required) |
| `AccountId` | string | Associated account (required) |
| `Amount` | currency | Deal value |
| `StageName` | picklist | Pipeline stage (required) |
| `Probability` | percent | Win probability |
| `CloseDate` | date | Expected close date (required) |
| `Type` | picklist | New Business, Existing Business |
| `LeadSource` | picklist | Where opportunity originated |
| `OwnerId` | string | Opportunity owner |
| `Description` | textarea | Deal notes |
| `NextStep` | string | Next action item |
| `IsClosed` | boolean | Is deal closed |
| `IsWon` | boolean | Is deal won |
| `ForecastCategory` | picklist | Omitted, Pipeline, Best Case, Commit, Closed |
| `CreatedDate` | datetime | Record creation date |
| `LastModifiedDate` | datetime | Last update timestamp |

## Required Fields
- `Name`
- `StageName`
- `CloseDate`
- `AccountId`

## Default Stages
| Stage | Probability | Forecast Category |
|-------|-------------|-------------------|
| Prospecting | 10% | Pipeline |
| Qualification | 20% | Pipeline |
| Needs Analysis | 30% | Pipeline |
| Value Proposition | 50% | Pipeline |
| Proposal/Quote | 60% | Best Case |
| Negotiation | 80% | Commit |
| Closed Won | 100% | Closed |
| Closed Lost | 0% | Omitted |

## Relationships
- **Account**: `AccountId` links to `/crm/salesforce/accounts.md`
- **Contact Roles**: Contacts involved in the opportunity
- **Products**: Line items via OpportunityLineItem
- **Activities**: Tasks, Events, Emails related to opportunity
- **Quotes**: Associated quote documents

## MCP Integration

### Create Opportunity
```python
mcp_Salesforce_create_record({
    "sobject": "Opportunity",
    "data": {
        "Name": "Acme Corp - Enterprise License",
        "AccountId": "001XXXXXXXXXXXX",
        "Amount": 50000,
        "StageName": "Qualification",
        "CloseDate": "2024-06-30",
        "Type": "New Business"
    }
})
```

### Query Opportunities (SOQL)
```python
mcp_Salesforce_query({
    "query": """
        SELECT Id, Name, Amount, StageName, CloseDate, Account.Name
        FROM Opportunity
        WHERE StageName NOT IN ('Closed Won', 'Closed Lost')
        ORDER BY CloseDate
    """
})
```

### Get Opportunity by ID
```python
mcp_Salesforce_get_record({
    "sobject": "Opportunity",
    "record_id": "006XXXXXXXXXXXX",
    "fields": ["Id", "Name", "Amount", "StageName", "CloseDate", "AccountId", "OwnerId"]
})
```

### Update Opportunity Stage
```python
mcp_Salesforce_update_record({
    "sobject": "Opportunity",
    "record_id": "006XXXXXXXXXXXX",
    "data": {
        "StageName": "Proposal/Quote",
        "Amount": 75000,
        "NextStep": "Schedule contract review"
    }
})
```

## Example Queries

### Get pipeline by stage
```python
opps = mcp_Salesforce_query({
    "query": """
        SELECT StageName, COUNT(Id) oppCount, SUM(Amount) totalAmount
        FROM Opportunity
        WHERE IsClosed = false
        GROUP BY StageName
    """
})
```

### Get opportunities closing this quarter
```python
opps = mcp_Salesforce_query({
    "query": """
        SELECT Id, Name, Amount, StageName, CloseDate, Account.Name, Owner.Name
        FROM Opportunity
        WHERE CloseDate = THIS_QUARTER
        AND IsClosed = false
        ORDER BY Amount DESC
    """
})
```

### Get stale opportunities
```python
opps = mcp_Salesforce_query({
    "query": """
        SELECT Id, Name, Amount, StageName, LastModifiedDate
        FROM Opportunity
        WHERE IsClosed = false
        AND LastModifiedDate < LAST_N_DAYS:30
    """
})
```

### Get opportunities with contact roles
```python
opps = mcp_Salesforce_query({
    "query": """
        SELECT Id, Name, Amount,
               (SELECT ContactId, Contact.Name, Role, IsPrimary
                FROM OpportunityContactRoles)
        FROM Opportunity
        WHERE Id = '006XXXXXXXXXXXX'
    """
})
```

### Calculate weighted pipeline
```python
opps = mcp_Salesforce_query({
    "query": """
        SELECT StageName, Probability, SUM(Amount) totalAmount
        FROM Opportunity
        WHERE IsClosed = false
        GROUP BY StageName, Probability
    """
})
# Weighted value = SUM(Amount * Probability)
```

## Common Workflows

1. **Opportunity Creation**: Create from qualified lead or account
2. **Stage Progression**: Move through pipeline stages
3. **Contact Roles**: Add decision makers and influencers
4. **Forecasting**: Calculate weighted pipeline by stage
5. **Close Date Management**: Track and adjust close dates
6. **Win/Loss Analysis**: Track closed opportunities for reporting
7. **Pipeline Alerts**: Notify on stale deals or slipping dates
