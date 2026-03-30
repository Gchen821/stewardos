from __future__ import annotations

from abc import abstractmethod
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from app.core.agent.base import Agent, AgentResult
from app.core.agent.context import ContextEnvelope
from app.core.skills.loader import SkillLoader


@dataclass(slots=True)
class AgentRuntimeProfile:
    code: str
    name: str
    agent_type: str
    description: str
    status: str
    allow_chat_select: bool
    max_risk_level: str
    bound_skills: list[str] = field(default_factory=list)
    prompt_text: str = ""
    manifest_path: str = ""
    prompt_path: str = ""
    rag_db_path: str = ""
    memory_db_path: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)


class RuntimeAgentBase(Agent):
    """Base runtime agent initialized from repository manifest + prompt files."""

    def __init__(self, profile: AgentRuntimeProfile, skill_loader: SkillLoader | None = None) -> None:
        super().__init__(name=profile.name, skill_loader=skill_loader)
        self.profile = profile

    def run(self, input_text: str, context: ContextEnvelope) -> AgentResult:
        rag = self.rag_search(input_text=input_text, top_k=3)
        result = self._run_with_profile(input_text=input_text, context=context, rag=rag)
        memory_snapshot = context.metadata.get("memory_snapshot")
        bound_skill_metas: list[dict[str, object]] = []
        if self.skill_loader is not None:
            for code in self.profile.bound_skills:
                meta = self.skill_loader.get_metadata(code)
                if meta is None:
                    bound_skill_metas.append({"code": code, "exists": False})
                else:
                    bound_skill_metas.append(
                        {
                            "code": meta.code,
                            "name": meta.name,
                            "status": meta.status,
                            "risk_level": meta.risk_level,
                            "entrypoint": meta.entrypoint,
                            "exists": True,
                        },
                    )
        result.metadata.update(
            {
                "agent_code": self.profile.code,
                "agent_type": self.profile.agent_type,
                "rag_db_path": self.profile.rag_db_path,
                "bound_skills": self.profile.bound_skills,
                "bound_skill_metas": bound_skill_metas,
                "allow_chat_select": self.profile.allow_chat_select,
                "memory_snapshot": memory_snapshot if isinstance(memory_snapshot, dict) else {},
            },
        )
        return result

    def rag_search(self, input_text: str, top_k: int = 3) -> dict[str, Any]:
        """RAG placeholder per agent.

        Each agent has an independent rag_db_path. Retrieval implementation will be
        added later.
        """
        return {
            "enabled": True,
            "db_path": self.profile.rag_db_path,
            "top_k": top_k,
            "hits": [],
            "note": "RAG retrieval is pending implementation.",
            "query": input_text,
        }

    @abstractmethod
    def _run_with_profile(
        self,
        input_text: str,
        context: ContextEnvelope,
        rag: dict[str, Any],
    ) -> AgentResult:
        raise NotImplementedError


def build_rag_db_path(base_root: str, agent_code: str) -> str:
    return str(Path(base_root) / "rag" / f"{agent_code}.sqlite")


def build_memory_db_path(base_root: str, agent_code: str) -> str:
    return str(Path(base_root) / "memory" / f"{agent_code}.sqlite")
