# Standard Library Imports
import logging
from collections.abc import Iterable

# Third Party Imports
import psutil
from opentelemetry import metrics as otel_metrics
from opentelemetry.metrics import CallbackOptions
from opentelemetry.metrics import Counter
from opentelemetry.metrics import Histogram
from opentelemetry.metrics import ObservableGauge
from opentelemetry.metrics import Observation

# Local Imports
from config.opentelemetry import get_meter

# Initialize Logger
logger: logging.Logger = logging.getLogger(__name__)

# Get OpenTelemetry Meter
meter: otel_metrics.Meter = get_meter()

# Create Requests Counter
health_check_requests_total: Counter = meter.create_counter(
    name="health_check_requests_total",
    unit="1",
    description="Total Number Of Health Check Requests",
)

# Create Errors Counter
health_check_errors_total: Counter = meter.create_counter(
    name="health_check_errors_total",
    unit="1",
    description="Total Number Of Health Check Errors",
)

# Create Duration Histogram
health_check_duration_ms: Histogram = meter.create_histogram(
    name="health_check_duration_ms",
    unit="ms",
    description="Health Check Request Duration In Milliseconds",
)


# Observe CPU Percent Callback
def _observe_cpu_percent(options: CallbackOptions) -> Iterable[Observation]:
    """
    Observe CPU Utilization Percentage

    Args:
        options (CallbackOptions): Callback Options Provided By SDK

    Returns:
        Iterable[Observation]: Collection Of CPU Percentage Observations
    """

    try:
        # Get CPU Percentage
        cpu_percent_value: float = psutil.cpu_percent()

        # Return Observation
        return [Observation(cpu_percent_value)]

    except psutil.Error as e:
        # Log Observation Error
        logger.exception(
            "CPU Percent Observation Failed",
            extra={"error_type": "psutil", "error": str(e)},
        )

        # Return Empty Observations
        return []


# Observe Memory Percent Callback
def _observe_memory_percent(options: CallbackOptions) -> Iterable[Observation]:
    """
    Observe Memory Utilization Percentage

    Args:
        options (CallbackOptions): Callback Options Provided By SDK

    Returns:
        Iterable[Observation]: Collection Of Memory Percentage Observations
    """

    try:
        # Get Memory Info
        memory_info = psutil.virtual_memory()

        # Get Memory Percentage
        memory_percent_value: float = float(memory_info.percent)

        # Return Observation
        return [Observation(memory_percent_value)]

    except psutil.Error as e:
        # Log Observation Error
        logger.exception(
            "Memory Percent Observation Failed",
            extra={"error_type": "psutil", "error": str(e)},
        )

        # Return Empty Observations
        return []


# Observe Disk Percent Callback
def _observe_disk_percent(options: CallbackOptions) -> Iterable[Observation]:
    """
    Observe Disk Utilization Percentage

    Args:
        options (CallbackOptions): Callback Options Provided By SDK

    Returns:
        Iterable[Observation]: Collection Of Disk Percentage Observations
    """

    try:
        # Get Disk Usage
        disk_info = psutil.disk_usage("/")

        # Get Disk Percentage
        disk_percent_value: float = float(disk_info.percent)

        # Return Observation
        return [Observation(disk_percent_value)]

    except psutil.Error as e:
        # Log Observation Error
        logger.exception(
            "Disk Percent Observation Failed",
            extra={"error_type": "psutil", "error": str(e)},
        )

        # Return Empty Observations
        return []


# Create CPU Percent Observable Gauge
system_cpu_percent: ObservableGauge = meter.create_observable_gauge(
    name="system_cpu_percent",
    callbacks=[_observe_cpu_percent],
    unit="percent",
    description="System CPU Utilization Percentage",
)

# Create Memory Percent Observable Gauge
system_memory_percent: ObservableGauge = meter.create_observable_gauge(
    name="system_memory_percent",
    callbacks=[_observe_memory_percent],
    unit="percent",
    description="System Memory Utilization Percentage",
)

# Create Disk Percent Observable Gauge
system_disk_percent: ObservableGauge = meter.create_observable_gauge(
    name="system_disk_percent",
    callbacks=[_observe_disk_percent],
    unit="percent",
    description="System Disk Utilization Percentage",
)

# Exports
__all__: list[str] = [
    "health_check_duration_ms",
    "health_check_errors_total",
    "health_check_requests_total",
    "system_cpu_percent",
    "system_disk_percent",
    "system_memory_percent",
]
