#!/usr/bin/env python3
"""
Create a sitemap-like URL inventory for one or more company websites using:
  - DataGen Python SDK (datagen_sdk)
  - Firecrawl MCP tool: mcp_Firecrawl_firecrawl_map

Prereqs:
  - `.venv` with deps installed (see pyproject.toml / uv.lock)
  - `DATAGEN_API_KEY` set (or in repo-root `.env`)

Examples:
  python3 integration/company-site-map.py --url https://scrunch.com
  python3 integration/company-site-map.py --url https://scrunch.com --url https://example.com --max-workers 2
  python3 integration/company-site-map.py --urls-file urls.txt --sitemap include --limit 200
"""

from __future__ import annotations

import argparse
import json
import os
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


def _slug_host(url: str) -> str:
    host = urlparse(url).netloc or urlparse("https://" + url).netloc
    host = host.lower().strip()
    return host.replace(":", "_") if host else "site"


def _safe_write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(content, encoding="utf-8")
    tmp.replace(path)


def _safe_write_json(path: Path, data: Any) -> None:
    _safe_write(path, json.dumps(data, indent=2, ensure_ascii=False) + "\n")


def _as_url_list(result: Any) -> list[str]:
    if isinstance(result, list):
        # Sometimes wrappers return a list of URLs directly, or a list of objects.
        urls: list[str] = []
        for item in result:
            urls.extend(_as_url_list(item))
        return urls

    if isinstance(result, dict):
        # Or { "links": [...] }
        links = result.get("links")
        if isinstance(links, list):
            urls: list[str] = []
            for item in links:
                if isinstance(item, str):
                    urls.append(item)
                elif isinstance(item, dict) and isinstance(item.get("url"), str):
                    urls.append(item["url"])
            return urls

    if isinstance(result, str):
        # DataGen often returns tool output as a stringified JSON payload.
        try:
            parsed = json.loads(result)
        except json.JSONDecodeError:
            return []
        return _as_url_list(parsed)

    return []


def _to_markdown(url: str, urls: list[str], meta: dict[str, Any]) -> str:
    lines: list[str] = [
        f"# Company Site Map: {_slug_host(url)}",
        "",
        f"- source_url: `{url}`",
        f"- discovered_urls: `{len(urls)}`",
        f"- generated_at_utc: `{meta['generated_at_utc']}`",
        "",
        "## Parameters",
        "",
        "```json",
        json.dumps(meta["parameters"], indent=2, ensure_ascii=False),
        "```",
        "",
        "## URLs",
        "",
    ]
    for u in urls:
        lines.append(f"- {u}")
    return "\n".join(lines).rstrip() + "\n"


@dataclass(frozen=True)
class Job:
    source_url: str
    params: dict[str, Any]


def _run_one(client: DatagenClient, job: Job) -> dict[str, Any]:
    result = client.execute_tool("mcp_Firecrawl_firecrawl_map", job.params)
    urls = sorted(set(_as_url_list(result)))
    return {"result": result, "urls": urls}


