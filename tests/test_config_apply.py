import tempfile
import unittest

from app.config import AppConfig, apply_config
from app.db import get_provider_mapping, list_routing_rules, open_db


class TestConfigApply(unittest.TestCase):
    def test_apply_config_upserts_mapping_and_rule(self) -> None:
        cfg = AppConfig(
            version=1,
            mappings=[
                {
                    "provider": "unknown",
                    "action": "echo_action",
                    "handler_mode": "noop",
                    "handler_target": None,
                    "enabled": True,
                }
            ],
            rules=[
                {
                    "provider": "github",
                    "name": "push",
                    "priority": 10,
                    "conditions": {"all": [{"op": "header_equals", "name": "x-github-event", "value": "push"}]},
                    "action": "handle_github_push",
                    "handler_mode": "noop",
                    "handler_target": None,
                    "enabled": True,
                }
            ],
        )

        with tempfile.TemporaryDirectory() as td:
            conn = open_db(f"{td}/t.sqlite3")
            try:
                apply_config(conn, cfg)

                m = get_provider_mapping(conn, provider="unknown")
                self.assertIsNotNone(m)
                self.assertEqual(m.action, "echo_action")

                rules = list_routing_rules(conn, provider="github")
                self.assertEqual(len(rules), 1)
                self.assertEqual(rules[0].name, "push")
                self.assertEqual(rules[0].action, "handle_github_push")
            finally:
                conn.close()


if __name__ == "__main__":
    unittest.main()

