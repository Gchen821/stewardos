from app.models import Skill
from app.repositories import SkillRepository
from app.registry.base import BaseRegistry
from app.schemas.manifests import SkillManifest


class SkillRegistry(BaseRegistry[SkillManifest]):
    manifest_model = SkillManifest

    def get_db_record_by_id(self, entity_id: int) -> Skill | None:
        return SkillRepository(self.session).get(entity_id)

    def get_db_record_by_code(self, code: str) -> Skill | None:
        return SkillRepository(self.session).get_by_code(code)
