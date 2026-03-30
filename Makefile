.PHONY: web-install web-dev docker-up docker-down docker-logs docs-sync infra-bootstrap redis-bootstrap minio-bootstrap db-init

web-install:
	cd apps/web && corepack enable && pnpm install

web-dev:
	cd apps/web && corepack enable && pnpm dev

docker-up:
	docker compose up -d

db-init:
	docker compose exec -T postgres psql -U steward -d stewardos -f /dev/stdin < infra/sql/001_init_schema.sql

redis-bootstrap:
	bash infra/sql/002_redis_bootstrap.sh

minio-bootstrap:
	bash infra/sql/003_minio_bootstrap.sh

infra-bootstrap:
	$(MAKE) db-init
	$(MAKE) redis-bootstrap
	$(MAKE) minio-bootstrap

docker-down:
	docker compose down

docker-logs:
	docker compose logs -f

docs-sync:
	./scripts/update-structure-doc.sh
