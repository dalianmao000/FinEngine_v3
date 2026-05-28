# FinAgent-Core 设计文档

> 日期：2026-05-28
> 版本：v1.0
> 项目名：FinAgent-Core（金融智能体核心引擎）

---

## 一、项目定位与目标

**定位**：面向金融支付场景的企业级Agent基础设施，支持智能客服 / 智能运营 / 智能推荐三大场景通过配置化切换。

**核心目标**：
- 3个月内跑通智能客服MVP，意图识别准确率≥90%
- 构建可复用的Agent PaaS底座，支持多场景快速接入
- 满足金融级安全、合规、可审计的硬性要求

**设计原则**：
- 大中台（统一底座）+ 小前台（场景编排）
- 核心自研：安全护栏、审计追踪、编排引擎
- 能力复用：LangGraph状态机、ChromaDB、阿里百炼

---

## 二、技术栈总览

| 架构层级 | 技术选型 | 版本 | 说明 |
|:---|:---|:---|:---|
| 后端框架 | FastAPI | 0.110+ | 异步高并发，API友好 |
| Agent编排 | LangGraph | 0.1+ | 状态机 + 自研安全护栏 |
| 大模型 | 阿里百炼（DashScope） | - | qwen-plus / qwen-max |
| 向量数据库 | ChromaDB | 0.4+ | 本地文件模式，免部署 |
| 关系数据库 | SQLite（演示）/ PostgreSQL（生产） | - | SQLAlchemy统一抽象 |
| 缓存 | Redis | 7+ | 短期记忆 + 会话状态 |
| 可观测 | OpenTelemetry + Arize Phoenix | - | 全链路Trace + LLM可视化 |
| 数据脱敏 | Microsoft Presidio | 2.2+ | 金融级PII检测与脱敏 |
| 配置管理 | YAML | - | 场景配置化管理 |

---

## 三、整体架构

```
┌─────────────────────────────────────────────────────────────┐
│  L3 业务接入层                                              │
│  [智能客服 API]  [智能运营 API]  [智能推荐 API]             │
└──────────────────────────┬──────────────────────────────────┘
                           │ 统一Agent API（/agent/chat）
┌──────────────────────────▼──────────────────────────────────┐
│  L2 场景编排层（YAML配置化）                                │
│  场景管理器（ScenarioManager）                               │
│  • Prompt模板 / 工具集 / 知识库 / 安全等级 / 记忆策略      │
└──────────────────────────┬──────────────────────────────────┘
                           │ 加载配置
┌──────────────────────────▼──────────────────────────────────┐
│  L1 Agent运行时（核心自研）                                 │
│  ┌────────────┬────────────┬────────────┬────────────┐        │
│  │编排引擎    │ 安全护栏   │ 审计追踪   │ 上下文工程 │        │
│  │Orchestrator│ SafetyGuard│ AuditLogger│ContextEng │        │
│  └────────────┴────────────┴────────────┴────────────┘        │
└──────────────────────────┬──────────────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────────┐
│  L0 能力层                                                  │
│  • RAG引擎（混合检索 + 知识时效性 + 溯源）                  │
│  • 工具注册中心（MCP协议 + 权限管控）                       │
│  • 大模型API（阿里百炼）                                    │
│  • 向量库（ChromaDB）+ 缓存（Redis）                        │
└─────────────────────────────────────────────────────────────┘
```

---

## 四、目录结构

