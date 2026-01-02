# Provider Routing Guide (single webhook endpoint)

Goal: We have **one** webhook endpoint that accepts **arbitrary** payloads. After ingest, a Claude subagent decides **which provider sent it** and **which subagent/command should run**.

## End-to-end path

1) **Webhook ingestion**  
`POST /webhook` (or `/webhook/<hint>`) stores:
- raw request metadata (headers, content-type, path)
- parsed JSON body when possible (else raw bytes as base64)

2) **Router agent is called**  
Claude is invoked with:
- the stored webhook payload (including headers + JSON)
- the current routing config (this file)

3) **Claude determines provider + route**  
Claude inspects the payload schema/signals and chooses:
- `provider` (e.g. `github`, `stripe`, `fireflies`, `unknown`)
- `event_type` (if available)
- `subagent` (or `command`) to handle it
- `arguments` needed by that subagent

## What to inspect in a webhook payload

Always check (in order):

1. **Signature headers** (strong provider signals)
- `stripe-signature` → Stripe
- `x-github-event` / `x-github-delivery` → GitHub
- `x-hub-signature` → often Fireflies-style HMAC webhooks

2. **Top-level JSON keys / shapes**
- Stripe events commonly have `{"id":"evt_...","object":"event","type":"...","data":...}`
- GitHub ping often includes `zen` and `hook_id`
- Fireflies-like payloads often include `meetingId` + `eventType` (and related transcript/meeting fields)

3. **Fallback**
- If no strong signals exist, classify as `unknown` and route to a generic “triage” subagent.

## Routing table (provider → default subagent)

Use this as the default mapping when no more specific rule matches:

| provider | default subagent | purpose |
|---|---|---|
| `fireflies` | `fireflies-triage` | parse transcript/meeting webhook, decide downstream action |
| `github` | `github-triage` | decide repo automation (issues/PRs/notifications) |
| `stripe` | `stripe-triage` | billing events (invoice/payment/customer) |
| `shopify` | `shopify-triage` | ecommerce events |
| `slack` | `slack-triage` | events/interactive payloads |
| `twilio` | `twilio-triage` | telephony/SMS callbacks |
| `unknown` | `webhook-triage` | guess provider + propose mapping |

## Provider-specific notes (Fireflies example)

If the webhook is “pretend Fireflies”:

1. Treat `x-hub-signature` as a strong signal for `provider="fireflies"`.
2. Look for an event type field (e.g. `eventType`) and a meeting identifier (e.g. `meetingId`).
3. Extract stable ids to support idempotency downstream:
   - prefer `clientReferenceId` if present (client-supplied stable id)
   - else build an id from `(meetingId, eventType)` when available
4. Choose subagent:
   - `fireflies-transcript-processor` if transcript content/URLs are present
   - `fireflies-meeting-metadata` if it’s a meeting-created/updated event
   - `fireflies-triage` if ambiguous

## Required output format for the router agent

Return a single JSON object:

```json
{
  "provider": "fireflies|github|stripe|...|unknown",
  "confidence": 0.0,
  "event_type": "string-or-null",
  "subagent": "string",
  "command": null,
  "arguments": {},
  "notes": "short explanation of why you chose this route"
}
```

Rules:
- Prefer `subagent` routing (human-readable, stable).
- Use `command` only if a specific whitelisted command is configured for that route.
- If unsure, pick `provider="unknown"` and `subagent="webhook-triage"`.

