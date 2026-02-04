import json
import logging
from typing import Any, Optional

import redis

from .config import get_settings

logger = logging.getLogger(__name__)


class RedisCache:
    def __init__(self) -> None:
        settings = get_settings()
        self._redis = redis.Redis(
            host=settings.redis_host or "localhost",
            port=settings.redis_port or 6379,
            db=settings.redis_db or 0,
            password=settings.redis_password,
            decode_responses=True,
        )
        self._ttl = settings.cache_ttl_seconds or 300

    def get(self, key: str) -> Optional[Any]:
        try:
            value = self._redis.get(key)
            if value:
                return json.loads(value)
        except Exception as e:
            logger.warning(f"Cache get failed for key {key}: {e}")
        return None

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        try:
            serialized = json.dumps(value)
            self._redis.set(key, serialized, ex=ttl or self._ttl)
        except Exception as e:
            logger.warning(f"Cache set failed for key {key}: {e}")

    def delete(self, key: str) -> None:
        try:
            self._redis.delete(key)
        except Exception as e:
            logger.warning(f"Cache delete failed for key {key}: {e}")

    def exists(self, key: str) -> bool:
        try:
            return bool(self._redis.exists(key))
        except Exception as e:
            logger.warning(f"Cache exists failed for key {key}: {e}")
            return False


# Global cache instance
_cache: Optional[RedisCache] = None


def get_cache() -> RedisCache:
    global _cache
    if _cache is None:
        _cache = RedisCache()
    return _cache