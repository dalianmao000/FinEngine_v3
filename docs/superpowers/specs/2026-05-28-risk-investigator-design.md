# Risk-Investigator 设计文档

> 日期：2026-05-28
> 版本：v1.0
> 项目名：Risk-Investigator（金融级风控智能调查与归因系统）

---

## 一、项目定位与目标

**定位**：面向金融风控场景的多智能体协同调查系统，作为风控审核员的"超级 Copilot"，辅助完成准实时/事后的风险研判与归因分析。

**核心目标**：
- 3个月内完成风控调查 Agent MVP，支持"情报收集→图谱探查→逻辑研判→报告生成"四阶段闭环
- 解决传统风控系统的"黑盒"痛点，输出 100% 白盒化、带完整证据链的《风险调查报告》
- 满足金融监管的可解释性要求，任何风控决策可回溯、可审计

**设计原则**：
- 大模型绝对不参与毫秒级实时交易拦截（那是规则引擎+ML的阵地）
- 大模型作为"超级调查员"介入准实时/事后的异动归因分析
- Human-in-the-loop：高风险操作（冻结/封禁）必须人工审批
- GraphRAG：利用图谱挖掘团伙欺诈和资金回流链路

---

## 二、技术栈总览

| 架构层级 | 技术选型 | 版本 | 说明 |
|:---|:---|:---|:---|
| 后端框架 | FastAPI | 0.110+ | 异步高并发，API友好 |
| Agent编排 | LangGraph | 0.1+ | 状态机 + Human-in-the-loop |
| 大模型 | 阿里百炼（DashScope）/ Ollama（本地） | - | qwen-plus / qwen2.5-7B |
| 图数据库 | Neo4j Aura / 本地 Docker | 5.x | 资金链路图谱存储与查询 |
| 向量数据库 | ChromaDB | 0.4+ | 历史相似案例检索 |
| 关系数据库 | SQLite（演示）/ PostgreSQL（生产） | - | SQLAlchemy统一抽象 |
| 可观测 | OpenTelemetry + Arize Phoenix | - | 全链路Trace + LLM可视化 |
| 数据脱敏 | Microsoft Presidio | 2.2+ | 金融级PII检测与脱敏 |
| 配置管理 | YAML | - | 调查场景配置化管理 |

---

## 三、整体架构

```
┌────────────────────────────────────────────────────────────┐
│                    业务触发层 (Trigger)                     │
│  • 实时风控引擎拦截的疑似欺诈交易 (需人工复核)              │
│  • 运营人员手动输入的疑似违规商户/账户线索                  │
└──────────────────────────┬─────────────────────────────────┘
                            │ POST /investigation/start
┌───────────────────────────▼─────────────────────────────────┐
│                多智能体编排层 (LangGraph)                    │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐  ┌─────────┐│
│  │情报收集Agent│→│图谱探查Agent│→│逻辑研判Agent│→│报告生成 ││
│  │ gather_intel│  │graph_explore│  │risk_reasoner│  │  Agent  ││
│  └────────────┘  └────────────┘  └────────────┘  └─────────┘│
│                                                              │
│  条件路由: high_risk → [人工审批节点] → END                   │
│           low_risk → END                                     │
└──────────────────────────┬────────────────────────────────────┘
                            │
┌───────────────────────────▼─────────────────────────────────┐
│                    风控专属能力层                            │
│  [GraphRAG] Neo4j(资金链路/团伙图谱) + ChromaDB(历史相似案例) │
│  [风控工具集] 交易流水查询 / 设备指纹 / IP画像 / 黑名单查询  │
│  [规则引擎] 硬性规则校验 (如: 涉赌涉诈直接冻结)               │
└──────────────────────────┬────────────────────────────────────┘
                            │
┌───────────────────────────▼─────────────────────────────────┐
│                    安全合规与审计层                          │
│  • PII数据动态脱敏 (送入大模型前掩码卡号/身份证)             │
│  • 决策证据链固化 (所有Tool调用与CoT推理过程上链/存证)       │
│  • Human-in-the-loop (冻结/封禁等高危动作必须人工审批)      │
└─────────────────────────────────────────────────────────────┘
```

---

## 四、目录结构

