"""Session persistence utility for storing and restoring runtime chat sessions."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime
import json
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class SessionSnapshot:
    session_id: str
    agent_name: str
    created_at: str
    updated_at: str
    history: list[dict[str, Any]]
    metadata: dict[str, Any]


class SessionStore:
    """JSON file session persistence for local runtime debugging."""

    def __init__(self, session_dir: str) -> None:
        self.session_dir = Path(session_dir)
        self.session_dir.mkdir(parents=True, exist_ok=True)

    def save(self, snapshot: SessionSnapshot) -> Path:
        path = self.session_dir / f"{snapshot.session_id}.json"
        path.write_text(json.dumps(asdict(snapshot), ensure_ascii=False, indent=2), encoding="utf-8")
        return path

    def load(self, session_id: str) -> SessionSnapshot | None:
        path = self.session_dir / f"{session_id}.json"
        if not path.exists():
            return None
        data = json.loads(path.read_text(encoding="utf-8"))
        return SessionSnapshot(
            session_id=str(data.get("session_id", session_id)),
            agent_name=str(data.get("agent_name", "")),
            created_at=str(data.get("created_at", datetime.utcnow().isoformat())),
            updated_at=str(data.get("updated_at", datetime.utcnow().isoformat())),
            history=list(data.get("history", [])),
            metadata=dict(data.get("metadata", {})),
        )