```
finagent-core/
├── app/
│   ├── __init__.py
│   ├── main.py                    # FastAPI入口，健康检查
│   ├── config.py                  # 配置管理（.env）
│   ├── api/
│   │   ├── __init__.py
│   │   ├── routes.py               # API路由
│   │   └── schemas.py              # Pydantic模型
│   ├── agent/
│   │   ├── __init__.py
│   │   ├── orchestrator.py         # Agent调度核心
│   │   ├── states.py               # 状态机定义
│   │   ├── memory/                 # 上下文工程
│   │   │   ├── __init__.py
│   │   │   ├── context_manager.py  # 上下文压缩与窗口管理
│   │   │   ├── short_term.py       # 短期记忆（会话级）
│   │   │   ├── long_term.py        # 长期记忆（用户画像）
│   │   │   └── entity_tracker.py   # 实体槽位追踪
│   │   ├── safety/                 # 安全护栏（增强）
│   │   │   ├── __init__.py
│   │   │   ├── pre_check.py        # 输入预检（脱敏/注入检测）
│   │   │   ├── post_check.py       # 输出校验（合规词/置信度）
│   │   │   ├── jailbreak_detector.py  # 越狱攻击检测
│   │   │   ├── confidence_monitor.py  # 模型置信度监控
│   │   │   └── policy_manager.py   # 安全策略热更新
│   │   ├── audit/                  # 审计追踪（增强）
│   │   │   ├── __init__.py
│   │   │   ├── logger.py           # 全链路TraceLogger
│   │   │   ├── tracer.py           # OpenTelemetry集成
│   │   │   ├── reporter.py         # 合规报表生成
│   │   │   └── anomaly_detector.py # 异常行为检测
│   │   └── routing.py              # 场景路由器
│   ├── tools/
│   │   ├── __init__.py
│   │   ├── registry.py             # 工具注册中心
│   │   ├── schema_validator.py     # 工具入参校验
│   │   └── built_in/               # 内置工具
│   │       ├── transaction_query.py
│   │       ├── knowledge_retriever.py
│   │       └── card_management.py
│   ├── scenarios/                  # 场景配置（YAML）
│   │   ├── customer_service.yaml
│   │   ├── operations.yaml
│   │   └── recommendation.yaml
│   ├── rag/                       # RAG引擎（增强）
│   │   ├── __init__.py
│   │   ├── embedding.py            # 向量化（DashScope Embedding）
│   │   ├── retriever.py            # 混合检索（BM25+向量+重排）
│   │   ├── reranker.py             # Cross-Encoder精排
│   │   ├── knowledge_base.py       # 知识库管理（增量更新）
│   │   ├── source_tracker.py      # 知识溯源
│   │   └── freshness_manager.py    # 知识时效性管理
│   └── utils/
│       ├── __init__.py
│       ├── desensitizer.py         # 脱敏引擎（Presidio封装）
│       └── compliance.py            # 合规词库
├── tests/
│   ├── __init__.py
│   ├── test_agent.py
│   ├── test_safety.py
│   ├── test_rag.py
│   └── test_audit.py
├── docker/
│   └── docker-compose.yml
├── docs/
│   └── design.md
├── .env.example
├── requirements.txt
└── README.md
```

---

## 五、核心模块详细设计

### 5.1 安全护栏（SafetyGuard）— 金融级多层防御

#### 5.1.1 输入预检（PreCheck）

```python
class SafetyPreCheck:
    """输入安全预检，四层防御"""

    def check(self, input_text: str, context: dict) -> CheckResult:
        results = []

        # Layer 1: PII脱敏
        pii_result = self.pii_redactor.redact(input_text)
        results.append(("pii_redact", pii_result))

        # Layer 2: Prompt注入检测
        injection_result = self.injection_detector.detect(input_text)
        results.append(("injection", injection_result))

        # Layer 3: 越狱攻击检测
        jailbreak_result = self.jailbreak_detector.detect(input_text)
        results.append(("jailbreak", jailbreak_result))

        # Layer 4: 场景权限校验
        permission_result = self.permission_checker.check(context)
        results.append(("permission", permission_result))

        # 综合判定
        blocked = any(r[1].blocked for r in results)
        risk_level = max(r[1].risk_level for r in results)

        return CheckResult(blocked=blocked, risk_level=risk_level, details=results)
```

#### 5.1.2 Prompt注入模式库

```python
INJECTION_PATTERNS = [
    r"(?i)ignore\s+(previous|all|my)\s+instructions",
    r"(?i)disregard\s+(your|all)\s+(rules|policies)",
    r"(?i)you\s+are\s+now\s+(?:a\s+)?(?:different|new)",
    r"(?i)forget\s+(?:everything|all|what)\s+(?:you|we)\s+know",
    r"(?i)pretend\s+(?:you|to)\s+(?:are|be)\s+(?:not|without)",
    r"(?i)system\s*:\s*",
    r"(?i)assistant\s*:\s*",
    r"<\s*script",  # XSS
    r"\{\{.*\}\}",  # 模板注入
]
```

#### 5.1.3 越狱攻击检测（JailbreakDetector）

