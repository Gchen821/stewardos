from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from uuid import UUID

from fastapi import HTTPException
from pydantic import ValidationError
from sqlalchemy.orm import Session

from app.gateway import ExecutionGateway, GatewayTraceContext
from app.models import Agent, JobRun
from app.repositories import AgentRepository, JobRunRepository, ToolRepository
from app.runtime.asset_executor import RegisteredAssetRuntimeExecutor
from app.runtime.capability_resolver import CapabilityResolver
from app.runtime.control_agent_loader import ControlAgentAsset, ControlAgentLoader
from app.runtime.llm_loader import LLMLoader
from app.runtime.prompt_builder import PromptBuilder
from app.schemas.conversations import ChatSendRequest, ChatSendResponse, ConversationCreate, MessageCreate
from app.schemas.runtime import (
    ButlerBindingSnapshot,
    ButlerExecutionRecord,
    ButlerExecutionTarget,
    ButlerIterationTrace,
    ButlerPlan,
    ButlerPlanStep,
    ButlerReflection,
    ButlerRunTrace,
    CapabilityResolution,
    RuntimeAsset,
)
from app.services.conversations import ConversationService

TOKEN_PATTERN = re.compile(r"[a-z0-9_]+|[\u4e00-\u9fff]{1,4}", re.IGNORECASE)


