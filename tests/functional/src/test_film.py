import http
import pytest
import time

from elasticsearch import AsyncElasticsearch

from tests.settings import TestSettings as test_settings
from tests.conftest import *

@pytest.mark.asyncio
async def test_get_film_all(get_films_data, get_es_client, es_write_data):
    # 1. Генерируем данные для ES

    es_data = get_films_data()

    # 2. Загружаем данные в ES

    es_client = get_es_client()
    await es_write_data(es_client, es_data)

    # 3. Запрашиваем данные из ES по API

    url = test_settings.service_url + '/api/v1/films'
    response = await make_get_request(url)

    # 4. Проверяем ответ
    assert response.status == http.HTTPStatus.OK
    assert len(response.body) == 60

@pytest.mark.parametrize(
    'query_data, expected_answer',
    [
        (
                {'search': 'The Star'},
                {'status': http.HTTPStatus.OK, 'length': 50}
        ),
        (
                {'search': 'Mashed potato'},
                {'status': http.HTTPStatus.OK, 'length': 0}
        )
    ]
)
@pytest.mark.asyncio
async def test_film_search(query_data, get_data, get_es_client, es_write_data, expected_answer):
    # 1. Генерируем данные для ES

    es_data = get_data()

    # 2. Загружаем данные в ES

    es_client = get_es_client()
    await es_write_data(es_client, es_data)

    # 3. Запрашиваем данные из ES по API

    url = test_settings.service_url + '/api/v1/films/search'
    response = await make_get_request(url, query_data)

    # 4. Проверяем ответ
    assert response.status == http.HTTPStatus.OK
    assert len(response.body) == 50

    # Поиск подстраки
    # Documetation: https://stackoverflow.com/questions/3437059/does-python-have-a-string-contains-substring-method
    # if not -1 then string is found
    assert str(response.body).find("The Star") != -1


@pytest.mark.asyncio
async def test_get_film_id(get_data, get_es_client, es_write_data):
    # 1. Генерируем данные для ES

    es_data = get_data()

    # 2. Загружаем данные в ES

    es_client = get_es_client()
    await es_write_data(es_client, es_data)

    # 3. Запрашиваем данные из ES по API

    # Get id of the first dictionary
    id = es_data[0]["id"]

    url = test_settings.service_url + '/api/v1/films/' + id
    response = await make_get_request(url)

    # 4. Проверяем ответ
    assert response.status == http.HTTPStatus.OK
    # Поиск подстраки с ID
    # Documetation: https://stackoverflow.com/questions/3437059/does-python-have-a-string-contains-substring-method
    # if not -1 then string is found
    assert len(response.body) == 1
    assert str(response.text).find(id) != -1

@pytest.mark.asyncio
async def test_redis_get_film_id(get_data, get_es_client, es_write_data, get_redis_client, redis_get_by_id):
    # 1. Генерируем данные для ES

    es_data = get_data()

    # 2. Загружаем данные в ES

    es_client = get_es_client()
    await es_write_data(es_client, es_data)

    # 3. Запрашиваем данные по API

    # Get id of the first dictionary
    id = es_data[0]["id"]

    url = test_settings.service_url + '/api/v1/films/' + id

     # 4. Замеряем время
    time_start = time.time()
    response = await make_get_request(url)
    time_end = time.time()

    time_no_cache = time_end - time_start

    # Замеряем время обращения к Redis оно должно быть меньше чем если нужно обрщаться к базе 
    time_cache_start = time.time()
    response = await make_get_request(url)
    time_cache_end = time.time()

    time_cache = time_cache_end - time_cache_start

    redis_client = get_redis_client()
    redis_data = await redis_get_by_id(redis_client, id)

    # 5. Проверяем ответ    
    assert response.status == http.HTTPStatus.OK
    # Время с кашированием Redis меньше чем обращение к базе так как качи всегда быстрее
    assert time_cache < time_no_cache
    assert len(redis_data) == 1
    assert str(redis_data).find(id) != -1