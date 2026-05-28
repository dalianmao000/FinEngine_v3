# Risk-Investigator

![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)
![LangGraph](https://img.shields.io/badge/LangGraph-0.1+-orange.svg)
![Neo4j](https://img.shields.io/badge/Neo4j-5.x-yellowgreen.svg)
![License](https://img.shields.io/badge/License-MIT-purple.svg)

金融级风控智能调查与归因系统

## 架构

```
┌─────────────────────────────────────────────────────────────────┐
│                     调查工作流                                    │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐          │
│  │   情报      │───▶│   图谱      │───▶│   逻辑      │          │
│  │   收集      │    │   探查      │    │   研判      │          │
│  │  (并行取证)  │    │ (Cypher查询)│    │ (指标分析)  │          │
│  └─────────────┘    └─────────────┘    └─────────────┘          │
│                                              │                   │
│                                              ▼                   │
│                                   ┌─────────────────────┐       │
│                                   │   报告生成          │       │
│                                   │   (证据汇总)         │       │
│                                   └─────────────────────┘       │
│                                              │                   │
│                                              ▼                   │
│                               ┌───────────────────────────────┐ │
│                               │  risk_level == "HIGH"?        │ │
│                               │  ┌─────────────────────────┐ │ │
│                               │  │   人工审批               │ │ │
│                               │  │   (Human-in-the-Loop)   │ │ │
│                               │  └─────────────────────────┘ │ │
│                               │           │                   │ │
│                               │           ▼                   │ │
│                               │  ┌─────────────────────────┐ │ │
│                               │  │   审批 / 拒绝            │ │ │
│                               │  └─────────────────────────┘ │ │
│                               └───────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

## 功能

- **多智能体工作流**: 协调式四阶段调查流程
  - 情报收集 (Intel Gathering) - 并行证据采集
  - 图谱探查 (Graph Exploration) - Neo4j Cypher 查询
  - 逻辑研判 (Risk Reasoning) - 指标化风险分析
  - 报告生成 (Report Generation) - 证据综合

- **GraphRAG**: 知识图谱增强检索，参数化 Cypher 查询

- **人工审批**: 高风险调查的审批工作流（risk_level == "HIGH"）

- **PII 脱敏**: 自动识别和保护电话号码、银行卡号、身份证号等个人隐私信息

- **审计日志**: 全链路追踪日志，带 trace_id，满足合规要求

- **LangGraph 状态机**: 条件路由，类型化状态管理

## 技术栈

- **框架**: FastAPI + 异步 SQLAlchemy
- **工作流**: LangGraph 状态机
- **图数据库**: Neo4j（通过 docker-compose 部署）
- **可观测性**: Phoenix (OpenTelemetry)
- **测试**: pytest + AsyncMock

## 快速开始

```bash
# 安装依赖
pip install -r requirements.txt

# 配置环境
cp .env.example .env
# 编辑 .env 配置（Neo4j、数据库连接等）

# 启动基础设施
cd docker && docker-compose up -d

# 运行应用
uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload

# 运行测试
cd .. && pytest tests/ -v
```

## API 接口

| 方法 | 路径 | 描述 |
|------|------|------|
| POST | `/api/v1/investigations` | 发起新调查 |
| GET | `/api/v1/investigations/{task_id}` | 查询调查状态 |
| POST | `/api/v1/investigations/{task_id}/approve` | 审批通过 |
| POST | `/api/v1/investigations/{task_id}/reject` | 审批拒绝 |
| GET | `/api/v1/health` | 健康检查 |

## 项目结构

```
risk-investigator/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI 入口
│   ├── config.py           # Pydantic Settings 配置
│   ├── investigation/      # 调查工作流核心
│   │   ├── __init__.py
│   │   ├── state.py        # RiskState TypedDict 类型定义
│   │   ├── workflow.py     # LangGraph 工作流定义
│   │   └── nodes/          # 四阶段调查节点
│   │       ├── __init__.py
│   │       ├── gather_intel.py      # 情报收集（并行取证）
│   │       ├── graph_explorer.py   # 图谱探查（Cypher 查询）
│   │       ├── risk_reasoner.py    # 逻辑研判（指标分析）
│   │       └── report_generator.py  # 报告生成（证据汇总）
│   ├── graph_rag/          # GraphRAG（图谱增强检索）
│   │   ├── __init__.py
│   │   └── cypher_generator.py  # Cypher 查询生成器
│   ├── tools/              # 工具注册中心
│   │   ├── __init__.py
│   │   ├── registry.py     # 工具注册表
│   │   └── risk_tools/     # 风控调查工具
│   │       ├── __init__.py
│   │       ├── transaction_query.py  # 交易流水查询
│   │       ├── graph_query.py        # 图谱查询
│   │       ├── blacklist_check.py   # 黑名单核查
│   │       ├── device_fingerprint.py # 设备指纹
│   │       └── ip_profiler.py        # IP 画像
│   ├── safety/             # 安全与合规
│   │   ├── __init__.py
│   │   ├── pii_redactor.py  # PII 脱敏（电话/卡号/身份证）
│   │   └── human_in_loop.py # 人工审批管理
│   ├── audit/              # 审计日志
│   │   ├── __init__.py
│   │   └── logger.py       # 审计日志记录器
│   ├── db/                 # 数据库
│   │   ├── __init__.py
│   │   ├── database.py     # 异步 SQLAlchemy 引擎
│   │   └── models.py       # SQLAlchemy 数据模型
│   └── api/                # API 路由
│       ├── __init__.py
│       ├── routes.py       # 路由定义
│       └── schemas.py      # Pydantic 请求/响应模型
├── tests/                  # 测试
│   ├── __init__.py
│   ├── test_investigation.py  # 集成测试
│   ├── test_state.py          # 状态测试
│   ├── test_workflow.py       # 工作流测试
│   ├── test_nodes.py          # 节点测试
│   ├── test_tools.py          # 工具测试
│   ├── test_pii_redactor.py   # 脱敏测试
│   ├── test_human_in_loop.py  # 人工审批测试
│   └── test_audit_logger.py   # 审计日志测试
├── docker/
│   ├── Dockerfile         # 容器镜像
│   └── docker-compose.yml  # Neo4j + PostgreSQL + Phoenix
├── risk_investigator.yaml    # LangGraph 工作流配置
├── requirements.txt        # 依赖
└── README_zh.md            # 本文件
```

## 风险等级

| 等级 | 指标数量 | 建议操作 | 人工审批 |
|------|----------|----------|----------|
| HIGH | ≥3 | 冻结账户 (freeze_account) | 必选 |
| MEDIUM | 1-2 | 标记审核 (flag_for_review) | 不需要 |
| LOW | 0 | 通过交易 (approve_transaction) | 不需要 |

## 许可证

MIT