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

## 许可证

MIT