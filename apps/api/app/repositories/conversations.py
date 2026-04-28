from uuid import UUID

from sqlalchemy import select

from app.models import Conversation, Message
from app.repositories.base import SQLAlchemyRepository


class ConversationRepository(SQLAlchemyRepository[Conversation]):
    model = Conversation

    def list_by_user(self, user_id: UUID) -> list[Conversation]:
        return list(
            self.session.scalars(
                select(Conversation).where(Conversation.user_id == user_id).order_by(Conversation.updated_at.desc())
            ).all()
        )


class MessageRepository(SQLAlchemyRepository[Message]):
    model = Message

    def list_by_conversation(self, conversation_id: int) -> list[Message]:
        return list(
            self.session.scalars(
                select(Message).where(Message.conversation_id == conversation_id).order_by(Message.id.asc())
            ).all()
        )
