#!/usr/bin/env python3
"""
Run Parallel FindAll jobs (in parallel) and write results into ./integration/.

Usage:
  PARALLEL_API_KEY=... python3 integration/findall_web_research.py
  PARALLEL_API_KEY=... python3 integration/findall_web_research.py --objective "FindAll …" --objective "FindAll …"
  PARALLEL_API_KEY=... python3 integration/findall_web_research.py --generator core --match-limit 25 --max-workers 3
"""

from __future__ import annotations

import argparse
import json
import os
import re
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import httpx
from dotenv import load_dotenv


DEFAULT_BETA_HEADER = "findall-2025-09-15"
DEFAULT_BASE_URL = "https://api.parallel.ai"


def _slugify(text: str, max_len: int = 80) -> str:
    cleaned = re.sub(r"[^a-zA-Z0-9]+", "-", text.strip()).strip("-").lower()
    if not cleaned:
        cleaned = "findall"
    return cleaned[:max_len].rstrip("-")


def _safe_write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    tmp.replace(path)


def _candidate_md(candidate: dict[str, Any]) -> str:
    name = candidate.get("name") or candidate.get("candidate_id") or "Unknown"
    url = candidate.get("url")
    description = candidate.get("description")
    parts: list[str] = [f"### {name}"]
    if url:
        parts.append(f"- URL: {url}")
    if description:
        parts.append(f"- Description: {description}")

    basis = candidate.get("basis") or []
    if isinstance(basis, list) and basis:
        parts.append("- Evidence:")
        for item in basis:
            field = item.get("field", "field")
            confidence = item.get("confidence")
            reasoning = item.get("reasoning")
            line = f"  - {field}"
            if confidence:
                line += f" ({confidence})"
            parts.append(line)
            if reasoning:
                parts.append(f"    - Reasoning: {reasoning}")
            citations = item.get("citations") or []
            if isinstance(citations, list) and citations:
                for c in citations[:5]:
                    c_title = c.get("title") or "Source"
                    c_url = c.get("url")
                    if c_url:
                        parts.append(f"    - Source: {c_title} — {c_url}")
    return "\n".join(parts).strip() + "\n"


def _result_to_markdown(result: dict[str, Any]) -> str:
    objective = result.get("objective") or "FindAll Results"
    findall_id = result.get("findall_id")
    status = (result.get("status") or {}).get("status")
    metrics = (result.get("status") or {}).get("metrics") or {}
    candidates = result.get("candidates") or []

    lines: list[str] = [f"# {objective}", ""]
    if findall_id:
        lines.append(f"- findall_id: `{findall_id}`")
    if status:
        lines.append(f"- status: `{status}`")
    if metrics:
        metrics_str = ", ".join(f"{k}={v}" for k, v in metrics.items())
        lines.append(f"- metrics: {metrics_str}")
    lines.append("")
    lines.append("## Candidates")
    lines.append("")

    if not isinstance(candidates, list) or not candidates:
        lines.append("_No candidates returned._\n")
        return "\n".join(lines)

    for cand in candidates:
        if isinstance(cand, dict):
            lines.append(_candidate_md(cand))
        else:
            lines.append(f"### {cand}\n")
    return "\n".join(lines).rstrip() + "\n"


@dataclass(frozen=True)
class FindAllConfig:
    api_key: str
    base_url: str
    beta_header: str
    generator: str
    match_limit: int
    poll_interval_s: float
    poll_timeout_s: float


def _headers(cfg: FindAllConfig) -> dict[str, str]:
    return {
        "x-api-key": cfg.api_key,
        "parallel-beta": cfg.beta_header,
        "content-type": "application/json",
    }


def run_findall_objective(cfg: FindAllConfig, objective: str) -> dict[str, Any]:
    timeout = httpx.Timeout(60.0, connect=30.0)
    with httpx.Client(base_url=cfg.base_url, headers=_headers(cfg), timeout=timeout) as client:
        ingest = client.post("/v1beta/findall/ingest", json={"objective": objective})
        ingest.raise_for_status()
        schema = ingest.json()

        run_payload = {
            "objective": schema.get("objective", objective),
            "entity_type": schema.get("entity_type"),
            "match_conditions": schema.get("match_conditions", []),
            "generator": cfg.generator,
            "match_limit": cfg.match_limit,
        }
        run = client.post("/v1beta/findall/runs", json=run_payload)
        run.raise_for_status()
        findall_id = run.json().get("findall_id")
        if not findall_id:
            raise RuntimeError(f"Create run response missing findall_id: {run.text}")

        deadline = time.time() + cfg.poll_timeout_s
        last_status: dict[str, Any] | None = None
        while time.time() < deadline:
            poll = client.get(f"/v1beta/findall/runs/{findall_id}")
            poll.raise_for_status()
            last_status = poll.json()
            status_obj = last_status.get("status") or {}
            if status_obj.get("status") == "completed" or status_obj.get("is_active") is False:
                break
            time.sleep(cfg.poll_interval_s)

        if not last_status:
            raise RuntimeError("Polling did not return any status payload.")

        result = client.get(f"/v1beta/findall/runs/{findall_id}/result")
        result.raise_for_status()
        return result.json()


