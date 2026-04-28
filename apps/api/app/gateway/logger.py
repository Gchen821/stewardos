from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from threading import Lock
from typing import Any
from uuid import UUID

from app.config import get_settings


class GatewayAuditLogger:
    _lock = Lock()

    def __init__(self) -> None:
        self.settings = get_settings()

    def write_event(self, payload: dict[str, Any]) -> None:
        event = {"ts": datetime.now(timezone.utc).isoformat(), **payload}
        path = self._resolve_log_path()
        line = json.dumps(event, ensure_ascii=False, default=self._json_default)
        with self._lock:
            path.parent.mkdir(parents=True, exist_ok=True)
            with path.open("a", encoding="utf-8") as handle:
                handle.write(line)
                handle.write("\n")

    def _resolve_log_path(self) -> Path:
        return self.settings.resolved_gateway_log_dir / f"{datetime.now(timezone.utc).date().isoformat()}.jsonl"

    @staticmethod
    def _json_default(value: Any) -> str:
        if isinstance(value, datetime):
            return value.isoformat()
        if isinstance(value, UUID):
            return str(value)
        return str(value)
