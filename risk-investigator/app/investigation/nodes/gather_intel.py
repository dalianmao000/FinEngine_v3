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

    async with asyncio.TaskGroup() as tg:
        task_transactions = tg.create_task(
            tool_registry.execute("get_transaction_history", user_id=target_user_id)
        )
        task_device = tg.create_task(
            tool_registry.execute("get_device_fingerprint", user_id=target_user_id)
        )
        task_ip = tg.create_task(
            tool_registry.execute("get_ip_profile", user_id=target_user_id)
        )
        task_blacklist = tg.create_task(
            tool_registry.execute("check_blacklist", user_id=target_user_id)
        )

    collected_evidence = {
        "transaction_history": task_transactions.result(),
        "device_info": task_device.result(),
        "ip_profile": task_ip.result(),
        "blacklist_status": task_blacklist.result(),
        "trigger_event": trigger_event,
        "collection_timestamp": datetime.now().isoformat(),
    }

    return {
        "collected_evidence": collected_evidence,
        "status": "GATHERING",
    }