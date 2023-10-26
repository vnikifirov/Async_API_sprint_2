from pydantic_settings import BaseSettings, SettingsConfigDict

# Pydantic Dotenv (.env) support
# Documentation: https://fastapi.tiangolo.com/advanced/settings/#read-settings-from-env
class TestSettings(BaseSettings):
    es_host: str
    es_index: str
    es_id_field: str
    es_index_mapping: dict

    redis_host: str
    service_url: str

    model_config = SettingsConfigDict(env_file=".env")

    #class Config:
    #    env_file = ".env"