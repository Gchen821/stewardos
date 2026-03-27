from fastapi import APIRouter

from app.api.routes.agents import router as agents_router
from app.api.routes.auth import router as auth_router
from app.api.routes.chat import router as chat_router
from app.api.routes.meta import router as meta_router
from app.api.routes.models import router as models_router
from app.api.routes.permissions import router as permissions_router
from app.api.routes.skills import router as skills_router

api_router = APIRouter()
api_router.include_router(meta_router)
api_router.include_router(auth_router)
api_router.include_router(chat_router)
api_router.include_router(agents_router)
api_router.include_router(skills_router)
api_router.include_router(models_router)
api_router.include_router(permissions_router)
