#!/usr/bin/env python3
"""
Download a Fireflies transcript to a specified directory.

Usage:
    python integration/download_fireflies_transcript.py [--transcript-id ID] [--mode fetch|transcript|summary] [--output-path /tmp/transcript]

Example:
    python integration/download_fireflies_transcript.py --transcript-id 01KCAFG6EPCT6FD06XCNRJEFRK --output-path ./transcripts
"""

import argparse
from datetime import datetime, timezone
import re
from pathlib import Path

from datagen_sdk.client import DatagenClient
from dotenv import load_dotenv


def _parse_transcript_id_from_text(text: str) -> str | None:
    match = re.search(r"\bid:\s*([A-Za-z0-9_-]+)\b", text, flags=re.IGNORECASE)
    return match.group(1) if match else None


def _parse_title_from_text(text: str) -> str | None:
    match = re.search(r"\btitle:\s*(.+?)(?:\n|$)", text, flags=re.IGNORECASE)
    return match.group(1).strip() if match else None


def _parse_date_from_text(text: str) -> str | None:
    # Supports formats like:
    # - dateString: "2025-12-13T04:30:00.000Z"
    # - DateString: 2025-12-13T04:30:00.000Z
    match = re.search(
        r"\bdatestring:\s*\"?(\d{4}-\d{2}-\d{2})",
        text,
        flags=re.IGNORECASE,
    )
    return match.group(1) if match else None


def main():
    parser = argparse.ArgumentParser(
        description="Download a Fireflies transcript (by ID) or the latest transcript."
    )
    parser.add_argument(
        "--transcript-id",
        type=str,
        default="",
        help="Fireflies transcript ID. If omitted, downloads the latest transcript.",
    )
    parser.add_argument(
        "--mode",
        type=str,
        default="fetch",
        choices=["fetch", "transcript", "summary"],
        help="Download mode: fetch (complete transcript + insights), transcript (transcript content), summary (summary only). Default: fetch.",
    )
    parser.add_argument(
        "--output-path",
        type=str,
        default="/tmp/transcript",
        help="Directory where transcript will be saved (default: /tmp/transcript)",
    )
    args = parser.parse_args()

    load_dotenv()
    client = DatagenClient()

    transcript_id = args.transcript_id.strip()
    title = "untitled"
    date_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    if transcript_id:
        print(f"Using provided transcript ID: {transcript_id}")
    else:
        print("Fetching recent transcripts from Fireflies...")
        result = client.execute_tool("mcp_Fireflies_fireflies_get_transcripts", {})

        first = result[0] if isinstance(result, list) and result else result

        if isinstance(first, str):
            transcript_id = _parse_transcript_id_from_text(first) or ""
            title = _parse_title_from_text(first) or title
            date_str = _parse_date_from_text(first) or date_str
        elif isinstance(first, dict):
            transcript_id = str(first.get("id") or "")
            title = str(first.get("title") or title)
            date_str = str(first.get("dateString") or date_str).split("T")[0]
        else:
            transcript_id = _parse_transcript_id_from_text(str(first)) or ""

        if not transcript_id:
            print("Error: No transcript ID found (provide --transcript-id to bypass).")
            return

        print(f"Found latest transcript: {title} ({date_str})")

    print(f"Transcript ID: {transcript_id}")

    # Fetch full transcript
    if args.mode == "fetch":
        print("Downloading complete transcript (fetch)...")
        transcript_data = client.execute_tool(
            "mcp_Fireflies_fireflies_fetch", {"id": transcript_id}
        )
    elif args.mode == "summary":
        print("Downloading summary...")
        transcript_data = client.execute_tool(
            "mcp_Fireflies_fireflies_get_summary", {"transcriptId": transcript_id}
        )
    else:
        print("Downloading transcript content...")
        transcript_data = client.execute_tool(
            "mcp_Fireflies_fireflies_get_transcript", {"transcriptId": transcript_id}
        )

    # Create output directory
    output_dir = Path(args.output_path)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Generate filename
    filename = output_dir / f"{transcript_id}.md"

    # Convert to markdown with front matter
    transcript_str = (
        str(transcript_data[0]) if isinstance(transcript_data, list) else str(transcript_data)
    )

    if title == "untitled":
        title = _parse_title_from_text(transcript_str) or title
    date_str = _parse_date_from_text(transcript_str) or date_str

    # Build markdown content
    markdown_content = f"""---
title: {title}
transcript_id: {transcript_id}
date: {date_str}
source: Fireflies
download_mode: {args.mode}
---

# {title}

**Date**: {date_str}
**Transcript ID**: {transcript_id}
**Mode**: {args.mode}

## Raw Transcript Data

```
{transcript_str}
```
"""

    # Save transcript as markdown
    with open(filename, "w") as f:
        f.write(markdown_content)

    print(f"\nSuccess!")
    print(f"File saved to: {filename}")
    print(f"File size: {filename.stat().st_size} bytes")


if __name__ == "__main__":
    main()
