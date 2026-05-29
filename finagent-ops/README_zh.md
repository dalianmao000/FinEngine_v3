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

## 项目结构

```
finagent-ops/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI 入口
│   ├── config.py           # Pydantic Settings 配置
│   ├── database.py         # 异步 SQLAlchemy 引擎
│   ├── models.py           # SQLAlchemy 数据模型
│   ├── api/                 # API 路由
│   │   ├── __init__.py
│   │   ├── gateway.py      # Serving Harness 网关
│   │   ├── eval.py         # Eval Harness 端点
│   │   ├── admin.py        # Admin 端点（策略管理）
│   │   └── routes.py       # 路由聚合
│   ├── harness/            # 五大 Harness 子系统
│   │   ├── __init__.py
│   │   ├── serving/        # Serving Harness（算力驾驭）
│   │   │   ├── __init__.py
│   │   │   ├── router.py       # 复杂度模型路由
│   │   │   ├── cache.py        # 语义缓存（Redis）
│   │   │   └── rate_limiter.py # 限流器（Token Bucket）
│   │   ├── security/       # Security Harness（安全驾驭）
│   │   │   ├── __init__.py
│   │   │   ├── guardrail.py    # PII 检测 + 内容过滤
│   │   │   └── policy_engine.py # OPA 风格策略引擎
│   │   ├── execution/      # Execution Harness（执行驾驭）
│   │   │   ├── __init__.py
│   │   │   ├── tool_registry.py  # 工具注册 + RBAC
│   │   │   └── sandbox.py      # 沙箱隔离执行
│   │   ├── eval/           # Eval Harness（评测驾驭）
│   │   │   ├── __init__.py
│   │   │   ├── judge.py        # LLM-as-a-Judge
│   │   │   ├── evaluator.py    # 批量评估器
│   │   │   └── dataset.py      # 测试数据集
│   │   └── observability/  # Observability Harness（可观测驾驭）
│   │       ├── __init__.py
│   │       ├── trace.py       # OpenTelemetry Trace 采集
│   │       ├── metrics.py     # Prometheus 指标
│   │       └── finops.py      # FinOps 成本归因
│   └── core/                # 核心工具
│       ├── __init__.py
│       ├── token_counter.py   # tiktoken Token 计数
│       └── exceptions.py      # 自定义异常
├── tests/                  # 测试
│   ├── __init__.py
│   ├── conftest.py         # pytest 异步配置
│   ├── test_serving.py
│   ├── test_security.py
│   ├── test_execution.py
│   ├── test_eval.py
│   ├── test_observability.py
│   ├── test_config.py
│   ├── test_models.py
│   ├── test_integration.py
│   └── test_api.py
├── docker/
│   ├── Dockerfile         # 容器镜像
│   └── docker-compose.yml  # PostgreSQL + Redis
├── docs/                   # 文档
├── requirements.txt        # 依赖
└── README_zh.md            # 本文件
```