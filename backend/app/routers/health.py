from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from app.config import Settings
from app.core.dependencies import get_app_settings, get_redis_service
from app.services.redis_service import RedisService


router = APIRouter(tags=["Health"])


class HealthResponse(BaseModel):
    status: str
    api: str
    redis: str
    environment: str


@router.get("/health", response_model=HealthResponse)
async def health_check(
    redis_service: RedisService = Depends(get_redis_service),
    settings: Settings = Depends(get_app_settings),
) -> HealthResponse:
    redis_connected = await redis_service.ping()

    if settings.redis_required and not redis_connected:
        raise HTTPException(
            status_code=503,
            detail={
                "status": "error",
                "api": "running",
                "redis": "disconnected",
                "environment": settings.app_env,
            },
        )

    return HealthResponse(
        status="ok" if redis_connected else "degraded",
        api="running",
        redis="connected" if redis_connected else "disconnected",
        environment=settings.app_env,
    )