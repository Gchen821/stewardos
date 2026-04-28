from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field

from app.schemas.common import ORMModel


class ConversationCreate(BaseModel):
    target_type: str = "agent"
    target_id: int
    title: str = "新会话"


class ConversationRead(ORMModel):
    id: int
    user_id: UUID
    target_type: str
    target_id: int
    title: str
    created_at: datetime
    updated_at: datetime


class MessageCreate(BaseModel):
    conversation_id: int
    sender_role: str
    sender_id: UUID | None = None
    content: str
    message_type: str = "text"
    metadata_json: dict[str, Any] = Field(default_factory=dict)


class MessageRead(ORMModel):
    id: int
    conversation_id: int
    sender_role: str
    sender_id: UUID | None
    content: str
    message_type: str
    metadata_json: dict[str, Any]
    created_at: datetime


class ChatSendRequest(BaseModel):
    conversation_id: int | None = None
    target_type: str = "agent"
    target_id: int
    content: str
    bound_agent_ids: list[int] = Field(default_factory=list)
    bound_skill_ids: list[int] = Field(default_factory=list)
    bound_tool_ids: list[int] = Field(default_factory=list)


class ChatSendResponse(BaseModel):
    conversation_id: int
    reply: str
    job_run_id: int
    selected_model: str
    metadata: dict[str, Any] = Field(default_factory=dict)
