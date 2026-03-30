#!/usr/bin/env bash
set -euo pipefail

MINIO_SERVICE="${MINIO_SERVICE:-minio}"
MINIO_ALIAS="${MINIO_ALIAS:-local}"
MINIO_ENDPOINT="${MINIO_ENDPOINT:-http://localhost:9000}"
MINIO_ACCESS_KEY="${MINIO_ACCESS_KEY:-minioadmin}"
MINIO_SECRET_KEY="${MINIO_SECRET_KEY:-minioadmin}"

echo "[minio] bootstrap start (service=${MINIO_SERVICE}, endpoint=${MINIO_ENDPOINT})"

docker compose exec -T "${MINIO_SERVICE}" mc alias set "${MINIO_ALIAS}" "${MINIO_ENDPOINT}" "${MINIO_ACCESS_KEY}" "${MINIO_SECRET_KEY}" >/dev/null

for bucket in agent-assets chat-attachments audit-snapshots imports-exports; do
  docker compose exec -T "${MINIO_SERVICE}" mc mb --ignore-existing "${MINIO_ALIAS}/${bucket}" >/dev/null
done

# Write idempotent placeholder objects.
docker compose exec -T "${MINIO_SERVICE}" sh -lc "echo stewardos | mc pipe ${MINIO_ALIAS}/agent-assets/.keep >/dev/null"
docker compose exec -T "${MINIO_SERVICE}" sh -lc "echo stewardos | mc pipe ${MINIO_ALIAS}/chat-attachments/.keep >/dev/null"
docker compose exec -T "${MINIO_SERVICE}" sh -lc "echo stewardos | mc pipe ${MINIO_ALIAS}/audit-snapshots/.keep >/dev/null"
docker compose exec -T "${MINIO_SERVICE}" sh -lc "echo stewardos | mc pipe ${MINIO_ALIAS}/imports-exports/.keep >/dev/null"

echo "[minio] bootstrap done"
