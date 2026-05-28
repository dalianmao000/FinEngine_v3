# FinAgent-Ops Design Specification

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build an enterprise-grade AI Harness Engineering platform (FinAgent-Ops) that provides Serving, Security, Execution, Eval, and Observability harnesses for financial AI applications.

**Architecture:** A FastAPI-based gateway platform that intercepts and manages all internal AI application traffic. It implements 5 harness subdomains: Serving (routing/caching), Security (policy/ABAC), Execution (sandbox/tool isolation), Eval (quality gates), and Observability (FinOps/trace). The platform does not process C端 business requests directly but acts as an infrastructure control layer.

**Tech Stack:** FastAPI, async SQLAlchemy, Redis (semantic cache/rate limiting), OpenTelemetry, PostgreSQL, Prometheus, Grafana, Pydantic.

---

## 1. Project Overview

### 1.1 Purpose
FinAgent-Ops is an enterprise-grade LLMOps / Agent PaaS platform that接管所有内部 AI 应用的流量、配置、监控和发布流程，实现"大模型调用的标准化、可观测化与成本最优化"。

### 1.2 Business Value
- **成本管控**: Token quota management, semantic caching to reduce redundant calls
- **质量保障**: Automated eval pipelines with CI/CD integration
- **安全合规**: OPA-style policy engine with ABAC for tool access control
- **可观测性**: FinOps-level cost attribution by business line, model, prompt version

### 1.3 Target Users
- Internal AI development teams (Agent developers)
- Business lines consuming AI capabilities
- Technology operations team (platform administrators)

---

## 2. Project Structure

```
finagent-ops/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI entry point
│   ├── config.py           # Configuration (from env)
│   ├── database.py         # Async SQLAlchemy setup
│   ├── models.py           # SQLAlchemy models
│   ├── api/
│   │   ├── __init__.py
│   │   ├── gateway.py      # Serving harness: routing, caching
│   │   ├── eval.py         # Eval harness endpoints
│   │   ├── admin.py        # Admin endpoints (policy management)
│   │   └── routes.py       # API router aggregator
│   ├── harness/
│   │   ├── __init__.py
│   │   ├── serving/        # Serving harness
│   │   │   ├── __init__.py
│   │   │   ├── router.py   # Model routing by complexity
│   │   │   ├── cache.py    # Semantic cache (Redis)
│   │   │   └── rate_limiter.py  # Rate limiting
│   │   ├── security/       # Security harness
│   │   │   ├── __init__.py
│   │   │   ├── guardrail.py   # Content filtering
│   │   │   └── policy_engine.py  # OPA-style policy engine
│   │   ├── execution/      # Execution harness
│   │   │   ├── __init__.py
│   │   │   ├── tool_registry.py  # Tool registration with RBAC
│   │   │   └── sandbox.py   # Tool execution isolation
│   │   ├── eval/           # Eval harness
│   │   │   ├── __init__.py
│   │   │   ├── judge.py    # LLM-as-a-Judge
│   │   │   ├── evaluator.py  # Eval runner
│   │   │   └── dataset.py  # Test dataset management
│   │   └── observability/  # Observability harness
│   │       ├── __init__.py
│   │       ├── trace.py    # OpenTelemetry trace collection
│   │       ├── metrics.py  # Prometheus metrics
│   │       └── finops.py   # Cost attribution
│   └── core/
│       ├── __init__.py
│       ├── token_counter.py   # Token counting (tiktoken)
│       └── exceptions.py      # Custom exceptions
├── tests/
│   ├── __init__.py
│   ├── test_serving.py
│   ├── test_security.py
│   ├── test_eval.py
│   ├── test_observability.py
│   └── conftest.py
├── docker/
│   ├── docker-compose.yml
│   └── Dockerfile
├── docs/
├── requirements.txt
└── README.md
```

---

## 3. API Endpoints

### 3.1 Gateway Endpoints (Serving Harness)

| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/v1/chat` | Proxy chat request with caching/routing |
| POST | `/api/v1/chat/stream` | Streaming chat with token counting |
| GET | `/api/v1/cache/stats` | Cache hit rate statistics |
| DELETE | `/api/v1/cache` | Clear semantic cache |

### 3.2 Model Management

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/v1/models` | List available models |
| POST | `/api/v1/models` | Register new model |
| PUT | `/api/v1/models/{model_id}` | Update model config |

### 3.3 Security Endpoints

| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/v1/policies` | Create security policy |
| GET | `/api/v1/policies` | List policies |
| POST | `/api/v1/guardrail/check` | Manual guardrail check |

### 3.4 Eval Endpoints

| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/v1/eval/run` | Trigger eval pipeline |
| GET | `/api/v1/eval/results` | Get eval results |
| POST | `/api/v1/eval/dataset` | Upload test dataset |
| GET | `/api/v1/eval/dataset` | List datasets |

### 3.5 Observability Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/v1/metrics` | Prometheus metrics endpoint |
| GET | `/api/v1/costs` | Cost attribution dashboard |
| GET | `/api/v1/traces` | Query traces |

### 3.6 Tool Registry Endpoints

| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/v1/tools` | Register a tool |
| GET | `/api/v1/tools` | List tools |
| GET | `/api/v1/tools/{tool_id}` | Get tool details |

### 3.7 Health

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/v1/health` | Health check |

---

## 4. Core Components

### 4.1 Serving Harness

**Router (Model Routing by Complexity)**
- Analyze request complexity via prompt embedding
- Route simple requests to `Qwen-7B` (low cost, low latency)
- Route complex requests to `Qwen-72B` (high cost, high quality)
- Configurable thresholds

**Semantic Cache (Redis-based)**
- Store request-response pairs with semantic similarity
- Use embedding similarity (cosine) to detect cache hits
- TTL-based cache expiration
- Cache hit rate metrics

**Rate Limiter**
- Token bucket algorithm per business line
- Configurable quotas (requests/minute, tokens/day)
- Redis-backed distributed rate limiting

### 4.2 Security Harness

**Guardrail (Content Filter)**
- Block PII in requests/responses
- Filter sensitive financial terms based on policy
- Async interceptor pattern (non-blocking)

**Policy Engine (OPA-style)**
- Rego-like policy rules stored in PostgreSQL
- Evaluate request context (user, business_line, tool)
- Return allow/deny with reason

**ABAC (Attribute-Based Access Control)**
- Attributes: user_id, business_line, tool_name, time
- Policy matching returns permissions
- Mock implementation (production needs LDAP)

### 4.3 Execution Harness

**Tool Registry**
- Register tools with metadata (name, description, RBAC roles)
- Tool invocation tracking
- Version management

**Sandbox (Tool Isolation)**
- Tool execution timeout enforcement
- Resource limit checks (memory, CPU)
- Mock sandbox (production needs gVisor)

### 4.4 Eval Harness

**LLM-as-a-Judge**
- Use a secondary LLM to evaluate responses
- Criteria: accuracy, relevance, safety, hallucination
- Configurable judge prompt templates

**Evaluator**
- Load test dataset (JSON/CSV)
- Run batch evaluation
- Generate score report (JSON + HTML)

**CI/CD Integration**
- Webhook trigger on code/prompt changes
- GitHub Actions workflow template
- PR comment with eval scores

### 4.5 Observability Harness

**Trace Collection (OpenTelemetry)**
- Span for: gateway, model_call, tool_execution, guardrail
- Attributes: business_line, model, prompt_version, token_count
- PostgreSQL trace storage

**Prometheus Metrics**
- `finagent_requests_total` (counter)
- `finagent_request_duration_seconds` (histogram)
- `finagent_cache_hit_total` (counter)
- `finagent_cost_by_business_line` (gauge)

**FinOps Dashboard**
- Cost by business line (daily/weekly/monthly)
- Cost by model (token breakdown)
- Cost by prompt version (trend)
- Cache hit rate over time

