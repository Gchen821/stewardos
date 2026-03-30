import asyncio
from dataclasses import asdict
import json

from fastapi import APIRouter
from fastapi import HTTPException
from fastapi.responses import StreamingResponse

from app.core.exceptions import HelloAgentsException
from app.domain.agents.factory import create_agent, inspect_agent_profile
from app.domain.chat.orchestrator import ChatOrchestrator
from app.schemas.chat import ChatSendRequest, ChatSendResponse

router = APIRouter(prefix="/chat", tags=["chat"])


@router.get("/blueprint")
async def chat_blueprint() -> dict[str, object]:
    return {
        "status": "active-v1",
        "orchestrator": "ChatOrchestrator",
        "targets": ["butler"],
        "streaming": {"enabled": True, "endpoint": "/api/v1/chat/stream", "protocol": "sse"},
        "context_inputs": [
            "system_prompt",
            "conversation_history",
            "memory_summary",
            "agent_notes",
            "rag_evidence",
            "tool_results",
        ],
    }


@router.post("/send", response_model=ChatSendResponse)
async def chat_send(payload: ChatSendRequest) -> ChatSendResponse:
    orchestrator = ChatOrchestrator()
    status, allow_chat_select = orchestrator.resolve_target_state(
        target_type=payload.target_type,
        target_id=payload.target_id,
    )
    decision = orchestrator.decide(
        target_type=payload.target_type,
        target_status=status,
        allow_chat_select=allow_chat_select,
    )
    if not decision.allow_chat:
        return ChatSendResponse(
            reply=f"目标 Agent 不可用（status={status}）。",
            selected_model="runtime-agent-v1",
            trace_id=None,
            metadata={"decision": asdict(decision)},
        )
    try:
        result, long_context = orchestrator.dispatch(
            target_type=payload.target_type,
            target_id=payload.target_id,
            input_text=payload.content,
            conversation_id=payload.conversation_id,
        )
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except HelloAgentsException as exc:
        async def llm_config_error() -> object:
            event = {
                "type": "error",
                "message": str(exc),
                "hint": "请检查 LLM_MODEL_ID / LLM_API_KEY / LLM_BASE_URL",
            }
            yield f"data: {json.dumps(event, ensure_ascii=False)}\n\n"

        return StreamingResponse(llm_config_error(), media_type="text/event-stream")
    if result is None:
        raise HTTPException(status_code=500, detail="agent runtime returned no result")
    return ChatSendResponse(
        reply=result.output_text,
        selected_model=str(result.metadata.get("selected_model", "runtime-agent-v1")),
        trace_id=None,
        metadata={
            "decision": asdict(decision),
            "agent": result.metadata,
            "used_tools": result.used_tools,
            "conversation_id": long_context["conversation_id"],
            "long_context": {
                "turn_count": long_context["turn_count"],
                "summary_strategy": long_context["summary_strategy"],
            },
        },
    )


@router.post("/stream")
async def chat_stream(payload: ChatSendRequest) -> StreamingResponse:
    orchestrator = ChatOrchestrator()
    status, allow_chat_select = orchestrator.resolve_target_state(
        target_type=payload.target_type,
        target_id=payload.target_id,
    )
    decision = orchestrator.decide(
        target_type=payload.target_type,
        target_status=status,
        allow_chat_select=allow_chat_select,
    )
    if not decision.allow_chat:
        async def denied() -> object:
            event = {
                "type": "error",
                "message": "当前仅支持主控管家对话。",
                "decision": asdict(decision),
            }
            yield f"data: {json.dumps(event, ensure_ascii=False)}\n\n"

        return StreamingResponse(denied(), media_type="text/event-stream")

    try:
        stream_dispatch = orchestrator.dispatch_stream(
            target_type=payload.target_type,
            target_id=payload.target_id,
            input_text=payload.content,
            conversation_id=payload.conversation_id,
        )
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    async def event_stream() -> object:
        start = {
            "type": "start",
            "conversation_id": stream_dispatch.long_context["conversation_id"],
            "selected_model": stream_dispatch.selected_model,
            "mode": "native_model_stream",
        }
        yield f"data: {json.dumps(start, ensure_ascii=False)}\n\n"
        try:
            for token in stream_dispatch.token_iter:
                data = {"type": "delta", "delta": token}
                yield f"data: {json.dumps(data, ensure_ascii=False)}\n\n"
                await asyncio.sleep(0)
        except HelloAgentsException as exc:
            error_data = {
                "type": "error",
                "message": str(exc),
                "hint": "请检查 LLM_MODEL_ID / LLM_API_KEY / LLM_BASE_URL",
            }
            yield f"data: {json.dumps(error_data, ensure_ascii=False)}\n\n"
            return
        done = {
            "type": "done",
            "selected_model": stream_dispatch.metadata.get("selected_model", stream_dispatch.selected_model),
            "metadata": {
                "decision": asdict(decision),
                "agent": stream_dispatch.metadata,
                "used_tools": [],
                "conversation_id": stream_dispatch.long_context["conversation_id"],
                "long_context": {
                    "turn_count": stream_dispatch.long_context["turn_count"],
                    "summary_strategy": stream_dispatch.long_context["summary_strategy"],
                },
            },
        }
        yield f"data: {json.dumps(done, ensure_ascii=False)}\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")


@router.get("/agent-profile/{agent_code}")
async def chat_agent_profile(agent_code: str) -> dict[str, object]:
    try:
        return inspect_agent_profile(agent_code=agent_code)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.post("/rag/search")
async def chat_rag_search(payload: dict[str, object]) -> dict[str, object]:
    """RAG reserved interface for future vector retrieval integration."""
    agent_code = str(payload.get("agent_code", "butler"))
    query = str(payload.get("query", ""))
    top_k = int(payload.get("top_k", 3))
    try:
        agent = create_agent(agent_code=agent_code)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return {
        "agent_code": agent_code,
        "query": query,
        "rag": agent.rag_search(input_text=query, top_k=top_k),
        "status": "placeholder",
    }
