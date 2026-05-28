import uuid
import time
from dataclasses import dataclass, field
from typing import Dict, Any, Optional

@dataclass
class Span:
    trace_id: str
    span_id: str
    name: str
    span_type: str
    start_time: float
    end_time: Optional[float] = None
    attributes: Dict[str, Any] = field(default_factory=dict)

class TraceCollector:
    def __init__(self):
        self.spans = []

    def start_span(self, name: str, span_type: str = "gateway", attributes: Optional[Dict] = None) -> Span:
        span = Span(
            trace_id=str(uuid.uuid4()),
            span_id=str(uuid.uuid4()),
            name=name,
            span_type=span_type,
            start_time=time.time(),
            attributes=attributes or {},
        )
        self.spans.append(span)
        return span

    def end_span(self, span: Span, result: Optional[Dict] = None):
        span.end_time = time.time()
        if result:
            span.attributes.update(result)

    def get_traces(self, limit: int = 100) -> list:
        return self.spans[-limit:]

    def clear(self):
        self.spans = []