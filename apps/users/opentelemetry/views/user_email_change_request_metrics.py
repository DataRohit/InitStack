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


# Email Change Request Token Reused Counter
user_email_change_request_token_reused_total: Counter = meter.create_counter(
    name="user.email_change_request.token.reused.total",
    description="Total Number Of Email Change Request Tokens Reused From Cache",
    unit="1",
)


# Email Change Request Token Generated Counter
user_email_change_request_token_generated_total: Counter = meter.create_counter(
    name="user.email_change_request.token.generated.total",
    description="Total Number Of New Email Change Request Tokens Generated",
    unit="1",
)


# Email Change Request Initiated Counter
user_email_change_request_initiated_total: Counter = meter.create_counter(
    name="user.email_change_request.initiated.total",
    description="Total Number Of Successful Email Change Requests Initiated",
    unit="1",
)


# Email Template Render Duration Histogram
user_email_change_request_email_template_render_duration: Histogram = meter.create_histogram(
    name="user.email_change_request.email_template.render.duration",
    description="Duration To Render Email Change Request Email Template",
    unit="s",
)


# Record Token Reused Function
def record_token_reused() -> None:
    """
    Record Email Change Request Token Reuse.
    """

    # Create Labels
    labels: dict[str, Any] = {}

    # Add Counter Value
    user_email_change_request_token_reused_total.add(1, labels)


# Record Token Generated Function
def record_token_generated() -> None:
    """
    Record New Email Change Request Token Generation.
    """

    # Create Labels
    labels: dict[str, Any] = {}

    # Add Counter Value
    user_email_change_request_token_generated_total.add(1, labels)


# Record Request Initiated Function
def record_email_change_request_initiated() -> None:
    """
    Record Successful Email Change Request Initiation.
    """

    # Create Labels
    labels: dict[str, Any] = {}

    # Add Counter Value
    user_email_change_request_initiated_total.add(1, labels)


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
    user_email_change_request_email_template_render_duration.record(duration, labels)


# Exports
__all__: list[str] = [
    "record_email_change_request_initiated",
    "record_email_template_render_duration",
    "record_token_generated",
    "record_token_reused",
    "user_email_change_request_email_template_render_duration",
    "user_email_change_request_initiated_total",
    "user_email_change_request_token_generated_total",
    "user_email_change_request_token_reused_total",
]
