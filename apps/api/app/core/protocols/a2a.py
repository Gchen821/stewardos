"""A2A protocol adapter placeholder for inter-agent communication."""

from app.core.protocols import ProtocolAdapter, ProtocolResult


class A2AAdapter(ProtocolAdapter):
    def call(self, payload: dict[str, object]) -> ProtocolResult:
        return ProtocolResult(success=True, data={"protocol": "a2a", "payload": payload})
