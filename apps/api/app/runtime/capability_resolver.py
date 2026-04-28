from collections import defaultdict

from sqlalchemy.orm import Session

from app.models import Skill, Tool
from app.repositories import (
    AgentSkillBindingRepository,
    AgentToolBindingRepository,
    SkillRepository,
    SkillToolBindingRepository,
    ToolRepository,
)
from app.registry import AgentRegistry, SkillRegistry, ToolRegistry
from app.schemas.runtime import CapabilityResolution, RuntimeAsset


class CapabilityResolver:
    def __init__(self, session: Session) -> None:
        self.session = session
        self.agent_registry = AgentRegistry(session)
        self.skill_registry = SkillRegistry(session)
        self.tool_registry = ToolRegistry(session)
        self.agent_skills = AgentSkillBindingRepository(session)
        self.skill_tools = SkillToolBindingRepository(session)
        self.agent_tools = AgentToolBindingRepository(session)
        self.skills = SkillRepository(session)
        self.tools = ToolRepository(session)

    def resolve_agent_capabilities(self, agent_id: int) -> CapabilityResolution:
        agent = self.agent_registry.load_by_id(agent_id)
        skill_bindings = [item for item in self.agent_skills.list_by_agent(agent_id) if item.enabled]
        direct_tool_bindings = [item for item in self.agent_tools.list_by_agent(agent_id) if item.enabled]

        skill_runtimes: list[RuntimeAsset] = []
        direct_tools: list[RuntimeAsset] = []
        skill_tools: dict[str, list[RuntimeAsset]] = {}
        unique_tools_map: dict[str, RuntimeAsset] = {}
        tool_sources: dict[str, list[str]] = defaultdict(list)

        for binding in skill_bindings:
            skill_record = self.skills.get(binding.skill_id)
            if skill_record is None or not skill_record.enabled or skill_record.is_deleted:
                continue
            skill_runtime = self.skill_registry.load_by_id(skill_record.id)
            skill_runtimes.append(skill_runtime)
            bound_skill_tools: list[RuntimeAsset] = []
            for skill_tool_binding in self.skill_tools.list_by_skill(skill_record.id):
                if not skill_tool_binding.enabled:
                    continue
                tool_record = self.tools.get(skill_tool_binding.tool_id)
                if tool_record is None or not tool_record.enabled or tool_record.is_deleted:
                    continue
                tool_runtime = self.tool_registry.load_by_id(tool_record.id)
                bound_skill_tools.append(tool_runtime)
                unique_tools_map.setdefault(tool_runtime.code, tool_runtime)
                source_tag = f"skill:{skill_runtime.code}"
                if source_tag not in tool_sources[tool_runtime.code]:
                    tool_sources[tool_runtime.code].append(source_tag)
            skill_tools[skill_runtime.code] = bound_skill_tools

        for binding in direct_tool_bindings:
            tool_record = self.tools.get(binding.tool_id)
            if tool_record is None or not tool_record.enabled or tool_record.is_deleted:
                continue
            tool_runtime = self.tool_registry.load_by_id(tool_record.id)
            direct_tools.append(tool_runtime)
            unique_tools_map.setdefault(tool_runtime.code, tool_runtime)
            if "agent_direct" not in tool_sources[tool_runtime.code]:
                tool_sources[tool_runtime.code].append("agent_direct")

        return CapabilityResolution(
            agent=agent,
            skills=skill_runtimes,
            direct_tools=direct_tools,
            skill_tools=skill_tools,
            unique_tools=list(unique_tools_map.values()),
            tool_sources=dict(tool_sources),
        )