```python
class JailbreakDetector:
    """检测常见越狱攻击模式"""

    ATTACK_PATTERNS = [
        # 角色扮演类
        "现在你是",
        "你是一个",
        "假设你是",
        # 编码类
        r"base64[:=]",
        r"\\x[0-9a-f]{2}",
        # 角色扮演绕过
        r"dan.*mode",
        r"developer.*mode",
        # 分割攻击
        r"[​-‏]",  # 零宽字符
    ]

    def detect(self, text: str) -> DetectionResult:
        matches = []
        for pattern in self.ATTACK_PATTERNS:
            found = re.findall(pattern, text, re.IGNORECASE)
            if found:
                matches.append({"pattern": pattern, "matches": found})

        risk_level = "high" if len(matches) >= 2 else "medium" if matches else "low"
        return DetectionResult(
            blocked=len(matches) >= 2,
            risk_level=risk_level,
            matches=matches
        )
```

#### 5.1.4 模型置信度监控（ConfidenceMonitor）

```python
class ConfidenceMonitor:
    """
    监控模型输出的置信度，低置信度触发人工介入
    """

    def __init__(self, threshold: float = 0.7):
        self.threshold = threshold

    async def check(self, response: LLMResponse) -> ConfidenceResult:
        # 方法1：利用API返回的logprobs计算置信度
        confidence = response.logprob_score

        # 方法2：多次采样检测一致性（如采样3次，统计答案一致性）
        consistency = await self._check_consistency(response.input)

        # 方法3：拒绝采样检测（让模型先说"无法回答"的能力）
        refusal_score = await self._check_refusal(response)

        final_score = (confidence + consistency + (1 - refusal_score)) / 3

        return ConfidenceResult(
            confidence=final_score,
            below_threshold=final_score < self.threshold,
            suggest_human=final_score < self.threshold * 0.8,
            details={
                "logprob": confidence,
                "consistency": consistency,
                "refusal_score": refusal_score
            }
        )
```

#### 5.1.5 安全策略热更新（PolicyManager）

```python
class SafetyPolicyManager:
    """
    支持运行时动态更新安全策略，无需重启服务
    """

    def __init__(self, policy_path: str = "scenarios/*/safety.yaml"):
        self.policy_path = policy_path
        self._cache = {}
        self._last_modified = {}
        self._watcher = FileWatcher(policy_path, callback=self._on_policy_change)

    def get_policy(self, scenario: str) -> SafetyPolicy:
        # 检查文件是否更新
        for path in glob.glob(self.policy_path.replace("*", scenario)):
            mtime = os.path.getmtime(path)
            if self._last_modified.get(path, 0) < mtime:
                self._reload_policy(path)
                self._last_modified[path] = mtime

        return self._cache.get(scenario)

    def _on_policy_change(self, event):
        # 文件变更 → 自动重新加载
        self._reload_policy(event.path)
```

#### 5.1.6 输出校验（PostCheck）

```python
class SafetyPostCheck:
    """输出安全校验"""

    def check(self, output_text: str, context: dict) -> CheckResult:
        results = []

        # Layer 1: 合规词拦截
        compliance_result = self.compliance_filter.check(output_text)
        results.append(("compliance", compliance_result))

        # Layer 2: 敏感信息二次屏蔽（模型可能返回真实卡号等）
        leak_result = self.data_leak_checker.check(output_text)
        results.append(("data_leak", leak_result))

        # Layer 3: 模型置信度校验
        confidence_result = self.confidence_monitor.check(context["llm_response"])
        results.append(("confidence", confidence_result))

        # Layer 4: 高风险操作标记（需人工确认）
        high_risk_result = self.high_risk_detector.check(output_text)
        results.append(("high_risk", high_risk_result))

        return self._aggregate_results(results)
```

---

### 5.2 审计追踪（AuditLogger）— 全链路可观测

#### 5.2.1 全链路TraceLogger

