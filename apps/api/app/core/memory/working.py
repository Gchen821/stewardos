"""Working memory for short-horizon context windows.

This module keeps a bounded in-process turn window per conversation to support
long-dialogue compression before sending context to the model.
"""

from __future__ import annotations

from collections import defaultdict, deque
from dataclasses import dataclass
from datetime import datetime
from threading import RLock


@dataclass(slots=True)
class WorkingTurn:
    role: str
    content: str
    created_at: str


class WorkingMemoryStore:
    """Bounded conversation memory for recent turns."""

    backend = "in-process"

    def __init__(self, max_turns: int = 24) -> None:
        self.max_turns = max(6, max_turns)
        self._turns: dict[str, deque[WorkingTurn]] = defaultdict(
            lambda: deque(maxlen=self.max_turns),
        )
        self._lock = RLock()

    def append_turn(self, conversation_id: str, role: str, content: str) -> None:
        text = content.strip()
        if not text:
            return
        with self._lock:
            self._turns[conversation_id].append(
                WorkingTurn(
                    role=role,
                    content=text,
                    created_at=datetime.utcnow().isoformat(),
                ),
            )

    def recent_turns(self, conversation_id: str, limit: int = 12) -> list[WorkingTurn]:
        with self._lock:
            turns = list(self._turns.get(conversation_id, deque()))
        if limit <= 0:
            return turns
        return turns[-limit:]

    def summarize_older_turns(
        self,
        conversation_id: str,
        keep_recent: int = 12,
        max_chars: int = 1200,
    ) -> str:
        with self._lock:
            turns = list(self._turns.get(conversation_id, deque()))
        if len(turns) <= keep_recent:
            return ""
        older = turns[:-keep_recent]
        text = " | ".join(f"{t.role}:{t.content}" for t in older)
        return text[:max_chars]
