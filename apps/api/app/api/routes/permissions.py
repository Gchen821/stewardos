from fastapi import APIRouter

router = APIRouter(prefix="/permissions", tags=["permissions"])


@router.get("/blueprint")
async def permissions_blueprint() -> dict[str, object]:
    return {
        "status": "planned",
        "layers": [
            "page_and_api_permissions",
            "agent_skill_permissions",
            "model_override_and_high_risk_permissions",
        ],
        "core_permissions": [
            "system.model.manage",
            "agent.manage",
            "skill.manage",
            "audit.read",
            "chat.use_agent",
        ],
    }
