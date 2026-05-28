from typing import TypedDict, Optional, List, Dict, Any


# Define explicitly allowed keys to prevent state pollution via dict coercion
RISK_STATE_KEYS = frozenset([
    "task_id",
    "target_user_id",
    "trigger_event",
    "status",
    "collected_evidence",
    "graph_query_result",
    "reasoning_process",
    "risk_level",
    "final_report",
    "human_approval_needed",
    "approval_result",
    "approver_id",
    "approval_comment",
])


def _validate_state_keys(state: Dict[str, Any]) -> Dict[str, Any]:
    """Filter state to only allowed keys, preventing injection attacks."""
    return {k: v for k, v in state.items() if k in RISK_STATE_KEYS}


class RiskState(TypedDict, total=False):
    """TypedDict for risk investigation workflow state.

    Note: total=False allows optional fields, but we validate
    incoming states to prevent key injection attacks.
    """
    task_id: str
    target_user_id: str
    trigger_event: str
    status: str
    collected_evidence: Dict[str, Any]
    graph_query_result: str
    reasoning_process: str
    risk_level: str
    final_report: Dict[str, Any]
    human_approval_needed: bool
    approval_result: Optional[str]
    approver_id: Optional[str]
    approval_comment: Optional[str]