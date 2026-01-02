from __future__ import annotations

import asyncio
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .logger import log_event
from .settings import get_settings


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def safe_agent_path(agent_name: str) -> Path:
    """Resolve agent file path safely within repo root.

    Looks for agents in this order:
    1. .claude/agents/{agent_name}.md (preferred, Claude Code standard)
    2. app/agents/{agent_name}.md (legacy/fallback)
    """
    repo_root = _repo_root()

    # Try .claude/agents/ first (Claude Code standard location)
    claude_agent_path = repo_root / ".claude" / "agents" / f"{agent_name}.md"
    if claude_agent_path.exists():
        # Ensure path is within repo root
        if not claude_agent_path.resolve().is_relative_to(repo_root.resolve()):
            raise ValueError(f"Invalid agent name: {agent_name}")
        return claude_agent_path

    # Fall back to app/agents/ (legacy location)
    app_agent_path = repo_root / "app" / "agents" / f"{agent_name}.md"

    # Ensure path is within repo root
    if not app_agent_path.resolve().is_relative_to(repo_root.resolve()):
        raise ValueError(f"Invalid agent name: {agent_name}")

    if not app_agent_path.exists():
        raise FileNotFoundError(
            f"Agent file not found. Searched:\n"
            f"  - {claude_agent_path}\n"
            f"  - {app_agent_path}"
        )

    return app_agent_path


@dataclass
class AgentConfig:
    """Configuration loaded from agent markdown file."""
    
    name: str
    system_prompt: str
    model: str | None = None
    description: str | None = None
    tools: list[str] | None = None
    
    @classmethod
    def from_file(cls, path: Path) -> "AgentConfig":
        """
        Load agent configuration from markdown file.
        
        Supports YAML frontmatter format:
        ---
        name: agent-name
        model: sonnet
        description: Agent description
        tools: ["Read", "Write"]
        ---
        
        Content after frontmatter becomes the system_prompt.
        """
        content = path.read_text(encoding="utf-8")
        
        # Parse frontmatter if present
        frontmatter_match = re.match(r"^---\s*\n(.*?)\n---\s*\n(.*)$", content, re.DOTALL)
        
        if frontmatter_match:
            frontmatter_text = frontmatter_match.group(1)
            system_prompt = frontmatter_match.group(2).strip()
            
            # Simple YAML-like parsing (handles basic key: value pairs)
            metadata: dict[str, Any] = {}
            for line in frontmatter_text.split("\n"):
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                if ":" in line:
                    key, value = line.split(":", 1)
                    key = key.strip()
                    value = value.strip()
                    
                    # Remove quotes if present
                    if value.startswith('"') and value.endswith('"'):
                        value = value[1:-1]
                    elif value.startswith("'") and value.endswith("'"):
                        value = value[1:-1]
                    
                    # Handle list values (basic support)
                    if value.startswith("[") and value.endswith("]"):
                        # Simple list parsing - remove brackets and split
                        items = value[1:-1].strip()
                        if items:
                            metadata[key] = [item.strip().strip('"').strip("'") for item in items.split(",")]
                        else:
                            metadata[key] = []
                    else:
                        metadata[key] = value
            
            name = metadata.get("name", path.stem)
            model = metadata.get("model")
            description = metadata.get("description")
            tools = metadata.get("tools")
            
            # Normalize model name (e.g., "sonnet" -> "claude-sonnet-4-5")
            if model:
                model_lower = model.lower()
                if model_lower == "sonnet":
                    model = "claude-sonnet-4-5"
                elif model_lower in ["opus", "claude-opus"]:
                    model = "claude-opus-4-1"
                elif not model.startswith("claude-"):
                    # Assume it's a shorthand, add claude- prefix if needed
                    model = f"claude-{model}"
        else:
            # No frontmatter, use entire content as system prompt
            name = path.stem
            system_prompt = content.strip()
            model = None
            description = None
            tools = None
        
        return cls(
            name=name,
            system_prompt=system_prompt,
            model=model,
            description=description,
            tools=tools if isinstance(tools, list) else None,
        )


