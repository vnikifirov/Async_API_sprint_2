import os
from logging import config as logging_config

from pydantic import BaseSettings
from pydantic_settings import BaseSettings, SettingsConfigDict

from core.logger import LOGGING

# Применяем настройки логирования
logging_config.dictConfig(LOGGING)

# Pydantic Dotenv (.env) support
# Documentation: https://fastapi.tiangolo.com/advanced/settings/#read-settings-from-env
class Settings(BaseSettings):
    project_name: str

     # Настройки Redis
    redis_host: str
    redis_port: int

     # Настройки Elasticsearch
    elastic_host: str
    elastic_port: int

    model_config = SettingsConfigDict(env_file=".env")

# Корень проекта
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
 