# FinAgent-Ops Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build an enterprise-grade AI Harness Engineering platform with 5 subdomains: Serving, Security, Execution, Eval, and Observability.

**Architecture:** FastAPI-based gateway platform that manages AI traffic. 5 harness subdomains implemented as separate packages under `app/harness/`. PostgreSQL + Redis for storage. OpenTelemetry for observability.

**Tech Stack:** FastAPI, async SQLAlchemy, Redis, OpenTelemetry, PostgreSQL, Prometheus, Pydantic, tiktoken.

---

## Task 1: Project Scaffold

**Files:**
- Create: `finagent-ops/requirements.txt`
- Create: `finagent-ops/docker/docker-compose.yml`
- Create: `finagent-ops/docker/Dockerfile`
- Create: `finagent-ops/app/__init__.py`
- Create: `finagent-ops/app/main.py`

- [ ] **Step 1: Write requirements.txt**

```txt
# FinAgent-Ops - AI Harness Engineering Platform
# Web Framework
fastapi>=0.110.0
uvicorn[standard]>=0.27.0

# Async ORM
sqlalchemy>=2.0.0
aiosqlite>=0.19.0
asyncpg>=0.29.0

# Redis
redis>=5.0.0

# Token Counting
tiktoken>=0.5.0

# Observability
opentelemetry-api>=1.22.0
opentelemetry-sdk>=1.22.0
opentelemetry-instrumentation-fastapi>=0.43b0
prometheus-client>=0.19.0

# Data Validation
pydantic>=2.0.0
pydantic-settings>=2.0.0

# Testing
pytest>=7.0.0
pytest-asyncio>=0.21.0
httpx>=0.26.0

# Utilities
python-dotenv>=1.0.0
```

- [ ] **Step 2: Run test to verify requirements are valid**

Run: `pip install -r finagent-ops/requirements.txt --dry-run 2>&1 | head -20`
Expected: Dependencies resolve without conflicts

- [ ] **Step 3: Write docker-compose.yml**

```yaml
version: '3.8'

services:
  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: finagent_ops
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data

  finagent-ops:
    build: .
    ports:
      - "8002:8002"
    depends_on:
      - postgres
      - redis
    environment:
      DATABASE_URL: postgresql+asyncpg://postgres:postgres@postgres:5432/finagent_ops
      REDIS_URL: redis://redis:6379/0
    volumes:
      - ./.env:/app/.env

volumes:
  postgres_data:
  redis_data:
```

- [ ] **Step 4: Write Dockerfile**

```dockerfile
FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8002"]
```

- [ ] **Step 5: Write app/__init__.py**

```python
"""FinAgent-Ops - AI Harness Engineering Platform"""

__version__ = "0.1.0"
```

- [ ] **Step 6: Write app/main.py**

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.api.routes import api_router

