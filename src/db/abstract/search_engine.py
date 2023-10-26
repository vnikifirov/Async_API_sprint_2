from typing import Optional
from redis.asyncio import Redis

class AsyncSearchEngine:
    @abstractmethod
    async def get(self, index: str, id: int, **kwargs):
        pass