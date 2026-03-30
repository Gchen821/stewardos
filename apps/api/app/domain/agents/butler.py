from __future__ import annotations

from app.core.agent.message import AgentMessage, MessageRole
from app.core.agent.base import AgentResult
from app.core.agent.context import ContextEnvelope
from app.core.exceptions import HelloAgentsException
from app.core.llm.client import HelloAgentsLLM
from app.core.llm.providers import OpenAICompatibleGateway
from app.domain.agents.base import RuntimeAgentBase


class ButlerAgent(RuntimeAgentBase):
    """Primary butler chat agent without skill/tool binding."""

    @staticmethod
    def _memory_system_messages(context: ContextEnvelope) -> list[AgentMessage]:
        blocks: list[AgentMessage] = []
        memory_snapshot = context.metadata.get("memory_snapshot")
        if isinstance(memory_snapshot, dict):
            semantic = memory_snapshot.get("semantic_memory") or []
            episodic = memory_snapshot.get("episodic_memory") or []
            if isinstance(semantic, list) and semantic:
                body = "\n".join(f"- {str(item)}" for item in semantic[:6])
                blocks.append(
                    AgentMessage(
                        role=MessageRole.SYSTEM,
                        content=f"长期记忆（语义）：\n{body}",
                    ),
                )
            if isinstance(episodic, list) and episodic:
                body = "\n".join(f"- {str(item)}" for item in episodic[:6])
                blocks.append(
                    AgentMessage(
                        role=MessageRole.SYSTEM,
                        content=f"长期记忆（情景）：\n{body}",
                    ),
                )
        if context.evidence:
            body = "\n".join(f"- {line}" for line in context.evidence[:8])
            blocks.append(
                AgentMessage(role=MessageRole.SYSTEM, content=f"上下文证据：\n{body}"),
            )
        return blocks

    def _run_with_profile(
        self,
        input_text: str,
        context: ContextEnvelope,
        rag: dict[str, object],
    ) -> AgentResult:
        summary = str(context.metadata.get("summary", "")).strip()
        turn_count = int(context.metadata.get("turn_count", len(context.history)))
        system_prompt = self.profile.prompt_text.strip() or (
            "你是 StewardOS 的主控管家助手。"
            "请直接、清晰地回答用户问题。当前阶段不调用子 Agent、Skill、Tool。"
        )

        messages: list[AgentMessage] = [AgentMessage(role=MessageRole.SYSTEM, content=system_prompt)]
        if summary:
            messages.append(
                AgentMessage(
                    role=MessageRole.SYSTEM,
                    content=f"会话历史摘要：{summary[:1000]}",
                ),
            )
        messages.extend(self._memory_system_messages(context))
        messages.extend(context.history)
        if not context.history or context.history[-1].content != input_text:
            messages.append(AgentMessage(role=MessageRole.USER, content=input_text))

        try:
            gateway = OpenAICompatibleGateway(llm_client=HelloAgentsLLM())
            llm_response = gateway.generate(messages=messages)
            text = llm_response.text.strip() or "我还没有生成有效回复，请再试一次。"
            return AgentResult(
                output_text=text,
                metadata={
                    "context_task": context.task,
                    "rag": rag,
                    "turn_count": turn_count,
                    "selected_model": llm_response.model,
                    "usage": llm_response.usage,
                    "execution_mode": "butler-chat-llm-v1",
                },
            )
        except HelloAgentsException as exc:
            return AgentResult(
                output_text=(
                    "当前 LLM 配置不可用，请先在 API 环境变量中配置："
                    "`LLM_MODEL_ID`、`LLM_API_KEY`、`LLM_BASE_URL`。"
                ),
                metadata={
                    "context_task": context.task,
                    "rag": rag,
                    "turn_count": turn_count,
                    "execution_mode": "butler-chat-fallback",
                    "error": str(exc),
                },
            )