```
risk-investigator/
├── app/
│   ├── __init__.py
│   ├── main.py                    # FastAPI入口，健康检查
│   ├── config.py                  # 配置管理（.env）
│   ├── api/
│   │   ├── __init__.py
│   │   ├── routes.py               # API路由
│   │   └── schemas.py              # Pydantic模型
│   ├── investigation/
│   │   ├── __init__.py
│   │   ├── workflow.py             # LangGraph调查工作流
│   │   ├── state.py                # RiskState状态定义
│   │   └── nodes/                  # 四阶段Agent节点
│   │       ├── __init__.py
│   │       ├── gather_intel.py     # 情报收集Agent
│   │       ├── graph_explorer.py   # 图谱探查Agent
│   │       ├── risk_reasoner.py    # 逻辑研判Agent
│   │       └── report_generator.py # 报告生成Agent
│   ├── tools/                      # 风控专属工具集
│   │   ├── __init__.py
│   │   ├── registry.py             # 工具注册中心
│   │   └── risk_tools/             # 风控工具
│   │       ├── transaction_query.py
│   │       ├── device_fingerprint.py
│   │       ├── ip_profiler.py
│   │       ├── blacklist_check.py
│   │       └── graph_query.py      # Neo4j Cypher查询
│   ├── graph_rag/                  # GraphRAG引擎
│   │   ├── __init__.py
│   │   ├── cypher_generator.py     # 大模型生成Cypher
│   │   └── subgraph_retriever.py   # 子图检索
│   ├── safety/                     # 风控专属安全
│   │   ├── __init__.py
│   │   ├── pii_redactor.py         # PII脱敏
│   │   └── human_in_loop.py        # 人工介入机制
│   ├── audit/                      # 风控专属审计
│   │   ├── __init__.py
│   │   ├── logger.py               # 调查链路日志
│   │   └── trace.py                # OpenTelemetry埋点
│   └── db/
│       ├── __init__.py
│       ├── database.py             # SQLAlchemy数据库
│       └── models.py               # 数据模型
├── tests/
│   ├── __init__.py
│   ├── test_investigation.py
│   ├── test_graph_rag.py
│   ├── test_safety.py
│   └── test_audit.py
├── docker/
│   ├── docker-compose.yml
│   └── Dockerfile
├── docs/
│   └── design.md
├── risk_investigator.yaml          # 风控场景配置
├── .env.example
├── requirements.txt
└── README.md
```

---

## 五、核心模块详细设计

### 5.1 多智能体调查工作流（LangGraph）

#### RiskState 状态定义

```python
class RiskState(TypedDict):
    task_id: str                      # 调查任务ID
    target_user_id: str               # 被调查用户ID
    trigger_event: str                # 触发事件描述
    collected_evidence: dict          # 情报收集结果
    graph_query_result: str           # 图谱查询结果
    reasoning_process: str            # 大模型思维链(CoT)
    risk_level: str                   # HIGH / MEDIUM / LOW
    final_report: dict                # 最终报告
    human_approval_needed: bool       # 是否需要人工审批
    approval_result: str             # 审批结果 (APPROVED / REJECTED / None)
```

#### 工作流图

```
start
  │
  ▼
┌─────────────────┐
│  gather_intel    │ ← 情报收集Agent (并发调用风控工具集)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  graph_explorer  │ ← 图谱探查Agent (生成Cypher查Neo4j)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  risk_reasoner  │ ← 逻辑研判Agent (CoT推理+GraphRAG)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ report_generator│ ← 报告生成Agent (白盒化输出)
└────────┬────────┘
         │
         ▼
  route_by_risk_level
    │                  │
    │ high_risk        │ low_risk / medium_risk
    ▼                  ▼
┌─────────────┐      END
│human_approval
└──────┬──────┘
       │
       ▼
      END
```

#### 条件路由函数

```python
def route_by_risk_level(state: RiskState) -> str:
    """根据风险等级路由"""
    if state.get("human_approval_needed"):
        return "human_approval"
    return "END"

def should_require_approval(state: RiskState) -> bool:
    """判断是否需要人工审批"""
    risk_level = state.get("risk_level", "LOW")
    # HIGH风险必须人工审批
    if risk_level == "HIGH":
        return True
    # 涉及冻结/封禁等高危操作也需审批
    report = state.get("final_report", {})
    if report.get("suggested_action") in ["freeze_account", "block_merchant"]:
        return True
    return False
```

---

### 5.2 情报收集 Agent (gather_intel)

**职责**：并发调用风控工具集，收集被调查用户的多维度情报。

**调用工具**：
- `get_transaction_history` - 查询近N笔交易流水
- `get_device_fingerprint` - 查询设备指纹信息
- `get_ip_profile` - 查询IP归属地与风险画像
- `check_blacklist` - 查询是否在黑名单中
- `get_user_profile` - 查询用户基本信息与画像

