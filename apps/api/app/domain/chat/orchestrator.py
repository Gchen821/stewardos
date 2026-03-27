from dataclasses import dataclass

from app.core.agent.base import AgentResult
from app.domain.agents.factory import create_agent


@dataclass(slots=True)
class ChatDecision:
    selected_target: str
    allow_chat: bool
    route_reason: str


class ChatOrchestrator:
    """Central runtime entry for chat selection, policy checks, and dispatch."""

    def decide(self, target_type: str, target_status: str) -> ChatDecision:
        allow = target_type == "butler" or target_status == "online"
        return ChatDecision(
            selected_target=target_type,
            allow_chat=allow,
            route_reason="butler_always_available" if target_type == "butler" else target_status,
        )

    def dispatch(self, target_type: str, name: str, input_text: str) -> AgentResult:
        agent = create_agent(target_type, name)
        from app.core.agent.context import ContextEnvelope

        context = ContextEnvelope(
            query=input_text,
            role_and_policies="Policy evaluation is delegated to guards.",
            task=input_text,
            state="runtime_state=planned",
        )
        return agent.run(input_text, context)
