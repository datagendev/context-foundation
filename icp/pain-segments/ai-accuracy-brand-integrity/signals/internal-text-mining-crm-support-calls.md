# Signal: Internal artifacts that mention AI answers (highest precision)

## What it indicates
Direct evidence that buyers/users are citing AI answers—and that those answers are wrong or risky.
This is the highest-precision signal for Pain Segment 1.

## Data sources (typical)
- CRM fields: `Closed Lost Reason`, deal notes, call summaries, competitor notes
- Call transcripts: Gong/Chorus/Zoom/Meet notes
- Support: Zendesk/Intercom tickets and tags
- Internal comms: Slack exports or searchable message history

## How to detect (programmatic)

### 1) Keyword + proximity queries
Search for AI mentions near high-stakes claim types:
- AI keywords: `chatgpt`, `gpt`, `perplexity`, `claude`, `gemini`, `copilot`, `ai said`
- Claim keywords: `pricing`, `SOC2`, `SOC 2`, `ISO`, `HIPAA`, `GDPR`, `DPA`, `subprocessor`, `integration`, `policy`

### 2) Classify the mention
Label each hit as:
- `wrong_claim` (explicitly wrong)
- `buyer_cited_ai` (buyer referenced AI, correctness unclear)
- `internal_check` (team is proactively checking AI answers)

### 3) Extract the artifact (for follow-up)
If present, store:
- model name
- prompt text
- screenshot/transcript link
- the claim being contested (pricing/compliance/etc.)

## Output fields (recommended)
- `ai_mentions_count_90d` (int)
- `ai_wrong_claim_mentions_90d` (int)
- `ai_mentions_claim_types` (string[])
- `ai_artifacts_present` (bool)

## Caveats / false positives
- Mentions like “we should try ChatGPT for copy” are not relevant—filter for claim types and buyer/user context.

