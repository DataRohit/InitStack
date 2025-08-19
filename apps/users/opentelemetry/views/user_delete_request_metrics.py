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


# Delete Request Token Reused Counter
user_delete_request_token_reused_total: Counter = meter.create_counter(
    name="user.delete_request.token.reused.total",
    description="Total Number Of Delete Request Tokens Reused From Cache",
    unit="1",
)


# Delete Request Token Generated Counter
user_delete_request_token_generated_total: Counter = meter.create_counter(
    name="user.delete_request.token.generated.total",
    description="Total Number Of New Delete Request Tokens Generated",
    unit="1",
)


# Delete Request Initiated Counter
user_delete_request_initiated_total: Counter = meter.create_counter(
    name="user.delete_request.initiated.total",
    description="Total Number Of Successful Delete Requests Initiated",
    unit="1",
)


# Email Template Render Duration Histogram
user_delete_request_email_template_render_duration: Histogram = meter.create_histogram(
    name="user.delete_request.email_template.render.duration",
    description="Duration To Render Delete Request Email Template",
    unit="s",
)


# Record Token Reused Function
def record_token_reused() -> None:
    """
    Record Delete Request Token Reuse.
    """

    # Create Labels
    labels: dict[str, Any] = {}

    # Add Counter Value
    user_delete_request_token_reused_total.add(1, labels)


# Record Token Generated Function
def record_token_generated() -> None:
    """
    Record New Delete Request Token Generation.
    """

    # Create Labels
    labels: dict[str, Any] = {}

    # Add Counter Value
    user_delete_request_token_generated_total.add(1, labels)


# Record Request Initiated Function
def record_delete_request_initiated() -> None:
    """
    Record Successful Delete Request Initiation.
    """

    # Create Labels
    labels: dict[str, Any] = {}

    # Add Counter Value
    user_delete_request_initiated_total.add(1, labels)


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
    user_delete_request_email_template_render_duration.record(duration, labels)


# Exports
__all__: list[str] = [
    "record_delete_request_initiated",
    "record_email_template_render_duration",
    "record_token_generated",
    "record_token_reused",
    "user_delete_request_email_template_render_duration",
    "user_delete_request_initiated_total",
    "user_delete_request_token_generated_total",
    "user_delete_request_token_reused_total",
]
