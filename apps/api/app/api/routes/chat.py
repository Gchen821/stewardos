from fastapi import APIRouter

router = APIRouter(prefix="/chat", tags=["chat"])


@router.get("/blueprint")
async def chat_blueprint() -> dict[str, object]:
    return {
        "status": "planned",
        "orchestrator": "ChatOrchestrator",
        "targets": ["butler", "agent"],
        "context_inputs": [
            "system_prompt",
            "conversation_history",
            "memory_summary",
            "agent_notes",
            "rag_evidence",
            "tool_results",
        ],
    }
