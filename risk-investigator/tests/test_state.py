import pytest
from app.investigation.state import RiskState


def test_risk_state_empty():
    """Test that RiskState can be empty (total=False)."""
    state = RiskState()
    assert state == {}


def test_risk_state_full():
    """Test RiskState with all fields."""
    state: RiskState = {
        "task_id": "task-123",
        "target_user_id": "user-456",
        "trigger_event": "suspicious_transaction",
        "status": "in_progress",
        "collected_evidence": {"evidence1": "data"},
        "graph_query_result": "graph data result",
        "reasoning_process": "reasoning here",
        "risk_level": "HIGH",
        "final_report": {"report": "summary"},
        "human_approval_needed": True,
        "approval_result": "approved",
        "approver_id": "admin-001",
        "approval_comment": "Looks good",
    }
    assert state["task_id"] == "task-123"
    assert state["risk_level"] == "HIGH"
    assert state["human_approval_needed"] is True


def test_risk_state_partial():
    """Test RiskState with only some fields."""
    state: RiskState = {
        "task_id": "task-789",
        "status": "pending",
    }
    assert state["task_id"] == "task-789"
    assert state.get("risk_level") is None


def test_risk_state_typing():
    """Test that fields have correct types."""
    state: RiskState = {
        "task_id": "task-123",
        "target_user_id": "user-456",
        "trigger_event": "fraud_detection",
        "status": "completed",
        "collected_evidence": {},
        "graph_query_result": "",
        "reasoning_process": "",
        "risk_level": "LOW",
        "final_report": {},
        "human_approval_needed": False,
        "approval_result": None,
        "approver_id": None,
        "approval_comment": None,
    }
    assert isinstance(state["task_id"], str)
    assert isinstance(state["human_approval_needed"], bool)
    assert isinstance(state["collected_evidence"], dict)