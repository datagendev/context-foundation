# ICP Personas (Pain-Based) — Scrunch

Scrunch helps brands monitor how they appear in AI-generated answers, understand why they rank (or don’t), and take action to improve visibility and accuracy (Monitoring → Insights → Agent Experience Platform). This ICP is derived from `company/deep-research-of-who-we-are.md` and `company/scrunch.com/pages/enterprise__881a030a15.md`.

The goal is to segment the market by **pain + trigger moments** (the “oh, AI is affecting us” moments), not by traditional firmographics.

## Known Customers (anchor accounts)

Use these as anchors for lookalikes and for validating the pains below:
- Lenovo
- Crunchbase
- BairesDev
- Skims
- BigTime
- Penn State University
- Clerk

## Content-Derived Targeting Hypotheses (Scrunch blog)

Source list: `company/scrunch.com/site-map/2025-12-14.md`. These are *hypotheses* based on how Scrunch positions the product in content; validate in calls.

| Post | Implied primary buyer/champion | Most aligned pain segment(s) | Why it’s a targeting signal |
| --- | --- | --- | --- |
| https://scrunch.com/blog/enterprise-ready | Enterprise marketing leader + security/procurement stakeholders | Pain 1, Pain 4 | Emphasizes enterprise requirements (security, governance, implementation) → upmarket intent |
| https://scrunch.com/blog/aeo-buyers-guide | SEO / PMM / Growth (with exec sponsor) | Pain 2, Pain 3 | “Buyer’s guide” framing signals category creation and evaluation-driven buying |
| https://scrunch.com/blog/agent-traffic-monitoring | Growth/Analytics + Web/Platform | Pain 3, Pain 4 | “Agent traffic” measurement + implementation implies cross-functional ownership and technical readiness |
| https://scrunch.com/news/2025-05-announcing-scrunch-ai%27s-agency-partnership-program | Agency owners + Head of SEO / Client Services | Pain 5 | Explicit agency packaging (multi-client, reporting, productized offering) |
| https://scrunch.com/blog/2025-07-how-runpod-leveraged-the-scrunch-ai-platform-to-achieve-4x-growth,-turning-chatgpt-into-a-top-performing-acquisition-channel- | Growth lead at technical B2B | Pain 3, Pain 4 | Case study tied to acquisition outcomes + site readiness fixes → “AI channel owner” persona |
| https://scrunch.com/news/2025-04-from-underdog-to-powerhouse-bairesdevs-78-ai-search-surge | Growth/SEO at B2B services | Pain 2, Pain 3 | Case study highlights competitive visibility + operational cadence → demand-gen pull |
| https://scrunch.com/blog/how-to-spot-the-bots-that-drive-revenue | Growth + Analytics/RevOps | Pain 3 | Focus on “which agents drive revenue” signals measurement/attribution buyer |
| https://scrunch.com/blog/2025-12-competitors-ai-search-citations | SEO / Competitive intelligence | Pain 2 | Competitor + citations language maps directly to “share-of-answer” buyers |

## The “AI Presence” Moments (high-signal triggers)

These are the moments when teams feel AI’s impact viscerally and will prioritize a solution:

- A customer/prospect says: “ChatGPT told me you don’t do X / you’re not SOC2 / your pricing is Y,” and it’s wrong.
- A sales rep drops a screenshot in Slack: “We lost the deal because Perplexity recommended Competitor A.”
- A PMM ships new positioning/pricing, but AI answers keep repeating the old story for weeks.
- An exec asks in a meeting: “Are we showing up in AI? Why is Competitor everywhere?”
- A support team sees tickets that start with: “Claude said…” or “I asked ChatGPT…”
- A brand/comms team sees AI hallucinations turning into reputational risk (policies, safety, compliance claims).
- A marketing team finally sees attribution signals: AI-referral traffic/conversions begin showing up, but it’s noisy and uncontrollable.

## Pain-Based Segments (prioritized)

Detailed signal checklists for the top three segments:
- Pain Segment 1 → [ai-accuracy-brand-integrity](pain-segments/ai-accuracy-brand-integrity/readme.md)
- Pain Segment 2 → [share-of-answer-loss](pain-segments/share-of-answer-loss/readme.md)
- Pain Segment 3 → [ai-channel-emergence](pain-segments/ai-channel-emergence/readme.md)

### Pain Segment 1 (Primary): “AI is saying the wrong thing about us” (accuracy + brand integrity)

**What they’re feeling**
- Loss of control over the brand narrative: incorrect capabilities, outdated pricing, wrong positioning, wrong comparisons.

**Trigger moments (when it becomes urgent)**
- Screenshot escalations from Sales/CS/Exec with a wrong AI answer
- A competitor uses AI answers as “proof” in a deal cycle
- A PR/comms incident where AI outputs amplify misinformation

**What it looks like in the wild**
- Internal artifact: a Slack screenshot or a forwarded chat transcript, escalated with “We need to fix this.”
- External artifact: a prospect/customer quoting an AI assistant as a source of truth.
- Business impact: confusion → stalled deals, churn risk, reputational risk, higher support load.

