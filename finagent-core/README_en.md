# FinAgent-Core

![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-green.svg)
![License](https://img.shields.io/badge/License-MIT-purple.svg)

Financial AI Agent Core Engine

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        FinAgent Core                              │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │                    API Gateway                            │   │
│  │              (FastAPI + CORS + Rate Limiting)              │   │
│  └──────────────────────────────────────────────────────────┘   │
│                            │                                     │
│                            ▼                                     │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │                    Agent Orchestrator                      │   │
│  │         (Scenario Router + Tool Dispatcher)                │   │
│  └──────────────────────────────────────────────────────────┘   │
│                            │                                     │
│          ┌─────────────────┼─────────────────┐                 │
│          ▼                 ▼                 ▼                   │
│  ┌─────────────┐   ┌─────────────┐   ┌─────────────┐          │
│  │    RAG      │   │   Tools    │   │   LLM       │          │
│  │   Engine    │   │  Registry  │   │  (DashScope)│          │
│  └─────────────┘   └─────────────┘   └─────────────┘          │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │              Security & Audit Layer                       │   │
│  │     (PII Detection + Content Filtering + Logging)         │   │
│  └──────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

## Features

- **Multi-Scenario Support**: Customer service, financial advisory, risk control
- **RAG Engine**: Knowledge base retrieval with vector search
- **Tool Registry**: Dynamic tool registration and execution
- **LLM Integration**: Alibaba DashScope (Qwen) integration
- **Security Layer**: PII detection, content filtering
- **Audit Logging**: Full conversation trace logging

## Tech Stack

- **Framework**: FastAPI + SQLAlchemy
- **LLM**: Alibaba DashScope (Qwen series)
- **Vector Search**: ChromaDB
- **Observability**: OpenTelemetry
- **Testing**: pytest

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your DASHSCOPE_API_KEY

# Start infrastructure
docker-compose up -d

# Run the application
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# Run tests
pytest tests/ -v
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/agent/chat` | Chat with agent |
| GET | `/api/v1/health` | Health check |

## Project Structure

```
finagent-core/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI entry point
│   ├── config.py           # Configuration
│   ├── database.py         # SQLAlchemy setup
│   ├── agent/
│   │   ├── __init__.py
│   │   ├── router.py       # Agent orchestration
│   │   ├── security.py     # PII detection, filtering
│   │   └── audit.py        # Audit logging
│   ├── rag/
│   │   ├── __init__.py
│   │   ├── engine.py       # RAG engine
│   │   └── embedder.py     # Text embedding
│   ├── tools/
│   │   ├── __init__.py
│   │   └── registry.py     # Tool registry
│   ├── llm/
│   │   ├── __init__.py
│   │   └── dashscope.py    # DashScope LLM client
│   ├── scenarios/
│   │   └── *.yaml          # Scenario configurations
│   └── api/
│       └── routes.py       # API routes
├── docker/
│   └── docker-compose.yml  # Services
├── docs/
└── requirements.txt
```

## Scenarios

| Scenario | Description |
|----------|-------------|
| customer_service | Customer inquiry handling |
| financial_advisory | Financial product recommendations |
| risk_control | Risk assessment and alerts |

## License

MIT