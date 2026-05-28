# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

FinEngine v3 is a production-grade AI Agent system portfolio with 3 independent projects for interview preparation:

- **finagent-core** - General AI Agent platform (Position 1)
- **finagent-ops** - AI Harness Engineering Platform / LLMOps (Position 2)
- **risk-investigator** - Risk investigation workflow (Position 3)

Each project is designed for a separate job position and lives in its own git branch with independent PR workflow.

## Quick Commands

```bash
# Project-specific commands (run inside project directory)
cd finagent-core|finagent-ops|risk-investigator

# Install dependencies
pip install -r requirements.txt

# Run tests
pytest tests/ -v

# Run single test file
pytest tests/test_specific.py -v

# Start infrastructure (where applicable)
cd docker && docker-compose up -d

# Run the application
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

## Architecture

### finagent-core (通用智能体核心引擎)
```
app/
├── agent/           # Orchestrator + state machine (LangGraph)
│   ├── orchestrator.py
│   ├── routing.py
│   ├── safety/      # Pre-check, post-check, jailbreak detection
│   └── memory/      # Short-term, long-term context
├── rag/             # Knowledge retrieval + embedding
├── tools/           # Tool registry with @register_tool decorator
├── llm/             # LLM client (DashScope/Qwen)
└── api/             # FastAPI routes
```

### finagent-ops (AI 驾驭工程平台)
```
app/
├── harness/
│   ├── serving/      # Model routing, semantic cache, rate limiter
│   ├── security/     # Guardrail, policy engine (OPA-style)
│   ├── execution/    # Tool registry, sandbox isolation
│   ├── eval/         # LLM-as-a-Judge, batch evaluator
│   └── observability/ # Trace, metrics, FinOps cost tracking
├── api/             # Gateway endpoints
└── core/            # Token counter, exceptions
```

### risk-investigator (风控调查工作流)
```
app/
├── investigation/
│   ├── workflow.py   # LangGraph workflow
│   ├── state.py     # TypedDict state
│   └── nodes/       # 4-stage investigation nodes
├── graph_rag/        # Cypher query generation for Neo4j
├── safety/           # PII redaction, human-in-loop
└── audit/           # Audit logger
```

## Git Workflow

Projects are separated into independent branches:
- `feature/finagent-core` → PR to main
- `feature/finagent-ops` → PR to main
- `feature/risk-investigator` → PR to main

**Critical**: When implementing features, do NOT mix code from multiple projects. Each task belongs to exactly one project branch.

## Key Patterns

- **Tool Registration**: `@register_tool` decorator for zero-config tool addition
- **State Management**: TypedDict + LangGraph conditional routing
- **Security**: PII detection via regex, parameterised Cypher queries (injection prevention)
- **Async**: All database/network operations use async/await with SQLAlchemy 2.0