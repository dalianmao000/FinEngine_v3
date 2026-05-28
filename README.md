# AI-Engine v3

金融级 AI Agent 系统 - 面试级生产项目集

> 本项目包含两个互补的 AI Agent 系统，展示从通用智能体平台到垂直场景解决方案的完整技术能力。

---

## 项目价值

### 为什么这不是 "玩具项目"

| 维度 | Demo 项目 | 本项目 | 差异原因 |
|------|-----------|--------|----------|
| **架构设计** | 单文件、硬编码逻辑 | 模块化、分层解耦 | 可扩展到 10+ 工具、3+ 场景 |
| **状态管理** | 全局变量、隐式状态 | TypedDict + LangGraph 状态机 | 类型安全、可复现、可调试 |
| **工具调用** | if-else 分支 | `@register_tool` 装饰器 | 新增工具无需修改核心代码 |
| **安全合规** | 无或形式化 | PII 脱敏 + 人工审批 + 审计日志 | 满足金融级合规要求 |
| **测试** | 无或手动测试 | 95+ 自动化测试 | 可持续集成、 regression 检测 |
| **图数据库** | Mock 数据 | Neo4j + 参数化 Cypher 查询 | 防止注入攻击、支持真实图查询 |
| **错误处理** | 返回码/异常泄露 | 统一的错误抽象 + 链路追踪 | 线上问题可定位、可复现 |

### 核心技术亮点

**1. Multi-Agent 协作模式**
```
FinAgent-Core: 通用平台（场景路由 + RAG + 工具编排）
Risk-Investigator: 垂直工作流（四阶段调查流水线）
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
AI-Engine_v3/
├── finagent-core/          # 通用智能体核心引擎
│   ├── app/
│   │   ├── agent/          # 编排器 + 状态机
│   │   ├── rag/            # 知识库检索
│   │   ├── tools/          # 工具注册中心
│   │   ├── llm/            # LLM 客户端
│   │   └── safety/         # PII 检测 + 内容过滤
│   └── tests/              # 核心测试
│
├── risk-investigator/      # 风控调查工作流
│   ├── app/
│   │   ├── investigation/  # 四阶段调查节点
│   │   ├── graph_rag/      # Cypher 查询生成
│   │   ├── safety/         # PII 脱敏 + 人工审批
│   │   └── audit/          # 审计日志
│   └── tests/              # 95 测试
│
└── README.md               # 本文件
```

---

## FinAgent-Core vs Risk-Investigator

| 维度 | FinAgent-Core | Risk-Investigator |
|------|---------------|-------------------|
| **定位** | 通用 Agent 平台 | 风控垂直场景工作流 |
| **架构** | 单体多技能 Agent | Pipeline 式多 Agent 协作 |
| **状态管理** | LangGraph 状态机 | TypedDict + 条件路由 |
| **核心能力** | 意图识别 + RAG + 工具调用 | 调查流水线 + 图查询 |
| **安全特点** | PII 检测 + 内容过滤 | PII 脱敏 + 人工审批 |
| **适用场景** | 智能客服、金融顾问 | 风险调查、异常归因 |

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

## 面试建议

### 岗位 1: 通用 AI Agent / 大模型方向

**核心竞争力展示:**
1. **架构设计**: 从 FinAgent-Core 展示 Agent 平台的模块化设计
2. **状态机应用**: LangGraph 的条件路由如何实现意图识别
3. **RAG 工程化**: 混合检索策略、向量数据库选型、评估指标
4. **工具调用链**: `@register_tool` 装饰器原理、工具执行流程

**高频问题准备:**
- "如何设计一个支持 10+ 工具的 Agent 系统？"
- "LangGraph 的状态机和普通状态机有什么区别？"
- "RAG 如何保证召回率和准确率的平衡？"
- "如果工具返回错误，Agent 如何处理？"

### 岗位 2: 风控 AI / 异常检测方向

**核心竞争力展示:**
1. **工作流设计**: Risk-Investigator 四阶段流水线架构
2. **图查询安全**: Cypher 注入防护、参数化查询原理
3. **人工审批机制**: HIGH risk 必须人工确认的风控设计
4. **可解释性**: 风险指标体系、证据链生成

**高频问题准备:**
- "如何设计一个风控调查的工作流？"
- "为什么要有人工审批环节？如何确定阈值？"
- "图数据库在风控场景的应用有哪些优势？"
- "PII 数据如何做到动态脱敏而不影响业务？"

### 通用问题清单

| 问题类型 | 示例问题 |
|----------|----------|
| 项目经历 | "介绍一下你在这个项目中负责的模块" |
| 技术深度 | "LangGraph 的 conditional edge 是如何实现的？" |
| 架构设计 | "为什么要分层设计？不用单体的好处是什么？" |
| 安全合规 | "如何防止 Cypher 注入攻击？" |
| 工程化 | "95 个测试是如何设计的？覆盖率多少？" |
| 业务理解 | "风控场景的核心挑战是什么？" |

### 回答技巧

**1. STAR 法则讲项目:**
```
Situation: 风控场景需要调查高风险交易
Task: 我负责设计调查工作流
Action: 实现了四阶段流水线 (情报收集→图谱探查→逻辑研判→报告生成)
Result: 将调查时间从 30 分钟缩短到 3 分钟
```

**2. 量化技术细节:**
- "使用 LangGraph 的条件路由，通过 `route_by_human_approval` 函数判断是否需要人工审批"
- "Cypher 查询使用参数化查询，防止注入攻击，参数通过 `$user_id` 占位符传递"
- "95 个测试覆盖 7 个模块，异步测试使用 `pytest.mark.asyncio`"

**3. 展示工程意识:**
- "发现 `datetime.utcnow()` 在 Python 3.12 废弃，主动替换为 `datetime.now(timezone.utc)`"
- "CORS 配置原来使用 `*`，修改为从环境变量读取可配置的白名单"
- "状态机使用 `total=False` TypedDict，通过 `RISK_STATE_KEYS` 白名单防止状态污染"

---

## 技术栈汇总

| 组件 | 技术选型 | 用途 |
|------|----------|------|
| 后端框架 | FastAPI 0.110+ | 异步 API |
| Agent 编排 | LangGraph 0.1+ | 状态机 + 条件路由 |
| 图数据库 | Neo4j | 知识图谱查询 |
| 向量数据库 | ChromaDB | RAG 检索 |
| LLM | DashScope (Qwen) | 文本生成 |
| ORM | SQLAlchemy 2.0 | 异步数据库 |
| 测试 | pytest | 异步测试 |
| 可观测 | OpenTelemetry + Phoenix | 全链路追踪 |

---

## 快速验证

```bash
# 克隆项目
git clone https://github.com/your-repo/AI-Engine_v3.git
cd AI-Engine_v3

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
```

---

## License

MIT