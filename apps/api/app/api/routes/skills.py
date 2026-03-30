from fastapi import APIRouter, HTTPException

from app.schemas.repository import RepositoryItem
from app.services.repository_storage import get_repository_storage_service

router = APIRouter(prefix="/skills", tags=["skills"])


@router.get("", response_model=list[RepositoryItem])
async def list_skills() -> list[RepositoryItem]:
    service = get_repository_storage_service()
    return service.list_skills()


@router.get("/{code}", response_model=RepositoryItem)
async def get_skill(code: str) -> RepositoryItem:
    service = get_repository_storage_service()
    item = service.get_skill(code)
    if item is None:
        raise HTTPException(status_code=404, detail=f"Skill '{code}' not found")
    return item
