
import aiohttp
import pytest

from elasticsearch import AsyncElasticsearch
from tests.settings import TestSettings as test_settings
from tests.conftest import es_write_data, get_es_client, make_get_request, get_films_data

@pytest.fixture
@pytest.mark.asyncio
async def make_get_request(url, params = ""):
    session = aiohttp.ClientSession()

    async with session.get(url, params=params) as response:
        yield response

    await session.close()
    