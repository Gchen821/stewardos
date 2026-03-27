from app.core.agent.base import Agent, AgentResult
from app.core.agent.context import ContextEnvelope


class SubAgentRunner(Agent):
    """Specialized agent runtime entry used by chat and job execution flows."""

    def run(self, input_text: str, context: ContextEnvelope) -> AgentResult:
        return AgentResult(
            output_text=f"Sub-agent placeholder response: {input_text}",
            metadata={"context_evidence": len(context.evidence)},
        )
