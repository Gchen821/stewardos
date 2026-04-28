from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field

from app.schemas.common import ORMModel


class BindingCreate(BaseModel):
    enabled: bool = True
    sort_order: int = 0
    source: str = "manual"
    exposure_mode: str = "summary"
    config_json: dict[str, Any] = Field(default_factory=dict)


class BindingRead(ORMModel):
    id: int
    enabled: bool
    sort_order: int
    source: str
    exposure_mode: str
    config_json: dict[str, Any]
    created_at: datetime
    updated_at: datetime


class AgentSkillBindingRead(BindingRead):
    agent_id: int
    skill_id: int


class SkillToolBindingRead(BindingRead):
    skill_id: int
    tool_id: int


class AgentToolBindingRead(BindingRead):
    agent_id: int
    tool_id: int
