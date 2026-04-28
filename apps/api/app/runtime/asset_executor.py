from __future__ import annotations

import importlib.util
from pathlib import Path
from typing import Any, Callable
from uuid import uuid4

from app.gateway import ExecutionGateway, GatewayCall, GatewayTraceContext
from app.runtime.capability_resolver import CapabilityResolver
from app.runtime.prompt_builder import PromptBuilder
from app.schemas.runtime import CapabilityResolution, RuntimeAsset


class RegisteredAssetRuntimeExecutor:
    def __init__(
        self,
        capability_resolver: CapabilityResolver,
        execution_gateway: ExecutionGateway | None = None,
    ) -> None:
        self.capabilities = capability_resolver
        self.prompts = PromptBuilder()
        self.gateway = execution_gateway

    def execute_agent(
        self,
        agent: RuntimeAsset,
        goal: str,
        iteration: int,
        planner_reason: str,
        reflection_memory: list[str],
        selected_tool_codes: list[str],
        trace_context: GatewayTraceContext | None = None,
    ) -> tuple[dict[str, Any], CapabilityResolution]:
        capability = self.capabilities.resolve_agent_capabilities(agent.id)
        bound_gateway = self.gateway.bind(trace_context) if self.gateway is not None and trace_context is not None else None
        context = {
            "goal": goal,
            "iteration": iteration,
            "planner_reason": planner_reason,
            "reflection_memory": reflection_memory,
            "agent": self._brief_asset(agent),
            "skills": [self._brief_asset(item) for item in capability.skills],
            "direct_tools": [self._brief_asset(item) for item in capability.direct_tools],
            "skill_tools": {
                skill_code: [self._brief_asset(item) for item in tools]
                for skill_code, tools in capability.skill_tools.items()
            },
            "selected_tool_codes": selected_tool_codes,
            "system_prompt_preview": self.prompts.build_agent_system_prompt(capability)[:800],
            "skill_prompt_previews": {
                skill.code: self.prompts.build_skill_execution_prompt(capability, skill.code)[:600]
                for skill in capability.skills
            },
            "trace_context": trace_context.to_log_dict() if trace_context is not None else {},
            "services": {"gateway": bound_gateway} if bound_gateway is not None else {},
        }
        return self._execute_runtime(agent, context, trace_context=trace_context), capability

    def execute_tool(
        self,
        tool: RuntimeAsset,
        goal: str,
        iteration: int,
        planner_reason: str,
        reflection_memory: list[str],
        upstream_results: list[dict[str, Any]],
        trace_context: GatewayTraceContext | None = None,
    ) -> dict[str, Any]:
        bound_gateway = self.gateway.bind(trace_context) if self.gateway is not None and trace_context is not None else None
        context = {
            "goal": goal,
            "iteration": iteration,
            "planner_reason": planner_reason,
            "reflection_memory": reflection_memory,
            "tool": self._brief_asset(tool),
            "upstream_results": upstream_results,
            "trace_context": trace_context.to_log_dict() if trace_context is not None else {},
            "services": {"gateway": bound_gateway} if bound_gateway is not None else {},
        }
        return self._execute_runtime(tool, context, trace_context=trace_context)

    def _execute_runtime(
        self,
        asset: RuntimeAsset,
        context: dict[str, Any],
        *,
        trace_context: GatewayTraceContext | None = None,
    ) -> dict[str, Any]:
        entry = asset.manifest.get("entry", {})
        runtime_name = entry.get("runtime", "main.py")
        runtime_path = Path(asset.file_path) / runtime_name
        runner = self._load_runner(runtime_path)
        if self.gateway is not None and trace_context is not None:
            output = self.gateway.execute(
                GatewayCall(
                    kind="asset_runtime",
                    target=f"{asset.code}:{runtime_name}",
                    metadata={
                        "asset_type": entry.get("type", "runtime"),
                        "asset_code": asset.code,
                        "asset_id": asset.id,
                    },
                ),
                trace_context.child(
                    scope="asset_runtime",
                    target_type="asset_runtime",
                    target_id=asset.id,
                ),
                lambda: runner(context),
            )
        else:
            output = runner(context)
        if isinstance(output, dict):
            return output
        return {"value": output}

    @staticmethod
    def _brief_asset(asset: RuntimeAsset) -> dict[str, Any]:
        return {
            "id": asset.id,
            "code": asset.code,
            "name": asset.name,
            "description": asset.description,
        }

    def _load_runner(self, runtime_path: Path) -> Callable[[dict[str, Any]], Any]:
        if not runtime_path.exists():
            raise RuntimeError(f"runtime file not found: {runtime_path}")
        module_name = f"stewardos_asset_runtime_{runtime_path.stem}_{uuid4().hex}"
        spec = importlib.util.spec_from_file_location(module_name, runtime_path)
        if spec is None or spec.loader is None:
            raise RuntimeError(f"cannot load runtime module: {runtime_path}")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        runner = getattr(module, "run", None)
        if not callable(runner):
            raise RuntimeError(f"runtime entry must export callable run(context): {runtime_path}")
        return runner
