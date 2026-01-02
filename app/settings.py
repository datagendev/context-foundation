from __future__ import annotations

from functools import lru_cache

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # Service
    host: str = "0.0.0.0"
    port: int = 8080
    app_db_path: str = "app/data/events.sqlite3"
    app_config_path: str = ""

    # Auth (empty = disabled)
    ingress_secret: str = ""
    cron_secret: str = ""
    admin_secret: str = ""

    # Optional webhook signatures
    webhook_secret: str = ""
    fireflies_webhook_secret: str = ""

    # Worker
    worker_poll_interval: float = 1.0
    worker_max_attempts: int = 8

    # Mapper AI fallback
    mapper_use_ai: bool = False
    mapper_ai_threshold: float = 0.65

    # Cron helper (HTTP)
    api_base_url: str = ""

    # LLM runner (legacy / generic)
    llm_mode: str = "noop"
    llm_command: str = ""
    llm_system_prompt: str | None = None

    # Action runner
    app_commands_path: str = "app/commands.json"
    action_agent_timeout_seconds: float = 90.0

    # Claude Agent SDK
    claude_agent_permission_mode: str = "bypassPermissions"
    claude_agent_model: str | None = None
    claude_agent_max_turns: int = 6
    claude_agent_timeout_seconds: float = 90.0

    # DataGen MCP Server
    datagen_api_key: str = ""
    datagen_mcp_url: str = "https://mcp.datagen.dev/mcp"

    @field_validator(
        "ingress_secret",
        "cron_secret",
        "admin_secret",
        "webhook_secret",
        "fireflies_webhook_secret",
        "app_config_path",
        "api_base_url",
        "llm_mode",
        "llm_command",
        "app_commands_path",
        "claude_agent_permission_mode",
        "datagen_api_key",
        "datagen_mcp_url",
        mode="before",
    )
    @classmethod
    def _strip_strings(cls, v: object) -> object:
        if isinstance(v, str):
            return v.strip()
        return v

    @field_validator("llm_system_prompt", "claude_agent_model", mode="before")
    @classmethod
    def _empty_to_none(cls, v: object) -> object:
        if v is None:
            return None
        if isinstance(v, str) and not v.strip():
            return None
        return v


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