**What they ask for**
- “How do we fix what AI says about us?”
- “How do we prevent wrong answers from spreading across models?”

**Scrunch wedge**
- Monitoring to quantify where inaccuracies appear and how often
- Insights to explain *why* the model is citing the wrong sources
- AXP to ensure AI agents can reliably read/cite the right pages

**First win (what ‘good’ looks like fast)**
- Identify the top inaccurate themes and the specific pages/sources driving them
- Ship targeted fixes that measurably improve citation accuracy for priority prompts

**Common owners**
- Brand/Comms, PMM, Head of SEO/Content; plus Web/Platform for implementation

**Signals (more accurate / higher-fidelity)**
- A real artifact exists (model + prompt + screenshot/transcript) showing an incorrect claim about pricing, compliance, integrations, or policies.
- CRM `Closed Lost` or deal notes explicitly cite an AI answer (or an AI-driven objection) as decision input.
- Support tickets/calls include “ChatGPT/Claude/Perplexity said…” followed by a specific incorrect statement.
- AI answers cite stale/non-canonical sources (old pricing pages, outdated docs, third-party summaries) for the wrong claims.

---

### Pain Segment 2 (Primary): “Competitors are winning the AI answer” (share-of-answer loss)

**What they’re feeling**
- They still win classic SEO or brand awareness, but AI assistants recommend competitors for category prompts (“best X”, “alternatives to Y”, “X vs Y”).

**Trigger moments**
- A rep sees AI summaries in the buyer workflow (prospect forwarded a chat transcript)
- Category-level prompts consistently cite competitors, not them
- Leadership asks for a “share of voice in AI” report and nobody can answer

**What it looks like in the wild**
- Internal artifact: Sales enablement doc suddenly includes “what AI says about us vs competitor.”
- External artifact: buyers asking AI “best {category}” and getting competitor-first recommendations.
- Business impact: fewer inbound assists, worse win rates, more pricing pressure (“AI says competitor is better for X”).

**What they ask for**
- “Where are we losing and why?”
- “What do we need to publish/change to be the cited recommendation?”

**Scrunch wedge**
- Competitive monitoring by topic/persona/model
- Gaps analysis: what AI is citing for competitors that it can’t find for you

**First win**
- A prioritized “citation gap list” (topics + pages + recommended content/structure changes)
- Early movement on high-intent prompts (the ones buyers actually ask)

**Common owners**
- Head of SEO, Demand Gen/Growth, PMM; plus Sales leadership as an internal champion

**Signals (more accurate / higher-fidelity)**
- Buyers share AI transcripts during evaluation (especially “best X”, “X vs Y”, “alternatives to X”) that cite competitors ahead of you.
- Sales enablement starts compiling “what AI says about us vs competitor” screenshots because it affects pipeline.
- A repeatable prompt set (across models) consistently cites competitor docs/pages for topics you consider core.
- “Alternatives to {your brand}” and comparison prompts trend toward competitor-first recommendations.

---

### Pain Segment 3 (Primary): “AI search started sending us customers — and we can’t control it” (new channel emergence)

**What they’re feeling**
- AI search becomes a real acquisition channel (or is clearly about to), but the team lacks a repeatable operating cadence.

**Trigger moments**
- First noticeable AI-driven signups/leads (or leadership believes it’s imminent)
- A competitor publicly claims “AI search growth” and leadership wants an answer
- The team tries manual prompt testing and realizes it doesn’t scale or stay consistent

**What it looks like in the wild**
- Internal artifact: “AI referrals” shows up in a growth dashboard, but nobody owns it.
- External artifact: prospects arrive with unusually well-formed questions (AI pre-research) and cite AI outputs.
- Business impact: missed upside (channel grows without them), wasted cycles on non-repeatable testing.

**What they ask for**
- “How do we make AI search a managed channel (like SEO)?”
- “What should we measure weekly, and what actions move the needle?”

**Scrunch wedge**
- Monitoring + analytics loop that turns prompt visibility into a weekly workflow
- Insights that convert “we’re not showing up” into actionable fixes

**First win**
- A weekly dashboard of priority prompts/topics with clear actions and owners
- Proof that specific changes map to improved citations/mentions and downstream conversions

**Common owners**
- Growth/Demand Gen + SEO/Content; often with RevOps/Analytics for attribution alignment

**Signals (more accurate / higher-fidelity)**
- Inbound leads explicitly say “found you via ChatGPT/Perplexity/Claude” (forms, calls, emails) or share AI summaries as context.
- Web analytics shows consistent AI referrers (or a measurable “dark” uplift paired with self-reported AI discovery).
- “AI referrals” shows up in dashboards/requests, but there is no defined owner/cadence.
- Manual prompt testing is happening across teams, but results are inconsistent and not operationalized.

---

### Pain Segment 4 (High-value): “Our site is not AI-readable” (technical crawlability + citations)

**What they’re feeling**
- They have great content, but AI agents can’t reliably crawl/parse it (JS-heavy pages, fragmented docs, messy IA, blocked user-agents, inconsistent metadata).

