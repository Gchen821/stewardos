"""Advanced agent patterns migrated from HelloAgents for optional runtime use."""

try:
    from .simple_agent import SimpleAgent
    from .react_agent import ReActAgent
    from .reflection_agent import ReflectionAgent
    from .plan_solve_agent import PlanSolveAgent
    from .factory import create_agent, default_subagent_factory
    PlanAndSolveAgent = PlanSolveAgent
except Exception:  # optional pattern modules can have extra runtime dependencies
    SimpleAgent = None  # type: ignore[assignment]
    ReActAgent = None  # type: ignore[assignment]
    ReflectionAgent = None  # type: ignore[assignment]
    PlanSolveAgent = None  # type: ignore[assignment]
    PlanAndSolveAgent = None  # type: ignore[assignment]
    create_agent = None  # type: ignore[assignment]
    default_subagent_factory = None  # type: ignore[assignment]

__all__ = ["SimpleAgent", "ReActAgent", "ReflectionAgent", "PlanSolveAgent", "PlanAndSolveAgent", "create_agent", "default_subagent_factory"]
