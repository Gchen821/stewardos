from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any

from app.core.agent.message import AgentMessage


@dataclass(slots=True)
class LLMResponse:
    text: str
    model: str
    usage: dict[str, Any] = field(default_factory=dict)
    tool_calls: list[dict[str, Any]] = field(default_factory=list)


class ModelGateway(ABC):
    @abstractmethod
    def generate(
        self,
        messages: list[AgentMessage],
        model_hint: str | None = None,
        tools: list[str] | None = None,
        stream: bool = False,
    ) -> LLMResponse:
        """Generate a model response from normalized agent messages."""
