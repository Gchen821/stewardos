# StewardOS

StewardOS 是一个私人 AI 管家平台的快速原型仓库。当前项目采用前后端全容器化开发模式，前端为 Next.js 控制台，后端为 FastAPI + Agent Runtime 骨架，依赖 PostgreSQL、Redis 和 MinIO。

## 快速启动

```bash
cp .env.example .env
docker compose up --build
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

## 项目结构（自动同步）

运行以下命令更新结构区块：

```bash
make docs-sync
```

<!-- STRUCTURE:START -->
.
- apps
  - api
    - Dockerfile
    - README.md
    - app
      - __init__.py
      - api
        - __init__.py
        - dependencies
        - router.py
        - routes
      - config.py
      - core
        - __init__.py
        - agent
        - llm
        - memory
        - protocols
        - tools
      - domain
        - __init__.py
        - agents
        - audit
        - chat
        - policy
        - skills
      - main.py
      - models
        - __init__.py
      - repositories
        - __init__.py
      - schemas
        - __init__.py
        - chat.py
      - services
        - __init__.py
    - requirements.txt
  - web
    - .gitignore
    - AGENTS.md
    - CLAUDE.md
    - README.md
    - eslint.config.mjs
    - next-env.d.ts
    - next.config.ts
    - package.json
    - pnpm-lock.yaml
    - pnpm-workspace.yaml
    - postcss.config.mjs
    - public
      - file.svg
      - globe.svg
      - next.svg
      - vercel.svg
      - window.svg
    - src
      - app
        - (console)
        - favicon.ico
        - globals.css
        - layout.tsx
        - page.tsx
      - components
        - console-shell.tsx
      - lib
        - api.ts
        - default-data.ts
        - steward-store.tsx
        - types.ts
    - tsconfig.json
- configs
- docs
  - architecture
    - StewardOS-Agent-Runtime-架构设计.md
    - api-contract.md
    - backend-architecture.md
    - database-design.md
    - frontend-architecture.md
    - 私人AI管家平台_快速原型开发文档_v3.md
    - 第七章 构建你的Agent框架.md
    - 第九章 上下文工程.md
    - 第八章 记忆与检索.md
    - 第十三章 智能旅行助手.md
    - 第十六章 毕业设计.md
    - 第十章 智能体通信协议.md
  - prd
  - tasks
- infra
  - docker
  - openapi
  - sql
- packages
  - sdk
  - shared
  - ui
- scripts
  - update-structure-doc.sh
- tests
- .env.example
- docker-compose.yml
- package.json
- Makefile
- pnpm-workspace.yaml
- turbo.json
- tsconfig.base.json
<!-- STRUCTURE:END -->