```python
class TraceLogger:
    """
    每个请求生成唯一TraceID，贯穿所有执行节点
    """

    async def log_node(self, trace_id: str, node: str, data: dict):
        """记录单个节点的输入输出"""
        record = {
            "trace_id": trace_id,
            "node": node,
            "timestamp": datetime.utcnow().isoformat(),
            "input_tokens": self._count_tokens(data.get("input", "")),
            "output_tokens": self._count_tokens(data.get("output", "")),
            "duration_ms": data.get("duration_ms", 0),
            "error": data.get("error"),
            "metadata": data.get("metadata", {})
        }
        await self._write_to_db(record)

    async def log_full_trace(self, trace_id: str) -> TraceReport:
        """生成完整链路报告"""
        records = await self._get_records_by_trace(trace_id)

        return TraceReport(
            trace_id=trace_id,
            total_duration_ms=sum(r.duration_ms for r in records),
            nodes=[r.node for r in records],
            safety_events=[r for r in records if r.node.startswith("safety_")],
            tool_calls=[r for r in records if r.node == "tool_call"],
            llm_calls=[r for r in records if r.node == "llm"],
            errors=[r for r in records if r.error]
        )
```

#### 5.2.2 OpenTelemetry集成（Tracer）

```python
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

class AgentTracer:
    """OpenTelemetry全链路埋点"""

    def __init__(self):
        self.tracer = trace.get_tracer("finagent-core")
        self.span_processor = BatchSpanProcessor(self._get_exporter())

    def start_span(self, name: str, attributes: dict):
        return self.tracer.start_as_current_span(
            name,
            attributes=attributes
        )

    async def trace_agent_execution(self, request: AgentRequest):
        with self.start_span("agent.orchestrate", {"scenario": request.scenario}):
            # 预检
            with self.start_span("safety.pre_check"):
                pre_result = await self.safety.pre_check(request.input)

            # 上下文构建
            with self.start_span("context.build"):
                context = await self.context_manager.build(request)

            # RAG检索
            with self.start_span("rag.retrieve"):
                rag_results = await self.rag.retrieve(context)

            # LLM调用
            with self.start_span("llm.call", {"model": model_name}):
                llm_response = await self.llm.call(context)

            # 后检
            with self.start_span("safety.post_check"):
                post_result = await self.safety.post_check(llm_response)

            # 审计记录
            with self.start_span("audit.log"):
                await self.audit.log_trace(request.trace_id, {
                    "pre_check": pre_result,
                    "rag_results": rag_results,
                    "llm_response": llm_response,
                    "post_check": post_result
                })
```

#### 5.2.3 合规报表生成（Reporter）

```python
class ComplianceReporter:
    """
    自动生成满足监管要求的审计报表
    """

    async def generate_monthly_report(self, year: int, month: int) -> Report:
        """生成月度审计报告"""
        records = await self._get_records(year, month)

        return Report(
            title=f"{year}年{month}月AI服务审计报告",
            summary=Summary(
                total_requests=len(records),
                blocked_requests=sum(1 for r in records if r.blocked),
                human_intervention_count=sum(1 for r in records if r.human_intervention),
                avg_response_time_ms=statistics.mean(r.duration_ms for r in records),
            ),
            safety_events=self._aggregate_safety_events(records),
            top_blocked_queries=self._top_blocked(records, limit=10),
            anomaly_alerts=self._detect_anomalies(records),
            compliance_status="符合监管要求" if self._check_compliance(records) else "需整改",
            generated_at=datetime.utcnow(),
        )

    def export_pdf(self, report: Report) -> bytes:
        """导出PDF格式（满足等保要求）"""
        pass
```

#### 5.2.4 异常行为检测（AnomalyDetector）

```python
class AnomalyDetector:
    """
    检测异常访问模式，自动告警
    """

    ANOMALY_RULES = {
        "高频访问": {"threshold": 100, "window": "1min", "severity": "warning"},
        "暴力猜解": {"threshold": 10, "window": "30s", "severity": "critical"},
        "批量数据拉取": {"threshold": 50, "window": "5min", "severity": "warning"},
        "异常时间访问": {"threshold": None, "window": "night", "severity": "info"},
    }

    async def detect(self, user_id: str) -> list[AnomalyAlert]:
        alerts = []
        for rule_name, rule_config in self.ANOMALY_RULES.items():
            count = await self._count_events(user_id, rule_config["window"])
            if rule_config["threshold"] and count > rule_config["threshold"]:
                alerts.append(AnomalyAlert(
                    user_id=user_id,
                    rule=rule_name,
                    count=count,
                    severity=rule_config["severity"],
                    timestamp=datetime.utcnow()
                ))

        if alerts:
            await self._send_alert(alerts)

        return alerts
```

---

### 5.3 RAG引擎 — 生产级知识检索

#### 5.3.1 混合检索（HybridRetriever）

