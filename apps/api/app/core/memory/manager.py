"""Unified memory manager for long-context + long-term recall.

This manager provides a stable API for all agents:
- append turn
- build memory snapshot for prompt construction
- lightweight fact extraction and persistence
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
import re
from threading import RLock

from app.core.memory.episodic import EpisodicMemoryStore
from app.core.memory.perceptual import PerceptualMemoryStore
from app.core.memory.semantic import SemanticMemoryStore
from app.core.memory.working import WorkingMemoryStore


@dataclass(slots=True)
class MemorySnapshot:
    """Prompt-ready memory bundle."""

    summary: str = ""
    working_memory: list[str] = field(default_factory=list)
    episodic_memory: list[str] = field(default_factory=list)
    semantic_memory: list[str] = field(default_factory=list)
    perceptual_memory: list[str] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)


class MemoryManager:
    """Agent-level memory manager with persistent episodic storage."""

    _instances: dict[tuple[str, str], "MemoryManager"] = {}
    _instances_lock = RLock()

    def __new__(
        cls,
        *,
        agent_code: str,
        memory_db_path: str,
        max_working_turns: int = 24,
    ) -> "MemoryManager":
        key = (agent_code, memory_db_path)
        with cls._instances_lock:
            if key in cls._instances:
                return cls._instances[key]
            instance = super().__new__(cls)
            cls._instances[key] = instance
            return instance

    def __init__(
        self,
        *,
        agent_code: str,
        memory_db_path: str,
        max_working_turns: int = 24,
    ) -> None:
        if getattr(self, "_initialized", False):
            return
        self.agent_code = agent_code
        self.memory_db_path = memory_db_path
        Path(memory_db_path).parent.mkdir(parents=True, exist_ok=True)
        self.working = WorkingMemoryStore(max_turns=max_working_turns)
        self.episodic = EpisodicMemoryStore(db_path=memory_db_path)
        self.semantic = SemanticMemoryStore(episodic_store=self.episodic)
        self.perceptual = PerceptualMemoryStore()
        self._initialized = True

    def append_turn(self, conversation_id: str, role: str, content: str) -> None:
        text = content.strip()
        if not text:
            return
        self.working.append_turn(conversation_id=conversation_id, role=role, content=text)
        self.episodic.append_turn(
            agent_code=self.agent_code,
            conversation_id=conversation_id,
            role=role,
            content=text,
        )
        if role == "user":
            for fact in self._extract_candidate_facts(text):
                self.episodic.add_fact(agent_code=self.agent_code, fact=fact, source="user_turn")

    def build_snapshot(
        self,
        conversation_id: str,
        query: str = "",
        *,
        recent_limit: int = 12,
        recall_k: int = 4,
        summary_chars: int = 1200,
    ) -> MemorySnapshot:
        recent = self.working.recent_turns(conversation_id=conversation_id, limit=recent_limit)
        summary = self.working.summarize_older_turns(
            conversation_id=conversation_id,
            keep_recent=recent_limit,
            max_chars=summary_chars,
        )
        query_text = query.strip()
        episodic_hits = self.episodic.recall_turns(
            agent_code=self.agent_code,
            query=query_text,
            top_k=recall_k,
        ) if query_text else []
        semantic_hits = self.semantic.recall(
            agent_code=self.agent_code,
            query=query_text,
            top_k=recall_k,
        ) if query_text else []
        perceptual_hits = self.perceptual.recall(
            agent_code=self.agent_code,
            query=query_text,
            top_k=min(3, recall_k),
        ) if query_text else []
        return MemorySnapshot(
            summary=summary,
            working_memory=[f"{turn.role}:{turn.content}" for turn in recent],
            episodic_memory=[
                f"{hit.role}@{hit.conversation_id}: {hit.content}"
                for hit in episodic_hits
            ],
            semantic_memory=semantic_hits,
            perceptual_memory=[
                f"{item.source_type}:{item.summary} ({item.source_uri})"
                for item in perceptual_hits
            ],
            notes=[],
        )

    def _extract_candidate_facts(self, text: str) -> list[str]:
        candidates: list[str] = []
        for sentence in re.split(r"[。！？!?；;\n]+", text):
            s = sentence.strip()
            if len(s) < 4:
                continue
            if (
                "请记住" in s
                or "记住" in s
                or "我叫" in s
                or "我是" in s
                or "我喜欢" in s
                or "我不喜欢" in s
                or "偏好" in s
                or "习惯" in s
            ):
                candidates.append(s[:300])
        # Deduplicate while preserving order.
        uniq: list[str] = []
        seen: set[str] = set()
        for item in candidates:
            if item in seen:
                continue
            seen.add(item)
            uniq.append(item)
        return uniq[:6]
