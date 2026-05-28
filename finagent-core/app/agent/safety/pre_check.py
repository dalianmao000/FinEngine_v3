from dataclasses import dataclass
from typing import Optional
import re

from app.utils.desensitizer import Desensitizer
from app.agent.safety.jailbreak_detector import JailbreakDetector
from app.agent.safety.policy_manager import SafetyPolicyManager


INJECTION_PATTERNS = [
    r"(?i)ignore\s+(previous|all|my)\s+instructions",
    r"(?i)disregard\s+(your|all)\s+(rules|policies)",
    r"(?i)you\s+are\s+now\s+(?:a\s+)?(?:different|new)",
    r"(?i)forget\s+(?:everything|all|what)\s+(?:you|we)\s+know",
    r"(?i)pretend\s+(?:you|to)\s+(?:are|be)\s+(?:not|without)",
    r"(?i)system\s*:\s*",
    r"(?i)assistant\s*:\s*",
    r"<\s*script",
    r"\{\{.*\}\}",
]


@dataclass
class CheckResult:
    blocked: bool
    risk_level: str
    details: dict
    message: Optional[str] = None


class SafetyPreCheck:
    """输入安全预检"""

    def __init__(self, policy_manager: SafetyPolicyManager = None):
        self.desensitizer = Desensitizer()
        self.jailbreak_detector = JailbreakDetector()
        self.policy_manager = policy_manager or SafetyPolicyManager()

    async def check(self, input_text: str, context: dict) -> CheckResult:
        details = {}
        max_risk = "low"

        # Layer 1: PII脱敏
        redacted_text, pii_replacements = self.desensitizer.redact(input_text)
        details["pii"] = {"replacements": pii_replacements, "redacted": redacted_text}

        # Layer 2: Prompt注入检测
        injection_matches = []
        for pattern in INJECTION_PATTERNS:
            if re.search(pattern, input_text):
                injection_matches.append(pattern)
        injection_risk = "high" if injection_matches else "low"
        details["injection"] = {"matches": injection_matches, "risk": injection_risk}
        if injection_risk == "high":
            max_risk = "high"

        # Layer 3: 越狱攻击检测
        jailbreak_result = self.jailbreak_detector.detect(input_text)
        details["jailbreak"] = jailbreak_result.__dict__
        if jailbreak_result.risk_level == "high":
            max_risk = "high"

        # Layer 4: 场景权限校验（基础实现）
        permission_risk = "low"
        details["permission"] = {"risk": permission_risk}

        # 综合判定
        blocked = max_risk == "high"

        return CheckResult(
            blocked=blocked,
            risk_level=max_risk,
            details=details,
            message="输入存在安全风险，已被拦截" if blocked else None,
        )