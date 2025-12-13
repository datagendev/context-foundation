# Call Transcripts

Raw voice of customer - call recordings and transcripts from sales, CS, and discovery calls.

## Structure

Each transcript file should include:
- **Raw transcript** from the call
- **Auto-extracted metadata**:
  - Pain points mentioned
  - Objections raised
  - Tool stack discussed
  - MEDDPIC fields (Metrics, Economic Buyer, Decision Criteria, Decision Process, Identify Pain, Champion)
  - Next steps agreed

## Naming Convention

```
YYYY-MM-DD_company-name_call-type.md
```

Example: `2024-03-15_acme-corp_discovery.md`

## Template

```markdown
# Call: [Company Name] - [Call Type]

## Metadata
- **Date**: YYYY-MM-DD
- **Attendees**: [Names and titles]
- **Call Type**: Discovery / Demo / Follow-up / Closing
- **Duration**: XX minutes
- **Recording**: [Link if available]

## Extracted Intelligence

### Pain Points
- [Pain point 1]
- [Pain point 2]

### Objections
- [Objection 1]
- [Objection 2]

### Tool Stack Mentioned
- [Tool 1]
- [Tool 2]

### MEDDPIC
- **Metrics**: [What success looks like]
- **Economic Buyer**: [Who controls budget]
- **Decision Criteria**: [How they'll decide]
- **Decision Process**: [Steps to close]
- **Identify Pain**: [Core problem]
- **Champion**: [Internal advocate]

### Next Steps
- [ ] [Action item 1]
- [ ] [Action item 2]

## Raw Transcript

[Full transcript here]
```

## Workflow

1. **Ingest**: Drop transcript from Gong/Chorus/manual notes
2. **Extract**: AI extracts pain points, objections, MEDDPIC
3. **Synthesize**: Roll up to `/synthesis/` docs
4. **Push to CRM**: Update contact/deal records with extracted data
