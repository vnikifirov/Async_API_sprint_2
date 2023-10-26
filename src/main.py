import logging

import uvicorn
from elasticsearch import AsyncElasticsearch
from fastapi import FastAPI
from fastapi.responses import ORJSONResponse
from redis.asyncio import Redis

from api.v1 import films, persons
from core import config
from core.logger import LOGGING
from db.implementation import search_engine
from db.implementation import cache

from contextlib import asynccontextmanager

from core.config import Settings

settings = Settings()

@asynccontextmanager
async def lifespan(app: FastAPI):
    cache.redis = Redis(host=settings.redis_host, port=settings.redis_port)
    search_engine.es = AsyncElasticsearch(hosts=[f'{settings.elastic_host}:{settings.elastic_port}'])
    
    yield
    
    await cache.redis.close()
    await search_engine.es.close()

app = FastAPI(
    title=settings.project_name,
    docs_url='/api/openapi',
    openapi_url='/api/openapi.json',
    default_response_class=ORJSONResponse,
    lifespan=lifespan
)

#@app.on_event('startup')
#async def startup():
    # Подключаемся к базам при старте сервера
    # Подключиться можем при работающем event-loop
    # Поэтому логика подключения происходит в асинхронной функции
#    redis.redis = Redis(host=config.REDIS_HOST, port=config.REDIS_PORT)
#    elastic.es = AsyncElasticsearch(hosts=[f'{config.ELASTIC_HOST}:{config.ELASTIC_PORT}'])


#@app.on_event('shutdown')
#async def shutdown():
#    # Отключаемся от баз при выключении сервера
#    await redis.redis.close()
#    await elastic.es.close()

# Подключаем роутер к серверу, указав префикс /v1/films
# Теги указываем для удобства навигации по документации
app.include_router(films.router, prefix='/api/v1/films', tags=['films-api'])
app.include_router(persons.router, prefix='/api/v1/persons', tags=['persons-api'])

if __name__ == '__main__':
    uvicorn.run(
        'main:app',
        host='0.0.0.0',
        port=8000,
        log_config=LOGGING,
        log_level=logging.DEBUG,
    ) 