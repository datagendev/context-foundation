#!/usr/bin/env python3
"""
OpenAI Deep Research - Submit research queries and poll for results.

Uses OpenAI's Responses API with background mode for long-running deep research tasks.

Documentation:
  - https://platform.openai.com/docs/guides/deep-research
  - https://platform.openai.com/docs/guides/background
  - https://cookbook.openai.com/examples/deep_research_api/introduction_to_deep_research_api

Models available:
  - o3-deep-research-2025-06-26 (default, higher quality, $10/$40 per 1M tokens in/out)
  - o4-mini-deep-research-2025-06-26 (faster, lower cost, $2/$8 per 1M tokens in/out)

How it works:
  1. Submit query with background=True to /v1/responses endpoint
  2. Immediately receive { id, status: "queued" } - no output yet
  3. Poll with responses.retrieve(id) while status is "queued" or "in_progress"
  4. Once status reaches terminal state, output is available

Requirements:
  - OPENAI_API_KEY environment variable (or in .env file)
  - background mode requires store=True (stateless requests not supported)

Examples:
  # Submit and poll for results
  uv run python integration/openai-deep-research.py --query "What are the latest trends in AI agents?"

  # Use faster/cheaper model
  uv run python integration/openai-deep-research.py --query "Analyze the CRM market" --model o4-mini-deep-research-2025-06-26

  # Submit without polling (get ID for later)
  uv run python integration/openai-deep-research.py --query "Deep analysis of..." --no-poll

  # Resume polling an existing request
  uv run python integration/openai-deep-research.py --poll-id resp_abc123
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from time import sleep
from typing import Any

from dotenv import load_dotenv

try:
    from openai import OpenAI
except ImportError:
    print("Error: openai package not installed. Run: uv add openai")
    sys.exit(1)


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def _safe_write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(content, encoding="utf-8")
    tmp.replace(path)


def _safe_write_json(path: Path, data: Any) -> None:
    _safe_write(path, json.dumps(data, indent=2, ensure_ascii=False) + "\n")


def _generate_output_path(output_dir: Path, query: str) -> Path:
    """Generate a unique output path based on timestamp and query slug."""
    timestamp = datetime.now(tz=timezone.utc).strftime("%Y-%m-%dT%H%M%SZ")
    slug = "".join(ch if ch.isalnum() else "-" for ch in query[:50]).strip("-").lower()
    while "--" in slug:
        slug = slug.replace("--", "-")
    return output_dir / f"research_{timestamp}_{slug}.json"


def submit_deep_research(
    client: OpenAI,
    query: str,
    model: str = "o3-deep-research-2025-06-26",
    stream: bool = False,
) -> Any:
    """Submit a deep research query in background mode."""
    print(f"Submitting deep research query...")
    print(f"  Model: {model}")
    print(f"  Query: {query[:100]}{'...' if len(query) > 100 else ''}")
    print()

    response = client.responses.create(
        model=model,
        input=query,
        background=True,
        store=True,  # Required for background mode
        stream=stream,
        tools=[{"type": "web_search_preview"}],  # Required for deep research
    )

    print(f"Response ID: {response.id}")
    print(f"Initial status: {response.status}")
    return response


def poll_for_results(
    client: OpenAI,
    response_id: str,
    poll_interval: float = 5.0,
    max_wait: float = 3600.0,  # 1 hour default max
    verbose: bool = True,
) -> Any:
    """Poll for results until completion or timeout."""
    elapsed = 0.0
    last_status = None

    while elapsed < max_wait:
        response = client.responses.retrieve(response_id)
        status = response.status

        if status != last_status:
            if verbose:
                print(f"[{elapsed:.0f}s] Status: {status}")
            last_status = status

        # Check for terminal states
        if status not in {"queued", "in_progress"}:
            return response

        sleep(poll_interval)
        elapsed += poll_interval

    raise TimeoutError(f"Research did not complete within {max_wait}s")


def extract_output(response: Any) -> dict[str, Any]:
    """Extract the output from a completed response."""
    result: dict[str, Any] = {
        "id": response.id,
        "status": response.status,
        "model": response.model,
        "created_at": getattr(response, "created_at", None),
    }

    # Try to get the output text
    if hasattr(response, "output_text") and response.output_text:
        result["output_text"] = response.output_text
    elif hasattr(response, "output") and response.output:
        result["output"] = response.output

    # Include usage if available
    if hasattr(response, "usage") and response.usage:
        result["usage"] = {
            "input_tokens": getattr(response.usage, "input_tokens", None),
            "output_tokens": getattr(response.usage, "output_tokens", None),
            "total_tokens": getattr(response.usage, "total_tokens", None),
        }

    return result


def main() -> int:
    load_dotenv(_repo_root() / ".env")

    parser = argparse.ArgumentParser(
        description="Submit deep research queries to OpenAI and poll for results."
    )
    parser.add_argument(
        "--query",
        type=str,
        default="",
        help="Research query to submit.",
    )
    parser.add_argument(
        "--poll-id",
        type=str,
        default="",
        help="Response ID to poll (resume an existing query).",
    )
    parser.add_argument(
        "--model",
        type=str,
        default="o3-deep-research-2025-06-26",
        choices=["o3-deep-research-2025-06-26", "o4-mini-deep-research-2025-06-26"],
        help="Deep research model to use.",
    )
    parser.add_argument(
        "--poll-interval",
        type=float,
        default=5.0,
        help="Seconds between status checks (default: 5).",
    )
    parser.add_argument(
        "--max-wait",
        type=float,
        default=3600.0,
        help="Maximum seconds to wait for completion (default: 3600).",
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default="research-outputs",
        help="Directory to save results (default: research-outputs).",
    )
    parser.add_argument(
        "--no-poll",
        action="store_true",
        help="Submit query but don't poll for results (just print response ID).",
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Minimal output (just final result).",
    )
    args = parser.parse_args()

    if not args.query and not args.poll_id:
        parser.error("Provide either --query or --poll-id")

    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        print("Error: OPENAI_API_KEY environment variable not set")
        return 1

    client = OpenAI(api_key=api_key)
    output_dir = (_repo_root() / args.output_dir).resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    verbose = not args.quiet

    try:
        if args.poll_id:
            # Resume polling an existing response
            if verbose:
                print(f"Resuming poll for response: {args.poll_id}")
            response = poll_for_results(
                client,
                args.poll_id,
                poll_interval=args.poll_interval,
                max_wait=args.max_wait,
                verbose=verbose,
            )
            query_for_path = args.poll_id
        else:
            # Submit new query
            response = submit_deep_research(
                client,
                args.query,
                model=args.model,
            )

            if args.no_poll:
                print(f"\nResponse submitted. Poll later with:")
                print(f"  --poll-id {response.id}")
                return 0

            if verbose:
                print(f"\nPolling for results (interval: {args.poll_interval}s, max: {args.max_wait}s)...")
                print()

            response = poll_for_results(
                client,
                response.id,
                poll_interval=args.poll_interval,
                max_wait=args.max_wait,
                verbose=verbose,
            )
            query_for_path = args.query

        # Extract and save results
        result = extract_output(response)
        result["query"] = args.query or args.poll_id
        result["completed_at"] = datetime.now(tz=timezone.utc).isoformat()

        output_path = _generate_output_path(output_dir, query_for_path)
        _safe_write_json(output_path, result)

        if verbose:
            print(f"\nFinal status: {result['status']}")
            print(f"Results saved to: {output_path}")

        # Print output text if available
        if "output_text" in result:
            print("\n" + "=" * 60)
            print("RESEARCH OUTPUT:")
            print("=" * 60)
            print(result["output_text"])
        elif "output" in result:
            print("\n" + "=" * 60)
            print("RESEARCH OUTPUT:")
            print("=" * 60)
            print(json.dumps(result["output"], indent=2))

        return 0 if result["status"] == "completed" else 1

    except TimeoutError as e:
        print(f"Error: {e}")
        return 2
    except Exception as e:
        print(f"Error: {type(e).__name__}: {e}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
