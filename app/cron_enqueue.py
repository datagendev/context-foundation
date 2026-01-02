from __future__ import annotations

import argparse
import os
from datetime import datetime, timezone

from .db import enqueue_event, init_db, open_db
from .settings import get_settings


DEFAULT_DB_PATH = get_settings().app_db_path


def main() -> None:
    parser = argparse.ArgumentParser(description="Enqueue a scheduled (cron) job into the same event queue.")
    parser.add_argument("--db", default=DEFAULT_DB_PATH)
    parser.add_argument("--job", required=True, help="Job name, e.g. daily-digest, pipeline-sweep")
    args = parser.parse_args()

    db_dir = os.path.dirname(args.db)
    if db_dir:
        os.makedirs(db_dir, exist_ok=True)
    conn = open_db(args.db)
    init_db(conn)

    now = datetime.now(timezone.utc).replace(microsecond=0)
    event_id = f"cron:{args.job}:{now.isoformat()}"
    row_id = enqueue_event(conn, source="cron", event_id=event_id, payload={"job": args.job, "scheduled_at": now.isoformat()})
    print(f"queued row_id={row_id} event_id={event_id}")


if __name__ == "__main__":
    main()