```python
class HybridRetriever:
    """
    三级召回：稀疏检索 → 密集检索 → 重排序
    """

    async def retrieve(self, query: str, top_k: int = 20) -> list[RetrievalResult]:
        # Stage 1: 稀疏检索（BM25）
        bm25_results = await self.bm25.retrieve(query, top_k=50)

        # Stage 2: 密集检索（向量相似度）
        query_embedding = await self.embedding_model.encode(query)
        vector_results = await self.vector_db.search(
            query_embedding,
            top_k=50,
            filter={"status": "active"}
        )

        # Stage 3: 融合（RRF融合算法）
        fused_results = self._reciprocal_rank_fusion(
            [bm25_results, vector_results],
            k=60
        )

        # Stage 4: Cross-Encoder精排
        reranked = await self.reranker.rerank(query, fused_results[:20], top_k=5)

        # Stage 5: 业务规则加权 + 时效性衰减
        weighted = self._apply_business_rules(reranked, query)

        return weighted

    def _reciprocal_rank_fusion(self, result_lists: list, k: int = 60) -> list:
        """RRF融合算法"""
        scores = {}
        for results in result_lists:
            for rank, result in enumerate(results):
                doc_id = result.doc_id
                scores[doc_id] = scores.get(doc_id, 0) + 1 / (k + rank + 1)

        sorted_docs = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        return [self._get_doc_by_id(doc_id) for doc_id, _ in sorted_docs]
```

#### 5.3.2 Cross-Encoder精排（Reranker）

```python
class CrossEncoderReranker:
    """
    使用Cross-Encoder对候选文档进行精细排序
    """

    def __init__(self, model_name: str = "BAAI/bge-reranker-base"):
        self.model = CrossEncoder(model_name)

    async def rerank(self, query: str, candidates: list[Document], top_k: int = 5):
        pairs = [(query, doc.content) for doc in candidates]
        scores = self.model.predict(pairs)

        reranked = sorted(
            zip(candidates, scores),
            key=lambda x: x[1],
            reverse=True
        )

        return [doc for doc, score in reranked[:top_k]]
```

#### 5.3.3 知识溯源（SourceTracker）

```python
class SourceTracker:
    """
    每个答案附带来源信息：文档ID、章节、更新时间、置信度
    """

    def track(self, answer: str, rag_results: list[RetrievalResult]) -> TrackedAnswer:
        """将RAG结果与答案关联，支持答案溯源"""
        citations = []
        for result in rag_results:
            # 检查答案是否引用了该文档片段
            if self._is_cited(answer, result.content):
                citations.append(Citation(
                    doc_id=result.doc_id,
                    doc_title=result.metadata.get("title"),
                    section=result.metadata.get("section"),
                    update_time=result.metadata.get("update_time"),
                    confidence=result.score,
                    quoted_text=self._extract_quoted_text(answer, result.content)
                ))

        return TrackedAnswer(
            answer=answer,
            citations=citations,
            overall_confidence=self._compute_overall_confidence(citations)
        )
```

#### 5.3.4 知识时效性管理（FreshnessManager）

```python
class FreshnessManager:
    """
    管理知识时效性，过期知识自动预警或降权
    """

    FRESHNESS_RULES = {
        "product_info": {"expiry_days": 30, "action": "降权"},
        "policy_doc": {"expiry_days": 7, "action": "预警"},
        "user_guide": {"expiry_days": 90, "action": "降权"},
        "regulation": {"expiry_days": 1, "action": "预警"},
    }

    async def check(self, doc_id: str) -> FreshnessStatus:
        doc = await self._get_doc(doc_id)
        category = doc.metadata.get("category", "general")
        rule = self.FRESHNESS_RULES.get(category, {"expiry_days": 90})

        days_since_update = (datetime.utcnow() - doc.update_time).days

        if days_since_update > rule["expiry_days"]:
            return FreshnessStatus(
                status="expired",
                action=rule["action"],
                days_since_update=days_since_update,
                expiry_days=rule["expiry_days"],
                suggestion=f"该文档已{rule['action']}，建议更新"
            )

        # 接近过期（超过70%有效期）
        threshold = rule["expiry_days"] * 0.7
        if days_since_update > threshold:
            return FreshnessStatus(
                status="expiring_soon",
                action="预警",
                days_since_update=days_since_update,
                expiry_days=rule["expiry_days"],
                suggestion="该文档即将过期，请关注"
            )

        return FreshnessStatus(status="fresh")
```

