from app.core.agent.base import AgentResult
from app.core.agent.context import ContextEnvelope
from app.domain.agents.base import RuntimeAgentBase


class SubAgentRunner(RuntimeAgentBase):
    """Specialized agent runtime entry used by chat and job execution flows."""

    def _run_with_profile(
        self,
        input_text: str,
        context: ContextEnvelope,
        rag: dict[str, object],
    ) -> AgentResult:
        return AgentResult(
            output_text=(
                f"{self.profile.name} 已接收任务：{input_text}\n"
                "当前为子 Agent 骨架执行，后续将接入具体 Skill 与 Tool 调度。"
            ),
            metadata={
                "context_evidence": len(context.evidence),
                "rag": rag,
            },
        )
