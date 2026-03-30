"""Context envelope and builder for runtime prompt assembly."""

from dataclasses import dataclass, field
from typing import Any

from app.core.agent.message import AgentMessage
from app.core.agent.gssc_builder import ContextBuilder as GSSCContextBuilder


@dataclass(slots=True)
class ContextEnvelope:
    query: str
    role_and_policies: str
    task: str
    state: str
    evidence: list[str] = field(default_factory=list)
    history: list[AgentMessage] = field(default_factory=list)
    output_contract: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)


class ContextBuilder:
    """Planned GSSC context builder.

    The implementation stays intentionally light for now. This class is the
    stable entry point for future gather/select/structure/compress logic.
    """

    def build(
        self,
        query: str,
        conversation: list[AgentMessage],
        memory: list[str],
        notes: list[str],
        evidence: list[str],
    ) -> ContextEnvelope:
        gssc = GSSCContextBuilder()
        structured = gssc.build(
            user_query=query,
            conversation_history=conversation,
            system_instructions="Follow system policies, risk limits, and active permissions.",
        )
        state_parts = [
            "memory_summary=" + "; ".join(memory) if memory else "memory_summary=none",
            "notes=" + "; ".join(notes) if notes else "notes=none",
        ]
        return ContextEnvelope(
            query=query,
            role_and_policies="Follow system policies, risk limits, and active permissions.",
            task=query,
            state="\n".join(state_parts + [f"structured_context_ready={bool(structured)}"]),
            evidence=evidence,
            history=conversation,
            output_contract="Respond with a grounded answer and explicit tool usage summary when applicable.",
            metadata={"gssc_context": structured},
        )
