from __future__ import annotations

import argparse
import threading
import time
import traceback
from datetime import datetime, timedelta, timezone

from .db import claim_next_event, init_db, mark_done, mark_error, mark_retry, open_db
from .processor import process_event
from .settings import get_settings


DEFAULT_DB_PATH = get_settings().app_db_path


def _utc_now() -> datetime:
    return datetime.now(timezone.utc).replace(microsecond=0)


def _next_attempt_time(attempt_count: int) -> str:
    delay_seconds = min(60, 2 ** min(attempt_count, 6))
    return (_utc_now() + timedelta(seconds=delay_seconds)).isoformat()


def run_worker(
    *,
    db_path: str,
    poll_interval: float = 1.0,
    run_once: bool = False,
    max_attempts: int = 8,
    stop_event: threading.Event | None = None,
) -> None:
    conn = open_db(db_path)
    init_db(conn)

    while True:
        if stop_event is not None and stop_event.is_set():
            return

        event = claim_next_event(conn)
        if event is None:
            if run_once:
                return
            time.sleep(poll_interval)
            continue

        try:
            result = process_event(conn, event)
            mark_done(conn, event_id=event.id, result=result)
            print(f"[done] id={event.id} source={event.source} event_id={event.event_id}")
        except Exception as e:
            new_attempt_count = event.attempt_count + 1
            err = f"{type(e).__name__}: {e}\n{traceback.format_exc(limit=5)}"

            if new_attempt_count >= max_attempts:
                mark_error(conn, event_id=event.id, attempt_count=new_attempt_count, error=err)
                print(f"[error] id={event.id} source={event.source} attempts={new_attempt_count}")
            else:
                next_attempt_at = _next_attempt_time(new_attempt_count)
                mark_retry(
                    conn,
                    event_id=event.id,
                    attempt_count=new_attempt_count,
                    next_attempt_at=next_attempt_at,
                    error=err,
                )
                print(f"[retry] id={event.id} source={event.source} attempts={new_attempt_count} next={next_attempt_at}")

        if run_once:
            return


def main() -> None:
    parser = argparse.ArgumentParser(description="Worker loop (claims queued events and processes them).")
    parser.add_argument("--db", default=DEFAULT_DB_PATH)
    parser.add_argument("--poll-interval", type=float, default=1.0)
    parser.add_argument("--run-once", action="store_true")
    parser.add_argument("--max-attempts", type=int, default=8)
    args = parser.parse_args()

    run_worker(
        db_path=args.db,
        poll_interval=args.poll_interval,
        run_once=args.run_once,
        max_attempts=args.max_attempts,
    )


if __name__ == "__main__":
    main()
