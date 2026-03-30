from fastapi import APIRouter
import os

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


@router.get("/runtime")
async def models_runtime() -> dict[str, object]:
    current_model = os.getenv("LLM_MODEL_ID", "").strip() or "unknown"
    fallback_model = os.getenv("LLM_FALLBACK_MODEL_ID", "").strip()
    return {
        "current_model": current_model,
        "fallback_model": fallback_model or None,
        "has_fallback": bool(fallback_model),
    }
