from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter
from opentelemetry.sdk.resources import Resource


class AgentTracer:
    """OpenTelemetry全链路埋点"""

    def __init__(self, service_name: str = "finagent-core"):
        resource = Resource.create({"service.name": service_name})
        provider = TracerProvider(resource=resource)
        processor = BatchSpanProcessor(ConsoleSpanExporter())
        provider.add_span_processor(processor)
        trace.set_tracer_provider(provider)
        self.tracer = trace.get_tracer(service_name)

    def start_span(self, name: str, attributes: dict = None):
        return self.tracer.start_as_current_span(
            name,
            attributes=attributes or {},
        )

    def trace_context(self, func, *args, **kwargs):
        with self.start_span(func.__name__):
            return func(*args, **kwargs)