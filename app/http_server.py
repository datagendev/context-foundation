from __future__ import annotations

import argparse
import base64
import hmac
import json
from contextlib import asynccontextmanager
from typing import Any

import uvicorn
from fastapi import BackgroundTasks, FastAPI, Request
from fastapi.responses import JSONResponse

from .agent_executor import execute_agent
from .config import apply_config, load_config
from .db import enqueue_event, get_event_row, init_db, list_action_runs_for_event, open_db
from .logger import get_logger
from .settings import Settings, get_settings
from .webhook_utils import verify_hmac_sha256_signature

logger = get_logger(__name__)

MAX_BODY_BYTES = 2_097_152


def _json(status: int, obj: dict[str, Any]) -> JSONResponse:
    return JSONResponse(status_code=status, content=obj)


def _unauthorized() -> JSONResponse:
    return _json(401, {"ok": False, "error": "unauthorized"})


def _require_secret(request: Request, *, secret: str, header_name: str) -> JSONResponse | None:
    if not secret:
        return None
    got = (request.headers.get(header_name) or "").strip()
    if not got or not hmac.compare_digest(got, secret):
        return _unauthorized()
    return None


def create_app(*, db_path: str | None = None, bootstrap: bool = True, settings: Settings | None = None) -> FastAPI:
    settings = settings or get_settings()
    resolved_db_path = db_path or settings.app_db_path

    @asynccontextmanager
    async def lifespan(_app: FastAPI):
        if bootstrap:
            import os

            db_dir = os.path.dirname(resolved_db_path)
            if db_dir:
                os.makedirs(db_dir, exist_ok=True)
            conn = open_db(resolved_db_path)
            try:
                init_db(conn)
                cfg = load_config()
                if cfg is not None:
                    apply_config(conn, cfg)
            finally:
                conn.close()
        yield

    app = FastAPI(title="Context Foundation", version="0.3", lifespan=lifespan)

    @app.get("/healthz")
    def healthz() -> dict[str, Any]:
        return {"ok": True}

    @app.get("/events/{event_row_id}")
    def get_event(request: Request, event_row_id: str) -> JSONResponse:
        auth = _require_secret(request, secret=settings.admin_secret, header_name="X-Admin-Secret")
        if auth is not None:
            return auth

        event_row_id = event_row_id.strip()
        if not event_row_id.isdigit():
            return _json(400, {"ok": False, "error": "invalid event id"})

        conn = open_db(resolved_db_path)
        try:
            row_id = int(event_row_id)
            event_row = get_event_row(conn, event_row_id=row_id)
            if event_row is None:
                return _json(404, {"ok": False, "error": "not found"})
            runs = list_action_runs_for_event(conn, event_row_id=row_id, limit=10)
        finally:
            conn.close()

        return _json(200, {"ok": True, "event": event_row, "action_runs": runs})

    @app.post("/cron/enqueue")
    def cron_enqueue(request: Request) -> JSONResponse:
        auth = _require_secret(request, secret=settings.ingress_secret, header_name="X-Ingress-Secret")
        if auth is not None:
            return auth

        auth = _require_secret(request, secret=settings.cron_secret, header_name="X-Cron-Secret")
        if auth is not None:
            return auth

        job = (request.query_params.get("job") or "").strip()
        if not job:
            return _json(400, {"ok": False, "error": "missing job"})

        conn = open_db(resolved_db_path)
        try:
            row_id = enqueue_event(conn, source="cron", event_id=None, payload={"job": job, "source_hint": "cron"})
        finally:
            conn.close()

        return _json(200, {"ok": True, "status": "queued", "row_id": row_id})

    async def _execute_agent_task(agent_name: str, payload: dict[str, Any]) -> None:
        """Background task to execute agent."""
        task_logger = get_logger("http_server.agent_task")
        try:
            await execute_agent(agent_name, payload)
        except Exception as e:
            # Log error but don't raise - webhook already returned 200
            task_logger.error("Agent execution failed for %s: %s", agent_name, e, exc_info=True)

    @app.post("/webhook/{agent_name}")
    async def webhook(request: Request, agent_name: str, background_tasks: BackgroundTasks) -> JSONResponse:
        auth = _require_secret(request, secret=settings.ingress_secret, header_name="X-Ingress-Secret")
        if auth is not None:
            return auth
        logger.info("Received webhook for %s", agent_name)
        agent_name = agent_name.strip("/") or "echo"
        if not agent_name:
            return _json(400, {"ok": False, "error": "agent_name required"})

        body = await request.body()
        if len(body) <= 0 or len(body) > MAX_BODY_BYTES:
            return _json(413, {"ok": False, "error": "payload too large or empty"})

        # Optional signature verification (single endpoint, detect by signature header).
        # - X-Signature: sha256=<hex> (custom)
        # - X-Hub-Signature: <hex> or sha256=<hex> (Fireflies per their docs)
        if settings.webhook_secret:
            sig = request.headers.get("X-Signature", "") or ""
            if sig and not verify_hmac_sha256_signature(secret=settings.webhook_secret, body=body, header_value=sig):
                return _json(401, {"ok": False, "error": "invalid signature"})

        if settings.fireflies_webhook_secret:
            ff_sig = request.headers.get("X-Hub-Signature", "") or ""
            if ff_sig and not verify_hmac_sha256_signature(
                secret=settings.fireflies_webhook_secret, body=body, header_value=ff_sig
            ):
                return _json(401, {"ok": False, "error": "invalid signature"})

        content_type = (request.headers.get("Content-Type") or "").lower()
        headers = {k.lower(): v for k, v in request.headers.items()}

        payload: dict[str, Any] = {
            "agent_name": agent_name,
            "method": request.method,
            "path": request.url.path,
            "content_type": content_type,
            "headers": headers,
        }

        json_body: dict[str, Any] | None = None
        if "application/json" in content_type:
            try:
                parsed = json.loads(body.decode("utf-8"))
                if isinstance(parsed, dict):
                    json_body = parsed
                    payload["json"] = json_body
                else:
                    payload["json"] = {"_non_object_json": True}
            except Exception:
                payload["parse_error"] = "invalid_json"
                payload["raw_body_base64"] = base64.b64encode(body).decode("ascii")
        else:
            payload["raw_body_base64"] = base64.b64encode(body).decode("ascii")

        # Validate agent exists before queuing
        try:
            from .agent_executor import safe_agent_path
            safe_agent_path(agent_name)
        except FileNotFoundError:
            return _json(404, {"ok": False, "error": f"agent not found: {agent_name}"})

        logger.info("Queueing agent execution for %s: %s", agent_name, payload)
        # Queue agent execution in background and return immediately
        background_tasks.add_task(_execute_agent_task, agent_name, payload)
        return _json(200, {"ok": True, "status": "accepted", "agent": agent_name})

    return app


_settings = get_settings()
app = create_app(db_path=_settings.app_db_path, bootstrap=True, settings=_settings)


def main() -> None:
    settings = get_settings()
    parser = argparse.ArgumentParser(description="Webhook ingestion server (queues events in SQLite).")
    parser.add_argument("--host", default=settings.host)
    parser.add_argument("--port", type=int, default=settings.port)
    parser.add_argument("--db", default=settings.app_db_path)
    parser.add_argument("--reload", action="store_true", help="Enable auto-reload on code changes")
    args = parser.parse_args()

    if args.reload:
        # Use import string for reload to work
        uvicorn.run(
            "app.http_server:app",
            host=args.host,
            port=args.port,
            access_log=False,
            reload=args.reload,
        )
    else:
        # Use app object directly when reload is disabled
        uvicorn.run(
            create_app(db_path=args.db, bootstrap=True, settings=settings),
            host=args.host,
            port=args.port,
            access_log=False,
        )


if __name__ == "__main__":
    main()
