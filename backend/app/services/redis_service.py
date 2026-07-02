import logging

from redis.asyncio import Redis
from redis.exceptions import RedisError


logger = logging.getLogger(__name__)


class RedisService:
    def __init__(self, redis_url: str):
        self.redis_url = redis_url
        self.client: Redis = Redis.from_url(
            redis_url,
            decode_responses=False,
        )

    async def ping(self) -> bool:
        try:
            return bool(await self.client.ping())
        except RedisError:
            logger.warning("Redis is not available at %s", self.redis_url)
            return False

    async def close(self) -> None:
        await self.client.aclose()