**输出格式**：
```python
{
    "transaction_summary": "近10笔交易，总金额XXX元，疑似异常交易X笔",
    "device_info": {"fingerprint": "...", "risk_level": "HIGH", "last_seen": "..."},
    "ip_info": {"ip": "...", "location": "...", "is_proxy": True},
    "blacklist_status": {"in_blacklist": False, "reason": None},
    "user_profile": {"age": 65, "occupation": "退休", "risk_features": [...]}
}
```

---

### 5.3 图谱探查 Agent (graph_explorer)

**职责**：将交易流水转化为 Cypher 查询语句，查 Neo4j 图谱挖掘隐蔽关联。

**核心逻辑**：
1. 从情报收集结果中提取交易对手方信息
2. 构造 Cypher 查询语句
3. 执行查询，获取资金链路子图
4. 将子图转化为文本描述，喂给研判Agent

**Cypher查询示例**：
```cypher
-- 查找资金回流路径
MATCH (a:User {id: $user_id})-[:TRANSFER]->(b:User)-[:TRANSFER]->(c:User)
WHERE c.risk_level = 'BLACK' OR c.in_blacklist = True
RETURN a, b, c, relationships(a, b, c) AS path

-- 查找疑似传销层级
MATCH (a:User {id: $user_id})-[:TRANSFER*1..3]->(other:User)
WHERE other.account_age_days < 30 AND other.transaction_count > 100
RETURN other
```

**输出格式**：
```python
{
    "fund_flow_paths": [
        {"from": "用户A", "to": "用户B", "amount": 50000, "risk_indicator": "资金回流"},
        {"from": "用户B", "to": "黑名单用户C", "amount": 48000, "risk_indicator": "涉黑关联"}
    ],
    "suspicious_clusters": ["传销层级A", "洗钱链路B"],
    "graph_summary": "发现2条资金回流路径，疑似杀猪盘"
}
```

---

### 5.4 逻辑研判 Agent (risk_reasoner)

**职责**：结合情报+图谱+RAG(历史案例)，进行 CoT 思维链推理，输出风险判定。

**Prompt设计**（关键部分）：
```
你是一名资深的金融风控专家。请根据以下情报和图谱分析结果，
判断用户的风险类型和风险等级。

要求：
1. 必须基于提供的证据进行推理，不能凭空臆测
2. 每个结论必须附带证据来源
3. 如果证据不足，明确标注"证据不足，待人工确认"

输出格式：
- risk_type: 风险类型 (电信诈骗/洗钱/套现/正常等)
- risk_level: HIGH / MEDIUM / LOW
- confidence: 置信度 (0.0-1.0)
- reasoning_chain: 推理链 (list[str])
- key_evidence: 关键证据列表
```

**GraphRAG增强**：
- 检索相似的历史欺诈案例作为参考
- 检索最新的电信诈骗手法库（需定期更新）
- 检索监管政策中的风险特征定义

**输出格式**：
```python
{
    "risk_type": "疑似电信网络诈骗-杀猪盘",
    "risk_level": "HIGH",
    "confidence": 0.92,
    "reasoning_chain": [
        "1. 用户画像异常：65岁退休人群，历史无深夜大额交易习惯。",
        "2. 设备指纹异常：本次交易使用的新设备，3天前曾登录过涉案账户X。",
        "3. 资金链路异常：收款方B与已知黑灰产节点C存在2度关联（图谱证据）。",
        "4. 行为模式异常：夜间22:00向陌生账户转账5万元，符合杀猪盘特征。"
    ],
    "key_evidence": [
        {"type": "device", "ref": "device_fingerprint_api", "detail": "新设备3天前登录涉案账户"},
        {"type": "graph", "ref": "neo4j_query_01", "detail": "资金回流至黑名单用户"}
    ]
}
```

---

### 5.5 报告生成 Agent (report_generator)

**职责**：生成白盒化《风险调查报告》，附带完整推理链和证据列表。

**输出JSON Schema**：
```python
{
    "report_id": "RPT-20260528-001",
    "task_id": "INV-20260528-001",
    "generated_at": "2026-05-28T10:30:00Z",
    "risk_level": "HIGH",
    "risk_type": "疑似电信网络诈骗-杀猪盘",
    "confidence_score": 0.92,
    "summary": "用户疑似遭遇杀猪盘诈骗，涉及金额5万元",
    "reasoning_chain": [
        "1. 用户画像异常：65岁退休人群，历史无深夜大额交易习惯。",
        "2. 设备指纹异常：本次交易使用的新设备，3天前曾登录过涉案账户X。",
        "3. 资金链路异常：收款方B与已知黑灰产节点C存在2度关联（图谱证据）。"
    ],
    "evidence_list": [
        {"type": "API_LOG", "ref": "device_fingerprint_api", "timestamp": "2026-05-28T10:00:00Z", "detail": "设备曾登录涉案账户"},
        {"type": "GRAPH_PATH", "ref": "neo4j_query_01", "nodes": ["UserA", "UserB", "BlacklistC"], "detail": "资金回流路径"}
    ],
    "suggested_action": "临时限制非柜面交易，下发核实工单",
    "requires_human_approval": True,
    "approval_deadline": "2026-05-28T12:00:00Z"
}
```

