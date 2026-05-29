# FinEngine v3

![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-green.svg)
![LangGraph](https://img.shields.io/badge/LangGraph-0.1+-orange.svg)
![Neo4j](https://img.shields.io/badge/Neo4j-5.x-yellowgreen.svg)
![License](https://img.shields.io/badge/License-MIT-purple.svg)

金融级 AI Agent 系统 - 通用智能体平台 / 垂直场景解决方案 / 基础设施管控平台

> 本项目包含三个互补的 AI Agent 系统，展示从通用智能体平台到垂直场景解决方案再到基础设施管控平台的完整技术能力。三者共享底层架构，形成"前线作战部队"（FinAgent-Core）、"后勤兵工厂与高速公路"（FinAgent-Ops）、"专项调查武器"（Risk-Investigator）的协同体系。

- **Position 1 - FinAgent-Core**：通用智能体核心引擎
- **Position 2 - FinAgent-Ops**：AI 驾驭工程平台（LLMOps）
- **Position 3 - Risk-Investigator**：风控调查工作流

**架构说明**：三个项目分别对应独立的 git 分支（`feature/finagent-core`、`feature/finagent-ops`、`feature/risk-investigator`），在单一代码库中独立演进。这样设计是为了展示"同一技术栈下不同定位的系统如何互补"，同时保持各自的独立性和可测试性。项目间的公共模式（如工具注册装饰器、TypedDict 状态设计）遵循相同的架构原则，但**未做显式代码共享**——每个项目都是完整自洽的实现，便于独立演示。

---

## 项目价值

### 为什么这不是 "玩具项目"

| 维度 | Demo 项目 | 本项目 | 差异原因 |
|------|-----------|--------|----------|
| **架构设计** | 单文件、硬编码逻辑 | 模块化、分层解耦 | 可扩展到 10+ 工具、3+ 场景 |
| **状态管理** | 全局变量、隐式状态 | TypedDict + LangGraph 状态机 | 类型安全、可复现、可调试 |
| **工具调用** | if-else 分支 | `@register_tool` 装饰器 | 新增工具无需修改核心代码 |
| **安全合规** | 无或形式化 | PII 脱敏 + 人工审批 + 审计日志 | 满足金融级合规要求 |
| **测试** | 无或手动测试 | 95+ 自动化测试 | 可持续集成、regression 检测 |
| **图数据库** | Mock 数据 | Neo4j + 参数化 Cypher 查询 | 防止注入攻击、支持真实图查询 |
| **错误处理** | 返回码/异常泄露 | 统一的错误抽象 + 链路追踪 | 线上问题可定位、可复现 |

### 核心技术亮点

**1. Multi-Agent 协作模式**
```
FinAgent-Core: 通用平台（场景路由 + RAG + 工具编排）
Risk-Investigator: 垂直工作流（四阶段调查流水线）
FinAgent-Ops: 基础设施管控（路由 + 缓存 + 安全 + 评测 + 可观测）
```

**2. 生产级安全设计**
- **Cypher 注入防护**: 参数化查询 `$user_id` 而非字符串拼接
- **PII 动态脱敏**: 电话/银行卡/身份证多模式检测
- **状态防篡改**: `RISK_STATE_KEYS` 白名单验证
- **人工审批门控**: HIGH risk 必须人工确认

**3. 可观测性架构**
- trace_id 全链路追踪
- OpenTelemetry 集成 (Phoenix)
- 分层日志（audit/info/debug）

---

## 项目结构

```
FinEngine_v3/
├── finagent-core/          # 通用智能体核心引擎 (Position 1)
│   ├── app/
│   │   ├── agent/          # 编排器 + 状态机
│   │   ├── rag/            # 知识库检索
│   │   ├── tools/          # 工具注册中心
│   │   ├── llm/            # LLM 客户端
│   │   └── safety/         # PII 检测 + 内容过滤
│   └── tests/              # 核心测试
│
├── risk-investigator/      # 风控调查工作流 (Position 3)
│   ├── app/
│   │   ├── investigation/  # 四阶段调查节点
│   │   ├── graph_rag/      # Cypher 查询生成
│   │   ├── safety/         # PII 脱敏 + 人工审批
│   │   └── audit/          # 审计日志
│   └── tests/              # 95 测试
│
├── finagent-ops/           # AI 驾驭工程平台 (Position 2)
│   ├── app/
│   │   ├── harness/
│   │   │   ├── serving/    # 模型路由 + 语义缓存 + 限流
│   │   │   ├── security/    # Guardrail + 策略引擎 + ABAC
│   │   │   ├── execution/   # 工具注册 + 沙箱隔离
│   │   │   ├── eval/        # LLM-as-a-Judge + 批量评估
│   │   │   └── observability/  # Trace + Metrics + FinOps
│   │   └── api/            # FastAPI 网关
│   └── tests/              # 集成测试
│
└── README.md               # 本文件
```

---

## FinAgent-Core vs Risk-Investigator vs FinAgent-Ops

| 维度 | FinAgent-Core | Risk-Investigator | FinAgent-Ops |
|------|---------------|-------------------|--------------|
| **定位** | 通用 Agent 平台 | 风控垂直场景工作流 | AI 驾驭工程平台 |
| **架构** | 单体多技能 Agent | Pipeline 式多 Agent 协作 | 5 大 Harness 子系统 |
| **状态管理** | LangGraph 状态机 | TypedDict + 条件路由 | 无状态（管控层） |
| **核心能力** | 意图识别 + RAG + 工具调用 | 调查流水线 + 图查询 | 路由/缓存/安全/评测/可观测 |
| **安全特点** | PII 检测 + 内容过滤 | PII 脱敏 + 人工审批 | Guardrail + OPA 策略引擎 |
| **适用场景** | 智能客服、金融顾问 | 风险调查、异常归因 | LLM/Agent 基础设施管控 |

**互补关系**: FinAgent-Core 是底座，Risk-Investigator 是基于底座构建的垂直解决方案。

---

## 与 Demo 项目的核心差异

### 1. 架构复杂度

**Demo 级:**
```python
# 一个文件解决所有问题
def chat(message):
    if "还款" in message:
        return query_db("SELECT ...")
    return "不知道"
```

**本项目:**
```python
# 分层解耦，可测试，可扩展
# Layer 1: Agent 编排器
state = {"scenario": "customer_service", "message": message}
next_node = routing.route(state)

# Layer 2: RAG 检索
context = rag_engine.retrieve(state["message"])

# Layer 3: LLM 生成
response = llm.generate(prompt, context)

# Layer 4: 安全检测
safe_response = security.filter(response)
```

### 2. 工具注册机制

**Demo 级:**
```python
# 硬编码工具调用
if tool == "query_balance":
    result = query_balance(account_id)
elif tool == "query_transaction":
    result = query_transaction(account_id)
```

**本项目:**
```python
# 装饰器注册，零修改扩展
@register_tool(name="query_balance", description="查询账户余额")
async def query_balance(account_id: str) -> dict:
    ...

# 工具执行器自动发现和调用
result = await tool_registry.execute("query_balance", account_id="12345")
```

### 3. 图数据库查询

**Demo 级 (注入风险):**
```python
# 危险！直接字符串拼接
query = f"MATCH (u:User) WHERE u.id = '{user_id}' RETURN u"
```

**本项目 (安全):**
```python
# 参数化查询，O(1) 安全性
query = "MATCH (u:User {user_id: $user_id}) RETURN u"
params = {"user_id": user_id}
```

### 4. 测试覆盖

| 测试类型 | Demo 级 | 本项目 |
|----------|---------|--------|
| 单元测试 | 无或少量 | ✅ 每个模块独立测试 |
| 集成测试 | 手动 Postman | ✅ E2E 自动化 |
| 异步测试 | 忽略 | ✅ `pytest.mark.asyncio` |
| Mock 策略 | 全局 patch | ✅ 精确路径 + context manager |

---

## MVP vs 生产级深度对比

> **重要认知**：个人 MVP 项目与金融级生产环境存在巨大鸿沟。本节帮助您理解从 MVP 到生产级的核心差异点。

### FinAgent-Core 核心模块对比

| 核心维度 | MVP 实现程度 | 生产级要求 | 差异理由 |
|:---|:---|:---|:---|
| **大模型推理** | 🟡 中等<br>调用公有云 API，本地 Ollama 跑 7B/14B | 🟢 极高<br>私有化部署垂域大模型，vLLM/TensorRT-LLM 加速，多活容灾 | 金融数据不允许出域<br>**难点**：高并发显存优化、异构算力调度 |
| **向量数据库** | 🟡 中等<br>ChromaDB 本地模式，几十篇文档 | 🟢 极高<br>Milvus 分布式集群，PB 级向量检索，多租户隔离 | 向量检索性能随数据量指数衰减<br>**难点**：召回率与延迟平衡、分布式索引 |
| **Agent 编排** | 🟡 中等<br>原生 LangGraph，本地内存状态 | 🟢 极高<br>自研框架，状态持久化，断点续传，千级并发 | 开源框架达不到金融级 SLA<br>**难点**：死锁预防、长耗时任务异步调度 |
| **多场景编排** | 🟡 中等<br>YAML 配置切换场景 | 🟢 极高<br>场景沙箱隔离，资源配额独立，算力灵活调度 | 多场景共用底座时资源竞争<br>**难点**：隔离与复用平衡 |
| **RAG 检索** | 🟡 中等<br>简单向量检索 + BM25，无重排序 | 🟢 极高<br>混合检索 + Cross-Encoder 重排序 + 时效性管理 | 召回率与准确率难以平衡<br>**难点**：知识时效性、溯源能力 |
| **安全与权限** | 🔴 较低<br>简单 PII 过滤，无细粒度权限 | 🟢 极高<br>NLP 脱敏网关，RBAC+ABAC，国密算法 | 金融监管红线<br>**难点**：动态脱敏性能、复杂权限策略 |
| **可观测性** | 🟡 中等<br>本地 Phoenix + 控制台日志 | 🟢 极高<br>全链路 Trace，Kafka→ES，保留 5 年，对接监管 | 审计是金融命脉<br>**难点**：海量 Trace 存储与快速检索 |
| **高可用部署** | 🟡 中等<br>Docker Compose 单机 | 🟢 极高<br>K8s 多活，异地灾备，自动故障恢复 | 单机无法满足金融 99.99% SLA<br>**难点**：流量切换、RTO/RPO 保障 |

### FinAgent-Ops 核心模块对比

| 核心维度 | MVP 实现程度 | 生产级要求 | 差异理由 |
|:---|:---|:---|:---|
| **Serving（路由/缓存/限流）** | 🟡 中等<br>token 数量简单分级，Redis 简单 KV 缓存，无向量检索 | 🟢 极高<br>混合意图识别 + 向量相似度匹配，ChromaDB 语义缓存，Redis 分布式限流 | 缓存命中率决定成本优化空间<br>**难点**：语义相似度阈值调优、缓存更新策略 |
| **Security（策略引擎）** | 🟡 中等<br>JSON 规则简单匹配，ABAC Mock 实现 | 🟢 极高<br>OPA Rego 完整语法，LDAP/AD 实时拉取角色，策略热更新 | 企业安全合规是底线<br>**难点**：策略版本管理、多租户隔离、评估性能 |
| **Eval（LLM-as-a-Judge）** | 🟡 中等<br>简单关键词打分，无真实 LLM 调用 | 🟢 极高<br>真实 Secondary LLM 评估，多维度 Cross-Encoder 重排序，Golden Dataset 专家标注 | 评估质量决定 Prompt 迭代方向<br>**难点**：Judge Model 选择、评估一致性、CI/CD 无缝集成 |
| **Observability（FinOps）** | 🟡 中等<br>内存计数器，PostgreSQL 日志，无真实 OpenTelemetry 上报 | 🟢 极高<br>Kafka → ClickHouse 全量 Trace，Prometheus + Grafana Dashboard，5 年保留 | 金融审计是监管要求<br>**难点**：海量数据低成本存储、查询性能、与监管报告对接 |
| **Execution（工具沙箱）** | 🔴 较低<br>Python subprocess 简单超时，无真实容器隔离 | 🟢 极高<br>gVisor/Kata Containers 进程级隔离，网络/文件系统权限最小化 | 恶意工具注入是生产级威胁<br>**难点**：冷启动延迟、资源配额动态调整 |

### AI Harness 工程深度对比表

| Harness 子域 | MVP 方案 (基础管控) | 实际生产级 Harness 工程 (深度驾驭) | 差异理由与生产级难点 |
|:---|:---|:---|:---|
| **1. Eval Harness<br>(评估与质量驾驭)** | 🟡 **脚本化与单一裁判**<br>写 Python 脚本读取测试集，用 LLM-as-a-Judge 打分，输出简单的准确率/幻觉率报告。 | 🟢 **标准化评测框架与防污染**<br>类似 `lm-evaluation-harness` 的企业级定制版。支持多维度指标（RAGAS/TruLens），**严格的测试集防污染隔离**，与 CI/CD 深度集成的质量门禁，支持小模型作为常态化 Judge 以降低成本。 | **理由**：大模型输出非确定，单次评测无统计学意义。<br>**难点**：构建金融专属 Golden Dataset（黄金测试集）；解决 LLM 裁判的"位置偏见"和"自我偏好"；高并发评测时的算力调度。 |
| **2. Serving Harness<br>(推理与流量驾驭)** | 🟡 **API 代理与基础限流**<br>FastAPI 转发请求，基于 Redis 做简单的 QPS 限流和基于规则的模型路由。 | 🟢 **底层推理引擎封装与算力池化**<br>深度集成 `vLLM/TGI`，管控 KV Cache 命中率、Continuous Batching 策略。实现**基于请求复杂度（Token预测）的智能路由**，多级 Fallback（降级）策略，以及 GPU 显存的动态切分（MIG/vGPU）。 | **理由**：金融级高并发下，简单的 API 转发会导致严重的长尾延迟（P99 飙升）。<br>**难点**：大请求（长上下文）对显存的瞬间挤占导致 OOM；多模型混部时的资源隔离与抢占。 |
| **3. Guardrail Harness<br>(安全与边界驾驭)** | 🟡 **规则拦截与简单分类**<br>正则表达式过滤敏感词，简单的 Prompt 注入检测，硬编码的合规词库。 | 🟢 **独立安全模型与动态策略引擎**<br>部署专门的 Guardrail 模型（如 `LlamaGuard` 或微调的 BERT），实现输入/输出**双向异步拦截**。策略引擎支持按业务线、用户角色动态下发安全规则，具备防越狱的自动化红蓝对抗演练机制。 | **理由**：正则无法理解语义级别的越狱攻击（如"角色扮演"、"Base64编码注入"）。<br>**难点**：安全模型自身的推理延迟不能拖累主业务；安全策略的误杀率（False Positive）控制。 |
| **4. Execution Harness<br>(Agent执行与沙箱驾驭)** | 🟡 **直接调用与弱隔离**<br>Agent 直接通过 HTTP 调用外部 API 或执行简单的 Python 脚本，缺乏严格的资源限制。 | 🟢 **强隔离沙箱与权限收敛**<br>代码执行工具放入 `gVisor` 或 `Kata Containers` 强隔离沙箱；API 调用经过统一的 MCP (Model Context Protocol) 网关，实施**细粒度到数据行级的 RBAC/ABAC 权限校验**和严格的超时强杀机制。 | **理由**：Agent 具备自主决策能力，一旦产生幻觉调用错误工具或执行死循环，破坏力极大。<br>**难点**：沙箱启动的冷启动延迟优化；复杂工具链调用时的分布式事务一致性与回滚。 |
| **5. Observability Harness<br>(可观测与成本驾驭)** | 🟡 **基础 Trace 与日志聚合**<br>OpenTelemetry 记录调用链路耗时，存入 PG 数据库，展示基础的 QPS 和错误率面板。 | 🟢 **Token 级归因与 AIOps 根因分析**<br>实现 **FinOps（云财务运营）**，将 Token 消耗精确归因到具体的 Prompt 版本、业务线甚至单个用户。引入 AIOps，对 Trace 数据进行异常检测，自动聚类 Badcase 并生成根因分析报告。 | **理由**：大模型的成本结构与传统微服务完全不同（按 Token 计费），且"系统没报错但回答是错的"这种隐性故障极多。<br>**难点**：海量 Trace 数据中语义级异常的自动发现；流式输出（Streaming）状态下的精准 Token 计量。 |

### Risk-Investigator 核心模块对比

| 核心维度 | MVP 项目实现程度 | 金融生产级要求 | 差异理由与生产级难点 |
|:---|:---|:---|:---|
| **大模型推理与算力** | 🟡 中等<br>调用公有云 API 或本地 Ollama 跑 Qwen-7B/14B，单节点运行 | 🟢 极高<br>私有化部署金融垂域大模型，vLLM/TensorRT-LLM 推理加速，K8s GPU 集群多活容灾 | 金融核心数据**绝对不允许出域**调用公有云 API<br>**难点**：高并发显存优化、异构算力调度、P99 延迟保障 |
| **数据源与 GraphRAG** | 🟡 中等<br>本地 Docker 跑 Neo4j，几十条伪造节点和边，向量库存几十篇 PDF | 🟢 极高<br>分布式图数据库集群，对接实时交易流水、设备指纹库、公安部黑名单，PB 级数据 | 个人无法获取真实金融数据<br>**难点**：多跳查询指数级性能衰减，实时流数据秒级入图 |
| **Agent 编排与状态机** | 🟡 中等<br>原生 LangGraph，状态存本地内存，支持简单线性/条件分支工作流 | 🟢 极高<br>自研框架，状态持久化到 Redis/DB，支持宕机断点续传、复杂事务补偿、千级并发 | 开源框架在极高并发和复杂事务处理上达不到金融级 SLA<br>**难点**：死锁预防、长耗时任务异步调度与资源隔离 |
| **安全、合规与权限** | 🔴 较低<br>简单正则替换脱敏，所有工具对 Agent 开放，无数据行级权限控制 | 🟢 极高<br>NLP 脱敏网关，RBAC+ABAC 数据权限，防 Prompt 注入专用安全模型，国密算法 | 金融监管红线<br>**难点**：动态脱敏性能损耗、复杂 ABAC 权限实时计算、防越狱攻击红蓝对抗 |
| **审计与可观测性** | 🟡 中等<br>Arize Phoenix 本地看 Trace，日志在控制台或本地文件，无长期存储 | 🟢 极高<br>全链路 Trace 接入 SkyWalking，日志加密写入 Kafka→ES，保留 5 年以上，对接监管审计报告 | 审计是金融风控命脉<br>**难点**：海量 Trace 低成本存储与快速检索、幻觉自动化监控与拦截 |
| **业务集成与工具调用** | 🟡 中等<br>FastAPI 编写 4 个返回固定 JSON 的假接口，同步调用，无熔断限流 | 🟢 极高<br>对接真实内部微服务（统一 API 网关），具备熔断、降级、限流，支持异步回调 | 个人无法连接真实银行内部系统<br>**难点**：老旧系统适配、跨部门 API 权限审批与网络打通 |

---

## 技术栈汇总

| 组件 | 技术选型 | 用途 |
|------|----------|------|
| 后端框架 | FastAPI 0.110+ | 异步 API + 中间件 |
| Agent 编排 | LangGraph 0.1+ | 状态机 + 条件路由 |
| 图数据库 | Neo4j | 知识图谱查询 |
| 向量数据库 | ChromaDB | RAG 检索 |
| LLM | DashScope (Qwen) | 文本生成 |
| ORM | SQLAlchemy 2.0 | 异步数据库 |
| 缓存/限流 | Redis | 语义缓存 + 分布式限流 |
| 可观测 | OpenTelemetry + Prometheus | 全链路追踪 + 指标采集 |
| 评测 | tiktoken + LLM-as-Judge | Token 计数 + 自动评分 |
| 测试 | pytest + pytest-asyncio | 异步测试 |

---

## 快速验证

```bash
# 克隆项目
git clone https://github.com/dalianmao000/FinEngine_v3.git
cd FinEngine_v3

# 验证 FinAgent-Core
cd finagent-core
pip install -r requirements.txt
pytest tests/ -v --tb=short

# 验证 Risk-Investigator
cd ../risk-investigator
pip install -r requirements.txt
cd docker && docker-compose up -d
cd ..
pytest tests/ -v --tb=short

# 验证 FinAgent-Ops
cd ../finagent-ops
pip install -r requirements.txt
cd docker && docker-compose up -d
cd ..
pytest tests/ -v --tb=short
```

---

## License

MIT