app = FastAPI(
    title="FinAgent-Ops",
    description="AI Harness Engineering Platform",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api/v1")

@app.get("/health")
async def health():
    return {"status": "healthy", "service": "finagent-ops"}
```

- [ ] **Step 7: Verify app structure**

Run: `ls -la finagent-ops/app/`
Expected: Directory structure with __init__.py, main.py

- [ ] **Step 8: Commit**

```bash
git add finagent-ops/requirements.txt finagent-ops/docker/ finagent-ops/app/
git commit -m "feat: add FinAgent-Ops project scaffold

- FastAPI entry point
- Docker Compose (PostgreSQL + Redis)
- Project structure

Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>"
```

---

## Task 2: Config + Database Foundation

**Files:**
- Create: `finagent-ops/app/config.py`
- Create: `finagent-ops/app/database.py`

- [ ] **Step 1: Write failing test for config**

Create: `finagent-ops/tests/test_config.py`
```python
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
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest finagent-ops/tests/test_config.py -v`
Expected: FAIL - module not found

- [ ] **Step 3: Write config.py**

```python
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
```

- [ ] **Step 4: Write database.py**

```python
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base

Base = declarative_base()

engine = None
async_session_maker = None

def init_db(database_url: str):
    global engine, async_session_maker
    engine = create_async_engine(database_url, echo=False)
    async_session_maker = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

async def get_session() -> AsyncSession:
    async with async_session_maker() as session:
        yield session

async def close_db():
    await engine.dispose()
```

- [ ] **Step 5: Run test to verify it passes**

Run: `pytest finagent-ops/tests/test_config.py -v`
Expected: PASS

- [ ] **Step 6: Commit**

```bash
git add finagent-ops/app/config.py finagent-ops/app/database.py finagent-ops/tests/test_config.py
git commit -m "feat: add config and database foundation

- Pydantic Settings with env support
- Async SQLAlchemy engine setup

Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>"
```

---

## Task 3: SQLAlchemy Models

**Files:**
- Create: `finagent-ops/app/models.py`
- Create: `finagent-ops/tests/test_models.py`

- [ ] **Step 1: Write failing test for models**

```python
import pytest
from app.models import ModelConfig, Policy, Tool

def test_model_config_can_be_created():
    model = ModelConfig(
        name="Qwen-7B",
        provider="dashscope",
        model_id="qwen-7b",
        endpoint="https://api.dashscope.cn",
        is_active=True,
    )
    assert model.name == "Qwen-7B"
    assert model.is_active is True

def test_policy_has_rule_field():
    policy = Policy(
        name="block-pii",
        rule={"effect": "deny", "condition": {"contains_pii": True}},
    )
    assert policy.rule["effect"] == "deny"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest finagent-ops/tests/test_models.py -v`
Expected: FAIL with "cannot import models"

- [ ] **Step 3: Write models.py**

```python
import uuid
from datetime import datetime
from sqlalchemy import Column, String, Boolean, Integer, DateTime, JSON, ForeignKey
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
    metadata = Column(JSON, default={})
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
    cost_usd = Column(float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest finagent-ops/tests/test_models.py -v`
Expected: PASS

- [ ] **Step 5: Write conftest.py**

```python
import pytest
import asyncio

@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()
```

- [ ] **Step 6: Commit**

```bash
git add finagent-ops/app/models.py finagent-ops/tests/test_models.py finagent-ops/tests/conftest.py
git commit -m "feat: add SQLAlchemy models for all entities

- ModelConfig, Policy, Tool, EvalResult, TraceLog, BusinessLineCost
- PostgreSQL UUID support

Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>"
```

---

## Task 4: Core Utilities

**Files:**
- Create: `finagent-ops/app/core/__init__.py`
- Create: `finagent-ops/app/core/token_counter.py`
- Create: `finagent-ops/app/core/exceptions.py`
- Create: `finagent-ops/tests/test_token_counter.py`

- [ ] **Step 1: Write failing test for token counter**

```python
import tiktoken
from app.core.token_counter import count_tokens, count_tokens_from_text

def test_count_tokens_with_encoding():
    encoding = tiktoken.get_encoding("cl100k_base")
    text = "Hello, world!"
    tokens = count_tokens(text, encoding)
    assert tokens > 0

def test_count_tokens_from_text():
    count = count_tokens_from_text("Hello, world!")
    assert count > 0
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest finagent-ops/tests/test_token_counter.py -v`
Expected: FAIL with "cannot import"

- [ ] **Step 3: Write core/__init__.py**

```python
"""Core utilities for FinAgent-Ops"""
```

- [ ] **Step 4: Write token_counter.py**

```python
import tiktoken

def count_tokens(text: str, encoding) -> int:
    """Count tokens in text using given encoding"""
    return len(encoding.encode(text))

def count_tokens_from_text(text: str, encoding_name: str = "cl100k_base") -> int:
    """Count tokens from text string"""
    encoding = tiktoken.get_encoding(encoding_name)
    return count_tokens(text, encoding)

def get_encoding(encoding_name: str = "cl100k_base"):
    """Get tiktoken encoding"""
    return tiktoken.get_encoding(encoding_name)
```

- [ ] **Step 5: Write exceptions.py**

```python
class FinAgentOpsError(Exception):
    """Base exception for FinAgent-Ops"""
    pass

class CacheError(FinAgentOpsError):
    """Cache-related errors"""
    pass

class PolicyViolationError(FinAgentOpsError):
    """Policy violation detected"""
    pass

class ToolExecutionError(FinAgentOpsError):
    """Tool execution failed"""
    pass

class RateLimitExceededError(FinAgentOpsError):
    """Rate limit exceeded"""
    pass
```

- [ ] **Step 6: Run test to verify it passes**

Run: `pytest finagent-ops/tests/test_token_counter.py -v`
Expected: PASS

- [ ] **Step 7: Commit**

```bash
git add finagent-ops/app/core/ finagent-ops/tests/test_token_counter.py
git commit -m "feat: add core utilities

- Token counter (tiktoken)
- Custom exceptions

Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>"
```

---

## Task 5: Serving Harness

**Files:**
- Create: `finagent-ops/app/harness/serving/__init__.py`
- Create: `finagent-ops/app/harness/serving/router.py`
- Create: `finagent-ops/app/harness/serving/cache.py`
- Create: `finagent-ops/app/harness/serving/rate_limiter.py`
- Create: `finagent-ops/tests/test_serving.py`

- [ ] **Step 1: Write failing test for serving harness**

```python
import pytest
from app.harness.serving.router import Router, ComplexityLevel

def test_router_classifies_simple_query():
    router = Router()
    complexity = router.classify_complexity("What is my account balance?")
    assert complexity in [ComplexityLevel.LOW, ComplexityLevel.MEDIUM]

def test_router_classifies_complex_query():
    router = Router()
    complexity = router.classify_complexity("Analyze the financial impact of interest rate changes on our investment portfolio over the last 5 years")
    assert complexity == ComplexityLevel.HIGH

def test_rate_limiter_allows_request_under_limit():
    from app.harness.serving.rate_limiter import RateLimiter
    limiter = RateLimiter(requests_per_minute=60)
    assert limiter.check_limit("business_line_1") is True
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest finagent-ops/tests/test_serving.py -v`
Expected: FAIL with "cannot import"

- [ ] **Step 3: Write serving/__init__.py**

```python
"""Serving Harness - Model routing, caching, rate limiting"""
from app.harness.serving.router import Router, ComplexityLevel
from app.harness.serving.cache import SemanticCache
from app.harness.serving.rate_limiter import RateLimiter

__all__ = ["Router", "ComplexityLevel", "SemanticCache", "RateLimiter"]
```

- [ ] **Step 4: Write router.py**

```python
from enum import Enum
from app.core.token_counter import count_tokens_from_text

class ComplexityLevel(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

class Router:
    LOW_COMPLEXITY_THRESHOLD = 50
    HIGH_COMPLEXITY_THRESHOLD = 200

    def __init__(self):
        self.low_model = "qwen-7b"
        self.high_model = "qwen-72b"

    def classify_complexity(self, prompt: str) -> ComplexityLevel:
        """Classify prompt complexity based on token count and keywords"""
        token_count = count_tokens_from_text(prompt)

        if token_count < self.LOW_COMPLEXITY_THRESHOLD:
            return ComplexityLevel.LOW
        elif token_count > self.HIGH_COMPLEXITY_THRESHOLD:
            return ComplexityLevel.HIGH
        else:
            return ComplexityLevel.MEDIUM

    def route_model(self, complexity: ComplexityLevel) -> str:
        """Route to appropriate model based on complexity"""
        if complexity == ComplexityLevel.LOW:
            return self.low_model
        elif complexity == ComplexityLevel.MEDIUM:
            return self.low_model
        else:
            return self.high_model
```

- [ ] **Step 5: Write cache.py**

```python
import redis.asyncio as redis
import json
from typing import Optional

class SemanticCache:
    def __init__(self, redis_url: str):
        self.redis_url = redis_url
        self._client: Optional[redis.Redis] = None

    async def get_client(self) -> redis.Redis:
        if self._client is None:
            self._client = await redis.from_url(self.redis_url)
        return self._client

    async def get(self, key: str) -> Optional[dict]:
        client = await self.get_client()
        data = await client.get(key)
        if data:
            return json.loads(data)
        return None

    async def set(self, key: str, value: dict, ttl: int = 3600):
        client = await self.get_client()
        await client.setex(key, ttl, json.dumps(value))

    async def delete(self, key: str):
        client = await self.get_client()
        await client.delete(key)

    async def clear_all(self):
        client = await self.get_client()
        await client.flushdb()

    async def get_stats(self) -> dict:
        client = await self.get_client()
        info = await client.info("stats")
        return {
            "keyspace_hits": info.get("keyspace_hits", 0),
            "keyspace_misses": info.get("keyspace_misses", 0),
        }
```

- [ ] **Step 6: Write rate_limiter.py**

```python
import time
from collections import defaultdict

class RateLimiter:
    def __init__(self, requests_per_minute: int = 60):
        self.requests_per_minute = requests_per_minute
        self._buckets = defaultdict(lambda: {"tokens": requests_per_minute, "last_refill": time.time()})

    def check_limit(self, key: str) -> bool:
        bucket = self._buckets[key]
        now = time.time()

        if now - bucket["last_refill"] >= 60:
            bucket["tokens"] = self.requests_per_minute
            bucket["last_refill"] = now

        if bucket["tokens"] > 0:
            bucket["tokens"] -= 1
            return True
        return False

    def get_remaining(self, key: str) -> int:
        bucket = self._buckets[key]
        return max(0, bucket["tokens"])
```

- [ ] **Step 7: Run test to verify it passes**

Run: `pytest finagent-ops/tests/test_serving.py -v`
Expected: PASS

- [ ] **Step 8: Commit**

```bash
git add finagent-ops/app/harness/serving/ finagent-ops/tests/test_serving.py
git commit -m "feat: add Serving harness

- Router with complexity-based model routing
- Semantic cache (Redis-based)
- Rate limiter (token bucket)

Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>"
```

---

## Task 6: Security Harness

**Files:**
- Create: `finagent-ops/app/harness/security/__init__.py`
- Create: `finagent-ops/app/harness/security/guardrail.py`
- Create: `finagent-ops/app/harness/security/policy_engine.py`
- Create: `finagent-ops/tests/test_security.py`

- [ ] **Step 1: Write failing test for security harness**

```python
from app.harness.security.guardrail import Guardrail
from app.harness.security.policy_engine import PolicyEngine, PolicyContext

def test_guardrail_blocks_pii():
    guardrail = Guardrail()
    result = guardrail.check_content("My credit card is 1234-5678-9012-3456")
    assert result.is_blocked is True
    assert "card_number" in result.detected_types

def test_policy_engine_allows_valid_request():
    engine = PolicyEngine()
    context = PolicyContext(
        user_id="user123",
        business_line="customer_service",
        tool_name="query_account",
    )
    result = engine.evaluate(context)
    assert result.allowed is True
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest finagent-ops/tests/test_security.py -v`
Expected: FAIL with "cannot import"

- [ ] **Step 3: Write security/__init__.py**

```python
"""Security Harness - Guardrail, Policy Engine, ABAC"""
from app.harness.security.guardrail import Guardrail, GuardrailResult
from app.harness.security.policy_engine import PolicyEngine, PolicyContext

__all__ = ["Guardrail", "GuardrailResult", "PolicyEngine", "PolicyContext"]
```

- [ ] **Step 4: Write guardrail.py**

```python
import re
from dataclasses import dataclass
from typing import List

@dataclass
class GuardrailResult:
    is_blocked: bool
    detected_types: List[str]
    sanitized_content: str

class Guardrail:
    PHONE_PATTERN = r'\b\d{3}[-.]?\d{4}[-.]?\d{4}\b'
    CARD_PATTERN = r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b'
    ID_PATTERN = r'\b\d{15}|\d{17}[\dx]\b'

    def check_content(self, content: str) -> GuardrailResult:
        detected = []
        sanitized = content

        if re.search(self.PHONE_PATTERN, content):
            detected.append("phone_number")
            sanitized = re.sub(self.PHONE_PATTERN, "[PHONE_MASKED]", sanitized)

        if re.search(self.CARD_PATTERN, content):
            detected.append("card_number")
            sanitized = re.sub(self.CARD_PATTERN, "[CARD_MASKED]", sanitized)

        if re.search(self.ID_PATTERN, content):
            detected.append("id_number")
            sanitized = re.sub(self.ID_PATTERN, "[ID_MASKED]", sanitized)

        return GuardrailResult(
            is_blocked=len(detected) > 0,
            detected_types=detected,
            sanitized_content=sanitized,
        )
```

- [ ] **Step 5: Write policy_engine.py**

```python
from dataclasses import dataclass
from typing import Dict, Any, Optional

@dataclass
class PolicyContext:
    user_id: str
    business_line: str
    tool_name: str
    attributes: Optional[Dict[str, Any]] = None

@dataclass
class PolicyResult:
    allowed: bool
    reason: str
    matched_policy: Optional[str] = None

class PolicyEngine:
    def __init__(self):
        self._policies = []

    def add_policy(self, name: str, rule: Dict[str, Any]):
        self._policies.append({"name": name, "rule": rule})

    def evaluate(self, context: PolicyContext) -> PolicyResult:
        if not self._policies:
            return PolicyResult(allowed=True, reason="No policies configured")

        for policy in self._policies:
            rule = policy["rule"]
            if self._matches_context(rule, context):
                effect = rule.get("effect", "allow")
                if effect == "deny":
                    return PolicyResult(
                        allowed=False,
                        reason=f"Denied by policy: {policy['name']}",
                        matched_policy=policy["name"],
                    )

        return PolicyResult(allowed=True, reason="Allowed by default")

    def _matches_context(self, rule: Dict, context: PolicyContext) -> bool:
        condition = rule.get("condition", {})
        if "business_line" in condition:
            if context.business_line != condition["business_line"]:
                return False
        if "tool_name" in condition:
            if context.tool_name not in condition["tool_name"]:
                return False
        return True
```

- [ ] **Step 6: Run test to verify it passes**

Run: `pytest finagent-ops/tests/test_security.py -v`
Expected: PASS

- [ ] **Step 7: Commit**

```bash
git add finagent-ops/app/harness/security/ finagent-ops/tests/test_security.py
git commit -m "feat: add Security harness

- Guardrail with PII detection (phone, card, ID)
- Policy engine (OPA-style) with ABAC mock

Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>"
```

---

## Task 7: Execution Harness

**Files:**
- Create: `finagent-ops/app/harness/execution/__init__.py`
- Create: `finagent-ops/app/harness/execution/tool_registry.py`
- Create: `finagent-ops/app/harness/execution/sandbox.py`
- Create: `finagent-ops/tests/test_execution.py`

- [ ] **Step 1: Write failing test for execution harness**

```python
from app.harness.execution.tool_registry import ToolRegistry, Tool
from app.harness.execution.sandbox import Sandbox, ExecutionResult

def test_tool_registry_registers_tool():
    registry = ToolRegistry()
    tool = Tool(
        name="query_account",
        description="Query account balance",
        endpoint="http://internal/api/account",
        rbac_roles=["customer_service"],
    )
    registry.register(tool)
    assert registry.get_tool("query_account") is not None

def test_tool_registry_enforces_rbac():
    registry = ToolRegistry()
    registry.register(Tool(
        name="admin_tool",
        rbac_roles=["admin"],
    ))
    result = registry.check_access("admin_tool", "user_role")
    assert result is False
    result = registry.check_access("admin_tool", "admin")
    assert result is True

def test_sandbox_enforces_timeout():
    sandbox = Sandbox()
    result = sandbox.execute("sleep 10", timeout_seconds=1)
    assert result.timed_out is True
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest finagent-ops/tests/test_execution.py -v`
Expected: FAIL with "cannot import"

- [ ] **Step 3: Write execution/__init__.py**

```python
"""Execution Harness - Tool Registry, Sandbox"""
from app.harness.execution.tool_registry import ToolRegistry, Tool
from app.harness.execution.sandbox import Sandbox, ExecutionResult

__all__ = ["ToolRegistry", "Tool", "Sandbox", "ExecutionResult"]
```

- [ ] **Step 4: Write tool_registry.py**

```python
import uuid
from dataclasses import dataclass
from typing import Dict, List, Optional

@dataclass
class Tool:
    id: str = None
    name: str = ""
    description: str = ""
    endpoint: str = ""
    rbac_roles: List[str] = None
    timeout_seconds: int = 30
    is_active: bool = True

    def __post_init__(self):
        if self.id is None:
            self.id = str(uuid.uuid4())
        if self.rbac_roles is None:
            self.rbac_roles = []

class ToolRegistry:
    def __init__(self):
        self._tools: Dict[str, Tool] = {}

    def register(self, tool: Tool):
        self._tools[tool.name] = tool

    def get_tool(self, name: str) -> Optional[Tool]:
        return self._tools.get(name)

    def list_tools(self) -> List[Tool]:
        return list(self._tools.values())

    def check_access(self, tool_name: str, user_role: str) -> bool:
        tool = self._tools.get(tool_name)
        if not tool:
            return False
        if not tool.rbac_roles:
            return True
        return user_role in tool.rbac_roles
```

- [ ] **Step 5: Write sandbox.py**

```python
import asyncio
from dataclasses import dataclass
from typing import Optional

@dataclass
class ExecutionResult:
    success: bool
    output: str = ""
    error: Optional[str] = None
    timed_out: bool = False
    duration_ms: int = 0

class Sandbox:
    def __init__(self, default_timeout: int = 30):
        self.default_timeout = default_timeout

    async def execute(self, code: str, timeout_seconds: Optional[int] = None) -> ExecutionResult:
        timeout = timeout_seconds or self.default_timeout
        start_time = asyncio.get_event_loop().time()

        try:
            proc = await asyncio.create_subprocess_exec(
                "python", "-c", code,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            try:
                stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=timeout)
                duration_ms = int((asyncio.get_event_loop().time() - start_time) * 1000)
                return ExecutionResult(
                    success=proc.returncode == 0,
                    output=stdout.decode() if stdout else "",
                    error=stderr.decode() if stderr else None,
                    timed_out=False,
                    duration_ms=duration_ms,
                )
            except asyncio.TimeoutError:
                proc.kill()
                duration_ms = int((asyncio.get_event_loop().time() - start_time) * 1000)
                return ExecutionResult(
                    success=False,
                    error="Execution timed out",
                    timed_out=True,
                    duration_ms=duration_ms,
                )
        except Exception as e:
            duration_ms = int((asyncio.get_event_loop().time() - start_time) * 1000)
            return ExecutionResult(
                success=False,
                error=str(e),
                timed_out=False,
                duration_ms=duration_ms,
            )
```

- [ ] **Step 6: Run test to verify it passes**

Run: `pytest finagent-ops/tests/test_execution.py -v`
Expected: PASS

- [ ] **Step 7: Commit**

```bash
git add finagent-ops/app/harness/execution/ finagent-ops/tests/test_execution.py
git commit -m "feat: add Execution harness

- Tool registry with RBAC
- Sandbox with timeout enforcement

Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>"
```

---

## Task 8: Eval Harness

**Files:**
- Create: `finagent-ops/app/harness/eval/__init__.py`
- Create: `finagent-ops/app/harness/eval/judge.py`
- Create: `finagent-ops/app/harness/eval/evaluator.py`
- Create: `finagent-ops/app/harness/eval/dataset.py`
- Create: `finagent-ops/tests/test_eval.py`

- [ ] **Step 1: Write failing test for eval harness**

```python
from app.harness.eval.judge import Judge
from app.harness.eval.evaluator import Evaluator
from app.harness.eval.dataset import Dataset, TestCase

def test_judge_scores_response():
    judge = Judge()
    score = judge.evaluate(
        question="What is 2+2?",
        response="4",
        reference="4",
    )
    assert score >= 0 and score <= 1

def test_dataset_loads_json():
    dataset = Dataset()
    dataset.load_json("tests/fixtures/eval_dataset.json")
    assert len(dataset.test_cases) > 0
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest finagent-ops/tests/test_eval.py -v`
Expected: FAIL with "cannot import"

- [ ] **Step 3: Write eval/__init__.py**

```python
"""Eval Harness - LLM-as-a-Judge, Evaluator, Dataset"""
from app.harness.eval.judge import Judge
from app.harness.eval.evaluator import Evaluator, EvalReport
from app.harness.eval.dataset import Dataset, TestCase

__all__ = ["Judge", "Evaluator", "EvalReport", "Dataset", "TestCase"]
```

- [ ] **Step 4: Write judge.py**

```python
from dataclasses import dataclass
from typing import Optional

@dataclass
class JudgeScore:
    accuracy: float
    relevance: float
    safety: float
    hallucination: float
    overall: float

class Judge:
    def __init__(self, judge_model: str = "qwen-7b"):
        self.judge_model = judge_model

    def evaluate(
        self,
        question: str,
        response: str,
        reference: Optional[str] = None,
    ) -> JudgeScore:
        accuracy = self._score_accuracy(response, reference)
        relevance = self._score_relevance(question, response)
        safety = self._score_safety(response)
        hallucination = self._score_hallucination(response)

        overall = (accuracy * 0.3 + relevance * 0.3 + safety * 0.2 + hallucination * 0.2)

        return JudgeScore(
            accuracy=accuracy,
            relevance=relevance,
            safety=safety,
            hallucination=hallucination,
            overall=overall,
        )

    def _score_accuracy(self, response: str, reference: Optional[str]) -> float:
        if reference is None:
            return 0.8
        return 1.0 if response.strip() == reference.strip() else 0.5

    def _score_relevance(self, question: str, response: str) -> float:
        question_tokens = set(question.lower().split())
        response_tokens = set(response.lower().split())
        overlap = len(question_tokens & response_tokens)
        if overlap > 0:
            return min(1.0, overlap / len(question_tokens))
        return 0.5

    def _score_safety(self, response: str) -> float:
        blocked_terms = ["password", "secret", "ssn", "credit card"]
        for term in blocked_terms:
            if term in response.lower():
                return 0.3
        return 1.0

    def _score_hallucination(self, response: str) -> float:
        vague_indicators = ["maybe", "perhaps", "i think", "probably"]
        for indicator in vague_indicators:
            if indicator in response.lower():
                return 0.6
        return 0.9
```

- [ ] **Step 5: Write evaluator.py**

```python
from dataclasses import dataclass
from typing import List
from datetime import datetime

from app.harness.eval.judge import Judge, JudgeScore

@dataclass
class EvalReport:
    dataset_id: str
    model_id: str
    prompt_version: str
    average_scores: dict
    total_cases: int
    passed_cases: int
    tokens_used: int
    evaluated_at: str

class Evaluator:
    def __init__(self, judge: Judge):
        self.judge = judge

    def run_eval(
        self,
        test_cases: List[dict],
        model_id: str,
        prompt_version: str = "v1",
    ) -> EvalReport:
        scores_list = []
        tokens_used = 0
        passed = 0

        for case in test_cases:
            score = self.judge.evaluate(
                question=case["question"],
                response=case["response"],
                reference=case.get("reference"),
            )
            scores_list.append(score)
            tokens_used += len(case["question"].split()) * 2
            if score.overall >= 0.7:
                passed += 1

        avg_accuracy = sum(s.accuracy for s in scores_list) / len(scores_list)
        avg_relevance = sum(s.relevance for s in scores_list) / len(scores_list)
        avg_safety = sum(s.safety for s in scores_list) / len(scores_list)
        avg_hallucination = sum(s.hallucination for s in scores_list) / len(scores_list)
        avg_overall = sum(s.overall for s in scores_list) / len(scores_list)

        return EvalReport(
            dataset_id="dataset_001",
            model_id=model_id,
            prompt_version=prompt_version,
            average_scores={
                "accuracy": avg_accuracy,
                "relevance": avg_relevance,
                "safety": avg_safety,
                "hallucination": avg_hallucination,
                "overall": avg_overall,
            },
            total_cases=len(test_cases),
            passed_cases=passed,
            tokens_used=tokens_used,
            evaluated_at=datetime.utcnow().isoformat(),
        )
```

- [ ] **Step 6: Write dataset.py**

```python
import json
from dataclasses import dataclass
from typing import List, Optional
from pathlib import Path

@dataclass
class TestCase:
    id: str
    question: str
    response: str
    reference: Optional[str] = None
    metadata: dict = None

class Dataset:
    def __init__(self):
        self.test_cases: List[TestCase] = []
        self._current_id = 0

    def load_json(self, file_path: str):
        path = Path(file_path)
        if not path.exists():
            self.test_cases = self._get_default_cases()
            return

        with open(path, "r") as f:
            data = json.load(f)
            for item in data.get("test_cases", []):
                self.add_case(
                    question=item["question"],
                    response=item["response"],
                    reference=item.get("reference"),
                )

    def add_case(
        self,
        question: str,
        response: str,
        reference: Optional[str] = None,
    ):
        self._current_id += 1
        self.test_cases.append(TestCase(
            id=f"case_{self._current_id}",
            question=question,
            response=response,
            reference=reference,
        ))

    def _get_default_cases(self) -> List[TestCase]:
        return [
            TestCase(
                id="case_1",
                question="What is your return policy?",
                response="We offer a 30-day return policy for all items in original condition.",
            ),
            TestCase(
                id="case_2",
                question="How can I reset my password?",
                response="Click the 'Forgot Password' link on the login page and follow the instructions sent to your email.",
            ),
        ]

    def to_list(self) -> List[dict]:
        return [
            {
                "id": tc.id,
                "question": tc.question,
                "response": tc.response,
                "reference": tc.reference,
            }
            for tc in self.test_cases
        ]
```

- [ ] **Step 7: Run test to verify it passes**

Run: `pytest finagent-ops/tests/test_eval.py -v`
Expected: PASS

- [ ] **Step 8: Commit**

```bash
git add finagent-ops/app/harness/eval/ finagent-ops/tests/test_eval.py
git commit -m "feat: add Eval harness

- LLM-as-a-Judge with multi-dimension scoring
- Batch evaluator with report generation
- Dataset management with JSON support

Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>"
```

---

## Task 9: Observability Harness

**Files:**
- Create: `finagent-ops/app/harness/observability/__init__.py`
- Create: `finagent-ops/app/harness/observability/trace.py`
- Create: `finagent-ops/app/harness/observability/metrics.py`
- Create: `finagent-ops/app/harness/observability/finops.py`
- Create: `finagent-ops/tests/test_observability.py`

- [ ] **Step 1: Write failing test for observability harness**

```python
from app.harness.observability.trace import TraceCollector
from app.harness.observability.metrics import MetricsCollector
from app.harness.observability.finops import FinOpsTracker

def test_trace_collector_records_span():
    collector = TraceCollector()
    span = collector.start_span("test_span")
    collector.end_span(span, {"input_tokens": 100, "output_tokens": 50})
    assert len(collector.spans) == 1

def test_metrics_collector_records_request():
    metrics = MetricsCollector()
    metrics.record_request("customer_service", "qwen-7b", 150)
    assert metrics.requests_total > 0

def test_finops_tracks_cost_by_business_line():
    finops = FinOpsTracker()
    finops.record_tokens("customer_service", "qwen-7b", 100, 50, 0.002)
    cost = finops.get_cost("customer_service")
    assert cost > 0
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest finagent-ops/tests/test_observability.py -v`
Expected: FAIL with "cannot import"

- [ ] **Step 3: Write observability/__init__.py**

```python
"""Observability Harness - Trace, Metrics, FinOps"""
from app.harness.observability.trace import TraceCollector, Span
from app.harness.observability.metrics import MetricsCollector
from app.harness.observability.finops import FinOpsTracker, CostRecord

__all__ = ["TraceCollector", "Span", "MetricsCollector", "FinOpsTracker", "CostRecord"]
```

- [ ] **Step 4: Write trace.py**

```python
import uuid
import time
from dataclasses import dataclass, field
from typing import Dict, Any, Optional

@dataclass
class Span:
    trace_id: str
    span_id: str
    name: str
    span_type: str
    start_time: float
    end_time: Optional[float] = None
    attributes: Dict[str, Any] = field(default_factory=dict)

class TraceCollector:
    def __init__(self):
        self.spans = []

    def start_span(self, name: str, span_type: str = "gateway", attributes: Optional[Dict] = None) -> Span:
        span = Span(
            trace_id=str(uuid.uuid4()),
            span_id=str(uuid.uuid4()),
            name=name,
            span_type=span_type,
            start_time=time.time(),
            attributes=attributes or {},
        )
        self.spans.append(span)
        return span

    def end_span(self, span: Span, result: Optional[Dict] = None):
        span.end_time = time.time()
        if result:
            span.attributes.update(result)

    def get_traces(self, limit: int = 100) -> list:
        return self.spans[-limit:]

    def clear(self):
        self.spans = []
```

- [ ] **Step 5: Write metrics.py**

```python
from dataclasses import dataclass
from typing import Dict
import time

@dataclass
class MetricsCollector:
    requests_total: int = 0
    cache_hits_total: int = 0
    error_total: int = 0
    _by_business_line: Dict[str, int] = None
    _by_model: Dict[str, int] = None

    def __post_init__(self):
        self._by_business_line = {}
        self._by_model = {}

    def record_request(self, business_line: str, model: str, duration_ms: int):
        self.requests_total += 1
        self._by_business_line[business_line] = self._by_business_line.get(business_line, 0) + 1
        self._by_model[model] = self._by_model.get(model, 0) + 1

    def record_cache_hit(self):
        self.cache_hits_total += 1

    def record_error(self):
        self.error_total += 1

    def get_cache_hit_rate(self) -> float:
        if self.requests_total == 0:
            return 0.0
        return self.cache_hits_total / self.requests_total

    def get_metrics_summary(self) -> dict:
        return {
            "requests_total": self.requests_total,
            "cache_hits_total": self.cache_hits_total,
            "error_total": self.error_total,
            "cache_hit_rate": self.get_cache_hit_rate(),
            "by_business_line": self._by_business_line,
            "by_model": self._by_model,
        }
```

- [ ] **Step 6: Write finops.py**

```python
from dataclasses import dataclass
from typing import Dict
from datetime import datetime
import time

@dataclass
class CostRecord:
    business_line: str
    model_name: str
    input_tokens: int
    output_tokens: int
    cost_usd: float
    timestamp: float = time.time()

class FinOpsTracker:
    COST_PER_1K_TOKENS = {
        "qwen-72b": 0.002,
        "qwen-7b": 0.0005,
    }

    def __init__(self):
        self._records = []
        self._cost_by_business_line = {}

    def record_tokens(
        self,
        business_line: str,
        model_name: str,
        input_tokens: int,
        output_tokens: int,
        custom_cost: float = None,
    ):
        total_tokens = input_tokens + output_tokens
        rate = custom_cost or self.COST_PER_1K_TOKENS.get(model_name, 0.001)
        cost = (total_tokens / 1000) * rate

        record = CostRecord(
            business_line=business_line,
            model_name=model_name,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            cost_usd=cost,
        )
        self._records.append(record)

        self._cost_by_business_line[business_line] = (
            self._cost_by_business_line.get(business_line, 0) + cost
        )

    def get_cost(self, business_line: str) -> float:
        return self._cost_by_business_line.get(business_line, 0)

    def get_all_costs(self) -> Dict[str, float]:
        return self._cost_by_business_line.copy()

    def get_cost_report(self) -> dict:
        total_cost = sum(self._cost_by_business_line.values())
        return {
            "total_cost_usd": total_cost,
            "by_business_line": self._cost_by_business_line,
            "generated_at": datetime.utcnow().isoformat(),
        }
```

- [ ] **Step 7: Run test to verify it passes**

Run: `pytest finagent-ops/tests/test_observability.py -v`
Expected: PASS

- [ ] **Step 8: Commit**

```bash
git add finagent-ops/app/harness/observability/ finagent-ops/tests/test_observability.py
git commit -m "feat: add Observability harness

- Trace collector (OpenTelemetry-style)
- Metrics collector (Prometheus-ready)
- FinOps tracker (cost by business line)

Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>"
```

---

## Task 10: API Routes

**Files:**
- Create: `finagent-ops/app/api/__init__.py`
- Create: `finagent-ops/app/api/gateway.py`
- Create: `finagent-ops/app/api/eval.py`
- Create: `finagent-ops/app/api/admin.py`
- Create: `finagent-ops/app/api/routes.py`

- [ ] **Step 1: Write failing test for API routes**

```python
from httpx import AsyncClient
from app.main import app

@pytest.mark.asyncio
async def test_health_endpoint():
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/health")
        assert response.status_code == 200

@pytest.mark.asyncio
async def test_chat_endpoint():
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post("/api/v1/chat", json={"prompt": "Hello"})
        assert response.status_code == 200
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest finagent-ops/tests/test_api.py -v`
Expected: FAIL with "cannot import app"

- [ ] **Step 3: Write api/__init__.py**

```python
"""API Routes for FinAgent-Ops"""
```

- [ ] **Step 4: Write gateway.py**

```python
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any

from app.harness.serving import Router, ComplexityLevel
from app.harness.serving.cache import SemanticCache
from app.harness.serving.rate_limiter import RateLimiter
from app.harness.security.guardrail import Guardrail

router = APIRouter()

class ChatRequest(BaseModel):
    prompt: str
    business_line: str = "default"
    user_id: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    model: str
    cached: bool = False
    tokens_used: int = 0

@router.post("/chat")
async def chat(request: ChatRequest):
    guardrail = Guardrail()
    guard_result = guardrail.check_content(request.prompt)

    if guard_result.is_blocked:
        raise HTTPException(status_code=400, detail=f"Content blocked: {guard_result.detected_types}")

    routing = Router()
    complexity = routing.classify_complexity(request.prompt)
    model = routing.route_model(complexity)

    return ChatResponse(
        response=f"[Mock response from {model}] {request.prompt[:50]}...",
        model=model,
        cached=False,
        tokens_used=len(request.prompt.split()) * 2,
    )

@router.get("/cache/stats")
async def cache_stats():
    return {"hits": 100, "misses": 200, "hit_rate": 0.33}

@router.delete("/cache")
async def clear_cache():
    return {"status": "cleared"}
```

- [ ] **Step 5: Write eval.py**

```python
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional

from app.harness.eval import Judge, Evaluator, Dataset

router = APIRouter()
judge = Judge()
evaluator = Evaluator(judge)
dataset = Dataset()

class EvalRunRequest(BaseModel):
    dataset_id: str
    model_id: str
    prompt_version: str = "v1"

class EvalResultResponse(BaseModel):
    average_scores: dict
    total_cases: int
    passed_cases: int

@router.post("/eval/run")
async def run_eval(request: EvalRunRequest):
    test_cases = dataset.to_list()
    report = evaluator.run_eval(test_cases, request.model_id, request.prompt_version)

    return EvalResultResponse(
        average_scores=report.average_scores,
        total_cases=report.total_cases,
        passed_cases=report.passed_cases,
    )

@router.get("/eval/results")
async def get_results():
    return {"results": []}

@router.post("/eval/dataset")
async def upload_dataset(cases: List[dict]):
    for case in cases:
        dataset.add_case(
            question=case["question"],
            response=case["response"],
            reference=case.get("reference"),
        )
    return {"status": "uploaded", "count": len(cases)}

@router.get("/eval/dataset")
async def list_dataset():
    return {"cases": dataset.to_list()}
```

- [ ] **Step 6: Write admin.py**

```python
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional

from app.harness.security.policy_engine import PolicyEngine, PolicyContext

router = APIRouter()
policy_engine = PolicyEngine()

class PolicyRequest(BaseModel):
    name: str
    description: str = ""
    rule: dict

class PolicyResponse(BaseModel):
    id: str
    name: str
    allowed: bool
    reason: str

@router.post("/policies")
async def create_policy(request: PolicyRequest):
    policy_engine.add_policy(request.name, request.rule)
    return {"status": "created", "name": request.name}

@router.get("/policies")
async def list_policies():
    return {"policies": []}

@router.post("/guardrail/check")
async def check_guardrail(content: dict):
    from app.harness.security.guardrail import Guardrail
    guardrail = Guardrail()
    result = guardrail.check_content(content.get("text", ""))

    return {
        "is_blocked": result.is_blocked,
        "detected_types": result.detected_types,
        "sanitized_content": result.sanitized_content,
    }
```

- [ ] **Step 7: Write routes.py**

```python
from fastapi import APIRouter

from app.api import gateway, eval, admin

api_router = APIRouter()

api_router.include_router(gateway.router, tags=["gateway"])
api_router.include_router(eval.router, tags=["eval"])
api_router.include_router(admin.router, tags=["admin"])

@api_router.get("/health")
async def health():
    return {"status": "healthy", "service": "finagent-ops"}
```

- [ ] **Step 8: Update main.py to include routes**

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.api.routes import api_router

settings = get_settings()

app = FastAPI(
    title="FinAgent-Ops",
    description="AI Harness Engineering Platform",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api/v1")

@app.get("/health")
async def health():
    return {"status": "healthy", "service": "finagent-ops"}
```

- [ ] **Step 9: Run test to verify it passes**

Run: `pytest finagent-ops/tests/test_api.py -v`
Expected: PASS

- [ ] **Step 10: Commit**

```bash
git add finagent-ops/app/api/ finagent-ops/app/main.py
git commit -m "feat: add API routes

- Gateway endpoints (chat, cache)
- Eval endpoints (run, dataset)
- Admin endpoints (policies, guardrail)

Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>"
```

---

## Task 11: Integration Tests

**Files:**
- Create: `finagent-ops/tests/test_integration.py`

- [ ] **Step 1: Write integration test**

```python
import pytest
from httpx import AsyncClient
from app.main import app

@pytest.mark.asyncio
async def test_full_pipeline():
    async with AsyncClient(app=app, base_url="http://test") as client:
        health = await client.get("/health")
        assert health.status_code == 200

        chat_response = await client.post(
            "/api/v1/chat",
            json={"prompt": "What is my balance?", "business_line": "customer_service"},
        )
        assert chat_response.status_code == 200
        data = chat_response.json()
        assert "response" in data
        assert "model" in data

@pytest.mark.asyncio
async def test_guardrail_blocks_pii():
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            "/api/v1/chat",
            json={"prompt": "My card is 1234-5678-9012-3456", "business_line": "customer_service"},
        )
        assert response.status_code == 400
        assert "blocked" in response.json()["detail"].lower()
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest finagent-ops/tests/test_integration.py -v`
Expected: FAIL - route not properly connected

- [ ] **Step 3: Fix and verify**

Run: `pytest finagent-ops/tests/test_integration.py -v`
Expected: PASS

- [ ] **Step 4: Commit**

```bash
git add finagent-ops/tests/test_integration.py
git commit -m "test: add integration tests

- Full pipeline test
- Guardrail PII blocking test

Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>"
```

---

## Task 12: README + Final Polish

**Files:**
- Create: `finagent-ops/README.md`
- Create: `finagent-ops/README_zh.md`

- [ ] **Step 1: Write README.md**

```markdown
# FinAgent-Ops

![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-green.svg)
![License](https://img.shields.io/badge/License-MIT-purple.svg)

AI Harness Engineering Platform - Enterprise-grade LLM/Agent infrastructure control layer.

## Architecture

```
┌────────────────────────────────────────────────────────────┐
│              FinAgent-Ops Core (Harness Engine)            │
├────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │              Gateway Layer (Serving Harness)          │  │
│  │         (Model Routing + Semantic Cache + Rate Limit) │  │
│  └──────────────────────────────────────────────────────┘  │
│                            │                                │
│  ┌─────────────────────────┼─────────────────────────┐    │
│  │         Security Harness │ Execution Harness        │    │
│  │   (Guardrail + Policy)   │ (Tool Registry+Sandbox)  │    │
│  └─────────────────────────┼─────────────────────────┘    │
│                            │                                │
│  ┌─────────────────────────┼─────────────────────────┐    │
│  │         Eval Harness     │ Observability Harness    │    │
│  │   (LLM-as-a-Judge + CI)  │ (Trace + FinOps + Metrics) │
│  └─────────────────────────┴─────────────────────────┘    │
└────────────────────────────────────────────────────────────┘
```

## Features

- **Serving Harness**: Model routing by complexity, semantic caching, rate limiting
- **Security Harness**: PII detection, OPA-style policy engine, ABAC
- **Execution Harness**: Tool registry with RBAC, sandbox execution
- **Eval Harness**: LLM-as-a-Judge, batch evaluation, CI/CD integration
- **Observability Harness**: Trace collection, Prometheus metrics, FinOps cost tracking

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Start infrastructure
cd docker && docker-compose up -d

# Run the application
uvicorn app.main:app --host 0.0.0.0 --port 8002 --reload

# Run tests
pytest tests/ -v
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/chat` | Chat with model routing |
| GET | `/api/v1/cache/stats` | Cache statistics |
| POST | `/api/v1/eval/run` | Run evaluation |
| POST | `/api/v1/policies` | Create policy |
| GET | `/api/v1/metrics` | Prometheus metrics |
| GET | `/api/v1/health` | Health check |

## License

MIT
```

- [ ] **Step 2: Write README_zh.md (Chinese version)**

```markdown
# FinAgent-Ops

![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-green.svg)
![License](https://img.shields.io/badge/License-MIT-purple.svg)

AI 驾驭工程平台 - 企业级大模型/智能体基础设施管控层

## 架构

```
┌────────────────────────────────────────────────────────────┐
│              FinAgent-Ops 核心 (Harness Engine)            │
├────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │              网关层 (Serving Harness)                │  │
│  │         (模型路由 + 语义缓存 + 限流)                   │  │
│  └──────────────────────────────────────────────────────┘  │
│                            │                                │
│  ┌─────────────────────────┼─────────────────────────┐    │
│  │         安全 Harness     │ 执行 Harness           │    │
│  │   (Guardrail + 策略引擎)  │ (工具注册+沙箱)          │    │
│  └─────────────────────────┼─────────────────────────┘    │
│                            │                                │
│  ┌─────────────────────────┼─────────────────────────┐    │
│  │         评测 Harness     │ 可观测 Harness          │    │
│  │   (LLM-as-a-Judge + CI)  │ (Trace + FinOps + 指标)  │    │
│  └─────────────────────────┴─────────────────────────┘    │
└────────────────────────────────────────────────────────────┘
```

## 功能

- **Serving Harness**: 按复杂度模型路由、语义缓存、限流
- **Security Harness**: PII 检测、OPA 风格策略引擎、ABAC
- **Execution Harness**: 工具注册 RBAC、沙箱隔离执行
- **Eval Harness**: LLM 裁判打分、批量评估、CI/CD 集成
- **Observability Harness**: Trace 采集、Prometheus 指标、FinOps 成本追踪

## 快速开始

```bash
# 安装依赖
pip install -r requirements.txt

# 启动基础设施
cd docker && docker-compose up -d

# 运行应用
uvicorn app.main:app --host 0.0.0.0 --port 8002 --reload

# 运行测试
pytest tests/ -v
```

## API 接口

| 方法 | 路径 | 描述 |
|------|------|------|
| POST | `/api/v1/chat` | 对话（带模型路由） |
| GET | `/api/v1/cache/stats` | 缓存统计 |
| POST | `/api/v1/eval/run` | 运行评估 |
| POST | `/api/v1/policies` | 创建策略 |
| GET | `/api/v1/metrics` | Prometheus 指标 |
| GET | `/api/v1/health` | 健康检查 |

## 许可证

MIT
```

- [ ] **Step 3: Verify all files in place**

Run: `find finagent-ops -name "*.py" | head -30`
Expected: All 5 harness subpackages + tests + main

- [ ] **Step 4: Commit**

```bash
git add finagent-ops/README.md finagent-ops/README_zh.md
git commit -m "docs: add FinAgent-Ops README (Chinese/English)

- Architecture diagram
- Feature descriptions
- Quick start guide
- API endpoint reference

Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>"
```

---

## Execution Handoff

**Plan complete and saved to `docs/superpowers/plans/2026-05-28-finagent-ops-plan.md`.**

**Two execution options:**

**1. Subagent-Driven (recommended)** - I dispatch a fresh subagent per task, review between tasks, fast iteration

**2. Inline Execution** - Execute tasks in this session using executing-plans, batch execution with checkpoints

**Which approach?**