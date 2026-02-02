import redis.asyncio as redis
from app.config import settings
import json
from typing import Optional, Dict, Any

redis_client: Optional[redis.Redis] = None


async def init_redis():
    """Initialize Redis connection"""
    global redis_client
    redis_client = await redis.from_url(
        settings.REDIS_URL,
        encoding="utf8",
        decode_responses=True
    )


async def close_redis():
    """Close Redis connection"""
    global redis_client
    if redis_client:
        await redis_client.close()


async def get_inventory_cache(store_id: str, product_id: str) -> Optional[Dict[str, Any]]:
    """Get cached inventory"""
    if not redis_client:
        return None
    cache_key = f"inventory:{store_id}:{product_id}"
    cached = await redis_client.get(cache_key)
    return json.loads(cached) if cached else None


async def set_inventory_cache(store_id: str, product_id: str, data: Dict[str, Any]):
    """Cache inventory with TTL"""
    if not redis_client:
        return
    cache_key = f"inventory:{store_id}:{product_id}"
    ttl = settings.REDIS_CACHE_TTL_MINUTES * 60
    await redis_client.setex(
        cache_key,
        ttl,
        json.dumps(data)
    )


async def invalidate_inventory_cache(store_id: str, product_id: str):
    """Invalidate specific inventory cache"""
    if not redis_client:
        return
    cache_key = f"inventory:{store_id}:{product_id}"
    await redis_client.delete(cache_key)


async def invalidate_store_cache(store_id: str):
    """Invalidate all inventory cache for a store"""
    if not redis_client:
        return
    pattern = f"inventory:{store_id}:*"
    keys = await redis_client.keys(pattern)
    if keys:
        await redis_client.delete(*keys)


async def get_reservation_cache(order_id: str) -> Optional[Dict[str, Any]]:
    """Get cached reservation (for quick expiry check)"""
    if not redis_client:
        return None
    cache_key = f"reservation:{order_id}"
    cached = await redis_client.get(cache_key)
    return json.loads(cached) if cached else None


async def set_reservation_cache(order_id: str, data: Dict[str, Any]):
    """Cache reservation with reservation validity TTL"""
    if not redis_client:
        return
    cache_key = f"reservation:{order_id}"
    ttl = settings.RESERVATION_VALIDITY_MINUTES * 60
    await redis_client.setex(
        cache_key,
        ttl,
        json.dumps(data)
    )


async def invalidate_reservation_cache(order_id: str):
    """Invalidate reservation cache"""
    if not redis_client:
        return
    cache_key = f"reservation:{order_id}"
    await redis_client.delete(cache_key)
