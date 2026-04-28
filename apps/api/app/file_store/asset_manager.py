from pathlib import Path
import shutil
from typing import Any
from uuid import UUID

import yaml

from app.config import get_settings
from app.schemas.assets import AssetKind, AssetTemplateContext


class AssetFileManager:
    TEXT_FILES = {"README.md", "prompt.md", "main.py", "schema.json"}

    def __init__(self) -> None:
        self.settings = get_settings()
        self.root = self.settings.resolved_repository_root
        self.archive_root = self.root / self.settings.asset_archive_dir_name
        self.archive_root.mkdir(parents=True, exist_ok=True)

    def build_user_root(self, owner_user_id: UUID | str) -> Path:
        return self.settings.resolved_user_root(owner_user_id)

    def build_user_asset_root(self, owner_user_id: UUID | str, asset_type: AssetKind) -> Path:
        return self.build_user_root(owner_user_id) / f"{asset_type}s"

    def build_asset_dir(self, owner_user_id: UUID | str, asset_type: AssetKind, folder_name: str) -> Path:
        return self.build_user_asset_root(owner_user_id, asset_type) / folder_name

    def ensure_user_directories(self, owner_user_id: UUID | str) -> None:
        user_root = self.build_user_root(owner_user_id)
        for directory in [
            user_root,
            user_root / "agents",
            user_root / "skills",
            user_root / "tools",
            user_root / "config",
        ]:
            directory.mkdir(parents=True, exist_ok=True)

    def create_asset_directory(
        self,
        owner_user_id: UUID | str,
        asset_type: AssetKind,
        context: AssetTemplateContext,
        folder_name: str | None = None,
    ) -> str:
        self.ensure_user_directories(owner_user_id)
        asset_dir = self.build_asset_dir(owner_user_id, asset_type, folder_name or context.code)
        asset_dir.mkdir(parents=True, exist_ok=True)
        (asset_dir / "resources").mkdir(exist_ok=True)

        manifest = self.default_manifest(asset_type, context)
        self.write_manifest(asset_dir, manifest)
        self.update_file(asset_dir, "README.md", f"# {context.name}\n\n{context.description or 'Describe this asset.'}\n")
        if asset_type == "agent":
            self.update_file(asset_dir, "prompt.md", f"You are {context.name}.")
        self.update_file(asset_dir, "main.py", self.default_runtime_stub(asset_type, context.code))
        self.update_file(asset_dir, "schema.json", "{\n  \"type\": \"object\",\n  \"properties\": {}\n}\n")
        return str(asset_dir)

    def default_manifest(self, asset_type: AssetKind, context: AssetTemplateContext) -> dict[str, Any]:
        if asset_type == "agent":
            return {
                "id": context.code,
                "type": "agent",
                "name": context.name,
                "version": "1.0.0",
                "description": context.description,
                "entry": {"prompt": "prompt.md", "runtime": "main.py"},
                "dependencies": {
                    "required_skills": [],
                    "default_skills": [],
                    "optional_skills": [],
                    "default_tools": [],
                },
                "config": {"memory_policy": "session", "retrieval_policy": "manual"},
            }
        if asset_type == "skill":
            return {
                "id": context.code,
                "type": "skill",
                "name": context.name,
                "version": "1.0.0",
                "description": context.description,
                "llm_exposure": {"short_desc": context.description, "when_to_use": "", "avoid_when": ""},
                "entry": {"runtime": "main.py", "prompt": "prompt.md"},
                "dependencies": {"tools": []},
                "input_schema": {},
            }
        return {
            "id": context.code,
            "type": "tool",
            "name": context.name,
            "version": "1.0.0",
            "description": context.description,
            "llm_exposure": {"short_desc": context.description, "args_desc": "", "caution": ""},
            "entry": {"runtime": "main.py"},
            "input_schema": {},
            "config": {"timeout": 60, "risk_level": "low"},
        }

    def default_runtime_stub(self, asset_type: AssetKind, code: str) -> str:
        return (
            "def run(context: dict) -> dict:\n"
            f"    return {{'asset_type': '{asset_type}', 'asset_code': '{code}', 'context': context}}\n"
        )

    def write_manifest(self, asset_dir: Path, content: dict[str, Any]) -> None:
        (asset_dir / "manifest.yaml").write_text(yaml.safe_dump(content, allow_unicode=True, sort_keys=False), encoding="utf-8")

    def read_manifest(self, file_path: str) -> dict[str, Any]:
        return yaml.safe_load((Path(file_path) / "manifest.yaml").read_text(encoding="utf-8")) or {}

    def read_file(self, file_path: str, filename: str) -> str:
        return (Path(file_path) / filename).read_text(encoding="utf-8")

    def update_file(self, file_path: str | Path, filename: str, content: str) -> None:
        target = Path(file_path) / filename
        target.write_text(content, encoding="utf-8")

    def file_exists(self, file_path: str, filename: str) -> bool:
        return (Path(file_path) / filename).exists()

    def archive_directory(self, file_path: str) -> None:
        source = Path(file_path)
        if not source.exists():
            return
        destination = self.archive_root / source.relative_to(self.root)
        destination.parent.mkdir(parents=True, exist_ok=True)
        if destination.exists():
            shutil.rmtree(destination)
        shutil.move(str(source), str(destination))
