"""Application settings using pydantic with environment variables."""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # LLM Configuration
    dashscope_api_key: str = ""
    llm_model: str = "qwen-plus"
    llm_base_url: str = "https://dashscope.aliyuncs.com/compatible-mode/v1"

    # Neo4j Configuration
    neo4j_uri: str = "bolt://localhost:7687"
    neo4j_user: str = "neo4j"
    neo4j_password: str = ""

    # ChromaDB Configuration
    chroma_db_path: str = "./data/chroma_db"

    # Database Configuration
    database_url: str = "sqlite+aiosqlite:///./data/risk_investigator.db"

    # Application Configuration
    app_host: str = "0.0.0.0"
    app_port: int = 8001
    log_level: str = "INFO"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()