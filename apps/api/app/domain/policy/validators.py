class AgentOnlineValidator:
    """Validate runtime readiness before an agent can go online."""

    def checklist(self) -> list[str]:
        return [
            "has_enabled_skill",
            "policy_is_valid",
            "model_binding_resolved",
            "risk_level_within_limits",
        ]
