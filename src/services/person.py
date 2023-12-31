from functools import lru_cache
from typing import Optional

from elasticsearch import AsyncElasticsearch, NotFoundError
from fastapi import Depends
from redis.asyncio import Redis

from db.implementation.search_engine import get_elastic

from db.implementation.cache import get_redis
from models.person import Person

# Elastic search docementation with examples - https://elasticsearch-dsl.readthedocs.io/en/latest/search_dsl.html#pagination
from elasticsearch import Elasticsearch
from elasticsearch_dsl import Search

PERSON_CACHE_EXPIRE_IN_SECONDS = 60 * 5  # 5 минут


class PersonService:
    def __init__(self, redis: Redis, elastic: AsyncElasticsearch):
        self.redis = redis
        self.elastic = elastic

    # get_by_id возвращает объект персон. Он опционален, так как фильм может отсутствовать в базе
    async def get_by_id(self, person_id: str) -> Optional[Person]:
        # Пытаемся получить данные из кеша, потому что оно работает быстрее
        person = await self._person_from_cache(person_id)
        if not person:
            # Если фильма нет в кеше, то ищем его в Elasticsearch
            person = await self._get_person_from_elastic(person_id)
            if not person_id:
                # Если он отсутствует в Elasticsearch, значит, фильма вообще нет в базе
                return None
            # Сохраняем фильм  в кеш
            await self._put_person_to_cache(person)

        return person
    
    async def add_person(self, person: Person) -> Optional[Person]:
        # Пытаемся получить данные из кеша, потому что оно работает быстрее
        await self._get_person_to_elastic(person)
       
        # Если фильма нет в кеше, то ищем его в Elasticsearch
        person = await self._get_person_from_elastic(person.id)
        if not person:
            return None
        
        return person


    # get_all возвращает лис объектов персон или None фильмов может и не быть в базе
    async def get_all_persons(self) -> Optional[list]:
        # Фильмы ищем в Elasticsearch
        persons = await self._get_all_persons_from_elastic()
        if not persons:
            # Если фильмы отсутствуют в Elasticsearch, значит, фильмов вообще нет в базе
            return None
        
        return persons

    async def _get_person_to_elastic(self, person: Person) -> Optional[Person]:
        try:
            self.elastic.index(index="persons", body=person.json(), id=person.id)
        except Exception:
            return None
        
        return person

    async def _get_person_from_elastic(self, person_id: str) -> Optional[Person]:
        try:
            doc = await self.elastic.get(index='persons', id=person_id)
        except NotFoundError:
            return None
        return Person(**doc['_source'])
    
    async def _get_all_persons_from_elastic(self) -> Optional[list]:
        try:
            persons = list
            search = Search(using=self.elastic, index="persons")

            # Stack overflow: https://stackoverflow.com/questions/50210299/how-to-get-all-documents-under-an-elasticsearch-index-with-python-client
            for hit in search.scan():
                person = Person(**hit['_source'])
                persons.append(person)

            return persons
            
        except NotFoundError:
            return None

    async def _person_from_cache(self, person_id: str) -> Optional[Person]:
        # Пытаемся получить данные о персоне из кеша, используя команду get
        # https://redis.io/commands/get/
        data = await self.redis.get(person_id)
        if not data:
            return None

        # pydantic предоставляет удобное API для создания объекта моделей из json
        person = Person.parse_raw(data)
        return person

    async def _put_person_to_cache(self, person: Person):
        # Сохраняем данные о фильме, используя команду set
        # Выставляем время жизни кеша — 5 минут
        # https://redis.io/commands/set/
        # pydantic позволяет сериализовать модель в json
        await self.redis.set(person.id, person.json(), PERSON_CACHE_EXPIRE_IN_SECONDS)


@lru_cache()
def get_person_service(
        redis: Redis = Depends(get_redis),
        elastic: AsyncElasticsearch = Depends(get_elastic),
) -> PersonService:
    return PersonService(redis, elastic)