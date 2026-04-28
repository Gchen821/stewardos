from sqlalchemy import select

from app.models import User
from app.repositories.base import SQLAlchemyRepository


class UserRepository(SQLAlchemyRepository[User]):
    model = User

    def get_by_username(self, username: str) -> User | None:
        return self.session.scalar(select(User).where(User.username == username))
