#!/usr/bin/env sh
set -eu

python -m app.db.wait_for_db
python -c "from app.db.init_db import init_db; init_db()"

UVICORN_ARGS="app.main:app --host 0.0.0.0 --port ${API_PORT:-8000}"
if [ "${API_RELOAD:-false}" = "true" ]; then
  exec uvicorn ${UVICORN_ARGS} --reload
fi

exec uvicorn ${UVICORN_ARGS}
