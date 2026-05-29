# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

<!-- test push -->

## Project Overview

FinEngine_v3 is a monorepo containing **three independent but architecturally related Python projects** that share design patterns and tech stack. All three coexist on the `main` branch — **do not create separate git worktrees for these projects**. Each project is a complete, standalone FastAPI application.



The three positions form a collaboration system: FinAgent-Core is the 前线作战部队 (front-line combat force), FinAgent-Ops is the 后勤兵工厂与高速公路 (logistics and highway infrastructure), and Risk-Investigator is the 专项调查武器 (specialized investigation weapon). See `README.md` for full architecture details.

---

## Development Commands

### All three projects share the same tech stack: FastAPI, LangGraph, SQLAlchemy (async), pytest

**Common setup:**
```bash
# Install dependencies
pip install -r requirements.txt

# Each project has its own .env.example — copy and configure
cp .env.example .env
```

**Running each project:**
```bash
# finagent-core (port 8000)
cd finagent-core && uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# finagent-ops (port 8002)
cd finagent-ops && uvicorn app.main:app --host 0.0.0.0 --port 8002 --reload

# risk-investigator (port 8001) — also requires Neo4j via docker
cd risk-investigator/docker && docker-compose up -d
cd .. && uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload
```

**Running tests:**
```bash
# finagent-core
cd finagent-core && pytest tests/ -v

# finagent-ops
cd finagent-ops && pytest tests/ -v

# risk-investigator
cd risk-investigator && pytest tests/ -v

# Run a single test file
pytest tests/test_workflow.py -v

# Run a single test
pytest tests/test_workflow.py::test_name -v
```

---

## Architecture Patterns

### Shared patterns across all three projects (follow these when making changes):

1. **Tool registration**: `@register_tool` decorator pattern. Tools are discovered via decorator, not hardcoded — new tools require zero core code changes.
2. **TypedDict state**: LangGraph-style `TypedDict` state classes for type-safe, debuggable state management.
3. **PII redaction**: All external data (user input, transaction notes) must be treated as untrusted — always apply PII redaction before logging or passing to LLM.
4. **Parameterized queries**: Cypher and SQL always use parameter binding (``) — never string concatenation.
5. **Audit logging**: Every operation records `trace_id`, timestamp, and structured metadata. Never use `print()` for business logic.
6. **Async SQLAlchemy 2.0**: All database operations use async sessions with `AsyncSession`.
7. **Conditional routing**: LangGraph conditional edges route based on state fields (e.g., `risk_level == HIGH` → human approval node).

### Project-specific patterns:

- **finagent-core**: Single-agent orchestration with scenario routing (`customer_service`, `financial_advisory`, `risk_control`), RAG engine, and layered safety checks.
- **risk-investigator**: Pipeline multi-agent with 4 sequential stages (情报收集 → 图谱探查 → 逻辑研判 → 报告生成). HIGH risk requires `human_in_loop` approval.
- **finagent-ops**: Five independent harness subsystems (serving, security, execution, eval, observability) — no shared state between them.

---

## Git Workflow

- **All three projects live on `main` branch** — do not create worktrees to isolate them.
- Branch protection is enabled: direct pushes to `main` are blocked. Use a PR branch (e.g., `docs/update-readme`) and merge via GitHub UI.
- Owner can self-approve PRs (disable include administrators in branch protection rules if needed).

---

## Personal Reference

- `.memo.md` at repo root contains interview Q&A reference material — never commit this to git.
- Chat files (`chat-岗位差异与协作模式分析 (N).txt`) contain collaborative relationship analysis between the three positions.
