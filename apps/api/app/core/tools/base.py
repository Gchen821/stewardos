from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class ToolResult:
    success: bool
    payload: dict[str, Any] = field(default_factory=dict)
    error: str | None = None


class Tool(ABC):
    def __init__(self, name: str, description: str) -> None:
        self.name = name
        self.description = description

    @abstractmethod
    def run(
        self,
        payload: dict[str, Any],
        runtime_context: dict[str, Any] | None = None,
    ) -> ToolResult:
        """Run a tool with the given payload."""
