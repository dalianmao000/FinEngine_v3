import pytest
from app.config import Settings

def test_settings_loads_from_env(monkeypatch):
    monkeypatch.setenv("DATABASE_URL", "postgresql+asyncpg://test:test@localhost:5432/test")
    monkeypatch.setenv("REDIS_URL", "redis://localhost:6379/0")
    monkeypatch.setenv("DASHSCOPE_API_KEY", "sk-test")

    settings = Settings()
    assert settings.database_url == "postgresql+asyncpg://test:test@localhost:5432/test"
    assert settings.redis_url == "redis://localhost:6379/0"
    assert settings.dashscope_api_key == "sk-test"