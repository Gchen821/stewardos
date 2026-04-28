from fastapi import HTTPException
from pathlib import Path
from uuid import UUID

from app.config import get_settings, reload_settings
from app.schemas.runtime import (
    RepositoryDirectoryBrowseRead,
    RepositoryDirectoryEntry,
    RepositorySettingsRead,
    RepositorySettingsUpdate,
)
from app.services.user_asset_bootstrap import UserAssetBootstrapService


class RepositorySettingsService:
    def __init__(self, user_id: UUID) -> None:
        self.settings = get_settings()
        self.env_path = Path.cwd() / ".env"
        self.user_id = user_id

    def get_settings_payload(self) -> RepositorySettingsRead:
        settings = get_settings()
        return RepositorySettingsRead(
            repository_root_path=settings.repository_root_path,
            resolved_repository_root=str(settings.resolved_repository_root),
            resolved_users_root=str(settings.resolved_users_root),
            resolved_current_user_root=str(settings.resolved_user_root(self.user_id)),
            resolved_current_user_config_dir=str(settings.resolved_user_config_dir(self.user_id)),
        )

    def browse_directories(self, path: str | None = None) -> RepositoryDirectoryBrowseRead:
        settings = get_settings()
        current_path = self._resolve_directory_path(path, settings.resolved_repository_root.parent, settings.app_dir)

        if not current_path.exists():
            raise HTTPException(status_code=404, detail="目录不存在")
        if not current_path.is_dir():
            raise HTTPException(status_code=400, detail="目标不是文件夹")

        directories = [
            RepositoryDirectoryEntry(name=child.name, path=str(child.resolve()))
            for child in sorted(current_path.iterdir(), key=lambda item: item.name.lower())
            if child.is_dir()
        ]
        parent_path = str(current_path.parent.resolve()) if current_path.parent != current_path else None

        return RepositoryDirectoryBrowseRead(
            current_path=str(current_path.resolve()),
            parent_path=parent_path,
            directories=directories,
        )

    def update_settings(self, payload: RepositorySettingsUpdate) -> RepositorySettingsRead:
        updates = {
            "REPOSITORY_ROOT_PATH": payload.repository_root_path,
        }
        self._write_env(updates)
        self.settings = reload_settings()
        self._ensure_current_user_directories()
        return self.get_settings_payload()

    def _write_env(self, updates: dict[str, str]) -> None:
        existing_lines = self.env_path.read_text(encoding="utf-8").splitlines() if self.env_path.exists() else []
        seen: set[str] = set()
        next_lines: list[str] = []

        for line in existing_lines:
            stripped = line.strip()
            if not stripped or stripped.startswith("#") or "=" not in line:
                next_lines.append(line)
                continue

            key, _, _ = line.partition("=")
            env_key = key.strip()
            if env_key in updates:
                next_lines.append(f"{env_key}={updates[env_key]}")
                seen.add(env_key)
            else:
                next_lines.append(line)

        if next_lines and next_lines[-1] != "":
            next_lines.append("")

        for key, value in updates.items():
            if key in seen:
                continue
            next_lines.append(f"{key}={value}")

        self.env_path.write_text("\n".join(next_lines).rstrip() + "\n", encoding="utf-8")

    def _resolve_directory_path(self, raw_path: str | None, default_path: Path, app_dir: Path) -> Path:
        if not raw_path:
            return default_path.resolve()

        candidate = Path(raw_path).expanduser()
        if candidate.is_absolute():
            return candidate.resolve()
        return (app_dir / candidate).resolve()

    def _ensure_current_user_directories(self) -> None:
        UserAssetBootstrapService().ensure_user_assets(self.user_id)
