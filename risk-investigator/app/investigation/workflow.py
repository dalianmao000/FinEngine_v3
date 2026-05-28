"""LangGraph investigation workflow for orchestrating the four investigation nodes."""

from typing import Literal
from datetime import datetime, timezone

from langgraph.graph import StateGraph, END

from app.investigation.state import RiskState
from app.investigation.nodes import (
    gather_intel_node,
    graph_explorer_node,
    risk_reasoner_node,
    report_generator_node,
)
from app.db.database import update_investigation_task, get_investigation_task


async def human_approval_node(state: RiskState) -> dict:
    """Node that updates task status to PENDING_APPROVAL.

    Args:
        state: The current risk investigation state

    Returns:
        Updated state dict with status PENDING_APPROVAL
    """
    task_id = state.get("task_id")
    risk_level = state.get("risk_level", "UNKNOWN")
    final_report_json = state.get("final_report")

    if task_id:
        await update_investigation_task(
            task_id,
            {
                "status": "PENDING_APPROVAL",
                "risk_level": risk_level,
                "final_report_json": final_report_json,
                "human_approval_needed": True,
            },
        )

    return {"status": "PENDING_APPROVAL"}


async def end_node(state: RiskState) -> dict:
    """Node that marks task as COMPLETED.

    Args:
        state: The current risk investigation state

    Returns:
        Updated state dict with status COMPLETED
    """
    task_id = state.get("task_id")
    risk_level = state.get("risk_level", "UNKNOWN")
    final_report_json = state.get("final_report")

    if task_id:
        await update_investigation_task(
            task_id,
            {
                "status": "COMPLETED",
                "risk_level": risk_level,
                "final_report_json": final_report_json,
                "human_approval_needed": False,
                "completed_at": datetime.now(timezone.utc),
            },
        )

    return {
        "status": "COMPLETED",
        "completed_at": datetime.now(timezone.utc).isoformat(),
    }


def route_by_risk_level(state: RiskState) -> Literal["human_approval", "end"]:
    """Route based on whether human approval is needed.

    Args:
        state: The current risk investigation state

    Returns:
        "human_approval" if approval is needed, "end" otherwise
    """
    if state.get("human_approval_needed"):
        return "human_approval"
    return "end"


async def complete_investigation_with_approval(
    task_id: str,
    approver_id: str,
    comment: str,
    action: str,
) -> dict:
    """Handle approval or rejection of a high-risk investigation.

    Args:
        task_id: The investigation task ID
        approver_id: ID of the approver
        comment: Approval/rejection comment
        action: Either "approve" or "reject"

    Returns:
        Updated task dictionary
    """
    approval_result = "APPROVED" if action == "approve" else "REJECTED"

    update_data = {
        "status": "COMPLETED",
        "approval_result": approval_result,
        "approver_id": approver_id,
        "approval_comment": comment,
        "completed_at": datetime.now(timezone.utc),
    }

    result = await update_investigation_task(task_id, update_data)
    return result


def build_investigation_graph():
    """Build and compile the investigation workflow graph.

    Returns:
        Compiled LangGraph workflow
    """
    workflow = StateGraph(RiskState)

    # Add nodes
    workflow.add_node("gather_intel", gather_intel_node)
    workflow.add_node("graph_explorer", graph_explorer_node)
    workflow.add_node("risk_reasoner", risk_reasoner_node)
    workflow.add_node("report_generator", report_generator_node)
    workflow.add_node("human_approval", human_approval_node)
    workflow.add_node("end_node", end_node)

    # Set entry point
    workflow.set_entry_point("gather_intel")

    # Add sequential edges
    workflow.add_edge("gather_intel", "graph_explorer")
    workflow.add_edge("graph_explorer", "risk_reasoner")
    workflow.add_edge("risk_reasoner", "report_generator")

    # Conditional edge from report_generator based on risk level
    workflow.add_conditional_edges(
        "report_generator",
        route_by_risk_level,
        {
            "human_approval": "human_approval",
            "end": "end_node",
        },
    )

    # Edge from human_approval to end_node
    workflow.add_edge("human_approval", "end_node")

    return workflow.compile()