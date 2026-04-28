from typing import Any
from uuid import UUID

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.file_store.asset_manager import AssetFileManager
from app.models import Agent, Skill, Tool
from app.repositories import AgentRepository, SkillRepository, ToolRepository
from app.schemas.assets import (
    AgentCreate,
    AgentUpdate,
    AssetKind,
    AssetTemplateContext,
    SkillCreate,
    SkillUpdate,
    ToolCreate,
    ToolUpdate,
)


class AssetService:
    def __init__(self, session: Session):
        self.session = session
        self.agents = AgentRepository(session)
        self.skills = SkillRepository(session)
        self.tools = ToolRepository(session)
        self.file_manager = AssetFileManager()

    def _repos(self, asset_type: AssetKind) -> Any:
        return {"agent": self.agents, "skill": self.skills, "tool": self.tools}[asset_type]

    def list_assets(self, asset_type: AssetKind) -> list[Agent | Skill | Tool]:
        return self._repos(asset_type).list_active()

    def get_asset(self, asset_type: AssetKind, asset_id: int) -> Agent | Skill | Tool:
        asset = self._repos(asset_type).get(asset_id)
        if asset is None or getattr(asset, "is_deleted", False):
            raise HTTPException(status_code=404, detail=f"{asset_type} not found")
        return asset

    def create_agent(self, payload: AgentCreate, owner_user_id: UUID) -> Agent:
        if self.agents.get_by_code(payload.code) is not None:
            raise HTTPException(status_code=409, detail="agent code already exists")
        entity = Agent(
            owner_user_id=owner_user_id,
            code=payload.code,
            name=payload.name,
            description=payload.description,
            type=payload.type,
            runtime_status=payload.runtime_status,
            file_path="__pending_agent_path__",
            manifest_version=payload.manifest_version,
            enabled=True,
            chat_selectable=payload.chat_selectable,
            is_builtin=payload.is_builtin,
        )
        self.agents.add(entity)
        try:
            entity.file_path = self.file_manager.create_asset_directory(
                owner_user_id,
                "agent",
                AssetTemplateContext(
                    owner_user_id=owner_user_id,
                    code=payload.code,
                    name=payload.name,
                    description=payload.description,
                ),
                folder_name=str(entity.id),
            )
            self.session.commit()
        except Exception:
            self.session.rollback()
            raise
        return entity

    def create_skill(self, payload: SkillCreate, owner_user_id: UUID) -> Skill:
        if self.skills.get_by_code(payload.code) is not None:
            raise HTTPException(status_code=409, detail="skill code already exists")
        entity = Skill(
            owner_user_id=owner_user_id,
            code=payload.code,
            name=payload.name,
            description=payload.description,
            category=payload.category,
            file_path="__pending_skill_path__",
            manifest_version=payload.manifest_version,
            enabled=True,
        )
        self.skills.add(entity)
        try:
            entity.file_path = self.file_manager.create_asset_directory(
                owner_user_id,
                "skill",
                AssetTemplateContext(
                    owner_user_id=owner_user_id,
                    code=payload.code,
                    name=payload.name,
                    description=payload.description,
                ),
                folder_name=str(entity.id),
            )
            self.session.commit()
        except Exception:
            self.session.rollback()
            raise
        return entity

    def create_tool(self, payload: ToolCreate, owner_user_id: UUID) -> Tool:
        if self.tools.get_by_code(payload.code) is not None:
            raise HTTPException(status_code=409, detail="tool code already exists")
        entity = Tool(
            owner_user_id=owner_user_id,
            code=payload.code,
            name=payload.name,
            description=payload.description,
            category=payload.category,
            file_path="__pending_tool_path__",
            manifest_version=payload.manifest_version,
            risk_level=payload.risk_level,
            enabled=True,
        )
        self.tools.add(entity)
        try:
            entity.file_path = self.file_manager.create_asset_directory(
                owner_user_id,
                "tool",
                AssetTemplateContext(
                    owner_user_id=owner_user_id,
                    code=payload.code,
                    name=payload.name,
                    description=payload.description,
                ),
                folder_name=str(entity.id),
            )
            self.session.commit()
        except Exception:
            self.session.rollback()
            raise
        return entity

    def update_agent(self, asset_id: int, payload: AgentUpdate) -> Agent:
        entity = self.get_asset("agent", asset_id)
        self._apply_updates(entity, payload.model_dump(exclude_none=True))
        self.session.commit()
        return entity

    def update_skill(self, asset_id: int, payload: SkillUpdate) -> Skill:
        entity = self.get_asset("skill", asset_id)
        self._apply_updates(entity, payload.model_dump(exclude_none=True))
        self.session.commit()
        return entity

    def update_tool(self, asset_id: int, payload: ToolUpdate) -> Tool:
        entity = self.get_asset("tool", asset_id)
        self._apply_updates(entity, payload.model_dump(exclude_none=True))
        self.session.commit()
        return entity

    def toggle_asset(self, asset_type: AssetKind, asset_id: int, enabled: bool) -> Agent | Skill | Tool:
        entity = self.get_asset(asset_type, asset_id)
        entity.enabled = enabled
        self.session.commit()
        return entity

    def soft_delete_asset(self, asset_type: AssetKind, asset_id: int) -> None:
        entity = self.get_asset(asset_type, asset_id)
        entity.is_deleted = True
        entity.enabled = False
        self.file_manager.archive_directory(entity.file_path)
        self.session.commit()

    @staticmethod
    def _apply_updates(entity: Any, values: dict[str, Any]) -> None:
        for key, value in values.items():
            setattr(entity, key, value)
