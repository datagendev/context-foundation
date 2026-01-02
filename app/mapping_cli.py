from __future__ import annotations

import argparse
import os
import json

from .db import (
    get_provider_mapping,
    init_db,
    list_routing_rules,
    open_db,
    upsert_provider_mapping,
    upsert_routing_rule,
)
from .config import apply_config, load_config
from .settings import get_settings


DEFAULT_DB_PATH = get_settings().app_db_path


def main() -> None:
    parser = argparse.ArgumentParser(description="Manage provider → action mappings (SQLite).")
    parser.add_argument("--db", default=DEFAULT_DB_PATH)

    sub = parser.add_subparsers(dest="cmd", required=True)

    set_cmd = sub.add_parser("set", help="Create/update a mapping")
    set_cmd.add_argument("--provider", required=True)
    set_cmd.add_argument("--action", required=True)
    set_cmd.add_argument("--handler-mode", default="noop", choices=["noop", "llm", "command", "agent"])
    set_cmd.add_argument("--handler-target", default=None)
    set_cmd.add_argument("--disabled", action="store_true")

    get_cmd = sub.add_parser("get", help="Fetch a mapping")
    get_cmd.add_argument("--provider", required=True)

    rule_set = sub.add_parser("rule-set", help="Create/update a routing rule")
    rule_set.add_argument("--provider", required=True)
    rule_set.add_argument("--name", required=True)
    rule_set.add_argument("--priority", type=int, default=100)
    rule_set.add_argument(
        "--conditions-json",
        required=True,
        help='JSON like {"all":[{"op":"header_present","name":"x-github-event"}]}',
    )
    rule_set.add_argument("--action", required=True)
    rule_set.add_argument("--handler-mode", default="noop", choices=["noop", "llm", "command", "agent"])
    rule_set.add_argument("--handler-target", default=None)
    rule_set.add_argument("--disabled", action="store_true")

    rule_list = sub.add_parser("rule-list", help="List routing rules for a provider")
    rule_list.add_argument("--provider", required=True)

    apply_cfg = sub.add_parser("apply-config", help="Apply mappings/rules from a JSON config file")
    apply_cfg.add_argument("--config", required=True, help="Path to config JSON (see app/config.example.json)")

    args = parser.parse_args()

    conn = open_db(args.db)
    try:
        init_db(conn)
        if args.cmd == "set":
            upsert_provider_mapping(
                conn,
                provider=args.provider.strip().lower(),
                action=args.action.strip(),
                handler_mode=args.handler_mode,
                handler_target=args.handler_target,
                enabled=not args.disabled,
            )
            print("ok")
            return

        if args.cmd == "get":
            mapping = get_provider_mapping(conn, provider=args.provider.strip().lower())
            if mapping is None:
                print("not found")
                return
            print(
                f"provider={mapping.provider} action={mapping.action} handler_mode={mapping.handler_mode} "
                f"handler_target={mapping.handler_target} enabled={mapping.enabled} updated_at={mapping.updated_at}"
            )
            return

        if args.cmd == "rule-set":
            conditions = json.loads(args.conditions_json)
            upsert_routing_rule(
                conn,
                provider=args.provider.strip().lower(),
                name=args.name.strip(),
                priority=args.priority,
                conditions=conditions,
                action=args.action.strip(),
                handler_mode=args.handler_mode,
                handler_target=args.handler_target,
                enabled=not args.disabled,
            )
            print("ok")
            return

        if args.cmd == "rule-list":
            rules = list_routing_rules(conn, provider=args.provider.strip().lower())
            if not rules:
                print("no rules")
                return
            for r in rules:
                print(
                    f"id={r.id} provider={r.provider} name={r.name} priority={r.priority} "
                    f"enabled={r.enabled} action={r.action} handler_mode={r.handler_mode} handler_target={r.handler_target}"
                )
            return

        if args.cmd == "apply-config":
            cfg = load_config(args.config)
            if cfg is None:
                raise SystemExit("No config loaded.")
            apply_config(conn, cfg)
            print("ok")
            return
    finally:
        conn.close()


if __name__ == "__main__":
    main()
