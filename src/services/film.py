from functools import lru_cache
from typing import Optional
from db.abstract.cache import AsyncCacheStorage
from db.abstract.search_engine import AsyncSearchEngine

from elasticsearch import AsyncElasticsearch, NotFoundError
from fastapi import Depends
from redis.asyncio import Redis

from db.implementation.search_engine import SearchEngineRepository
from db.implementation.cache import MemcachedRepository

from models.film import Film

# Elastic search docementation with examples - https://elasticsearch-dsl.readthedocs.io/en/latest/search_dsl.html#pagination
from elasticsearch import Elasticsearch
from elasticsearch_dsl import Search

FILM_CACHE_EXPIRE_IN_SECONDS = 60 * 5  # 5 минут


class FilmService:
    def __init__(self, cache: AsyncCacheStorage, search_engine: AsyncSearchEngine):
        self.cache = cache
        self.search_engine = search_engine

    # get_by_id возвращает объект фильма. Он опционален, так как фильм может отсутствовать в базе
    async def get_by_id(self, film_id: str) -> Optional[Film]:
        # Пытаемся получить данные из кеша, потому что оно работает быстрее
        film = await self._film_from_cache(film_id)
        if not film:
            # Если фильма нет в кеше, то ищем его в Elasticsearch
            film = await self._get_film_from_elastic(film_id)
            if not film:
                # Если он отсутствует в Elasticsearch, значит, фильма вообще нет в базе
                return None
            # Сохраняем фильм  в кеш
            await self._put_film_to_cache(film)

        return film
    
    # get_all возвращает лис объектов фильма или None фильмов может и не быть в базе
    async def get_all(self, page_size, page_number, query) -> Optional[list]:
        # Фильмы ищем в Elasticsearch
        films = await self._get_all_film_from_elastic(page_size, page_number, query)
        if not films:
            # Если фильмы отсутствуют в Elasticsearch, значит, фильмов вообще нет в базе
            return None
        
        return films

    async def _get_film_from_elastic(self, film_id: str) -> Optional[Film]:
        try:
            doc = await self.search_engine.get(index='movies', id=film_id)
        except NotFoundError:
            return None
        return Film(**doc['_source'])
    
    async def _get_all_film_from_elastic(self, page_size, page_number, query) -> Optional[list]:
        movies = list

        # Разбиение на страницы Python
        # Статья: https://dev.to/emilossola/a-step-by-step-guide-for-pagination-in-python-1464
        start_index = (page_number - 1) * page_size
        end_index = page_number * page_size

        # Документация ElasticSeach - https://elasticsearch-py.readthedocs.io/en/master/api.html
        # Погинация документация - https://www.elastic.co/guide/en/elasticsearch/reference/current/paginate-search-results.html#paginate-search-results
        # Поиск по полям класса ElasticSeach - https://stackoverflow.com/questions/37709100/how-do-i-do-a-partial-match-in-elasticsearch 
        search = Search(using=self.search_engine, index="movies", body= { "from": start_index, "size": end_index, "query": { query } })

        # Stack overflow: https://stackoverflow.com/questions/50210299/how-to-get-all-documents-under-an-elasticsearch-index-with-python-client
        for hit in search.scan():
            movie = Film(**hit['_source'])
            movies.append(movie)

        return movies

    async def _film_from_cache(self, film_id: str) -> Optional[Film]:
        # Пытаемся получить данные о фильме из кеша, используя команду get
        # https://redis.io/commands/get/
        data = await self.cache.get(film_id)
        if not data:
            return None

        # pydantic предоставляет удобное API для создания объекта моделей из json
        film = Film.parse_raw(data)
        return film

    async def _put_film_to_cache(self, film: Film):
        # Сохраняем данные о фильме, используя команду set
        # Выставляем время жизни кеша — 5 минут
        # https://redis.io/commands/set/
        # pydantic позволяет сериализовать модель в json
        await self.cache.set(film.id, film.json(), FILM_CACHE_EXPIRE_IN_SECONDS)


@lru_cache()
def get_film_service(
        #redis: Redis = Depends(get_redis),
        cache: AsyncCacheStorage = Depends(MemcachedRepository),
        search_engine: AsyncSearchEngine= Depends(SearchEngineRepository),
) -> FilmService:
    return FilmService(cache, search_engine)
