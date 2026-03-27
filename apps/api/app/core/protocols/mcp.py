from app.core.protocols import ProtocolAdapter, ProtocolResult


class MCPAdapter(ProtocolAdapter):
    def call(self, payload: dict[str, object]) -> ProtocolResult:
        return ProtocolResult(success=True, data={"protocol": "mcp", "payload": payload})
