from fastapi import APIRouter, HTTPException

from app.schemas.repository import RepositoryItem
from app.services.repository_storage import get_repository_storage_service

router = APIRouter(prefix="/tools", tags=["tools"])


@router.get("", response_model=list[RepositoryItem])
async def list_tools() -> list[RepositoryItem]:
    service = get_repository_storage_service()
    return service.list_tools()


@router.get("/{code}", response_model=RepositoryItem)
async def get_tool(code: str) -> RepositoryItem:
    service = get_repository_storage_service()
    item = service.get_tool(code)
    if item is None:
        raise HTTPException(status_code=404, detail=f"Tool '{code}' not found")
    return item
