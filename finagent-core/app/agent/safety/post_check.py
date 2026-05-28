from dataclasses import dataclass
from typing import Optional

from app.agent.safety.confidence_monitor import ConfidenceMonitor
from app.utils.compliance import ComplianceChecker
from app.utils.desensitizer import Desensitizer


@dataclass
class CheckResult:
    blocked: bool
    risk_level: str
    details: dict
    message: Optional[str] = None


class SafetyPostCheck:
    """输出安全校验"""

    def __init__(
        self,
        compliance_checker: ComplianceChecker = None,
        confidence_monitor: ConfidenceMonitor = None,
    ):
        self.compliance = compliance_checker or ComplianceChecker()
        self.confidence = confidence_monitor or ConfidenceMonitor()
        self.desensitizer = Desensitizer()

    async def check(self, output_text: str, context: dict) -> CheckResult:
        details = {}
        max_risk = "low"

        # Layer 1: 合规词拦截
        has_compliance_issue, found_words = self.compliance.check(output_text)
        if has_compliance_issue:
            max_risk = "high"
        details["compliance"] = {"found_words": found_words, "risk": "high" if has_compliance_issue else "low"}

        # Layer 2: 敏感信息二次屏蔽
        _, pii_leaks = self.desensitizer.redact(output_text)
        has_leak = len(pii_leaks) > 0
        if has_leak:
            max_risk = "high"
        details["data_leak"] = {"leaks": pii_leaks, "risk": "high" if has_leak else "low"}

        # Layer 3: 置信度校验
        llm_response = context.get("llm_response")
        if llm_response:
            conf_result = await self.confidence.check(llm_response)
            details["confidence"] = conf_result.__dict__
            if conf_result.suggest_human:
                max_risk = "medium"

        return CheckResult(
            blocked=max_risk == "high",
            risk_level=max_risk,
            details=details,
        )