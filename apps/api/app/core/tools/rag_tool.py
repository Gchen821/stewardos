"""Built-in RAG tool placeholder for grounded evidence retrieval."""

from app.core.tools.base import Tool, ToolResult


class RagTool(Tool):
    def __init__(self) -> None:
        super().__init__(
            name="rag_tool",
            description="Retrieve grounded evidence from knowledge collections.",
        )

    def run(
        self,
        payload: dict[str, object],
        runtime_context: dict[str, object] | None = None,
    ) -> ToolResult:
        return ToolResult(success=True, payload={"status": "planned", "query": payload})
