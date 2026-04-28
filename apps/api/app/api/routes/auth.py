from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.dependencies.db import get_db_session
from app.schemas.auth import LoginRequest, LoginResponse
from app.schemas.users import UserRead
from app.services.auth import AuthService
from app.services.user_asset_bootstrap import UserAssetBootstrapService

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=LoginResponse)
def login(payload: LoginRequest, session: Session = Depends(get_db_session)) -> LoginResponse:
    service = AuthService(session)
    user = service.authenticate(payload.username, payload.password)
    if user is None:
        raise HTTPException(status_code=401, detail="invalid username or password")
    bootstrap = UserAssetBootstrapService(session)
    bootstrap.ensure_user_assets(user.id)
    bootstrap.normalize_user_asset_paths(user.id)
    return LoginResponse(access_token=service.issue_token(user), user=UserRead.model_validate(user))
