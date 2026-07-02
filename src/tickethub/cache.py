import json
import logging
from typing import Any

from redis.asyncio import Redis
from redis.exceptions import RedisError

from tickethub.config import settings

logger = logging.getLogger(__name__)

redis_client = Redis.from_url(
    settings.redis_url,
    decode_responses=True,
)


async def get_cache(key: str) -> Any | None:
    # Dohvaća vrijednost iz cachea ako je cache uključen
    if not settings.cache_enabled:
        return None

    try:
        cached_value = await redis_client.get(key)

        if cached_value is None:
            return None

        return json.loads(cached_value)
    except (RedisError, json.JSONDecodeError):
        logger.warning("Neuspješan dohvat iz cachea za ključ: %s", key)
        return None


async def set_cache(
    key: str,
    value: Any,
    ttl_seconds: int | None = None,
) -> None:
    # Sprema vrijednost u cache
    if not settings.cache_enabled:
        return

    try:
        await redis_client.set(
            key,
            json.dumps(value),
            ex=ttl_seconds or settings.cache_ttl_seconds,
        )
    except (RedisError, TypeError):
        logger.warning("Neuspješno spremanje u cache za ključ: %s", key)


async def delete_cache_pattern(pattern: str) -> None:
    # Briše cache ključeve koji odgovaraju zadanom uzorku
    if not settings.cache_enabled:
        return

    try:
        async for key in redis_client.scan_iter(match=pattern):
            await redis_client.delete(key)
    except RedisError:
        logger.warning("Neuspješno brisanje cachea za uzorak: %s", pattern)
