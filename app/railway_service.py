from __future__ import annotations

import os
import threading

import uvicorn

from .config import apply_config, load_config
from .db import init_db, open_db
from .http_server import create_app
from .settings import get_settings
from .worker import run_worker


def main() -> None:
    settings = get_settings()
    host = settings.host or "0.0.0.0"
    port = settings.port
    db_path = settings.app_db_path

    db_dir = os.path.dirname(db_path)
    if db_dir:
        os.makedirs(db_dir, exist_ok=True)
    conn = open_db(db_path)
    try:
        init_db(conn)
        cfg = load_config()
        if cfg is not None:
            apply_config(conn, cfg)
    finally:
        conn.close()

    stop_event = threading.Event()

    worker_thread = threading.Thread(
        target=run_worker,
        kwargs={
            "db_path": db_path,
            "poll_interval": settings.worker_poll_interval,
            "run_once": False,
            "max_attempts": settings.worker_max_attempts,
            "stop_event": stop_event,
        },
        daemon=True,
        name="worker",
    )
    worker_thread.start()

    app = create_app(db_path=db_path, bootstrap=False, settings=settings)
    server = uvicorn.Server(uvicorn.Config(app, host=host, port=port, access_log=False))
    try:
        server.run()
    finally:
        stop_event.set()


if __name__ == "__main__":
    main()
