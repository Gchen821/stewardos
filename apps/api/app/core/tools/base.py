"""Tool primitives for governed tool execution and schema exposure."""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any

from pydantic import BaseModel


@dataclass(slots=True)
class ToolResult:
    success: bool
    payload: dict[str, Any] = field(default_factory=dict)
    error: str | None = None


class ToolParameter(BaseModel):
    name: str
    type: str
    description: str
    required: bool = True
    default: Any = None


class Tool(ABC):
    def __init__(self, name: str, description: str, expandable: bool = False) -> None:
        self.name = name
        self.description = description
        self.expandable = expandable

    def get_parameters(self) -> list[ToolParameter]:
        return []

    @abstractmethod
    def run(
        self,
        payload: dict[str, Any],
        runtime_context: dict[str, Any] | None = None,
    ) -> ToolResult | Any:
        """Run a tool with the given payload."""
