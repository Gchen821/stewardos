# PostgreSQL 常用操作指令（StewardOS）

## 1. 当前项目默认连接信息

- Host: `localhost`
- Port: `5432`
- Database: `stewardos`
- Username: `steward`
- Password: `steward_local`
- Container: `stewardos-postgres`

以上来自 `docker-compose.yml` 与 `.env` 当前默认值。

## 2. 进入数据库（容器内）

```bash
docker compose exec postgres psql -U steward -d stewardos
```

退出：

```sql
\q
```

## 3. 直接执行单条 SQL

```bash
docker compose exec -T postgres psql -U steward -d stewardos -c "SELECT now();"
```

## 4. 执行 SQL 文件

```bash
docker compose exec -T postgres psql -U steward -d stewardos -f /dev/stdin < infra/sql/001_init_schema.sql
```

## 5. 查看数据库对象

进入 `psql` 后常用命令：

```sql
\l                 -- 列出数据库
\c stewardos       -- 切换数据库
\dt                -- 列出表
\d users           -- 查看表结构
\dn                -- 列出 schema
```

## 6. 常用查询

```sql
SELECT count(*) FROM information_schema.tables WHERE table_schema='public';
SELECT code FROM roles ORDER BY code;
SELECT code FROM permissions ORDER BY code;
SELECT id, email, display_name FROM users ORDER BY created_at DESC;
```

## 7. 导出与导入

导出（备份）：

```bash
docker compose exec -T postgres pg_dump -U steward -d stewardos > infra/sql/stewardos_backup.sql
```

导入（恢复）：

```bash
docker compose exec -T postgres psql -U steward -d stewardos -f /dev/stdin < infra/sql/stewardos_backup.sql
```

## 8. 重置 public schema（危险）

```bash
docker compose exec -T postgres psql -U steward -d stewardos -c "DROP SCHEMA public CASCADE; CREATE SCHEMA public;"
```

然后重新执行初始化脚本：

```bash
docker compose exec -T postgres psql -U steward -d stewardos -f /dev/stdin < infra/sql/001_init_schema.sql
```

## 9. 连接串（供应用配置）

容器内服务互联（API -> Postgres）：

```text
postgresql+psycopg://steward:steward_local@postgres:5432/stewardos
```

宿主机本地连接：

```text
postgresql://steward:steward_local@localhost:5432/stewardos
```
