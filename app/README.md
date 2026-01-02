# Webhooks + Cron → Event Queue → Worker (Claude/LLM)

This folder is a minimal “trigger service” you can deploy or run locally so external systems can:

- send webhooks (GitHub/Stripe/etc.)
- trigger scheduled work (cron)
- enqueue events quickly and reliably
- process them asynchronously in a worker that can call an LLM (Claude Code CLI, Claude API, etc.)

It uses **FastAPI + Uvicorn** for HTTP and **SQLite** (stdlib) as the queue for simplicity.

## Architecture (minimal + production-shaped)

1. **Webhook server** receives `POST /webhook/<source>` and enqueues the payload (fast 200 OK).
2. **Worker** claims queued events, runs your logic/LLM, stores results, retries on failure.
3. **Cron** enqueues scheduled “events” (same pipeline as webhooks).

## Idempotency (avoid duplicate runs)

Webhook enqueueing is idempotent:

- `event_id` is taken from (first match):
  - `X-Event-Id` (custom)
  - `X-GitHub-Delivery` (GitHub)
  - top-level JSON `id` (common for providers like Stripe)
  - fallback: `sha256:<hash-of-raw-body>`
- All webhooks are stored with `source="webhook"`, so sending the same webhook to `/webhook` vs `/webhook/<hint>` still dedupes.

If the same `(source, event_id)` is received again, the server returns `200` with `status=duplicate_ignored` and the event is not re-processed.

Action execution is also idempotent per event:

- For a given queued event and routed `action`, the worker will not run the handler again if there is already a `done` action run recorded.

## Mapper (provider → rule → action → handler)

The worker does:

1. Detect provider (heuristics; optional AI fallback)
2. Apply the **first matching routing rule** for that provider (by priority)
3. Fall back to a provider-level mapping
4. Run a handler:
   - `noop`: do nothing
   - `agent`: run a Claude Agent SDK prompt (subagent) and return structured JSON
   - `command`: run a whitelisted local command from `app/commands.json`

## Quickstart (local)

Settings are loaded from environment variables (and optional `.env`) via `app/settings.py`.

Initialize DB + start the webhook server:

```bash
uv run python -m app.webhook_server --port 8080
```

Or run Uvicorn directly:

```bash
uv run uvicorn app.http_server:app --host 127.0.0.1 --port 8080
```

In another terminal, start the worker:

```bash
uv run python -m app.worker
```

If you want a single process that runs **both** (closer to how you’ll run it with SQLite on Railway):

```bash
uv run python -m app.railway_service
```

Send a test webhook:

```bash
curl -sS -X POST "http://127.0.0.1:8080/webhook/test" \
  -H "Content-Type: application/json" \
  -H "X-Event-Id: evt_123" \
  -d '{"hello":"world"}'
```

Check the worker logs; it should pick up the event and mark it done.

Note: some sandboxed environments block binding/listening on ports. If you hit `PermissionError: [Errno 1] Operation not permitted`, run the server outside the sandbox (or deploy it).

If `uv run ...` fails with a cache permission error, try:

```bash
UV_CACHE_DIR=.uv-cache uv run python -m app.railway_service
```

## Cron (enqueue scheduled jobs)

Enqueue a job:

```bash
uv run python -m app.cron_enqueue --job daily-digest
```

If you’re triggering cron via HTTP (recommended on Railway when using SQLite in the web service):

```bash
API_BASE_URL="http://127.0.0.1:8080" uv run python -m app.cron_call_http --job daily-digest
```

Example crontab entries (runs every 5 minutes):

```cron
*/5 * * * * cd /path/to/context-foundation && python3 -m app.cron_enqueue --job daily-digest
*/5 * * * * cd /path/to/context-foundation && python3 -m app.worker --run-once
```

## Webhook signature verification (optional)

If you set `WEBHOOK_SECRET`, the server will verify a simple HMAC SHA-256 signature:

- Header: `X-Signature: sha256=<hex>`
- Signature base string: raw request body bytes

Example (bash):

```bash
export WEBHOOK_SECRET="replace-me"
body='{"hello":"world"}'
sig=$(BODY="$body" WEBHOOK_SECRET="$WEBHOOK_SECRET" uv run python - <<'PY'
import hmac, hashlib, os
body = os.environ["BODY"].encode("utf-8")
secret = os.environ["WEBHOOK_SECRET"].encode("utf-8")
print(hmac.new(secret, body, hashlib.sha256).hexdigest())
PY
)
curl -sS -X POST "http://127.0.0.1:8080/webhook/test" \
  -H "Content-Type: application/json" \
  -H "X-Event-Id: evt_124" \
  -H "X-Signature: sha256=$sig" \
  -d "$body"
```

