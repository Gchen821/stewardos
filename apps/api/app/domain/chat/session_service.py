from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from threading import RLock
import uuid


@dataclass(slots=True)
class SessionTurn:
    role: str
    content: str
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass(slots=True)
class SessionState:
    conversation_id: str
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    summary: str = ""
    turns: list[SessionTurn] = field(default_factory=list)


class SessionService:
    """In-memory session service with simple long-context compression."""

    _store: dict[str, SessionState] = {}
    _lock = RLock()

    def ensure_session(self, conversation_id: str | None = None) -> SessionState:
        with self._lock:
            cid = conversation_id or f"conv-{uuid.uuid4().hex[:12]}"
            if cid not in self._store:
                self._store[cid] = SessionState(conversation_id=cid)
            return self._store[cid]

    def append_turn(self, conversation_id: str, role: str, content: str) -> SessionState:
        with self._lock:
            state = self.ensure_session(conversation_id)
            state.turns.append(SessionTurn(role=role, content=content))
            state.updated_at = datetime.utcnow()
            return state

    def build_long_context(
        self,
        conversation_id: str,
        max_recent_turns: int = 18,
        max_summary_chars: int = 1200,
    ) -> dict[str, object]:
        state = self.ensure_session(conversation_id)
        turns = state.turns
        if len(turns) <= max_recent_turns:
            recent = turns
            old = []
        else:
            old = turns[:-max_recent_turns]
            recent = turns[-max_recent_turns:]

        if old:
            summary_src = " | ".join(f"{t.role}:{t.content}" for t in old)
            state.summary = summary_src[:max_summary_chars]

        return {
            "conversation_id": state.conversation_id,
            "summary": state.summary,
            "recent_turns": [
                {"role": t.role, "content": t.content, "created_at": t.created_at.isoformat()}
                for t in recent
            ],
            "turn_count": len(turns),
            "summary_strategy": "compress_old_turns_keep_recent_window",
        }
