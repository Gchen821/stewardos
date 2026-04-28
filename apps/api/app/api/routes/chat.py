from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.dependencies.auth import get_current_user
from app.api.dependencies.db import get_db_session
from app.schemas.conversations import ChatSendRequest, ChatSendResponse
from app.schemas.users import UserRead
from app.runtime.chat_runtime import ChatRuntimeService

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("/send", response_model=ChatSendResponse)
def chat_send(
    payload: ChatSendRequest,
    current_user: UserRead = Depends(get_current_user),
    session: Session = Depends(get_db_session),
) -> ChatSendResponse:
    return ChatRuntimeService(session).send(current_user.id, payload)
