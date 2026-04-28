from typing import Any

from pydantic import BaseModel, Field


class AgentEntry(BaseModel):
    prompt: str = "prompt.md"
    runtime: str = "main.py"


class AgentDependencies(BaseModel):
    required_skills: list[str] = Field(default_factory=list)
    default_skills: list[str] = Field(default_factory=list)
    optional_skills: list[str] = Field(default_factory=list)
    default_tools: list[str] = Field(default_factory=list)


class AgentConfig(BaseModel):
    memory_policy: str = "session"
    retrieval_policy: str = "manual"


class AgentManifest(BaseModel):
    id: str
    type: str = "agent"
    name: str
    version: str = "1.0.0"
    description: str = ""
    entry: AgentEntry = Field(default_factory=AgentEntry)
    dependencies: AgentDependencies = Field(default_factory=AgentDependencies)
    config: AgentConfig = Field(default_factory=AgentConfig)


class SkillExposure(BaseModel):
    short_desc: str = ""
    when_to_use: str = ""
    avoid_when: str = ""


class SkillEntry(BaseModel):
    runtime: str = "main.py"
    prompt: str | None = "prompt.md"


class SkillDependencies(BaseModel):
    tools: list[str] = Field(default_factory=list)


class SkillManifest(BaseModel):
    id: str
    type: str = "skill"
    name: str
    version: str = "1.0.0"
    description: str = ""
    llm_exposure: SkillExposure = Field(default_factory=SkillExposure)
    entry: SkillEntry = Field(default_factory=SkillEntry)
    dependencies: SkillDependencies = Field(default_factory=SkillDependencies)
    input_schema: dict[str, Any] = Field(default_factory=dict)


class ToolExposure(BaseModel):
    short_desc: str = ""
    args_desc: str = ""
    caution: str = ""


class ToolEntry(BaseModel):
    runtime: str = "main.py"


class ToolConfig(BaseModel):
    timeout: int = 60
    risk_level: str = "low"


class ToolManifest(BaseModel):
    id: str
    type: str = "tool"
    name: str
    version: str = "1.0.0"
    description: str = ""
    llm_exposure: ToolExposure = Field(default_factory=ToolExposure)
    entry: ToolEntry = Field(default_factory=ToolEntry)
    input_schema: dict[str, Any] = Field(default_factory=dict)
    config: ToolConfig = Field(default_factory=ToolConfig)
