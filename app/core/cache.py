import json
from typing import Any

import redis.asyncio as aioredis

from app.core.config import settings

DEFAULT_TTL = 60  # 1 minuto


async def _get_redis() -> aioredis.Redis:
    return aioredis.from_url(settings.redis_url)


async def cache_get(key: str) -> Any | None:
    redis = await _get_redis()
    try:
        data = await redis.get(key)
        if data:
            return json.loads(data)
        return None
    finally:
        await redis.aclose()


async def cache_set(key: str, value: Any, ttl: int = DEFAULT_TTL) -> None:
    redis = await _get_redis()
    try:
        await redis.set(key, json.dumps(value, default=str), ex=ttl)
    finally:
        await redis.aclose()


async def cache_delete_pattern(pattern: str) -> None:
    redis = await _get_redis()
    try:
        async for key in redis.scan_iter(match=pattern):
            await redis.delete(key)
    finally:
        await redis.aclose()