async def execute_agent(agent_name: str, payload: dict[str, Any]) -> dict[str, Any]:
    """
    Execute a Claude Agent SDK agent with the given payload.
    
    This function properly loads agent markdown files following Claude Agent SDK patterns:
    - Parses YAML frontmatter for metadata (name, model, description, tools)
    - Uses the content as the system prompt
    - Respects model specified in frontmatter, falling back to settings
    
    Args:
        agent_name: Name of the agent (loads from app/agents/{agent_name}.md)
        payload: Arbitrary payload dict to pass to the agent
        
    Returns:
        Result dict from the agent execution
    """
    from claude_agent_sdk import query
    from claude_agent_sdk.types import (
        AssistantMessage,
        ClaudeAgentOptions,
        ResultMessage,
        TextBlock,
        ToolUseBlock,
        ToolResultBlock,
        UserMessage,
    )
    
    # Load and parse agent markdown file
    agent_path = safe_agent_path(agent_name)
    agent_config = AgentConfig.from_file(agent_path)
    
    # Format payload as JSON string for the agent prompt
    user_prompt = f"""Here is the input data to process:

```json
{json.dumps(payload, indent=2, ensure_ascii=False)}
```

Process this data according to your system prompt instructions."""
    
    settings = get_settings()
    
    # Use model from agent config if specified, otherwise fall back to settings
    model = agent_config.model or settings.claude_agent_model
    
    # Filter out interactive tools that require user input (not supported in webhook/async mode)
    # These tools block waiting for CLI input which doesn't work with webhooks
    INTERACTIVE_TOOLS = {"askUserQuestion", "AskUserQuestion", "ask_user_question"}
    
    allowed_tools = agent_config.tools
    if allowed_tools:
        # Filter out interactive tools
        allowed_tools = [t for t in allowed_tools if t not in INTERACTIVE_TOOLS]
    
    # Configure MCP servers if DataGen API key is available
    # SDK expects: dict[str, McpServerConfig] where McpServerConfig can be:
    # - McpStdioServerConfig: {"type": "stdio", "command": "...", "args": [...]}
    # - McpSSEServerConfig: {"type": "sse", "url": "...", "headers": {...}}
    # - McpHttpServerConfig: {"type": "http", "url": "...", "headers": {...}}
    # - McpSdkServerConfig: {"type": "sdk", "name": "...", "instance": server}
    mcp_servers: dict[str, dict[str, Any]] = {}
    mcp_servers_available: set[str] = set()
    
    if settings.datagen_api_key:
        mcp_servers["datagen"] = {
            "type": "http",
            "url": settings.datagen_mcp_url,
            "headers": {
                "x-api-key": settings.datagen_api_key,
            },
        }
        mcp_servers_available.add("datagen")

    # Validate that agent's tools have required MCP servers configured
    # Tool name patterns that require specific MCP servers
    MCP_TOOL_PATTERNS: dict[str, list[str]] = {
        "datagen": [
            "mcp__datagen__",      # DataGen direct tools
            "mcp_datagen_",        # Alternative naming
            "mcp_Slack_",          # Slack via DataGen
            "mcp_Firecrawl_",      # Firecrawl via DataGen
            "mcp_GitHub_",         # GitHub via DataGen
            "mcp_Linear_",         # Linear via DataGen
            "mcp_Notion_",         # Notion via DataGen
            "mcp_Google",          # Google tools via DataGen
        ],
    }
    
    # Check if agent requires MCP servers that aren't configured
    if allowed_tools:
        missing_mcp: dict[str, list[str]] = {}
        
        for tool in allowed_tools:
            for mcp_name, patterns in MCP_TOOL_PATTERNS.items():
                if any(tool.startswith(pattern) for pattern in patterns):
                    if mcp_name not in mcp_servers_available:
                        if mcp_name not in missing_mcp:
                            missing_mcp[mcp_name] = []
                        missing_mcp[mcp_name].append(tool)
        
        if missing_mcp:
            # Log the validation failure
            log_event(
                "agent_mcp_validation_failed",
                agent_name=agent_name,
                missing_mcp_servers=list(missing_mcp.keys()),
                tools_requiring_mcp=missing_mcp,
            )
            
            # Build error message
            error_parts = [f"Agent '{agent_name}' requires MCP servers that are not configured:"]
            for mcp_name, tools in missing_mcp.items():
                error_parts.append(f"  - {mcp_name}: {', '.join(tools[:3])}" + 
                                   (f" (+{len(tools)-3} more)" if len(tools) > 3 else ""))
            
            if "datagen" in missing_mcp:
                error_parts.append("\nTo fix: Set DATAGEN_API_KEY environment variable")
            
            raise ValueError("\n".join(error_parts))

    # Log agent execution start
    log_event(
        "agent_start",
        agent_name=agent_name,
        agent_config_name=agent_config.name,
        model=model,
        payload_keys=list(payload.keys()),
        interactive_tools_disabled=True,
        mcp_servers_configured=len(mcp_servers),
        mcp_servers_available=list(mcp_servers_available),
    )

    opts = ClaudeAgentOptions(
        system_prompt=agent_config.system_prompt,
        cwd=str(_repo_root()),
        permission_mode=settings.claude_agent_permission_mode,
        model=model,
        max_turns=settings.claude_agent_max_turns,
        # If agent specifies tools, use filtered list (interactive tools removed for webhook mode)
        allowed_tools=allowed_tools if allowed_tools else None,
        mcp_servers=mcp_servers if mcp_servers else None,
    )
    
    final: Any = None
    tool_call_count = 0
    tool_result_count = 0
    text_chunks: list[str] = []
    
    timeout_seconds = get_settings().claude_agent_timeout_seconds
    
    async def _process_messages() -> Any:
        """Process messages from Claude Agent SDK query."""
        nonlocal final, tool_call_count, tool_result_count, text_chunks
        async for msg in query(prompt=user_prompt, options=opts):
            # Handle AssistantMessage (text and tool calls)
            if isinstance(msg, AssistantMessage):
                for block in msg.content:
                    # Log text chunks
                    if isinstance(block, TextBlock):
                        text = block.text
                        text_chunks.append(text)
                        log_event(
                            "agent_text",
                            agent_name=agent_name,
                            chunk=text[:500],  # Truncate long chunks
                            truncated=len(text) > 500,
                            chunk_length=len(text),
                        )
                    # Log tool calls
                    elif isinstance(block, ToolUseBlock):
                        tool_call_count += 1
                        # Truncate large tool inputs for logging
                        tool_input = block.input
                        if isinstance(tool_input, dict):
                            tool_input_str = json.dumps(tool_input, ensure_ascii=False)
                            if len(tool_input_str) > 1000:
                                tool_input_str = tool_input_str[:1000] + "... (truncated)"
                        else:
                            tool_input_str = str(tool_input)[:1000]
                        
                        log_event(
                            "agent_tool_use",
                            agent_name=agent_name,
                            tool=block.name,
                            tool_id=getattr(block, "id", None),
                            input=tool_input_str,
                            input_length=len(str(tool_input)),
                        )
            
            # Handle UserMessage (may contain tool results)
            elif isinstance(msg, UserMessage):
                if hasattr(msg, "content") and msg.content:
                    if isinstance(msg.content, list):
                        for block in msg.content:
                            if isinstance(block, ToolResultBlock):
                                tool_result_count += 1
                                # Extract tool result content
                                tool_result = block.content
                                if isinstance(tool_result, list):
                                    # Handle list of result blocks
                                    result_text = ""
                                    for item in tool_result:
                                        if hasattr(item, "text"):
                                            result_text += item.text
                                        elif isinstance(item, str):
                                            result_text += item
                                    tool_result_str = result_text
                                elif isinstance(tool_result, str):
                                    tool_result_str = tool_result
                                else:
                                    tool_result_str = json.dumps(tool_result, ensure_ascii=False)
                                
                                if len(tool_result_str) > 1000:
                                    tool_result_str = tool_result_str[:1000] + "... (truncated)"
                                
                                log_event(
                                    "agent_tool_result",
                                    agent_name=agent_name,
                                    tool_id=getattr(block, "tool_use_id", None),
                                    is_error=getattr(block, "is_error", False),
                                    result=tool_result_str,
                                    result_length=len(str(tool_result)),
                                )
            
            # Handle ResultMessage (final result with cost info)
            elif isinstance(msg, ResultMessage):
                if msg.structured_output is not None:
                    final = msg.structured_output
                elif msg.result is not None:
                    final = msg.result
                
                # Log final result with cost information
                usage_info = {}
                if hasattr(msg, "usage") and msg.usage:
                    usage_info = {
                        "input_tokens": msg.usage.get("input_tokens") if isinstance(msg.usage, dict) else None,
                        "output_tokens": msg.usage.get("output_tokens") if isinstance(msg.usage, dict) else None,
                    }
                
                log_event(
                    "agent_result",
                    agent_name=agent_name,
                    has_structured_output=msg.structured_output is not None,
                    has_result=msg.result is not None,
                    total_cost_usd=getattr(msg, "total_cost_usd", None),
                    **usage_info,
                )
            else:
                # Log other message types
                log_event(
                    "agent_message",
                    agent_name=agent_name,
                    msg_type=type(msg).__name__,
                )
        return final
    
    try:
        final = await asyncio.wait_for(_process_messages(), timeout=timeout_seconds)
    except asyncio.TimeoutError as e:
        log_event(
            "agent_error",
            agent_name=agent_name,
            error=f"Claude Agent SDK timed out after {timeout_seconds}s",
            error_type="TimeoutError",
        )
        raise RuntimeError(f"Claude Agent SDK timed out after {timeout_seconds}s") from e
    except Exception as e:
        log_event(
            "agent_error",
            agent_name=agent_name,
            error=str(e),
            error_type=type(e).__name__,
        )
        raise
    finally:
        # Log execution summary
        log_event(
            "agent_complete",
            agent_name=agent_name,
            tool_calls=tool_call_count,
            tool_results=tool_result_count,
            text_chunks=len(text_chunks),
            total_text_length=sum(len(chunk) for chunk in text_chunks),
            has_result=final is not None,
        )
    
    if final is None:
        return {"error": "no_result"}
    if isinstance(final, dict):
        return final
    if isinstance(final, str):
        try:
            parsed = json.loads(final)
            if isinstance(parsed, dict):
                return parsed
            return {"result": parsed}
        except json.JSONDecodeError:
            return {"raw_result": final}
    return {"result": final}