## Plugging in Claude / an LLM

By default the worker uses a safe no-op handler (no AI, no commands).

### AI provider detection (optional)

Enable AI fallback provider detection (only used when heuristics confidence is low):

```bash
export MAPPER_USE_AI=1
export MAPPER_AI_THRESHOLD=0.65
```

This uses **Claude Agent SDK** under the hood and typically requires your Claude/Anthropic credentials in the environment.

### Handler mode: `agent` (Claude Agent SDK)

Create a mapping or rule with `--handler-mode agent` and `--handler-target` pointing to:

- a short name that resolves to `.claude/agents/` first, then `app/agents/` (e.g. `slack-message-sender` → `.claude/agents/slack-message-sender.md` or `echo` → `app/agents/echo.md`)
- or an explicit relative path like `.claude/agents/slack-message-sender.md` or `app/agents/echo.md`

**Note:** Agents created via Claude Code's `/agents` command are automatically placed in `.claude/agents/` and will be found first.

### Handler mode: `command` (whitelisted argv)

Create `app/commands.json` based on `app/commands.example.json`, then map:

- `--handler-mode command`
- `--handler-target <key in commands.json>`

The worker passes a JSON object on stdin and expects JSON on stdout.

### Legacy / generic LLM runner

If you want to call an external CLI (e.g., Claude Code CLI) directly, set:

- `LLM_MODE=command`
- `LLM_COMMAND` to a command that reads stdin and prints a JSON object to stdout.

Example shape (adjust to your CLI):

```bash
export LLM_MODE=command
export LLM_COMMAND="claude -p -"
uv run python -m app.worker
```

If the command output is not valid JSON, the worker will store it under `{"raw_stdout": ...}`.

## Files

- `app/http_server.py`: FastAPI app + HTTP endpoints (webhooks + cron + debug read).
- `app/webhook_server.py`: convenience wrapper that runs the HTTP server.
- `app/settings.py`: environment-based settings with defaults (`pydantic-settings`).
- `app/worker.py`: worker loop (claims events, retries, stores results).
- `app/cron_enqueue.py`: CLI to enqueue scheduled jobs/events.
- `app/cron_call_http.py`: call the API to enqueue a cron job (Railway-friendly).
- `app/db.py`: SQLite schema + queue helpers.
- `app/mapping_cli.py`: CLI to manage provider → action mappings.
- `app/llm_runner.py`: adapter for calling an LLM (noop/command).
- `app/detect_provider.py`: heuristics-based provider detection.
- `app/railway_service.py`: runs webhook server + worker in one process.
- `app/mapper.py`: provider detection + routing (rules/mappings).
- `app/rule_eval.py`: rule conditions evaluator.
- `app/action_runner.py`: executes mapped handlers (noop/agent/command).
- `app/ai_classifier.py`: Claude Agent SDK provider classifier.
- `app/claude_agent_sdk_runner.py`: minimal SDK wrapper for structured outputs.

## Tests

Run:

```bash
uv run python -m unittest -v
```

Claude Agent SDK integration test (requires credentials + network; opt-in):

```bash
RUN_CLAUDE_AGENT_SDK_TESTS=1 uv run python -m unittest -v tests.test_claude_agent_sdk_integration
```

## End-to-end local test (send webhook → get agent output)

This uses the `GET /events/<row_id>` debug endpoint (protect it with `ADMIN_SECRET`).

1) Start the combined service (webhook + worker):

```bash
export INGRESS_SECRET="dev-ingress"
export ADMIN_SECRET="dev-admin"
export APP_DB_PATH="app/data/dev.sqlite3"
export APP_CONFIG_PATH="app/config.example.json"
uv run python -m app.railway_service
```

2) Route “unknown” payloads to the example agent:

```bash
uv run python -m app.mapping_cli set --provider unknown --action echo_action --handler-mode agent --handler-target echo
```

3) Send a webhook (capture `row_id` from the response):

```bash
curl -sS -X POST "http://127.0.0.1:8080/webhook" \
  -H "X-Ingress-Secret: dev-ingress" \
  -H "Content-Type: application/json" \
  -d '{"any":"payload"}'
```

4) Fetch the stored event + action run output (poll until the event `status` becomes `done`):

```bash
curl -sS "http://127.0.0.1:8080/events/<row_id>" -H "X-Admin-Secret: dev-admin"
```

## Config file (bootstrap mappings/rules)

You can load mappings + rules from a JSON config at startup:

- Set `APP_CONFIG_PATH=app/config.example.json`
- Or apply it on-demand:

```bash
uv run python -m app.mapping_cli apply-config --config app/config.example.json
```
