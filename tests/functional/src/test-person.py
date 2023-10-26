import aiohttp
import pytest

from elasticsearch import AsyncElasticsearch

from tests.settings import TestSettings as test_settings
from tests.conftest import es_write_data, get_es_client, make_get_request, get_films_data

@pytest.mark.asyncio
async def test_get_persons_all(get_persons_data, get_es_client, es_write_data):
    # 1. Генерируем данные для ES

    es_data = get_persons_data()

    # 2. Загружаем данные в ES

    es_client = get_es_client()
    await es_write_data(es_client, es_data)

    # 3. Запрашиваем данные из ES по API

    url = test_settings.service_url + '/api/v1/persons'
    response = await make_get_request(url)

    # 4. Проверяем ответ
    assert response.status == 200
    assert len(response.body) == 5

@pytest.mark.parametrize(
    'query_data, expected_answer',
    [
        (
                {'search': 'Nicole'},
                {'status': 200, 'length': 5}
        ),
        (
                {'search': 'Mashed potato'},
                {'status': 200, 'length': 0}
        )
    ]
)
@pytest.mark.asyncio
async def test_person_search(query_data, get_persons_data, get_es_client, es_write_data, expected_answer):
    # 1. Генерируем данные для ES

    es_data = get_persons_data()

    # 2. Загружаем данные в ES

    es_client = get_es_client()
    await es_write_data(es_client, es_data)

    # 3. Запрашиваем данные из ES по API

    url = test_settings.service_url + '/api/v1/persons/search'
    response = await make_get_request(url, query_data)

    # 4. Проверяем ответ
    assert response.status == 200
    assert len(response.body) == 50

    # Поиск подстраки
    # Documetation: https://stackoverflow.com/questions/3437059/does-python-have-a-string-contains-substring-method
    # if not -1 then string is found
    assert str(response.body).find("Nicole") != -1


@pytest.mark.asyncio
async def test_get_person_by_id(get_persons_data, get_es_client, es_write_data):
    # 1. Генерируем данные для ES

    es_data = get_persons_data()

    # 2. Загружаем данные в ES

    es_client = get_es_client()
    await es_write_data(es_client, es_data)

    # 3. Запрашиваем данные из ES по API

    # Get id of the first dictionary
    id = es_data[0]["id"]

    url = test_settings.service_url + '/api/v1/persons/' + id
    response = await make_get_request(url)

    # 4. Проверяем ответ
    assert response.status == 200
    # Поиск подстраки с ID
    # Documetation: https://stackoverflow.com/questions/3437059/does-python-have-a-string-contains-substring-method
    # if not -1 then string is found
    assert len(response.body) == 1
    assert str(response.text).find(id) != -1

@pytest.mark.asyncio
async def test_get_film_by_person_id(get_persons_data, get_films_data, get_es_client, es_write_data):
    # 1. Генерируем данные для ES

    # Фильмы содержат ID персон и поэтому мы можем в теории найти фильмы где перснона была снята.
    es_persons_data = get_persons_data()
    es_films_data = get_films_data()

    # 2. Загружаем данные в ES

    es_client = get_es_client()
    await es_write_data(es_client, es_persons_data)

    await es_write_data(es_client, es_films_data)

    # 3. Запрашиваем данные из ES по API

    # Получить ИД первого человека
    id = es_persons_data[0]["id"]

    url = test_settings.service_url + '/api/v1/persons/' + id + '/film'
    response = await make_get_request(url)

    # 4. Проверяем ответ
    assert response.status == 200
    # Поиск подстраки с ID
    # Documetation: https://stackoverflow.com/questions/3437059/does-python-have-a-string-contains-substring-method
    # if -1 then string is not found
    # В нашем случаии фильмов нету так как данные не привязаны друг к другу по ID
    assert len(response.body) == 0
    assert str(response.text).find(id) == -1

