# Salesforce Contacts

Qualified people associated with accounts - individuals you've engaged with.

## Schema

| Field | Type | Description |
|-------|------|-------------|
| `Id` | string | Unique Salesforce contact ID |
| `FirstName` | string | First name |
| `LastName` | string | Last name (required) |
| `Email` | string | Email address |
| `Phone` | string | Phone number |
| `MobilePhone` | string | Mobile phone |
| `Title` | string | Job title |
| `Department` | string | Department |
| `AccountId` | string | Link to Account record |
| `OwnerId` | string | Record owner |
| `LeadSource` | picklist | Where contact originated |
| `MailingAddress` | address | Mailing address (Street, City, State, PostalCode, Country) |
| `Description` | textarea | Notes about the contact |
| `CreatedDate` | datetime | Record creation date |
| `LastModifiedDate` | datetime | Last update timestamp |

## Required Fields
- `LastName`

## Relationships
- **Account**: `AccountId` links to `/crm/salesforce/accounts.md`
- **Opportunities**: Contact can be linked to multiple opportunities via ContactRoles
- **Activities**: Tasks, Events, Emails logged against contact
- **Cases**: Support cases associated with contact

## MCP Integration

### Create Contact
```python
mcp_Salesforce_create_record({
    "sobject": "Contact",
    "data": {
        "FirstName": "Jane",
        "LastName": "Doe",
        "Email": "jane@acme.com",
        "Title": "VP Sales",
        "AccountId": "001XXXXXXXXXXXX"
    }
})
```

### Query Contacts (SOQL)
```python
mcp_Salesforce_query({
    "query": """
        SELECT Id, FirstName, LastName, Email, Title, Account.Name
        FROM Contact
        WHERE Email = 'jane@acme.com'
    """
})
```

### Get Contact by ID
```python
mcp_Salesforce_get_record({
    "sobject": "Contact",
    "record_id": "003XXXXXXXXXXXX",
    "fields": ["Id", "FirstName", "LastName", "Email", "Title", "AccountId"]
})
```

### Update Contact
```python
mcp_Salesforce_update_record({
    "sobject": "Contact",
    "record_id": "003XXXXXXXXXXXX",
    "data": {
        "Title": "Chief Revenue Officer",
        "Phone": "+1-555-123-4567"
    }
})
```

## Example Queries

### Find contacts by account
```python
contacts = mcp_Salesforce_query({
    "query": """
        SELECT Id, FirstName, LastName, Email, Title
        FROM Contact
        WHERE AccountId = '001XXXXXXXXXXXX'
        ORDER BY LastName
    """
})
```

### Find contacts by email domain
```python
contacts = mcp_Salesforce_query({
    "query": """
        SELECT Id, FirstName, LastName, Email, Title, Account.Name
        FROM Contact
        WHERE Email LIKE '%@acme.com'
    """
})
```

### Find recently created contacts
```python
contacts = mcp_Salesforce_query({
    "query": """
        SELECT Id, FirstName, LastName, Email, Title, CreatedDate
        FROM Contact
        WHERE CreatedDate = LAST_N_DAYS:30
        ORDER BY CreatedDate DESC
    """
})
```

### Find contacts without recent activity
```python
contacts = mcp_Salesforce_query({
    "query": """
        SELECT Id, FirstName, LastName, Email, LastActivityDate
        FROM Contact
        WHERE LastActivityDate < LAST_N_DAYS:90
        OR LastActivityDate = null
    """
})
```

## Common Workflows

1. **Lead Conversion**: Convert qualified Lead to Contact + Account + Opportunity
2. **Contact Enrichment**: Update contact with external data (title, phone)
3. **Contact Deduplication**: Find and merge duplicate contacts
4. **Account Association**: Link orphan contacts to accounts
5. **Contact Roles**: Add contacts to opportunity contact roles
