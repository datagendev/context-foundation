import asyncio
import os
import json
from pathlib import Path
import unittest


class TestClaudeAgentSdkIntegration(unittest.IsolatedAsyncioTestCase):
    async def test_claude_reads_repo_file(self) -> None:
        if os.getenv("RUN_CLAUDE_AGENT_SDK_TESTS", "").strip() not in {"1", "true", "yes"}:
            self.skipTest("Set RUN_CLAUDE_AGENT_SDK_TESTS=1 to enable this integration test.")

        repo_root = Path(__file__).resolve().parents[1]

        from claude_agent_sdk import query
        from claude_agent_sdk.types import ClaudeAgentOptions, ResultMessage

        schema = {
            "type": "object",
            "additionalProperties": False,
            "properties": {"project_name": {"type": "string"}},
            "required": ["project_name"],
        }

        prompt = (
            "Read the file `pyproject.toml` in the current working directory.\n"
            "Find `[project].name` and return it.\n"
            "Return ONLY valid JSON matching the schema."
        )

        opts = ClaudeAgentOptions(
            cwd=str(repo_root),
            permission_mode=os.getenv("CLAUDE_AGENT_PERMISSION_MODE", "bypassPermissions"),
            output_format={"type": "json_schema", "schema": schema},
            max_turns=int(os.getenv("CLAUDE_AGENT_MAX_TURNS", "6")),
            model=os.getenv("CLAUDE_AGENT_MODEL") or None,
        )

        async def _run() -> dict:
            final = None
            async for msg in query(prompt=prompt, options=opts):
                if isinstance(msg, ResultMessage):
                    final = msg.structured_output or msg.result
            if not isinstance(final, dict):
                raise AssertionError(f"Expected structured dict result, got: {type(final)} {final!r}")
            return final

        result = await asyncio.wait_for(_run(), timeout=float(os.getenv("CLAUDE_AGENT_TEST_TIMEOUT", "120")))
        if os.getenv("SHOW_CLAUDE_AGENT_OUTPUT", "").strip() in {"1", "true", "yes"}:
            print("Claude Agent SDK structured output:", json.dumps(result, ensure_ascii=False))
        self.assertEqual(result.get("project_name"), "context-foundation")


if __name__ == "__main__":
    unittest.main()
