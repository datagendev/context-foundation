from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any

from .claude_agent_sdk_runner import run_structured_json_schema
from .settings import get_settings


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def _safe_relpath(path: str) -> Path:
    candidate = Path(path)
    if candidate.is_absolute():
        p = candidate.resolve()
    else:
        p = (_repo_root() / path).resolve()
    if _repo_root() not in p.parents and p != _repo_root():
        raise RuntimeError("Refusing to read agent prompt outside repo root.")
    return p


def _resolve_agent_path(agent_name: str) -> str:
    """
    Resolve agent path, checking Claude Code location first.

    Looks for agents in this order:
    1. .claude/agents/{agent_name}.md (preferred, Claude Code standard)
    2. app/agents/{agent_name}.md (legacy/fallback)

    Returns the relative path string for use with _safe_relpath.
    """
    repo_root = _repo_root()

    # Try .claude/agents/ first (Claude Code standard location)
    claude_path = repo_root / ".claude" / "agents" / f"{agent_name}.md"
    if claude_path.exists():
        return f".claude/agents/{agent_name}.md"

    # Fall back to app/agents/ (legacy location)
    return f"app/agents/{agent_name}.md"


def run_action(
    *,
    handler_mode: str,
    handler_target: str | None,
    action: str,
    event_payload: dict[str, Any],
    router: dict[str, Any],
) -> dict[str, Any]:
    settings = get_settings()
    mode = (handler_mode or "noop").strip().lower()

    if mode in {"", "noop", "none"}:
        return {"mode": "noop", "action": action}

    if mode == "command":
        commands_path = settings.app_commands_path
        full_path = _safe_relpath(commands_path)
        if not full_path.exists():
            raise RuntimeError(f"Missing commands file: {commands_path}")

        commands = json.loads(full_path.read_text(encoding="utf-8"))
        if not isinstance(commands, dict):
            raise RuntimeError("commands.json must be an object mapping name -> argv list")

        if not handler_target:
            raise RuntimeError("handler_target required for command mode")
        argv = commands.get(handler_target)
        if not isinstance(argv, list) or not all(isinstance(x, str) for x in argv):
            raise RuntimeError(f"Unknown or invalid command target: {handler_target!r}")

        stdin_payload = json.dumps(
            {"action": action, "router": router, "payload": event_payload},
            ensure_ascii=False,
            separators=(",", ":"),
        ).encode("utf-8")

        proc = subprocess.run(argv, input=stdin_payload, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
        out = proc.stdout.decode("utf-8", errors="replace").strip()
        err = proc.stderr.decode("utf-8", errors="replace").strip()
        if proc.returncode != 0:
            raise RuntimeError(f"command failed (exit {proc.returncode}): {err or out}")
        try:
            return json.loads(out) if out else {"stdout": out, "stderr": err}
        except json.JSONDecodeError:
            return {"stdout": out, "stderr": err}

    if mode == "agent":
        if not handler_target:
            raise RuntimeError("handler_target required for agent mode")
        prompt_path = handler_target
        if not (prompt_path.endswith(".md") or "/" in prompt_path):
            # Resolve agent name to path, checking .claude/agents/ first
            prompt_path = _resolve_agent_path(handler_target)

        full_prompt_path = _safe_relpath(prompt_path)
        prompt_obj = {"action": action, "router": router, "payload": event_payload}

        timeout_seconds = settings.action_agent_timeout_seconds
        proc = subprocess.run(
            [sys.executable, "-m", "app.agent_cli", "--agent", str(full_prompt_path)],
            input=json.dumps(prompt_obj, ensure_ascii=False).encode("utf-8"),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
            timeout=timeout_seconds,
        )
        out = proc.stdout.decode("utf-8", errors="replace").strip()
        err = proc.stderr.decode("utf-8", errors="replace").strip()
        if proc.returncode != 0:
            raise RuntimeError(f"agent subprocess failed (exit {proc.returncode}): {err or out}")
        try:
            return json.loads(out) if out else {"stdout": out, "stderr": err}
        except json.JSONDecodeError:
            return {"stdout": out, "stderr": err}

    if mode == "llm":
        schema = {
            "type": "object",
            "additionalProperties": True,
        }
        prompt = (
            "Given an event payload and an action name, produce JSON arguments for the action.\n"
            "Return ONLY JSON."
        )
        return run_structured_json_schema(
            system_prompt=settings.llm_system_prompt or prompt,
            prompt=json.dumps({"action": action, "router": router, "payload": event_payload}, ensure_ascii=False),
            json_schema=schema,
        )

    raise RuntimeError(f"Unsupported handler_mode: {handler_mode!r}")
