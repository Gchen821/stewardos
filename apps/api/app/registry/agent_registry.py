from app.models import Agent
from app.repositories import AgentRepository
from app.registry.base import BaseRegistry
from app.schemas.manifests import AgentManifest


class AgentRegistry(BaseRegistry[AgentManifest]):
    manifest_model = AgentManifest

    def get_db_record_by_id(self, entity_id: int) -> Agent | None:
        return AgentRepository(self.session).get(entity_id)

    def get_db_record_by_code(self, code: str) -> Agent | None:
        return AgentRepository(self.session).get_by_code(code)
