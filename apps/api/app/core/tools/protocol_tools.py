from app.core.protocols.a2a import A2AAdapter
from app.core.protocols.anp import ANPAdapter
from app.core.protocols.mcp import MCPAdapter
from app.core.tools.base import Tool, ToolResult


class ProtocolTool(Tool):
    def __init__(self, protocol: str) -> None:
        super().__init__(
            name=f"{protocol}_tool",
            description=f"Protocol-backed tool adapter for {protocol}.",
        )
        adapters = {
            "mcp": MCPAdapter(),
            "a2a": A2AAdapter(),
            "anp": ANPAdapter(),
        }
        self.adapter = adapters[protocol]

    def run(
        self,
        payload: dict[str, object],
        runtime_context: dict[str, object] | None = None,
    ) -> ToolResult:
        result = self.adapter.call(payload)
        return ToolResult(success=result.success, payload=result.data, error=result.error)
