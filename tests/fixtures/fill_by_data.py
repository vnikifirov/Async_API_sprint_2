import datetime
import uuid
from typing import List

import aiohttp
import pytest

from elasticsearch import AsyncElasticsearch
from tests.settings import TestSettings as test_settings

@pytest.fixture
@pytest.mark.asyncio
async def get_persons_data():
    data = [{
        'id': str(uuid.uuid4()),
        'full_name': 'Bob Nicole',
        'created': datetime.datetime.now().isoformat(),
        'modified': datetime.datetime.now().isoformat(),
        'gender': 'Man'
    } for _ in range(5)]

    return data


@pytest.fixture
@pytest.mark.asyncio
async def get_genres_data():
    data = [{
        'id': str(uuid.uuid4()),
        'name': 'Action',
        'created': datetime.datetime.now().isoformat(),
        'modified': datetime.datetime.now().isoformat()
    } for _ in range(5)]

    return data

@pytest.fixture
@pytest.mark.asyncio
async def get_films_data():
    data = [{
        'id': str(uuid.uuid4()),
        'title': 'The Star',
        'genres': ['Action', 'Sci-Fi'],
        'description': 'New World',
        'rating': 8.5,
        'type': 'movie',
        'directors': ['Ben', 'Howard'],
        'actors': [
            {'id': '111', 'name': 'Ann'},
            {'id': '222', 'name': 'Bob'}
        ],
        'screenwriters': [
            {'id': '333', 'name': 'Ben'},
            {'id': '444', 'name': 'Howard'}
        ],
        'creation_date': datetime.datetime.now().isoformat()
    } for _ in range(60)]

    return data
