from typing import TypedDict, Optional, List, Dict, Any


class RiskState(TypedDict, total=False):
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