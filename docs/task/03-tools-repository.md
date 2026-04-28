# Tools 仓库与绑定机制说明（MVP）

## 1. 工具仓库结构

路径：`apps/api/repositories/tools/<tool_id>/`

最小文件：

- `manifest.yaml`
- `tool.py`（本地工具可执行入口）
- `TOOL.md`（说明）

## 2. 两类工具来源

### local

- `source_type: local`
- 通过 `entrypoint` / `executor` 加载 Python callable（默认 `run(payload)`）

### mcp

- `source_type: mcp`
- 通过 `mcp` 配置映射到统一 executor
- 当前 MVP 支持 `http/sse` 字段约定，按 HTTP invoke 方式调用
- 示例 `web_query` 默认 `enabled: false`，避免在未配置鉴权时阻塞启动

## 3. Agent 绑定策略

### 静态绑定

在 Agent manifest 中填写：

```yaml
bound_tools:
  - knowledge_query
```

### 动态绑定

```yaml
tool_binding_policy:
  tags_any: [search]
  source_types: [local, mcp]
  enabled_only: true
```

绑定流程：

1. 先取静态 `bound_tools`
2. 再按动态策略筛选 registry
3. 合并去重，得到 `available_tools`

## 4. 配置位置

- MCP 地址与调用参数：`apps/api/repositories/tools/*/manifest.yaml`
- MCP token 实际值：`.env`

示例：

```yaml
mcp:
  transport: http
  server_url: ${MCP_WEB_SERVER_URL}
  endpoint: /invoke
  timeout: 20
  auth_env: MCP_WEB_AUTH_TOKEN
```

## 5. 可观测接口

- `GET /api/v1/tools/registry`：查看全部注册工具
- `GET /api/v1/agents/{code}/tools`：查看某 Agent 的最终可用工具集
