from sqlalchemy import select

from app.models import Agent, Skill, Tool
from app.repositories.base import SQLAlchemyRepository


class AgentRepository(SQLAlchemyRepository[Agent]):
    model = Agent

    def get_by_code(self, code: str) -> Agent | None:
        return self.session.scalar(select(Agent).where(Agent.code == code, Agent.is_deleted.is_(False)))

    def list_active(self) -> list[Agent]:
        return self.list(Agent.is_deleted.is_(False), order_by=Agent.id.desc())


class SkillRepository(SQLAlchemyRepository[Skill]):
    model = Skill

    def get_by_code(self, code: str) -> Skill | None:
        return self.session.scalar(select(Skill).where(Skill.code == code, Skill.is_deleted.is_(False)))

    def list_active(self) -> list[Skill]:
        return self.list(Skill.is_deleted.is_(False), order_by=Skill.id.desc())


class ToolRepository(SQLAlchemyRepository[Tool]):
    model = Tool

    def get_by_code(self, code: str) -> Tool | None:
        return self.session.scalar(select(Tool).where(Tool.code == code, Tool.is_deleted.is_(False)))

    def list_active(self) -> list[Tool]:
        return self.list(Tool.is_deleted.is_(False), order_by=Tool.id.desc())
