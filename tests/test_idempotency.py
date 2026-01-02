import json
import sqlite3
import tempfile
import unittest
from unittest import mock

from app.db import (
    create_action_run,
    finish_action_run,
    init_db,
    open_db,
    upsert_provider_mapping,
)
from app.webhook_utils import derive_event_id
from app.processor import process_event


class TestWebhookIdempotency(unittest.TestCase):
    def test_derive_event_id_prefers_x_event_id(self) -> None:
        raw = b'{"hello":"world"}'
        event_id = derive_event_id(headers={"x-event-id": "evt_custom"}, json_body={"id": "evt_ignored"}, raw_body=raw)
        self.assertEqual(event_id, "evt_custom")

    def test_derive_event_id_falls_back_to_github_delivery(self) -> None:
        raw = b'{"hello":"world"}'
        event_id = derive_event_id(headers={"x-github-delivery": "gh_123"}, json_body=None, raw_body=raw)
        self.assertEqual(event_id, "gh_123")

    def test_derive_event_id_falls_back_to_json_id(self) -> None:
        raw = b'{"id":"evt_12345678","object":"event"}'
        event_id = derive_event_id(headers={}, json_body={"id": "evt_12345678", "object": "event"}, raw_body=raw)
        self.assertEqual(event_id, "evt_12345678")

    def test_derive_event_id_falls_back_to_sha256(self) -> None:
        raw = b"abc"
        event_id = derive_event_id(headers={}, json_body=None, raw_body=raw)
        self.assertTrue(event_id.startswith("sha256:"))


class TestActionRunIdempotency(unittest.TestCase):
    def test_create_action_run_is_idempotent_per_event_action(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            db_path = f"{td}/t.sqlite3"
            conn = open_db(db_path)
            try:
                init_db(conn)
                event_row_id = 1

                run1 = create_action_run(
                    conn,
                    event_row_id=event_row_id,
                    provider="github",
                    action="handle_github",
                    handler_mode="noop",
                    handler_target=None,
                    input_obj={"x": 1},
                )
                run2 = create_action_run(
                    conn,
                    event_row_id=event_row_id,
                    provider="github",
                    action="handle_github",
                    handler_mode="noop",
                    handler_target=None,
                    input_obj={"x": 2},
                )
                self.assertEqual(run1, run2)

                count = conn.execute(
                    "SELECT COUNT(*) AS c FROM action_runs WHERE event_row_id=? AND action=?",
                    (event_row_id, "handle_github"),
                ).fetchone()["c"]
                self.assertEqual(count, 1)
            finally:
                conn.close()

    def test_process_event_skips_when_action_already_done(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            db_path = f"{td}/t.sqlite3"
            conn = open_db(db_path)
            try:
                init_db(conn)
                upsert_provider_mapping(
                    conn,
                    provider="github",
                    action="handle_github",
                    handler_mode="noop",
                    handler_target=None,
                    enabled=True,
                )

                # Create an events row with a payload that detects as GitHub.
                payload = {"headers": {"x-github-event": "push"}, "json": {"ref": "refs/heads/main"}}
                cur = conn.execute(
                    """
                    INSERT INTO events (source, event_id, received_at, status, next_attempt_at, payload_json)
                    VALUES ('webhook', 'evt_1', '2020-01-01T00:00:00+00:00', 'processing', '2020-01-01T00:00:00+00:00', ?)
                    """,
                    (json.dumps(payload),),
                )
                event_row_id = int(cur.lastrowid)

                # Pretend the action already ran successfully.
                run_id = create_action_run(
                    conn,
                    event_row_id=event_row_id,
                    provider="github",
                    action="handle_github",
                    handler_mode="noop",
                    handler_target=None,
                    input_obj={"router": {}, "payload": payload},
                )
                finish_action_run(conn, run_id=run_id, status="done", output_obj={"ok": True, "already": "done"})

                # If action runner is called, fail the test.
                with mock.patch("app.processor.run_action", side_effect=AssertionError("should not run_action")):
                    from app.db import Event

                    event = Event(
                        id=event_row_id,
                        source="webhook",
                        event_id="evt_1",
                        received_at="2020-01-01T00:00:00+00:00",
                        status="processing",
                        attempt_count=0,
                        next_attempt_at="2020-01-01T00:00:00+00:00",
                        payload=payload,
                    )
                    out = process_event(conn, event)
                    self.assertTrue(out["ok"])
                    self.assertTrue(out.get("idempotent_replay"))
                    self.assertEqual(out["result"]["already"], "done")
            finally:
                conn.close()


if __name__ == "__main__":
    unittest.main()
