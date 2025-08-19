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


# Reset Password Request Token Reused Counter
user_reset_password_request_token_reused_total: Counter = meter.create_counter(
    name="user.reset_password_request.token.reused.total",
    description="Total Number Of Reset Password Request Tokens Reused From Cache",
    unit="1",
)


# Reset Password Request Token Generated Counter
user_reset_password_request_token_generated_total: Counter = meter.create_counter(
    name="user.reset_password_request.token.generated.total",
    description="Total Number Of New Reset Password Request Tokens Generated",
    unit="1",
)


# Reset Password Request Initiated Counter
user_reset_password_request_initiated_total: Counter = meter.create_counter(
    name="user.reset_password_request.initiated.total",
    description="Total Number Of Successful Reset Password Requests Initiated",
    unit="1",
)


# Email Template Render Duration Histogram
user_reset_password_request_email_template_render_duration: Histogram = meter.create_histogram(
    name="user.reset_password_request.email_template.render.duration",
    description="Duration To Render Reset Password Request Email Template",
    unit="s",
)


# Record Token Reused Function
def record_token_reused() -> None:
    """
    Record Reset Password Request Token Reuse.
    """

    # Create Labels
    labels: dict[str, Any] = {}

    # Add Counter Value
    user_reset_password_request_token_reused_total.add(1, labels)


# Record Token Generated Function
def record_token_generated() -> None:
    """
    Record New Reset Password Request Token Generation.
    """

    # Create Labels
    labels: dict[str, Any] = {}

    # Add Counter Value
    user_reset_password_request_token_generated_total.add(1, labels)


# Record Request Initiated Function
def record_reset_password_request_initiated() -> None:
    """
    Record Successful Reset Password Request Initiation.
    """

    # Create Labels
    labels: dict[str, Any] = {}

    # Add Counter Value
    user_reset_password_request_initiated_total.add(1, labels)


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
    user_reset_password_request_email_template_render_duration.record(duration, labels)


# Exports
__all__: list[str] = [
    "record_email_template_render_duration",
    "record_reset_password_request_initiated",
    "record_token_generated",
    "record_token_reused",
    "user_reset_password_request_email_template_render_duration",
    "user_reset_password_request_initiated_total",
    "user_reset_password_request_token_generated_total",
    "user_reset_password_request_token_reused_total",
]
