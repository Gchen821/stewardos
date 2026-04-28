from contextlib import asynccontextmanager
from uuid import uuid4

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from app.api.router import api_router
from app.config import get_settings
from app.db.init_db import init_db
from app.gateway import ExecutionGateway, GatewayCall, reset_current_request_id, set_current_request_id


@asynccontextmanager
async def lifespan(_: FastAPI):
    init_db()
    yield


settings = get_settings()
gateway = ExecutionGateway()

app = FastAPI(
    title=settings.project_name,
    version="0.1.0",
    docs_url=settings.docs_url,
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def request_tracking_middleware(request: Request, call_next):
    request_id = request.headers.get("X-Request-Id") or f"req_{uuid4().hex}"
    request.state.request_id = request_id
    token = set_current_request_id(request_id)
    trace_context = gateway.build_trace_context(
        scope="api_request",
        target_type="http",
        session_id=request.headers.get("X-Session-Id") or f"http:{request_id}",
    )
    try:
        response = await gateway.execute_async(
            GatewayCall(
                kind="api",
                target=f"{request.method} {request.url.path}",
                metadata={
                    "method": request.method,
                    "path": request.url.path,
                },
            ),
            trace_context,
            lambda: call_next(request),
        )
    finally:
        reset_current_request_id(token)
    response.headers["X-Request-Id"] = request_id
    return response

app.include_router(api_router, prefix=settings.api_v1_prefix)
