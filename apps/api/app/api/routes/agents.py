from fastapi import APIRouter, HTTPException

from app.schemas.repository import RepositoryItem
from app.services.repository_storage import get_repository_storage_service

router = APIRouter(prefix="/agents", tags=["agents"])


@router.get("", response_model=list[RepositoryItem])
async def list_agents() -> list[RepositoryItem]:
    service = get_repository_storage_service()
    return service.list_agents()


@router.get("/{code}", response_model=RepositoryItem)
async def get_agent(code: str) -> RepositoryItem:
    service = get_repository_storage_service()
    item = service.get_agent(code)
    if item is None:
        raise HTTPException(status_code=404, detail=f"Agent '{code}' not found")
    return item