---

## 5. Database Schema

### 5.1 Models (SQLAlchemy)

**ModelConfig**
```python
id: UUID (PK)
name: str
provider: str  # dashscope, openai
model_id: str  # qwen-72b, qwen-7b
endpoint: str
config: JSON  # temperature, max_tokens, etc.
is_active: bool
created_at: datetime
updated_at: datetime
```

**Policy**
```python
id: UUID (PK)
name: str
description: str
rule: JSON  # Rego-like policy
priority: int
is_active: bool
created_at: datetime
```

**Tool**
```python
id: UUID (PK)
name: str
description: str
endpoint: str
rbac_roles: JSON  # allowed roles
timeout_seconds: int
is_active: bool
created_at: datetime
```

**EvalResult**
```python
id: UUID (PK)
dataset_id: UUID (FK)
model_id: str
prompt_version: str
scores: JSON  # {accuracy, relevance, safety, hallucination}
tokens_used: int
evaluated_at: datetime
```

**TraceLog**
```python
id: UUID (PK)
trace_id: str
span_type: str  # gateway, model_call, tool
business_line: str
model_name: str
prompt_version: str
input_tokens: int
output_tokens: int
duration_ms: int
metadata: JSON
created_at: datetime
```

**BusinessLineCost**
```python
id: UUID (PK)
business_line: str
date: date
model_name: str
prompt_version: str
input_tokens: int
output_tokens: int
cost_usd: float
created_at: datetime
```

---

## 6. Configuration

### 6.1 Environment Variables

```env
# Database
DATABASE_URL=postgresql+asyncpg://user:pass@localhost:5432/finagent_ops

# Redis
REDIS_URL=redis://localhost:6379/0

# LLM Providers
DASHSCOPE_API_KEY=sk-xxxxx

# OpenTelemetry
OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:4317
OTEL_SERVICE_NAME=finagent-ops

# Server
HOST=0.0.0.0
PORT=8002
```

### 6.1 Config Models (Pydantic)

```python
class Settings(BaseSettings):
    database_url: str
    redis_url: str
    dashscope_api_key: str
    otel_exporter_otlp_endpoint: str = "http://localhost:4317"
    otel_service_name: str = "finagent-ops"
    host: str = "0.0.0.0"
    port: int = 8002
```

---

## 7. Acceptance Criteria

### 7.1 Serving Harness
- [ ] Cache hit rate > 30% for repeated queries
- [ ] Model routing reduces cost by > 40% for simple queries
- [ ] Rate limiter enforces quota correctly

### 7.2 Security Harness
- [ ] Guardrail blocks PII in requests
- [ ] Policy engine evaluates and returns allow/deny
- [ ] ABAC restricts tool access by role

### 7.3 Execution Harness
- [ ] Tool registry stores and retrieves tools
- [ ] Timeout enforcement works
- [ ] Sandbox execution is isolated

### 7.4 Eval Harness
- [ ] LLM-as-a-Judge scores responses
- [ ] Batch eval runs and generates report
- [ ] CI/CD webhook integration works

### 7.5 Observability Harness
- [ ] OpenTelemetry traces are recorded
- [ ] Prometheus metrics are exposed
- [ ] FinOps dashboard shows cost by business line

---

## 8. MVP vs Production Gap

| Component | MVP | Production Gap |
|-----------|-----|----------------|
| Semantic Cache | Redis with simple embedding | Vector DB (ChromaDB) for semantic matching |
| ABAC | Mock in-memory | LDAP/AD integration |
| Sandbox | Mock timeout | gVisor/Kata Containers |
| Trace Storage | PostgreSQL | ClickHouse for OLAP |
| Eval Dataset | CSV with 20 samples | Golden dataset with domain experts |

---

## 9. Project Naming

- **Project**: FinAgent-Ops
- **No company names** in any generated files
- Use "FinEngine" as the overall platform name

---

## 10. License

MIT License