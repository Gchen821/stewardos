from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.dependencies.auth import get_current_user
from app.api.dependencies.db import get_db_session
from app.schemas.conversations import ConversationCreate, ConversationRead, MessageRead
from app.schemas.users import UserRead
from app.services.conversations import ConversationService

router = APIRouter(prefix="/conversations", tags=["conversations"])


@router.get("", response_model=list[ConversationRead])
def list_conversations(
    current_user: UserRead = Depends(get_current_user),
    session: Session = Depends(get_db_session),
) -> list[ConversationRead]:
    items = ConversationService(session).list_conversations(current_user.id)
    return [ConversationRead.model_validate(item) for item in items]


@router.post("", response_model=ConversationRead)
def create_conversation(
    payload: ConversationCreate,
    current_user: UserRead = Depends(get_current_user),
    session: Session = Depends(get_db_session),
) -> ConversationRead:
    item = ConversationService(session).create_conversation(current_user.id, payload)
    return ConversationRead.model_validate(item)


@router.get("/{conversation_id}/messages", response_model=list[MessageRead])
def list_messages(conversation_id: int, session: Session = Depends(get_db_session)) -> list[MessageRead]:
    items = ConversationService(session).list_messages(conversation_id)
    return [MessageRead.model_validate(item) for item in items]
