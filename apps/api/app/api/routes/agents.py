from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.dependencies.auth import get_current_user
from app.api.dependencies.db import get_db_session
from app.runtime.capability_resolver import CapabilityResolver
from app.schemas.assets import AgentCreate, AgentRead, AgentUpdate, ToggleResponse
from app.schemas.runtime import CapabilityResolution
from app.schemas.users import UserRead
from app.services.assets import AssetService

router = APIRouter(prefix="/agents", tags=["agents"])


@router.get("", response_model=list[AgentRead])
def list_agents(session: Session = Depends(get_db_session)) -> list[AgentRead]:
    return [AgentRead.model_validate(item) for item in AssetService(session).list_assets("agent")]


@router.post("", response_model=AgentRead)
def create_agent(
    payload: AgentCreate,
    current_user: UserRead = Depends(get_current_user),
    session: Session = Depends(get_db_session),
) -> AgentRead:
    entity = AssetService(session).create_agent(payload, owner_user_id=current_user.id)
    return AgentRead.model_validate(entity)


@router.get("/{agent_id}", response_model=AgentRead)
def get_agent(agent_id: int, session: Session = Depends(get_db_session)) -> AgentRead:
    return AgentRead.model_validate(AssetService(session).get_asset("agent", agent_id))


@router.put("/{agent_id}", response_model=AgentRead)
def update_agent(payload: AgentUpdate, agent_id: int, session: Session = Depends(get_db_session)) -> AgentRead:
    return AgentRead.model_validate(AssetService(session).update_agent(agent_id, payload))


@router.delete("/{agent_id}")
def delete_agent(agent_id: int, session: Session = Depends(get_db_session)) -> dict[str, str]:
    AssetService(session).soft_delete_asset("agent", agent_id)
    return {"message": "deleted"}


@router.post("/{agent_id}/enable", response_model=ToggleResponse)
def enable_agent(agent_id: int, session: Session = Depends(get_db_session)) -> ToggleResponse:
    entity = AssetService(session).toggle_asset("agent", agent_id, True)
    return ToggleResponse(id=entity.id, enabled=entity.enabled)


@router.post("/{agent_id}/disable", response_model=ToggleResponse)
def disable_agent(agent_id: int, session: Session = Depends(get_db_session)) -> ToggleResponse:
    entity = AssetService(session).toggle_asset("agent", agent_id, False)
    return ToggleResponse(id=entity.id, enabled=entity.enabled)


@router.get("/{agent_id}/capabilities", response_model=CapabilityResolution)
def get_capabilities(agent_id: int, session: Session = Depends(get_db_session)) -> CapabilityResolution:
    return CapabilityResolver(session).resolve_agent_capabilities(agent_id)
