from fastapi import APIRouter

router = APIRouter(prefix="/skills", tags=["skills"])


@router.get("/blueprint")
async def skills_blueprint() -> dict[str, object]:
    return {
        "status": "planned",
        "skill_definition": {
            "code": "unique identifier",
            "risk_level": "L0-L3",
            "protocol_type": "builtin|mcp|a2a|custom",
            "io_schema": "json schema",
        },
    }
