# Standard Library Imports
from typing import Any

# Third Party Imports
from opentelemetry import metrics
from opentelemetry.metrics import Counter
from opentelemetry.metrics import Histogram

# Local Imports
from config.opentelemetry import get_meter

# Get Meter Instance
meter: metrics.Meter = get_meter()


# Activation Completed Counter
user_activate_completed_total: Counter = meter.create_counter(
    name="user.activate.completed.total",
    description="Total Number Of Successful User Activations Completed",
    unit="1",
)


# Email Template Render Duration Histogram
user_activate_email_template_render_duration: Histogram = meter.create_histogram(
    name="user.activate.email_template.render.duration",
    description="Duration To Render Activation Welcome Email Template",
    unit="s",
)


# Record Activation Completed Function
def record_activation_completed() -> None:
    """
    Record Successful User Activation Completion.
    """

    # Create Labels
    labels: dict[str, Any] = {}

    # Add Counter Value
    user_activate_completed_total.add(1, labels)


# Record Email Template Render Duration Function
def record_email_template_render_duration(duration: float) -> None:
    """
    Record Email Template Render Duration.

    Args:
        duration (float): Duration In Seconds.
    """

    # Create Labels
    labels: dict[str, Any] = {}

    # Record Histogram Value
    user_activate_email_template_render_duration.record(duration, labels)


# Exports
__all__: list[str] = [
    "record_activation_completed",
    "record_email_template_render_duration",
    "user_activate_completed_total",
    "user_activate_email_template_render_duration",
]
