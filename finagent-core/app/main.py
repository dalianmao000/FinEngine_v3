from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import router, set_orchestrator
from app.api.schemas import AgentChatRequest
from app.config import settings
from app.rag.knowledge_base import KnowledgeBase
from app.rag.embedding import EmbeddingClient
from app.rag.retriever import SimpleRetriever
from app.llm.client import DashScopeClient
from app.agent.memory.context_manager import ContextManager
from app.agent.safety.pre_check import SafetyPreCheck
from app.agent.safety.post_check import SafetyPostCheck
from app.agent.audit.logger import TraceLogger
from app.agent.routing import ScenarioRouter
from app.agent.orchestrator import AgentOrchestrator
import uvicorn

app = FastAPI(title="FinAgent-Core", version="1.0.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
app.include_router(router, prefix="/api/v1")

# Initialize components
kb = KnowledgeBase(settings.chroma_data_path)
kb.add_documents([{
    "id": "doc1",
    "content": "信用卡还款日是每月15日，如有问题可联系客服。",
    "metadata": {"title": "信用卡规则", "category": "product_info"}
}])

emb = EmbeddingClient()
retriever = SimpleRetriever(kb, emb)
llm = DashScopeClient(settings.dashscope_api_key, settings.dashscope_model)
context_mgr = ContextManager()
safety_pre = SafetyPreCheck()
safety_post = SafetyPostCheck()
audit = TraceLogger()
scenario_router = ScenarioRouter()
orchestrator = AgentOrchestrator(retriever, llm, context_mgr, safety_pre, safety_post, audit, scenario_router)

# Set orchestrator for routes
set_orchestrator(orchestrator)


@app.get("/api/v1/health")
async def health():
    return {"status": "ok"}


@app.post("/api/v1/agent/chat")
async def chat(request: AgentChatRequest):
    return await orchestrator.execute(request.scenario, request.user_id, request.message, request.session_id)


if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=settings.api_port, reload=True)