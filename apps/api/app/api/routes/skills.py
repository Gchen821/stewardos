from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.dependencies.auth import get_current_user
from app.api.dependencies.db import get_db_session
from app.schemas.assets import SkillCreate, SkillRead, SkillUpdate, ToggleResponse
from app.schemas.users import UserRead
from app.services.assets import AssetService

router = APIRouter(prefix="/skills", tags=["skills"])


@router.get("", response_model=list[SkillRead])
def list_skills(session: Session = Depends(get_db_session)) -> list[SkillRead]:
    return [SkillRead.model_validate(item) for item in AssetService(session).list_assets("skill")]


@router.post("", response_model=SkillRead)
def create_skill(
    payload: SkillCreate,
    current_user: UserRead = Depends(get_current_user),
    session: Session = Depends(get_db_session),
) -> SkillRead:
    entity = AssetService(session).create_skill(payload, owner_user_id=current_user.id)
    return SkillRead.model_validate(entity)


@router.get("/{skill_id}", response_model=SkillRead)
def get_skill(skill_id: int, session: Session = Depends(get_db_session)) -> SkillRead:
    return SkillRead.model_validate(AssetService(session).get_asset("skill", skill_id))


@router.put("/{skill_id}", response_model=SkillRead)
def update_skill(payload: SkillUpdate, skill_id: int, session: Session = Depends(get_db_session)) -> SkillRead:
    return SkillRead.model_validate(AssetService(session).update_skill(skill_id, payload))


@router.delete("/{skill_id}")
def delete_skill(skill_id: int, session: Session = Depends(get_db_session)) -> dict[str, str]:
    AssetService(session).soft_delete_asset("skill", skill_id)
    return {"message": "deleted"}


@router.post("/{skill_id}/enable", response_model=ToggleResponse)
def enable_skill(skill_id: int, session: Session = Depends(get_db_session)) -> ToggleResponse:
    entity = AssetService(session).toggle_asset("skill", skill_id, True)
    return ToggleResponse(id=entity.id, enabled=entity.enabled)


@router.post("/{skill_id}/disable", response_model=ToggleResponse)
def disable_skill(skill_id: int, session: Session = Depends(get_db_session)) -> ToggleResponse:
    entity = AssetService(session).toggle_asset("skill", skill_id, False)
    return ToggleResponse(id=entity.id, enabled=entity.enabled)
