# StewardOS API Runtime Blueprint

`apps/api` 当前包含两层结构：

- `app/core`: 可复用的 Agent Runtime Core，定义 Agent、Tool、Memory、Context、Protocol、Model Gateway 等抽象
- `app/domain`: StewardOS 业务运行时，负责主控管家、子 Agent、技能治理、权限策略、聊天编排与审计

约束：

- `api/` 只负责 HTTP 契约
- `core/` 不感知页面语义与业务表结构
- `domain/` 负责业务规则
- `repositories/` 负责 PostgreSQL、Redis、MinIO 等存储访问

推荐实施顺序：

1. 先补 `models/`、`schemas/`、`repositories/`
2. 再补 `domain/chat`、`domain/policy`、`domain/skills`
3. 最后将 `core/memory`、`core/llm`、`core/protocols` 从占位实现替换为真实运行时