def main() -> int:
    load_dotenv(_repo_root() / ".env")

    parser = argparse.ArgumentParser(description="Map company websites via Firecrawl map (through DataGen SDK).")
    parser.add_argument("--url", action="append", default=[], help="Website URL to map (repeatable).")
    parser.add_argument("--urls-file", type=str, default="", help="Path to a newline-delimited list of URLs.")
    parser.add_argument(
        "--companies-dir",
        type=str,
        default="company",
        help="Root folder where company subfolders are created (e.g. company/scrunch.com/site-map/...).",
    )
    parser.add_argument("--limit", type=int, default=200, help="Max URLs to return (Firecrawl map limit).")
    parser.add_argument("--search", type=str, default="", help="Optional Firecrawl map 'search' filter.")
    parser.add_argument(
        "--sitemap",
        type=str,
        default="include",
        choices=["include", "skip", "only"],
        help="How Firecrawl should use sitemaps.",
    )
    parser.add_argument("--include-subdomains", action="store_true", help="Include subdomains in discovery.")
    parser.add_argument(
        "--no-ignore-query-parameters",
        action="store_true",
        help="Do not ignore query parameters when deduplicating URLs.",
    )
    parser.add_argument("--max-workers", type=int, default=4, help="Parallelism across sites.")
    parser.add_argument("--datagen-base-url", type=str, default="https://api.datagen.dev", help="DataGen API base URL.")
    args = parser.parse_args()

    urls: list[str] = list(args.url)
    if args.urls_file:
        urls_path = Path(args.urls_file)
        urls.extend([line.strip() for line in urls_path.read_text(encoding="utf-8").splitlines() if line.strip()])
    urls = [u for u in urls if u]

    if not urls:
        raise SystemExit("Provide at least one --url (or --urls-file).")

    client = DatagenClient(base_url=args.datagen_base_url)

    companies_dir = (_repo_root() / args.companies_dir).resolve()
    companies_dir.mkdir(parents=True, exist_ok=True)

    common_params: dict[str, Any] = {
        "limit": args.limit,
        "sitemap": args.sitemap,
        "includeSubdomains": bool(args.include_subdomains),
        "ignoreQueryParameters": not bool(args.no_ignore_query_parameters),
    }
    if args.search:
        common_params["search"] = args.search

    jobs: list[Job] = [Job(source_url=u, params={**common_params, "url": u}) for u in urls]

    generated_at = datetime.now(tz=timezone.utc).isoformat(timespec="seconds")
    run_id = datetime.now(tz=timezone.utc).strftime("%Y-%m-%dT%H%M%SZ")
    results: dict[str, str] = {}

    with ThreadPoolExecutor(max_workers=max(1, args.max_workers)) as pool:
        future_to_job = {pool.submit(_run_one, client, job): job for job in jobs}
        for fut in as_completed(future_to_job):
            job = future_to_job[fut]
            host_slug = _slug_host(job.source_url)
            company_dir = companies_dir / host_slug
            (company_dir / "site-map").mkdir(parents=True, exist_ok=True)
            base = company_dir / "site-map" / datetime.now(tz=timezone.utc).date().isoformat()

            try:
                payload = fut.result()
                meta = {
                    "generated_at_utc": generated_at,
                    "source_url": job.source_url,
                    "parameters": job.params,
                    "discovered_url_count": len(payload["urls"]),
                }
                json_out = {
                    "meta": meta,
                    "urls": payload["urls"],
                    "raw_result": payload["result"],
                }
                _safe_write_json(Path(str(base) + ".json"), json_out)
                _safe_write(Path(str(base) + ".md"), _to_markdown(job.source_url, payload["urls"], meta))
                readme_path = company_dir / "README.md"
                if not readme_path.exists():
                    _safe_write(
                        readme_path,
                        "\n".join(
                            [
                                f"# {host_slug}",
                                "",
                                f"- website: `{job.source_url}`",
                                "",
                                "## Contents",
                                "",
                                "- `site-map/`: URL inventories generated via Firecrawl map.",
                                "",
                            ]
                        ),
                    )
                results[job.source_url] = "ok"
                print(f"[ok] {job.source_url} -> {base}.(json|md)")
            except Exception as exc:  # noqa: BLE001
                _safe_write(Path(str(base) + ".error.txt"), f"{type(exc).__name__}: {exc}\n")
                results[job.source_url] = "error"
                print(f"[error] {job.source_url} -> {base}.error.txt")

    _safe_write_json(
        companies_dir / f"site-map-run-summary_{run_id}.json",
        {"generated_at_utc": generated_at, "run_id": run_id, "results": results},
    )
    return 0 if all(v == "ok" for v in results.values()) else 2


if __name__ == "__main__":
    raise SystemExit(main())
