"""Risk reasoner node for analyzing evidence and determining risk level."""

from typing import Dict, Any


async def risk_reasoner_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """Analyze collected evidence and graph query results to determine risk level.

    Args:
        state: The current risk investigation state

    Returns:
        Updated state dict with risk_level, reasoning_process, final_report, and status
    """
    collected_evidence = state.get("collected_evidence", {})
    graph_query_result = state.get("graph_query_result", "")

    risk_indicators = []

    # Check device risk level
    device_info = collected_evidence.get("device_info", {})
    if device_info.get("risk_level") == "HIGH":
        risk_indicators.append("device_info.risk_level == HIGH")

    # Check blacklist status
    blacklist_status = collected_evidence.get("blacklist_status", {})
    if blacklist_status.get("is_blacklisted") is True:
        risk_indicators.append("blacklist_status.in_blacklist == True")

    # Check for fund flow patterns
    if "资金回流" in graph_query_result:
        risk_indicators.append("资金回流 detected in graph query")

    # Check for pyramid scheme indicators
    if "传销" in graph_query_result:
        risk_indicators.append("传销 detected in graph query")

    # Determine risk level based on indicators
    indicator_count = len(risk_indicators)

    if indicator_count >= 3:
        risk_level = "HIGH"
        confidence = 0.92
    elif indicator_count >= 1:
        risk_level = "MEDIUM"
        confidence = 0.65
    else:
        risk_level = "LOW"
        confidence = 0.95

    reasoning_process = f"""
Risk Analysis Summary:
- Indicators found: {indicator_count}
- Indicator details: {risk_indicators}
- Risk level: {risk_level}
- Confidence: {confidence}

Evidence Summary:
- Device risk: {device_info.get('risk_level', 'UNKNOWN')}
- Blacklist status: {blacklist_status.get('is_blacklisted', False)}
- Has fund回流 pattern: {'资金回流' in graph_query_result}
- Has pyramid scheme pattern: {'传销' in graph_query_result}
""".strip()

    final_report = {
        "risk_level": risk_level,
        "confidence": confidence,
        "risk_indicators": risk_indicators,
        "indicator_count": indicator_count,
        "reasoning_summary": reasoning_process,
    }

    return {
        "risk_level": risk_level,
        "reasoning_process": reasoning_process,
        "final_report": final_report,
        "status": "REASONING",
    }