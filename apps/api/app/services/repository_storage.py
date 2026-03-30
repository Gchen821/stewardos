from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
import re
from pathlib import Path
from typing import Any

import yaml

from app.config import Settings, get_settings
from app.schemas.repository import RepositoryItem, RepositorySummary

CODE_PATTERN = re.compile(r"^[a-z0-9_]+$")


@dataclass
class RepositoryPaths:
    root: Path
    agents: Path
    skills: Path
    tools: Path


class RepositoryStorageService:
    def __init__(self, settings: Settings):
        root = Path(settings.repository_root_path).resolve()
        self.paths = RepositoryPaths(
            root=root,
            agents=root / settings.repository_agents_dir,
            skills=root / settings.repository_skills_dir,
            tools=root / settings.repository_tools_dir,
        )
        self._agents: list[RepositoryItem] = []
        self._skills: list[RepositoryItem] = []
        self._tools: list[RepositoryItem] = []
        self._invalid_entries: list[str] = []

    def initialize(self, auto_bootstrap: bool) -> None:
        self.ensure_structure()
        if auto_bootstrap:
            self.bootstrap_examples()
        self.scan()

    def ensure_structure(self) -> None:
        self.paths.root.mkdir(parents=True, exist_ok=True)
        self.paths.agents.mkdir(parents=True, exist_ok=True)
        self.paths.skills.mkdir(parents=True, exist_ok=True)
        self.paths.tools.mkdir(parents=True, exist_ok=True)

    def bootstrap_examples(self) -> None:
        self._ensure_example_agent()
        self._ensure_example_skill()
        self._ensure_example_tool()

    def scan(self) -> None:
        self._invalid_entries = []
        self._agents = self._scan_items(
            base=self.paths.agents,
            kind="agent",
            markdown_name="AGENT.md",
        )
        self._skills = self._scan_items(
            base=self.paths.skills,
            kind="skill",
            markdown_name="SKILL.md",
        )
        self._tools = self._scan_items(
            base=self.paths.tools,
            kind="tool",
            markdown_name="TOOL.md",
        )

    def summary(self) -> RepositorySummary:
        return RepositorySummary(
            root_path=str(self.paths.root),
            total_agents=len(self._agents),
            total_skills=len(self._skills),
            total_tools=len(self._tools),
            invalid_entries=self._invalid_entries,
        )

    def list_agents(self) -> list[RepositoryItem]:
        return self._agents

    def list_skills(self) -> list[RepositoryItem]:
        return self._skills

    def list_tools(self) -> list[RepositoryItem]:
        return self._tools

    def get_agent(self, code: str) -> RepositoryItem | None:
        return self._find_by_code(self._agents, code)

    def get_skill(self, code: str) -> RepositoryItem | None:
        return self._find_by_code(self._skills, code)

    def get_tool(self, code: str) -> RepositoryItem | None:
        return self._find_by_code(self._tools, code)

    def get_agent_runtime_config(self, code: str) -> dict[str, Any] | None:
        agent_dir = self.paths.agents / code
        if not agent_dir.exists() or not agent_dir.is_dir():
            return None
        manifest_path = agent_dir / "manifest.yaml"
        manifest = self._read_manifest(manifest_path)
        prompt_file = str(manifest.get("prompt_file", "prompt.md"))
        prompt_path = agent_dir / prompt_file
        prompt_text = prompt_path.read_text(encoding="utf-8") if prompt_path.exists() else ""
        return {
            "code": code,
            "manifest": manifest,
            "manifest_path": str(manifest_path),
            "prompt_path": str(prompt_path),
            "prompt_text": prompt_text,
        }

    @staticmethod
    def _find_by_code(items: list[RepositoryItem], code: str) -> RepositoryItem | None:
        return next((item for item in items if item.code == code), None)

    def _scan_items(self, base: Path, kind: str, markdown_name: str) -> list[RepositoryItem]:
        items: list[RepositoryItem] = []
        for entry in sorted(base.iterdir()):
            if not entry.is_dir():
                continue
            code = entry.name
            if not CODE_PATTERN.match(code):
                self._invalid_entries.append(
                    f"{kind}:{code} invalid code, expected regex {CODE_PATTERN.pattern}",
                )
                continue

            manifest_path = entry / "manifest.yaml"
            markdown_path = entry / markdown_name
            manifest = self._read_manifest(manifest_path)
            if manifest.get("code") and manifest["code"] != code:
                self._invalid_entries.append(
                    f"{kind}:{code} manifest code mismatch ({manifest['code']})",
                )

            item = RepositoryItem(
                kind=kind,
                code=code,
                name=str(manifest.get("name", code)),
                description=_as_optional_str(manifest.get("description")),
                version=_as_optional_str(manifest.get("version")),
                status=_as_optional_str(manifest.get("status")),
                path=str(entry),
                manifest_exists=manifest_path.exists(),
                markdown_exists=markdown_path.exists(),
                extra=self._build_extra(kind=kind, manifest=manifest),
            )
            items.append(item)
        return items

    @staticmethod
    def _build_extra(kind: str, manifest: dict[str, Any]) -> dict[str, object]:
        if kind == "agent":
            return {
                "type": manifest.get("type", "subagent"),
                "allow_chat_select": bool(manifest.get("allow_chat_select", True)),
                "max_risk_level": manifest.get("max_risk_level", "L1"),
                "bound_skills": manifest.get("bound_skills", []),
            }
        if kind == "skill":
            return {
                "risk_level": manifest.get("risk_level", "L1"),
                "entrypoint": manifest.get("entrypoint", "scripts/workflow.py"),
                "bound_tools": manifest.get("bound_tools", []),
            }
        return {
            "risk_level": manifest.get("risk_level", "L1"),
            "runtime_type": manifest.get("runtime_type", "python"),
            "entrypoint": manifest.get("entrypoint", "tool.py"),
        }

    @staticmethod
    def _read_manifest(path: Path) -> dict[str, Any]:
        if not path.exists():
            return {}
        raw = path.read_text(encoding="utf-8")
        data = yaml.safe_load(raw) or {}
        return data if isinstance(data, dict) else {}

    def _ensure_example_agent(self) -> None:
        base = self.paths.agents / "butler"
        base.mkdir(parents=True, exist_ok=True)
        _write_if_missing(
            base / "manifest.yaml",
            (
                "name: Butler\n"
                "code: butler\n"
                "version: 0.1.0\n"
                "type: butler\n"
                "description: 平台主控管家 Agent\n"
                "prompt_file: prompt.md\n"
                "allow_chat_select: true\n"
                "max_risk_level: L1\n"
                "bound_skills:\n"
                "  - knowledge_search\n"
                "status: offline\n"
            ),
        )
        _write_if_missing(
            base / "AGENT.md",
            "# Butler\n\n主控管家 Agent，用于统一接收任务并调度 Skills。\n",
        )
        _write_if_missing(
            base / "prompt.md",
            "# Butler Prompt\n\n你是 StewardOS 的主控管家。\n",
        )

    def _ensure_example_skill(self) -> None:
        base = self.paths.skills / "knowledge_search"
        (base / "scripts").mkdir(parents=True, exist_ok=True)
        _write_if_missing(
            base / "manifest.yaml",
            (
                "name: Knowledge Search\n"
                "code: knowledge_search\n"
                "version: 0.1.0\n"
                "description: 检索知识并返回结构化摘要\n"
                "entrypoint: scripts/workflow.py\n"
                "risk_level: L1\n"
                "bound_tools:\n"
                "  - knowledge_query\n"
                "status: active\n"
            ),
        )
        _write_if_missing(
            base / "SKILL.md",
            "# Knowledge Search\n\nSkill 负责证据检索与摘要编排。\n",
        )
        _write_if_missing(
            base / "scripts" / "workflow.py",
            "def run(payload: dict) -> dict:\n    return {\"ok\": True, \"echo\": payload}\n",
        )

    def _ensure_example_tool(self) -> None:
        base = self.paths.tools / "knowledge_query"
        base.mkdir(parents=True, exist_ok=True)
        _write_if_missing(
            base / "manifest.yaml",
            (
                "name: Knowledge Query\n"
                "code: knowledge_query\n"
                "version: 0.1.0\n"
                "description: 对接外部知识源查询\n"
                "entrypoint: tool.py\n"
                "runtime_type: python\n"
                "risk_level: L1\n"
                "status: active\n"
            ),
        )
        _write_if_missing(
            base / "TOOL.md",
            "# Knowledge Query\n\n底层 Tool，供 Skills 调用。\n",
        )
        _write_if_missing(
            base / "tool.py",
            "def run(payload: dict) -> dict:\n    return {\"result\": [], \"payload\": payload}\n",
        )


def _as_optional_str(value: Any) -> str | None:
    if value is None:
        return None
    return str(value)


def _write_if_missing(path: Path, content: str) -> None:
    if path.exists():
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


@lru_cache
def get_repository_storage_service() -> RepositoryStorageService:
    settings = get_settings()
    service = RepositoryStorageService(settings=settings)
    service.initialize(auto_bootstrap=settings.repository_auto_bootstrap)
    return service
