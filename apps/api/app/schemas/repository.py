from pydantic import BaseModel, Field


class RepositoryItem(BaseModel):
    kind: str = Field(description="agent|skill|tool")
    code: str
    name: str
    description: str | None = None
    version: str | None = None
    status: str | None = None
    path: str
    manifest_exists: bool = False
    markdown_exists: bool = False
    extra: dict[str, object] = Field(default_factory=dict)


class RepositorySummary(BaseModel):
    root_path: str
    total_agents: int
    total_skills: int
    total_tools: int
    invalid_entries: list[str] = Field(default_factory=list)
