"""Device fingerprint tools for risk investigation."""

from typing import Dict, Any
from app.tools.registry import register_tool


MOCK_DEVICE_INFO = {
    "device_id": "DEV_123456",
    "user_id": "user_123",
    "device_type": "mobile",
    "os": "iOS 17.5",
    "browser": "Safari",
    "ip_address": "192.168.1.100",
    "location": {
        "country": "China",
        "region": "Beijing",
        "city": "Beijing",
        "latitude": 39.9042,
        "longitude": 116.4074,
    },
    "risk_level": "HIGH",
    "risk_factors": [
        "使用代理服务器",
        "IP地址位于高风险地区",
        "设备指纹异常",
    ],
    "is_rooted": False,
    "is_emulator": False,
    "last_seen": "2026-05-28T10:30:00Z",
}


@register_tool("get_device_fingerprint")
async def get_device_fingerprint(user_id: str, device_id: str = None) -> Dict[str, Any]:
    """Get device fingerprint information for a user."""
    if device_id is None:
        device_id = f"DEV_{user_id.split('_')[1]}"
    return {
        "user_id": user_id,
        "device_id": device_id,
        "device_type": MOCK_DEVICE_INFO["device_type"],
        "os": MOCK_DEVICE_INFO["os"],
        "browser": MOCK_DEVICE_INFO["browser"],
        "ip_address": MOCK_DEVICE_INFO["ip_address"],
        "location": MOCK_DEVICE_INFO["location"],
        "risk_level": MOCK_DEVICE_INFO["risk_level"],
        "risk_factors": MOCK_DEVICE_INFO["risk_factors"],
        "is_rooted": MOCK_DEVICE_INFO["is_rooted"],
        "is_emulator": MOCK_DEVICE_INFO["is_emulator"],
        "last_seen": MOCK_DEVICE_INFO["last_seen"],
    }