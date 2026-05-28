from fastapi import APIRouter, HTTPException
from app.api.schemas import (
    HealthResponse,
    AgentChatRequest,
    AgentChatResponse,
    ScenarioSwitchRequest,
    ScenarioSwitchResponse,
)
from datetime import datetime

router = APIRouter()

# Global orchestrator reference (will be set by main.py)
_orchestrator = None


def set_orchestrator(orch):
    global _orchestrator
    _orchestrator = orch


@router.get("/health", response_model=HealthResponse)
async def health_check():
    return HealthResponse(status="ok", timestamp=datetime.utcnow())


@router.post("/agent/chat", response_model=AgentChatResponse)
async def chat(request: AgentChatRequest):
    if _orchestrator is None:
        raise HTTPException(status_code=503, detail="Service not initialized")
    return await _orchestrator.execute(request.scenario, request.user_id, request.message, request.session_id)


@router.post("/agent/switch-scenario", response_model=ScenarioSwitchResponse)
async def switch_scenario(request: ScenarioSwitchRequest):
    if _orchestrator is None:
        raise HTTPException(status_code=503, detail="Service not initialized")
    # Could implement scenario switching logic here
    return ScenarioSwitchResponse(success=True, current_scenario=request.scenario, message="Scenario switched")