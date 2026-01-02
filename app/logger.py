from __future__ import annotations

import json
import logging
import sys
from typing import Any

# ANSI color codes
class Colors:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    
    # Text colors
    BLACK = "\033[30m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"
    
    # Bright colors
    BRIGHT_BLACK = "\033[90m"
    BRIGHT_RED = "\033[91m"
    BRIGHT_GREEN = "\033[92m"
    BRIGHT_YELLOW = "\033[93m"
    BRIGHT_BLUE = "\033[94m"
    BRIGHT_MAGENTA = "\033[95m"
    BRIGHT_CYAN = "\033[96m"
    BRIGHT_WHITE = "\033[97m"

# Check if output is a TTY (terminal) to enable colors
_use_colors = sys.stderr.isatty()

def _colorize(text: str, color: str) -> str:
    """Apply color to text if colors are enabled."""
    if _use_colors:
        return f"{color}{text}{Colors.RESET}"
    return text

# Configure root logger for the app
_logger = logging.getLogger("app")
_logger.setLevel(logging.INFO)

# Remove existing handlers to avoid duplicates
_logger.handlers.clear()

# Create console handler
_console_handler = logging.StreamHandler(sys.stderr)
_console_handler.setLevel(logging.INFO)


class PrettyFormatter(logging.Formatter):
    """Pretty formatter with colors for structured JSON logs and regular logs."""
    
    # Color mapping for log levels
    LEVEL_COLORS = {
        "DEBUG": Colors.DIM + Colors.WHITE,
        "INFO": Colors.CYAN,
        "WARNING": Colors.YELLOW,
        "ERROR": Colors.RED,
        "CRITICAL": Colors.BOLD + Colors.RED,
    }
    
    # Color mapping for event types
    EVENT_COLORS = {
        "agent_start": Colors.BRIGHT_GREEN,
        "agent_complete": Colors.GREEN,
        "agent_error": Colors.RED,
        "agent_tool_use": Colors.BRIGHT_BLUE,
        "agent_tool_result": Colors.BLUE,
        "agent_text": Colors.WHITE,
        "agent_result": Colors.BRIGHT_CYAN,
        "agent_message": Colors.DIM + Colors.WHITE,
    }
    
    def format(self, record: logging.LogRecord) -> str:
        message = record.getMessage()
        
        # Try to parse as JSON (structured event logs)
        try:
            data = json.loads(message)
            if isinstance(data, dict) and "event" in data:
                return self._format_event(data, record)
        except (json.JSONDecodeError, ValueError):
            pass
        
        # Regular log message
        return self._format_regular(record, message)
    
    def _format_event(self, data: dict[str, Any], record: logging.LogRecord) -> str:
        """Format structured event logs with colors."""
        event = data.get("event", "unknown")
        event_color = self.EVENT_COLORS.get(event, Colors.WHITE)
        
        # Build the formatted output
        parts = []
        
        # Timestamp
        timestamp = self.formatTime(record, "%H:%M:%S")
        parts.append(_colorize(f"[{timestamp}]", Colors.DIM + Colors.BRIGHT_BLACK))
        
        # Event name (colored)
        parts.append(_colorize(f" {event.upper()} ", event_color + Colors.BOLD))
        
        # Agent name if present
        if "agent_name" in data:
            agent_name = data.pop("agent_name")
            parts.append(_colorize(f"agent={agent_name}", Colors.BRIGHT_MAGENTA))
        
        # Key-value pairs
        for key, value in sorted(data.items()):
            if key == "event":
                continue
            
            # Format value nicely
            formatted_value = self._format_value(value)
            
            # Color code different types of fields
            if key in ("tool", "tool_id"):
                parts.append(_colorize(f"{key}={formatted_value}", Colors.BRIGHT_CYAN))
            elif key in ("error", "error_type"):
                parts.append(_colorize(f"{key}={formatted_value}", Colors.RED))
            elif key in ("result", "chunk"):
                # Truncate long results
                if isinstance(value, str) and len(value) > 100:
                    formatted_value = value[:97] + "..."
                parts.append(_colorize(f"{key}={formatted_value}", Colors.DIM + Colors.WHITE))
            elif isinstance(value, (int, float)):
                parts.append(_colorize(f"{key}={formatted_value}", Colors.BRIGHT_YELLOW))
            elif isinstance(value, bool):
                color = Colors.BRIGHT_GREEN if value else Colors.BRIGHT_RED
                parts.append(_colorize(f"{key}={formatted_value}", color))
            else:
                parts.append(f"{key}={formatted_value}")
        
        return " ".join(parts)
    
    def _format_regular(self, record: logging.LogRecord, message: str) -> str:
        """Format regular log messages with colors."""
        level_color = self.LEVEL_COLORS.get(record.levelname, Colors.WHITE)
        
        parts = []
        
        # Timestamp
        timestamp = self.formatTime(record, "%H:%M:%S")
        parts.append(_colorize(f"[{timestamp}]", Colors.DIM + Colors.BRIGHT_BLACK))
        
        # Log level
        level_str = record.levelname.ljust(8)
        parts.append(_colorize(level_str, level_color + Colors.BOLD))
        
        # Logger name
        if record.name != "app":
            logger_name = record.name.replace("app.", "")
            parts.append(_colorize(f"[{logger_name}]", Colors.DIM + Colors.WHITE))
        
        # Message
        parts.append(message)
        
        # Exception info if present
        if record.exc_info:
            parts.append("\n" + _colorize(self.formatException(record.exc_info), Colors.RED))
        
        return " ".join(parts)
    
    def _format_value(self, value: Any) -> str:
        """Format a value for display."""
        if value is None:
            return _colorize("null", Colors.DIM)
        if isinstance(value, bool):
            return _colorize(str(value).lower(), Colors.BRIGHT_GREEN if value else Colors.BRIGHT_RED)
        if isinstance(value, (int, float)):
            return str(value)
        if isinstance(value, str):
            # Escape newlines and truncate if too long
            if len(value) > 200:
                return value[:197] + "..."
            return value.replace("\n", "\\n")
        if isinstance(value, (list, dict)):
            return json.dumps(value, ensure_ascii=False)[:100] + ("..." if len(str(value)) > 100 else "")
        return str(value)


_console_handler.setFormatter(PrettyFormatter())
_logger.addHandler(_console_handler)

# Prevent propagation to root logger
_logger.propagate = False


def get_logger(name: str | None = None) -> logging.Logger:
    """
    Get a logger instance for the given name.
    
    Args:
        name: Logger name (typically __name__). If None, returns the app logger.
        
    Returns:
        Logger instance configured for structured JSON logging.
    """
    if name is None:
        return _logger
    return logging.getLogger(f"app.{name}")


def log_event(event: str, **data: Any) -> None:
    """
    Emit a structured JSON log event.
    
    This is a convenience function for logging structured events that will be
    parsed as JSON (one JSON object per line).
    
    Args:
        event: Event name/type
        **data: Additional data to include in the log entry
    """
    payload = {"event": event, **data}
    _logger.info(json.dumps(payload, ensure_ascii=False))

