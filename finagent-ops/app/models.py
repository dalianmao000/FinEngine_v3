import uuid
from datetime import datetime
from sqlalchemy import Column, String, Boolean, Integer, DateTime, JSON, Float
from sqlalchemy.dialects.postgresql import UUID

from app.database import Base

class ModelConfig(Base):
    __tablename__ = "model_configs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    provider = Column(String, nullable=False)  # dashscope, openai
    model_id = Column(String, nullable=False)
    endpoint = Column(String)
    config = Column(JSON, default={})
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Policy(Base):
    __tablename__ = "policies"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    description = Column(String)
    rule = Column(JSON, nullable=False)
    priority = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class Tool(Base):
    __tablename__ = "tools"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False, unique=True)
    description = Column(String)
    endpoint = Column(String)
    rbac_roles = Column(JSON, default=[])
    timeout_seconds = Column(Integer, default=30)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class EvalResult(Base):
    __tablename__ = "eval_results"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    dataset_id = Column(UUID(as_uuid=True))
    model_id = Column(String, nullable=False)
    prompt_version = Column(String)
    scores = Column(JSON, default={})
    tokens_used = Column(Integer, default=0)
    evaluated_at = Column(DateTime, default=datetime.utcnow)

class TraceLog(Base):
    __tablename__ = "trace_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    trace_id = Column(String, nullable=False, index=True)
    span_type = Column(String, nullable=False)
    business_line = Column(String)
    model_name = Column(String)
    prompt_version = Column(String)
    input_tokens = Column(Integer, default=0)
    output_tokens = Column(Integer, default=0)
    duration_ms = Column(Integer, default=0)
    trace_metadata = Column(JSON, default={})
    created_at = Column(DateTime, default=datetime.utcnow)

class BusinessLineCost(Base):
    __tablename__ = "business_line_costs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    business_line = Column(String, nullable=False, index=True)
    date = Column(String, nullable=False, index=True)
    model_name = Column(String)
    prompt_version = Column(String)
    input_tokens = Column(Integer, default=0)
    output_tokens = Column(Integer, default=0)
    cost_usd = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)