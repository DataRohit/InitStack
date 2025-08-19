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


# Email Change Confirm Token Cache Mismatch Counter
user_email_change_confirm_token_cache_mismatch_total: Counter = meter.create_counter(
    name="user.email_change_confirm.token_cache.mismatch.total",
    description="Total Number Of Email Change Confirm Cache Token Mismatches",
    unit="1",
)


# Email Change Performed Counter
user_email_change_confirm_performed_total: Counter = meter.create_counter(
    name="user.email_change_confirm.performed.total",
    description="Total Number Of Successful Email Changes From Confirm Flow",
    unit="1",
)


# Tokens Revoked Counter
user_email_change_confirm_tokens_revoked_total: Counter = meter.create_counter(
    name="user.email_change_confirm.tokens.revoked.total",
    description="Total Number Of Tokens Revoked During Email Change Confirm",
    unit="1",
)


# Success Email Template Render Duration Histogram
user_email_change_confirm_success_email_template_render_duration: Histogram = meter.create_histogram(
    name="user.email_change_confirm.success_email_template.render.duration",
    description="Duration To Render Email Change Success Email Template",
    unit="s",
)


# Reactivation Email Template Render Duration Histogram
user_email_change_confirm_reactivation_email_template_render_duration: Histogram = meter.create_histogram(
    name="user.email_change_confirm.reactivation_email_template.render.duration",
    description="Duration To Render Reactivation Request Email Template",
    unit="s",
)


# Record Token Cache Mismatch Function
def record_token_cache_mismatch() -> None:
    """
    Record Email Change Token Cache Mismatch.
    """

    # Create Labels
    labels: dict[str, Any] = {}

    # Add Counter Value
    user_email_change_confirm_token_cache_mismatch_total.add(1, labels)


# Record Email Change Performed Function
def record_email_change_performed() -> None:
    """
    Record Successful Email Change.
    """

    # Create Labels
    labels: dict[str, Any] = {}

    # Add Counter Value
    user_email_change_confirm_performed_total.add(1, labels)


# Record Tokens Revoked Function
def record_tokens_revoked(token_type: str) -> None:
    """
    Record Token Revocation During Flow.

    Args:
        token_type (str): Token Type Revoked.
    """

    # Create Labels
    labels: dict[str, Any] = {"token_type": token_type}

    # Add Counter Value
    user_email_change_confirm_tokens_revoked_total.add(1, labels)


# Record Success Email Template Render Duration Function
def record_success_email_template_render_duration(duration: float) -> None:
    """
    Record Success Email Template Render Duration.

    Args:
        duration (float): Duration In Seconds.
    """

    # Create Labels
    labels: dict[str, Any] = {}

    # Record Histogram Value
    user_email_change_confirm_success_email_template_render_duration.record(duration, labels)


# Record Reactivation Email Template Render Duration Function
def record_reactivation_email_template_render_duration(duration: float) -> None:
    """
    Record Reactivation Email Template Render Duration.

    Args:
        duration (float): Duration In Seconds.
    """

    # Create Labels
    labels: dict[str, Any] = {}

    # Record Histogram Value
    user_email_change_confirm_reactivation_email_template_render_duration.record(duration, labels)


# Exports
__all__: list[str] = [
    "record_email_change_performed",
    "record_reactivation_email_template_render_duration",
    "record_success_email_template_render_duration",
    "record_token_cache_mismatch",
    "record_tokens_revoked",
    "user_email_change_confirm_performed_total",
    "user_email_change_confirm_reactivation_email_template_render_duration",
    "user_email_change_confirm_success_email_template_render_duration",
    "user_email_change_confirm_token_cache_mismatch_total",
    "user_email_change_confirm_tokens_revoked_total",
]
