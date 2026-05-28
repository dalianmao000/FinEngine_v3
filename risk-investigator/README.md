# Risk-Investigator

A financial risk investigation system with multi-agent workflow, utilizing GraphRAG, LangGraph, and human-in-the-loop validation.

## Features

- **Multi-Agent Workflow**: Coordinated agents for gathering, graphing, reasoning, and reporting
- **GraphRAG**: Knowledge graph-enhanced retrieval for relationship analysis
- **Human-in-the-Loop**: Approval workflow for high-risk investigations
- **PII Redaction**: Automated personally identifiable information protection
- **Audit Logging**: Comprehensive trace and audit trail

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your settings

# Run the application
uvicorn app.main:app --host 0.0.0.0 --port 8001
```

## API Documentation

Once running, visit `/docs` for interactive API documentation.