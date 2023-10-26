from typing import Optional
from redis.asyncio import Redis
from db.abstract.cache import AsyncCacheStorage
#redis: Optional[Redis] = None
redis: Redis | None = None

class MemcachedRepository(AsyncCacheStorage):
    # Функция понадобится при внедрении зависимостей    
    async def get(self, key: str, **kwargs):
        return await redis.get(key)

    async def set(self, key: str, value: str, expire: int, **kwargs):
        await redis.set(key, value, expire)