"""Semantic memory facade.

V1 uses lexical recall over persisted facts as a lightweight fallback.
V1.5 can swap this facade to vector retrieval without changing callers.
"""

from __future__ import annotations

from app.core.memory.episodic import EpisodicMemoryStore


class SemanticMemoryStore:
    """Semantic recall abstraction backed by episodic fact retrieval."""

    backend = "lexical-fallback"

    def __init__(self, episodic_store: EpisodicMemoryStore) -> None:
        self.episodic_store = episodic_store

    def recall(self, agent_code: str, query: str, top_k: int = 4) -> list[str]:
        return self.episodic_store.recall_facts(
            agent_code=agent_code,
            query=query,
            top_k=top_k,
        )
