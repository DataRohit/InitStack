# Standard Library Imports
from typing import Any

# Third Party Imports
from opentelemetry import metrics
from opentelemetry.metrics import Counter

# Local Imports
from config.opentelemetry import get_meter

# Get Meter Instance
meter: metrics.Meter = get_meter()


# OAuth Callback Received Counter
oauth_callback_received_total: Counter = meter.create_counter(
    name="oauth.callback.received.total",
    description="Total Number Of OAuth Callback Requests Received",
    unit="1",
)


# Backend Loaded Counter
oauth_callback_backend_loaded_total: Counter = meter.create_counter(
    name="oauth.callback.backend.loaded.total",
    description="Total Number Of OAuth Backends Loaded In Callback",
    unit="1",
)


# Callback Complete Success Counter
oauth_callback_complete_success_total: Counter = meter.create_counter(
    name="oauth.callback.complete.success.total",
    description="Total Number Of Successful OAuth Callback Completions",
    unit="1",
)


# Callback Complete Failure Counter
oauth_callback_complete_failure_total: Counter = meter.create_counter(
    name="oauth.callback.complete.failure.total",
    description="Total Number Of Failed OAuth Callback Completions",
    unit="1",
)


# Access Token Generated Counter
oauth_callback_access_token_generated_total: Counter = meter.create_counter(
    name="oauth.callback.access_token.generated.total",
    description="Total Number Of Access Tokens Generated In OAuth Callback",
    unit="1",
)


# Access Token Reused Counter
oauth_callback_access_token_reused_total: Counter = meter.create_counter(
    name="oauth.callback.access_token.reused.total",
    description="Total Number Of Access Tokens Reused In OAuth Callback",
    unit="1",
)


# Refresh Token Generated Counter
oauth_callback_refresh_token_generated_total: Counter = meter.create_counter(
    name="oauth.callback.refresh_token.generated.total",
    description="Total Number Of Refresh Tokens Generated In OAuth Callback",
    unit="1",
)


# Refresh Token Reused Counter
oauth_callback_refresh_token_reused_total: Counter = meter.create_counter(
    name="oauth.callback.refresh_token.reused.total",
    description="Total Number Of Refresh Tokens Reused In OAuth Callback",
    unit="1",
)


# Record Callback Received Function
def record_callback_received() -> None:
    """
    Record OAuth Callback Received.
    """

    # Create Labels
    labels: dict[str, Any] = {}

    # Add Counter Value
    oauth_callback_received_total.add(1, labels)


# Record Backend Loaded Function
def record_callback_backend_loaded() -> None:
    """
    Record OAuth Backend Loaded In Callback.
    """

    # Create Labels
    labels: dict[str, Any] = {}

    # Add Counter Value
    oauth_callback_backend_loaded_total.add(1, labels)


# Record Callback Complete Success Function
def record_callback_complete_success() -> None:
    """
    Record OAuth Callback Complete Success.
    """

    # Create Labels
    labels: dict[str, Any] = {}

    # Add Counter Value
    oauth_callback_complete_success_total.add(1, labels)


# Record Callback Complete Failure Function
def record_callback_complete_failure() -> None:
    """
    Record OAuth Callback Complete Failure.
    """

    # Create Labels
    labels: dict[str, Any] = {}

    # Add Counter Value
    oauth_callback_complete_failure_total.add(1, labels)


# Record Access Token Generated Function
def record_callback_access_token_generated() -> None:
    """
    Record Access Token Generated In Callback.
    """

    # Create Labels
    labels: dict[str, Any] = {}

    # Add Counter Value
    oauth_callback_access_token_generated_total.add(1, labels)


# Record Access Token Reused Function
def record_callback_access_token_reused() -> None:
    """
    Record Access Token Reused In Callback.
    """

    # Create Labels
    labels: dict[str, Any] = {}

    # Add Counter Value
    oauth_callback_access_token_reused_total.add(1, labels)


# Record Refresh Token Generated Function
def record_callback_refresh_token_generated() -> None:
    """
    Record Refresh Token Generated In Callback.
    """

    # Create Labels
    labels: dict[str, Any] = {}

    # Add Counter Value
    oauth_callback_refresh_token_generated_total.add(1, labels)


# Record Refresh Token Reused Function
def record_callback_refresh_token_reused() -> None:
    """
    Record Refresh Token Reused In Callback.
    """

    # Create Labels
    labels: dict[str, Any] = {}

    # Add Counter Value
    oauth_callback_refresh_token_reused_total.add(1, labels)


# Exports
__all__: list[str] = [
    "oauth_callback_access_token_generated_total",
    "oauth_callback_access_token_reused_total",
    "oauth_callback_backend_loaded_total",
    "oauth_callback_complete_failure_total",
    "oauth_callback_complete_success_total",
    "oauth_callback_received_total",
    "oauth_callback_refresh_token_generated_total",
    "oauth_callback_refresh_token_reused_total",
    "record_callback_access_token_generated",
    "record_callback_access_token_reused",
    "record_callback_backend_loaded",
    "record_callback_complete_failure",
    "record_callback_complete_success",
    "record_callback_received",
    "record_callback_refresh_token_generated",
    "record_callback_refresh_token_reused",
]
