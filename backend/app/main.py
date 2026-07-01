from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.core.exceptions import AppException, app_exception_handler
from app.core.logging import configure_logging
from app.routers import health
from app.services.redis_service import RedisService


@asynccontextmanager
async def lifespan(app: FastAPI):
    configure_logging()

    settings = get_settings()

    app.state.redis_service = RedisService(settings.redis_url)

    yield

    await app.state.redis_service.close()


settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    debug=settings.debug,
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_exception_handler(AppException, app_exception_handler)

app.include_router(health.router)


@app.get("/", tags=["Root"])
async def root() -> dict[str, str]:
    return {
        "message": "Pipefy RAG Chat API",
        "docs": "/docs",
        "health": "/health",
    }