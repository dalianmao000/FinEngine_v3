"""IP profiler tools for risk investigation."""

from typing import Dict, Any
from app.tools.registry import register_tool


MOCK_IP_DATA = {
    "ip_address": "203.0.113.50",
    "user_id": "user_123",
    "is_proxy": True,
    "is_vpn": True,
    "is_tor": False,
    "is_datacenter": True,
    "isp": "Example ISP",
    "org": "Example Organization",
    "country": "United States",
    "region": "California",
    "city": "San Francisco",
    "latitude": 37.7749,
    "longitude": -122.4194,
    "timezone": "America/Los_Angeles",
    "risk_score": 85,
    "risk_level": "HIGH",
    "risk_reasons": [
        "IP来自数据中心",
        "检测到代理服务器",
        "VPN使用",
        "IP地址曾在黑名单中出现",
    ],
    "first_seen": "2025-01-15T08:00:00Z",
    "last_seen": "2026-05-28T10:30:00Z",
}


@register_tool("get_ip_profile")
async def get_ip_profile(user_id: str, ip_address: str = None) -> Dict[str, Any]:
    """Get IP profile and risk analysis for a user."""
    if ip_address is None:
        ip_address = MOCK_IP_DATA["ip_address"]
    return {
        "ip_address": ip_address,
        "user_id": user_id,
        "is_proxy": MOCK_IP_DATA["is_proxy"],
        "is_vpn": MOCK_IP_DATA["is_vpn"],
        "is_tor": MOCK_IP_DATA["is_tor"],
        "is_datacenter": MOCK_IP_DATA["is_datacenter"],
        "isp": MOCK_IP_DATA["isp"],
        "org": MOCK_IP_DATA["org"],
        "country": MOCK_IP_DATA["country"],
        "region": MOCK_IP_DATA["region"],
        "city": MOCK_IP_DATA["city"],
        "latitude": MOCK_IP_DATA["latitude"],
        "longitude": MOCK_IP_DATA["longitude"],
        "timezone": MOCK_IP_DATA["timezone"],
        "risk_score": MOCK_IP_DATA["risk_score"],
        "risk_level": MOCK_IP_DATA["risk_level"],
        "risk_reasons": MOCK_IP_DATA["risk_reasons"],
        "first_seen": MOCK_IP_DATA["first_seen"],
        "last_seen": MOCK_IP_DATA["last_seen"],
    }