# Third Party Imports
from django.conf import settings
from opentelemetry import trace
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

    # Create Tracer Provider With The Resource
    tracer_provider: TracerProvider = TracerProvider(resource=resource)

    # Create OTLP Exporter Pointing To The Collector
    otlp_exporter: OTLPSpanExporter = OTLPSpanExporter(
        endpoint=settings.OTEL_EXPORTER_OTLP_ENDPOINT,
    )

    # Add OTLP Exporter To The Tracer Provider
    tracer_provider.add_span_processor(
        span_processor=BatchSpanProcessor(
            span_exporter=otlp_exporter,
        ),
    )

    # Set The Tracer Provider
    trace.set_tracer_provider(tracer_provider=tracer_provider)

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

    # Mark As Configured
    _OTEL_CONFIGURED = True


# Module State Flag
_OTEL_CONFIGURED: bool = False
