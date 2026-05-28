from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Optional


@dataclass
class AnomalyAlert:
    user_id: str
    rule: str
    count: int
    severity: str
    timestamp: datetime


class AnomalyDetector:
    """检测异常访问模式"""

    ANOMALY_RULES = {
        "高频访问": {"threshold": 100, "window": "1min", "severity": "warning"},
        "暴力猜解": {"threshold": 10, "window": "30s", "severity": "critical"},
        "批量数据拉取": {"threshold": 50, "window": "5min", "severity": "warning"},
        "异常时间访问": {"threshold": None, "window": "night", "severity": "info"},
    }

    def __init__(self):
        self._event_counts: dict[str, list[datetime]] = {}

    async def detect(self, user_id: str) -> list[AnomalyAlert]:
        alerts = []
        now = datetime.utcnow()

        for rule_name, rule_config in self.ANOMALY_RULES.items():
            if rule_config["window"] == "night":
                if 0 <= now.hour < 6:
                    alerts.append(AnomalyAlert(
                        user_id=user_id,
                        rule=rule_name,
                        count=1,
                        severity=rule_config["severity"],
                        timestamp=now,
                    ))
                continue

            threshold = rule_config["threshold"]
            if not threshold:
                continue

            window_minutes = int(rule_config["window"].rstrip("s").rstrip("min"))
            cutoff = now - timedelta(minutes=window_minutes)

            if user_id not in self._event_counts:
                self._event_counts[user_id] = []

            self._event_counts[user_id] = [
                t for t in self._event_counts[user_id] if t > cutoff
            ]
            self._event_counts[user_id].append(now)

            count = len(self._event_counts[user_id])
            if count > threshold:
                alerts.append(AnomalyAlert(
                    user_id=user_id,
                    rule=rule_name,
                    count=count,
                    severity=rule_config["severity"],
                    timestamp=now,
                ))

        return alerts