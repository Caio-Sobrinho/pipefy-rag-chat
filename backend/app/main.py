from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.core.exceptions import AppException, app_exception_handler
from app.routers import chat, documents, health, search, upload
from app.services.chat_service import ChatService
from app.services.document_service import DocumentService
from app.services.redis_service import RedisService
from app.services.redis_vector_service import RedisVectorService
from app.services.retriever_service import RetrieverService


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()

    app.state.redis_service = RedisService(settings.redis_url)
    app.state.redis_vector_service = RedisVectorService(
        redis_service=app.state.redis_service,
        settings=settings,
    )
    app.state.document_service = DocumentService(
        settings=settings,
        redis_vector_service=app.state.redis_vector_service,
    )
    app.state.retriever_service = RetrieverService(
        settings=settings,
        document_service=app.state.document_service,
        redis_vector_service=app.state.redis_vector_service,
    )
    app.state.chat_service = ChatService()

    yield

    await app.state.redis_service.close()


settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    version="0.6.0",
    debug=settings.debug,
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
app.include_router(upload.router)
app.include_router(documents.router)
app.include_router(search.router)
app.include_router(chat.router)


@app.get("/", tags=["Root"])
async def root() -> dict[str, str]:
    return {
        "message": "Pipefy RAG Chat API",
        "docs": "/docs",
        "health": "/health",
    }