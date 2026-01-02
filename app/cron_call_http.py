from __future__ import annotations

import argparse
import urllib.parse
import urllib.request

from .settings import get_settings


def main() -> None:
    settings = get_settings()
    parser = argparse.ArgumentParser(description="Railway cron helper: call the API to enqueue a scheduled job.")
    parser.add_argument("--job", required=True)
    parser.add_argument("--api-base-url", default=settings.api_base_url)
    args = parser.parse_args()

    if not args.api_base_url:
        raise SystemExit("Missing API_BASE_URL (e.g. https://your-service.up.railway.app)")

    base = args.api_base_url.rstrip("/")
    url = f"{base}/cron/enqueue?{urllib.parse.urlencode({'job': args.job})}"

    req = urllib.request.Request(url, method="POST")
    if settings.cron_secret:
        req.add_header("X-Cron-Secret", settings.cron_secret)

    with urllib.request.urlopen(req, timeout=30) as resp:  # noqa: S310
        body = resp.read().decode("utf-8", errors="replace")
        print(body)


if __name__ == "__main__":
    main()
