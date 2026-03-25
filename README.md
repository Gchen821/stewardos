# StewardOS

StewardOS 是一个私人 AI 管家平台的快速原型仓库。当前仓库已经补齐前后端基础模板，并通过 Docker Compose 把 Next.js、FastAPI、PostgreSQL、Redis 和 MinIO 串成了一套可直接运行的全容器化开发环境。

## 当前目录结构

```text
.
├── apps
│   ├── api                 # FastAPI 模板、Dockerfile、requirements
│   └── web                 # Next.js 前端
├── configs                 # 配置模板预留
├── docs                    # PRD、架构和任务文档
├── infra
│   ├── docker              # 容器脚本预留
│   ├── openapi             # OpenAPI 导出预留
│   └── sql                 # SQL 脚本预留
├── packages
│   ├── sdk                 # SDK 预留
│   ├── shared              # 共享类型预留
│   └── ui                  # UI 组件预留
├── scripts                 # 脚本预留
├── tests                   # 测试预留
├── .env.example
├── docker-compose.yml
├── package.json
├── pnpm-workspace.yaml
├── tsconfig.base.json
└── turbo.json
```

## 当前状态

- `apps/web` 提供一个可直接访问 API 文档和健康检查的首页
- `apps/api` 提供 FastAPI 应用入口、配置模块和基础健康检查路由
- `docker-compose.yml` 已接入 PostgreSQL、Redis、MinIO、API、Web 五个容器
- 根目录已具备 monorepo 级别的基础配置，可继续往完整 MVP 演进

## 环境要求

- Node.js 20
- pnpm 10+
- Python 3.11
- Docker / Docker Compose

## 启动方式

### 1. 初始化环境变量

```bash
cp .env.example .env
```

### 2. 一条命令启动全栈容器

```bash
docker compose up --build
```

首次启动会构建 `apps/api` 镜像，并在开发模式挂载代码目录。

启动完成后可访问：

- Web: `http://localhost:3000`
- API Root: `http://localhost:8000/api/v1/`
- API Docs: `http://localhost:8000/docs`
- Health: `http://localhost:8000/api/v1/health`
- PostgreSQL: `localhost:5432`
- Redis: `localhost:6379`
- MinIO API: `http://localhost:9000`
- MinIO Console: `http://localhost:9001`

### 3. 后台运行 / 停止

```bash
docker compose up -d --build
docker compose down
```

### 4. 查看日志

```bash
docker compose logs -f
docker compose logs -f api
docker compose logs -f web
```

### 5. 本地单独启动前端

```bash
cd apps/web
corepack enable
pnpm install
pnpm dev
```

访问地址：`http://localhost:3000`

### 6. 本地单独启动 API

```bash
cd apps/api
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

访问地址：`http://localhost:8000/docs`

### 7. 常用命令

```bash
make web-install
make web-dev
make docker-up
make docker-down
make docker-logs
```

## 下一步建议

1. 在 `apps/api/app` 下继续补数据库会话、鉴权、中间件和业务模块。
2. 在 `packages/shared` 和 `packages/ui` 中落共享类型与通用组件。
3. 把前端首页替换成真实的 Dashboard / Chat / Agents 页面。
4. 为 PostgreSQL、Redis、MinIO 接入初始化脚本、迁移和测试。
