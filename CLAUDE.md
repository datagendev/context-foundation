# CLAUDE.md

This file provides guidance to Claude Code when working in this repository.

## Repository Overview

GTM context "starter kit" with Markdown docs and templates organized by workflow area. See `AGENTS.md` for detailed structure.

## DataGen SDK Usage Guide

### Setup

1. **Get API Key**: https://datagen.dev/account?tab=api

2. **Add MCP Server to Claude Code**:
```bash
claude mcp add --transport http datagen https://mcp.datagen.dev/mcp \
  --header "x-api-key: YOUR_API_KEY"
```

3. **Connect Services**: Go to https://datagen.dev and add integrations (Gmail, Supabase, Linear, Slack, etc.) via OAuth

### When to Use SDK vs Interactive MCP

**Use interactive MCP tools for:**
- Quick lookups, single queries, exploratory work

**Recommend SDK when:**
- Exporting 100+ rows of data
- Processing lists (send emails to 50 contacts, update 200 records)
- Any loop-based operations
- Results need to be saved to files

SDK achieves 98% token savings on batch operations.

### Basic Usage Pattern

```python
from datagen_sdk import DatagenClient

client = DatagenClient()
result = client.execute_tool("tool_name", {params})
```

### Example: Large Data Export

```python
from datagen_sdk import DatagenClient
import csv

client = DatagenClient()

# Fetch all contacts in one call
contacts = client.execute_tool("mcp_Supabase_run_sql", {
    "params": {
        "sql": "SELECT * FROM contacts WHERE status='active'",
        "projectId": "your-project-id"
    }
})

# Write to CSV locally - no token overhead per row
with open("contacts_export.csv", "w") as f:
    writer = csv.DictWriter(f, fieldnames=contacts[0].keys())
    writer.writeheader()
    writer.writerows(contacts)
```

### Key Benefits

- Credentials isolated in gateway (LLM never sees secrets)
- Exact schemas via `getToolDetails()` (no hallucinated params)
- Built-in retry logic across all services
- One pattern for Gmail, Slack, Linear, Supabase, etc.
