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


# Register Request Initiated Counter
user_register_initiated_total: Counter = meter.create_counter(
    name="user.register.initiated.total",
    description="Total Number Of Successful User Registration Requests Initiated",
    unit="1",
)


# Activation Token Generated Counter
user_register_activation_token_generated_total: Counter = meter.create_counter(
    name="user.register.activation_token.generated.total",
    description="Total Number Of Activation Tokens Generated During Registration",
    unit="1",
)


# Email Template Render Duration Histogram
user_register_email_template_render_duration: Histogram = meter.create_histogram(
    name="user.register.email_template.render.duration",
    description="Duration To Render Registration Activation Email Template",
    unit="s",
)


# Record Register Initiated Function
def record_register_initiated() -> None:
    """
    Record Successful Registration Initiation.
    """

    # Create Labels
    labels: dict[str, Any] = {}

    # Add Counter Value
    user_register_initiated_total.add(1, labels)


# Record Activation Token Generated Function
def record_activation_token_generated() -> None:
    """
    Record Activation Token Generation For Registration.
    """

    # Create Labels
    labels: dict[str, Any] = {}

    # Add Counter Value
    user_register_activation_token_generated_total.add(1, labels)


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
    user_register_email_template_render_duration.record(duration, labels)


# Exports
__all__: list[str] = [
    "record_activation_token_generated",
    "record_email_template_render_duration",
    "record_register_initiated",
    "user_register_activation_token_generated_total",
    "user_register_email_template_render_duration",
    "user_register_initiated_total",
]
