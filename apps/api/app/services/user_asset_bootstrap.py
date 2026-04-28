from __future__ import annotations

from pathlib import Path
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.file_store.asset_manager import AssetFileManager
from app.models import Agent, Skill, Tool
from app.runtime.control_agent_loader import ControlAgentLoader


class UserAssetBootstrapService:
    def __init__(self, session: Session | None = None) -> None:
        self.session = session
        self.file_manager = AssetFileManager()

    def ensure_user_assets(self, user_id: UUID | str) -> bool:
        user_root = self.file_manager.build_user_root(user_id)
        if user_root.exists():
            return False
        self.file_manager.ensure_user_directories(user_id)
        ControlAgentLoader(user_id).warmup()
        return True

    def normalize_user_asset_paths(self, user_id: UUID | str) -> None:
        if self.session is None:
            return
        self._normalize_rows(Agent, user_id, "agent")
        self._normalize_rows(Skill, user_id, "skill")
        self._normalize_rows(Tool, user_id, "tool")
        self.session.commit()

    def _normalize_rows(self, model: type[Agent] | type[Skill] | type[Tool], user_id: UUID | str, asset_type: str) -> None:
        rows = list(self.session.scalars(select(model).where(model.owner_user_id == user_id)).all())
        for row in rows:
            expected_path = self.file_manager.build_asset_dir(user_id, asset_type, str(row.id))
            current_path = Path(row.file_path)
            if current_path.resolve() == expected_path.resolve():
                continue
            if current_path.exists() and not expected_path.exists():
                expected_path.parent.mkdir(parents=True, exist_ok=True)
                current_path.rename(expected_path)
                row.file_path = str(expected_path)
                continue
            if expected_path.exists():
                row.file_path = str(expected_path)
