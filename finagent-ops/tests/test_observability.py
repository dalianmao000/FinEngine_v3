from app.harness.observability.trace import TraceCollector
from app.harness.observability.metrics import MetricsCollector
from app.harness.observability.finops import FinOpsTracker

def test_trace_collector_records_span():
    collector = TraceCollector()
    span = collector.start_span("test_span")
    collector.end_span(span, {"input_tokens": 100, "output_tokens": 50})
    assert len(collector.spans) == 1

def test_metrics_collector_records_request():
    metrics = MetricsCollector()
    metrics.record_request("customer_service", "qwen-7b", 150)
    assert metrics.requests_total > 0

def test_finops_tracks_cost_by_business_line():
    finops = FinOpsTracker()
    finops.record_tokens("customer_service", "qwen-7b", 100, 50, 0.002)
    cost = finops.get_cost("customer_service")
    assert cost > 0