from fastapi import APIRouter, Body, Depends
from sqlalchemy.orm import Session

from app.api.dependencies.db import get_db_session
from app.schemas.bindings import (
    AgentSkillBindingRead,
    AgentToolBindingRead,
    BindingCreate,
    SkillToolBindingRead,
)
from app.services.bindings import BindingService

router = APIRouter(tags=["bindings"])


@router.get("/agents/{agent_id}/skills", response_model=list[AgentSkillBindingRead])
def list_agent_skills(agent_id: int, session: Session = Depends(get_db_session)) -> list[AgentSkillBindingRead]:
    return [AgentSkillBindingRead.model_validate(item) for item in BindingService(session).list_agent_skills(agent_id)]


@router.post("/agents/{agent_id}/skills/{skill_id}", response_model=AgentSkillBindingRead)
def bind_agent_skill(
    agent_id: int,
    skill_id: int,
    payload: BindingCreate = Body(default_factory=BindingCreate),
    session: Session = Depends(get_db_session),
) -> AgentSkillBindingRead:
    binding = BindingService(session).bind_agent_skill(agent_id, skill_id, payload)
    return AgentSkillBindingRead.model_validate(binding)


@router.delete("/agents/{agent_id}/skills/{skill_id}")
def unbind_agent_skill(agent_id: int, skill_id: int, session: Session = Depends(get_db_session)) -> dict[str, str]:
    BindingService(session).unbind_agent_skill(agent_id, skill_id)
    return {"message": "deleted"}


@router.get("/skills/{skill_id}/tools", response_model=list[SkillToolBindingRead])
def list_skill_tools(skill_id: int, session: Session = Depends(get_db_session)) -> list[SkillToolBindingRead]:
    return [SkillToolBindingRead.model_validate(item) for item in BindingService(session).list_skill_tools(skill_id)]


@router.post("/skills/{skill_id}/tools/{tool_id}", response_model=SkillToolBindingRead)
def bind_skill_tool(
    skill_id: int,
    tool_id: int,
    payload: BindingCreate = Body(default_factory=BindingCreate),
    session: Session = Depends(get_db_session),
) -> SkillToolBindingRead:
    binding = BindingService(session).bind_skill_tool(skill_id, tool_id, payload)
    return SkillToolBindingRead.model_validate(binding)


@router.delete("/skills/{skill_id}/tools/{tool_id}")
def unbind_skill_tool(skill_id: int, tool_id: int, session: Session = Depends(get_db_session)) -> dict[str, str]:
    BindingService(session).unbind_skill_tool(skill_id, tool_id)
    return {"message": "deleted"}


@router.get("/agents/{agent_id}/tools", response_model=list[AgentToolBindingRead])
def list_agent_tools(agent_id: int, session: Session = Depends(get_db_session)) -> list[AgentToolBindingRead]:
    return [AgentToolBindingRead.model_validate(item) for item in BindingService(session).list_agent_tools(agent_id)]


@router.post("/agents/{agent_id}/tools/{tool_id}", response_model=AgentToolBindingRead)
def bind_agent_tool(
    agent_id: int,
    tool_id: int,
    payload: BindingCreate = Body(default_factory=BindingCreate),
    session: Session = Depends(get_db_session),
) -> AgentToolBindingRead:
    binding = BindingService(session).bind_agent_tool(agent_id, tool_id, payload)
    return AgentToolBindingRead.model_validate(binding)


@router.delete("/agents/{agent_id}/tools/{tool_id}")
def unbind_agent_tool(agent_id: int, tool_id: int, session: Session = Depends(get_db_session)) -> dict[str, str]:
    BindingService(session).unbind_agent_tool(agent_id, tool_id)
    return {"message": "deleted"}
