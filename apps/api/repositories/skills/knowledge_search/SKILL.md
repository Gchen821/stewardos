---
name: Knowledge Search
description: 查询知识库并返回结构化摘要。
---

# Knowledge Search

该技能遵循仓库规范：`manifest.yaml + SKILL.md + scripts/workflow.py`。

默认行为：
- 接收 `query` / `limit` 参数。
- 调用绑定工具 `knowledge_query`（当前为占位实现）。
- 输出标准结构，供 Agent 编排层统一处理。
