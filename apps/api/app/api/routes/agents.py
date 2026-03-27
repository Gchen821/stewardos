from fastapi import APIRouter

router = APIRouter(prefix="/agents", tags=["agents"])


@router.get("/blueprint")
async def agents_blueprint() -> dict[str, object]:
    return {
        "status": "planned",
        "managed_fields": [
            "name",
            "code",
            "type",
            "status",
            "bound_skills",
            "bound_models",
            "risk_level",
            "policy_state",
        ],
    }
