
from typing import Any, Optional
import json
from redis import Redis
from app.core.config import settings

from redis.retry import Retry
from redis.backoff import ExponentialBackoff

retry = Retry(ExponentialBackoff(), 3)
redis_client = Redis(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    db=settings.REDIS_DB,
    password=settings.REDIS_PASSWORD,
    decode_responses=True,
    retry=retry,
    socket_timeout=5,
    socket_connect_timeout=5
)

def cache_get(key: str) -> Optional[Any]:
    """Get value from cache"""
    try:
        value = redis_client.get(key)
        return json.loads(value) if value else None
    except json.JSONDecodeError:
        logger.error(f"Failed to decode cached value for key: {key}")
        return None
    except redis.RedisError as e:
        logger.error(f"Redis error while getting key {key}: {str(e)}")
        return None

def cache_set(key: str, value: Any, expire: int = 3600) -> bool:
    """Set value in cache"""
    try:
        return redis_client.setex(key, expire, json.dumps(value))
    except (json.JSONEncodeError, redis.RedisError) as e:
        logger.error(f"Failed to cache value for key {key}: {str(e)}")
        return False
