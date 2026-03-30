# StewardOS API（当前结构说明）

本文件说明 `apps/api` 当前后端目录职责和关键文件功能，作为开发对齐基线。

## 1) 总体分层

- `app/api`：HTTP 契约层（路由、请求响应、状态码）。
- `app/domain`：业务编排层（主控/子 Agent、会话流、策略）。
- `app/core`：运行时内核层（Agent/LLM/Tool/Memory/Protocol/Skills 通用能力）。
- `app/services`：应用服务层（当前含仓库扫描与配置读取）。
- `app/schemas`：Pydantic DTO（请求/响应模型）。
- `app/models`：数据库模型层（当前为预留骨架）。
- `app/repositories`：数据访问层（当前为预留骨架）。
- `repositories/`：文件系统资源仓库（agents/skills/tools 实例资源）。

## 2) app 目录与文件作用

### `app/main.py`
- FastAPI 启动入口。
- 负责创建应用实例、挂载路由、定义基础生命周期。

### `app/config.py`
- 全局配置模型（环境变量读取）。
- 定义数据库、Redis、MinIO、仓库路径、API 前缀等配置项。

### `app/api/`
- `router.py`：汇总注册各业务路由。
- `routes/chat.py`：聊天发送、流式输出、RAG 预留接口。
- `routes/agents.py`：Agent 仓库查询接口。
- `routes/skills.py`：Skill 仓库查询接口。
- `routes/tools.py`：Tool 仓库查询接口。
- `routes/models.py`：模型配置相关接口（当前偏骨架）。
- `routes/permissions.py`：权限查询/展示接口（当前偏骨架）。
- `routes/auth.py`：认证接口占位。
- `routes/meta.py`：健康与元信息接口。

### `app/domain/`
- `agents/base.py`：运行时 Agent 基类（profile + RAG 预留）。
- `agents/butler.py`：主控管家执行逻辑（当前可对话骨架）。
- `agents/subagent.py`：子 Agent 执行骨架。
- `agents/factory.py`：按仓库配置构建 Agent 实例。
- `chat/orchestrator.py`：聊天主流程编排（目标解析、上下文装配、分发）。
- `chat/session_service.py`：会话与长上下文拼装。
- `chat/message_service.py`：消息切片/基础处理。
- `skills/*`：技能绑定与运行服务骨架。
- `policy/*`：策略与校验骨架。
- `audit/service.py`：审计服务骨架。

### `app/core/`
- `__init__.py`：内核统一导出入口。
- `exceptions.py`：内核通用异常定义。
- `runtime_config.py`：运行时配置模型（从迁移框架吸收）。
- `lifecycle.py`：Agent 生命周期事件模型。
- `session_store.py`：会话快照读写（本地 JSON）。
- `streaming.py`：SSE 与文本流工具函数。

#### `app/core/agent`
- `base.py`：Agent 抽象、AgentResult、历史能力位。
- `message.py`：统一消息模型（含 Python 3.10 兼容）。
- `context.py`：ContextEnvelope + 统一 ContextBuilder 入口。
- `executor.py`：Agent 执行协调器。
- `gssc_builder.py`：GSSC（Gather/Select/Structure/Compress）上下文构建器。
- `history.py`：历史消息管理与压缩。
- `token_counter.py`：token 估算与缓存计数。
- `truncator.py`：工具输出截断器。
- `patterns/`：高级 Agent 模式（simple/react/reflection/plan），作为可选能力。

#### `app/core/llm`
- `gateway.py`：模型网关抽象与统一返回结构。
- `providers.py`：Provider 网关实现（OpenAI 兼容入口）。
- `router.py`：模型优先级路由（会话覆盖 > Agent 绑定 > 默认）。
- `client.py`：统一 LLM 客户端（流式/工具调用/异步）。
- `adapters.py`：多 Provider 适配器（OpenAI/Anthropic/Gemini 等）。
- `response.py`：LLM 响应数据结构（含 tool call 结构）。

#### `app/core/tools`
- `base.py`：Tool 抽象、ToolResult、ToolParameter。
- `registry.py`：工具注册与执行入口，含熔断器集成。
- `response.py`：标准 ToolResponse 协议。
- `errors.py`：工具错误码定义。
- `circuit_breaker.py`：工具熔断机制。
- `tool_filter.py`：子 Agent 工具过滤策略。
- `skill_tool.py`：执行仓库 Skill entrypoint 的通用工具。
- `memory_tool.py` / `note_tool.py` / `rag_tool.py`：内置工具骨架。
- `protocol_tools.py`：协议适配工具包装。
- `builtin/`：文件操作、待办、任务分派等内置工具集合。

#### `app/core/skills`
- `loader.py`：Skill 元数据 + 正文 + 资源分层加载。
- `registry.py`：Skill 启用状态和运行时绑定注册。

#### `app/core/memory`
- `manager.py`：记忆快照总入口。
- `working.py` / `episodic.py` / `semantic.py`：各类记忆存储骨架。

#### `app/core/protocols`
- `__init__.py`：协议适配抽象定义。
- `mcp.py`：MCP 适配占位。
- `a2a.py`：A2A 适配占位。
- `anp.py`：ANP 适配占位。

#### `app/core/observability`
- `trace_logger.py`：JSONL + HTML 双格式 trace 记录。

### `app/services/`
- `repository_storage.py`：文件仓库扫描、解析、启动自举、运行时配置读取。

### `app/schemas/`
- `chat.py`：聊天请求/响应 DTO。
- `repository.py`：仓库条目 DTO（agent/skill/tool 统一）。

### `app/models/` 与 `app/repositories/`
- 当前主要为后续数据库/缓存访问预留目录，待按数据层计划逐步补齐。

## 3) 文件系统仓库（`apps/api/repositories`）

- `agents/`：Agent 配置与提示词（如 `butler/manifest.yaml`、`prompt.md`）。
- `skills/`：Skill 资源（`manifest.yaml` + `SKILL.md` + `scripts/workflow.py`）。
- `tools/`：Tool 资源（`manifest.yaml` + `TOOL.md` + `tool.py`）。

当前已内置示例：
- Agents：`butler`
- Skills：`knowledge_search`、`web_search`、`web_reader`、`xlsx_recalc`
- Tools：`knowledge_query`、`web_query`、`file_reader`、`spreadsheet_ops`

## 4) 当前可用接口（与结构对应）

- `GET /api/v1/health`
- `GET /api/v1/repository/summary`
- `POST /api/v1/repository/scan`
- `GET /api/v1/agents`
- `GET /api/v1/agents/{code}`
- `GET /api/v1/skills`
- `GET /api/v1/skills/{code}`
- `GET /api/v1/tools`
- `GET /api/v1/tools/{code}`
- `POST /api/v1/chat/send`
- `POST /api/v1/chat/stream`
- `POST /api/v1/chat/rag/search`
