import redis.asyncio as aioredis
from src.config.settings import settings
import json
import structlog
import os
from typing import Optional, Any

logger = structlog.get_logger()

class RedisCache:
    def __init__(self):
        self.redis = None

    async def connect(self):
        if os.environ.get("TESTING") == "1":
            return
        self.redis = aioredis.from_url(settings.REDIS_URL, decode_responses=True)
        logger.info("Connected to Redis")

    async def close(self):
        if self.redis:
            await self.redis.close()

    async def get(self, key: str) -> Optional[Any]:
        if not self.redis or os.environ.get("TESTING") == "1":
            return None
        data = await self.redis.get(key)
        return json.loads(data) if data else None

    async def set(self, key: str, value: Any, ttl_seconds: int = 3600):
        if not self.redis or os.environ.get("TESTING") == "1":
            return
        await self.redis.set(key, json.dumps(value), ex=ttl_seconds)
        
    async def delete_by_prefix(self, prefix: str):
        if not self.redis or os.environ.get("TESTING") == "1":
            return
        # A simple scan to clear cache for a district
        cursor = '0'
        while cursor != 0:
            cursor, keys = await self.redis.scan(cursor=cursor, match=f"{prefix}*", count=100)
            if keys:
                await self.redis.delete(*keys)

redis_cache = RedisCache()
