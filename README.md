# StewardOS

StewardOS 是一个私人 AI 管家平台的快速原型仓库。当前项目采用前后端全容器化开发模式，前端为 Next.js 控制台，后端为 FastAPI + Agent Runtime 骨架，依赖 PostgreSQL、Redis 和 MinIO。

## 快速启动

```bash
cp .env.example .env
docker compose up --build
```

初始化（按需执行，不会在每次启动自动跑）：

```bash
make infra-bootstrap
```

或仅执行 Redis / MinIO：

```bash
make redis-bootstrap
make minio-bootstrap
```

也可以通过 one-shot profile 触发：

```bash
docker compose --profile bootstrap run --rm redis-init
docker compose --profile bootstrap run --rm minio-init
```

服务地址：

- Web: `http://localhost:3000`
- API Root: `http://localhost:8000/api/v1/`
- API Docs: `http://localhost:8000/docs`
- Health: `http://localhost:8000/api/v1/health`
- PostgreSQL: `localhost:5432`
- Redis: `localhost:6379`
- MinIO API: `http://localhost:9000`
- MinIO Console: `http://localhost:9001`


## 当前状态

- 前端控制台页面已落地：主控聊天、子 Agent 对话、Agent 仓库、Skills 仓库、Tools 仓库、账户设置。
- Agent/Skills 仓库已实现本地状态的权限启用与 CRUD 交互，后端 API 已预留接口常量。
- 后端已落地 Core/Domain 分层骨架与路由蓝图，适合作为下一阶段对接实现基础。

## 文档导航

- 产品范围与 MVP 需求：[私人AI管家平台_快速原型开发文档_v3.md](/home/gc/project/StewardOS/docs/architecture/私人AI管家平台_快速原型开发文档_v3.md)
- Agent Runtime 运行时架构：[StewardOS-Agent-Runtime-架构设计.md](/home/gc/project/StewardOS/docs/architecture/StewardOS-Agent-Runtime-架构设计.md)
- 前端架构设计：[frontend-architecture.md](/home/gc/project/StewardOS/docs/architecture/frontend-architecture.md)
- 后端架构设计：[backend-architecture.md](/home/gc/project/StewardOS/docs/architecture/backend-architecture.md)
- 数据库与存储设计：[database-design.md](/home/gc/project/StewardOS/docs/architecture/database-design.md)
- API 契约草案：[api-contract.md](/home/gc/project/StewardOS/docs/architecture/api-contract.md)
- API 目录蓝图：[apps/api/README.md](/home/gc/project/StewardOS/apps/api/README.md)
- 数据库操作速查：[database-ops-cheatsheet.md](/home/gc/project/StewardOS/infra/sql/database-ops-cheatsheet.md)
- Redis/MinIO 操作速查：[redis-minio-ops-cheatsheet.md](/home/gc/project/StewardOS/infra/sql/redis-minio-ops-cheatsheet.md)

## 项目结构（自动同步）

运行以下命令更新结构区块：

```bash
make docs-sync
```

api/：路由层。定义 HTTP 接口、入参出参、状态码，不写核心业务。
core/：运行时内核。放通用能力抽象（Agent、LLM、Tools、Memory、Protocols、Skills），可被不同业务复用。
domain/：业务编排层。把主控管家/子Agent、会话流程、策略规则组织起来，调用 core 完成执行。
services/：应用服务与外部资源协调。你现在的 repository_storage.py 就是管理 agent/skill/tool 仓库目录的服务。
repositories/：数据访问层（建议逐步补齐）。封装 PostgreSQL/Redis/MinIO 的读写，不让上层直接碰存储细节。
schemas/：Pydantic 请求/响应模型（DTO），用于 API 契约。
models/：数据库实体模型（SQLAlchemy/SQLModel 等），对应表结构。
config.py：统一配置入口（环境变量、默认值、settings）。
main.py：FastAPI 启动入口，组装路由、中间件、生命周期。