from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from app.core.dependencies import get_redis_service
from app.services.redis_service import RedisService


router = APIRouter(tags=["Health"])


class HealthResponse(BaseModel):
    status: str
    redis: str


@router.get("/health", response_model=HealthResponse)
async def health_check(
    redis_service: RedisService = Depends(get_redis_service),
) -> HealthResponse:
    redis_connected = await redis_service.ping()

    if not redis_connected:
        raise HTTPException(
            status_code=503,
            detail={
                "status": "error",
                "redis": "disconnected",
            },
        )

    return HealthResponse(
        status="ok",
        redis="connected",
    )