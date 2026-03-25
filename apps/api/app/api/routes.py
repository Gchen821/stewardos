from fastapi import APIRouter

from app.config import get_settings

router = APIRouter()


@router.get("/", tags=["meta"])
async def root() -> dict[str, str]:
    settings = get_settings()
    return {
        "name": settings.project_name,
        "environment": settings.app_env,
        "docs_url": settings.docs_url,
        "health_url": f"{settings.api_v1_prefix}/health",
    }


@router.get("/health", tags=["system"])
async def health() -> dict[str, object]:
    settings = get_settings()
    return {
        "status": "ok",
        "service": "api",
        "environment": settings.app_env,
        "version": "0.1.0",
        "dependencies": {
            "database_configured": bool(settings.database_url),
            "redis_configured": bool(settings.redis_url),
            "minio_endpoint": settings.minio_endpoint,
        },
    }
