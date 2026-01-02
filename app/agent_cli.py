from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from .claude_agent_sdk_runner import run_structured_json_schema


def main() -> None:
    parser = argparse.ArgumentParser(description="Run an agent prompt (Claude Agent SDK) with JSON stdin and JSON stdout.")
    parser.add_argument("--agent", required=True, help="Path to agent prompt markdown (e.g. .claude/agents/slack-message-sender.md or app/agents/echo.md)")
    args = parser.parse_args()

    agent_path = Path(args.agent).resolve()
    agent_prompt = agent_path.read_text(encoding="utf-8")

    import sys

    raw = sys.stdin.read()

    input_obj: dict[str, Any] = {}
    if raw.strip():
        input_obj = json.loads(raw)

    schema = {
        "type": "object",
        "additionalProperties": True,
    }
    out = run_structured_json_schema(
        system_prompt=agent_prompt,
        prompt=json.dumps(input_obj, ensure_ascii=False),
        json_schema=schema,
    )
    print(json.dumps(out, ensure_ascii=False))


if __name__ == "__main__":
    main()
