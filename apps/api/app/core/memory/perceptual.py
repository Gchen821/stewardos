"""Perceptual memory placeholder for future multimodal retrieval.

This module reserves the interface for image/audio/video memory so current
text-only runtime can evolve without breaking the memory API.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class PerceptualMemoryItem:
    source_type: str
    source_uri: str
    summary: str
    score: float = 0.0


class PerceptualMemoryStore:
    """Reserved multimodal memory store.

    V1 behavior:
    - no persistence
    - no retrieval
    - keeps a stable interface for V2 multimodal integration
    """

    backend = "reserved"

    def recall(self, agent_code: str, query: str, top_k: int = 3) -> list[PerceptualMemoryItem]:
        _ = (agent_code, query, top_k)
        return []
