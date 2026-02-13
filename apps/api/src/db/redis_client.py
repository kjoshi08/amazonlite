import os

import redis

try:
    # Optional: if your project has settings, we use it as fallback
    from src.core.config import settings  # type: ignore
except Exception:
    settings = None  # type: ignore

_redis_client = None


def _redis_url() -> str:
    # 1) Prefer environment variable (docker-compose already sets this)
    env_url = os.getenv("REDIS_URL")
    if env_url:
        return env_url

    # 2) Fallback to settings if it exists
    if settings is not None and hasattr(settings, "REDIS_URL"):
        return getattr(settings, "REDIS_URL")

    # 3) Last resort default
    return "redis://redis:6379/0"


def get_redis():
    global _redis_client
    if _redis_client is None:
        _redis_client = redis.Redis.from_url(_redis_url(), decode_responses=True)
    return _redis_client


def ping_redis():
    return get_redis().ping()
