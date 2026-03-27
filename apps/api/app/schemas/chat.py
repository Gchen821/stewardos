from pydantic import BaseModel, Field


class ChatSendRequest(BaseModel):
    conversation_id: str | None = None
    target_type: str = Field(description="butler or agent")
    target_id: str | None = None
    content: str


class ChatSendResponse(BaseModel):
    reply: str
    selected_model: str
    trace_id: str | None = None
