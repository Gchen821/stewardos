from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

from app.schemas.common import ORMModel


class UserCreate(BaseModel):
    username: str
    password: str


class UserRead(ORMModel):
    id: UUID
    username: str
    status: str
    created_at: datetime
    updated_at: datetime
