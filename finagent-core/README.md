# FinAgent-Core

![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-green.svg)
![License](https://img.shields.io/badge/License-MIT-purple.svg)

金融智能体核心引擎

## 架构

```
┌─────────────────────────────────────────────────────────────────┐
│                        FinAgent Core                              │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │                    API 网关                                │   │
│  │              (FastAPI + CORS + 限流)                       │   │
│  └──────────────────────────────────────────────────────────┘   │
│                            │                                     │
│                            ▼                                     │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │                    Agent 编排器                              │   │
│  │         (场景路由 + 工具分发)                                 │   │
│  └──────────────────────────────────────────────────────────┘   │
│                            │                                     │
│          ┌─────────────────┼─────────────────┐                 │
│          ▼                 ▼                 ▼                   │
│  ┌─────────────┐   ┌─────────────┐   ┌─────────────┐          │
│  │    RAG      │   │   工具      │   │    LLM      │          │
│  │   引擎       │   │  注册中心   │   │  (DashScope)│          │
│  └─────────────┘   └─────────────┘   └─────────────┘          │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │              安全与审计层                                  │   │
│  │     (PII检测 + 内容过滤 + 日志记录)                        │   │
│  └──────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

## 功能

- **多场景支持**: 客户服务、金融顾问、风险控制
- **RAG 引擎**: 知识库检索，向量搜索
- **工具注册中心**: 动态工具注册与执行
- **LLM 集成**: 阿里 DashScope（通义千问）集成
- **安全层**: PII 检测、内容过滤
- **审计日志**: 全链路对话日志记录

## 技术栈

- **框架**: FastAPI + SQLAlchemy
- **LLM**: 阿里 DashScope（通义千问系列）
- **向量检索**: ChromaDB
- **可观测性**: OpenTelemetry
- **测试**: pytest

## 快速开始

```bash
# 安装依赖
pip install -r requirements.txt

# 配置环境
cp .env.example .env
# 编辑 .env 填入 DASHSCOPE_API_KEY

# 启动基础设施
docker-compose up -d

# 运行应用
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# 运行测试
pytest tests/ -v
```

## API 接口

| 方法 | 路径 | 描述 |
|------|------|------|
| POST | `/api/v1/agent/chat` | 与智能体对话 |
| GET | `/api/v1/health` | 健康检查 |

## 项目结构

```
finagent-core/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI 入口
│   ├── config.py           # 配置
│   ├── database.py         # SQLAlchemy 配置
│   ├── agent/
│   │   ├── __init__.py
│   │   ├── router.py       # Agent 编排
│   │   ├── security.py     # PII 检测、内容过滤
│   │   └── audit.py        # 审计日志
│   ├── rag/
│   │   ├── __init__.py
│   │   ├── engine.py       # RAG 引擎
│   │   └── embedder.py     # 文本嵌入
│   ├── tools/
│   │   ├── __init__.py
│   │   └── registry.py     # 工具注册
│   ├── llm/
│   │   ├── __init__.py
│   │   └── dashscope.py    # DashScope LLM 客户端
│   ├── scenarios/
│   │   └── *.yaml          # 场景配置
│   └── api/
│       └── routes.py       # API 路由
├── docker/
│   └── docker-compose.yml  # 服务
├── docs/
└── requirements.txt
```

## 场景

| 场景 | 描述 |
|------|------|
| customer_service | 客户咨询处理 |
| financial_advisory | 金融产品推荐 |
| risk_control | 风险评估与预警 |

## 许可证

MIT