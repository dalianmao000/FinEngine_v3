"""Pydantic models for API requests and responses."""

from datetime import datetime
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field


class TaskStatus(str, Enum):
    """Status of an investigation task."""

    PENDING = "PENDING"
    GATHERING = "GATHERING"
    GRAPHING = "GRAPHING"
    REASONING = "REASONING"
    GENERATING = "GENERATING"
    PENDING_APPROVAL = "PENDING_APPROVAL"
    COMPLETED = "COMPLETED"


class RiskLevel(str, Enum):
    """Risk level classification."""

    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


class StartInvestigationRequest(BaseModel):
    """Request to start a new investigation."""

    target_user_id: str = Field(..., description="ID of the user to investigate")
    trigger_event: str = Field(..., description="Event that triggered the investigation")
    priority: str = Field(default="MEDIUM", description="Priority level")


class StartInvestigationResponse(BaseModel):
    """Response after starting an investigation."""

    task_id: str
    status: TaskStatus
    created_at: datetime
    estimated_completion_time: Optional[datetime] = None


class InvestigationStatusResponse(BaseModel):
    """Response with investigation status."""

    task_id: str
    status: TaskStatus
    risk_level: Optional[RiskLevel] = None
    human_approval_needed: bool = False
    created_at: datetime
    completed_at: Optional[datetime] = None


class EvidenceItem(BaseModel):
    """Evidence item in an investigation report."""

    type: str
    ref: str
    timestamp: datetime
    detail: str
    nodes: Optional[List[str]] = None


class InvestigationReport(BaseModel):
    """Investigation report response."""

    report_id: str
    task_id: str
    status: TaskStatus
    risk_level: RiskLevel
    risk_type: str
    confidence_score: float
    summary: str
    reasoning_chain: List[str]
    evidence_list: List[EvidenceItem]
    suggested_action: str
    requires_human_approval: bool
    approval_deadline: Optional[datetime] = None


class ApprovalRequest(BaseModel):
    """Request to approve an investigation."""

    approver_id: str
    comment: Optional[str] = None


class RejectRequest(BaseModel):
    """Request to reject an investigation."""

    approver_id: str
    comment: Optional[str] = None


class TraceLogEntry(BaseModel):
    """Single trace log entry."""

    timestamp: datetime
    agent: str
    action: str
    details: Optional[str] = None


class TraceResponse(BaseModel):
    """Response with trace logs."""

    task_id: str
    logs: List[TraceLogEntry]