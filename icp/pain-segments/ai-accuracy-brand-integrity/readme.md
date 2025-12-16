# Pain Segment: AI is saying the wrong thing about us (accuracy + brand integrity)

## What this pain is
AI assistants (ChatGPT/Perplexity/Claude/Gemini/Copilot/etc.) are becoming a “source of truth” in buying, support, and executive decision-making. This segment is about **AI outputs that are confidently wrong** about the company—capabilities, compliance, pricing, positioning, or policies—creating brand and revenue risk.

## Who feels it (common owners)
- Brand/Comms, PR
- Product Marketing (PMM)
- Head of SEO / Content
- Customer Support / CS leadership (as an escalation path)
- Web/Platform (to implement technical/content fixes)

## Targeting (who to prioritize)

These targeting cues reflect how Scrunch positions itself in content (see `icp/personas.md` → “Content-Derived Targeting Hypotheses”).

### Best-fit company profiles
- **Enterprise / security-conscious orgs** where brand and factual accuracy are high-stakes (pricing, compliance, policies, capabilities).
- **Regulated or trust-heavy categories** (fintech, healthcare, education, infra/devtools, marketplaces) where “SOC2/HIPAA/ISO/GDPR” claims materially impact deals.
- **High-volume buyer research environments** where prospects rely on AI summaries during evaluation (large inbound, many concurrent deals, lots of comparisons).

### Best-fit “truth surfaces” (where errors hurt most)
- Security/trust center, compliance pages, subprocessors, privacy/terms
- Pricing/plans pages and packaging/positioning pages
- Product docs/API/integrations pages that buyers use to validate capabilities

### Strong “why now” indicators (prioritization)
- Recent changes to pricing/positioning/security claims (AI keeps repeating the old story).
- Multiple internal teams escalating AI screenshots (Sales, Support, Exec, Comms).
- Third-party sites outrank first-party pages for brand-fact queries (pricing/compliance/integrations), increasing the chance AI cites stale/incorrect sources.

### Deprioritize / weak fit
- They want “prompt hacks” without owning content/site changes.
- No clear owner across Comms/PMM/SEO/Web to implement fixes and validate results.

## Trigger moments (what creates urgency)
- Sales/CS escalates a screenshot or transcript of a wrong answer (“We need to fix this.”)
- A deal is stalled or lost because a buyer trusts an incorrect AI summary
- A comms/compliance incident where AI misinformation amplifies reputational or regulatory risk

## Signals (more accurate / higher-fidelity)

For programmatic, at-scale signals (web + databases), see: `signals/readme.md`.

### High-confidence (direct evidence)
- A call transcript / email / ticket contains: “ChatGPT/Claude/Perplexity said…” followed by a specific incorrect claim.
- CRM `Closed Lost` notes explicitly cite an AI answer, screenshot, or “AI recommended competitor.”
- An internal escalation thread includes model name + prompt + screenshot + link to the cited source.

### Strong (repeatable patterns)
- Support tickets trend up for topics that align with common hallucinations (pricing, security/compliance, integrations, “do you support X”).
- New content/positioning shipped, but AI outputs still reflect the old narrative after 2–6+ weeks.
- AI answers cite stale or non-canonical sources (old pricing pages, outdated docs, old press, third-party summaries).

### Weak (needs validation)
- General leadership anxiety: “Are we showing up in AI?” with no concrete wrong output.
- Anecdotes without prompt or model details (“someone saw something in ChatGPT”).

### Anti-signals (deprioritize)
- They only want “prompt hacks” and won’t own content/site changes.
- No owner for response + remediation (comms/PMM/SEO/web all “not us”).

## Where to detect it (data sources)
- CRM: `Closed Lost Reason`, deal notes, competitor fields, call summaries
- Call transcripts: Gong/Chorus/Zoom notes for “ChatGPT said”, “Perplexity”, “Claude”, “AI summary”
- Support: Zendesk/Intercom tags + full-text search for AI references
- Internal comms: Slack search queries for “chatgpt”, “perplexity”, “claude said”, “AI said”
- Web: top-cited pages for wrong claims; pages that are stale, non-canonical, or duplicate

## Qualification questions (fast)
- “What’s the most damaging wrong AI answer you’ve seen? Who escalated it, and do you have the prompt/screenshot?”
- “Which 3 claims must be correct in AI answers (security, pricing, integrations, policies)?”
- “When did you last update positioning/pricing/docs, and what pages are canonical?”

## What success looks like (early)
- A prioritized list of inaccurate themes + the sources causing them (by model/topic)
- A short remediation plan (content + technical) tied to measurable improvements in citations/accuracy on priority prompts
