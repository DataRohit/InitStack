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


# Deactivate Confirm Token Cache Mismatch Counter
user_deactivate_confirm_token_cache_mismatch_total: Counter = meter.create_counter(
    name="user.deactivate_confirm.token_cache.mismatch.total",
    description="Total Number Of Deactivate Confirm Cache Token Mismatches",
    unit="1",
)


# Deactivation Performed Counter
user_deactivate_confirm_deactivation_performed_total: Counter = meter.create_counter(
    name="user.deactivate_confirm.deactivation_performed.total",
    description="Total Number Of Successful User Deactivations From Confirm Flow",
    unit="1",
)


# Tokens Revoked Counter
user_deactivate_confirm_tokens_revoked_total: Counter = meter.create_counter(
    name="user.deactivate_confirm.tokens.revoked.total",
    description="Total Number Of Tokens Revoked During Deactivate Confirm",
    unit="1",
)


# Email Template Render Duration Histogram
user_deactivate_confirm_email_template_render_duration: Histogram = meter.create_histogram(
    name="user.deactivate_confirm.email_template.render.duration",
    description="Duration To Render Deactivation Success Email Template",
    unit="s",
)


# Record Token Cache Mismatch Function
def record_token_cache_mismatch() -> None:
    """
    Record Deactivation Token Cache Mismatch.
    """

    # Create Labels
    labels: dict[str, Any] = {}

    # Add Counter Value
    user_deactivate_confirm_token_cache_mismatch_total.add(1, labels)


# Record Deactivation Performed Function
def record_deactivation_performed() -> None:
    """
    Record Successful User Deactivation.
    """

    # Create Labels
    labels: dict[str, Any] = {}

    # Add Counter Value
    user_deactivate_confirm_deactivation_performed_total.add(1, labels)


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
    user_deactivate_confirm_tokens_revoked_total.add(1, labels)


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
    user_deactivate_confirm_email_template_render_duration.record(duration, labels)


# Exports
__all__: list[str] = [
    "record_deactivation_performed",
    "record_email_template_render_duration",
    "record_token_cache_mismatch",
    "record_tokens_revoked",
    "user_deactivate_confirm_deactivation_performed_total",
    "user_deactivate_confirm_email_template_render_duration",
    "user_deactivate_confirm_token_cache_mismatch_total",
    "user_deactivate_confirm_tokens_revoked_total",
]
