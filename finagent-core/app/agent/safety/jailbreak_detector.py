import re
from dataclasses import dataclass
from typing import Optional


@dataclass
class DetectionResult:
    blocked: bool
    risk_level: str
    matches: list


class JailbreakDetector:
    """检测越狱攻击模式"""

    ATTACK_PATTERNS = [
        r"现在你是",
        r"你是一个",
        r"假设你是",
        r"base64[:=]",
        r"\\x[0-9a-f]{2}",
        r"dan.*mode",
        r"developer.*mode",
        r"[​-‏]",
    ]

    def detect(self, text: str) -> DetectionResult:
        matches = []
        for pattern in self.ATTACK_PATTERNS:
            found = re.findall(pattern, text, re.IGNORECASE | re.UNICODE)
            if found:
                matches.append({"pattern": pattern, "matches": found})

        risk_level = "high" if len(matches) >= 2 else "medium" if matches else "low"
        return DetectionResult(
            blocked=len(matches) >= 2,
            risk_level=risk_level,
            matches=matches,
        )