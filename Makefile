.PHONY: web-install web-dev docker-up docker-down docker-logs

web-install:
	cd apps/web && corepack enable && pnpm install

web-dev:
	cd apps/web && corepack enable && pnpm dev

docker-up:
	docker compose up -d

docker-down:
	docker compose down

docker-logs:
	docker compose logs -f
