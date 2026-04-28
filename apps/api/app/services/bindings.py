from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models import AgentSkillBinding, AgentToolBinding, SkillToolBinding
from app.repositories import (
    AgentRepository,
    AgentSkillBindingRepository,
    AgentToolBindingRepository,
    SkillRepository,
    SkillToolBindingRepository,
    ToolRepository,
)
from app.schemas.bindings import BindingCreate


class BindingService:
    def __init__(self, session: Session):
        self.session = session
        self.agents = AgentRepository(session)
        self.skills = SkillRepository(session)
        self.tools = ToolRepository(session)
        self.agent_skills = AgentSkillBindingRepository(session)
        self.skill_tools = SkillToolBindingRepository(session)
        self.agent_tools = AgentToolBindingRepository(session)

    def list_agent_skills(self, agent_id: int) -> list[AgentSkillBinding]:
        self._ensure_agent(agent_id)
        return self.agent_skills.list_by_agent(agent_id)

    def bind_agent_skill(self, agent_id: int, skill_id: int, payload: BindingCreate) -> AgentSkillBinding:
        self._ensure_agent(agent_id)
        self._ensure_skill(skill_id)
        existing = self.agent_skills.get_by_unique(agent_id, skill_id)
        if existing is not None:
            existing.enabled = payload.enabled
            existing.sort_order = payload.sort_order
            existing.source = payload.source
            existing.exposure_mode = payload.exposure_mode
            existing.config_json = payload.config_json
            self.session.commit()
            return existing
        binding = AgentSkillBinding(agent_id=agent_id, skill_id=skill_id, **payload.model_dump())
        self.agent_skills.add(binding)
        self.session.commit()
        return binding

    def unbind_agent_skill(self, agent_id: int, skill_id: int) -> None:
        binding = self.agent_skills.get_by_unique(agent_id, skill_id)
        if binding is None:
            raise HTTPException(status_code=404, detail="binding not found")
        self.agent_skills.delete(binding)
        self.session.commit()

    def list_skill_tools(self, skill_id: int) -> list[SkillToolBinding]:
        self._ensure_skill(skill_id)
        return self.skill_tools.list_by_skill(skill_id)

    def bind_skill_tool(self, skill_id: int, tool_id: int, payload: BindingCreate) -> SkillToolBinding:
        self._ensure_skill(skill_id)
        self._ensure_tool(tool_id)
        existing = self.skill_tools.get_by_unique(skill_id, tool_id)
        if existing is not None:
            existing.enabled = payload.enabled
            existing.sort_order = payload.sort_order
            existing.source = payload.source
            existing.exposure_mode = payload.exposure_mode
            existing.config_json = payload.config_json
            self.session.commit()
            return existing
        binding = SkillToolBinding(skill_id=skill_id, tool_id=tool_id, **payload.model_dump())
        self.skill_tools.add(binding)
        self.session.commit()
        return binding

    def unbind_skill_tool(self, skill_id: int, tool_id: int) -> None:
        binding = self.skill_tools.get_by_unique(skill_id, tool_id)
        if binding is None:
            raise HTTPException(status_code=404, detail="binding not found")
        self.skill_tools.delete(binding)
        self.session.commit()

    def list_agent_tools(self, agent_id: int) -> list[AgentToolBinding]:
        self._ensure_agent(agent_id)
        return self.agent_tools.list_by_agent(agent_id)

    def bind_agent_tool(self, agent_id: int, tool_id: int, payload: BindingCreate) -> AgentToolBinding:
        self._ensure_agent(agent_id)
        self._ensure_tool(tool_id)
        existing = self.agent_tools.get_by_unique(agent_id, tool_id)
        if existing is not None:
            existing.enabled = payload.enabled
            existing.sort_order = payload.sort_order
            existing.source = payload.source
            existing.exposure_mode = payload.exposure_mode
            existing.config_json = payload.config_json
            self.session.commit()
            return existing
        binding = AgentToolBinding(agent_id=agent_id, tool_id=tool_id, **payload.model_dump())
        self.agent_tools.add(binding)
        self.session.commit()
        return binding

    def unbind_agent_tool(self, agent_id: int, tool_id: int) -> None:
        binding = self.agent_tools.get_by_unique(agent_id, tool_id)
        if binding is None:
            raise HTTPException(status_code=404, detail="binding not found")
        self.agent_tools.delete(binding)
        self.session.commit()

    def _ensure_agent(self, agent_id: int) -> None:
        if self.agents.get(agent_id) is None:
            raise HTTPException(status_code=404, detail="agent not found")

    def _ensure_skill(self, skill_id: int) -> None:
        if self.skills.get(skill_id) is None:
            raise HTTPException(status_code=404, detail="skill not found")

    def _ensure_tool(self, tool_id: int) -> None:
        if self.tools.get(tool_id) is None:
            raise HTTPException(status_code=404, detail="tool not found")
