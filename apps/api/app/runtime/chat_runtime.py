from datetime import datetime, timezone
from uuid import UUID

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.gateway import ExecutionGateway, GatewayCall
from app.models import JobRun
from app.repositories import AgentRepository, JobRunRepository
from app.runtime.butler_runtime import ButlerRuntimeService
from app.runtime.capability_resolver import CapabilityResolver
from app.runtime.llm_loader import LLMLoader
from app.runtime.prompt_builder import PromptBuilder
from app.schemas.conversations import ChatSendRequest, ChatSendResponse, ConversationCreate, MessageCreate
from app.services.conversations import ConversationService


class ChatRuntimeService:
    """
    Runtime entry for direct agent chat and butler orchestration.
    """

    def __init__(self, session: Session) -> None:
        self.session = session
        self.agents = AgentRepository(session)
        self.job_runs = JobRunRepository(session)
        self.conversations = ConversationService(session)
        self.capabilities = CapabilityResolver(session)
        self.prompts = PromptBuilder()
        self.llm_loader = LLMLoader()
        self.gateway = ExecutionGateway()

    def send(self, user_id: UUID, payload: ChatSendRequest) -> ChatSendResponse:
        if payload.target_type == "butler":
            return ButlerRuntimeService(self.session).send(user_id, payload)
        if payload.target_type != "agent":
            raise HTTPException(status_code=400, detail="unsupported target type")
        agent = self.agents.get(payload.target_id)
        if agent is None or agent.is_deleted:
            raise HTTPException(status_code=404, detail="agent not found")
        if agent.type in ButlerRuntimeService.SUPERVISOR_AGENT_TYPES or agent.code in ButlerRuntimeService.SUPERVISOR_AGENT_TYPES:
            return ButlerRuntimeService(self.session).send(user_id, payload, supervisor_agent=agent)

        conversation = self._ensure_conversation(user_id, payload)
        self.conversations.create_message(
            MessageCreate(
                conversation_id=conversation.id,
                sender_role="user",
                sender_id=user_id,
                content=payload.content,
                message_type="text",
            )
        )

        capability = self.capabilities.resolve_agent_capabilities(agent.id)
        system_prompt = self.prompts.build_agent_system_prompt(capability)
        skill_prompts = {
            skill.code: self.prompts.build_skill_execution_prompt(capability, skill.code) for skill in capability.skills
        }
        llm_config = self.llm_loader.load()
        trace_context = self.gateway.build_trace_context(
            user_id=user_id,
            conversation_id=conversation.id,
            agent_id=agent.id,
            scope="chat_runtime",
            target_type=payload.target_type,
            target_id=payload.target_id,
        )

        reply = self.gateway.execute(
            GatewayCall(
                kind="llm",
                target=f"{llm_config.provider}:{llm_config.model}",
                metadata={
                    "agent_code": agent.code,
                    "system_prompt_length": len(system_prompt),
                    "skill_prompt_count": len(skill_prompts),
                    "tool_count": len(capability.unique_tools),
                },
            ),
            trace_context.child(scope="chat_agent_llm"),
            lambda: self._mock_assistant_reply(agent.name, payload.content, capability, system_prompt),
        )
        assistant_message = self.conversations.create_message(
            MessageCreate(
                conversation_id=conversation.id,
                sender_role="assistant",
                content=reply,
                message_type="mock_assistant",
                metadata_json={
                    "system_prompt": system_prompt,
                    "skill_prompts": skill_prompts,
                    "llm": llm_config.model_dump(),
                    "trace": trace_context.to_log_dict(),
                },
            )
        )

        started_at = datetime.now(timezone.utc)
        job_run = self.job_runs.add(
            JobRun(
                user_id=user_id,
                agent_id=agent.id,
                conversation_id=conversation.id,
                status="completed",
                input_json={"content": payload.content},
                context_json={
                    "system_prompt": system_prompt,
                    "skill_prompts": skill_prompts,
                    "tool_sources": capability.tool_sources,
                    "llm": llm_config.model_dump(),
                    "trace": trace_context.to_log_dict(),
                },
                output_json={"reply": reply, "assistant_message_id": assistant_message.id},
                error_message=None,
                started_at=started_at,
                ended_at=datetime.now(timezone.utc),
            )
        )
        self.session.commit()

        return ChatSendResponse(
            conversation_id=conversation.id,
            reply=reply,
            job_run_id=job_run.id,
            selected_model=f"{llm_config.provider}:{llm_config.model}",
            metadata={
                "tool_sources": capability.tool_sources,
                "skill_codes": [item.code for item in capability.skills],
                "direct_tool_codes": [item.code for item in capability.direct_tools],
                "request_id": trace_context.request_id,
                "session_id": trace_context.session_id,
                "trace_id": trace_context.trace_id,
            },
        )

    def _ensure_conversation(self, user_id: UUID, payload: ChatSendRequest):
        if payload.conversation_id is not None:
            return self.conversations.get_conversation(payload.conversation_id)
        title = payload.content[:20] or "新会话"
        return self.conversations.create_conversation(
            user_id,
            ConversationCreate(target_type=payload.target_type, target_id=payload.target_id, title=title),
        )

    @staticmethod
    def _mock_assistant_reply(agent_name: str, user_text: str, capability, system_prompt: str) -> str:
        skill_names = ", ".join(skill.name for skill in capability.skills) or "无"
        tool_names = ", ".join(tool.name for tool in capability.unique_tools) or "无"
        return (
            f"[MockAssistant:{agent_name}] 已接收消息：{user_text}\n"
            f"已解析技能：{skill_names}\n"
            f"已解析工具：{tool_names}\n"
            f"系统提示摘要长度：{len(system_prompt)}"
        )
