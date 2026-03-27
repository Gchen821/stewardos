from dataclasses import dataclass


@dataclass(slots=True)
class RoutingDecision:
    selected_model: str
    reason: str
    fallback_model: str | None = None


class ModelRouter:
    """Resolve model precedence across system, butler, agent, and conversation."""

    def resolve(
        self,
        conversation_override: str | None = None,
        agent_binding: str | None = None,
        butler_default: str | None = None,
        system_default: str = "system-default",
        fallback_model: str | None = None,
    ) -> RoutingDecision:
        selected = (
            conversation_override
            or agent_binding
            or butler_default
            or system_default
        )
        return RoutingDecision(
            selected_model=selected,
            reason="conversation_override > agent_binding > butler_default > system_default",
            fallback_model=fallback_model,
        )
