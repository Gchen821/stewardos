from typing import Any

from pydantic import BaseModel, Field


class RuntimeAsset(BaseModel):
    id: int
    code: str
    name: str
    description: str
    file_path: str
    manifest: dict[str, Any]


class ToolSourceMap(BaseModel):
    tool_code: str
    sources: list[str] = Field(default_factory=list)


class CapabilityResolution(BaseModel):
    agent: RuntimeAsset
    skills: list[RuntimeAsset] = Field(default_factory=list)
    direct_tools: list[RuntimeAsset] = Field(default_factory=list)
    skill_tools: dict[str, list[RuntimeAsset]] = Field(default_factory=dict)
    unique_tools: list[RuntimeAsset] = Field(default_factory=list)
    tool_sources: dict[str, list[str]] = Field(default_factory=dict)


class ButlerBindingSnapshot(BaseModel):
    agent_ids: list[int] = Field(default_factory=list)
    skill_ids: list[int] = Field(default_factory=list)
    tool_ids: list[int] = Field(default_factory=list)


class ButlerExecutionTarget(BaseModel):
    asset_type: str
    asset_id: int
    asset_code: str
    asset_name: str
    reason: str = ""
    source: str = ""


class ButlerPlanStep(BaseModel):
    title: str
    detail: str
    target: ButlerExecutionTarget | None = None


class ButlerPlan(BaseModel):
    iteration: int
    objective: str
    summary: str
    controller_code: str = ""
    prompt_preview: str = ""
    memory_notes: list[str] = Field(default_factory=list)
    selected_agents: list[ButlerExecutionTarget] = Field(default_factory=list)
    selected_tools: list[ButlerExecutionTarget] = Field(default_factory=list)
    steps: list[ButlerPlanStep] = Field(default_factory=list)


class ButlerExecutionRecord(BaseModel):
    asset_type: str
    asset_id: int
    asset_code: str
    asset_name: str
    status: str
    detail: str
    result: dict[str, Any] = Field(default_factory=dict)
    tool_sources: dict[str, list[str]] = Field(default_factory=dict)
    error: str | None = None


class ButlerReflection(BaseModel):
    completed: bool
    summary: str
    controller_code: str = ""
    prompt_preview: str = ""
    confidence: float = 0.0
    missing_requirements: list[str] = Field(default_factory=list)
    memory_for_planner: list[str] = Field(default_factory=list)
    blocked_asset_codes: list[str] = Field(default_factory=list)


class ButlerIterationTrace(BaseModel):
    iteration: int
    planner: ButlerPlan
    executions: list[ButlerExecutionRecord] = Field(default_factory=list)
    reflection: ButlerReflection


class ButlerRunTrace(BaseModel):
    goal: str
    completed: bool
    final_output: str
    max_iterations: int
    selected_model: str
    binding_snapshot: ButlerBindingSnapshot = Field(default_factory=ButlerBindingSnapshot)
    iterations: list[ButlerIterationTrace] = Field(default_factory=list)


class LLMRuntimeConfig(BaseModel):
    provider: str
    model: str
    fallback_model: str | None = None
    api_key: str | None = None
    base_url: str | None = None
    timeout_seconds: int = 60


class LLMSettingsUpdate(BaseModel):
    provider: str
    model: str
    fallback_model: str | None = None
    base_url: str | None = None
    timeout_seconds: int = 60
    api_key: str | None = None


class LLMProviderRecord(BaseModel):
    provider: str
    model: str
    fallback_model: str | None = None
    base_url: str | None = None
    timeout_seconds: int = 60
    api_key: str | None = None
    updated_at: str | None = None


class LLMSettingsRead(BaseModel):
    provider: str
    model: str
    fallback_model: str | None = None
    base_url: str | None = None
    api_key: str | None = None
    timeout_seconds: int = 60
    api_key_env_name: str
    api_key_configured: bool = False
    records: dict[str, LLMProviderRecord] = Field(default_factory=dict)
    runtime: LLMRuntimeConfig


class RepositorySettingsUpdate(BaseModel):
    repository_root_path: str


class RepositorySettingsRead(RepositorySettingsUpdate):
    resolved_repository_root: str
    resolved_users_root: str
    resolved_current_user_root: str
    resolved_current_user_config_dir: str


class RepositoryDirectoryEntry(BaseModel):
    name: str
    path: str


class RepositoryDirectoryBrowseRead(BaseModel):
    current_path: str
    parent_path: str | None = None
    directories: list[RepositoryDirectoryEntry] = Field(default_factory=list)
