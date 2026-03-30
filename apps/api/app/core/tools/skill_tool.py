"""Runtime skill execution tool that loads repository skill entrypoints."""

from __future__ import annotations

from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
from types import ModuleType
from typing import Any

from app.core.skills.loader import SkillLoader
from app.core.tools.base import Tool, ToolResult


class SkillTool(Tool):
    """Execute repository skill entrypoints as runtime tools."""

    def __init__(self, skill_loader: SkillLoader) -> None:
        super().__init__(
            name="skill_tool",
            description="Load and execute repository skills by code.",
        )
        self.skill_loader = skill_loader

    def run(
        self,
        payload: dict[str, Any],
        runtime_context: dict[str, Any] | None = None,
    ) -> ToolResult:
        _ = runtime_context
        code = str(payload.get("skill_code", "")).strip()
        skill_payload = payload.get("payload", {})
        if not code:
            return ToolResult(success=False, error="missing 'skill_code'")
        if not isinstance(skill_payload, dict):
            return ToolResult(success=False, error="'payload' must be an object")

        metadata = self.skill_loader.get_metadata(code)
        if metadata is None:
            return ToolResult(success=False, error=f"skill '{code}' not found")
        script_path = metadata.path / metadata.entrypoint
        if not script_path.exists():
            return ToolResult(success=False, error=f"entrypoint not found: {script_path}")

        try:
            module = self._load_module(script_path=script_path, module_name=f"skill_{code}")
            handler = getattr(module, "run", None)
            if not callable(handler):
                return ToolResult(success=False, error=f"skill '{code}' entrypoint has no callable run(payload)")
            output = handler(skill_payload)
            if isinstance(output, dict):
                return ToolResult(success=True, payload=output)
            return ToolResult(success=True, payload={"output": output})
        except Exception as exc:
            return ToolResult(success=False, error=str(exc))

    @staticmethod
    def _load_module(script_path: Path, module_name: str) -> ModuleType:
        spec = spec_from_file_location(module_name, script_path.as_posix())
        if spec is None or spec.loader is None:
            raise RuntimeError(f"cannot load module from {script_path}")
        module = module_from_spec(spec)
        spec.loader.exec_module(module)
        return module
