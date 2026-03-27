from app.core.agent.base import Agent, AgentResult
from app.core.agent.context import ContextEnvelope


class ButlerAgent(Agent):
    """Primary agent responsible for orchestration and summarization."""

    def run(self, input_text: str, context: ContextEnvelope) -> AgentResult:
        return AgentResult(
            output_text=f"Butler placeholder response: {input_text}",
            metadata={"context_task": context.task},
        )
