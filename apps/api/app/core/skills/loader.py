"""Repository-native skill loader with progressive metadata/body/resource loading."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re
from typing import Any

import yaml

FRONTMATTER_PATTERN = re.compile(r"^---\s*\n(.*?)\n---\s*\n(.*)$", re.DOTALL)


@dataclass(slots=True)
class SkillMetadata:
    code: str
    name: str
    description: str
    status: str
    risk_level: str
    path: Path
    skill_md_path: Path
    manifest_path: Path
    entrypoint: str
    bound_tools: list[str]


@dataclass(slots=True)
class SkillDefinition:
    metadata: SkillMetadata
    body: str
    scripts: list[Path]
    references: list[Path]
    examples: list[Path]


class SkillLoader:
    """Repository-native skill loader with progressive disclosure.

    Layer 1: metadata from `manifest.yaml` (+ optional SKILL frontmatter)
    Layer 2: full `SKILL.md` body
    Layer 3: scripts/references/examples files
    """

    def __init__(self, skills_dir: Path):
        self.skills_dir = Path(skills_dir)
        self.skills_dir.mkdir(parents=True, exist_ok=True)
        self.metadata_cache: dict[str, SkillMetadata] = {}
        self.skill_cache: dict[str, SkillDefinition] = {}
        self.scan()

    def scan(self) -> None:
        self.metadata_cache.clear()
        for skill_dir in sorted(self.skills_dir.iterdir()):
            if not skill_dir.is_dir():
                continue
            code = skill_dir.name
            manifest_path = skill_dir / "manifest.yaml"
            skill_md_path = skill_dir / "SKILL.md"
            manifest = self._load_yaml(manifest_path)
            if not manifest:
                continue
            frontmatter, _ = self._read_skill_md(skill_md_path)
            metadata = SkillMetadata(
                code=code,
                name=str(frontmatter.get("name") or manifest.get("name") or code),
                description=str(frontmatter.get("description") or manifest.get("description") or ""),
                status=str(manifest.get("status", "active")),
                risk_level=str(manifest.get("risk_level", "L1")),
                path=skill_dir,
                skill_md_path=skill_md_path,
                manifest_path=manifest_path,
                entrypoint=str(manifest.get("entrypoint", "scripts/workflow.py")),
                bound_tools=[str(x) for x in manifest.get("bound_tools", [])],
            )
            self.metadata_cache[code] = metadata

    def list_codes(self) -> list[str]:
        return sorted(self.metadata_cache.keys())

    def get_descriptions(self) -> str:
        if not self.metadata_cache:
            return "暂无可用技能"
        return "\n".join(
            f"- {m.code}: {m.description or m.name}"
            for m in [self.metadata_cache[k] for k in self.list_codes()]
        )

    def get_metadata(self, code: str) -> SkillMetadata | None:
        return self.metadata_cache.get(code)

    def get_skill(self, code: str) -> SkillDefinition | None:
        if code in self.skill_cache:
            return self.skill_cache[code]
        metadata = self.metadata_cache.get(code)
        if metadata is None:
            return None
        _, body = self._read_skill_md(metadata.skill_md_path)
        skill = SkillDefinition(
            metadata=metadata,
            body=body,
            scripts=self._collect_files(metadata.path / "scripts"),
            references=self._collect_files(metadata.path / "references"),
            examples=self._collect_files(metadata.path / "examples"),
        )
        self.skill_cache[code] = skill
        return skill

    def reload(self) -> None:
        self.skill_cache.clear()
        self.scan()

    @staticmethod
    def _load_yaml(path: Path) -> dict[str, Any]:
        if not path.exists():
            return {}
        raw = path.read_text(encoding="utf-8")
        data = yaml.safe_load(raw) or {}
        return data if isinstance(data, dict) else {}

    @staticmethod
    def _collect_files(path: Path) -> list[Path]:
        if not path.exists():
            return []
        return [item for item in path.rglob("*") if item.is_file()]

    @staticmethod
    def _read_skill_md(path: Path) -> tuple[dict[str, Any], str]:
        if not path.exists():
            return {}, ""
        content = path.read_text(encoding="utf-8")
        match = FRONTMATTER_PATTERN.match(content)
        if not match:
            return {}, content.strip()
        frontmatter_text, body = match.groups()
        data = yaml.safe_load(frontmatter_text) or {}
        return (data if isinstance(data, dict) else {}), body.strip()
