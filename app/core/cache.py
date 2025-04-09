
from typing import Any, Optional
import json
from redis import Redis
from app.core.config import settings

redis_client = Redis(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    db=0,
    decode_responses=True
)

def cache_get(key: str) -> Optional[Any]:
    """Get value from cache"""
    try:
        value = redis_client.get(key)
        return json.loads(value) if value else None
    except:
        return None

def cache_set(key: str, value: Any, expire: int = 3600) -> bool:
    """Set value in cache"""
    try:
        return redis_client.setex(key, expire, json.dumps(value))
    except:
        return False