---

### 5.6 Human-in-the-loop (人工介入机制)

**触发条件**：
- 风险等级为 HIGH
- 建议动作为 `freeze_account`、`block_merchant`、`close_account` 等高危操作

**实现机制**：
1. 报告生成后，工作流暂停于人工审批节点
2. 系统生成审批任务，推送给风控审核员
3. 审核员在 Web/移动端查看报告，点击"批准"或"驳回"
4. 审核结果写入 state.approval_result
5. 工作流继续执行或终止

**API接口**：
```python
# POST /investigation/{task_id}/approve
{"approver_id": "auditor_001", "comment": "确认无误，执行冻结"}

# POST /investigation/{task_id}/reject
{"approver_id": "auditor_001", "comment": "误报，排除风险"}
```

---

### 5.7 PII动态脱敏

**脱敏规则**：
| 原始数据 | 脱敏后 | 正则示例 |
|:---|:---|:---|
| 银行卡号 | `[CARD_001]` | `6[0-9]{14,16}` |
| 手机号 | `[PHONE_001]` | `1[3-9][0-9]{9}` |
| 身份证号 | `[ID_001]` | `[0-9]{17}[0-9X]` |
| 姓名 | `[NAME_001]` | 保留，仅在需要时显示 |

**处理时机**：
- 情报收集阶段：外部数据进入系统前先脱敏
- 图谱查询阶段：Neo4j中只存储脱敏后的节点ID
- 大模型调用前：再次确认Prompt中无明文PII
- 报告生成阶段：根据审核员权限决定是否还原

---

## 六、API接口设计

### 6.1 核心接口

| 方法 | 路径 | 说明 |
|:---|:---|:---|
| POST | `/investigation/start` | 发起风控调查任务 |
| GET | `/investigation/{task_id}/status` | 查询任务状态与进度 |
| GET | `/investigation/{task_id}/report` | 获取调查报告 |
| POST | `/investigation/{task_id}/approve` | 人工审批通过 |
| POST | `/investigation/{task_id}/reject` | 人工审批驳回 |
| GET | `/investigation/{task_id}/trace` | 获取完整链路Trace |
| GET | `/health` | 健康检查 |

### 6.2 请求/响应示例

```json
// POST /investigation/start
// Request
{
    "target_user_id": "user_12345",
    "trigger_event": "用户A在异地向陌生账户B转账50万元，触发反诈模型预警",
    "priority": "HIGH"
}

// Response
{
    "task_id": "INV-20260528-001",
    "status": "PENDING",
    "created_at": "2026-05-28T10:00:00Z",
    "estimated_completion_time": "2026-05-28T10:05:00Z"
}
```

```json
// GET /investigation/INV-20260528-001/report
// Response
{
    "report_id": "RPT-20260528-001",
    "task_id": "INV-20260528-001",
    "status": "PENDING_APPROVAL",
    "risk_level": "HIGH",
    "risk_type": "疑似电信网络诈骗-杀猪盘",
    "confidence_score": 0.92,
    "summary": "用户疑似遭遇杀猪盘诈骗，涉及金额5万元",
    "suggested_action": "临时限制非柜面交易，下发核实工单",
    "requires_human_approval": true,
    "approval_deadline": "2026-05-28T12:00:00Z"
}
```

---

## 七、数据库Schema

### 7.1 调查任务表 (investigation_tasks)

```sql
CREATE TABLE investigation_tasks (
    id TEXT PRIMARY KEY,
    task_id TEXT NOT NULL UNIQUE,
    target_user_id TEXT NOT NULL,
    trigger_event TEXT,
    status TEXT NOT NULL DEFAULT 'PENDING',
    risk_level TEXT,
    final_report_json TEXT,
    human_approval_needed BOOLEAN DEFAULT FALSE,
    approval_result TEXT,
    approver_id TEXT,
    approval_comment TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,
    INDEX idx_task_id (task_id),
    INDEX idx_status (status),
    INDEX idx_target_user_id (target_user_id),
    INDEX idx_created_at (created_at)
);
```

### 7.2 审计日志表 (audit_logs)

