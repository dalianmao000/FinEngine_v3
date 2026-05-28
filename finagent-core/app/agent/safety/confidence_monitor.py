from dataclasses import dataclass
from typing import Optional


@dataclass
class ConfidenceResult:
    confidence: float
    below_threshold: bool
    suggest_human: bool
    details: dict


class ConfidenceMonitor:
    """监控模型输出置信度"""

    def __init__(self, threshold: float = 0.7):
        self.threshold = threshold

    async def check(self, response: any) -> ConfidenceResult:
        """基础实现：置信度低于阈值时建议人工介入"""
        confidence = getattr(response, "logprob_score", 1.0)

        if confidence == 1.0:
            confidence = 0.85

        return ConfidenceResult(
            confidence=confidence,
            below_threshold=confidence < self.threshold,
            suggest_human=confidence < self.threshold * 0.8,
            details={"logprob": confidence},
        )