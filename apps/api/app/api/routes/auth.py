from fastapi import APIRouter

router = APIRouter(prefix="/auth", tags=["auth"])


@router.get("/blueprint")
async def auth_blueprint() -> dict[str, object]:
    return {
        "status": "planned",
        "routes": ["/login", "/refresh", "/logout"],
        "notes": [
            "JWT + Refresh Token handled in API layer.",
            "Route guards remain in Web until auth provider is implemented.",
        ],
    }
