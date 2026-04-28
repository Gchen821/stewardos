from dataclasses import dataclass
from typing import Any, Generic, TypeVar

from fastapi import HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.file_store.asset_manager import AssetFileManager
from app.schemas.runtime import RuntimeAsset

ManifestT = TypeVar("ManifestT", bound=BaseModel)


@dataclass
class RegistryCacheItem:
    runtime: RuntimeAsset


class BaseRegistry(Generic[ManifestT]):
    def __init__(self, session: Session) -> None:
        self.session = session
        self.file_manager = AssetFileManager()
        self.cache_by_id: dict[int, RegistryCacheItem] = {}
        self.cache_by_code: dict[str, RegistryCacheItem] = {}

    @property
    def manifest_model(self) -> type[ManifestT]:
        raise NotImplementedError

    def get_db_record_by_id(self, entity_id: int) -> Any:
        raise NotImplementedError

    def get_db_record_by_code(self, code: str) -> Any:
        raise NotImplementedError

    def load_by_id(self, entity_id: int) -> RuntimeAsset:
        cached = self.cache_by_id.get(entity_id)
        if cached is not None:
            return cached.runtime
        record = self.get_db_record_by_id(entity_id)
        if record is None:
            raise HTTPException(status_code=404, detail="asset not found")
        return self._load_record(record)

    def load_by_code(self, code: str) -> RuntimeAsset:
        cached = self.cache_by_code.get(code)
        if cached is not None:
            return cached.runtime
        record = self.get_db_record_by_code(code)
        if record is None:
            raise HTTPException(status_code=404, detail="asset not found")
        return self._load_record(record)

    def refresh(self, entity_id: int) -> RuntimeAsset:
        self.invalidate(entity_id=entity_id)
        return self.load_by_id(entity_id)

    def invalidate(self, entity_id: int | None = None, code: str | None = None) -> None:
        if entity_id is not None:
            cached = self.cache_by_id.pop(entity_id, None)
            if cached is not None:
                self.cache_by_code.pop(cached.runtime.code, None)
        if code is not None:
            cached = self.cache_by_code.pop(code, None)
            if cached is not None:
                self.cache_by_id.pop(cached.runtime.id, None)

    def _load_record(self, record: Any) -> RuntimeAsset:
        manifest_dict = self.file_manager.read_manifest(record.file_path)
        manifest = self.manifest_model.model_validate(manifest_dict)
        runtime = RuntimeAsset(
            id=record.id,
            code=record.code,
            name=record.name,
            description=record.description,
            file_path=record.file_path,
            manifest=manifest.model_dump(),
        )
        cached = RegistryCacheItem(runtime=runtime)
        self.cache_by_id[record.id] = cached
        self.cache_by_code[record.code] = cached
        return runtime
