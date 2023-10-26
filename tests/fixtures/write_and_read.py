import json
from typing import List

import aiohttp
import pytest
import redis

from elasticsearch import AsyncElasticsearch
from tests.settings import TestSettings as test_settings

@pytest.fixture
@pytest.mark.asyncio
def es_write_data():
    async def inner(es_client: AsyncElasticsearch, data: List[dict]):
        bulk_query = get_es_bulk_query(data, test_settings.es_index, test_settings.es_id_field)
        str_query = '\n'.join(bulk_query) + '\n'

        response = await es_client.bulk(str_query, refresh=True)

        if response['errors']:
            raise Exception('Ошибка записи данных в Elasticsearch')
    return inner

@pytest.fixture
@pytest.mark.asyncio
def redis_get_by_id():
    async def inner(redis_client: Redis, id: str):
        response = await redis_client.get(id)
        return response
    return inner

@pytest.fixture
@pytest.mark.asyncio
def get_es_bulk_query():
    async def inner(data: List[dict]):
        bulk_query = []
        for row in data:
            bulk_query.extend([
                json.dumps({'index': {'_index': test_settings.es_index, '_id': row[test_settings.es_id_field]}}),
                json.dumps(row)
            ])
    return inner