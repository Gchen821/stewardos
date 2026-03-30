"""Tool registry with function support, circuit breaker, and typed results."""

from __future__ import annotations

from typing import Any, Callable
import json

from app.core.tools.base import Tool
from app.core.tools.base import ToolResult
from app.core.tools.circuit_breaker import CircuitBreaker
from app.core.tools.response import ToolResponse, ToolStatus


class ToolRegistry:
    """Registry for tool registration, execution, and optional circuit breaking."""

    def __init__(self, circuit_breaker: CircuitBreaker | None = None) -> None:
        self._tools: dict[str, Tool] = {}
        self._functions: dict[str, dict[str, Any]] = {}
        self.circuit_breaker = circuit_breaker or CircuitBreaker()

    def register(self, tool: Tool) -> None:
        self._tools[tool.name] = tool

    def register_tool(self, tool: Tool) -> None:
        self.register(tool)

    def register_function(self, name: str, description: str, func: Callable[[str], str]) -> None:
        self._functions[name] = {"description": description, "func": func}

    def get(self, name: str) -> Tool | None:
        return self._tools.get(name)

    def get_function(self, name: str) -> Callable[[str], str] | None:
        record = self._functions.get(name)
        if record is None:
            return None
        return record["func"]  # type: ignore[return-value]

    def execute(self, name: str, payload: dict[str, Any], runtime_context: dict[str, Any] | None = None) -> ToolResult:
        if self.circuit_breaker.is_open(name):
            return ToolResult(success=False, error=f"tool '{name}' temporarily unavailable due to circuit open")
        tool = self._tools.get(name)
        if tool is None:
            return ToolResult(success=False, error=f"tool '{name}' not found")
        result = tool.run(payload=payload, runtime_context=runtime_context)
        if isinstance(result, ToolResult):
            self.circuit_breaker.record_result(
                name,
                ToolResponse.success(text="ok")
                if result.success
                else ToolResponse(status=ToolStatus.ERROR, text=result.error or "error"),
            )
            return result
        if isinstance(result, ToolResponse):
            self.circuit_breaker.record_result(name, result)
            if result.status == ToolStatus.ERROR:
                return ToolResult(success=False, error=result.text, payload=result.data)
            return ToolResult(success=True, payload=result.data)
        self.circuit_breaker.record_result(name, ToolResponse.success(text="ok"))
        return ToolResult(success=True, payload={"output": result})

    def execute_tool(self, name: str, input_text: str) -> ToolResult:
        if self.circuit_breaker.is_open(name):
            return ToolResult(success=False, error=f"tool '{name}' temporarily unavailable due to circuit open")
        tool = self._tools.get(name)
        if tool is not None:
            try:
                data = json.loads(input_text) if input_text.strip().startswith("{") else {"input": input_text}
            except json.JSONDecodeError:
                data = {"input": input_text}
            return self.execute(name=name, payload=data)
        func_record = self._functions.get(name)
        if func_record is not None:
            try:
                output = str(func_record["func"](input_text))
            except Exception as exc:
                return ToolResult(success=False, error=str(exc))
            return ToolResult(success=True, payload={"output": output})
        return ToolResult(success=False, error=f"tool '{name}' not found")

    def list_tools(self) -> list[str]:
        return sorted(set(self._tools.keys()) | set(self._functions.keys()))
