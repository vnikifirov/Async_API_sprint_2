from typing import Optional
from elasticsearch import AsyncElasticsearch

#es: Optional[AsyncElasticsearch] = None
es: AsyncElasticsearch | None = None

class SearchEngineRepository(AsyncSearchEngine):
    async def get(self, index: str, id: int, **kwargs):
        return self.es.get(index=index, id=id)