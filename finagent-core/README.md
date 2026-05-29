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
│   ├── config.py           # Pydantic Settings 配置
│   ├── database.py         # 异步 SQLAlchemy 引擎
│   ├── agent/
│   │   ├── __init__.py
│   │   ├── orchestrator.py  # Agent 编排器（场景路由 + 工具分发）
│   │   ├── routing.py       # 场景路由器
│   │   ├── states.py       # TypedDict 状态定义
│   │   ├── safety/         # 安全层
│   │   │   ├── __init__.py
│   │   │   ├── pre_check.py      # 输入安全检查
│   │   │   ├── post_check.py     # 输出安全检查
│   │   │   ├── jailbreak_detector.py  # 越狱检测
│   │   │   ├── policy_manager.py    # 策略管理
│   │   │   └── confidence_monitor.py # 置信度监控
│   │   ├── memory/          # 记忆管理
│   │   │   ├── __init__.py
│   │   │   ├── short_term.py     # 短期记忆（会话级）
│   │   │   ├── long_term.py      # 长期记忆（持久化）
│   │   │   ├── context_manager.py # 上下文管理器
│   │   │   └── entity_tracker.py  # 实体追踪器
│   │   └── audit/          # 审计
│   │       ├── __init__.py
│   │       ├── logger.py         # 审计日志
│   │       ├── tracer.py        # 链路追踪
│   │       ├── anomaly_detector.py  # 异常检测
│   │       └── reporter.py      # 报告生成
│   ├── rag/                # RAG 引擎
│   │   ├── __init__.py
│   │   ├── knowledge_base.py   # 知识库管理
│   │   ├── embedding.py        # 文本嵌入
│   │   └── retriever.py       # 检索器（混合检索）
│   ├── tools/               # 工具注册中心
│   │   ├── __init__.py
│   │   ├── registry.py        # 工具注册表
│   │   ├── schema_validator.py # 参数校验
│   │   └── built_in/          # 内置工具
│   │       ├── __init__.py
│   │       ├── card_management.py  # 卡管理工具
│   │       ├── transaction_query.py # 交易查询工具
│   │       └── knowledge_retriever.py # 知识检索工具
│   ├── llm/                 # LLM 客户端
│   │   ├── __init__.py
│   │   └── client.py        # DashScope 客户端
│   ├── scenarios/           # 场景配置
│   │   ├── customer_service.yaml  # 客服场景
│   │   ├── operations.yaml        # 运营场景
│   │   └── recommendation.yaml    # 推荐场景
│   ├── api/                 # API 路由
│   │   ├── __init__.py
│   │   ├── routes.py        # 路由聚合
│   │   └── schemas.py      # Pydantic 请求/响应模型
│   └── utils/               # 工具函数
│       ├── __init__.py
│       ├── desensitizer.py  # 脱敏工具
│       └── compliance.py   # 合规检查
├── docker/
│   └── docker-compose.yml  # PostgreSQL + Redis 服务
├── tests/                  # 测试
│   ├── __init__.py
│   ├── test_agent.py
│   ├── test_rag.py
│   ├── test_tools.py
│   └── test_api.py
├── data/                   # 数据目录
├── docs/                   # 文档
├── requirements.txt        # 依赖
└── README.md               # 本文件
```

## 场景

| 场景 | 描述 |
|------|------|
| customer_service | 客户咨询处理 |
| financial_advisory | 金融产品推荐 |
| risk_control | 风险评估与预警 |

## 许可证

MIT