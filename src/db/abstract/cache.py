from typing import Optional
from redis.asyncio import Redis

class AsyncCacheStorage:
    @abstractmethod
    async def get(self, key: str, **kwargs):
        pass

    @abstractmethod
    async def set(self, key: str, value: str, expire: int, **kwargs):
        pass