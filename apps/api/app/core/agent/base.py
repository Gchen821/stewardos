from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any

from app.core.agent.context import ContextEnvelope
from app.core.agent.message import AgentMessage


@dataclass(slots=True)
class AgentResult:
    output_text: str
    messages: list[AgentMessage] = field(default_factory=list)
    used_tools: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)


class Agent(ABC):
    def __init__(self, name: str) -> None:
        self.name = name

    @abstractmethod
    def run(self, input_text: str, context: ContextEnvelope) -> AgentResult:
        """Run the agent within a prebuilt runtime context."""
