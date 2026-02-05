"""Redis-based caching and rate limiting.

Provides production-ready implementations that fall back gracefully
when Redis is unavailable.
"""

import asyncio
import hashlib
import json
from collections.abc import Callable
from functools import wraps
from typing import Any, TypeVar

from intelli.config import settings

T = TypeVar("T")

# Lazy Redis connection
_redis_client = None


async def get_redis():
    """Get or create Redis client with lazy initialization."""
    global _redis_client

    if _redis_client is not None:
        return _redis_client

    if not settings.redis_url:
        return None

    try:
        import redis.asyncio as redis

        _redis_client = redis.from_url(
            settings.redis_url,
            encoding="utf-8",
            decode_responses=True,
        )
        # Test connection
        await _redis_client.ping()
        return _redis_client
    except Exception:
        return None


class RedisRateLimiter:
    """Redis-based sliding window rate limiter.

    Falls back to allowing requests if Redis is unavailable.
    Uses MULTI/EXEC for atomic operations.
    """

    def __init__(self, prefix: str = "ratelimit"):
        self.prefix = prefix

    def _key(self, identifier: str) -> str:
        return f"{self.prefix}:{identifier}"

    async def is_allowed(
        self,
        identifier: str,
        limit: int,
        window_seconds: int = 60,
    ) -> tuple[bool, int, int]:
        """Check if request is allowed under rate limit.

        Args:
            identifier: Unique identifier (API key ID, IP, etc.)
            limit: Max requests per window
            window_seconds: Time window in seconds

        Returns:
            Tuple of (is_allowed, remaining, reset_after_seconds)
        """
        redis = await get_redis()
        if redis is None:
            # Fail open if Redis unavailable
            return True, limit, window_seconds

        import time

        now = time.time()
        key = self._key(identifier)
        window_start = now - window_seconds

        try:
            pipe = redis.pipeline()
            # Remove old entries
            pipe.zremrangebyscore(key, 0, window_start)
            # Count current entries
            pipe.zcard(key)
            # Add current request (will be committed if under limit)
            pipe.zadd(key, {str(now): now})
            # Set expiry
            pipe.expire(key, window_seconds)
            results = await pipe.execute()

            current_count = results[1]

            if current_count >= limit:
                # Over limit - remove the request we just added
                await redis.zrem(key, str(now))
                # Get oldest entry for reset time
                oldest = await redis.zrange(key, 0, 0, withscores=True)
                reset_after = int(oldest[0][1] + window_seconds - now) if oldest else window_seconds
                return False, 0, reset_after

            remaining = limit - current_count - 1
            return True, remaining, window_seconds

        except Exception:
            # Fail open on errors
            return True, limit, window_seconds

    async def get_remaining(
        self,
        identifier: str,
        limit: int,
        window_seconds: int = 60,
    ) -> int:
        """Get remaining requests in current window."""
        redis = await get_redis()
        if redis is None:
            return limit

        import time

        now = time.time()
        key = self._key(identifier)
        window_start = now - window_seconds

        try:
            # Remove old and count
            await redis.zremrangebyscore(key, 0, window_start)
            count = await redis.zcard(key)
            return max(0, limit - count)
        except Exception:
            return limit


class RedisCache:
    """Simple Redis cache with JSON serialization.

    Falls back to no-op if Redis unavailable.
    """

    def __init__(self, prefix: str = "cache", default_ttl: int = 300):
        self.prefix = prefix
        self.default_ttl = default_ttl

    def _key(self, key: str) -> str:
        return f"{self.prefix}:{key}"

    async def get(self, key: str) -> Any | None:
        """Get value from cache."""
        redis = await get_redis()
        if redis is None:
            return None

        try:
            value = await redis.get(self._key(key))
            if value is None:
                return None
            return json.loads(value)
        except Exception:
            return None

    async def set(
        self,
        key: str,
        value: Any,
        ttl: int | None = None,
    ) -> bool:
        """Set value in cache."""
        redis = await get_redis()
        if redis is None:
            return False

        try:
            serialized = json.dumps(value, default=str)
            await redis.setex(
                self._key(key),
                ttl or self.default_ttl,
                serialized,
            )
            return True
        except Exception:
            return False

    async def delete(self, key: str) -> bool:
        """Delete value from cache."""
        redis = await get_redis()
        if redis is None:
            return False

        try:
            await redis.delete(self._key(key))
            return True
        except Exception:
            return False

    async def get_or_set(
        self,
        key: str,
        factory: Callable[[], T],
        ttl: int | None = None,
    ) -> T:
        """Get from cache or compute and cache."""
        value = await self.get(key)
        if value is not None:
            return value

        # Compute value
        if asyncio.iscoroutinefunction(factory):
            value = await factory()
        else:
            value = factory()

        await self.set(key, value, ttl)
        return value


def cached(
    key_prefix: str,
    ttl: int = 300,
    key_builder: Callable[..., str] | None = None,
):
    """Decorator for caching function results.

    Args:
        key_prefix: Prefix for cache keys
        ttl: Time to live in seconds
        key_builder: Function to build cache key from args
    """
    cache = RedisCache(prefix=key_prefix, default_ttl=ttl)

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Build cache key
            if key_builder:
                cache_key = key_builder(*args, **kwargs)
            else:
                # Default: hash args
                key_data = json.dumps(
                    {"args": args, "kwargs": kwargs},
                    sort_keys=True,
                    default=str,
                )
                cache_key = hashlib.md5(key_data.encode()).hexdigest()

            # Try cache
            cached_value = await cache.get(cache_key)
            if cached_value is not None:
                return cached_value

            # Compute and cache
            if asyncio.iscoroutinefunction(func):
                result = await func(*args, **kwargs)
            else:
                result = func(*args, **kwargs)

            await cache.set(cache_key, result, ttl)
            return result

        return wrapper

    return decorator


# Global instances
rate_limiter = RedisRateLimiter()
cache = RedisCache()
