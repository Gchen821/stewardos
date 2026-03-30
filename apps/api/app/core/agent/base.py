"""Core agent abstractions and execution result contracts."""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any

from app.core.agent.context import ContextEnvelope
from app.core.agent.message import AgentMessage
from app.core.skills.loader import SkillLoader
from app.core.tools.registry import ToolRegistry


@dataclass(slots=True)
class AgentResult:
    output_text: str
    messages: list[AgentMessage] = field(default_factory=list)
    used_tools: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)


class Agent(ABC):
    """Core Agent base aligned with HelloAgents style, kept domain-compatible."""

    def __init__(
        self,
        name: str,
        tool_registry: ToolRegistry | None = None,
        skill_loader: SkillLoader | None = None,
    ) -> None:
        self.name = name
        self.tool_registry = tool_registry
        self.skill_loader = skill_loader
        self._history: list[AgentMessage] = []

    @abstractmethod
    def run(self, input_text: str, context: ContextEnvelope) -> AgentResult:
        """Run the agent within a prebuilt runtime context."""

    def add_message(self, message: AgentMessage) -> None:
        self._history.append(message)

    def clear_history(self) -> None:
        self._history.clear()

    def get_history(self) -> list[AgentMessage]:
        return self._history.copy()
