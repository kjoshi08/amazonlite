import json
from typing import Any, Optional

from src.db.redis_client import get_redis


def get_cache_json(key: str) -> Optional[Any]:
    r = get_redis()
    val = r.get(key)
    if not val:
        return None
    return json.loads(val)


def set_cache_json(key: str, value: Any, ttl_seconds: int = 30) -> None:
    r = get_redis()
    r.setex(key, ttl_seconds, json.dumps(value))
