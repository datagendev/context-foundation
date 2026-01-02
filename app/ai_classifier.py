from __future__ import annotations

import json
from typing import Any

from .claude_agent_sdk_runner import run_structured_json_schema


def _truncate_json(obj: Any, *, max_chars: int = 20_000) -> Any:
    try:
        s = json.dumps(obj, ensure_ascii=False)
    except Exception:
        return {"note": "unserializable"}
    if len(s) <= max_chars:
        return obj
    return {"truncated_json": s[:max_chars], "original_length": len(s)}


def summarize_payload_for_ai(payload: dict[str, Any]) -> dict[str, Any]:
    headers = payload.get("headers")
    headers_out: dict[str, Any] = {}
    if isinstance(headers, dict):
        for k, v in headers.items():
            ks = str(k).lower()
            if ks in {
                "x-github-event",
                "x-github-delivery",
                "stripe-signature",
                "x-shopify-topic",
                "x-slack-signature",
                "x-twilio-signature",
                "content-type",
                "user-agent",
            }:
                headers_out[ks] = v
        headers_out["__all_header_names__"] = sorted({str(k).lower() for k in headers.keys()})[:200]

    summary: dict[str, Any] = {
        "source_hint": payload.get("source_hint"),
        "path": payload.get("path"),
        "content_type": payload.get("content_type"),
        "headers": headers_out,
    }
    if isinstance(payload.get("json"), dict):
        summary["json"] = _truncate_json(payload["json"])
        summary["json_top_level_keys"] = sorted(list(payload["json"].keys()))[:200]
    return summary


def ai_detect_provider(payload: dict[str, Any]) -> dict[str, Any]:
    schema = {
        "type": "object",
        "additionalProperties": False,
        "properties": {
            "provider": {"type": "string"},
            "confidence": {"type": "number", "minimum": 0, "maximum": 1},
            "event_type": {"type": ["string", "null"]},
            "event_type_path": {"type": ["string", "null"]},
            "event_id": {"type": ["string", "null"]},
            "event_id_path": {"type": ["string", "null"]},
            "notes": {"type": "string"},
        },
        "required": ["provider", "confidence", "event_type", "event_type_path", "event_id", "event_id_path", "notes"],
    }

    system_prompt = (
        "You are a webhook payload classifier.\n"
        "Given an arbitrary webhook payload summary, identify which provider/service likely sent it.\n"
        "Return ONLY the JSON required by the schema.\n"
        "If unsure, use provider='unknown' and low confidence.\n"
        "If you can identify an event type (like 'invoice.paid') and where it lives in the JSON body, fill event_type and event_type_path.\n"
        "Paths are dot-separated within the JSON body (e.g. 'type', 'event.type')."
    )

    prompt_obj = {"task": "classify_webhook_provider", "payload_summary": summarize_payload_for_ai(payload)}
    return run_structured_json_schema(system_prompt=system_prompt, prompt=json.dumps(prompt_obj, ensure_ascii=False), json_schema=schema)

