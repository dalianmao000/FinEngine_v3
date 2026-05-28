from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, String, Text, Boolean, Integer, DateTime, JSON
from datetime import datetime

Base = declarative_base()


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(String, primary_key=True)
    trace_id = Column(String, nullable=False, index=True)
    user_id = Column(String, index=True)
    scenario = Column(String)
    input_text = Column(Text)
    output_text = Column(Text)
    blocked = Column(Boolean, default=False)
    block_reason = Column(Text)
    human_intervention = Column(Boolean, default=False)
    nodes_json = Column(JSON)
    safety_events_json = Column(JSON)
    total_duration_ms = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)


class KnowledgeDoc(Base):
    __tablename__ = "knowledge_base"

    id = Column(String, primary_key=True)
    content = Column(Text, nullable=False)
    category = Column(String, index=True)
    title = Column(String)
    section = Column(String)
    update_time = Column(DateTime)
    expiry_days = Column(Integer, default=90)
    status = Column(String, default="active")
    metadata_json = Column(JSON)


class UserMemory(Base):
    __tablename__ = "user_memories"

    id = Column(String, primary_key=True)
    user_id = Column(String, nullable=False, index=True)
    memory_type = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    session_id = Column(String)
    expires_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)


async def init_db(database_url: str):
    engine = create_async_engine(database_url, echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    return engine


async def get_session(engine):
    async_session = async_sessionmaker(engine, class_=AsyncSession)
    async with async_session() as session:
        yield session
