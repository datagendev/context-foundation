from __future__ import annotations

import asyncio
import json
from pathlib import Path
from typing import Any

from .settings import get_settings


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def run_structured_json_schema(
    *,
    system_prompt: str | None,
    prompt: str,
    json_schema: dict[str, Any],
) -> dict[str, Any]:
    from claude_agent_sdk import query
    from claude_agent_sdk.types import ClaudeAgentOptions, ResultMessage

    async def _run() -> Any:
        settings = get_settings()

        # Configure MCP servers if DataGen API key is available
        mcp_servers = []
        if settings.datagen_api_key:
            mcp_servers.append({
                "name": "datagen",
                "transport": {
                    "type": "http",
                    "url": settings.datagen_mcp_url,
                    "headers": {
                        "x-api-key": settings.datagen_api_key,
                    },
                },
            })

        opts = ClaudeAgentOptions(
            system_prompt=system_prompt,
            cwd=str(_repo_root()),
            permission_mode=settings.claude_agent_permission_mode,
            model=settings.claude_agent_model,
            output_format={"type": "json_schema", "schema": json_schema},
            max_turns=settings.claude_agent_max_turns,
            mcp_servers=mcp_servers if mcp_servers else None,
        )

        final: Any = None
        async for msg in query(prompt=prompt, options=opts):
            if isinstance(msg, ResultMessage):
                if msg.structured_output is not None:
                    final = msg.structured_output
                elif msg.result is not None:
                    final = msg.result
        return final

    timeout_seconds = get_settings().claude_agent_timeout_seconds
    try:
        out = asyncio.run(asyncio.wait_for(_run(), timeout=timeout_seconds))
    except asyncio.TimeoutError as e:
        raise RuntimeError(f"Claude Agent SDK timed out after {timeout_seconds}s") from e
    if out is None:
        return {"error": "no_result"}
    if isinstance(out, dict):
        return out
    if isinstance(out, str):
        try:
            parsed = json.loads(out)
            if isinstance(parsed, dict):
                return parsed
            return {"result": parsed}
        except json.JSONDecodeError:
            return {"raw_result": out}
    return {"result": out}
