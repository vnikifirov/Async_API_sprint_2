from functools import lru_cache
from typing import Optional

from elasticsearch import AsyncElasticsearch, NotFoundError
from fastapi import Depends
from redis.asyncio import Redis

from db.implementation.search_engine import get_elastic

from db.implementation.cache import get_redis
from models.genre import Genre

# Elastic search docementation with examples - https://elasticsearch-dsl.readthedocs.io/en/latest/search_dsl.html#pagination
from elasticsearch import Elasticsearch
from elasticsearch_dsl import Search

GENRE_CACHE_EXPIRE_IN_SECONDS = 60 * 5  # 5 минут


class GenreService:
    def __init__(self, redis: Redis, elastic: AsyncElasticsearch):
        self.redis = redis
        self.elastic = elastic

    # get_by_id возвращает объект жанра. Он опционален, так как жанр может отсутствовать в базе
    async def get_by_id(self, genre_id: str) -> Optional[Genre]:
        # Пытаемся получить данные из кеша, потому что оно работает быстрее
        genre = await self._genre_from_cache(genre_id)
        if not genre:
            # Если фильма нет в кеше, то ищем его в Elasticsearch
            genre = await self._get_genre_from_elastic(genre_id)
            if not genre_id:
                # Если он отсутствует в Elasticsearch, значит, фильма вообще нет в базе
                return None
            # Сохраняем фильм  в кеш
            await self._put_genre_to_cache(genre)

        return genre
    
    # get_by_name возвращает объект жанра. Он опционален, так как фильм может отсутствовать в базе
    async def get_by_id(self, genre_id: str) -> Optional[Genre]:
        # Пытаемся получить данные из кеша, потому что оно работает быстрее
        genre = await self._genre_from_cache(genre_id)
        if not genre:
            # Если фильма нет в кеше, то ищем его в Elasticsearch
            genre = await self._get_genre_from_elastic(genre_id)
            if not genre_id:
                # Если он отсутствует в Elasticsearch, значит, фильма вообще нет в базе
                return None
            # Сохраняем фильм  в кеш
            await self._put_genre_to_cache(genre)

        return genre
    
    # get_by_name возвращает объект жанра. Он опционален, так как фильм может отсутствовать в базе
    async def get_by_name(self, genre_name: str) -> Optional[Genre]:
        # Пытаемся получить данные из кеша, потому что оно работает быстрее
        #genre = await self._genre_from_cache(None, genre_name)
        #if not genre:
            # Если фильма нет в кеше, то ищем его в Elasticsearch
        genre = await self._get_genre_by_name_from_elastic(genre_name)
        if not genre:
            # Если он отсутствует в Elasticsearch, значит, фильма вообще нет в базе
            return None

        return genre

    async def add_genre(self, genre: Genre) -> Optional[Genre]:
        # Пытаемся получить данные из кеша, потому что оно работает быстрее
        await self._get_genre_to_elastic(genre)
       
        # Если фильма нет в кеше, то ищем его в Elasticsearch
        genre = await self._get_genre_to_elastic(genre.id)
        if not genre:
            return None
        
        return genre


    # get_all возвращает лис объектов персон или None фильмов может и не быть в базе
    async def get_all_genres(self) -> Optional[list]:
        # Фильмы ищем в Elasticsearch
        genres = await self._get_all_genres_from_elastic()
        if not genres:
            # Если фильмы отсутствуют в Elasticsearch, значит, фильмов вообще нет в базе
            return None
        
        return genres

    async def _get_genre_to_elastic(self, genre: Genre) -> Optional[Genre]:
        try:
            self.elastic.index(index="genres", body=genre.json(), id=genre.id)
        except Exception:
            return None
        
        return genre

    async def _get_genre_from_elastic(self, genres_id: str) -> Optional[Genre]:
        try:
            doc = await self.elastic.get(index='genres', id=genres_id)
        except NotFoundError:
            return None
        return Genre(**doc['_source'])
    
    async def _get_genre_by_name_from_elastic(self, name) -> Optional[list]:
        try:
            result = Genre
            search = Search(using=self.elastic, index="genres")

            # Stack overflow: https://stackoverflow.com/questions/50210299/how-to-get-all-documents-under-an-elasticsearch-index-with-python-client
            for hit in search.scan():
                genre = Genre(**hit['_source'])
                if genre.name == name:
                    result = genre

            return result
            
        except NotFoundError:
            return None

    async def _get_all_genres_from_elastic(self) -> Optional[list]:
        try:
            genres = list
            search = Search(using=self.elastic, index="genres")

            # Stack overflow: https://stackoverflow.com/questions/50210299/how-to-get-all-documents-under-an-elasticsearch-index-with-python-client
            for hit in search.scan():
                genre = Genre(**hit['_source'])
                genres.append(genre)

            return genres
            
        except NotFoundError:
            return None

    async def _genre_from_cache(self, genre_id: str) -> Optional[Genre]:
        # Пытаемся получить данные о персоне из кеша, используя команду get
        # https://redis.io/commands/get/
        
        data = await self.redis.get(genre_id)

        if not data:
            return None

        # pydantic предоставляет удобное API для создания объекта моделей из json
        genre = Genre.parse_raw(data)
        return genre

    async def _put_genre_to_cache(self, genre: Genre):
        # Сохраняем данные о фильме, используя команду set
        # Выставляем время жизни кеша — 5 минут
        # https://redis.io/commands/set/
        # pydantic позволяет сериализовать модель в json
        await self.redis.set(genre.id, genre.json(), GENRE_CACHE_EXPIRE_IN_SECONDS)


@lru_cache()
def get_genre_service(
        redis: Redis = Depends(get_redis),
        elastic: AsyncElasticsearch = Depends(get_elastic),
) -> GenreService:
    return GenreService(redis, elastic)