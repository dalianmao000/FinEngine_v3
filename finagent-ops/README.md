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