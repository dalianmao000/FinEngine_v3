import uuid
from typing import Optional
from app.agent.states import AgentState, create_initial_state
from app.rag.retriever import SimpleRetriever
from app.llm.client import DashScopeClient
from app.agent.memory.context_manager import ContextManager
from app.agent.safety.pre_check import SafetyPreCheck
from app.agent.safety.post_check import SafetyPostCheck
from app.agent.audit.logger import TraceLogger
from app.agent.routing import ScenarioRouter


class AgentOrchestrator:
    """Agent调度核心"""

    def __init__(
        self,
        retriever: SimpleRetriever,
        llm_client: DashScopeClient,
        context_manager: ContextManager,
        safety_pre: SafetyPreCheck,
        safety_post: SafetyPostCheck,
        audit_logger: TraceLogger,
        scenario_router: ScenarioRouter,
    ):
        self.retriever = retriever
        self.llm = llm_client
        self.context = context_manager
        self.safety_pre = safety_pre
        self.safety_post = safety_post
        self.audit = audit_logger
        self.router = scenario_router

    async def execute(self, scenario: str, user_id: str, message: str, session_id: str = None) -> dict:
        trace_id = f"trace_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}_{uuid.uuid4().hex[:6]}"
        session_id = session_id or f"sess_{uuid.uuid4().hex[:8]}"

        state = create_initial_state(scenario, user_id, session_id, trace_id, message)

        await self.audit.log_node(trace_id, "start", {"input": message})

        # 1. 安全预检
        state = await self._run_pre_check(state)

        if state.get("blocked"):
            return self._build_blocked_response(state)

        # 2. 上下文构建 + RAG
        state = await self._build_context(state)

        # 3. 场景配置加载
        scenario_config = self.router.load_scenario(scenario)

        # 4. LLM调用
        state = await self._call_llm(state, scenario_config)

        # 5. 安全后检
        state = await self._run_post_check(state)

        if state.get("blocked"):
            return self._build_blocked_response(state)

        return self._build_success_response(state)

    async def _run_pre_check(self, state: AgentState) -> AgentState:
        await self.audit.log_node(state["trace_id"], "safety.pre_check", {"input": state["messages"][-1]["content"]})
        result = await self.safety_pre.check(state["messages"][-1]["content"], {
            "user_id": state["user_id"],
            "scenario": state["scenario"],
        })
        state["safety_result"]["pre_check"] = result
        state["blocked"] = result.blocked
        return state

    async def _build_context(self, state: AgentState) -> AgentState:
        await self.audit.log_node(state["trace_id"], "context.build", {})
        context_text = await self.context.build(
            session_id=state["session_id"],
            user_input=state["messages"][-1]["content"],
            scenario=state["scenario"],
        )
        state["context"]["full_context"] = context_text

        rag_results = await self.retriever.retrieve(state["messages"][-1]["content"])
        state["rag_results"] = rag_results
        state["context"]["rag_context"] = self._format_rag_context(rag_results)

        await self.audit.log_node(state["trace_id"], "rag.retrieve", {"results": rag_results})
        return state

    async def _call_llm(self, state: AgentState, scenario_config: dict) -> AgentState:
        await self.audit.log_node(state["trace_id"], "llm.call", {"scenario": state["scenario"]})
        prompt = self._build_prompt(state, scenario_config)
        answer = await self.llm.call(prompt)
        state["final_answer"] = answer
        state["messages"].append({"role": "assistant", "content": answer})
        return state

    async def _run_post_check(self, state: AgentState) -> AgentState:
        await self.audit.log_node(state["trace_id"], "safety.post_check", {"output": state["final_answer"]})
        result = await self.safety_post.check(state["final_answer"], {"llm_response": state.get("llm_response")})
        state["safety_result"]["post_check"] = result
        state["blocked"] = result.blocked
        return state

    def _build_prompt(self, state: AgentState, config: dict) -> str:
        system_prompt = config.get("prompt_template", "你是一个专业的AI助手。")
        rag_context = state["context"].get("rag_context", "")
        user_message = state["messages"][-1]["content"]

        prompt = f"{system_prompt}\n\n"
        if rag_context:
            prompt += f"相关知识：\n{rag_context}\n\n"
        prompt += f"用户问题：{user_message}"
        return prompt

    def _format_rag_context(self, results: list) -> str:
        if not results:
            return ""
        lines = []
        for i, r in enumerate(results, 1):
            lines.append(f"[{i}] {r['content']}")
        return "\n".join(lines)

    def _build_blocked_response(self, state: AgentState) -> dict:
        return {
            "trace_id": state["trace_id"],
            "answer": "抱歉，您的请求无法处理，请联系客服。",
            "sources": [],
            "safety": {"blocked": True, "confidence": 0.0},
            "trace_url": None,
        }

    def _build_success_response(self, state: AgentState) -> dict:
        sources = []
        for r in state.get("rag_results", []):
            sources.append({
                "doc_id": r.get("id"),
                "title": r.get("metadata", {}).get("title", ""),
                "section": r.get("metadata", {}).get("section"),
                "confidence": 1.0 - r.get("distance", 0),
            })

        return {
            "trace_id": state["trace_id"],
            "answer": state["final_answer"],
            "sources": sources,
            "safety": {
                "blocked": False,
                "confidence": state["safety_result"].get("post_check", {}).get("confidence", 1.0),
            },
            "trace_url": f"http://localhost:6001/trace/{state['trace_id']}",
        }