from sqlalchemy import select

from app.models import AgentSkillBinding, AgentToolBinding, SkillToolBinding
from app.repositories.base import SQLAlchemyRepository


class AgentSkillBindingRepository(SQLAlchemyRepository[AgentSkillBinding]):
    model = AgentSkillBinding

    def list_by_agent(self, agent_id: int) -> list[AgentSkillBinding]:
        return list(
            self.session.scalars(
                select(AgentSkillBinding)
                .where(AgentSkillBinding.agent_id == agent_id)
                .order_by(AgentSkillBinding.sort_order.asc(), AgentSkillBinding.id.asc())
            ).all()
        )

    def get_by_unique(self, agent_id: int, skill_id: int) -> AgentSkillBinding | None:
        return self.session.scalar(
            select(AgentSkillBinding).where(
                AgentSkillBinding.agent_id == agent_id,
                AgentSkillBinding.skill_id == skill_id,
            )
        )


class SkillToolBindingRepository(SQLAlchemyRepository[SkillToolBinding]):
    model = SkillToolBinding

    def list_by_skill(self, skill_id: int) -> list[SkillToolBinding]:
        return list(
            self.session.scalars(
                select(SkillToolBinding)
                .where(SkillToolBinding.skill_id == skill_id)
                .order_by(SkillToolBinding.sort_order.asc(), SkillToolBinding.id.asc())
            ).all()
        )

    def get_by_unique(self, skill_id: int, tool_id: int) -> SkillToolBinding | None:
        return self.session.scalar(
            select(SkillToolBinding).where(
                SkillToolBinding.skill_id == skill_id,
                SkillToolBinding.tool_id == tool_id,
            )
        )


class AgentToolBindingRepository(SQLAlchemyRepository[AgentToolBinding]):
    model = AgentToolBinding

    def list_by_agent(self, agent_id: int) -> list[AgentToolBinding]:
        return list(
            self.session.scalars(
                select(AgentToolBinding)
                .where(AgentToolBinding.agent_id == agent_id)
                .order_by(AgentToolBinding.sort_order.asc(), AgentToolBinding.id.asc())
            ).all()
        )

    def get_by_unique(self, agent_id: int, tool_id: int) -> AgentToolBinding | None:
        return self.session.scalar(
            select(AgentToolBinding).where(
                AgentToolBinding.agent_id == agent_id,
                AgentToolBinding.tool_id == tool_id,
            )
        )
