from dataclasses import dataclass, field


@dataclass(slots=True)
class MemorySnapshot:
    working_memory: list[str] = field(default_factory=list)
    episodic_memory: list[str] = field(default_factory=list)
    semantic_memory: list[str] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)


class MemoryManager:
    """Phased memory manager.

    V1 uses PostgreSQL + Redis for summaries, notes, and short-lived state.
    Vector and graph stores are deferred to later milestones.
    """

    def build_snapshot(self, conversation_id: str | None = None) -> MemorySnapshot:
        _ = conversation_id
        return MemorySnapshot()
