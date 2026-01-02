from __future__ import annotations

import json
import shlex
import subprocess
from typing import Any

from .settings import get_settings


def run_llm(*, prompt: str, input_obj: dict[str, Any]) -> dict[str, Any]:
    settings = get_settings()
    mode = settings.llm_mode.strip().lower()

    if mode in {"noop", "none", ""}:
        return {"mode": "noop", "note": "No LLM configured."}

    if mode == "echo":
        return {"mode": "echo", "prompt": prompt, "input": input_obj}

    if mode == "command":
        cmd = settings.llm_command
        if not cmd:
            raise RuntimeError("LLM_MODE=command requires LLM_COMMAND to be set.")

        argv = shlex.split(cmd)
        stdin_payload = json.dumps(
            {"prompt": prompt, "input": input_obj},
            ensure_ascii=False,
            separators=(",", ":"),
        ).encode("utf-8")

        proc = subprocess.run(
            argv,
            input=stdin_payload,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
        stdout = proc.stdout.decode("utf-8", errors="replace").strip()
        stderr = proc.stderr.decode("utf-8", errors="replace").strip()

        if proc.returncode != 0:
            raise RuntimeError(f"LLM command failed (exit {proc.returncode}): {stderr or stdout}")

        try:
            return json.loads(stdout)
        except json.JSONDecodeError:
            return {"raw_stdout": stdout, "raw_stderr": stderr}

    if mode in {"claude_agent_sdk", "claude-agent-sdk", "claude"}:
        try:
            from .claude_agent_sdk_runner import run_structured_json_schema
        except Exception as e:  # pragma: no cover
            raise RuntimeError(f"Failed to import Claude Agent SDK runner: {e}") from e

        schema: dict[str, Any] = {
            "type": "object",
            "additionalProperties": True,
        }
        result = run_structured_json_schema(
            system_prompt=settings.llm_system_prompt,
            prompt=json.dumps({"prompt": prompt, "input": input_obj}, ensure_ascii=False),
            json_schema=schema,
        )
        return result

    raise RuntimeError(f"Unsupported LLM_MODE: {mode!r}")
