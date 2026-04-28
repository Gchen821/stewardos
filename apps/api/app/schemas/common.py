from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict


class ORMModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class MessageResponse(BaseModel):
    message: str
    data: Any | None = None


class TimestampedResponse(ORMModel):
    id: int
    created_at: datetime
    updated_at: datetime
