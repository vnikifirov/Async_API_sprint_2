from typing import List

import aiohttp
import pytest
import redis

from elasticsearch import AsyncElasticsearch
from tests.settings import TestSettings as test_settings

@pytest.fixture(scope='session')
@pytest.mark.asyncio
async def get_es_client():
    client = AsyncElasticsearch(hosts=test_settings.es_host)
    yield client
    await client.close()

@pytest.fixture(scope='session')
@pytest.mark.asyncio
async def get_redis_client():
    redis = redis.Redis(host='localhost', port=6379, db=0)
    yield redis
    await redis.close()