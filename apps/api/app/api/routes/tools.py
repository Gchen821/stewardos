from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.dependencies.auth import get_current_user
from app.api.dependencies.db import get_db_session
from app.schemas.assets import ToggleResponse, ToolCreate, ToolRead, ToolUpdate
from app.schemas.users import UserRead
from app.services.assets import AssetService

router = APIRouter(prefix="/tools", tags=["tools"])


@router.get("", response_model=list[ToolRead])
def list_tools(session: Session = Depends(get_db_session)) -> list[ToolRead]:
    return [ToolRead.model_validate(item) for item in AssetService(session).list_assets("tool")]


@router.post("", response_model=ToolRead)
def create_tool(
    payload: ToolCreate,
    current_user: UserRead = Depends(get_current_user),
    session: Session = Depends(get_db_session),
) -> ToolRead:
    entity = AssetService(session).create_tool(payload, owner_user_id=current_user.id)
    return ToolRead.model_validate(entity)


@router.get("/{tool_id}", response_model=ToolRead)
def get_tool(tool_id: int, session: Session = Depends(get_db_session)) -> ToolRead:
    return ToolRead.model_validate(AssetService(session).get_asset("tool", tool_id))


@router.put("/{tool_id}", response_model=ToolRead)
def update_tool(payload: ToolUpdate, tool_id: int, session: Session = Depends(get_db_session)) -> ToolRead:
    return ToolRead.model_validate(AssetService(session).update_tool(tool_id, payload))


@router.delete("/{tool_id}")
def delete_tool(tool_id: int, session: Session = Depends(get_db_session)) -> dict[str, str]:
    AssetService(session).soft_delete_asset("tool", tool_id)
    return {"message": "deleted"}


@router.post("/{tool_id}/enable", response_model=ToggleResponse)
def enable_tool(tool_id: int, session: Session = Depends(get_db_session)) -> ToggleResponse:
    entity = AssetService(session).toggle_asset("tool", tool_id, True)
    return ToggleResponse(id=entity.id, enabled=entity.enabled)


@router.post("/{tool_id}/disable", response_model=ToggleResponse)
def disable_tool(tool_id: int, session: Session = Depends(get_db_session)) -> ToggleResponse:
    entity = AssetService(session).toggle_asset("tool", tool_id, False)
    return ToggleResponse(id=entity.id, enabled=entity.enabled)
