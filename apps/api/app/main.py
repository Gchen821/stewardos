from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.router import api_router
from app.config import get_settings
from app.services.repository_storage import get_repository_storage_service


@asynccontextmanager
async def lifespan(_: FastAPI):
    get_repository_storage_service()
    yield


settings = get_settings()

app = FastAPI(
    title=settings.project_name,
    description="StewardOS backend API template powered by FastAPI.",
    version="0.1.0",
    docs_url=settings.docs_url,
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix=settings.api_v1_prefix)
