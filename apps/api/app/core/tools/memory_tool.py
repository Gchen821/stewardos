from app.core.tools.base import Tool, ToolResult


class MemoryTool(Tool):
    def __init__(self) -> None:
        super().__init__(
            name="memory_tool",
            description="Persist and retrieve working memory, notes, and summaries.",
        )

    def run(
        self,
        payload: dict[str, object],
        runtime_context: dict[str, object] | None = None,
    ) -> ToolResult:
        return ToolResult(success=True, payload={"status": "planned", "input": payload})
