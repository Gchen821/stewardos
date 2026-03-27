from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class ProtocolResult:
    success: bool
    data: dict[str, Any] = field(default_factory=dict)
    error: str | None = None


class ProtocolAdapter(ABC):
    @abstractmethod
    def call(self, payload: dict[str, Any]) -> ProtocolResult:
        """Call an external capability using a protocol-specific adapter."""
