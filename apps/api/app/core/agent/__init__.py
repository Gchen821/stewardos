"""Agent abstractions, context builders, and optional advanced execution patterns."""

from app.core.agent.base import Agent, AgentResult
from app.core.agent.context import ContextBuilder, ContextEnvelope
from app.core.agent.executor import AgentExecutor
from app.core.agent.history import HistoryManager
from app.core.agent.token_counter import TokenCounter
from app.core.agent.truncator import ObservationTruncator

__all__ = [
    "Agent",
    "AgentResult",
    "ContextBuilder",
    "ContextEnvelope",
    "AgentExecutor",
    "HistoryManager",
    "TokenCounter",
    "ObservationTruncator",
]
