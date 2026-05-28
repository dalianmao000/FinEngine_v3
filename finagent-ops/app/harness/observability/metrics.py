from dataclasses import dataclass
from typing import Dict
import time

@dataclass
class MetricsCollector:
    requests_total: int = 0
    cache_hits_total: int = 0
    error_total: int = 0
    _by_business_line: Dict[str, int] = None
    _by_model: Dict[str, int] = None

    def __post_init__(self):
        self._by_business_line = {}
        self._by_model = {}

    def record_request(self, business_line: str, model: str, duration_ms: int):
        self.requests_total += 1
        self._by_business_line[business_line] = self._by_business_line.get(business_line, 0) + 1
        self._by_model[model] = self._by_model.get(model, 0) + 1

    def record_cache_hit(self):
        self.cache_hits_total += 1

    def record_error(self):
        self.error_total += 1

    def get_cache_hit_rate(self) -> float:
        if self.requests_total == 0:
            return 0.0
        return self.cache_hits_total / self.requests_total

    def get_metrics_summary(self) -> dict:
        return {
            "requests_total": self.requests_total,
            "cache_hits_total": self.cache_hits_total,
            "error_total": self.error_total,
            "cache_hit_rate": self.get_cache_hit_rate(),
            "by_business_line": self._by_business_line,
            "by_model": self._by_model,
        }