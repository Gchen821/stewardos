from fastapi import APIRouter

router = APIRouter(prefix="/models", tags=["models"])


@router.get("/blueprint")
async def models_blueprint() -> dict[str, object]:
    return {
        "status": "planned",
        "routing_priority": [
            "conversation_override",
            "agent_binding",
            "butler_default",
            "system_default",
            "fallback_model",
        ],
    }
