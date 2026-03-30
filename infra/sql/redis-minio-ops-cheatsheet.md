# Redis / MinIO 常用操作指令（StewardOS）

## 1. Redis 连接信息（当前默认）

- Host: `localhost`
- Port: `6379`
- DB: `0`
- Password: 未设置（默认无密码）
- Container: `stewardos-redis`

进入 Redis CLI：

```bash
docker compose exec redis redis-cli
```

进入指定 DB：

```bash
docker compose exec redis redis-cli -n 0
```

常用命令：

```bash
PING
SELECT 0
KEYS steward:*
GET steward:config:namespace
SMEMBERS steward:agent:online:set
XRANGE steward:jobs:stream - +
XINFO GROUPS steward:jobs:stream
```

执行 bootstrap 脚本：

```bash
bash infra/sql/002_redis_bootstrap.sh
```

---

## 2. MinIO 连接信息（当前默认）

- API Endpoint: `http://localhost:9000`
- Console: `http://localhost:9001`
- Access Key: `minioadmin`
- Secret Key: `minioadmin`
- Container: `stewardos-minio`

查看桶列表（使用容器内 `mc`）：

```bash
docker compose exec minio mc alias set local http://localhost:9000 minioadmin minioadmin
docker compose exec minio mc ls local
```

常用命令：

```bash
docker compose exec minio mc mb --ignore-existing local/agent-assets
docker compose exec minio mc mb --ignore-existing local/chat-attachments
docker compose exec minio mc ls local/agent-assets
docker compose exec minio mc stat local/agent-assets/.keep
```

执行 bootstrap 脚本：

```bash
bash infra/sql/003_minio_bootstrap.sh
```

---

## 3. 一键执行 Redis + MinIO 初始化

```bash
bash infra/sql/002_redis_bootstrap.sh
bash infra/sql/003_minio_bootstrap.sh
```

使用 Makefile：

```bash
make redis-bootstrap
make minio-bootstrap
make infra-bootstrap
```

使用 docker compose one-shot profile（默认不会自动执行）：

```bash
docker compose --profile bootstrap run --rm redis-init
docker compose --profile bootstrap run --rm minio-init
```
