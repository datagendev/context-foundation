#!/usr/bin/env python3
"""
Convert OpenAI deep research JSON outputs to Markdown with YAML frontmatter.

Converts research-outputs/*.json files to markdown with:
- YAML frontmatter containing metadata (query, completed_at, model, id)
- Formatted output_text as markdown body

Examples:
  uv run python integration/convert-research-outputs.py
  uv run python integration/convert-research-outputs.py --output-dir research-markdown
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime
from pathlib import Path


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def _convert_json_to_markdown(json_file: Path, output_file: Path) -> None:
    """Convert a research JSON file to markdown with frontmatter."""
    with open(json_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Extract metadata
    query = data.get("query", "")
    completed_at = data.get("completed_at", "")
    model = data.get("model", "")
    response_id = data.get("id", "")
    output_text = data.get("output_text", "")

    # Parse completed_at to a more readable format
    try:
        dt = datetime.fromisoformat(completed_at.replace("Z", "+00:00"))
        completed_at_formatted = dt.strftime("%Y-%m-%d %H:%M:%S UTC")
    except (ValueError, AttributeError):
        completed_at_formatted = completed_at

    # Create YAML frontmatter
    frontmatter = f"""---
query: {json.dumps(query)}
completed_at: {json.dumps(completed_at_formatted)}
model: {model}
response_id: {response_id}
source_file: {json_file.name}
---
"""

    # Combine frontmatter and output text
    markdown_content = frontmatter + "\n" + output_text.strip() + "\n"

    # Write to output file
    output_file.parent.mkdir(parents=True, exist_ok=True)
    output_file.write_text(markdown_content, encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Convert research JSON outputs to Markdown with YAML frontmatter.")
    parser.add_argument(
        "--research-dir",
        type=str,
        default="research-outputs",
        help="Source directory with research JSON files (default: research-outputs).",
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default="research-markdown",
        help="Output directory for markdown files (default: research-markdown).",
    )
    args = parser.parse_args()

    repo_root = _repo_root()
    research_dir = (repo_root / args.research_dir).resolve()
    output_dir = (repo_root / args.output_dir).resolve()

    if not research_dir.exists():
        print(f"Error: Research directory not found: {research_dir}")
        return 1

    json_files = sorted(research_dir.glob("*.json"))
    if not json_files:
        print(f"No JSON files found in {research_dir}")
        return 1

    output_dir.mkdir(parents=True, exist_ok=True)

    for json_file in json_files:
        output_file = output_dir / json_file.with_suffix(".md").name
        try:
            _convert_json_to_markdown(json_file, output_file)
            print(f"✓ {json_file.name} → {output_file.name}")
        except Exception as e:
            print(f"✗ {json_file.name}: {type(e).__name__}: {e}")
            return 1

    print(f"\nConverted {len(json_files)} research outputs to markdown.")
    print(f"Results saved to: {output_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
