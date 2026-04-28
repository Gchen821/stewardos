from __future__ import annotations

from contextvars import ContextVar, Token
from dataclasses import dataclass, replace
from uuid import UUID, uuid4

_request_id_var: ContextVar[str | None] = ContextVar("stewardos_request_id", default=None)


def set_current_request_id(request_id: str) -> Token[str | None]:
    return _request_id_var.set(request_id)


def reset_current_request_id(token: Token[str | None]) -> None:
    _request_id_var.reset(token)


def get_current_request_id() -> str | None:
    return _request_id_var.get()


def ensure_current_request_id() -> str:
    return get_current_request_id() or f"req_{uuid4().hex}"


@dataclass(frozen=True, slots=True)
class GatewayTraceContext:
    request_id: str
    session_id: str
    trace_id: str
    span_id: str
    parent_span_id: str | None = None
    user_id: str | None = None
    conversation_id: int | None = None
    job_run_id: int | None = None
    agent_id: int | None = None
    scope: str = ""
    iteration: int | None = None
    target_type: str | None = None
    target_id: int | None = None

    def child(
        self,
        *,
        scope: str | None = None,
        iteration: int | None = None,
        job_run_id: int | None = None,
        agent_id: int | None = None,
        target_type: str | None = None,
        target_id: int | None = None,
    ) -> GatewayTraceContext:
        return GatewayTraceContext(
            request_id=self.request_id,
            session_id=self.session_id,
            trace_id=self.trace_id,
            span_id=f"span_{uuid4().hex}",
            parent_span_id=self.span_id,
            user_id=self.user_id,
            conversation_id=self.conversation_id,
            job_run_id=self.job_run_id if job_run_id is None else job_run_id,
            agent_id=self.agent_id if agent_id is None else agent_id,
            scope=self.scope if scope is None else scope,
            iteration=self.iteration if iteration is None else iteration,
            target_type=self.target_type if target_type is None else target_type,
            target_id=self.target_id if target_id is None else target_id,
        )

    def with_job_run(self, job_run_id: int) -> GatewayTraceContext:
        return replace(self, job_run_id=job_run_id)

    def to_log_dict(self) -> dict[str, object | None]:
        return {
            "request_id": self.request_id,
            "session_id": self.session_id,
            "trace_id": self.trace_id,
            "span_id": self.span_id,
            "parent_span_id": self.parent_span_id,
            "user_id": self.user_id,
            "conversation_id": self.conversation_id,
            "job_run_id": self.job_run_id,
            "agent_id": self.agent_id,
            "scope": self.scope,
            "iteration": self.iteration,
            "target_type": self.target_type,
            "target_id": self.target_id,
        }


def build_trace_context(
    *,
    user_id: UUID | str | None = None,
    conversation_id: int | None = None,
    agent_id: int | None = None,
    scope: str = "",
    target_type: str | None = None,
    target_id: int | None = None,
    session_id: str | None = None,
) -> GatewayTraceContext:
    resolved_session_id = session_id or (
        f"conversation:{conversation_id}" if conversation_id is not None else f"session:{uuid4().hex}"
    )
    return GatewayTraceContext(
        request_id=ensure_current_request_id(),
        session_id=resolved_session_id,
        trace_id=f"trace_{uuid4().hex}",
        span_id=f"span_{uuid4().hex}",
        parent_span_id=None,
        user_id=None if user_id is None else str(user_id),
        conversation_id=conversation_id,
        job_run_id=None,
        agent_id=agent_id,
        scope=scope,
        iteration=None,
        target_type=target_type,
        target_id=target_id,
    )
