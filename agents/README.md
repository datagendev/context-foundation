# Agents

Specialized AI agents for specific GTM workflows. Each agent has focused context and skills.

## Agent Types

### Content Agents
- **content-creator** - Multi-step content production (topic → outline → draft → polish)
- **newsletter-generator** - Weekly briefing to public newsletter
- **social-writer** - Platform-specific social content

### Sales Agents
- **prospect-researcher** - Deep research on target accounts/contacts
- **email-drafter** - Personalized outreach based on research
- **objection-handler** - Suggested responses to common objections

### Operations Agents
- **transcript-processor** - Extract insights from call transcripts
- **crm-updater** - Push extracted data to CRM
- **data-enricher** - Enrich records with external data

## Agent Architecture

Each agent should have:

```
agents/
├── [agent-name]/
│   ├── README.md          # What this agent does
│   ├── instructions.md    # System prompt / behavior
│   ├── skills.md          # Skills this agent can call
│   └── examples/          # Few-shot examples
```

## Agent Template

```markdown
# [Agent Name]

## Purpose
[What this agent does and when to use it]

## Trigger
[How to invoke - e.g., "research prospect [company]"]

## Inputs
- [Input 1]: [Description]
- [Input 2]: [Description]

## Outputs
- [Output 1]: [Description]
- [Output 2]: [Description]

## Context Files Used
- /icp/personas.md
- /synthesis/pain-points.md
- [etc.]

## Workflow Steps
1. [Step 1]
2. [Step 2]
3. [Step 3]

## Example

**Input**: "research prospect Acme Corp"

**Output**:
[Example output]
```

## Skills vs Agents

**Skills**: Single-purpose capabilities (e.g., "write in brand voice")
**Agents**: Multi-step workflows that may use multiple skills

## Best Practices

1. **Keep agents focused** - One job per agent
2. **Use progressive context** - Load only what's needed per step
3. **Human checkpoints** - Add approval steps for important decisions
4. **Store outputs** - Save results to appropriate folders
5. **Learn from feedback** - Add corrections to training data
