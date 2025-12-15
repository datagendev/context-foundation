# Transcript Summarization Guideline (Company-Aware)

Use this guideline to turn a raw call transcript into a high-signal, CRM-ready summary that also updates your shared context (synthesis docs).

## Inputs (what to read first)

1. **Raw transcript**
   - Fireflies raw download: `/crm/transcripts/<transcript_id>.md`
   - Or curated transcript: `/crm/transcripts/YYYY-MM-DD_company-name_call-type.md`
2. **CRM account context (preferred; not implemented yet)**
   - When available, pull from CRM: account/company record, contacts, open opportunity, stage history, notes, next step, and last touch.
   - Until CRM context is wired up, use `@company` context + prior transcripts as a proxy.
3. **@company context (required)**
   - Treat `@company` as the company folder: `/company/<company-domain>/`
   - Start with `/company/<company-domain>/README.md`
   - If present, use competitive context: `/company/<company-domain>/competitive-intelligence/profile.md`
   - If present, use scraped pages / research: `/company/<company-domain>/pages/`, `/company/<company-domain>/research/`, `/company/<company-domain>/site-map/`
4. **Existing canonical context (optional but recommended)**
   - `/synthesis/pain-points.md`, `/synthesis/objections.md`, `/synthesis/tool-stacks.md`
   - Prior call notes for this account (search in `/crm/transcripts/`)

## Output (where to write)

- **Curated call note (recommended):** `/crm/transcripts/YYYY-MM-DD_company-name_call-type.md`
  - Include a link back to the raw file (`/crm/transcripts/<transcript_id>.md`) if available.
- Keep the raw Fireflies artifact as-is (ID-based) for traceability and re-processing.

## Summary principles

- **Lead with decisions and change:** what’s now true after this call (commitments, timelines, next steps).
- **Be specific:** include numbers, systems, names, dates, and constraints; avoid generic “they want automation”.
- **Separate facts vs inference:** label assumptions explicitly.
- **Tie to @company context:** highlight anything that contradicts or updates what you already believe about the account.
- **Make it actionable:** every summary should enable a follow-up email + CRM update without re-listening.
- **Handle sensitive data:** do not copy secrets, credentials, or unnecessary PII into summaries.

## Privacy & redaction

- Prefer roles over personal details (e.g., “Security lead” vs personal notes).
- If the transcript contains sensitive values (API keys, passwords, tokens), replace with `[REDACTED]`.
- If you must reference PII, keep it minimal and strictly relevant to next steps.

## Required sections (copy-paste template)

```markdown
# Call: @company - [Call Type]

## Metadata
- **Date**: YYYY-MM-DD
- **Company**: @company (domain: <company-domain>)
- **Transcript Source**: Fireflies
- **Transcript ID**: <id>
- **Attendees**: [name — role] (confirm spellings)
- **Call Type**: Discovery / Demo / Follow-up / Closing / Other
- **Stage**: [Lead / Qualified / Eval / Security / Procurement / Closed Won/Lost]
- **Recording/Transcript Link**: [Fireflies URL if present]

## TL;DR
- **Why now**: [trigger event]
- **Top 3 takeaways**:
  1. ...
  2. ...
  3. ...
- **Decision(s)**: [what was decided, by whom]
- **Next step**: [single most important next action + date]

## Understand who we are
- **One-liner**: [what we do in 1 sentence, in their language]
- **What we’re not**: [explicit non-goals to prevent scope creep]
- **Where we fit**: [where we plug into their stack/workflow]
- **Proof points**: [1-3 relevant examples, metrics, or references]
- **What we want from them**: [the ask: access, intro, data, pilot, decision]

## Account Context (from CRM + @company)
- **CRM snapshot**: [stage, last touch, owners, existing notes — if available]
- **What we thought before the call**: [1-3 bullets based on `/company/<domain>/...` and prior transcripts]
- **What changed after the call**: [new facts, corrected assumptions]
- **Competing alternatives mentioned**: [tools/vendors + where they fit]

## Customer Situation
- **Current workflow**: [today’s process, step-by-step]
- **Stakeholders & roles**:
  - [Role] — [Name] — [priority / concerns]
- **Tool stack**: [systems mentioned; include vendor + module if possible]
- **Constraints**: [security, privacy, legal, budget, timeline, IT ownership]

## Pain Points (verbatim when possible)
- [Pain] — **impact**: [time/$/risk] — **evidence**: ["short quote" or paraphrase]
- ...

## Desired Outcomes / Success Criteria
- **Must-have outcomes**: [...]
- **Nice-to-have outcomes**: [...]
- **How they will measure success**: [metrics + baseline if stated]

## Requirements
- **Functional**: [...]
- **Integrations**: [...]
- **Data**: [sources, PII, retention, access controls]
- **Non-functional**: [latency, reliability, governance, audit logs]

## Objections / Risks
- [Objection] — **root cause**: [...] — **response to test**: [...]
- **Deal risks**: [champion, budget, timeline, urgency, internal politics]

## MEDDPIC (if sales motion)
- **Metrics**: [...]
- **Economic Buyer**: [...]
- **Decision Criteria**: [...]
- **Decision Process**: [...]
- **Paper Process**: [...]
- **Identify Pain**: [...]
- **Champion**: [...]

## Action Items (owner + due date)
- [ ] **Us**: ... (Owner: , Due: YYYY-MM-DD)
- [ ] **Them**: ... (Owner: , Due: YYYY-MM-DD)

## Follow-up Assets
### Follow-up email draft (3–8 sentences)
[Write the email.]

### CRM updates (copy/paste)
- Account: ...
- Contacts: [who to create/update]
- Opportunity: [stage, next step, close date guess, amount if stated]
- Notes: [paste-ready bullets]

## Source
- Raw transcript: `/crm/transcripts/<transcript_id>.md`
```

## What to extract from the transcript (high-signal checklist)

- **Dates & deadlines**: pilot start, procurement dates, renewal windows, events.
- **Numbers**: volume (calls/emails/tickets), headcount, budget bands, time saved, error rates.
- **System boundaries**: where data lives, who owns it, what cannot change.
- **Buying dynamics**: who cares, who blocks, what proof is required.
- **Competitive mentions**: “we tried X”, “we’re replacing Y”, “we compare you to Z”.
- **Exact language**: 3–5 short quotes that capture pains/criteria (useful for messaging).

## Updating shared context (synthesis)

After writing the curated call note, add/refresh entries in:
- `/synthesis/pain-points.md` (new pain points + evidence)
- `/synthesis/objections.md` (new objections + effective responses)
- `/synthesis/tool-stacks.md` (new tools/integrations mentioned)
- `/synthesis/feature-requests.md` (explicit asks and why they matter)

When adding to synthesis docs, always include a source link to the curated call note (or transcript ID file).
