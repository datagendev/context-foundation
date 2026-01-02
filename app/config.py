from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .db import init_db, upsert_provider_mapping, upsert_routing_rule
from .settings import get_settings


@dataclass(frozen=True)
class AppConfig:
    version: int
    mappings: list[dict[str, Any]]
    rules: list[dict[str, Any]]


def load_config(path: str | None = None) -> AppConfig | None:
    config_path = path or get_settings().app_config_path or os.getenv("APP_CONFIG_PATH", "").strip()
    if not config_path:
        return None

    p = Path(config_path)
    raw = p.read_text(encoding="utf-8")
    obj = json.loads(raw)
    if not isinstance(obj, dict):
        raise ValueError("Config must be a JSON object.")

    version = int(obj.get("version", 1))
    mappings = obj.get("mappings", [])
    rules = obj.get("rules", [])

    if not isinstance(mappings, list) or not all(isinstance(x, dict) for x in mappings):
        raise ValueError("config.mappings must be a list of objects.")
    if not isinstance(rules, list) or not all(isinstance(x, dict) for x in rules):
        raise ValueError("config.rules must be a list of objects.")

    return AppConfig(version=version, mappings=mappings, rules=rules)


def apply_config(conn: Any, config: AppConfig) -> None:
    init_db(conn)

    for m in config.mappings:
        provider = str(m.get("provider") or "").strip().lower()
        action = str(m.get("action") or "").strip()
        if not provider or not action:
            continue
        upsert_provider_mapping(
            conn,
            provider=provider,
            action=action,
            handler_mode=str(m.get("handler_mode") or "noop"),
            handler_target=m.get("handler_target"),
            enabled=bool(m.get("enabled", True)),
        )

    for r in config.rules:
        provider = str(r.get("provider") or "").strip().lower()
        name = str(r.get("name") or "").strip()
        action = str(r.get("action") or "").strip()
        if not provider or not name or not action:
            continue

        conditions = r.get("conditions")
        if not isinstance(conditions, dict):
            continue

        upsert_routing_rule(
            conn,
            provider=provider,
            name=name,
            priority=int(r.get("priority", 100)),
            conditions=conditions,
            action=action,
            handler_mode=str(r.get("handler_mode") or "noop"),
            handler_target=r.get("handler_target"),
            enabled=bool(r.get("enabled", True)),
        )