```sql
CREATE TABLE audit_logs (
    id TEXT PRIMARY KEY,
    trace_id TEXT NOT NULL,
    task_id TEXT NOT NULL,
    node_name TEXT NOT NULL,
    input_data_json TEXT,
    output_data_json TEXT,
    duration_ms INTEGER,
    error TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_trace_id (trace_id),
    INDEX idx_task_id (task_id),
    INDEX idx_node_name (node_name),
    INDEX idx_created_at (created_at)
);
```

### 7.3 审批记录表 (approval_records)

```sql
CREATE TABLE approval_records (
    id TEXT PRIMARY KEY,
    task_id TEXT NOT NULL,
    approver_id TEXT NOT NULL,
    action TEXT NOT NULL,
    comment TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_task_id (task_id),
    INDEX idx_approver_id (approver_id)
);
```

---

## 八、调查任务状态机

```
PENDING
   │
   ▼
GATHERING ←── 并发调用风控工具集
   │
   ▼
GRAPHING ←── Neo4j图谱查询
   │
   ▼
REASONING ←── CoT推理+GraphRAG
   │
   ▼
GENERATING ←── 生成白盒化报告
   │
   ▼
PENDING_APPROVAL ←── 等待人工审批
   │
   ├─── APPROVED ──→ COMPLETED
   │
   └─── REJECTED ──→ COMPLETED (标记为误报)
```

---

## 九、执行流程（完整链路）

```
触发预警：用户A转账50万给陌生账户B
         │
         ▼
┌───────────────────────────────────────┐
│  1. 发起调查 (POST /investigation/start)
│     创建任务，记录 trace_id
└────────────────────┬──────────────────┘
                     ▼
┌───────────────────────────────────────┐
│  2. 情报收集 (gather_intel)           │
│     并发调用5个风控工具               │
│     • 交易流水 / 设备指纹 / IP画像    │
│     • 黑名单查询 / 用户画像           │
│     输出：结构化情报JSON              │
└────────────────────┬──────────────────┘
                     ▼
┌───────────────────────────────────────┐
│  3. 图谱探查 (graph_explorer)         │
│     提取交易对手方，生成Cypher         │
│     查询Neo4j资金链路                 │
│     输出：子图描述+风险关联           │
└────────────────────┬──────────────────┘
                     ▼
┌───────────────────────────────────────┐
│  4. 逻辑研判 (risk_reasoner)          │
│     结合情报+图谱+RAG(历史案例)       │
│     CoT推理，输出风险判定             │
│     输出：risk_level + reasoning_chain│
└────────────────────┬──────────────────┘
                     ▼
┌───────────────────────────────────────┐
│  5. 报告生成 (report_generator)       │
│     生成白盒化JSON报告                │
│     判断是否需要人工审批              │
└────────────────────┬──────────────────┘
                     ▼
           route_by_risk_level
             │                  │
             │ HIGH             │ MEDIUM/LOW
             ▼                  ▼
┌──────────────────┐          END
│ PENDING_APPROVAL │
│ (暂停，等待审批)  │
└────────┬─────────┘
         │
         ▼
  人工审批 (POST /approve 或 /reject)
         │
         ▼
        END
```

---

## 十、4周落地计划

| 周次 | 目标 | 核心交付 |
|:---|:---|:---|
| **Week 1** | 基建与Mock | FastAPI + LangGraph状态机 + 4个风控Mock工具 + Neo4j本地图谱 |
| **Week 2** | 调查工作流 | 4阶段Agent节点 + 条件路由 + 断点续传 |
| **Week 3** | GraphRAG与安全 | Cypher生成器 + PII脱敏 + Human-in-the-loop |
| **Week 4** | 可观测性与文档 | OpenTelemetry埋点 + Arize Phoenix + README |

---

## 十一、风险与应对

| 风险 | 影响 | 应对措施 |
|:---|:---|:---|
| 大模型幻觉导致错误判定 | 高 | 强制JSON Schema输出 + 证据链校验 + 人工审批兜底 |
| 图谱查询超时/内存溢出 | 中 | Cypher查询深度限制(≤3跳) + 超时熔断 + 降级为规则引擎 |
| 审计日志丢失 | 高 | 异步写入 + 本地缓冲 + 定时落库 |
| 人工审批延误 | 中 | 设置SLA超时提醒 + 自动升级机制 |

---

## 十二、设计确认清单

- [x] 架构分层清晰（触发层→编排层→能力层→安全层）
- [x] 四阶段调查工作流设计完整
- [x] GraphRAG（图谱增强检索）设计完整
- [x] Human-in-the-loop 人工介入机制完整
- [x] PII动态脱敏设计完整
- [x] API接口设计完整
- [x] 数据库Schema设计完整
- [x] 调查任务状态机设计完整
- [x] 4周落地计划可执行