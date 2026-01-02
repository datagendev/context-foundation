from __future__ import annotations

import hashlib
import hmac
import re
from typing import Any


def verify_hmac_sha256_signature(*, secret: str, body: bytes, header_value: str) -> bool:
    """
    Accepts either:
    - "sha256=<hex>"
    - "<hex>"
    """
    m = re.fullmatch(r"sha256=([0-9a-fA-F]{64})", header_value.strip())
    if m:
        got = m.group(1).lower()
    else:
        m2 = re.fullmatch(r"([0-9a-fA-F]{64})", header_value.strip())
        if not m2:
            return False
        got = m2.group(1).lower()
    expected = hmac.new(secret.encode("utf-8"), body, hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, got)


def derive_event_id(*, headers: dict[str, str], json_body: dict[str, Any] | None, raw_body: bytes) -> str:
    header_get = lambda k: (headers.get(k.lower()) or "").strip()  # noqa: E731

    event_id = header_get("x-event-id") or None
    if event_id is None:
        event_id = header_get("x-github-delivery") or None
    if event_id is None and isinstance(json_body, dict):
        json_id = json_body.get("id")
        if isinstance(json_id, str) and len(json_id.strip()) >= 8:
            event_id = json_id
    if event_id is None and isinstance(json_body, dict):
        # Fireflies: prefer clientReferenceId (user-supplied stable id) if present.
        client_ref = json_body.get("clientReferenceId")
        if isinstance(client_ref, str) and len(client_ref.strip()) >= 4:
            event_id = f"fireflies_ref:{client_ref.strip()}"
    if event_id is None and isinstance(json_body, dict):
        meeting_id = json_body.get("meetingId")
        event_type = json_body.get("eventType")
        if isinstance(meeting_id, str) and meeting_id.strip() and isinstance(event_type, str) and event_type.strip():
            event_id = f"fireflies:{meeting_id.strip()}:{event_type.strip()}"
    if event_id is None:
        event_id = f"sha256:{hashlib.sha256(raw_body).hexdigest()}"
    return event_id

