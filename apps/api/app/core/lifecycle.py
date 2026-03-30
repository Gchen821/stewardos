"""Lifecycle event primitives for agent execution hooks."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import StrEnum
from typing import Any, Awaitable, Callable


class EventType(StrEnum):
    AGENT_START = "agent_start"
    AGENT_STEP = "agent_step"
    AGENT_FINISH = "agent_finish"
    AGENT_ERROR = "agent_error"


@dataclass(slots=True)
class AgentEvent:
    type: EventType
    agent_name: str
    timestamp: datetime = field(default_factory=datetime.utcnow)
    data: dict[str, Any] = field(default_factory=dict)


LifecycleHook = Callable[[AgentEvent], Awaitable[None]]
