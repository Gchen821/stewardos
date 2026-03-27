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
        "runtime_doc": "/docs/architecture/StewardOS-Agent-Runtime-架构设计.md",
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
        "runtime": {
            "core_layer": "planned",
            "domain_layer": "planned",
            "context_builder": "planned",
            "protocols": ["mcp", "a2a", "anp"],
        },
    }
