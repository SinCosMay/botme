import json

import redis

from app.core.config import settings


_cache_client: redis.Redis | None = None


def get_cache_client() -> redis.Redis:
    global _cache_client
    if _cache_client is None:
        _cache_client = redis.from_url(settings.REDIS_URL, decode_responses=True)
    return _cache_client


def get_cached_json(key: str) -> dict | None:
    try:
        raw = get_cache_client().get(key)
    except redis.RedisError:
        return None

    if not raw:
        return None

    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return None


def set_cached_json(key: str, payload: dict, ttl_seconds: int) -> None:
    try:
        get_cache_client().setex(key, ttl_seconds, json.dumps(payload))
    except redis.RedisError:
        return
