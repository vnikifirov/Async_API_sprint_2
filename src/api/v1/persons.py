from http import HTTPStatus
from api.v1.films import FilmResponse

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from services.film import FilmService

from services.person import PersonService, get_person_service
from services.film import FilmService, get_film_service

from django.core.paginator import Paginator
from django.http import JsonResponse
from django.core import serializers

from operator import attrgetter

router = APIRouter()

class PersonResponse(BaseModel):
    pass 

class PersonRequest(BaseModel):
    pass 

@router.get('/persons', response_model=list, summary="Вернуть всех персон из базы")
async def person_all(sort: str = "id", pageSize = 5, pageNumber = 1, person_service: PersonService = Depends(get_person_service)) -> list:
    """
    Получить все персоны из базы:

    - **id**: Каждая персона имеет ID
    - **full_name**: Полное имя прерсоны ФИО
    - **created*: Дата когда прерсона была добавлена в базу
    - **modified**: Дата когда прерсона была модифицирована в базе
    - **gender* Пол персоны муж или жен

    """

    persons= await person_service.get_all()
    if not persons:
        # Если фильмы не найден, отдаём 404 статус
        # Желательно пользоваться уже определёнными HTTP-статусами, которые содержат enum  
                # Такой код будет более поддерживаемым
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='persons not found')

    sorted_list = list 
    if sort == "id":
        sorted_list = sorted(persons, key=attrgetter('person.id'))

    if sort == "full_name":
        sorted_list = sorted(persons, key=attrgetter('person.full_name'))

    if sort == "gender":
        sorted_list = sorted(persons, key=attrgetter('person.gender'))

    paginator = Paginator(sorted_list, pageSize)
    page = paginator.page(pageNumber)

    # Не Перекладываем данные из models.Person в Person, просто отдаем колекцию данных
    # Обратите внимание, что у модели бизнес-логики есть поле description 
        # Которое отсутствует в модели ответа API. 
        # Если бы использовалась общая модель для бизнес-логики и формирования ответов API
        # вы бы предоставляли клиентам данные, которые им не нужны 
        # и, возможно, данные, которые опасно возвращать
    data_serialized = serializers.serialize("json", page.object_list)

    return JsonResponse(data_serialized, safe=False)

@router.get('/persons/search', response_model=list, summary="Вернуть всех персон из базы и используя запрос / query")
async def person_all(query: str = "", pageSize = 5, pageNumber = 1, person_service: PersonService = Depends(get_person_service)) -> list:
    """
    Получить все персоны из базы:

    - **id**: Каждая персона имеет ID
    - **full_name**: Полное имя прерсоны ФИО
    - **created*: Дата когда прерсона была добавлена в базу
    - **modified**: Дата когда прерсона была модифицирована в базе
    - **gender* Пол персоны муж или жен

    """

    persons= await person_service.get_all()
    if not persons:
        # Если фильмы не найден, отдаём 404 статус
        # Желательно пользоваться уже определёнными HTTP-статусами, которые содержат enum  
                # Такой код будет более поддерживаемым
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='persons not found')

    # Запрос и фильтрацию можно выполнить на стороне БД
    queried_list = filter(lambda person: query in person.full_name, persons) 

    paginator = Paginator(queried_list, pageSize)
    page = paginator.page(pageNumber)   

    # Не Перекладываем данные из models.Person в Person, просто отдаем колекцию данных
    # Обратите внимание, что у модели бизнес-логики есть поле description 
        # Которое отсутствует в модели ответа API. 
        # Если бы использовалась общая модель для бизнес-логики и формирования ответов API
        # вы бы предоставляли клиентам данные, которые им не нужны 
        # и, возможно, данные, которые опасно возвращать
    data_serialized = serializers.serialize("json", page.object_list)

    return JsonResponse(data_serialized, safe=False)

# Внедряем FilmService с помощью Depends(get_film_service)
@router.get('/persons/{person_id}', response_model=PersonService, summary="Вернуть персону по ID из базы")
async def person_details(person_id: str, person_service: PersonService = Depends(get_person_service)) -> PersonService:
    """
    Получить персону по ID: 

    - **id**: Каждая персона имеет ID
    - **full_name**: Полное имя прерсоны ФИО
    - **created*: Дата когда прерсона была добавлена в базу
    - **modified**: Дата когда прерсона была модифицирована в базе
    - **gender* Пол персоны муж или жен
    
    """

    person = await person_service.get_by_id(person_id)
    if not person:
        # Если Person не найден, отдаём 404 статус
        # Желательно пользоваться уже определёнными HTTP-статусами, которые содержат enum  
                # Такой код будет более поддерживаемым
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='person not found')

    # Перекладываем данные из models.Person в Person
    # Обратите внимание, что у модели бизнес-логики есть поле description 
        # Которое отсутствует в модели ответа API. 
        # Если бы использовалась общая модель для бизнес-логики и формирования ответов API
        # вы бы предоставляли клиентам данные, которые им не нужны 
        # и, возможно, данные, которые опасно возвращать
    return PersonResponse(person) 

@router.get('/persons/{person_id}/film', response_model=FilmResponse, summary="Вернуть фильмы по персоне ID из базы")
async def film_by_person_id(person_id: str, pageSize = 5, pageNumber = 1, film_service: FilmService = Depends(get_film_service)) -> list:
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

    films = await film_service.get_all()
    if not films:
        # Если Person не найден, отдаём 404 статус
        # Желательно пользоваться уже определёнными HTTP-статусами, которые содержат enum  
                # Такой код будет более поддерживаемым
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='No films in database')

    films_by_person_id = list

    # На заметку НИКОГДА не писать BLL логику в контролере и ВСЕГДА делать конретный запрос к БД чтобы не писать лишнюю логику. Ушел в магазин =) 
    for film in films:
        found = False
        for actor in film.actors:
            if actor.id == person_id:
                found = True

        if found != True:
            for director in film.directors:
                if director.id == person_id:
                    found = True

        if found != True:
            for screenwriter in film.screenwriters:
                if screenwriter.id == person_id:
                    found = True

        if found == True:
            film_by_person_id.append(film)                
    # На заметку НИКОГДА не писать BLL логику в контролере и ВСЕГДА делать конретный запрос к БД чтобы не писать лишнюю логику. Ушел в магазин =) 

    # Перекладываем данные из models.Person в Person
    # Обратите внимание, что у модели бизнес-логики есть поле description 
        # Которое отсутствует в модели ответа API. 
        # Если бы использовалась общая модель для бизнес-логики и формирования ответов API
        # вы бы предоставляли клиентам данные, которые им не нужны 
        # и, возможно, данные, которые опасно возвращать
    return films_by_person_id

@router.post('/persons/create}', response_model=PersonRequest, summary="Добавить новую персону в базу")
async def person_details(person: PersonRequest, person_service: PersonService = Depends(get_person_service)) -> PersonRequest:
    """
    Создать / Добавить новую персону: 

    - **id**: Каждая персона имеет ID
    - **full_name**: Полное имя прерсоны ФИО
    - **created*: Дата когда прерсона была добавлена в базу
    - **modified**: Дата когда прерсона была модифицирована в базе
    - **gender* Пол персоны муж или жен
     
    """

    person = await person_service.add_person(person)
    if not person:
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail='cannnot add person')

    return PersonResponse(person)  