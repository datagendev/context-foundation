# Signal: AI crawler controls in `robots.txt`

## What it indicates
They’re aware of AI crawling and are actively managing it.
This is usually an **awareness / governance** signal, not direct evidence of wrong answers.

## How to detect (programmatic)
- Fetch `https://{domain}/robots.txt`
- Search for AI-related user-agents and directives.

### Common patterns to match
- OpenAI: `GPTBot`, `OAI-SearchBot`, `ChatGPT-User`
- Perplexity: `PerplexityBot`, `Perplexity-User`
- Google AI controls: `Google-Extended`
- Other: `CCBot`, `anthropic` (varies), `Bytespider` (varies)

### Scoring suggestions
- **1:** any AI user-agent mentioned
- **2:** explicit allow/deny rules for sensitive sections (e.g., `/pricing`, `/security`, `/docs`)

## Output fields (recommended)
- `robots_txt_found` (bool)
- `robots_ai_user_agents` (string[])
- `robots_ai_rules_present` (bool)

## Caveats / false positives
- Robots directives vary by crawler and are not a guarantee of enforcement.
- Some AI access happens through user-initiated fetchers, browsers, or third-party retrieval layers.

