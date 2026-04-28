from datetime import datetime, timezone
from uuid import UUID

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models import Conversation, Message
from app.repositories import ConversationRepository, MessageRepository
from app.schemas.conversations import ConversationCreate, MessageCreate


class ConversationService:
    def __init__(self, session: Session):
        self.session = session
        self.conversations = ConversationRepository(session)
        self.messages = MessageRepository(session)

    def list_conversations(self, user_id: UUID) -> list[Conversation]:
        return self.conversations.list_by_user(user_id)

    def create_conversation(self, user_id: UUID, payload: ConversationCreate) -> Conversation:
        conversation = Conversation(
            user_id=user_id,
            target_type=payload.target_type,
            target_id=payload.target_id,
            title=payload.title,
        )
        self.conversations.add(conversation)
        self.session.commit()
        return conversation

    def get_conversation(self, conversation_id: int) -> Conversation:
        conversation = self.conversations.get(conversation_id)
        if conversation is None:
            raise HTTPException(status_code=404, detail="conversation not found")
        return conversation

    def list_messages(self, conversation_id: int) -> list[Message]:
        self.get_conversation(conversation_id)
        return self.messages.list_by_conversation(conversation_id)

    def create_message(self, payload: MessageCreate) -> Message:
        message = Message(
            conversation_id=payload.conversation_id,
            sender_role=payload.sender_role,
            sender_id=payload.sender_id,
            content=payload.content,
            message_type=payload.message_type,
            metadata_json=payload.metadata_json,
            created_at=datetime.now(timezone.utc),
        )
        self.messages.add(message)
        conversation = self.get_conversation(payload.conversation_id)
        conversation.updated_at = datetime.now(timezone.utc)
        self.session.commit()
        return message
