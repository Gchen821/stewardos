from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    project_name: str = Field(default="StewardOS", alias="PROJECT_NAME")
    app_env: str = Field(default="development", alias="APP_ENV")

    api_host: str = Field(default="0.0.0.0", alias="API_HOST")
    api_port: int = Field(default=8000, alias="API_PORT")
    api_reload: bool = Field(default=True, alias="API_RELOAD")
    api_v1_prefix: str = Field(default="/api/v1", alias="API_V1_PREFIX")

    database_url: str = Field(
        default="postgresql+psycopg://steward:steward_local@localhost:5432/stewardos",
        alias="DATABASE_URL",
    )
    redis_url: str = Field(default="redis://localhost:6379/0", alias="REDIS_URL")
    minio_endpoint: str = Field(default="localhost:9000", alias="MINIO_ENDPOINT")
    repository_root_path: str = Field(
        default="./repositories",
        alias="REPOSITORY_ROOT_PATH",
    )
    repository_agents_dir: str = Field(default="agents", alias="REPOSITORY_AGENTS_DIR")
    repository_skills_dir: str = Field(default="skills", alias="REPOSITORY_SKILLS_DIR")
    repository_tools_dir: str = Field(default="tools", alias="REPOSITORY_TOOLS_DIR")
    repository_auto_bootstrap: bool = Field(
        default=True,
        alias="REPOSITORY_AUTO_BOOTSTRAP",
    )

    @property
    def docs_url(self) -> str:
        return "/docs"


@lru_cache
def get_settings() -> Settings:
    return Settings()
