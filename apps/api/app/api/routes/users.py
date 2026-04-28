from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.dependencies.auth import get_current_user
from app.api.dependencies.db import get_db_session
from app.schemas.users import UserCreate, UserRead
from app.services.users import UserService

router = APIRouter(prefix="/users", tags=["users"])


@router.post("", response_model=UserRead)
def create_user(payload: UserCreate, session: Session = Depends(get_db_session)) -> UserRead:
    return UserRead.model_validate(UserService(session).create_user(payload))


@router.get("/me", response_model=UserRead)
def get_me(current_user: UserRead = Depends(get_current_user)) -> UserRead:
    return current_user
