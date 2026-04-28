# 工具注册与绑定闭环：架构与实现计划（已落地）

## 改造目标

在不重建主干架构的前提下，增强现有：

- `RepositoryStorageService`：负责扫描与清单标准化
- `ToolRegistry`：负责统一注册与查询
- `AgentFactory`：负责 Agent 启动时绑定工具集

最终形成：`扫描 -> 标准化 -> 注册 -> 绑定 -> 可观测` 的最小闭环。

## 目录与模块决策

- 沿用目录：
  - `apps/api/repositories/tools/*`（工具仓库）
  - `apps/api/repositories/agents/*`（Agent 仓库）
  - `apps/api/app/core/tools/*`
  - `apps/api/app/services/*`
  - `apps/api/app/api/routes/*`
- 新增：
  - `apps/api/app/core/tools/spec.py`（统一 ToolSpec）
  - `apps/api/app/services/tool_registry_service.py`（注册与绑定服务）

## 数据与清单规范

工具 manifest 统一字段：

- `tool_id/code/name/description/source_type/enabled/version/tags`
- `input_schema/output_schema/executor`
- MCP 工具附加：
  - `mcp.transport`
  - `mcp.server_url|command`
  - `mcp.timeout`
  - `mcp.auth_env`

Agent manifest 增量字段：

- `bound_tools: []`（静态绑定）
- `tool_binding_policy`（动态策略）
  - `tags_any`
  - `source_types`
  - `enabled_only`

## 持久化与配置方案

- 工具/Agent 元数据：文件仓库 (`repositories/*/manifest.yaml`)
- 鉴权密钥：环境变量（`.env`）
- 运行时 registry：进程内缓存（`ToolRegistryService`）

## 实施顺序（本轮已执行）

1. 扫描层：增强 manifest 标准化输出
2. 注册层：`ToolRegistry` 增加结构化 spec 注册、查询、执行
3. 绑定层：`AgentFactory` 构建时解析静态+动态策略
4. 观测层：新增只读 API 查看工具注册与 Agent 可用工具
5. 配置层：补齐 `.env.example` 与示例 manifest

## MVP 范围

- 支持 local + mcp 同仓注册
- 支持静态+动态混合绑定
- 支持按 `tags/source_type/enabled` 查询
- 支持只读接口：
  - `GET /api/v1/tools/registry`
  - `GET /api/v1/agents/{code}/tools`
