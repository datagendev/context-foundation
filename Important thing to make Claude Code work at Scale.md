---
title: "Claude Code: From Assistant to Agent Platform"
description: Architecture guide for scaling Claude Code through layered infrastructure with Commands, Agents, Skills, Scripts, and DataGen SDK
category: research
tags:
  - claude-code
  - architecture
  - agents
  - automation
  - datagen-sdk
  - mcp
created: 2026-01-05
updated: 2026-01-05
status: active
priority: high
based_on:
  - "[[datan-python-sdk]]"
reference:
  - https://www.producttalk.org/give-claude-code-a-memory/?srsltid=AfmBOopKsidPFkLxjhvuTnrXRqj6cFbHwHycxiC5glYxB6WiYBbHkaoK
---

# Claude Code: From Assistant to Agent Platform

## Paradigm Shift

**Traditional usage**: Claude Code → Software
_Claude Code assists you in building software (Claude is the helper)_

**Agent platform**: Software → Claude Code agent
_You build software infrastructure to serve Claude Code agents (Software becomes the foundation for agents)_

This is the fundamental shift: from using Claude to build software for humans, to building software that empowers Claude agents to work autonomously at scale.

## Architecture Schematic

### Component Flow

```mermaid
flowchart TB
    User[User] -->|Invokes| Command[Command<br/>Prompt template + arguments]
    Command -->|Calls| Agent[Agent<br/>Sub-process with async/parallel control]
    Agent -->|Uses| Skill[Skill<br/>Script + prompt.md]
    Skill -->|Executes| Script[Composable<br/>Scripts]

    Script -->|Uses| SDK[DataGen SDK<br/>MCP as Code wrapper]
    Script -->|CRUD operations| DB[(Database<br/>Data at scale)]

    SDK -->|Wraps| MCP[MCP Tools<br/>Communication layer]
    MCP -->|Connects to| External[External Services<br/>LinkedIn, CRMs, etc.]

    subgraph Context["Context Layer"]
        FileStruct[File Structure<br/>Hierarchical + README]
        Memory[Memory<br/>CLAUDE.md files]
        Git[Version Control<br/>Git + GitHub]
    end

    subgraph Tools["Foundation"]
        SDK
        MCP
        DB
        External
    end

    Agent -.->|Requires| Context

    style Command fill:#e1f5ff
    style Agent fill:#fff3e0
    style Skill fill:#f3e5f5
    style Script fill:#e8f5e9
    style SDK fill:#e8eaf6
    style MCP fill:#fff9c4
    style DB fill:#ffebee
    style External fill:#fce4ec
```

### Simplified View

```mermaid
graph LR
    A[Command] --> B[Agent]
    B --> C[Skill]
    C --> D[Script]
    D --> E[DataGen SDK]
    D --> F[Database]
    E --> G[MCP Tools]
    G --> H[External Services]

    style A fill:#e1f5ff
    style B fill:#fff3e0
    style C fill:#f3e5f5
    style D fill:#e8f5e9
    style E fill:#e8eaf6
    style F fill:#ffebee
    style G fill:#fff9c4
    style H fill:#fce4ec
```

## Core Components

### Context Layer (Required for effective agents)
1. **File Structure**: Create a good separated, hierarchical file structure. Each folder should have a readme.md if possible
2. **Memory**: `~/.claude/CLAUDE.md`, `~/project/CLAUDE.md`, use "#" to add more, and have a good `/handoff` command for inter-session memory
3. **Version Control**: Sync across session, client using Git, GitHub, GitHub CLI

### Execution Layer
4. **Command**: Prompt template with arguments (e.g., `/commit`, `/enrich-leads`)
5. **Agents**: Sub-process with async/parallel control
6. **Skills**: Script + prompt.md combination
7. **Scripts**: The script should be composable. not the whole integrated workflow. Build good IO between scripts so it can be easily chained. 

### Foundation Layer (Tools for scale)
8. **DataGen SDK** \*: Python SDK that wraps MCP tools so they can be used as code (not just AI tools)
9. **MCP Tools**: Communication protocols for external services (LinkedIn, CRMs, etc.)
10. **Database**: Data at scale (PostgreSQL, Supabase, etc.)

## Quality of Life Improvements

1. **IDE not terminal**: Cursor/Windsurf for better developer experience
2. **Obsidian**: Markdown editing with graph visualization and backlinks
3. **MCP Gateway**: Manage MCPs at scale
4. **Useful commands**: `/compact`, `/clear`, `/askUserQuestion`

## Data Flow Example

```
User → /enrich-leads campaign.csv
  ↓
Command (parsed with arguments)
  ↓
Agent (spawned with parallel control)
  ↓
Skills (CSV parser + enrichment + CRM sync)
  ↓
Scripts (Python execution)
  ↓
DataGen SDK wraps MCP tools as Python functions
  ↓
MCP Tools → External Services (LinkedIn, CRMs)
  ↓
Results saved to Database + local files (bypass token limits)
  ↓
Results returned to User
```

###  \*Why DataGen SDK?
MCP tools have token limits when used as AI tools. DataGen SDK wraps MCPs so you can:
- ✅ Call MCPs as Python functions: `client.execute_tool("get_linkedin_posts", {...})`
- ✅ Save large outputs locally to bypass token limits
- ✅ Process data with scripts before feeding to AI
- ✅ One credential manager for all tools (like 1Password)
- ✅ Safer than env vars - AI can only access tools you grant, not raw credentials 

### Code Example
```python
from datagen_sdk import DatagenClient

client = DatagenClient()

# Use MCP as code instead of AI tool
posts = client.execute_tool(
    "get_linkedin_person_posts",
    {"linkedin_url": lead.linkedin_url}
)

# Save locally to bypass token limits
with open("./posts.json", "w") as f:
    json.dump(posts, f, indent=2)

# Claude Code can now read saved files at its own pace
``` 