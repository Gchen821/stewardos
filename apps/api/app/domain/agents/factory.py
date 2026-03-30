from __future__ import annotations

from dataclasses import asdict

from app.core.skills.loader import SkillLoader
from app.domain.agents.base import (
    AgentRuntimeProfile,
    build_memory_db_path,
    build_rag_db_path,
)
from app.domain.agents.butler import ButlerAgent
from app.domain.agents.subagent import SubAgentRunner
from app.services.repository_storage import get_repository_storage_service


def create_agent(agent_code: str):
    service = get_repository_storage_service()
    bundle = service.get_agent_runtime_config(agent_code)
    if bundle is None:
        raise ValueError(f"Agent config not found for code='{agent_code}'")

    manifest = bundle.get("manifest", {})
    agent_type = str(manifest.get("type", "subagent"))
    profile = AgentRuntimeProfile(
        code=agent_code,
        name=str(manifest.get("name", agent_code)),
        agent_type=agent_type,
        description=str(manifest.get("description", "")),
        status=str(manifest.get("status", "offline")),
        allow_chat_select=bool(manifest.get("allow_chat_select", True)),
        max_risk_level=str(manifest.get("max_risk_level", "L1")),
        bound_skills=[str(x) for x in manifest.get("bound_skills", [])],
        prompt_text=str(bundle.get("prompt_text", "")),
        manifest_path=str(bundle.get("manifest_path", "")),
        prompt_path=str(bundle.get("prompt_path", "")),
        rag_db_path=build_rag_db_path(service.paths.root.as_posix(), agent_code),
        memory_db_path=build_memory_db_path(service.paths.root.as_posix(), agent_code),
        metadata={"manifest": manifest},
    )
    skill_loader = SkillLoader(skills_dir=service.paths.skills)
    if agent_type == "butler":
        return ButlerAgent(profile=profile, skill_loader=skill_loader)
    return SubAgentRunner(profile=profile, skill_loader=skill_loader)


def inspect_agent_profile(agent_code: str) -> dict[str, object]:
    agent = create_agent(agent_code)
    return asdict(agent.profile)
