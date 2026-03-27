from app.core.protocols import ProtocolAdapter, ProtocolResult


class ANPAdapter(ProtocolAdapter):
    def call(self, payload: dict[str, object]) -> ProtocolResult:
        return ProtocolResult(success=True, data={"protocol": "anp", "payload": payload})
