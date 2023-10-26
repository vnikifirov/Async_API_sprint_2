import aiohttp
import pytest

from elasticsearch import AsyncElasticsearch

from tests.settings import TestSettings as test_settings
from tests.conftest import es_write_data, get_es_client, make_get_request, get_genres_data

@pytest.mark.asyncio
async def test_get_genres_all(get_genres_data, get_es_client, es_write_data):
    # 1. Генерируем данные для ES

    es_data = get_genres_data()

    # 2. Загружаем данные в ES

    es_client = get_es_client()
    await es_write_data(es_client, es_data)

    # 3. Запрашиваем данные из ES по API

    url = test_settings.service_url + '/api/v1/genres'
    response = await make_get_request(url)

    # 4. Проверяем ответ
    assert response.status == 200
    assert len(response.body) == 5

@pytest.mark.asyncio
async def test_get_film_id(get_genres_data, get_es_client, es_write_data):
    # 1. Генерируем данные для ES

    es_data = get_genres_data()

    # 2. Загружаем данные в ES

    es_client = get_es_client()
    await es_write_data(es_client, es_data)

    # 3. Запрашиваем данные из ES по API

    # Get id of the first dictionary
    id = es_data[0]["id"]

    url = test_settings.service_url + '/api/v1/genres/' + id
    response = await make_get_request(url)

    # 4. Проверяем ответ
    assert response.status == 200
    # Поиск подстраки с ID
    # Documetation: https://stackoverflow.com/questions/3437059/does-python-have-a-string-contains-substring-method
    # if not -1 then string is found
    assert len(response.body) == 1
    assert str(response.text).find(id) != -1

