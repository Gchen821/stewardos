"""Skill registry managing runtime enablement and metadata-backed lookup."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from app.core.skills.loader import SkillDefinition, SkillLoader


@dataclass(slots=True)
class SkillRuntimeBinding:
    code: str
    enabled: bool = True
    config: dict[str, object] = field(default_factory=dict)


class SkillRegistry:
    """Runtime registry for selecting and loading enabled skills."""

    def __init__(self, skills_dir: Path):
        self.loader = SkillLoader(skills_dir=skills_dir)
        self._bindings: dict[str, SkillRuntimeBinding] = {}

    def register(self, code: str, enabled: bool = True, config: dict[str, object] | None = None) -> None:
        if self.loader.get_metadata(code) is None:
            raise ValueError(f"Skill '{code}' not found")
        self._bindings[code] = SkillRuntimeBinding(
            code=code,
            enabled=enabled,
            config=config or {},
        )

    def unregister(self, code: str) -> None:
        self._bindings.pop(code, None)

    def is_enabled(self, code: str) -> bool:
        binding = self._bindings.get(code)
        return bool(binding and binding.enabled)

    def list_registered(self) -> list[str]:
        return sorted(self._bindings.keys())

    def list_enabled(self) -> list[str]:
        return sorted([code for code, binding in self._bindings.items() if binding.enabled])

    def get(self, code: str) -> SkillDefinition | None:
        if not self.is_enabled(code):
            return None
        return self.loader.get_skill(code)

    def descriptions(self) -> str:
        enabled = self.list_enabled()
        if not enabled:
            return "暂无已启用技能"
        rows: list[str] = []
        for code in enabled:
            meta = self.loader.get_metadata(code)
            if meta is None:
                continue
            rows.append(f"- {meta.code}: {meta.description or meta.name}")
        return "\n".join(rows) if rows else "暂无已启用技能"
