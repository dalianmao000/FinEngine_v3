"""Gather intel node for collecting initial evidence."""

import asyncio
from datetime import datetime
from typing import Dict, Any

from app.tools.registry import tool_registry


async def gather_intel_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """Gather intelligence by executing multiple tools concurrently.

    Args:
        state: The current risk investigation state

    Returns:
        Updated state dict with collected_evidence and status
    """
    target_user_id = state.get("target_user_id", "")
    trigger_event = state.get("trigger_event", "")

    task_transactions = asyncio.create_task(
        tool_registry.execute("get_transaction_history", user_id=target_user_id)
    )
    task_device = asyncio.create_task(
        tool_registry.execute("get_device_fingerprint", user_id=target_user_id)
    )
    task_ip = asyncio.create_task(
        tool_registry.execute("get_ip_profile", user_id=target_user_id)
    )
    task_blacklist = asyncio.create_task(
        tool_registry.execute("check_blacklist", user_id=target_user_id)
    )

    results = await asyncio.gather(
        task_transactions, task_device, task_ip, task_blacklist
    )

    collected_evidence = {
        "transaction_history": results[0],
        "device_info": results[1],
        "ip_profile": results[2],
        "blacklist_status": results[3],
        "trigger_event": trigger_event,
        "collection_timestamp": datetime.now().isoformat(),
    }

    return {
        "collected_evidence": collected_evidence,
        "status": "GATHERING",
    }