"""Normalized runtime message model shared by agents and LLM gateway."""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any

try:  # Python 3.11+
    from enum import StrEnum
except ImportError:  # Python 3.10 fallback
    class StrEnum(str, Enum):
        pass


class MessageRole(StrEnum):
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"
    TOOL = "tool"


@dataclass(slots=True)
class AgentMessage:
    role: MessageRole
    content: str
    name: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)
