from __future__ import annotations

from dataclasses import dataclass, field
from time import perf_counter
from typing import Any, Awaitable, Callable, Literal, TypeVar

from starlette.responses import Response

from app.config import get_settings
from app.gateway.context import GatewayTraceContext, build_trace_context
from app.gateway.logger import GatewayAuditLogger

GatewayCallKind = Literal["api", "llm", "mcp", "asset_runtime", "workflow"]
SyncResultT = TypeVar("SyncResultT")
AsyncResultT = TypeVar("AsyncResultT")


@dataclass(slots=True)
class GatewayCall:
    kind: GatewayCallKind
    target: str
    metadata: dict[str, Any] = field(default_factory=dict)


class ExecutionGateway:
    def __init__(self, audit_logger: GatewayAuditLogger | None = None) -> None:
        self.settings = get_settings()
        self.logger = audit_logger or GatewayAuditLogger()

    def build_trace_context(self, **kwargs: Any) -> GatewayTraceContext:
        return build_trace_context(**kwargs)

    def bind(self, trace_context: GatewayTraceContext) -> RuntimeExecutionHandle:
        return RuntimeExecutionHandle(self, trace_context)

    def execute(
        self,
        call: GatewayCall,
        trace_context: GatewayTraceContext,
        operation: Callable[[], SyncResultT],
    ) -> SyncResultT:
        started = perf_counter()
        try:
            result = operation()
        except Exception as exc:
            self._write_event(
                call=call,
                trace_context=trace_context,
                status="failed",
                latency_ms=self._elapsed_ms(started),
                result=None,
                error_message=str(exc),
            )
            raise
        self._write_event(
            call=call,
            trace_context=trace_context,
            status="completed",
            latency_ms=self._elapsed_ms(started),
            result=result,
            error_message=None,
        )
        return result

    async def execute_async(
        self,
        call: GatewayCall,
        trace_context: GatewayTraceContext,
        operation: Callable[[], Awaitable[AsyncResultT]],
    ) -> AsyncResultT:
        started = perf_counter()
        try:
            result = await operation()
        except Exception as exc:
            self._write_event(
                call=call,
                trace_context=trace_context,
                status="failed",
                latency_ms=self._elapsed_ms(started),
                result=None,
                error_message=str(exc),
            )
            raise
        self._write_event(
            call=call,
            trace_context=trace_context,
            status="completed",
            latency_ms=self._elapsed_ms(started),
            result=result,
            error_message=None,
        )
        return result

    def record(
        self,
        call: GatewayCall,
        trace_context: GatewayTraceContext,
        *,
        status: str,
        result: Any = None,
        error_message: str | None = None,
        latency_ms: int | None = None,
    ) -> None:
        self._write_event(
            call=call,
            trace_context=trace_context,
            status=status,
            latency_ms=latency_ms,
            result=result,
            error_message=error_message,
        )

    def _write_event(
        self,
        *,
        call: GatewayCall,
        trace_context: GatewayTraceContext,
        status: str,
        latency_ms: int | None,
        result: Any,
        error_message: str | None,
    ) -> None:
        try:
            self.logger.write_event(
                {
                    "event": "gateway_call",
                    "kind": call.kind,
                    "status": status,
                    "target": call.target,
                    "latency_ms": latency_ms,
                    "metadata": call.metadata,
                    "result": self._summarize_value(result),
                    "error_message": error_message,
                    **trace_context.to_log_dict(),
                }
            )
        except Exception:  # pragma: no cover - log write must not break runtime
            return

    @staticmethod
    def _elapsed_ms(started: float) -> int:
        return int((perf_counter() - started) * 1000)

    def _summarize_value(self, value: Any) -> dict[str, Any]:
        preview_limit = self.settings.gateway_log_preview_chars
        if value is None:
            return {}
        if isinstance(value, Response):
            return {
                "type": "response",
                "status_code": value.status_code,
                "media_type": value.media_type,
            }
        if isinstance(value, dict):
            return {
                "type": "dict",
                "keys": sorted(value.keys())[:20],
                "preview": self._truncate(str(value), preview_limit),
            }
        if isinstance(value, list):
            return {
                "type": "list",
                "length": len(value),
                "preview": self._truncate(str(value), preview_limit),
            }
        if isinstance(value, str):
            return {
                "type": "str",
                "length": len(value),
                "preview": self._truncate(value, preview_limit),
            }
        return {
            "type": type(value).__name__,
            "preview": self._truncate(repr(value), preview_limit),
        }

    @staticmethod
    def _truncate(value: str, limit: int) -> str:
        if len(value) <= limit:
            return value
        return f"{value[:limit]}..."


class RuntimeExecutionHandle:
    def __init__(self, gateway: ExecutionGateway, trace_context: GatewayTraceContext) -> None:
        self.gateway = gateway
        self.trace_context = trace_context

    def child(
        self,
        *,
        scope: str | None = None,
        iteration: int | None = None,
        agent_id: int | None = None,
        target_type: str | None = None,
        target_id: int | None = None,
    ) -> RuntimeExecutionHandle:
        return RuntimeExecutionHandle(
            self.gateway,
            self.trace_context.child(
                scope=scope,
                iteration=iteration,
                agent_id=agent_id,
                target_type=target_type,
                target_id=target_id,
            ),
        )

    def execute(
        self,
        *,
        kind: GatewayCallKind,
        target: str,
        operation: Callable[[], SyncResultT],
        metadata: dict[str, Any] | None = None,
        scope: str | None = None,
        iteration: int | None = None,
        target_type: str | None = None,
        target_id: int | None = None,
    ) -> SyncResultT:
        child_trace = self.trace_context.child(
            scope=scope,
            iteration=iteration,
            target_type=target_type,
            target_id=target_id,
        )
        return self.gateway.execute(
            GatewayCall(kind=kind, target=target, metadata=metadata or {}),
            child_trace,
            operation,
        )

    def execute_mcp(
        self,
        *,
        server: str,
        tool: str,
        arguments: dict[str, Any],
        operation: Callable[[], SyncResultT],
        scope: str = "mcp",
        iteration: int | None = None,
        target_id: int | None = None,
    ) -> SyncResultT:
        metadata = {
            "server": server,
            "tool": tool,
            "argument_keys": sorted(arguments.keys()),
        }
        return self.execute(
            kind="mcp",
            target=f"{server}.{tool}",
            operation=operation,
            metadata=metadata,
            scope=scope,
            iteration=iteration,
            target_type="mcp",
            target_id=target_id,
        )

    def execute_llm(
        self,
        *,
        provider: str,
        model: str,
        message_count: int,
        operation: Callable[[], SyncResultT],
        metadata: dict[str, Any] | None = None,
        scope: str = "llm",
        iteration: int | None = None,
        target_id: int | None = None,
    ) -> SyncResultT:
        details = {
            "provider": provider,
            "model": model,
            "message_count": message_count,
            **(metadata or {}),
        }
        return self.execute(
            kind="llm",
            target=f"{provider}:{model}",
            operation=operation,
            metadata=details,
            scope=scope,
            iteration=iteration,
            target_type="llm",
            target_id=target_id,
        )
