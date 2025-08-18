# Third Party Imports
from django.conf import settings
from opentelemetry import metrics
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.http.metric_exporter import OTLPMetricExporter
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.boto3sqs import Boto3SQSInstrumentor
from opentelemetry.instrumentation.botocore import BotocoreInstrumentor
from opentelemetry.instrumentation.celery import CeleryInstrumentor
from opentelemetry.instrumentation.django import DjangoInstrumentor
from opentelemetry.instrumentation.logging import LoggingInstrumentor
from opentelemetry.instrumentation.pika import PikaInstrumentor
from opentelemetry.instrumentation.psycopg import PsycopgInstrumentor
from opentelemetry.instrumentation.redis import RedisInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor


# Configure OpenTelemetry
def configure_opentelemetry() -> None:
    """
    Function To Configure OpenTelemetry For The Application.
    """

    # Set The Global Flag To Prevent Double Configuration
    global _OTEL_CONFIGURED  # noqa: PLW0603

    # If The OpenTelemetry Has Already Been Configured
    if _OTEL_CONFIGURED is True:
        # Return Early
        return

    # Create Resource With Service Information
    resource: Resource = Resource.create(
        attributes={
            "service.name": settings.OTEL_SERVICE_NAME,
            "service.namespace": settings.OTEL_SERVICE_NAMESPACE,
            "deployment.environment": settings.OTEL_SERVICE_ENVIRONMENT,
            "service.version": settings.OTEL_SERVICE_VERSION,
            "service.instance.id": settings.OTEL_SERVICE_INSTANCE_ID,
        },
    )

    # Configure Tracing
    configure_tracing(resource)

    # Configure Metrics
    configure_metrics(resource)

    # Instrument Libraries
    instrument_libraries()

    # Mark As Configured
    _OTEL_CONFIGURED = True


# Configure Tracing
def configure_tracing(resource: Resource) -> None:
    """
    Configure OpenTelemetry Tracing.
    """

    # Create Tracer Provider With The Resource
    tracer_provider: TracerProvider = TracerProvider(resource=resource)

    # Create OTLP Exporter Pointing To The Collector
    otlp_trace_exporter: OTLPSpanExporter = OTLPSpanExporter(
        endpoint=f"{settings.OTEL_EXPORTER_OTLP_ENDPOINT}/v1/traces",
    )

    # Add OTLP Exporter To The Tracer Provider
    tracer_provider.add_span_processor(
        span_processor=BatchSpanProcessor(
            span_exporter=otlp_trace_exporter,
        ),
    )

    # Set The Tracer Provider
    trace.set_tracer_provider(tracer_provider=tracer_provider)


# Configure Metrics
def configure_metrics(resource: Resource) -> None:
    """
    Configure OpenTelemetry Metrics.
    """

    # Create OTLP Metrics Exporter
    otlp_metric_exporter: OTLPMetricExporter = OTLPMetricExporter(
        endpoint=f"{settings.OTEL_EXPORTER_OTLP_ENDPOINT}/v1/metrics",
    )

    # Create Periodic Exporting Metric Reader
    metric_reader = PeriodicExportingMetricReader(
        exporter=otlp_metric_exporter,
        export_interval_millis=5000,  # Export every 5 seconds
        export_timeout_millis=30000,  # 30 second timeout
    )

    # Create Meter Provider With The Resource
    meter_provider: MeterProvider = MeterProvider(
        resource=resource,
        metric_readers=[metric_reader],
    )

    # Set The Meter Provider
    metrics.set_meter_provider(meter_provider=meter_provider)


# Instrument Libraries
def instrument_libraries() -> None:
    """
    Instrument Third-Party Libraries.
    """

    # Instrument Django
    DjangoInstrumentor().instrument()

    # Instrument Other Libraries
    RequestsInstrumentor().instrument()
    CeleryInstrumentor().instrument()
    LoggingInstrumentor().instrument()
    Boto3SQSInstrumentor().instrument()
    BotocoreInstrumentor().instrument()
    PikaInstrumentor().instrument()
    PsycopgInstrumentor().instrument()
    RedisInstrumentor().instrument()


# Get Meter
def get_meter() -> metrics.Meter:
    """
    Get a meter instance for creating custom metrics.

    Returns:
        Meter: OpenTelemetry meter instance
    """

    # Get Meter
    return metrics.get_meter(
        name=settings.OTEL_SERVICE_NAME,
        version=settings.OTEL_SERVICE_VERSION,
        schema_url="https://opentelemetry.io/schemas/1.11.0",
    )


# Get Tracer
def get_tracer() -> trace.Tracer:
    """
    Get a tracer instance for creating custom spans.

    Returns:
        Tracer: OpenTelemetry tracer instance
    """

    # Get Tracer
    return trace.get_tracer(
        name=settings.OTEL_SERVICE_NAME,
        version=settings.OTEL_SERVICE_VERSION,
        schema_url="https://opentelemetry.io/schemas/1.11.0",
    )


# Module State Flag
_OTEL_CONFIGURED: bool = False

# Exports
__all__ = [
    "configure_opentelemetry",
    "get_meter",
    "get_tracer",
]