#### 5.3.5 增量更新（IncrementalIndexer）

```python
class IncrementalIndexer:
    """
    知识库新增时无需全量重建，支持增量向量化
    """

    async def add_documents(self, documents: list[Document]):
        # 1. 增量向量化
        embeddings = await self.embedding_model.encode_batch(
            [doc.content for doc in documents]
        )

        # 2. 增量写入向量库
        await self.vector_db.add(
            ids=[doc.id for doc in documents],
            embeddings=embeddings,
            metadatas=[doc.metadata for doc in documents]
        )

        # 3. 更新索引元数据
        await self._update_index_metadata(documents)

        # 4. 触发全量重排（如有必要）
        if self._should_trigger_rebuild():
            await self._schedule_rebuild()
```

---

## 六、三场景配置对比

| 模块 | 智能客服 | 智能运营 | 智能推荐 |
|:---|:---|:---|:---|
| **Agent范式** | ReAct + 多轮状态机 | Plan-and-Execute | 大模型辅助 + 传统推荐 |
| **短期记忆** | 强（5-10轮） | 中（单任务为主） | 弱（实时推荐） |
| **长期记忆** | 中（历史工单） | 弱（任务独立） | 强（用户偏好） |
| **实体追踪** | 强（卡号/账号/交易） | 中（数据表/报表） | 弱（商品ID） |
| **RAG依赖** | 强（FAQ+业务规则） | 中（SOP+历史报告） | 弱（商品描述） |
| **安全等级** | 高（防注入+合规话术） | 中（数据权限管控） | 中（合规推荐） |
| **工具集** | 只读查询（账户/交易/FAQ） | SQL沙箱/Python/报表生成 | 画像查询/推荐API/文案生成 |
| **性能要求** | 中（<1s首字延迟） | 低（分钟级可接受） | 高（<200ms或异步） |

---

## 七、执行流程（完整链路）

```
用户输入："我的信用卡还款日是哪天？"
        │
        ▼
┌───────────────────────────────────────┐
│  1. 预检（SafetyPreCheck）             │
│     • PII脱敏（保留语义，隐藏实体）    │
│     • Prompt注入检测                   │
│     • 越狱攻击检测                     │
│     • 场景权限校验                     │
│     结果：[通过/拦截/需人工]           │
└────────────────────┬──────────────────┘
                    ▼
┌───────────────────────────────────────┐
│  2. 上下文构建（ContextManager）       │
│     • 加载短期记忆（最近5轮对话）      │
│     • 加载长期记忆（用户画像）         │
│     • RAG检索（Top5，混合召回+重排）   │
│     • 动态压缩（Token预算管理）        │
└────────────────────┬──────────────────┘
                    ▼
┌───────────────────────────────────────┐
│  3. 场景路由（ScenarioRouter）         │
│     • 加载场景配置（YAML）             │
│     • 注入Prompt模板/工具集/安全等级   │
└────────────────────┬──────────────────┘
                    ▼
┌───────────────────────────────────────┐
│  4. Agent执行（Orchestrator）           │
│     • 意图识别 → 任务分解             │
│     • 工具调用（RAG/查询/执行）        │
│     • 结果聚合                         │
│     全链路Trace埋点                    │
└────────────────────┬──────────────────┘
                    ▼
┌───────────────────────────────────────┐
│  5. 后检（SafetyPostCheck）             │
│     • 合规词拦截                       │
│     • 敏感信息二次屏蔽                 │
│     • 模型置信度校验                   │
│     • 高风险操作标记                   │
└────────────────────┬──────────────────┘
                    ▼
┌───────────────────────────────────────┐
│  6. 审计记录（TraceLogger）            │
│     • 全链路节点记录                   │
│     • 安全事件标记                     │
│     • 异常行为检测                     │
└────────────────────┬──────────────────┘
                    ▼
                返回用户
```

---

## 八、数据库Schema

### 8.1 审计日志表（audit_logs）

