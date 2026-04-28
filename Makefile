.DEFAULT_GOAL := help

.PHONY: help web-install web-dev docker-up docker-down docker-logs docs-sync infra-bootstrap redis-bootstrap minio-bootstrap db-init docker-api docker-apireact

help:
	@printf '%s\n' \
		'Available targets:' \
		'  web-install      Install web dependencies with pnpm' \
		'  web-dev          Start the web dev server' \
		'  docker-up        Start the Docker stack in detached mode' \
		'  docker-api       Recreate only the api container' \
		'  docker-down      Stop the Docker stack' \
		'  docker-logs      Follow Docker Compose logs' \
		'  db-init          Apply the initial PostgreSQL schema' \
		'  redis-bootstrap  Bootstrap Redis data' \
		'  minio-bootstrap  Bootstrap MinIO buckets and policies' \
		'  infra-bootstrap  Run db-init, redis-bootstrap, and minio-bootstrap' \
		'  docs-sync        Refresh generated structure docs'

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

docker-api:
	docker compose up -d --force-recreate --no-deps api

docker-apireact:
	$(MAKE) docker-api