**Trigger moments**
- “We have the content, but AI never cites us.”
- Web team hears: “We need an AI-friendly version of the site,” but a rebuild is too expensive

**What it looks like in the wild**
- Internal artifact: SEO says “we published it,” engineering says “it’s behind JS/blocked/fragmented.”
- External artifact: AI answers mention the category, but never cite their site (or cites thin/irrelevant pages).
- Business impact: great content with zero AI distribution; persistent citation gaps despite content investment.

**What they ask for**
- “How do we make our site AI-agent friendly without replatforming?”
- “How do we prove technical changes improved citations?”

**Scrunch wedge**
- AXP as the technical unlock: serve AI agents content they can parse and cite
- Monitoring to validate impact (citations/mentions by topic and model)

**First win**
- A subset of priority pages becomes consistently citable across key AI platforms
- Reduced “AI can’t find us” problem on the highest-value topics

**Common owners**
- Web platform/digital engineering + SEO; security/IT involved if governance is required

**Signals (more accurate / higher-fidelity)**
- Server logs / bot management show AI user-agents are blocked, challenged, or served inconsistent content (e.g., WAF rules, auth walls, aggressive rate limits).
- Key pages are JS-heavy or fragmented (docs split across many routes), and “view source” is thin vs what humans see.
- AI answers mention the category but rarely/never cite their domain for priority topics despite strong content investment.
- SEO and engineering are already in conflict about “we published it” vs “it’s not crawlable/citable.”

---

### Pain Segment 5 (Partner): “Clients keep asking about AI search” (agency productization)

**What they’re feeling**
- They need defensible measurement and repeatable execution to sell “AI visibility” as a service.

**Trigger moments**
- Multiple clients ask the same “How do we show up in ChatGPT?” question in a month
- Competitive agency claims “GEO/AI SEO” and wins pitches

**What it looks like in the wild**
- Internal artifact: the agency creates a “GEO offering” deck but can’t operationalize measurement/actions.
- External artifact: client demands recurring reporting and proof of impact beyond screenshots.
- Business impact: churn risk, stalled expansions, margin loss (too much manual work per account).

**What they ask for**
- “How do we report AI visibility without spending hours prompting?”
- “What’s the playbook we can run across accounts?”

**Scrunch wedge**
- Multi-client monitoring + standardized reporting cadence
- Playbooks grounded in measurable changes (not “prompt vibes”)

**First win**
- A client-ready baseline report + an “actions shipped → visibility improved” story

**Common owners**
- Head of SEO, VP Client Services, Agency owner/partner

**Signals (more accurate / higher-fidelity)**
- Multiple clients ask for “AI visibility/GEO” reporting in a short window, and the agency is answering with screenshots/manual prompts.
- The agency has (or is building) a GEO offering deck but cannot define a repeatable measurement cadence or tie actions to outcomes.
- Client renewals/expansions start requiring an “AI visibility” story alongside SEO/performance reporting.
- Delivery teams report margin compression due to manual prompt testing and bespoke reporting.

## 5-Minute Qualification (pain-first)

Ask these and you’ll know quickly if there’s a real problem:

- “What’s the most damaging AI answer you’ve seen about your brand/product? Who escalated it?”
- “Name the 3 prompts you *wish* you won today. Do you show up right now?”
- “When you update positioning/pricing, how long does it take for the market to ‘learn’ it?”
- “Do Sales/Support see ‘ChatGPT said…’ in real conversations?”
- “If we improved citations for 10 prompts this month, what downstream KPI moves?”

Green lights:
- They can name specific wrong/competitive AI answers and who got burned by it
- They have clear priority prompts/topics (not “we want to show up everywhere”)
- They’re willing to assign owners for content + web changes

Red flags:
- No concrete examples (“we just want to be early”) and no owner/urgency
- They want “prompt hacking” without owning the underlying content/structure

## Buyer + Champion Map (pain-based)

Use the pain to pick the entry point:
- Accuracy/brand integrity pain → Brand/Comms, PMM, SEO
- Competitive share-of-answer pain → SEO, Growth/Demand Gen, PMM
- New channel emergence → Growth + SEO (with Analytics/RevOps)
- Technical AI-readability → Web/Platform + SEO (Security/IT as needed)
- Agency productization → Head of SEO, Client Services, Partner/Owner

## Known Customer Anchors → Likely Pain (hypotheses to validate)

The customer list in `company/deep-research-of-who-we-are.md` suggests these pains show up across very different orgs. Use this as a starting hypothesis (not a claim about any specific customer’s internal situation):

- Lenovo: Pain 1 + Pain 2 + Pain 4 tend to be acute when brand accuracy and scale matter.
- Crunchbase / Clerk / BigTime: Pain 2 + Pain 3 tend to be acute where inbound growth and comparisons matter.
- Skims: Pain 1 + Pain 2 tend to be acute where AI recommendations influence purchase journeys.
- Penn State University: Pain 1 tends to be acute where public-facing accuracy matters (programs, admissions, policies).
- BairesDev / agencies: Pain 5 tends to be acute where services teams need repeatable reporting + execution.
