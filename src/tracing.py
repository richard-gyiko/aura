from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import Resource, SERVICE_NAME
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor


def configure_otlp_tracing(endpoint: str = "http://localhost:4317") -> trace.TracerProvider:
    # Configure Tracing with required service name
    resource = Resource(attributes={
        SERVICE_NAME: "aura"
    })
    
    tracer_provider = TracerProvider(resource=resource)
    processor = BatchSpanProcessor(
        OTLPSpanExporter(
            endpoint=endpoint,
            insecure=True
        )
    )
    tracer_provider.add_span_processor(processor)
    trace.set_tracer_provider(tracer_provider)

    return tracer_provider
