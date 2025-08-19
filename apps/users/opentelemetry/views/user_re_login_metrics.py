# Standard Library Imports
from typing import Any

# Third Party Imports
from opentelemetry import metrics
from opentelemetry.metrics import Counter

# Local Imports
from config.opentelemetry import get_meter

# Get Meter Instance
meter: metrics.Meter = get_meter()


# Re-Login Initiated Counter
user_re_login_initiated_total: Counter = meter.create_counter(
    name="user.re_login.initiated.total",
    description="Total Number Of Successful User Re-Logins",
    unit="1",
)


# Access Token Generated Counter
user_re_login_access_token_generated_total: Counter = meter.create_counter(
    name="user.re_login.access_token.generated.total",
    description="Total Number Of Access Tokens Generated During Re-Login",
    unit="1",
)


# Record Re-Login Initiated Function
def record_re_login_initiated() -> None:
    """
    Record Successful Re-Login Initiation.
    """

    # Create Labels
    labels: dict[str, Any] = {}

    # Add Counter Value
    user_re_login_initiated_total.add(1, labels)


# Record Access Token Generated Function
def record_access_token_generated() -> None:
    """
    Record Access Token Generation During Re-Login.
    """

    # Create Labels
    labels: dict[str, Any] = {}

    # Add Counter Value
    user_re_login_access_token_generated_total.add(1, labels)


# Exports
__all__: list[str] = [
    "record_access_token_generated",
    "record_re_login_initiated",
    "user_re_login_access_token_generated_total",
    "user_re_login_initiated_total",
]
