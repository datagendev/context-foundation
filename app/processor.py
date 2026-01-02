from __future__ import annotations

import json
from typing import Any

from .db import Event
from .db import create_action_run, finish_action_run, get_action_run_for_event_action, restart_action_run
from .mapper import route_event
from .action_runner import run_action


def process_event(conn: Any, event: Event) -> dict[str, Any]:
    decision = route_event(conn, event.payload)
    router = {
        "provider": decision.provider,
        "confidence": decision.confidence,
        "event_type": decision.event_type,
        "matched_rule": decision.matched_rule,
        "mapped_action": decision.action,
        "handler_mode": decision.handler_mode,
        "handler_target": decision.handler_target,
        "reasons": decision.reasons,
        "ai_detection": decision.ai_detection,
    }

    if not decision.action or not decision.handler_mode:
        return {"ok": True, "source": event.source, "event_id": event.event_id, "router": router, "result": {"note": "no mapping"}}

    existing = get_action_run_for_event_action(conn, event_row_id=event.id, action=decision.action)
    if existing is not None and existing.get("status") == "done":
        out = existing.get("output_json")
        if isinstance(out, str) and out:
            try:
                return {
                    "ok": True,
                    "source": event.source,
                    "event_id": event.event_id,
                    "router": router,
                    "result": json.loads(out),
                    "idempotent_replay": True,
                }
            except json.JSONDecodeError:
                return {
                    "ok": True,
                    "source": event.source,
                    "event_id": event.event_id,
                    "router": router,
                    "result": {"raw_output_json": out},
                    "idempotent_replay": True,
                }

    run_id = create_action_run(
        conn,
        event_row_id=event.id,
        provider=decision.provider,
        action=decision.action,
        handler_mode=decision.handler_mode,
        handler_target=decision.handler_target,
        input_obj={"router": router, "payload": event.payload},
    )

    try:
        if existing is not None and existing.get("status") == "error" and int(existing.get("id")) == run_id:
            restart_action_run(conn, run_id=run_id)

        output = run_action(
            handler_mode=decision.handler_mode,
            handler_target=decision.handler_target,
            action=decision.action,
            event_payload=event.payload,
            router=router,
        )
        finish_action_run(conn, run_id=run_id, status="done", output_obj=output)
        return {"ok": True, "source": event.source, "event_id": event.event_id, "router": router, "result": output}
    except Exception as e:
        err = f"{type(e).__name__}: {e}"
        finish_action_run(conn, run_id=run_id, status="error", error=err)
        return {"ok": False, "source": event.source, "event_id": event.event_id, "router": router, "error": err}
