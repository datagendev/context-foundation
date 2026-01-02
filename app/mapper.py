from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .db import ProviderMapping, RoutingRule, get_provider_mapping, list_routing_rules
from .detect_provider import ProviderDetection, detect_provider
from .ai_classifier import ai_detect_provider
from .rule_eval import rule_matches
from .settings import get_settings


@dataclass(frozen=True)
class RouteDecision:
    provider: str
    confidence: float
    detection: ProviderDetection
    ai_detection: dict[str, Any] | None
    event_type: str | None
    matched_rule: str | None
    action: str | None
    handler_mode: str | None
    handler_target: str | None
    reasons: list[str]


def _best_provider_hint(payload: dict[str, Any]) -> tuple[str | None, float]:
    hint = payload.get("source_hint")
    if hint is None:
        return None, 0.0
    hint_s = str(hint).strip().lower()
    if not hint_s or hint_s in {"unknown", "test"}:
        return None, 0.0
    return hint_s, 0.6


def _choose_provider(payload: dict[str, Any]) -> ProviderDetection:
    hint, hint_conf = _best_provider_hint(payload)
    detection = detect_provider(payload)
    if hint and hint_conf > detection.confidence:
        return ProviderDetection(provider=hint, confidence=hint_conf, signals=["path:source_hint"])
    return detection


def route_event(conn: Any, payload: dict[str, Any]) -> RouteDecision:
    settings = get_settings()
    detection = _choose_provider(payload)
    reasons: list[str] = list(detection.signals)

    ai_out: dict[str, Any] | None = None
    event_type: str | None = None
    if settings.mapper_use_ai and detection.confidence < settings.mapper_ai_threshold:
        try:
            ai_out = ai_detect_provider(payload)
            ai_provider = str(ai_out.get("provider") or "").strip().lower()
            ai_conf = float(ai_out.get("confidence") or 0.0)
            if ai_provider and ai_provider != "unknown" and ai_conf >= detection.confidence:
                reasons.append("ai:provider_override")
                detection = ProviderDetection(provider=ai_provider, confidence=ai_conf, signals=detection.signals + ["ai:detected"])
            event_type = ai_out.get("event_type") if isinstance(ai_out.get("event_type"), str) else None
        except Exception as e:
            reasons.append(f"ai:error:{type(e).__name__}")

    provider = detection.provider
    rules: list[RoutingRule] = []
    if provider:
        rules = [r for r in list_routing_rules(conn, provider=provider) if r.enabled]

    for rule in rules:
        match = rule_matches(payload, rule.conditions)
        if match.matched:
            reasons.extend([f"rule:{rule.name}"] + match.reasons)
            return RouteDecision(
                provider=provider,
                confidence=detection.confidence,
                detection=detection,
                ai_detection=ai_out,
                event_type=event_type,
                matched_rule=rule.name,
                action=rule.action,
                handler_mode=rule.handler_mode,
                handler_target=rule.handler_target,
                reasons=reasons,
            )

    mapping: ProviderMapping | None = None
    if provider:
        mapping = get_provider_mapping(conn, provider=provider)
        if mapping and mapping.enabled:
            reasons.append("fallback:provider_mapping")
            return RouteDecision(
                provider=provider,
                confidence=detection.confidence,
                detection=detection,
                ai_detection=ai_out,
                event_type=event_type,
                matched_rule=None,
                action=mapping.action,
                handler_mode=mapping.handler_mode,
                handler_target=mapping.handler_target,
                reasons=reasons,
            )

    return RouteDecision(
        provider=provider,
        confidence=detection.confidence,
        detection=detection,
        ai_detection=ai_out,
        event_type=event_type,
        matched_rule=None,
        action=None,
        handler_mode=None,
        handler_target=None,
        reasons=reasons,
    )