```sql
CREATE TABLE audit_logs (
    id TEXT PRIMARY KEY,
    trace_id TEXT NOT NULL,
    user_id TEXT,
    scenario TEXT NOT NULL,
    input_text TEXT,
    output_text TEXT,
    blocked BOOLEAN DEFAULT FALSE,
    block_reason TEXT,
    human_intervention BOOLEAN DEFAULT FALSE,
    nodes_json TEXT,  -- JSON: 各节点耗时/输入/输出
    safety_events_json TEXT,  -- JSON: 安全事件列表
    total_duration_ms INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_trace_id (trace_id),
    INDEX idx_user_id (user_id),
    INDEX idx_created_at (created_at)
);
```

### 8.2 知识库表（knowledge_base）

```sql
CREATE TABLE knowledge_base (
    id TEXT PRIMARY KEY,
    content TEXT NOT NULL,
    category TEXT,
    title TEXT,
    section TEXT,
    update_time TIMESTAMP,
    expiry_days INTEGER DEFAULT 90,
    status TEXT DEFAULT 'active',
    metadata_json TEXT,
    INDEX idx_category (category),
    INDEX idx_status (status),
    FULLTEXT INDEX idx_content (content)
);
```

### 8.3 用户记忆表（user_memories）

```sql
CREATE TABLE user_memories (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    memory_type TEXT NOT NULL,  -- 'short_term' | 'long_term' | 'entity'
    content TEXT NOT NULL,
    session_id TEXT,
    expires_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_user_id (user_id),
    INDEX idx_memory_type (memory_type),
    INDEX idx_expires_at (expires_at)
);
```

---

## 九、API接口设计

### 9.1 核心接口

| 方法 | 路径 | 说明 |
|:---|:---|:---|
| GET | `/health` | 健康检查 |
| POST | `/agent/chat` | 统一Agent对话接口 |
| POST | `/agent/switch-scenario` | 运行时切换场景 |
| GET | `/audit/traces/{trace_id}` | 查询链路详情 |
| GET | `/audit/report/{year}/{month}` | 下载月度审计报告 |
| POST | `/knowledge/add` | 添加知识条目 |
| GET | `/knowledge/search` | 搜索知识库 |
| GET | `/safety/policy/{scenario}` | 获取安全策略 |

### 9.2 请求/响应示例

```json
// POST /agent/chat
// Request
{
    "scenario": "customer_service",
    "user_id": "user_12345",
    "message": "我的信用卡还款日是哪天？",
    "session_id": "sess_abc123"
}

// Response
{
    "trace_id": "trace_20260528_001",
    "answer": "您的信用卡还款日是每月15日。如有疑问可联系客服。",
    "sources": [
        {
            "doc_id": "doc_001",
            "title": "信用卡还款规则",
            "section": "第三条",
            "confidence": 0.95
        }
    ],
    "safety": {
        "blocked": false,
        "confidence": 0.88
    },
    "trace_url": "http://localhost:6001/trace/trace_20260528_001"
}
```

---

## 十、4周落地计划

| 周次 | 目标 | 核心交付 |
|:---|:---|:---|
| **Week 1** | 跑通核心骨架 | FastAPI + LangGraph状态机 + DashScope接入 + ChromaDB RAG跑通 |
| **Week 2** | 安全与审计 | SafetyGuard多层防御 + AuditLogger全链路Trace + OpenTelemetry集成 |
| **Week 3** | 上下文工程 | 短期/长期记忆 + 实体追踪 + 上下文压缩 |
| **Week 4** | 工程化与展示 | Docker一键启动 + Arize Phoenix可视化 + Locust压测 + 场景切换演示 |

---

## 十一、风险与应对

| 风险 | 影响 | 应对措施 |
|:---|:---|:---|
| 模型幻觉导致错误回答 | 高 | 安全护栏+置信度监控+人工介入开关 |
| 知识库过期导致误导 | 中 | FreshnessManager自动预警+有效期管理 |
| 安全护栏被绕过 | 高 | 定期红蓝对抗+越狱模式库持续更新 |
| 审计日志丢失 | 高 | 异步写入+本地缓冲+定时落库 |
| 上下文窗口溢出 | 中 | ContextManager动态压缩+降级兜底 |

---

## 十二、设计确认清单

- [x] 架构分层清晰（L0-L3）
- [x] 安全护栏多层防御设计完整
- [x] 审计全链路Trace设计完整
- [x] RAG三级召回+时效性管理设计完整
- [x] 三场景配置化切换机制明确
- [x] 上下文工程四层记忆设计完整
- [x] API接口设计完整
- [x] 数据库Schema设计完整
- [x] 4周落地计划可执行