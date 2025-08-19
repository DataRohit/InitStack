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


# Delete Confirm Token Cache Mismatch Counter
user_delete_confirm_token_cache_mismatch_total: Counter = meter.create_counter(
    name="user.delete_confirm.token_cache.mismatch.total",
    description="Total Number Of Delete Confirm Cache Token Mismatches",
    unit="1",
)


# Deletion Performed Counter
user_delete_confirm_deletion_performed_total: Counter = meter.create_counter(
    name="user.delete_confirm.deletion_performed.total",
    description="Total Number Of Successful User Deletions From Confirm Flow",
    unit="1",
)


# Tokens Revoked Counter
user_delete_confirm_tokens_revoked_total: Counter = meter.create_counter(
    name="user.delete_confirm.tokens.revoked.total",
    description="Total Number Of Tokens Revoked During Delete Confirm",
    unit="1",
)


# Email Template Render Duration Histogram
user_delete_confirm_email_template_render_duration: Histogram = meter.create_histogram(
    name="user.delete_confirm.email_template.render.duration",
    description="Duration To Render Deletion Success Email Template",
    unit="s",
)


# Record Token Cache Mismatch Function
def record_token_cache_mismatch() -> None:
    """
    Record Deletion Token Cache Mismatch.
    """

    # Create Labels
    labels: dict[str, Any] = {}

    # Add Counter Value
    user_delete_confirm_token_cache_mismatch_total.add(1, labels)


# Record Deletion Performed Function
def record_deletion_performed() -> None:
    """
    Record Successful User Deletion.
    """

    # Create Labels
    labels: dict[str, Any] = {}

    # Add Counter Value
    user_delete_confirm_deletion_performed_total.add(1, labels)


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
    user_delete_confirm_tokens_revoked_total.add(1, labels)


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
    user_delete_confirm_email_template_render_duration.record(duration, labels)


# Exports
__all__: list[str] = [
    "record_deletion_performed",
    "record_email_template_render_duration",
    "record_token_cache_mismatch",
    "record_tokens_revoked",
    "user_delete_confirm_deletion_performed_total",
    "user_delete_confirm_email_template_render_duration",
    "user_delete_confirm_token_cache_mismatch_total",
    "user_delete_confirm_tokens_revoked_total",
]
