#!/usr/bin/env python3
"""
Scrape one or more specific URLs into Markdown and save them under `companies/<domain>/`.

This uses:
  - DataGen Python SDK (datagen_sdk)
  - Firecrawl MCP tool: mcp_Firecrawl_firecrawl_scrape

Examples:
  uv run python integration/company-scrape-url.py --url https://scrunch.com/enterprise
  uv run python integration/company-scrape-url.py --url https://scrunch.com/pricing --only-main-content
  uv run python integration/company-scrape-url.py --urls-file urls.txt --max-workers 4
"""

from __future__ import annotations

import argparse
import hashlib
import json
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

from datagen_sdk.client import DatagenClient
from dotenv import load_dotenv


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def _host(url: str) -> str:
    parsed = urlparse(url)
    return (parsed.netloc or urlparse("https://" + url).netloc).lower().strip()


def _slug_path(url: str) -> str:
    parsed = urlparse(url)
    path = parsed.path.strip("/")
    if not path:
        return "home"
    safe = "".join(ch if ch.isalnum() else "-" for ch in path).strip("-").lower()
    while "--" in safe:
        safe = safe.replace("--", "-")
    return safe or "page"


def _url_id(url: str) -> str:
    return hashlib.sha1(url.encode("utf-8")).hexdigest()[:10]


def _safe_write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(content, encoding="utf-8")
    tmp.replace(path)


def _safe_write_json(path: Path, data: Any) -> None:
    _safe_write(path, json.dumps(data, indent=2, ensure_ascii=False) + "\n")


def _extract_markdown(result: Any) -> str:
    """
    Firecrawl scrape often returns a JSON-ish payload containing markdown.
    We try a few common shapes; fall back to raw string.
    """
    if isinstance(result, list):
        for item in result:
            md = _extract_markdown(item)
            if md.strip():
                return md
        return ""

    if isinstance(result, str):
        try:
            parsed = json.loads(result)
        except json.JSONDecodeError:
            return result
        return _extract_markdown(parsed)

    if isinstance(result, dict):
        for key in ("markdown", "md", "content"):
            val = result.get(key)
            if isinstance(val, str) and val.strip():
                return val
        data = result.get("data")
        if isinstance(data, dict):
            return _extract_markdown(data)

    return ""


@dataclass(frozen=True)
class Job:
    url: str
    params: dict[str, Any]


def _run_one(client: DatagenClient, job: Job) -> dict[str, Any]:
    raw = client.execute_tool("mcp_Firecrawl_firecrawl_scrape", job.params)
    md = _extract_markdown(raw)
    return {"raw": raw, "markdown": md}


def main() -> int:
    load_dotenv(_repo_root() / ".env")

    parser = argparse.ArgumentParser(description="Scrape URLs to Markdown via Firecrawl (through DataGen SDK).")
    parser.add_argument("--url", action="append", default=[], help="URL to scrape (repeatable).")
    parser.add_argument("--urls-file", type=str, default="", help="Path to a newline-delimited list of URLs.")
    parser.add_argument(
        "--companies-dir",
        type=str,
        default="companies",
        help="Root folder where company subfolders are created (e.g. companies/scrunch.com/pages/...).",
    )
    parser.add_argument("--max-workers", type=int, default=4, help="Parallelism across URLs.")
    parser.add_argument("--datagen-base-url", type=str, default="https://api.datagen.dev", help="DataGen API base URL.")

    parser.add_argument("--max-age", type=int, default=172800000, help="Cache maxAge ms (default 2 days).")
    parser.add_argument("--mobile", action="store_true", help="Use mobile user agent.")
    parser.add_argument("--only-main-content", action="store_true", help="Prefer main content only.")
    parser.add_argument("--remove-base64-images", action="store_true", help="Remove base64 images from output.")
    parser.add_argument("--wait-for", type=int, default=0, help="Wait time ms before scraping.")
    args = parser.parse_args()

    urls: list[str] = list(args.url)
    if args.urls_file:
        urls_path = Path(args.urls_file)
        urls.extend([line.strip() for line in urls_path.read_text(encoding="utf-8").splitlines() if line.strip()])
    urls = [u for u in urls if u]
    if not urls:
        raise SystemExit("Provide at least one --url (or --urls-file).")

    companies_dir = (_repo_root() / args.companies_dir).resolve()
    companies_dir.mkdir(parents=True, exist_ok=True)

    client = DatagenClient(base_url=args.datagen_base_url)

    scraped_at = datetime.now(tz=timezone.utc).isoformat(timespec="seconds")
    run_id = datetime.now(tz=timezone.utc).strftime("%Y-%m-%dT%H%M%SZ")

    base_params: dict[str, Any] = {
        "formats": ["markdown"],
        "maxAge": args.max_age,
    }
    if args.mobile:
        base_params["mobile"] = True
    if args.only_main_content:
        base_params["onlyMainContent"] = True
    if args.remove_base64_images:
        base_params["removeBase64Images"] = True
    if args.wait_for > 0:
        base_params["waitFor"] = args.wait_for

    jobs: list[Job] = [Job(url=u, params={**base_params, "url": u}) for u in urls]
    results: dict[str, str] = {}

    with ThreadPoolExecutor(max_workers=max(1, args.max_workers)) as pool:
        future_to_job = {pool.submit(_run_one, client, job): job for job in jobs}
        for fut in as_completed(future_to_job):
            job = future_to_job[fut]
            host = _host(job.url)
            slug = _slug_path(job.url)
            uid = _url_id(job.url)

            company_dir = companies_dir / host
            pages_dir = company_dir / "pages"
            pages_dir.mkdir(parents=True, exist_ok=True)

            base = pages_dir / f"{slug}__{uid}"
            try:
                payload = fut.result()
                md = payload["markdown"] or ""
                if not md.strip():
                    md = f"_No markdown returned for `{job.url}`._\n"

                header = "\n".join(
                    [
                        f"# Page: {slug}",
                        "",
                        f"- source_url: `{job.url}`",
                        f"- scraped_at_utc: `{scraped_at}`",
                        "",
                    ]
                )
                _safe_write(Path(str(base) + ".md"), header + md.rstrip() + "\n")
                _safe_write_json(
                    Path(str(base) + ".json"),
                    {"meta": {"source_url": job.url, "scraped_at_utc": scraped_at, "parameters": job.params}, "raw": payload["raw"]},
                )

                readme_path = company_dir / "README.md"
                if not readme_path.exists():
                    _safe_write(
                        readme_path,
                        "\n".join(
                            [
                                f"# {host}",
                                "",
                                f"- website: `{urlparse(job.url).scheme}://{host}`",
                                "",
                                "## Contents",
                                "",
                                "- `site-map/`: URL inventories generated via Firecrawl map.",
                                "- `pages/`: Markdown scrapes of specific URLs.",
                                "",
                            ]
                        ),
                    )

                results[job.url] = "ok"
                print(f"[ok] {job.url} -> {base}.(md|json)")
            except Exception as exc:  # noqa: BLE001
                _safe_write(Path(str(base) + ".error.txt"), f"{type(exc).__name__}: {exc}\n")
                results[job.url] = "error"
                print(f"[error] {job.url} -> {base}.error.txt")

    _safe_write_json(companies_dir / f"page-scrape-run-summary_{run_id}.json", {"run_id": run_id, "scraped_at_utc": scraped_at, "results": results})
    return 0 if all(v == "ok" for v in results.values()) else 2


if __name__ == "__main__":
    raise SystemExit(main())
