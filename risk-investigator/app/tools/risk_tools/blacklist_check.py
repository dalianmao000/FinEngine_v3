"""Blacklist check tools for risk investigation."""

from typing import Dict, Any, List
from app.tools.registry import register_tool


BLACKLISTED_USERS = {"user_999", "user_888"}

BLACKLISTED_IPS = {"203.0.113.1", "198.51.100.1"}

BLACKLISTED_DEVICES = {"DEV_999", "DEV_888"}

BLACKLIST_RECORDS = {
    "user_999": {
        "user_id": "user_999",
        "reason": "涉嫌欺诈",
        "listed_at": "2026-01-15T08:00:00Z",
        "listed_by": "system",
    },
    "user_888": {
        "user_id": "user_888",
        "reason": "账户被盗用",
        "listed_at": "2026-03-20T14:30:00Z",
        "listed_by": "manual_review",
    },
}


@register_tool("check_blacklist")
async def check_blacklist(
    user_id: str = None,
    ip_address: str = None,
    device_id: str = None,
) -> Dict[str, Any]:
    """Check if user, IP or device is in blacklist."""
    results = {
        "user_id": user_id,
        "ip_address": ip_address,
        "device_id": device_id,
        "is_blacklisted": False,
        "blacklist_type": None,
        "details": None,
    }

    if user_id and user_id in BLACKLISTED_USERS:
        results["is_blacklisted"] = True
        results["blacklist_type"] = "user"
        results["details"] = BLACKLIST_RECORDS.get(user_id)
        return results

    if ip_address and ip_address in BLACKLISTED_IPS:
        results["is_blacklisted"] = True
        results["blacklist_type"] = "ip"
        results["details"] = {"ip_address": ip_address, "reason": "IP黑名单"}
        return results

    if device_id and device_id in BLACKLISTED_DEVICES:
        results["is_blacklisted"] = True
        results["blacklist_type"] = "device"
        results["details"] = {"device_id": device_id, "reason": "设备黑名单"}
        return results

    return results