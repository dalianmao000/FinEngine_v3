from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class HealthResponse(BaseModel):
    status: str
    timestamp: datetime


class AgentChatRequest(BaseModel):
    scenario: str = Field(..., description="场景名称: customer_service/operations/recommendation")
    user_id: str
    message: str
    session_id: Optional[str] = None


class SourceInfo(BaseModel):
    doc_id: str
    title: str
    section: Optional[str] = None
    confidence: float


class SafetyInfo(BaseModel):
    blocked: bool
    confidence: float


class AgentChatResponse(BaseModel):
    trace_id: str
    answer: str
    sources: list[SourceInfo] = []
    safety: SafetyInfo
    trace_url: Optional[str] = None


class ScenarioSwitchRequest(BaseModel):
    scenario: str


class ScenarioSwitchResponse(BaseModel):
    success: bool
    current_scenario: str
    message: str