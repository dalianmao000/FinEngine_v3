from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """应用配置管理"""

    # 阿里百炼
    dashscope_api_key: str
    dashscope_model: str = "qwen-plus"

    # 数据库
    database_url: str = "sqlite+aiosqlite:///./finagent.db"

    # Redis
    redis_url: str = "redis://localhost:6379/0"

    # ChromaDB
    chroma_data_path: str = "./data/chroma"

    # 服务
    api_port: int = 8000
    phoenix_port: int = 6001

    # 安全
    confidence_threshold: float = 0.7

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()