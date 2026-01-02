from __future__ import annotations

import json
import sqlite3
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def open_db(db_path: str) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path, isolation_level=None, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute("PRAGMA synchronous=NORMAL;")
    conn.execute("PRAGMA busy_timeout=3000;")
    return conn


def init_db(conn: sqlite3.Connection) -> None:
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS events (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          source TEXT NOT NULL,
          event_id TEXT,
          received_at TEXT NOT NULL,
          status TEXT NOT NULL,
          attempt_count INTEGER NOT NULL DEFAULT 0,
          next_attempt_at TEXT NOT NULL,
          processing_started_at TEXT,
          processed_at TEXT,
          payload_json TEXT NOT NULL,
          result_json TEXT,
          last_error TEXT
        );
        """
    )
    conn.execute(
        """
        CREATE UNIQUE INDEX IF NOT EXISTS events_source_event_id_uq
        ON events(source, event_id)
        WHERE event_id IS NOT NULL;
        """
    )
    conn.execute(
        """
        CREATE INDEX IF NOT EXISTS events_status_next_attempt_idx
        ON events(status, next_attempt_at);
        """
    )
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS provider_mappings (
          provider TEXT PRIMARY KEY,
          action TEXT NOT NULL,
          handler_mode TEXT NOT NULL DEFAULT 'noop',
          handler_target TEXT,
          enabled INTEGER NOT NULL DEFAULT 1,
          updated_at TEXT NOT NULL
        );
        """
    )
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS routing_rules (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          provider TEXT NOT NULL,
          name TEXT NOT NULL,
          priority INTEGER NOT NULL DEFAULT 100,
          conditions_json TEXT NOT NULL,
          action TEXT NOT NULL,
          handler_mode TEXT NOT NULL DEFAULT 'noop',
          handler_target TEXT,
          enabled INTEGER NOT NULL DEFAULT 1,
          updated_at TEXT NOT NULL,
          UNIQUE(provider, name)
        );
        """
    )
    conn.execute(
        """
        CREATE INDEX IF NOT EXISTS routing_rules_provider_priority_idx
        ON routing_rules(provider, enabled, priority, id);
        """
    )
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS action_runs (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          event_row_id INTEGER NOT NULL,
          started_at TEXT NOT NULL,
          finished_at TEXT,
          status TEXT NOT NULL,
          provider TEXT,
          action TEXT,
          handler_mode TEXT,
          handler_target TEXT,
          input_json TEXT NOT NULL,
          output_json TEXT,
          error TEXT,
          FOREIGN KEY(event_row_id) REFERENCES events(id)
        );
        """
    )
    conn.execute(
        """
        CREATE INDEX IF NOT EXISTS action_runs_event_idx
        ON action_runs(event_row_id, id);
        """
    )
    conn.execute(
        """
        CREATE UNIQUE INDEX IF NOT EXISTS action_runs_event_action_uq
        ON action_runs(event_row_id, action)
        WHERE action IS NOT NULL;
        """
    )


@dataclass(frozen=True)
class ProviderMapping:
    provider: str
    action: str
    handler_mode: str
    handler_target: str | None
    enabled: bool
    updated_at: str


@dataclass(frozen=True)
class RoutingRule:
    id: int
    provider: str
    name: str
    priority: int
    conditions: dict[str, Any]
    action: str
    handler_mode: str
    handler_target: str | None
    enabled: bool
    updated_at: str


def upsert_provider_mapping(
    conn: sqlite3.Connection,
    *,
    provider: str,
    action: str,
    handler_mode: str = "noop",
    handler_target: str | None = None,
    enabled: bool = True,
) -> None:
    now = utc_now_iso()
    conn.execute(
        """
        INSERT INTO provider_mappings (provider, action, handler_mode, handler_target, enabled, updated_at)
        VALUES (?, ?, ?, ?, ?, ?)
        ON CONFLICT(provider) DO UPDATE SET
          action=excluded.action,
          handler_mode=excluded.handler_mode,
          handler_target=excluded.handler_target,
          enabled=excluded.enabled,
          updated_at=excluded.updated_at
        """,
        (provider, action, handler_mode, handler_target, 1 if enabled else 0, now),
    )


def get_provider_mapping(conn: sqlite3.Connection, *, provider: str) -> ProviderMapping | None:
    row = conn.execute(
        """
        SELECT provider, action, handler_mode, handler_target, enabled, updated_at
        FROM provider_mappings
        WHERE provider = ?
        """,
        (provider,),
    ).fetchone()
    if row is None:
        return None
    return ProviderMapping(
        provider=str(row["provider"]),
        action=str(row["action"]),
        handler_mode=str(row["handler_mode"]),
        handler_target=row["handler_target"],
        enabled=bool(int(row["enabled"])),
        updated_at=str(row["updated_at"]),
    )


