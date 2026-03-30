"""LLM gateway contracts used by domain runtime and provider adapters."""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Iterator

from app.core.agent.message import AgentMessage
from app.core.llm.response import LLMToolResponse


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

    def stream_generate(
        self,
        messages: list[AgentMessage],
        model_hint: str | None = None,
        tools: list[str] | None = None,
    ) -> Iterator[str]:
        """Optional streaming generation hook."""
        _ = (messages, model_hint, tools)
        raise NotImplementedError

    def generate_with_tools(
        self,
        messages: list[dict[str, Any]],
        tools: list[dict[str, Any]],
        model_hint: str | None = None,
    ) -> LLMToolResponse:
        """Optional function-calling hook."""
        _ = (messages, tools, model_hint)
        raise NotImplementedError