def main() -> int:
    parser = argparse.ArgumentParser(description="Parallel FindAll runner for web research integrations.")
    parser.add_argument(
        "--objective",
        action="append",
        default=[],
        help="Natural-language FindAll objective (repeatable).",
    )
    parser.add_argument("--base-url", default=DEFAULT_BASE_URL, help="Parallel API base URL.")
    parser.add_argument("--beta-header", default=DEFAULT_BETA_HEADER, help="Value for the parallel-beta header.")
    parser.add_argument("--generator", default="core", choices=["base", "core", "pro"], help="FindAll generator tier.")
    parser.add_argument("--match-limit", type=int, default=25, help="Max matched candidates to return.")
    parser.add_argument("--max-workers", type=int, default=3, help="Max parallel FindAll runs.")
    parser.add_argument("--poll-interval", type=float, default=2.0, help="Seconds between status polls.")
    parser.add_argument("--poll-timeout", type=float, default=600.0, help="Max seconds to wait per run.")
    parser.add_argument(
        "--out-dir",
        default=str(Path(__file__).resolve().parent),
        help="Directory to write outputs (defaults to ./integration).",
    )
    args = parser.parse_args()

    load_dotenv(Path(__file__).resolve().parents[1] / ".env")

    api_key = os.environ.get("PARALLEL_API_KEY", "").strip()
    if not api_key:
        raise SystemExit("Missing PARALLEL_API_KEY env var.")

    base_url = os.environ.get("PARALLEL_BASE_URL", args.base_url)
    beta_header = os.environ.get("PARALLEL_BETA_HEADER", args.beta_header)
    generator = os.environ.get("FINDALL_GENERATOR", args.generator)
    match_limit = int(os.environ.get("FINDALL_MATCH_LIMIT", str(args.match_limit)))
    max_workers = int(os.environ.get("FINDALL_MAX_WORKERS", str(args.max_workers)))
    poll_interval = float(os.environ.get("FINDALL_POLL_INTERVAL", str(args.poll_interval)))
    poll_timeout = float(os.environ.get("FINDALL_POLL_TIMEOUT", str(args.poll_timeout)))

    objectives = args.objective or [
        "FindAll web research API providers that offer search and citation-backed results for LLM research. "
        "Include official docs/pricing links in citations."
    ]

    cfg = FindAllConfig(
        api_key=api_key,
        base_url=base_url,
        beta_header=beta_header,
        generator=generator,
        match_limit=match_limit,
        poll_interval_s=poll_interval,
        poll_timeout_s=poll_timeout,
    )

    out_dir = Path(args.out_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    jobs: dict[str, str] = {}
    for obj in objectives:
        slug = _slugify(obj)
        # Avoid collisions when objectives are similar.
        while slug in jobs:
            slug = f"{slug}-x"
        jobs[slug] = obj

    results: dict[str, str] = {}
    with ThreadPoolExecutor(max_workers=max(1, max_workers)) as pool:
        future_to_slug = {pool.submit(run_findall_objective, cfg, obj): slug for slug, obj in jobs.items()}
        for fut in as_completed(future_to_slug):
            slug = future_to_slug[fut]
            try:
                payload = fut.result()
                _safe_write_json(out_dir / f"{slug}.json", payload)
                (out_dir / f"{slug}.md").write_text(_result_to_markdown(payload), encoding="utf-8")
                results[slug] = "ok"
            except Exception as e:  # noqa: BLE001
                (out_dir / f"{slug}.error.txt").write_text(str(e).strip() + "\n", encoding="utf-8")
                results[slug] = "error"

    summary = {"out_dir": str(out_dir), "results": results, "objectives": jobs}
    _safe_write_json(out_dir / "run_summary.json", summary)
    return 0 if all(v == "ok" for v in results.values()) else 2


if __name__ == "__main__":
    raise SystemExit(main())
