from app.models import Tool
from app.repositories import ToolRepository
from app.registry.base import BaseRegistry
from app.schemas.manifests import ToolManifest


class ToolRegistry(BaseRegistry[ToolManifest]):
    manifest_model = ToolManifest

    def get_db_record_by_id(self, entity_id: int) -> Tool | None:
        return ToolRepository(self.session).get(entity_id)

    def get_db_record_by_code(self, code: str) -> Tool | None:
        return ToolRepository(self.session).get_by_code(code)
