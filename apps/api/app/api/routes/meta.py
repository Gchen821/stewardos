from fastapi import APIRouter, Depends

from app.api.dependencies.auth import get_current_user
from app.runtime.butler_runtime import ButlerRuntimeService
from app.runtime.llm_loader import LLMLoader
from app.schemas.runtime import (
    RepositoryDirectoryBrowseRead,
    LLMSettingsRead,
    LLMSettingsUpdate,
    RepositorySettingsRead,
    RepositorySettingsUpdate,
)
from app.schemas.users import UserRead
from app.services.llm_settings import LLMSettingsService
from app.services.repository_settings import RepositorySettingsService

router = APIRouter(tags=["meta"])


@router.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@router.get("/runtime/info")
def runtime_info() -> dict[str, object]:
    llm = LLMLoader().load()
    butler = ButlerRuntimeService.describe()
    return {
        "mode": "butler-and-agent-chat",
        "runtime_scope": {
            "enabled": ["agent_chat", "butler_orchestration"],
            "reserved": ["multi_agent_collaboration"],
        },
        "butler": butler,
        "llm": llm.model_dump(exclude={"api_key"}),
        "auth": {"default_admin": "admin", "default_password": "123456"},
    }


@router.get("/runtime/llm-settings", response_model=LLMSettingsRead)
def get_llm_settings(current_user: UserRead = Depends(get_current_user)) -> LLMSettingsRead:
    return LLMSettingsService(current_user.id).get_settings_payload()


@router.put("/runtime/llm-settings", response_model=LLMSettingsRead)
def update_llm_settings(payload: LLMSettingsUpdate, current_user: UserRead = Depends(get_current_user)) -> LLMSettingsRead:
    return LLMSettingsService(current_user.id).update_settings(payload)


@router.get("/runtime/repository-settings", response_model=RepositorySettingsRead)
def get_repository_settings(current_user: UserRead = Depends(get_current_user)) -> RepositorySettingsRead:
    return RepositorySettingsService(current_user.id).get_settings_payload()


@router.put("/runtime/repository-settings", response_model=RepositorySettingsRead)
def update_repository_settings(
    payload: RepositorySettingsUpdate,
    current_user: UserRead = Depends(get_current_user),
) -> RepositorySettingsRead:
    return RepositorySettingsService(current_user.id).update_settings(payload)


@router.get("/runtime/repository-directories", response_model=RepositoryDirectoryBrowseRead)
def browse_repository_directories(
    path: str | None = None,
    current_user: UserRead = Depends(get_current_user),
) -> RepositoryDirectoryBrowseRead:
    return RepositorySettingsService(current_user.id).browse_directories(path)
