from __future__ import annotations

from dataclasses import dataclass
from shutil import copytree
from typing import Any
from uuid import UUID

from app.file_store.asset_manager import AssetFileManager
from app.schemas.manifests import AgentManifest


@dataclass(frozen=True)
class ControlAgentAsset:
    code: str
    name: str
    description: str
    file_path: str
    prompt_path: str
    runtime_path: str
    prompt: str
    manifest: dict[str, Any]


class ControlAgentLoader:
    CONTROL_AGENT_CODES = ("planner", "reflection")
    _shared_cache: dict[tuple[str, str], ControlAgentAsset] = {}

    def __init__(self, user_id: UUID | str) -> None:
        self.file_manager = AssetFileManager()
        self.user_id = str(user_id)
        self.template_root = self.file_manager.settings.app_dir / "repositories" / "agents"
        self.root = self.file_manager.build_user_asset_root(self.user_id, "agent")
        self.file_manager.ensure_user_directories(self.user_id)

    def warmup(self) -> dict[str, ControlAgentAsset]:
        return self.load_all()

    def load_all(self) -> dict[str, ControlAgentAsset]:
        return {code: self.load(code) for code in self.CONTROL_AGENT_CODES}

    def load(self, code: str) -> ControlAgentAsset:
        cache_key = (str(self.root), code)
        cached = self._shared_cache.get(cache_key)
        if cached is not None:
            return cached

        self._ensure_user_asset(code)
        asset_dir = self.root / code
        if not asset_dir.exists():
            raise RuntimeError(f"control agent asset not found: {asset_dir}")

        manifest_dict = self.file_manager.read_manifest(str(asset_dir))
        manifest = AgentManifest.model_validate(manifest_dict)
        prompt_name = manifest.entry.prompt or "prompt.md"
        runtime_name = manifest.entry.runtime or "main.py"
        prompt_path = asset_dir / prompt_name
        runtime_path = asset_dir / runtime_name

        if not prompt_path.exists():
            raise RuntimeError(f"control agent prompt not found: {prompt_path}")
        if not runtime_path.exists():
            raise RuntimeError(f"control agent runtime not found: {runtime_path}")

        asset = ControlAgentAsset(
            code=manifest.id,
            name=manifest.name,
            description=manifest.description,
            file_path=str(asset_dir),
            prompt_path=str(prompt_path),
            runtime_path=str(runtime_path),
            prompt=prompt_path.read_text(encoding="utf-8"),
            manifest=manifest.model_dump(),
        )
        self._shared_cache[cache_key] = asset
        return asset

    def _ensure_user_asset(self, code: str) -> None:
        target_dir = self.root / code
        if target_dir.exists():
            return
        template_dir = self.template_root / code
        if not template_dir.exists():
            raise RuntimeError(f"control agent template not found: {template_dir}")
        copytree(template_dir, target_dir)
