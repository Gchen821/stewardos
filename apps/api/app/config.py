from functools import lru_cache
import os
from pathlib import Path
from uuid import UUID

from pydantic import AliasChoices, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    project_name: str = Field(default="StewardOS Agent Runtime", alias="PROJECT_NAME")
    app_env: str = Field(default="development", alias="APP_ENV")

    api_host: str = Field(default="0.0.0.0", alias="API_HOST")
    api_port: int = Field(default=8000, alias="API_PORT")
    api_reload: bool = Field(default=True, alias="API_RELOAD")
    api_v1_prefix: str = Field(default="/api/v1", alias="API_V1_PREFIX")

    database_url: str = Field(
        default="postgresql+psycopg://steward:steward_local@localhost:5432/stewardos",
        alias="DATABASE_URL",
    )

    repository_root_path: str = Field(default="./repositories", alias="REPOSITORY_ROOT_PATH")
    gateway_log_dir: str = Field(default="./runtime_logs/gateway", alias="GATEWAY_LOG_DIR")
    gateway_log_preview_chars: int = Field(default=400, alias="GATEWAY_LOG_PREVIEW_CHARS")
    asset_archive_dir_name: str = Field(default="_archive", alias="ASSET_ARCHIVE_DIR_NAME")
    bootstrap_admin_username: str = Field(default="admin", alias="BOOTSTRAP_ADMIN_USERNAME")
    bootstrap_admin_password: str = Field(default="123456", alias="BOOTSTRAP_ADMIN_PASSWORD")

    llm_provider: str = Field(default="auto", alias="LLM_PROVIDER")
    llm_model: str = Field(default="gpt-4o-mini", validation_alias=AliasChoices("LLM_MODEL", "LLM_MODEL_ID"))
    llm_fallback_model: str | None = Field(
        default=None,
        validation_alias=AliasChoices("LLM_FALLBACK_MODEL", "LLM_FALLBACK_MODEL_ID"),
    )
    llm_api_key: str | None = Field(default=None, alias="LLM_API_KEY")
    llm_base_url: str | None = Field(default=None, alias="LLM_BASE_URL")
    llm_timeout_seconds: int = Field(default=60, validation_alias=AliasChoices("LLM_TIMEOUT_SECONDS", "LLM_TIMEOUT"))
    openai_api_key: str | None = Field(default=None, alias="OPENAI_API_KEY")
    modelscope_api_key: str | None = Field(default=None, alias="MODELSCOPE_API_KEY")
    zhipu_api_key: str | None = Field(default=None, alias="ZHIPU_API_KEY")
    anthropic_api_key: str | None = Field(default=None, alias="ANTHROPIC_API_KEY")
    dashscope_api_key: str | None = Field(default=None, alias="DASHSCOPE_API_KEY")

    @property
    def docs_url(self) -> str:
        return "/docs"

    @property
    def app_dir(self) -> Path:
        return Path(__file__).resolve().parents[1]

    @property
    def resolved_repository_root(self) -> Path:
        return (self.app_dir / self.repository_root_path).resolve()

    @property
    def resolved_users_root(self) -> Path:
        return (self.resolved_repository_root / "users").resolve()

    @property
    def resolved_gateway_log_dir(self) -> Path:
        return (self.app_dir / self.gateway_log_dir).resolve()

    def resolved_user_root(self, user_id: UUID | str) -> Path:
        return (self.resolved_users_root / str(user_id)).resolve()

    def resolved_user_config_dir(self, user_id: UUID | str) -> Path:
        return (self.resolved_user_root(user_id) / "config").resolve()

    def ensure_directories(self) -> None:
        self.resolved_repository_root.mkdir(parents=True, exist_ok=True)
        self.resolved_users_root.mkdir(parents=True, exist_ok=True)
        self.resolved_gateway_log_dir.mkdir(parents=True, exist_ok=True)

    def get_env(self, name: str) -> str | None:
        return os.getenv(name)


@lru_cache
def get_settings() -> Settings:
    settings = Settings()
    settings.ensure_directories()
    return settings


def reload_settings() -> Settings:
    get_settings.cache_clear()
    return get_settings()
