"""Report generator node for creating the final investigation report."""

import uuid
from datetime import datetime
from typing import Dict, Any

from app.safety.pii_redactor import redact_pii


async def report_generator_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """Generate the final investigation report with evidence summary.

    Args:
        state: The current risk investigation state

    Returns:
        Updated state dict with final_report, human_approval_needed, and status
    """
    collected_evidence = state.get("collected_evidence", {})
    graph_query_result = state.get("graph_query_result", "")
    final_report = state.get("final_report", {})
    risk_level = state.get("risk_level", "LOW")

    # Build evidence list from collected evidence
    evidence_list = []

    transaction_history = collected_evidence.get("transaction_history", {})
    if transaction_history:
        evidence_list.append({
            "type": "transaction_history",
            "summary": f"Found {transaction_history.get('total_count', 0)} transactions",
            "details": transaction_history,
        })

    device_info = collected_evidence.get("device_info", {})
    if device_info:
        evidence_list.append({
            "type": "device_fingerprint",
            "summary": f"Device risk level: {device_info.get('risk_level', 'UNKNOWN')}",
            "details": device_info,
        })

    ip_profile = collected_evidence.get("ip_profile", {})
    if ip_profile:
        evidence_list.append({
            "type": "ip_profile",
            "summary": f"IP risk score: {ip_profile.get('risk_score', 'UNKNOWN')}",
            "details": ip_profile,
        })

    blacklist_status = collected_evidence.get("blacklist_status", {})
    if blacklist_status:
        evidence_list.append({
            "type": "blacklist_check",
            "summary": f"Blacklisted: {blacklist_status.get('is_blacklisted', False)}",
            "details": blacklist_status,
        })

    if graph_query_result:
        evidence_list.append({
            "type": "graph_analysis",
            "summary": "Fund flow and relationship analysis completed",
            "details": graph_query_result,
        })

    # Determine suggested action based on risk level
    if risk_level == "HIGH":
        suggested_action = "freeze_account"
    elif risk_level == "MEDIUM":
        suggested_action = "flag_for_review"
    else:
        suggested_action = "approve_transaction"

    # Determine if human approval is needed
    human_approval_needed = (
        risk_level == "HIGH" or suggested_action in ["freeze_account", "block_merchant"]
    )

    # Generate report ID
    report_id = f"RPT-{datetime.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:8].upper()}"

    # Redact PII from graph_query_result before including in report
    redacted_graph_summary = redact_pii(graph_query_result[:500]) if graph_query_result else ""

    # Enrich the final report
    enriched_report = {
        "report_id": report_id,
        "generated_at": datetime.now().isoformat(),
        "risk_level": risk_level,
        "confidence": final_report.get("confidence", 0.0),
        "suggested_action": suggested_action,
        "risk_indicators": final_report.get("risk_indicators", []),
        "reasoning_summary": final_report.get("reasoning_summary", ""),
        "evidence_list": evidence_list,
        "evidence_count": len(evidence_list),
        "graph_query_summary": redacted_graph_summary,
    }

    return {
        "final_report": enriched_report,
        "human_approval_needed": human_approval_needed,
        "status": "GENERATING",
    }