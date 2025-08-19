# Standard Library Imports
from typing import Any

# Third Party Imports
from opentelemetry import metrics
from opentelemetry.metrics import Counter

# Local Imports
from config.opentelemetry import get_meter

# Get Meter Instance
meter: metrics.Meter = get_meter()


# Login Initiated Counter
user_login_initiated_total: Counter = meter.create_counter(
    name="user.login.initiated.total",
    description="Total Number Of Successful User Logins",
    unit="1",
)


# Access Token Generated Counter
user_login_access_token_generated_total: Counter = meter.create_counter(
    name="user.login.access_token.generated.total",
    description="Total Number Of Access Tokens Generated During Login",
    unit="1",
)


# Access Token Reused Counter
user_login_access_token_reused_total: Counter = meter.create_counter(
    name="user.login.access_token.reused.total",
    description="Total Number Of Access Tokens Reused From Cache During Login",
    unit="1",
)


# Refresh Token Generated Counter
user_login_refresh_token_generated_total: Counter = meter.create_counter(
    name="user.login.refresh_token.generated.total",
    description="Total Number Of Refresh Tokens Generated During Login",
    unit="1",
)


# Refresh Token Reused Counter
user_login_refresh_token_reused_total: Counter = meter.create_counter(
    name="user.login.refresh_token.reused.total",
    description="Total Number Of Refresh Tokens Reused From Cache During Login",
    unit="1",
)


# Record Login Initiated Function
def record_login_initiated() -> None:
    """
    Record Successful Login Initiation.
    """

    # Create Labels
    labels: dict[str, Any] = {}

    # Add Counter Value
    user_login_initiated_total.add(1, labels)


# Record Access Token Generated Function
def record_access_token_generated() -> None:
    """
    Record Access Token Generation During Login.
    """

    # Create Labels
    labels: dict[str, Any] = {}

    # Add Counter Value
    user_login_access_token_generated_total.add(1, labels)


# Record Access Token Reused Function
def record_access_token_reused() -> None:
    """
    Record Access Token Reuse During Login.
    """

    # Create Labels
    labels: dict[str, Any] = {}

    # Add Counter Value
    user_login_access_token_reused_total.add(1, labels)


# Record Refresh Token Generated Function
def record_refresh_token_generated() -> None:
    """
    Record Refresh Token Generation During Login.
    """

    # Create Labels
    labels: dict[str, Any] = {}

    # Add Counter Value
    user_login_refresh_token_generated_total.add(1, labels)


# Record Refresh Token Reused Function
def record_refresh_token_reused() -> None:
    """
    Record Refresh Token Reuse During Login.
    """

    # Create Labels
    labels: dict[str, Any] = {}

    # Add Counter Value
    user_login_refresh_token_reused_total.add(1, labels)


# Exports
__all__: list[str] = [
    "record_access_token_generated",
    "record_access_token_reused",
    "record_login_initiated",
    "record_refresh_token_generated",
    "record_refresh_token_reused",
    "user_login_access_token_generated_total",
    "user_login_access_token_reused_total",
    "user_login_initiated_total",
    "user_login_refresh_token_generated_total",
    "user_login_refresh_token_reused_total",
]
