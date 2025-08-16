# Standard Library Imports
import os
from logging.config import dictConfig

# Third Party Imports
from celery import Celery
from celery.signals import setup_logging
from django.conf import settings

# Local Imports
from config.opentelemetry import configure_opentelemetry

# Set The Default Django Settings Module
os.environ.setdefault(
    key="DJANGO_SETTINGS_MODULE",
    value="config.settings",
)

# Configure OpenTelemetry Early In Celery Processes
configure_opentelemetry()

# Create Celery Application Instance
app: Celery = Celery(
    "initstack",
    broker=settings.RABBITMQ_URL,
    backend=settings.ELASTICSEARCH_URL,
)

# Load Django Settings With CELERY Namespace
app.config_from_object(
    obj="django.conf:settings",
    namespace="CELERY",
)

# Discover Tasks From Registered Apps
app.autodiscover_tasks()


# Configure Celery Logging
@setup_logging.connect
def config_loggers(*args, **kwargs) -> None:
    """Configure Celery Logging Using Django Settings.

    Args:
        *args: Variable Length Argument List.
        **kwargs: Arbitrary Keyword Arguments.

    Returns:
        None
    """

    # Configure Celery Logging
    dictConfig(settings.LOGGING)


# Exports
__all__: list[str] = ["app"]
