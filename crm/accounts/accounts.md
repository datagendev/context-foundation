# Salesforce Accounts

Organizations and companies in your CRM - the businesses you're targeting.

## Schema

| Field | Type | Description |
|-------|------|-------------|
| `Id` | string | Unique Salesforce account ID |
| `Name` | string | Account name (required) |
| `Website` | url | Company website |
| `Industry` | picklist | Industry classification |
| `Type` | picklist | Prospect, Customer, Partner, etc. |
| `NumberOfEmployees` | number | Employee count |
| `AnnualRevenue` | currency | Annual revenue |
| `Phone` | string | Main phone number |
| `BillingAddress` | address | Billing address |
| `ShippingAddress` | address | Shipping address |
| `OwnerId` | string | Account owner |
| `ParentId` | string | Parent account (for hierarchies) |
| `Description` | textarea | Account description |
| `Rating` | picklist | Hot, Warm, Cold |
| `CreatedDate` | datetime | Record creation date |
| `LastModifiedDate` | datetime | Last update timestamp |

## Required Fields
- `Name`

## Relationships
- **Contacts**: Multiple contacts belong to one account
- **Opportunities**: Multiple opportunities linked to account
- **Cases**: Support cases associated with account
- **Parent Account**: Hierarchical account relationships
- **Child Accounts**: Subsidiary accounts

## MCP Integration

### Create Account
```python
mcp_Salesforce_create_record({
    "sobject": "Account",
    "data": {
        "Name": "Acme Corporation",
        "Website": "https://acme.com",
        "Industry": "Technology",
        "NumberOfEmployees": 500,
        "AnnualRevenue": 50000000,
        "Type": "Prospect"
    }
})
```

### Query Accounts (SOQL)
```python
mcp_Salesforce_query({
    "query": """
        SELECT Id, Name, Website, Industry, NumberOfEmployees, AnnualRevenue
        FROM Account
        WHERE Website LIKE '%acme.com%'
    """
})
```

### Get Account by ID
```python
mcp_Salesforce_get_record({
    "sobject": "Account",
    "record_id": "001XXXXXXXXXXXX",
    "fields": ["Id", "Name", "Website", "Industry", "Type", "OwnerId"]
})
```

### Update Account
```python
mcp_Salesforce_update_record({
    "sobject": "Account",
    "record_id": "001XXXXXXXXXXXX",
    "data": {
        "Type": "Customer",
        "Rating": "Hot"
    }
})
```

## Example Queries

### Find accounts by industry
```python
accounts = mcp_Salesforce_query({
    "query": """
        SELECT Id, Name, Website, NumberOfEmployees, AnnualRevenue
        FROM Account
        WHERE Industry = 'Technology'
        ORDER BY AnnualRevenue DESC
    """
})
```

### Find accounts by employee count range
```python
accounts = mcp_Salesforce_query({
    "query": """
        SELECT Id, Name, Website, NumberOfEmployees
        FROM Account
        WHERE NumberOfEmployees >= 100 AND NumberOfEmployees <= 1000
    """
})
```

### Find accounts without opportunities
```python
accounts = mcp_Salesforce_query({
    "query": """
        SELECT Id, Name, Website
        FROM Account
        WHERE Id NOT IN (SELECT AccountId FROM Opportunity)
    """
})
```

### Find accounts with open opportunities
```python
accounts = mcp_Salesforce_query({
    "query": """
        SELECT Id, Name,
               (SELECT Id, Name, Amount, StageName FROM Opportunities WHERE IsClosed = false)
        FROM Account
        WHERE Id IN (SELECT AccountId FROM Opportunity WHERE IsClosed = false)
    """
})
```

### Get account hierarchy
```python
accounts = mcp_Salesforce_query({
    "query": """
        SELECT Id, Name, ParentId, Parent.Name
        FROM Account
        WHERE ParentId != null
    """
})
```

## Common Workflows

1. **Account Enrichment**: Enrich with firmographic data (employees, revenue, tech stack)
2. **Account Scoring**: Score based on ICP fit criteria
3. **Territory Assignment**: Assign accounts to sales reps by region/industry
4. **Account Hierarchy**: Build parent-child relationships for enterprise accounts
5. **Duplicate Detection**: Find and merge duplicate accounts by domain/name
6. **Account Health**: Track engagement and activity across account
