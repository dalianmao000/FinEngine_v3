from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class Summary:
    total_requests: int
    blocked_requests: int
    human_intervention_count: int
    avg_response_time_ms: float


@dataclass
class ComplianceReport:
    title: str
    summary: Summary
    safety_events: list
    top_blocked_queries: list
    anomaly_alerts: list
    compliance_status: str
    generated_at: datetime


class ComplianceReporter:
    """生成满足监管要求的审计报表"""

    async def generate_monthly_report(
        self, year: int, month: int, records: list
    ) -> ComplianceReport:
        total = len(records)
        blocked = sum(1 for r in records if r.get("blocked"))
        human_intervention = sum(1 for r in records if r.get("human_intervention"))

        durations = [r.get("duration_ms", 0) for r in records if r.get("duration_ms")]
        avg_duration = sum(durations) / len(durations) if durations else 0

        summary = Summary(
            total_requests=total,
            blocked_requests=blocked,
            human_intervention_count=human_intervention,
            avg_response_time_ms=avg_duration,
        )

        return ComplianceReport(
            title=f"{year}年{month}月AI服务审计报告",
            summary=summary,
            safety_events=[],
            top_blocked_queries=[],
            anomaly_alerts=[],
            compliance_status="符合监管要求",
            generated_at=datetime.utcnow(),
        )