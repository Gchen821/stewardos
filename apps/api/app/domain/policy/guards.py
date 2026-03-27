class PolicyGuard:
    """Evaluate request-level, agent-level, and model-level permissions."""

    def layers(self) -> list[str]:
        return [
            "page_and_api_permissions",
            "agent_skill_permissions",
            "model_override_and_high_risk_permissions",
        ]
