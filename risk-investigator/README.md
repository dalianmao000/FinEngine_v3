# Risk-Investigator

A financial-grade risk investigation and attribution system with multi-agent workflow, GraphRAG, and human-in-the-loop validation.

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     Investigation Workflow                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐          │
│  │   Gather    │───▶│   Graph    │───▶│    Risk    │          │
│  │   Intel     │    │  Explorer  │    │  Reasoner  │          │
│  │  (并行取证)  │    │ (图谱探查)  │    │ (逻辑研判)  │          │
│  └─────────────┘    └─────────────┘    └─────────────┘          │
│                                              │                   │
│                                              ▼                   │
│                                   ┌─────────────────────┐       │
│                                   │   Report Generator   │       │
│                                   │     (报告生成)        │       │
│                                   └─────────────────────┘       │
│                                              │                   │
│                                              ▼                   │
│                               ┌───────────────────────────────┐ │
│                               │  risk_level == "HIGH"?         │ │
│                               │  ┌─────────────────────────┐  │ │
│                               │  │  Human-in-the-Loop      │  │ │
│                               │  │  (人工审批)               │  │ │
│                               │  └─────────────────────────┘  │ │
│                               │           │                    │ │
│                               │           ▼                    │ │
│                               │  ┌─────────────────────────┐  │ │
│                               │  │   Approve / Reject       │  │ │
│                               │  └─────────────────────────┘  │ │
│                               └───────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

## Features

- **Multi-Agent Workflow**: Coordinated 4-stage investigation pipeline
  - Intel Gathering (情报收集) - parallel evidence collection
  - Graph Exploration (图谱探查) - Neo4j Cypher queries
  - Risk Reasoning (逻辑研判) - indicator-based analysis
  - Report Generation (报告生成) - evidence synthesis

- **GraphRAG**: Knowledge graph-enhanced retrieval with parameterized Cypher queries

- **Human-in-the-Loop**: Approval workflow for high-risk investigations (risk_level == "HIGH")

- **PII Redaction**: Automated PII protection for phone numbers, card numbers, and ID numbers

- **Audit Logging**: Full-chain trace logging with trace_id for compliance

- **LangGraph State Machine**: Conditional routing with typed state management

## Tech Stack

- **Framework**: FastAPI + async SQLAlchemy
- **Workflow**: LangGraph state machine
- **Graph Database**: Neo4j (via docker-compose)
- **Observability**: Phoenix (OpenTelemetry)
- **Testing**: pytest + AsyncMock

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your settings (Neo4j, database URL, etc.)

# Start infrastructure
cd docker && docker-compose up -d

# Run the application
uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload

# Run tests
cd .. && pytest tests/ -v
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/investigations` | Start new investigation |
| GET | `/api/v1/investigations/{task_id}` | Get investigation status |
| POST | `/api/v1/investigations/{task_id}/approve` | Approve pending investigation |
| POST | `/api/v1/investigations/{task_id}/reject` | Reject pending investigation |
| GET | `/api/v1/health` | Health check |

## Project Structure

```
risk-investigator/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI entry point
│   ├── config.py           # Configuration
│   ├── database.py         # Async SQLAlchemy setup
│   ├── models.py           # SQLAlchemy models
│   ├── investigation/
│   │   ├── state.py        # RiskState TypedDict
│   │   ├── workflow.py     # LangGraph workflow
│   │   └── nodes/
│   │       ├── gather_intel.py
│   │       ├── graph_explorer.py
│   │       ├── risk_reasoner.py
│   │       └── report_generator.py
│   ├── tools/
│   │   ├── registry.py     # ToolRegistry with @register_tool
│   │   └── risk_tools.py   # Investigation tools
│   ├── safety/
│   │   ├── pii_redactor.py # PII masking
│   │   └── human_in_loop.py # Approval manager
│   ├── audit/
│   │   └── logger.py       # AuditLogger
│   └── api/
│       └── routes.py       # API routes
├── docker/
│   ├── docker-compose.yml  # Neo4j + Phoenix
│   └── Dockerfile
├── tests/
│   ├── test_investigation.py
│   ├── test_state.py
│   ├── test_tools.py
│   ├── test_workflow.py
│   └── test_pii_redactor.py
└── requirements.txt
```

## Risk Levels

| Level | Indicators | Action | Human Approval |
|-------|------------|--------|----------------|
| HIGH | ≥3 | freeze_account | Required |
| MEDIUM | 1-2 | flag_for_review | Not required |
| LOW | 0 | approve_transaction | Not required |

## License

MIT