from app.core.tools.base import Tool, ToolResult


class NoteTool(Tool):
    def __init__(self) -> None:
        super().__init__(
            name="note_tool",
            description="Create structured notes for long-running sessions and tasks.",
        )

    def run(
        self,
        payload: dict[str, object],
        runtime_context: dict[str, object] | None = None,
    ) -> ToolResult:
        return ToolResult(success=True, payload={"status": "planned", "note": payload})
