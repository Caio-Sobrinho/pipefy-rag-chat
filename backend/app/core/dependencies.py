from fastapi import Request

from app.config import Settings, get_settings
from app.services.redis_service import RedisService


def get_redis_service(request: Request) -> RedisService:
    return request.app.state.redis_service


def get_app_settings() -> Settings:
    return get_settings()