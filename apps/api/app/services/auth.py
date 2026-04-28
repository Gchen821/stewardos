import hashlib

from sqlalchemy.orm import Session

from app.models import User
from app.repositories import UserRepository


def hash_password(password: str) -> str:
    # Placeholder only. Replace with bcrypt/argon2 before production rollout.
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def verify_password(password: str, password_hash: str) -> bool:
    return hash_password(password) == password_hash


class AuthService:
    def __init__(self, session: Session):
        self.session = session
        self.users = UserRepository(session)

    def authenticate(self, username: str, password: str) -> User | None:
        user = self.users.get_by_username(username)
        if user is None:
            return None
        if not verify_password(password, user.password_hash):
            return None
        return user

    def issue_token(self, user: User) -> str:
        return f"mock-token-{user.id}"
