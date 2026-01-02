# Railway (SQLite-first) setup

SQLite is easiest on Railway when **one long-running service owns the database file**.
So we run the webhook server + worker in the same process, and trigger “cron” by making an HTTP call into that service.

## 1) Create the web service (webhook + worker)

1. Create a new Railway project from this repo.
2. Add a **Volume** to the service (for SQLite persistence).
3. Set these service settings:

**Start command**

```bash
python3 -m app.railway_service
```

**Environment variables**

- `APP_DB_PATH=/data/events.sqlite3` (pick a mount path you’ll use for the Volume)
- `INGRESS_SECRET=...` (recommended; blocks arbitrary inbound webhooks)
- `CRON_SECRET=...` (recommended; blocks cron enqueue endpoint)
- `ADMIN_SECRET=...` (recommended; protects `GET /events/<row_id>`)
- Optional: `WEBHOOK_SECRET=...` (enables simple HMAC signature check for `/webhook*`)
- Optional: `MAPPER_USE_AI=1` (enable Claude Agent SDK fallback provider detection)
- Optional: `MAPPER_AI_THRESHOLD=0.65` (only call AI below this heuristic confidence)

**Volume**

- Mount path: `/data`

After deploy, you should have:

- `GET /healthz` → `{ "ok": true }`
- `POST /webhook` or `POST /webhook/<hint>` → queues an event quickly (200 OK)
- `GET /events/<row_id>` → debug view of stored payload/result (use `ADMIN_SECRET`)

## 2) Create a Railway Cron Job (HTTP-triggered)

Create a new **Cron Job** service in the same Railway project.

**Schedule**

- e.g. every 5 minutes: `*/5 * * * *` (Railway cron runs in UTC)

**Start command**

```bash
python3 -m app.cron_call_http --job daily-digest
```

**Environment variables**

- `API_BASE_URL=https://<your-web-service-domain>` (the public URL of the web service)
- `CRON_SECRET=...` (must match the web service)

The cron job service should start, call the web service’s `/cron/enqueue`, and then exit.

## 3) Add a provider → action mapping

Locally (or via Railway “Run Command”), add a mapping:

```bash
python3 -m app.mapping_cli set --provider stripe --action handle_stripe --handler-mode noop
```

Add a rule (example: GitHub push events):

```bash
python3 -m app.mapping_cli rule-set \
  --provider github \
  --name push \
  --priority 10 \
  --conditions-json '{"all":[{"op":"header_present","name":"x-github-event"},{"op":"header_equals","name":"x-github-event","value":"push"}]}' \
  --action handle_github_push \
  --handler-mode noop
```

Then send a webhook with a Stripe header (or payload shape) and the worker will attach:

- `router.provider`
- `router.mapped_action`

to the stored event result.

## Notes / limitations

- SQLite won’t work across multiple Railway services unless they share the same persistent filesystem mount; this setup avoids that by keeping DB + worker in one service.
- This is an MVP pipeline: ingest → detect provider (heuristics) → look up mapping → (optionally) invoke an LLM runner.
