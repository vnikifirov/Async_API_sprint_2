from http import HTTPStatus

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from django.core.paginator import Paginator
from django.http import JsonResponse
from django.core import serializers

from operator import attrgetter

from services.person import PersonService, get_person_service
from services.genre import GenreService, get_genre_service

router = APIRouter()

class GenreResponse(BaseModel):
    pass 

# Внедряем GenreService с помощью Depends(get_film_service)
@router.get('/genres', response_model=list, summary="Вернуть все жанры из базы", response_description="Лист жанры из базы")
async def film_all(genre_service: GenreService = Depends(get_genre_service)) -> list:
    """
    Получить все фильмы из базы:

    - **id**: Каждый жанр имеет ID
    - **name**: Название жанра

    """

    genres = await genre_service.get_all_genres()
    if not genres:
        # Если фильмы не найден, отдаём 404 статус
        # Желательно пользоваться уже определёнными HTTP-статусами, которые содержат enum  
                # Такой код будет более поддерживаемым
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='genre not found')

    #if sort == "genres":
    #    sorted_list = sorted(films, )

    # Не Перекладываем данные из models.Film в Film, просто отдаем колекцию данных
    # Обратите внимание, что у модели бизнес-логики есть поле description 
        # Которое отсутствует в модели ответа API. 
        # Если бы использовалась общая модель для бизнес-логики и формирования ответов API
        # вы бы предоставляли клиентам данные, которые им не нужны 
        # и, возможно, данные, которые опасно возвращать
    return genres

@router.get('/genres/{genre_id}', response_model=GenreResponse, summary="Вернуть жанр по ID из базы")
async def get_genre(genre_id: str, genre_service: GenreService = Depends(get_person_service)) -> GenreResponse:

    """
    Получить жанр по ID: 

    - **id**: Каждый жанр имеет ID
    - **name**: Каждый жанр имеет имя
     
    """

    genre = await genre_service.get_by_id(genre_id)
    if not genre:
        # Если Person не найден, отдаём 404 статус
        # Желательно пользоваться уже определёнными HTTP-статусами, которые содержат enum  
                # Такой код будет более поддерживаемым
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='genre not found')

    # Перекладываем данные из models.Person в Person
    # Обратите внимание, что у модели бизнес-логики есть поле description 
        # Которое отсутствует в модели ответа API. 
        # Если бы использовалась общая модель для бизнес-логики и формирования ответов API
        # вы бы предоставляли клиентам данные, которые им не нужны 
        # и, возможно, данные, которые опасно возвращать
    return GenreResponse(genre) 