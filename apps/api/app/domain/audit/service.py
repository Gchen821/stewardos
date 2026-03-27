class AuditService:
    """Record runtime and admin activity for traceability."""

    def tracked_entities(self) -> list[str]:
        return ["conversation", "agent", "skill", "model", "policy", "job_run"]