def upsert_routing_rule(
    conn: sqlite3.Connection,
    *,
    provider: str,
    name: str,
    priority: int,
    conditions: dict[str, Any],
    action: str,
    handler_mode: str = "noop",
    handler_target: str | None = None,
    enabled: bool = True,
) -> None:
    now = utc_now_iso()
    conn.execute(
        """
        INSERT INTO routing_rules
          (provider, name, priority, conditions_json, action, handler_mode, handler_target, enabled, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(provider, name) DO UPDATE SET
          priority=excluded.priority,
          conditions_json=excluded.conditions_json,
          action=excluded.action,
          handler_mode=excluded.handler_mode,
          handler_target=excluded.handler_target,
          enabled=excluded.enabled,
          updated_at=excluded.updated_at
        """,
        (
            provider,
            name,
            int(priority),
            json.dumps(conditions, separators=(",", ":"), ensure_ascii=False),
            action,
            handler_mode,
            handler_target,
            1 if enabled else 0,
            now,
        ),
    )


def list_routing_rules(conn: sqlite3.Connection, *, provider: str) -> list[RoutingRule]:
    rows = conn.execute(
        """
        SELECT id, provider, name, priority, conditions_json, action, handler_mode, handler_target, enabled, updated_at
        FROM routing_rules
        WHERE provider = ?
        ORDER BY enabled DESC, priority ASC, id ASC
        """,
        (provider,),
    ).fetchall()
    rules: list[RoutingRule] = []
    for row in rows:
        rules.append(
            RoutingRule(
                id=int(row["id"]),
                provider=str(row["provider"]),
                name=str(row["name"]),
                priority=int(row["priority"]),
                conditions=json.loads(row["conditions_json"]),
                action=str(row["action"]),
                handler_mode=str(row["handler_mode"]),
                handler_target=row["handler_target"],
                enabled=bool(int(row["enabled"])),
                updated_at=str(row["updated_at"]),
            )
        )
    return rules


def create_action_run(
    conn: sqlite3.Connection,
    *,
    event_row_id: int,
    provider: str | None,
    action: str | None,
    handler_mode: str | None,
    handler_target: str | None,
    input_obj: dict[str, Any],
) -> int:
    input_json = json.dumps(input_obj, separators=(",", ":"), ensure_ascii=False)
    try:
        cur = conn.execute(
            """
            INSERT INTO action_runs
              (event_row_id, started_at, status, provider, action, handler_mode, handler_target, input_json)
            VALUES (?, ?, 'running', ?, ?, ?, ?, ?)
            """,
            (event_row_id, utc_now_iso(), provider, action, handler_mode, handler_target, input_json),
        )
        return int(cur.lastrowid)
    except sqlite3.IntegrityError:
        row = conn.execute(
            """
            SELECT id
            FROM action_runs
            WHERE event_row_id = ? AND action = ?
            ORDER BY id DESC
            LIMIT 1
            """,
            (event_row_id, action),
        ).fetchone()
        if row is None:
            raise
        return int(row["id"])


def get_action_run(conn: sqlite3.Connection, *, run_id: int) -> dict[str, Any] | None:
    row = conn.execute(
        """
        SELECT id, event_row_id, started_at, finished_at, status, provider, action, handler_mode, handler_target, input_json, output_json, error
        FROM action_runs
        WHERE id = ?
        """,
        (run_id,),
    ).fetchone()
    if row is None:
        return None
    return dict(row)


def get_action_run_for_event_action(conn: sqlite3.Connection, *, event_row_id: int, action: str) -> dict[str, Any] | None:
    row = conn.execute(
        """
        SELECT id, event_row_id, started_at, finished_at, status, provider, action, handler_mode, handler_target, input_json, output_json, error
        FROM action_runs
        WHERE event_row_id = ? AND action = ?
        ORDER BY id DESC
        LIMIT 1
        """,
        (event_row_id, action),
    ).fetchone()
    if row is None:
        return None
    return dict(row)


def restart_action_run(conn: sqlite3.Connection, *, run_id: int) -> None:
    conn.execute(
        """
        UPDATE action_runs
        SET started_at=?, finished_at=NULL, status='running', output_json=NULL, error=NULL
        WHERE id=?
        """,
        (utc_now_iso(), run_id),
    )


