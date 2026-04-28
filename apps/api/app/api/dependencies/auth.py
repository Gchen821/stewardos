from uuid import UUID

from fastapi import Depends, Header, HTTPException
from sqlalchemy.orm import Session

from app.api.dependencies.db import get_db_session
from app.repositories import UserRepository
from app.schemas.users import UserRead


def get_current_user(
    authorization: str | None = Header(default=None),
    session: Session = Depends(get_db_session),
) -> UserRead:
    if authorization and authorization.startswith("Bearer mock-token-"):
        token_user_id = authorization.removeprefix("Bearer mock-token-")
        try:
            parsed_user_id = UUID(token_user_id)
        except ValueError:
            parsed_user_id = None
        if parsed_user_id is not None:
            user = UserRepository(session).get(parsed_user_id)
            if user is not None:
                return UserRead.model_validate(user)
    admin = UserRepository(session).get_by_username("admin")
    if admin is None:
        raise HTTPException(status_code=401, detail="authentication required")
    return UserRead.model_validate(admin)
