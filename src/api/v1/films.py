from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, FastAPI, Path, Query
from pydantic import BaseModel

from operator import attrgetter

from services.film import FilmService, get_film_service

import json

router = APIRouter()

class FilmResponse(BaseModel):
    pass 

@router.get('/films', 
            response_model=list, 
            summary="Вернуть все фильмы из базы", 
            response_description="Лист фильмов из базы")
async def film_all(sort: str = "id", 
                   page_size: Annotated[int, Query(description='Pagination page size', ge=1)] = 10,
                   page_number: Annotated[int, Query(description='Pagination page number', ge=1)] = 1, 
                   film_service: FilmService = Depends(get_film_service)) -> list:
    """
    Получить все фильмы из базы:
    - **id**: Каждый фильм имеет ID
    - **title**: Название фильма
    - **creation_date**: Дата когда фильм был снят
    - **description**: Описание фильма
    - **rating**: Рейтинг фильма
    - **type**: Тип фильма
    - **genres**: Жанр фильма
    - **actors**: Актеры фильма
    - **directors**: Режиссеры фильма
    - **screenwriters**: Сценаристы фильма
    """

    films= await film_service.get_all(page_size, page_number)
    if not films:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='film not found')

    sorted_list = list 
    if sort == "id":
        sorted_list = sorted(films, key=attrgetter('film.id'))

    if sort == "title":
        sorted_list = sorted(films, key=attrgetter('film.title'))

    if sort == "description":
        sorted_list = sorted(films, key=attrgetter('film.description'))

    if sort == "rating":
        sorted_list = sorted(films, key=attrgetter('film.rating'))

    if sort == "type":
        sorted_list = sorted(films, key=attrgetter('film.type'))

    json_string = json.dumps([ob.__dict__ for ob in sorted_list])

    return json_string

@router.get('/films/search', 
            response_model=list, 
            summary="Вернуть все фильмы из базы", 
            response_description="Лист фильмов из базы")
async def film_all(query = "", 
                   page_size: Annotated[int, Query(description='Pagination page size', ge=1)] = 10,
                   page_number: Annotated[int, Query(description='Pagination page number', ge=1)] = 1,
                   film_service: FilmService = Depends(get_film_service)) -> list:
    """
    Получить все фильмы из базы:

    - **id**: Каждый фильм имеет ID
    - **title**: Название фильма
    - **creation_date**: Дата когда фильм был снят
    - **description**: Описание фильма
    - **rating**: Рейтинг фильма
    - **type**: Тип фильма
    - **genres**: Жанр фильма
    - **actors**: Актеры фильма
    - **directors**: Режиссеры фильма
    - **screenwriters**: Сценаристы фильма
    """

    films= await film_service.get_all(page_size, page_number, query)
    if not films:
        # Если фильмы не найден, отдаём 404 статус
        # Желательно пользоваться уже определёнными HTTP-статусами, которые содержат enum  
                # Такой код будет более поддерживаемым
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='film not found')

    #queried_list = filter(lambda film: query in film.title or query in film.description, films)  
    json_string = json.dumps([ob.__dict__ for ob in films])

    return HttpResponse(json_string)

@router.get('/films/{film_id}', response_model=FilmResponse, summary="Найти фильм по ID и вернуть его", response_description="Фильм из базы")
async def film_details(film_id: str, film_service: FilmService = Depends(get_film_service)) -> FilmResponse:
    """
    Получить фильм из базы по ID:

    - **id**: Каждый фильм имеет ID
    - **title**: Название фильма
    - **creation_date**: Дата когда фильм был снят
    - **description**: Описание фильма
    - **rating**: Рейтинг фильма
    - **type**: Тип фильма
    - **genres**: Жанр фильма
    - **actors**: Актеры фильма
    - **directors**: Режиссеры фильма
    - **screenwriters**: Сценаристы фильма
    """
        
    film = await film_service.get_by_id(film_id)
    if not film:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='film not found')
    
    json_string = json.dumps(film.__dict__)

    return HttpResponse(json_string) 