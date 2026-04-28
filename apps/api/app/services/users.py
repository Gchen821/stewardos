from uuid import UUID

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models import User
from app.repositories import UserRepository
from app.schemas.users import UserCreate
from app.services.auth import hash_password
from app.services.user_asset_bootstrap import UserAssetBootstrapService


class UserService:
    def __init__(self, session: Session):
        self.session = session
        self.users = UserRepository(session)

    def create_user(self, payload: UserCreate) -> User:
        if self.users.get_by_username(payload.username) is not None:
            raise HTTPException(status_code=409, detail="username already exists")
        user = User(
            username=payload.username,
            password_hash=hash_password(payload.password),
            status="active",
        )
        self.users.add(user)
        self.session.commit()
        UserAssetBootstrapService(self.session).ensure_user_assets(user.id)
        return user

    def get_user(self, user_id: UUID) -> User:
        user = self.users.get(user_id)
        if user is None:
            raise HTTPException(status_code=404, detail="user not found")
        return user