class ButlerRuntimeService:
    """
    ButlerRuntimeService 是主管家编排入口。

    主流程：
    1. 接收用户消息
    2. 解析本轮绑定资产
    3. 加载 planner / reflection 控制资产
    4. 执行 planner -> asset execution -> reflection 的循环
    5. 把最终结果和 trace 回写到会话与 job_run
    """

    MAX_ITERATIONS = 3
    SUPERVISOR_AGENT_TYPES = {"butler", "supervisor", "planner", "reflection"}

    def __init__(self, session: Session) -> None:
        # 保存数据库会话，供整个主管家执行周期复用。
        self.session = session
        # 访问 agent 表，用于选候选执行 agent。
        self.agents = AgentRepository(session)
        # 访问 tool 表，用于选候选执行 tool。
        self.tools = ToolRepository(session)
        # 记录每次 butler 执行的作业结果。
        self.job_runs = JobRunRepository(session)
        # 读写会话与消息。
        self.conversations = ConversationService(session)
        # 把 agent + 绑定的 skills/tools 解析成运行时能力。
        self.capabilities = CapabilityResolver(session)
        # 统一记录 API / LLM / MCP / runtime 调用的执行网关。
        self.gateway = ExecutionGateway()
        # 真正执行注册资产 runtime 的执行器。
        self.executor = RegisteredAssetRuntimeExecutor(self.capabilities, self.gateway)
        # 读取当前模型配置。
        self.llm_loader = LLMLoader()
        # 构造 planner / reflection / agent 的提示词文本。
        self.prompts = PromptBuilder()

    @classmethod
    def describe(cls) -> dict[str, object]:
        # 对外暴露 butler 当前支持的运行模式说明。
        return {
            "mode": "active",
            "workflow": ["planner", "registered_asset_execution", "reflection", "loop_until_done_or_limit"],
            "max_iterations": cls.MAX_ITERATIONS,
            "execution_assets": {
                "agents": "enabled repo-registered agents",
                "tools": "enabled repo-registered tools",
            },
            "notes": [
                "planner and reflection are filesystem-loaded control roles under the current user asset root",
                "execution phase reuses registered assets from the repository",
            ],
        }

    def send(
        self,
        user_id: UUID,
        payload: ChatSendRequest,
        supervisor_agent: Agent | None = None,
    ) -> ChatSendResponse:
        # 先拿到当前会话；如果前端没传 conversation_id，就创建新会话。
        conversation = self._ensure_conversation(user_id, payload)
        # 解析本轮显式绑定的 agent / skill / tool；若没传，则从历史消息继承。
        binding_snapshot = self._resolve_binding_snapshot(conversation.id, payload)
        # 读取当前配置的模型信息，仅用于 trace 和回包元数据。
        llm_config = self.llm_loader.load()
        selected_model = f"{llm_config.provider}:{llm_config.model}"
        # 用户本轮真正的目标文本。
        goal = payload.content.strip()
        # job_run.agent_id 不能空，这里选一个可落库的 agent 作为这次主管家作业归属。
        job_agent = self._resolve_job_run_agent(binding_snapshot, supervisor_agent)
        # 生成整次主管家 workflow 的追踪上下文，后续 planner / asset runtime / reflection 共用。
        trace_context = self.gateway.build_trace_context(
            user_id=user_id,
            conversation_id=conversation.id,
            agent_id=job_agent.id,
            scope="butler_runtime",
            target_type=payload.target_type,
            target_id=payload.target_id,
        )
        # 从当前用户资产目录加载 planner / reflection 控制资产。
        control_assets = ControlAgentLoader(user_id).load_all()

        # 先把用户消息写入会话，后续 trace 和 assistant 回复都依赖这条上下文。
        self.conversations.create_message(
            MessageCreate(
                conversation_id=conversation.id,
                sender_role="user",
                sender_id=user_id,
                content=payload.content,
                message_type="text",
                metadata_json={
                    "binding_snapshot": binding_snapshot.model_dump(),
                    "trace": trace_context.to_log_dict(),
                },
            )
        )

        # 记录 butler 执行起始时间，用于 job_run。
        started_at = datetime.now(timezone.utc)
        # 进入主管家主循环：planner -> execute -> reflection。
        trace = self._run_workflow(
            goal=goal,
            binding_snapshot=binding_snapshot,
            selected_model=selected_model,
            supervisor_agent=supervisor_agent,
            planner_asset=control_assets["planner"],
            reflection_asset=control_assets["reflection"],
            trace_context=trace_context,
        )
        # 把主管家最终回答和完整 workflow trace 写成 assistant 消息。
        assistant_message = self.conversations.create_message(
            MessageCreate(
                conversation_id=conversation.id,
                sender_role="assistant",
                content=trace.final_output,
                message_type="butler_assistant",
                metadata_json={
                    "binding_snapshot": binding_snapshot.model_dump(),
                    "workflow": trace.model_dump(),
                    "control_agents": self._control_asset_metadata(control_assets),
                    "llm": llm_config.model_dump(exclude={"api_key"}),
                    "trace": trace_context.to_log_dict(),
                },
            )
        )

        # 把整次 butler 执行落到 job_runs，便于后续追踪和审计。
        job_run = self.job_runs.add(
            JobRun(
                user_id=user_id,
                agent_id=job_agent.id,
                conversation_id=conversation.id,
                status="completed" if trace.completed else "incomplete",
                input_json={
                    "content": payload.content,
                    "binding_snapshot": binding_snapshot.model_dump(),
                },
                context_json={
                    "workflow": "butler",
                    "selected_model": selected_model,
                    "job_agent_id": job_agent.id,
                    "supervisor_agent_id": supervisor_agent.id if supervisor_agent is not None else None,
                    "control_agents": self._control_asset_metadata(control_assets),
                    "trace": trace_context.to_log_dict(),
                },
                output_json={
                    "reply": trace.final_output,
                    "assistant_message_id": assistant_message.id,
                    "workflow": trace.model_dump(),
                },
                error_message=None,
                started_at=started_at,
                ended_at=datetime.now(timezone.utc),
            )
        )
        # 统一提交上面所有数据库变更。
        self.session.commit()

        # 返回给前端本次会话 id、最终 reply、job_run id 和 trace 元数据。
        return ChatSendResponse(
            conversation_id=conversation.id,
            reply=trace.final_output,
            job_run_id=job_run.id,
            selected_model=selected_model,
            metadata={
                "workflow": trace.model_dump(),
                "binding_snapshot": binding_snapshot.model_dump(),
                "request_id": trace_context.request_id,
                "session_id": trace_context.session_id,
                "trace_id": trace_context.trace_id,
            },
        )

    def _ensure_conversation(self, user_id: UUID, payload: ChatSendRequest):
        # 如果前端已经指定会话，直接复用。
        if payload.conversation_id is not None:
            return self.conversations.get_conversation(payload.conversation_id)
        # 否则按消息前 20 个字符创建一个新的 butler 会话标题。
        title = payload.content[:20] or "主管家会话"
        return self.conversations.create_conversation(
            user_id,
            ConversationCreate(target_type=payload.target_type, target_id=payload.target_id, title=title),
        )

    def _resolve_binding_snapshot(self, conversation_id: int, payload: ChatSendRequest) -> ButlerBindingSnapshot:
        # 先尝试使用本次请求显式传入的绑定范围。
        snapshot = ButlerBindingSnapshot(
            agent_ids=sorted(set(payload.bound_agent_ids)),
            skill_ids=sorted(set(payload.bound_skill_ids)),
            tool_ids=sorted(set(payload.bound_tool_ids)),
        )
        # 只要本次传了任一绑定，就直接用它，不回退历史。
        if snapshot.agent_ids or snapshot.skill_ids or snapshot.tool_ids:
            return snapshot
        # 如果本次没传，则从历史消息里反向查找最近一次 binding_snapshot。
        for message in reversed(self.conversations.list_messages(conversation_id)):
            raw_snapshot = message.metadata_json.get("binding_snapshot")
            if not isinstance(raw_snapshot, dict):
                continue
            try:
                # 命中历史绑定快照就复用。
                return ButlerBindingSnapshot.model_validate(raw_snapshot)
            except ValidationError:
                # 旧消息格式异常时跳过，继续向前找。
                continue
        # 历史也没有，就返回空绑定。
        return snapshot

    def _resolve_job_run_agent(
        self,
        binding_snapshot: ButlerBindingSnapshot,
        supervisor_agent: Agent | None,
    ) -> Agent:
        # 如果本次是通过某个 supervisor agent 入口进来的，优先把 job 记在它身上。
        if supervisor_agent is not None:
            return supervisor_agent

        # 否则找一个普通可用 agent 作为 job_run 的归属对象。
        candidates = [
            item
            for item in self.agents.list_active()
            if item.enabled
            and not item.is_deleted
            and item.type not in self.SUPERVISOR_AGENT_TYPES
            and item.code not in self.SUPERVISOR_AGENT_TYPES
        ]
        # 如果用户显式绑定过 agent，则优先用绑定集合里的第一个。
        if binding_snapshot.agent_ids:
            bound_candidates = [item for item in candidates if item.id in binding_snapshot.agent_ids]
            if bound_candidates:
                return bound_candidates[0]
        # 没有显式绑定时，退回任意可用普通 agent。
        if candidates:
            return candidates[0]
        # 如果系统里一个普通 agent 都没有，主管家就没法运行。
        raise HTTPException(status_code=400, detail="butler workflow requires at least one registered agent")

    def _run_workflow(
        self,
        goal: str,
        binding_snapshot: ButlerBindingSnapshot,
        selected_model: str,
        supervisor_agent: Agent | None,
        planner_asset: ControlAgentAsset,
        reflection_asset: ControlAgentAsset,
        trace_context: GatewayTraceContext,
    ) -> ButlerRunTrace:
        # 收集当前轮可参与规划的 agent 候选。
        candidate_capabilities = self._load_candidate_agents(binding_snapshot, supervisor_agent)
        # 收集当前轮可参与规划的 tool 候选。
        candidate_tools = self._load_candidate_tools(binding_snapshot)
        # 预构建 id -> capability/tool 映射，执行阶段直接查表。
        capability_map = {item.agent.id: item for item in candidate_capabilities}
        tool_map = {item.id: item for item in candidate_tools}

        # planner_memory: reflection 回灌给下一轮 planner 的记忆。
        planner_memory: list[str] = []
        # blocked_codes: 本轮失败或不应再选的资产 code。
        blocked_codes: set[str] = set()
        # seen_signatures: 避免 planner 一直选同一套 agent/tool 组合。
        seen_signatures: set[tuple[tuple[str, ...], tuple[str, ...]]] = set()
        # 累积每轮 trace。
        iterations: list[ButlerIterationTrace] = []

        # 最多执行 MAX_ITERATIONS 轮。
        for iteration in range(1, self.MAX_ITERATIONS + 1):
            # planner 阶段：基于目标、记忆、绑定和候选资产生成本轮计划。
            plan = self._build_plan(
                goal=goal,
                iteration=iteration,
                binding_snapshot=binding_snapshot,
                planner_memory=planner_memory,
                blocked_codes=blocked_codes,
                candidate_capabilities=candidate_capabilities,
                candidate_tools=candidate_tools,
                planner_asset=planner_asset,
            )
            # 用本轮选中的 agent/tool code 作为签名，检查是否重复规划。
            signature = (
                tuple(item.asset_code for item in plan.selected_agents),
                tuple(item.asset_code for item in plan.selected_tools),
            )
            repeated_plan = signature in seen_signatures
            seen_signatures.add(signature)

            # execute 阶段：真正执行 planner 选中的注册资产。
            executions = self._execute_plan(
                goal=goal,
                iteration=iteration,
                planner_memory=planner_memory,
                plan=plan,
                capability_map=capability_map,
                tool_map=tool_map,
                trace_context=trace_context,
            )
            # reflection 阶段：判断本轮是否完成；未完成则输出记忆给下一轮 planner。
            reflection = self._reflect(
                goal,
                plan,
                executions,
                repeated_plan,
                reflection_asset=reflection_asset,
            )
            # 把本轮 planner / execute / reflection 组成一条 trace。
            iterations.append(
                ButlerIterationTrace(
                    iteration=iteration,
                    planner=plan,
                    executions=executions,
                    reflection=reflection,
                )
            )
            # 反思认为完成，就提前结束循环。
            if reflection.completed:
                break
            # 把反思产生的记忆和 blocked 资产回灌给下一轮。
            planner_memory.extend(reflection.memory_for_planner)
            blocked_codes.update(reflection.blocked_asset_codes)

        # 只看最后一轮 reflection 的 completed 结果。
        completed = bool(iterations and iterations[-1].reflection.completed)
        # 把完整多轮 trace 渲染成最终返回给用户的文本。
        final_output = self._render_final_output(goal, iterations, completed)
        return ButlerRunTrace(
            goal=goal,
            completed=completed,
            final_output=final_output,
            max_iterations=self.MAX_ITERATIONS,
            selected_model=selected_model,
            binding_snapshot=binding_snapshot,
            iterations=iterations,
        )

    def _load_candidate_agents(
        self,
        binding_snapshot: ButlerBindingSnapshot,
        supervisor_agent: Agent | None,
    ) -> list[CapabilityResolution]:
        # 这里加载的是“普通执行 agent”，不包含 planner/reflection 这类控制角色。
        items: list[CapabilityResolution] = []
        for record in self.agents.list_active():
            # 必须启用、未删除、并且允许聊天选择。
            if not record.enabled or record.is_deleted or not record.chat_selectable:
                continue
            # 如果当前是从某个 supervisor 入口进来的，不把它自己再作为候选执行 agent。
            if supervisor_agent is not None and record.id == supervisor_agent.id:
                continue
            # 控制角色不进入普通执行候选池。
            if record.type in self.SUPERVISOR_AGENT_TYPES or record.code in self.SUPERVISOR_AGENT_TYPES:
                continue
            # 如果用户显式绑定了 agent，只在绑定范围内选。
            if binding_snapshot.agent_ids and record.id not in binding_snapshot.agent_ids:
                continue
            # 解析成运行时能力对象，后续 planner 和 executor 都使用它。
            items.append(self.capabilities.resolve_agent_capabilities(record.id))
        return items

    def _load_candidate_tools(self, binding_snapshot: ButlerBindingSnapshot) -> list[RuntimeAsset]:
        # 这里加载的是可被 planner 直接选中的 tool 候选。
        items: list[RuntimeAsset] = []
        for record in self.tools.list_active():
            if not record.enabled or record.is_deleted:
                continue
            # 如果用户显式绑定了 tool，只在绑定范围内选。
            if binding_snapshot.tool_ids and record.id not in binding_snapshot.tool_ids:
                continue
            # 解析为 RuntimeAsset，供 planner 评分和 executor 执行。
            items.append(self.capabilities.tool_registry.load_by_id(record.id))
        return items

    def _build_plan(
        self,
        goal: str,
        iteration: int,
        binding_snapshot: ButlerBindingSnapshot,
        planner_memory: list[str],
        blocked_codes: set[str],
        candidate_capabilities: list[CapabilityResolution],
        candidate_tools: list[RuntimeAsset],
        planner_asset: ControlAgentAsset,
    ) -> ButlerPlan:
        # 先拼出 planner 最终看到的 prompt 文本，便于后续 trace 保留。
        planner_prompt = self.prompts.build_planner_prompt(
            planner_asset,
            goal=goal,
            binding_snapshot=binding_snapshot,
            planner_memory=planner_memory,
            candidate_capabilities=candidate_capabilities,
            candidate_tools=candidate_tools,
            blocked_codes=blocked_codes,
        )
        # 目标和历史记忆一起分词，用于做启发式打分。
        query_tokens = self._tokenize(" ".join([goal, *planner_memory]))
        scored_agents: list[tuple[int, CapabilityResolution, str]] = []
        for capability in candidate_capabilities:
            # 已被 blocked 的资产不再参与本轮规划。
            if capability.agent.code in blocked_codes:
                continue
            # 给每个候选 agent 打分，并记录选择原因。
            score, reason = self._score_agent(goal, query_tokens, capability, binding_snapshot)
            scored_agents.append((score, capability, reason))
        # 分数高的排前面。
        scored_agents.sort(key=lambda item: (-item[0], item[1].agent.name, item[1].agent.id))

        scored_tools: list[tuple[int, RuntimeAsset, str]] = []
        for tool in candidate_tools:
            if tool.code in blocked_codes:
                continue
            # 给每个候选 tool 打分，并记录选择原因。
            score, reason = self._score_tool(goal, query_tokens, tool, binding_snapshot)
            scored_tools.append((score, tool, reason))
        scored_tools.sort(key=lambda item: (-item[0], item[1].name, item[1].id))

        # 根据打分结果挑出本轮真正要执行的 agent/tool。
        selected_agents = self._pick_agents(scored_agents)
        selected_tools = self._pick_tools(scored_tools, has_agents=bool(selected_agents))

        # steps 是返回给前端/trace 的“可读化计划步骤”。
        steps = [
            ButlerPlanStep(
                title="规划任务",
                detail="梳理用户目标、历史反思记忆和当前可用资产范围。",
            )
        ]
        for _, capability, reason in selected_agents:
            # 把每个选中的 agent 转成可显示的计划步骤。
            steps.append(
                ButlerPlanStep(
                    title=f"调用 Agent {capability.agent.name}",
                    detail=reason,
                    target=ButlerExecutionTarget(
                        asset_type="agent",
                        asset_id=capability.agent.id,
                        asset_code=capability.agent.code,
                        asset_name=capability.agent.name,
                        reason=reason,
                        source=self._selection_source(capability.agent.id, binding_snapshot.agent_ids),
                    ),
                )
            )
        for _, tool, reason in selected_tools:
            # 把每个选中的 tool 转成可显示的计划步骤。
            steps.append(
                ButlerPlanStep(
                    title=f"调用 Tool {tool.name}",
                    detail=reason,
                    target=ButlerExecutionTarget(
                        asset_type="tool",
                        asset_id=tool.id,
                        asset_code=tool.code,
                        asset_name=tool.name,
                        reason=reason,
                        source=self._selection_source(tool.id, binding_snapshot.tool_ids),
                    ),
                )
            )
        # 最后固定补一条 reflection 步骤。
        steps.append(
            ButlerPlanStep(
                title="反思结果",
                detail="基于本轮执行结果判断是否达成目标，若未达成则生成下一轮记忆。",
            )
        )

        # summary 是这一轮计划的概要说明。
        summary_parts = [
            f"第 {iteration} 轮规划",
            f"候选 Agent {len(candidate_capabilities)} 个",
            f"候选 Tool {len(candidate_tools)} 个",
        ]
        if planner_memory:
            summary_parts.append(f"继承记忆 {len(planner_memory)} 条")
        if binding_snapshot.agent_ids or binding_snapshot.skill_ids or binding_snapshot.tool_ids:
            summary_parts.append("本轮使用了用户绑定范围")

        # 返回结构化的 ButlerPlan，供 executor、reflection 和 trace 使用。
        return ButlerPlan(
            iteration=iteration,
            objective=goal,
            summary="，".join(summary_parts),
            controller_code=planner_asset.code,
            prompt_preview=planner_prompt[:400],
            memory_notes=planner_memory[-5:],
            selected_agents=[
                ButlerExecutionTarget(
                    asset_type="agent",
                    asset_id=capability.agent.id,
                    asset_code=capability.agent.code,
                    asset_name=capability.agent.name,
                    reason=reason,
                    source=self._selection_source(capability.agent.id, binding_snapshot.agent_ids),
                )
                for _, capability, reason in selected_agents
            ],
            selected_tools=[
                ButlerExecutionTarget(
                    asset_type="tool",
                    asset_id=tool.id,
                    asset_code=tool.code,
                    asset_name=tool.name,
                    reason=reason,
                    source=self._selection_source(tool.id, binding_snapshot.tool_ids),
                )
                for _, tool, reason in selected_tools
            ],
            steps=steps,
        )

    def _pick_agents(
        self,
        scored_agents: list[tuple[int, CapabilityResolution, str]],
    ) -> list[tuple[int, CapabilityResolution, str]]:
        # 优先选择正分候选；没有正分时，兜底取第一名。
        positive = [item for item in scored_agents if item[0] > 0]
        if positive:
            return positive[:2]
        return scored_agents[:1]

    def _pick_tools(
        self,
        scored_tools: list[tuple[int, RuntimeAsset, str]],
        has_agents: bool,
    ) -> list[tuple[int, RuntimeAsset, str]]:
        # tool 逻辑和 agent 类似，但如果已经选了 agent，默认不强行补低分 tool。
        positive = [item for item in scored_tools if item[0] > 0]
        if positive:
            return positive[:2]
        if has_agents:
            return []
        return scored_tools[:1]

    def _execute_plan(
        self,
        goal: str,
        iteration: int,
        planner_memory: list[str],
        plan: ButlerPlan,
        capability_map: dict[int, CapabilityResolution],
        tool_map: dict[int, RuntimeAsset],
        trace_context: GatewayTraceContext,
    ) -> list[ButlerExecutionRecord]:
        # records 是本轮执行结果列表；upstream_results 会传给后续 tool。
        records: list[ButlerExecutionRecord] = []
        upstream_results: list[dict[str, str]] = []
        # planner 选中的 tool code 会一并传给 agent runtime，告诉它本轮可配合哪些工具。
        selected_tool_codes = [item.asset_code for item in plan.selected_tools]

        # 先执行 agent。
        for target in plan.selected_agents:
            capability = capability_map.get(target.asset_id)
            if capability is None:
                # 候选池里已经没有这个 agent 时，直接标记失败。
                records.append(
                    ButlerExecutionRecord(
                        asset_type="agent",
                        asset_id=target.asset_id,
                        asset_code=target.asset_code,
                        asset_name=target.asset_name,
                        status="failed",
                        detail="planner selected an agent that is no longer available",
                        result={},
                        tool_sources={},
                        error="agent not found in runtime scope",
                    )
                )
                continue
            try:
                # 真正调用资产执行器，进入该 agent 的 runtime。
                result, resolved_capability = self.executor.execute_agent(
                    capability.agent,
                    goal=goal,
                    iteration=iteration,
                    planner_reason=target.reason,
                    reflection_memory=planner_memory[-5:],
                    selected_tool_codes=selected_tool_codes,
                    trace_context=trace_context.child(
                        scope="butler_agent_runtime",
                        iteration=iteration,
                        agent_id=target.asset_id,
                        target_type="agent",
                        target_id=target.asset_id,
                    ),
                )
                # 执行成功后，把结果整理成统一记录格式。
                record = ButlerExecutionRecord(
                    asset_type="agent",
                    asset_id=target.asset_id,
                    asset_code=target.asset_code,
                    asset_name=target.asset_name,
                    status=self._result_status(result),
                    detail=self._summarize_result(result),
                    result=result,
                    tool_sources=resolved_capability.tool_sources,
                    error=None,
                )
            except Exception as exc:  # pragma: no cover - defensive runtime isolation
                # 任意运行时异常都被隔离为 failed，不中断整个主管家流程。
                record = ButlerExecutionRecord(
                    asset_type="agent",
                    asset_id=target.asset_id,
                    asset_code=target.asset_code,
                    asset_name=target.asset_name,
                    status="failed",
                    detail=f"runtime execution failed: {exc}",
                    result={},
                    tool_sources={},
                    error=str(exc),
                )
            records.append(record)
            # agent 的执行摘要会传给后续 tool，形成串联上下文。
            upstream_results.append(
                {
                    "asset_code": record.asset_code,
                    "status": record.status,
                    "summary": record.detail,
                }
            )

        # 再执行 tool。
        for target in plan.selected_tools:
            tool = tool_map.get(target.asset_id)
            if tool is None:
                # 计划里选中的 tool 不在当前候选池，直接记失败。
                records.append(
                    ButlerExecutionRecord(
                        asset_type="tool",
                        asset_id=target.asset_id,
                        asset_code=target.asset_code,
                        asset_name=target.asset_name,
                        status="failed",
                        detail="planner selected a tool that is no longer available",
                        result={},
                        tool_sources={},
                        error="tool not found in runtime scope",
                    )
                )
                continue
            try:
                # tool runtime 会收到前面 agent 的执行摘要。
                result = self.executor.execute_tool(
                    tool,
                    goal=goal,
                    iteration=iteration,
                    planner_reason=target.reason,
                    reflection_memory=planner_memory[-5:],
                    upstream_results=upstream_results,
                    trace_context=trace_context.child(
                        scope="butler_tool_runtime",
                        iteration=iteration,
                        target_type="tool",
                        target_id=target.asset_id,
                    ),
                )
                # 整理工具执行结果。
                record = ButlerExecutionRecord(
                    asset_type="tool",
                    asset_id=target.asset_id,
                    asset_code=target.asset_code,
                    asset_name=target.asset_name,
                    status=self._result_status(result),
                    detail=self._summarize_result(result),
                    result=result,
                    tool_sources={},
                    error=None,
                )
            except Exception as exc:  # pragma: no cover - defensive runtime isolation
                # tool 运行失败同样只影响当前记录，不会让 butler 整体崩掉。
                record = ButlerExecutionRecord(
                    asset_type="tool",
                    asset_id=target.asset_id,
                    asset_code=target.asset_code,
                    asset_name=target.asset_name,
                    status="failed",
                    detail=f"runtime execution failed: {exc}",
                    result={},
                    tool_sources={},
                    error=str(exc),
                )
            records.append(record)
            # 工具结果继续加入上游摘要，便于后面扩展链式工具。
            upstream_results.append(
                {
                    "asset_code": record.asset_code,
                    "status": record.status,
                    "summary": record.detail,
                }
            )
        return records

    def _reflect(
        self,
        goal: str,
        plan: ButlerPlan,
        executions: list[ButlerExecutionRecord],
        repeated_plan: bool,
        reflection_asset: ControlAgentAsset,
    ) -> ButlerReflection:
        # 拼出 reflection 本轮看到的完整提示词文本。
        reflection_prompt = self.prompts.build_reflection_prompt(
            reflection_asset,
            goal=goal,
            plan=plan,
            executions=executions,
            repeated_plan=repeated_plan,
        )
        # 分类统计本轮失败和未完成的执行记录。
        failures = [item for item in executions if item.status == "failed"]
        incomplete = [item for item in executions if item.status == "incomplete"]
        # 下面三个集合分别给 trace、下一轮 planner 和记忆阻断使用。
        missing_requirements: list[str] = []
        memory_for_planner: list[str] = []
        blocked_asset_codes: list[str] = []

        # planner 一项都没选出来，说明当前候选资产不够。
        if not executions:
            missing_requirements.append("planner did not select any executable registered asset")
            memory_for_planner.append("扩大候选资产范围，或先在仓库中注册可执行的 agent/tool。")
        # 如果重复同一套失败组合，明确要求 planner 换策略。
        if repeated_plan and (failures or incomplete or not executions):
            missing_requirements.append("planner repeated the same asset combination without solving the gap")
            memory_for_planner.append("避免重复使用同一套失败组合，优先切换到其他已注册资产。")

        # 所有 failed 资产都进入 blocked，并把失败原因回灌给 planner。
        for item in failures:
            missing_requirements.append(f"{item.asset_code} execution failed")
            memory_for_planner.append(f"避开失败资产 {item.asset_code}，失败原因：{item.error or item.detail}")
            blocked_asset_codes.append(item.asset_code)

        # incomplete 资产说明方向可能对，但条件不够，要把缺口描述清楚。
        for item in incomplete:
            missing_requirements.append(f"{item.asset_code} returned incomplete status")
            memory_for_planner.append(f"围绕 {item.asset_code} 补足缺失条件后再继续尝试。")

        # 只要本轮有执行，且没有 failed / incomplete，就判定主管家目标完成。
        if executions and not failures and not incomplete:
            summary = (
                f"Reflection 判定目标已完成，planner 选中的 {len(executions)} 个已注册资产都返回了可接受结果。"
            )
            return ButlerReflection(
                completed=True,
                summary=summary,
                controller_code=reflection_asset.code,
                prompt_preview=reflection_prompt[:400],
                confidence=0.92,
                missing_requirements=[],
                memory_for_planner=[],
                blocked_asset_codes=[],
            )

        # 否则返回未完成，并把缺失项和记忆交给下一轮 planner。
        summary = (
            f"Reflection 判定目标暂未完成：{goal}。"
            f" 失败资产 {len(failures)} 个，未完成资产 {len(incomplete)} 个。"
        )
        return ButlerReflection(
            completed=False,
            summary=summary,
            controller_code=reflection_asset.code,
            prompt_preview=reflection_prompt[:400],
            confidence=0.33 if executions else 0.1,
            missing_requirements=missing_requirements,
            memory_for_planner=memory_for_planner,
            blocked_asset_codes=blocked_asset_codes,
        )

    @staticmethod
    def _control_asset_metadata(control_assets: dict[str, ControlAgentAsset]) -> dict[str, dict[str, str]]:
        # 把 planner / reflection 的文件路径信息整理进 trace，方便前端展示和调试。
        return {
            code: {
                "name": asset.name,
                "file_path": asset.file_path,
                "prompt_path": asset.prompt_path,
                "runtime_path": asset.runtime_path,
            }
            for code, asset in control_assets.items()
        }

    def _render_final_output(
        self,
        goal: str,
        iterations: list[ButlerIterationTrace],
        completed: bool,
    ) -> str:
        # 如果连一轮都没跑出来，直接返回兜底文本。
        if not iterations:
            return f"主管家未找到可执行流程：{goal}"

        # 把多轮 trace 渲染成用户可读的总结文本。
        lines = [
            f"{'主管家已完成目标' if completed else '主管家未在限制轮次内完成目标'}：{goal}",
            f"总轮次：{len(iterations)}",
        ]
        for trace in iterations:
            agent_names = "、".join(item.asset_name for item in trace.planner.selected_agents) or "无"
            tool_names = "、".join(item.asset_name for item in trace.planner.selected_tools) or "无"
            lines.append(f"第 {trace.iteration} 轮计划：Agent[{agent_names}] Tool[{tool_names}]")
            for record in trace.executions:
                lines.append(f"- {record.asset_name} ({record.status})：{record.detail}")
            lines.append(f"反思：{trace.reflection.summary}")
        last_reflection = iterations[-1].reflection
        # 若最终没完成，则把最后一轮生成的记忆建议也带给用户。
        if not completed and last_reflection.memory_for_planner:
            lines.append("下一轮建议或最终记忆：")
            for note in last_reflection.memory_for_planner:
                lines.append(f"- {note}")
        return "\n".join(lines)

    def _score_agent(
        self,
        goal: str,
        query_tokens: set[str],
        capability: CapabilityResolution,
        binding_snapshot: ButlerBindingSnapshot,
    ) -> tuple[int, str]:
        # 把 agent 自身信息、技能和工具描述拼成一个语料串，用于和目标做启发式匹配。
        corpus_parts = [
            capability.agent.code,
            capability.agent.name,
            capability.agent.description,
            *(item.code for item in capability.skills),
            *(item.name for item in capability.skills),
            *(item.description for item in capability.skills),
            *(item.code for item in capability.unique_tools),
            *(item.name for item in capability.unique_tools),
            *(item.description for item in capability.unique_tools),
        ]
        corpus = " ".join(part for part in corpus_parts if part)
        # 基础分来自目标关键词和语料的重叠度。
        score = self._overlap_score(query_tokens, corpus)
        # 用户显式绑定的 agent 提高优先级。
        if capability.agent.id in binding_snapshot.agent_ids:
            score += 12
        # 如果这个 agent 挂载了用户显式绑定的 skill，也提高优先级。
        matched_skill_ids = {item.id for item in capability.skills} & set(binding_snapshot.skill_ids)
        if matched_skill_ids:
            score += 8 + len(matched_skill_ids)
        # 有 skills / tools 的 agent 在默认情况下稍微更优。
        if capability.skills:
            score += 1
        if capability.unique_tools:
            score += 1
        # reason 会进入 plan.steps 和 trace，方便解释 planner 为什么选它。
        reason_parts = [
            f"与目标的语义匹配分数 {score}",
            f"绑定技能 {len(matched_skill_ids)} 个",
            f"可用技能 {len(capability.skills)} 个",
            f"可用工具 {len(capability.unique_tools)} 个",
        ]
        if capability.agent.id in binding_snapshot.agent_ids:
            reason_parts.append("命中用户显式绑定的 Agent")
        return score, "；".join(reason_parts)

    def _score_tool(
        self,
        goal: str,
        query_tokens: set[str],
        tool: RuntimeAsset,
        binding_snapshot: ButlerBindingSnapshot,
    ) -> tuple[int, str]:
        # tool 只用自身 code/name/description 做匹配。
        corpus = " ".join([tool.code, tool.name, tool.description])
        score = self._overlap_score(query_tokens, corpus)
        # 用户显式绑定的 tool 提高优先级。
        if tool.id in binding_snapshot.tool_ids:
            score += 10
        # 名称或描述中带 mcp 的工具额外微调一点分数。
        if "mcp" in tool.code.lower() or "mcp" in tool.description.lower():
            score += 1
        reason_parts = [f"与目标的语义匹配分数 {score}"]
        if tool.id in binding_snapshot.tool_ids:
            reason_parts.append("命中用户显式绑定的 Tool")
        return score, "；".join(reason_parts)

    @staticmethod
    def _selection_source(asset_id: int, bound_ids: list[int]) -> str:
        # 标记当前资产是用户显式绑定选中的，还是 planner 自主选择的。
        return "user_bound" if asset_id in bound_ids else "planner_selected"

    @staticmethod
    def _tokenize(text: str) -> set[str]:
        # 用预定义正则把英文 token 和中文短片段切出来，统一转小写。
        return {item.lower() for item in TOKEN_PATTERN.findall(text or "") if item.strip()}

    def _overlap_score(self, query_tokens: set[str], corpus: str) -> int:
        # 没有查询 token 时直接返回 0 分。
        if not query_tokens:
            return 0
        corpus_lower = corpus.lower()
        corpus_tokens = self._tokenize(corpus_lower)
        # token 完整命中比单纯子串命中权重更高。
        token_hits = len(query_tokens & corpus_tokens)
        substring_hits = sum(1 for token in query_tokens if len(token) > 1 and token in corpus_lower)
        return token_hits * 4 + substring_hits

    @staticmethod
    def _result_status(result: dict[str, object]) -> str:
        # 统一把 runtime 返回值归一化到 completed / incomplete / failed 三种状态。
        if result.get("completed") is False:
            return "incomplete"
        if result.get("needs_more_work") is True:
            return "incomplete"
        status = str(result.get("status", "")).lower()
        if status in {"failed", "error"}:
            return "failed"
        if status in {"incomplete", "needs_more", "needs_attention"}:
            return "incomplete"
        return "completed"

    def _summarize_result(self, result: dict[str, object]) -> str:
        # 优先取运行时明确返回的自然语言字段作为摘要。
        for key in ["final_answer", "answer", "summary", "result", "message"]:
            value = result.get(key)
            if isinstance(value, str) and value.strip():
                return value.strip()[:240]
        # 没有明确摘要时，把整个结果压成 JSON 文本做兜底展示。
        compact = json.dumps(result, ensure_ascii=False, default=str)
        return compact[:240] + ("..." if len(compact) > 240 else "")
