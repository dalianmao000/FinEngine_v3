"""Database initialization and utilities."""

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base

from app.config import settings

Base = declarative_base()
engine = None
async_session_maker = None


async def init_db():
    """Initialize the database."""
    global engine, async_session_maker
    engine = create_async_engine(settings.database_url, echo=False)
    async_session_maker = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def get_db():
    """Get a database session."""
    async with async_session_maker() as session:
        yield session