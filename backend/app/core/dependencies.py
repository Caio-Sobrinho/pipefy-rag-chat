from fastapi import Request

from app.config import Settings, get_settings
from app.services.chat_service import ChatService
from app.services.document_service import DocumentService
from app.services.redis_service import RedisService
from app.services.redis_vector_service import RedisVectorService


def get_redis_service(request: Request) -> RedisService:
    return request.app.state.redis_service


def get_redis_vector_service(request: Request) -> RedisVectorService:
    return request.app.state.redis_vector_service


def get_document_service(request: Request) -> DocumentService:
    return request.app.state.document_service


def get_chat_service(request: Request) -> ChatService:
    return request.app.state.chat_service


def get_app_settings() -> Settings:
    return get_settings()