from dataclasses import asdict, dataclass
from typing import Iterator

from app.core.agent.base import AgentResult
from app.core.agent.message import AgentMessage, MessageRole
from app.core.agent.token_counter import TokenCounter
from app.core.exceptions import HelloAgentsException
from app.core.llm.client import HelloAgentsLLM
from app.core.memory.manager import MemoryManager, MemorySnapshot
from app.domain.agents.factory import create_agent
from app.domain.chat.session_service import SessionService


@dataclass(slots=True)
class ChatDecision:
    selected_target: str
    allow_chat: bool
    route_reason: str


@dataclass(slots=True)
class ChatStreamDispatch:
    token_iter: Iterator[str]
    selected_model: str
    long_context: dict[str, object]
    metadata: dict[str, object]


class ChatOrchestrator:
    """Central runtime entry for chat selection, policy checks, and dispatch."""

    def __init__(self) -> None:
        self.session_service = SessionService()

    @staticmethod
    def _memory_blocks(snapshot: MemorySnapshot) -> list[str]:
        blocks: list[str] = []
        if snapshot.summary:
            blocks.append(f"历史摘要：{snapshot.summary[:1200]}")
        if snapshot.semantic_memory:
            joined = "\n".join(f"- {item}" for item in snapshot.semantic_memory[:6])
            blocks.append(f"长期记忆（语义）：\n{joined}")
        if snapshot.episodic_memory:
            joined = "\n".join(f"- {item}" for item in snapshot.episodic_memory[:6])
            blocks.append(f"长期记忆（情景）：\n{joined}")
        if snapshot.perceptual_memory:
            joined = "\n".join(f"- {item}" for item in snapshot.perceptual_memory[:4])
            blocks.append(f"感知记忆（预留）：\n{joined}")
        return blocks

    @staticmethod
    def _normalize_usage(raw_usage: object) -> dict[str, int]:
        if not isinstance(raw_usage, dict):
            return {}
        prompt = int(raw_usage.get("prompt_tokens", 0) or 0)
        completion = int(raw_usage.get("completion_tokens", 0) or 0)
        total = int(raw_usage.get("total_tokens", 0) or 0)
        if total <= 0:
            total = prompt + completion
        return {
            "prompt_tokens": max(0, prompt),
            "completion_tokens": max(0, completion),
            "total_tokens": max(0, total),
        }

    @staticmethod
    def _estimate_usage(
        model: str,
        payload_messages: list[dict[str, str]],
        completion_text: str,
    ) -> dict[str, int]:
        counter = TokenCounter(model=model)
        role_map = {
            "system": MessageRole.SYSTEM,
            "user": MessageRole.USER,
            "assistant": MessageRole.ASSISTANT,
            "tool": MessageRole.TOOL,
        }
        prompt_messages: list[AgentMessage] = []
        for msg in payload_messages:
            role = role_map.get(str(msg.get("role", "user")), MessageRole.USER)
            content = str(msg.get("content", ""))
            prompt_messages.append(AgentMessage(role=role, content=content))
        prompt_tokens = counter.count_messages(prompt_messages)
        completion_tokens = max(0, counter.count_text(completion_text))
        return {
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "total_tokens": prompt_tokens + completion_tokens,
        }

    def decide(
        self,
        target_type: str,
        target_status: str,
        allow_chat_select: bool = True,
    ) -> ChatDecision:
        allow = target_type == "butler"
        return ChatDecision(
            selected_target=target_type,
            allow_chat=allow,
            route_reason="butler_only_v1" if target_type == "butler" else "subagent_disabled_v1",
        )

    def resolve_agent_code(self, target_type: str, target_id: str | None) -> str:
        if target_type == "butler":
            return "butler"
        if not target_id:
            raise ValueError("target_id is required for sub-agent chat")
        return target_id

    def resolve_target_state(self, target_type: str, target_id: str | None) -> tuple[str, bool]:
        if target_type == "butler":
            return ("online", True)
        _ = target_id
        return ("disabled", False)

    def dispatch(
        self,
        target_type: str,
        target_id: str | None,
        input_text: str,
        conversation_id: str | None = None,
    ) -> tuple[AgentResult, dict[str, object]]:
        agent_code = self.resolve_agent_code(target_type=target_type, target_id=target_id)
        agent = create_agent(agent_code=agent_code)
        memory_manager = MemoryManager(
            agent_code=agent.profile.code,
            memory_db_path=agent.profile.memory_db_path or agent.profile.rag_db_path,
        )

        session = self.session_service.ensure_session(conversation_id=conversation_id)
        self.session_service.append_turn(
            conversation_id=session.conversation_id,
            role="user",
            content=input_text,
        )
        memory_manager.append_turn(
            conversation_id=session.conversation_id,
            role="user",
            content=input_text,
        )
        long_context = self.session_service.build_long_context(
            conversation_id=session.conversation_id,
        )
        memory_snapshot = memory_manager.build_snapshot(
            conversation_id=session.conversation_id,
            query=input_text,
        )

        history_messages = [
            AgentMessage(
                role=MessageRole.USER if t["role"] == "user" else MessageRole.ASSISTANT,
                content=t["content"],
            )
            for t in long_context["recent_turns"]
        ]
        from app.core.agent.context import ContextEnvelope

        memory_blocks = self._memory_blocks(memory_snapshot)
        context = ContextEnvelope(
            query=input_text,
            role_and_policies=(
                "当前仅允许主控管家对话；子 Agent 调度暂未开放。"
            ),
            task=input_text,
            state=(
                f"runtime_state=active\n"
                f"target_type={target_type}\n"
                f"agent_code={agent_code}\n"
                f"turn_count={long_context['turn_count']}"
            ),
            history=history_messages,
            evidence=memory_blocks,
            metadata={
                "conversation_id": session.conversation_id,
                "summary": long_context["summary"],
                "summary_strategy": long_context["summary_strategy"],
                "turn_count": long_context["turn_count"],
                "memory_snapshot": asdict(memory_snapshot),
            },
        )
        result = agent.run(input_text, context)
        self.session_service.append_turn(
            conversation_id=session.conversation_id,
            role="assistant",
            content=result.output_text,
        )
        memory_manager.append_turn(
            conversation_id=session.conversation_id,
            role="assistant",
            content=result.output_text,
        )
        return result, long_context

    def dispatch_stream(
        self,
        target_type: str,
        target_id: str | None,
        input_text: str,
        conversation_id: str | None = None,
    ) -> ChatStreamDispatch:
        agent_code = self.resolve_agent_code(target_type=target_type, target_id=target_id)
        if agent_code != "butler":
            raise ValueError("stream currently supports butler only")
        agent = create_agent(agent_code=agent_code)
        memory_manager = MemoryManager(
            agent_code=agent.profile.code,
            memory_db_path=agent.profile.memory_db_path or agent.profile.rag_db_path,
        )

        session = self.session_service.ensure_session(conversation_id=conversation_id)
        self.session_service.append_turn(
            conversation_id=session.conversation_id,
            role="user",
            content=input_text,
        )
        memory_manager.append_turn(
            conversation_id=session.conversation_id,
            role="user",
            content=input_text,
        )
        long_context = self.session_service.build_long_context(
            conversation_id=session.conversation_id,
        )
        memory_snapshot = memory_manager.build_snapshot(
            conversation_id=session.conversation_id,
            query=input_text,
        )

        history_messages = [
            AgentMessage(
                role=MessageRole.USER if t["role"] == "user" else MessageRole.ASSISTANT,
                content=t["content"],
            )
            for t in long_context["recent_turns"]
        ]
        summary = str(long_context.get("summary", "")).strip()
        system_prompt = getattr(agent.profile, "prompt_text", "").strip() or (
            "你是 StewardOS 的主控管家助手。"
            "请直接、清晰地回答用户问题。当前阶段不调用子 Agent、Skill、Tool。"
        )

        payload_messages: list[dict[str, str]] = [{"role": "system", "content": system_prompt}]
        if summary:
            payload_messages.append({"role": "system", "content": f"会话历史摘要：{summary[:1000]}"})
        for block in self._memory_blocks(memory_snapshot):
            payload_messages.append({"role": "system", "content": block})
        payload_messages.extend({"role": m.role.value, "content": m.content} for m in history_messages)
        if not history_messages or history_messages[-1].content != input_text:
            payload_messages.append({"role": "user", "content": input_text})

        llm = HelloAgentsLLM()
        selected_model = llm.model
        metadata: dict[str, object] = {
            "conversation_id": session.conversation_id,
            "turn_count": long_context["turn_count"],
            "summary_strategy": long_context["summary_strategy"],
            "agent_code": agent_code,
            "execution_mode": "butler-native-token-stream-v1",
            "selected_model": selected_model,
            "memory_snapshot": asdict(memory_snapshot),
            "usage": {
                "prompt_tokens": 0,
                "completion_tokens": 0,
                "total_tokens": 0,
            },
        }

        def native_token_stream() -> Iterator[str]:
            chunks: list[str] = []
            try:
                for token in llm.stream_invoke(payload_messages):
                    chunks.append(token)
                    yield token
            except HelloAgentsException:
                raise
            finally:
                completion_text = "".join(chunks)
                raw_usage = None
                if getattr(llm, "last_call_stats", None) is not None:
                    raw_usage = llm.last_call_stats.usage
                    if llm.last_call_stats.model:
                        metadata["selected_model"] = llm.last_call_stats.model
                normalized_usage = self._normalize_usage(raw_usage)
                if normalized_usage.get("total_tokens", 0) <= 0 and completion_text:
                    normalized_usage = self._estimate_usage(
                        model=selected_model,
                        payload_messages=payload_messages,
                        completion_text=completion_text,
                    )
                if normalized_usage:
                    metadata["usage"] = normalized_usage
                if chunks:
                    self.session_service.append_turn(
                        conversation_id=session.conversation_id,
                        role="assistant",
                        content=completion_text,
                    )
                    memory_manager.append_turn(
                        conversation_id=session.conversation_id,
                        role="assistant",
                        content=completion_text,
                    )

        return ChatStreamDispatch(
            token_iter=native_token_stream(),
            selected_model=selected_model,
            long_context=long_context,
            metadata=metadata,
        )
