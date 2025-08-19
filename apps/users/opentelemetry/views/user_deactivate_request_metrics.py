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


# Deactivate Request Token Reused Counter
user_deactivate_request_token_reused_total: Counter = meter.create_counter(
    name="user.deactivate_request.token.reused.total",
    description="Total Number Of Deactivate Request Tokens Reused From Cache",
    unit="1",
)


# Deactivate Request Token Generated Counter
user_deactivate_request_token_generated_total: Counter = meter.create_counter(
    name="user.deactivate_request.token.generated.total",
    description="Total Number Of New Deactivate Request Tokens Generated",
    unit="1",
)


# Deactivate Request Initiated Counter
user_deactivate_request_initiated_total: Counter = meter.create_counter(
    name="user.deactivate_request.initiated.total",
    description="Total Number Of Successful Deactivate Requests Initiated",
    unit="1",
)


# Email Template Render Duration Histogram
user_deactivate_request_email_template_render_duration: Histogram = meter.create_histogram(
    name="user.deactivate_request.email_template.render.duration",
    description="Duration To Render Deactivate Request Email Template",
    unit="s",
)


# Record Token Reused Function
def record_token_reused() -> None:
    """
    Record Deactivate Request Token Reuse.
    """

    # Create Labels
    labels: dict[str, Any] = {}

    # Add Counter Value
    user_deactivate_request_token_reused_total.add(1, labels)


# Record Token Generated Function
def record_token_generated() -> None:
    """
    Record New Deactivate Request Token Generation.
    """

    # Create Labels
    labels: dict[str, Any] = {}

    # Add Counter Value
    user_deactivate_request_token_generated_total.add(1, labels)


# Record Request Initiated Function
def record_deactivate_request_initiated() -> None:
    """
    Record Successful Deactivate Request Initiation.
    """

    # Create Labels
    labels: dict[str, Any] = {}

    # Add Counter Value
    user_deactivate_request_initiated_total.add(1, labels)


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
    user_deactivate_request_email_template_render_duration.record(duration, labels)


# Exports
__all__: list[str] = [
    "record_deactivate_request_initiated",
    "record_email_template_render_duration",
    "record_token_generated",
    "record_token_reused",
    "user_deactivate_request_email_template_render_duration",
    "user_deactivate_request_initiated_total",
    "user_deactivate_request_token_generated_total",
    "user_deactivate_request_token_reused_total",
]
