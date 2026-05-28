from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/finagent_ops"
    redis_url: str = "redis://localhost:6379/0"
    dashscope_api_key: str = ""
    otel_exporter_otlp_endpoint: str = "http://localhost:4317"
    otel_service_name: str = "finagent-ops"
    host: str = "0.0.0.0"
    port: int = 8002

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

@lru_cache()
def get_settings() -> Settings:
    return Settings()