from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class ProviderDetection:
    provider: str
    confidence: float
    signals: list[str]


def _lower_headers(headers: dict[str, Any] | None) -> dict[str, str]:
    if not headers:
        return {}
    lowered: dict[str, str] = {}
    for k, v in headers.items():
        if k is None:
            continue
        key = str(k).strip().lower()
        if not key:
            continue
        lowered[key] = "" if v is None else str(v)
    return lowered


def detect_provider(payload: dict[str, Any]) -> ProviderDetection:
    headers = _lower_headers(payload.get("headers"))
    json_body = payload.get("json")
    signals: list[str] = []

    # Fireflies webhooks use `x-hub-signature` (HMAC SHA-256) per their docs.
    if "x-hub-signature" in headers:
        signals.append("header:x-hub-signature")
        if isinstance(json_body, dict) and "meetingId" in json_body and "eventType" in json_body:
            signals.append("json:fireflies_shape")
            return ProviderDetection(provider="fireflies", confidence=0.98, signals=signals)
        return ProviderDetection(provider="fireflies", confidence=0.8, signals=signals)

    if "stripe-signature" in headers:
        signals.append("header:stripe-signature")
        return ProviderDetection(provider="stripe", confidence=0.98, signals=signals)

    if "x-github-event" in headers or "x-github-delivery" in headers:
        if "x-github-event" in headers:
            signals.append("header:x-github-event")
        if "x-github-delivery" in headers:
            signals.append("header:x-github-delivery")
        return ProviderDetection(provider="github", confidence=0.98, signals=signals)

    if "x-shopify-topic" in headers:
        signals.append("header:x-shopify-topic")
        return ProviderDetection(provider="shopify", confidence=0.98, signals=signals)

    if "x-slack-signature" in headers:
        signals.append("header:x-slack-signature")
        return ProviderDetection(provider="slack", confidence=0.95, signals=signals)

    if "x-twilio-signature" in headers:
        signals.append("header:x-twilio-signature")
        return ProviderDetection(provider="twilio", confidence=0.95, signals=signals)

    if isinstance(json_body, dict):
        if json_body.get("object") == "event" and "type" in json_body and "data" in json_body:
            signals.append("json:stripe_event_shape")
            return ProviderDetection(provider="stripe", confidence=0.85, signals=signals)

        if "zen" in json_body and "hook_id" in json_body:
            signals.append("json:github_ping_shape")
            return ProviderDetection(provider="github", confidence=0.75, signals=signals)

        if "challenge" in json_body and re.search(r"slack", str(json_body.get("token", "")), re.I):
            signals.append("json:slack_challenge_shape")
            return ProviderDetection(provider="slack", confidence=0.65, signals=signals)

    return ProviderDetection(provider="unknown", confidence=0.2, signals=signals)
