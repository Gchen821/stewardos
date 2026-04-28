from fastapi import APIRouter

from app.api.routes.agents import router as agents_router
from app.api.routes.auth import router as auth_router
from app.api.routes.bindings import router as bindings_router
from app.api.routes.chat import router as chat_router
from app.api.routes.conversations import router as conversations_router
from app.api.routes.meta import router as meta_router
from app.api.routes.skills import router as skills_router
from app.api.routes.tools import router as tools_router
from app.api.routes.users import router as users_router

api_router = APIRouter()
api_router.include_router(meta_router)
api_router.include_router(auth_router)
api_router.include_router(users_router)
api_router.include_router(agents_router)
api_router.include_router(skills_router)
api_router.include_router(tools_router)
api_router.include_router(bindings_router)
api_router.include_router(conversations_router)
api_router.include_router(chat_router)
