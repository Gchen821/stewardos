from fastapi import APIRouter

from app.config import get_settings
from app.schemas.repository import RepositorySummary
from app.services.repository_storage import get_repository_storage_service

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
    repository = get_repository_storage_service()
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
        "repository": repository.summary().model_dump(),
    }


@router.get("/repository/summary", response_model=RepositorySummary, tags=["repository"])
async def repository_summary() -> RepositorySummary:
    service = get_repository_storage_service()
    return service.summary()


@router.post("/repository/scan", response_model=RepositorySummary, tags=["repository"])
async def repository_scan() -> RepositorySummary:
    service = get_repository_storage_service()
    service.scan()
    return service.summary()
