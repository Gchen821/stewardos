"""Agent executor coordinating context construction and invocation."""

from app.core.agent.base import Agent, AgentResult
from app.core.agent.context import ContextBuilder
from app.core.agent.message import AgentMessage


class AgentExecutor:
    """Thin coordinator between messages, memory, context, and agent runtime."""

    def __init__(self, context_builder: ContextBuilder) -> None:
        self.context_builder = context_builder

    def execute(
        self,
        agent: Agent,
        input_text: str,
        history: list[AgentMessage] | None = None,
        memory: list[str] | None = None,
        notes: list[str] | None = None,
        evidence: list[str] | None = None,
    ) -> AgentResult:
        context = self.context_builder.build(
            query=input_text,
            conversation=history or [],
            memory=memory or [],
            notes=notes or [],
            evidence=evidence or [],
        )
        return agent.run(input_text, context)
