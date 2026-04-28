from datetime import datetime
from typing import Any, Literal
from uuid import UUID

from pydantic import BaseModel, Field

from app.schemas.common import ORMModel

AssetKind = Literal["agent", "skill", "tool"]


class AssetBase(BaseModel):
    code: str
    name: str
    description: str = ""


class AgentCreate(AssetBase):
    type: str = "default"
    runtime_status: str = "draft"
    manifest_version: str = "1.0.0"
    chat_selectable: bool = True
    is_builtin: bool = False


class AgentUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    type: str | None = None
    runtime_status: str | None = None
    manifest_version: str | None = None
    chat_selectable: bool | None = None


class AgentRead(ORMModel):
    id: int
    owner_user_id: UUID
    code: str
    name: str
    description: str
    type: str
    runtime_status: str
    file_path: str
    manifest_version: str
    enabled: bool
    chat_selectable: bool
    is_builtin: bool
    is_deleted: bool
    created_at: datetime
    updated_at: datetime


class SkillCreate(AssetBase):
    category: str = "general"
    manifest_version: str = "1.0.0"


class SkillUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    category: str | None = None
    manifest_version: str | None = None


class SkillRead(ORMModel):
    id: int
    owner_user_id: UUID
    code: str
    name: str
    description: str
    category: str
    file_path: str
    manifest_version: str
    enabled: bool
    is_deleted: bool
    created_at: datetime
    updated_at: datetime


class ToolCreate(AssetBase):
    category: str = "general"
    manifest_version: str = "1.0.0"
    risk_level: str = "low"


class ToolUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    category: str | None = None
    manifest_version: str | None = None
    risk_level: str | None = None


class ToolRead(ORMModel):
    id: int
    owner_user_id: UUID
    code: str
    name: str
    description: str
    category: str
    file_path: str
    manifest_version: str
    risk_level: str
    enabled: bool
    is_deleted: bool
    created_at: datetime
    updated_at: datetime


class AssetFileUpdate(BaseModel):
    content: str


class AssetFileRead(BaseModel):
    filename: str
    content: str


class AssetManifestRead(BaseModel):
    content: dict[str, Any]


class ToggleResponse(BaseModel):
    id: int
    enabled: bool


class AssetTemplateContext(BaseModel):
    owner_user_id: UUID
    code: str
    name: str
    description: str = ""
