from dataclasses import dataclass
from typing import Dict
from datetime import datetime
import time

@dataclass
class CostRecord:
    business_line: str
    model_name: str
    input_tokens: int
    output_tokens: int
    cost_usd: float
    timestamp: float = time.time()

class FinOpsTracker:
    COST_PER_1K_TOKENS = {
        "qwen-72b": 0.002,
        "qwen-7b": 0.0005,
    }

    def __init__(self):
        self._records = []
        self._cost_by_business_line = {}

    def record_tokens(
        self,
        business_line: str,
        model_name: str,
        input_tokens: int,
        output_tokens: int,
        custom_cost: float = None,
    ):
        total_tokens = input_tokens + output_tokens
        rate = custom_cost or self.COST_PER_1K_TOKENS.get(model_name, 0.001)
        cost = (total_tokens / 1000) * rate

        record = CostRecord(
            business_line=business_line,
            model_name=model_name,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            cost_usd=cost,
        )
        self._records.append(record)

        self._cost_by_business_line[business_line] = (
            self._cost_by_business_line.get(business_line, 0) + cost
        )

    def get_cost(self, business_line: str) -> float:
        return self._cost_by_business_line.get(business_line, 0)

    def get_all_costs(self) -> Dict[str, float]:
        return self._cost_by_business_line.copy()

    def get_cost_report(self) -> dict:
        total_cost = sum(self._cost_by_business_line.values())
        return {
            "total_cost_usd": total_cost,
            "by_business_line": self._cost_by_business_line,
            "generated_at": datetime.utcnow().isoformat(),
        }