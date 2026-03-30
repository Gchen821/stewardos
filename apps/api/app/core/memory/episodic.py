"""Episodic memory for persistent turn timelines and extracted facts.

This module persists long-term memories in SQLite as a local development-safe
backend. It supports:
- turn persistence (cross-session)
- lightweight lexical recall
- fact persistence for user preferences/instructions
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
import re
import sqlite3
from threading import RLock


def _tokenize(text: str) -> set[str]:
    lowered = text.lower()
    tokens: set[str] = set(re.findall(r"[a-z0-9_]{2,}", lowered))
    for chunk in re.findall(r"[\u4e00-\u9fa5]{2,}", lowered):
        tokens.add(chunk)
        if len(chunk) == 2:
            continue
        for i in range(0, len(chunk) - 1):
            tokens.add(chunk[i : i + 2])
    return tokens


def _overlap_score(query: str, target: str) -> int:
    q = _tokenize(query)
    t = _tokenize(target)
    if not q or not t:
        return 0
    return len(q.intersection(t))


@dataclass(slots=True)
class EpisodicHit:
    content: str
    role: str
    conversation_id: str
    created_at: str
    score: int


class EpisodicMemoryStore:
    """SQLite-backed episodic memory store."""

    backend = "sqlite"

    def __init__(self, db_path: str) -> None:
        self.db_path = db_path
        self._lock = RLock()
        self._init_db()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self) -> None:
        db_file = Path(self.db_path)
        db_file.parent.mkdir(parents=True, exist_ok=True)
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS episodic_turns (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    agent_code TEXT NOT NULL,
                    conversation_id TEXT NOT NULL,
                    role TEXT NOT NULL,
                    content TEXT NOT NULL,
                    created_at TEXT NOT NULL
                )
                """,
            )
            conn.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_episodic_agent_time
                ON episodic_turns(agent_code, created_at DESC)
                """,
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS memory_facts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    agent_code TEXT NOT NULL,
                    fact TEXT NOT NULL,
                    source TEXT NOT NULL DEFAULT 'user_turn',
                    weight REAL NOT NULL DEFAULT 1.0,
                    created_at TEXT NOT NULL
                )
                """,
            )
            conn.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_memory_facts_agent_time
                ON memory_facts(agent_code, created_at DESC)
                """,
            )
            conn.commit()

    def append_turn(
        self,
        agent_code: str,
        conversation_id: str,
        role: str,
        content: str,
    ) -> None:
        text = content.strip()
        if not text:
            return
        with self._lock, self._connect() as conn:
            conn.execute(
                """
                INSERT INTO episodic_turns (agent_code, conversation_id, role, content, created_at)
                VALUES (?, ?, ?, ?, ?)
                """,
                (agent_code, conversation_id, role, text, datetime.utcnow().isoformat()),
            )
            conn.commit()

    def recall_turns(self, agent_code: str, query: str, top_k: int = 4) -> list[EpisodicHit]:
        with self._lock, self._connect() as conn:
            rows = conn.execute(
                """
                SELECT conversation_id, role, content, created_at
                FROM episodic_turns
                WHERE agent_code = ?
                ORDER BY created_at DESC
                LIMIT 300
                """,
                (agent_code,),
            ).fetchall()
        hits: list[EpisodicHit] = []
        for row in rows:
            score = _overlap_score(query, str(row["content"]))
            if score > 0:
                hits.append(
                    EpisodicHit(
                        content=str(row["content"]),
                        role=str(row["role"]),
                        conversation_id=str(row["conversation_id"]),
                        created_at=str(row["created_at"]),
                        score=score,
                    ),
                )
        hits.sort(key=lambda item: (item.score, item.created_at), reverse=True)
        return hits[: max(1, top_k)]

    def add_fact(
        self,
        agent_code: str,
        fact: str,
        source: str = "user_turn",
        weight: float = 1.0,
    ) -> None:
        normalized = fact.strip()
        if not normalized:
            return
        with self._lock, self._connect() as conn:
            conn.execute(
                """
                INSERT INTO memory_facts (agent_code, fact, source, weight, created_at)
                VALUES (?, ?, ?, ?, ?)
                """,
                (agent_code, normalized, source, float(weight), datetime.utcnow().isoformat()),
            )
            conn.commit()

    def recall_facts(self, agent_code: str, query: str, top_k: int = 4) -> list[str]:
        with self._lock, self._connect() as conn:
            rows = conn.execute(
                """
                SELECT fact, created_at
                FROM memory_facts
                WHERE agent_code = ?
                ORDER BY created_at DESC
                LIMIT 300
                """,
                (agent_code,),
            ).fetchall()
        ranked: list[tuple[int, str, str]] = []
        for row in rows:
            fact = str(row["fact"])
            score = _overlap_score(query, fact)
            if score > 0:
                ranked.append((score, str(row["created_at"]), fact))
        ranked.sort(reverse=True)
        deduped: list[str] = []
        seen: set[str] = set()
        for _, _, fact in ranked:
            if fact in seen:
                continue
            seen.add(fact)
            deduped.append(fact)
            if len(deduped) >= max(1, top_k):
                break
        return deduped
