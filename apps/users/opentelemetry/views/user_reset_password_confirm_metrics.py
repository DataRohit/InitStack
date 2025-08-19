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


# Reset Password Confirm Token Cache Mismatch Counter
user_reset_password_confirm_token_cache_mismatch_total: Counter = meter.create_counter(
    name="user.reset_password_confirm.token_cache.mismatch.total",
    description="Total Number Of Reset Password Confirm Cache Token Mismatches",
    unit="1",
)


# Password Reset Performed Counter
user_reset_password_confirm_performed_total: Counter = meter.create_counter(
    name="user.reset_password_confirm.performed.total",
    description="Total Number Of Successful Password Resets From Confirm Flow",
    unit="1",
)


# Tokens Revoked Counter
user_reset_password_confirm_tokens_revoked_total: Counter = meter.create_counter(
    name="user.reset_password_confirm.tokens.revoked.total",
    description="Total Number Of Tokens Revoked During Reset Password Confirm",
    unit="1",
)


# Email Template Render Duration Histogram
user_reset_password_confirm_email_template_render_duration: Histogram = meter.create_histogram(
    name="user.reset_password_confirm.email_template.render.duration",
    description="Duration To Render Password Reset Success Email Template",
    unit="s",
)


# Record Token Cache Mismatch Function
def record_token_cache_mismatch() -> None:
    """
    Record Password Reset Token Cache Mismatch.
    """

    # Create Labels
    labels: dict[str, Any] = {}

    # Add Counter Value
    user_reset_password_confirm_token_cache_mismatch_total.add(1, labels)


# Record Password Reset Performed Function
def record_password_reset_performed() -> None:
    """
    Record Successful Password Reset.
    """

    # Create Labels
    labels: dict[str, Any] = {}

    # Add Counter Value
    user_reset_password_confirm_performed_total.add(1, labels)


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
    user_reset_password_confirm_tokens_revoked_total.add(1, labels)


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
    user_reset_password_confirm_email_template_render_duration.record(duration, labels)


# Exports
__all__: list[str] = [
    "record_email_template_render_duration",
    "record_password_reset_performed",
    "record_token_cache_mismatch",
    "record_tokens_revoked",
    "user_reset_password_confirm_email_template_render_duration",
    "user_reset_password_confirm_performed_total",
    "user_reset_password_confirm_token_cache_mismatch_total",
    "user_reset_password_confirm_tokens_revoked_total",
]
