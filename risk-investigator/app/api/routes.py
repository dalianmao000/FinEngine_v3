"""API routes for investigation endpoints."""

from datetime import datetime, timedelta
from typing import Optional
import uuid

from fastapi import APIRouter, HTTPException

from app.api.schemas import (
    StartInvestigationRequest,
    StartInvestigationResponse,
    InvestigationStatusResponse,
    InvestigationReport,
    ApprovalRequest,
    RejectRequest,
    TraceResponse,
    TraceLogEntry,
    TaskStatus,
    RiskLevel,
    EvidenceItem,
)

router = APIRouter(prefix="/investigation", tags=["investigation"])

# In-memory placeholder storage
_task_store: dict = {}


@router.post("/start", response_model=StartInvestigationResponse)
async def start_investigation(request: StartInvestigationRequest):
    """Start a new investigation task."""
    task_id = str(uuid.uuid4())
    now = datetime.utcnow()
    _task_store[task_id] = {
        "task_id": task_id,
        "status": TaskStatus.PENDING,
        "target_user_id": request.target_user_id,
        "trigger_event": request.trigger_event,
        "priority": request.priority,
        "created_at": now,
        "risk_level": None,
        "human_approval_needed": False,
        "completed_at": None,
    }
    return StartInvestigationResponse(
        task_id=task_id,
        status=TaskStatus.PENDING,
        created_at=now,
        estimated_completion_time=now + timedelta(minutes=10),
    )


@router.get("/{task_id}/status", response_model=InvestigationStatusResponse)
async def get_investigation_status(task_id: str):
    """Get the status of an investigation task."""
    task = _task_store.get(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return InvestigationStatusResponse(
        task_id=task["task_id"],
        status=task["status"],
        risk_level=task.get("risk_level"),
        human_approval_needed=task.get("human_approval_needed", False),
        created_at=task["created_at"],
        completed_at=task.get("completed_at"),
    )


@router.get("/{task_id}/report", response_model=InvestigationReport)
async def get_investigation_report(task_id: str):
    """Get the investigation report."""
    task = _task_store.get(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    if task["status"] != TaskStatus.COMPLETED:
        raise HTTPException(status_code=400, detail="Report not available yet")
    return InvestigationReport(
        report_id=str(uuid.uuid4()),
        task_id=task_id,
        status=task["status"],
        risk_level=task.get("risk_level", RiskLevel.MEDIUM),
        risk_type="placeholder",
        confidence_score=0.0,
        summary="Placeholder report - implementation pending",
        reasoning_chain=[],
        evidence_list=[],
        suggested_action="pending",
        requires_human_approval=task.get("human_approval_needed", False),
    )


@router.post("/{task_id}/approve")
async def approve_investigation(task_id: str, request: ApprovalRequest):
    """Approve an investigation task."""
    task = _task_store.get(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return {"message": "Investigation approved", "task_id": task_id}


@router.post("/{task_id}/reject")
async def reject_investigation(task_id: str, request: RejectRequest):
    """Reject an investigation task."""
    task = _task_store.get(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return {"message": "Investigation rejected", "task_id": task_id}


@router.get("/{task_id}/trace", response_model=TraceResponse)
async def get_trace_logs(task_id: str):
    """Get trace logs for an investigation task."""
    task = _task_store.get(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return TraceResponse(
        task_id=task_id,
        logs=[
            TraceLogEntry(
                timestamp=task["created_at"],
                agent="system",
                action="task_created",
                details=f"Investigation started for user {task['target_user_id']}",
            )
        ],
    )