def finish_action_run(
    conn: sqlite3.Connection,
    *,
    run_id: int,
    status: str,
    output_obj: dict[str, Any] | None = None,
    error: str | None = None,
) -> None:
    output_json = None
    if output_obj is not None:
        output_json = json.dumps(output_obj, separators=(",", ":"), ensure_ascii=False)
    conn.execute(
        """
        UPDATE action_runs
        SET finished_at=?, status=?, output_json=?, error=?
        WHERE id=?
        """,
        (utc_now_iso(), status, output_json, error, run_id),
    )


@dataclass(frozen=True)
class Event:
    id: int
    source: str
    event_id: str | None
    received_at: str
    status: str
    attempt_count: int
    next_attempt_at: str
    payload: dict[str, Any]


def enqueue_event(
    conn: sqlite3.Connection,
    *,
    source: str,
    event_id: str | None,
    payload: dict[str, Any],
) -> int:
    received_at = utc_now_iso()
    next_attempt_at = received_at
    payload_json = json.dumps(payload, separators=(",", ":"), ensure_ascii=False)
    cur = conn.execute(
        """
        INSERT INTO events (source, event_id, received_at, status, next_attempt_at, payload_json)
        VALUES (?, ?, ?, 'pending', ?, ?)
        """,
        (source, event_id, received_at, next_attempt_at, payload_json),
    )
    return int(cur.lastrowid)


def claim_next_event(conn: sqlite3.Connection) -> Event | None:
    now = utc_now_iso()
    conn.execute("BEGIN IMMEDIATE;")
    try:
        row = conn.execute(
            """
            SELECT id, source, event_id, received_at, status, attempt_count, next_attempt_at, payload_json
            FROM events
            WHERE status IN ('pending', 'retry') AND next_attempt_at <= ?
            ORDER BY received_at ASC
            LIMIT 1
            """,
            (now,),
        ).fetchone()
        if row is None:
            conn.execute("COMMIT;")
            return None

        conn.execute(
            """
            UPDATE events
            SET status='processing', processing_started_at=?
            WHERE id=? AND status IN ('pending', 'retry')
            """,
            (now, row["id"]),
        )
        conn.execute("COMMIT;")

        payload = json.loads(row["payload_json"])
        return Event(
            id=int(row["id"]),
            source=str(row["source"]),
            event_id=row["event_id"],
            received_at=str(row["received_at"]),
            status=str(row["status"]),
            attempt_count=int(row["attempt_count"]),
            next_attempt_at=str(row["next_attempt_at"]),
            payload=payload,
        )
    except Exception:
        conn.execute("ROLLBACK;")
        raise


def mark_done(conn: sqlite3.Connection, *, event_id: int, result: dict[str, Any]) -> None:
    now = utc_now_iso()
    result_json = json.dumps(result, separators=(",", ":"), ensure_ascii=False)
    conn.execute(
        """
        UPDATE events
        SET status='done', processed_at=?, result_json=?, last_error=NULL
        WHERE id=?
        """,
        (now, result_json, event_id),
    )


def mark_retry(
    conn: sqlite3.Connection,
    *,
    event_id: int,
    attempt_count: int,
    next_attempt_at: str,
    error: str,
) -> None:
    conn.execute(
        """
        UPDATE events
        SET status='retry', attempt_count=?, next_attempt_at=?, last_error=?
        WHERE id=?
        """,
        (attempt_count, next_attempt_at, error, event_id),
    )


def mark_error(conn: sqlite3.Connection, *, event_id: int, attempt_count: int, error: str) -> None:
    now = utc_now_iso()
    conn.execute(
        """
        UPDATE events
        SET status='error', attempt_count=?, processed_at=?, last_error=?
        WHERE id=?
        """,
        (attempt_count, now, error, event_id),
    )


def get_event_row(conn: sqlite3.Connection, *, event_row_id: int) -> dict[str, Any] | None:
    row = conn.execute(
        """
        SELECT id, source, event_id, received_at, status, attempt_count, next_attempt_at, processing_started_at, processed_at,
               payload_json, result_json, last_error
        FROM events
        WHERE id = ?
        """,
        (event_row_id,),
    ).fetchone()
    return dict(row) if row is not None else None


def list_action_runs_for_event(conn: sqlite3.Connection, *, event_row_id: int, limit: int = 20) -> list[dict[str, Any]]:
    rows = conn.execute(
        """
        SELECT id, event_row_id, started_at, finished_at, status, provider, action, handler_mode, handler_target, input_json, output_json, error
        FROM action_runs
        WHERE event_row_id = ?
        ORDER BY id DESC
        LIMIT ?
        """,
        (event_row_id, int(limit)),
    ).fetchall()
    return [dict(r) for r in rows]
