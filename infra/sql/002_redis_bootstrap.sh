#!/usr/bin/env bash
set -euo pipefail

REDIS_SERVICE="${REDIS_SERVICE:-redis}"
REDIS_DB="${REDIS_DB:-0}"

echo "[redis] bootstrap start (service=${REDIS_SERVICE}, db=${REDIS_DB})"

docker compose exec -T "${REDIS_SERVICE}" redis-cli -n "${REDIS_DB}" SET steward:config:namespace stewardos >/dev/null
docker compose exec -T "${REDIS_SERVICE}" redis-cli -n "${REDIS_DB}" SET steward:config:session_ttl_seconds 7200 >/dev/null
docker compose exec -T "${REDIS_SERVICE}" redis-cli -n "${REDIS_DB}" SADD steward:agent:online:set butler >/dev/null

# Create streams if missing and try creating consumer groups in idempotent mode.
docker compose exec -T "${REDIS_SERVICE}" redis-cli -n "${REDIS_DB}" XADD steward:jobs:stream '*' type bootstrap status ok >/dev/null
docker compose exec -T "${REDIS_SERVICE}" redis-cli -n "${REDIS_DB}" XADD steward:audit:stream '*' type bootstrap status ok >/dev/null

docker compose exec -T "${REDIS_SERVICE}" sh -lc "redis-cli -n ${REDIS_DB} XGROUP CREATE steward:jobs:stream steward-jobs-cg \$ MKSTREAM 2>/dev/null || true"
docker compose exec -T "${REDIS_SERVICE}" sh -lc "redis-cli -n ${REDIS_DB} XGROUP CREATE steward:audit:stream steward-audit-cg \$ MKSTREAM 2>/dev/null || true"

echo "[redis] bootstrap done"
