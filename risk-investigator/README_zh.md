# Risk-Investigator

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
│   ├── config.py           # 配置
│   ├── database.py         # 异步 SQLAlchemy 配置
│   ├── models.py           # SQLAlchemy 模型
│   ├── investigation/
│   │   ├── state.py        # RiskState 类型定义
│   │   ├── workflow.py     # LangGraph 工作流
│   │   └── nodes/
│   │       ├── gather_intel.py    # 情报收集节点
│   │       ├── graph_explorer.py  # 图谱探查节点
│   │       ├── risk_reasoner.py   # 逻辑研判节点
│   │       └── report_generator.py # 报告生成节点
│   ├── tools/
│   │   ├── registry.py     # 工具注册中心 (@register_tool 装饰器)
│   │   └── risk_tools.py   # 调查工具
│   ├── safety/
│   │   ├── pii_redactor.py  # PII 脱敏
│   │   └── human_in_loop.py # 人工审批管理
│   ├── audit/
│   │   └── logger.py       # 审计日志
│   └── api/
│       └── routes.py       # API 路由
├── docker/
│   ├── docker-compose.yml  # Neo4j + Phoenix
│   └── Dockerfile
├── tests/
│   ├── test_investigation.py  # 集成测试
│   ├── test_state.py          # 状态测试
│   ├── test_tools.py          # 工具测试
│   ├── test_workflow.py       # 工作流测试
│   └── test_pii_redactor.py   # 脱敏测试
└── requirements.txt
```

## 风险等级

| 等级 | 指标数量 | 建议操作 | 人工审批 |
|------|----------|----------|----------|
| HIGH | ≥3 | 冻结账户 (freeze_account) | 必选 |
| MEDIUM | 1-2 | 标记审核 (flag_for_review) | 不需要 |
| LOW | 0 | 通过交易 (approve_transaction) | 不需要 |

## 许可证

MIT