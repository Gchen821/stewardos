# StewardOS Task 文档入口

本目录记录“工具注册与绑定闭环（真实 MCP）”本轮实施内容，代码与文档一一对应。

## 本轮目标

- 统一注册本地工具与 MCP 工具
- Agent 同时支持静态绑定与动态绑定
- 运行时可观测当前 Agent 的可用工具集
- 提供只读 API 便于前端与调试联动

## 文档索引

- [01-architecture-and-implementation-plan.md](./01-architecture-and-implementation-plan.md)
- [03-tools-repository.md](./03-tools-repository.md)

## 配置入口

- MCP 服务地址与参数：`apps/api/repositories/tools/*/manifest.yaml` 的 `mcp` 段
- 鉴权变量值：根目录 `.env`（参考 `.env.example` 的 `MCP_*` 示例）
