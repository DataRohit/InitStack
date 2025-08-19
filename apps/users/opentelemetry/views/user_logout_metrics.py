# Standard Library Imports
from typing import Any

# Third Party Imports
from opentelemetry import metrics
from opentelemetry.metrics import Counter

# Local Imports
from config.opentelemetry import get_meter

# Get Meter Instance
meter: metrics.Meter = get_meter()


# Logout Initiated Counter
user_logout_initiated_total: Counter = meter.create_counter(
    name="user.logout.initiated.total",
    description="Total Number Of Successful User Logouts",
    unit="1",
)


# Tokens Revoked Counter
user_logout_tokens_revoked_total: Counter = meter.create_counter(
    name="user.logout.tokens.revoked.total",
    description="Total Number Of Tokens Revoked During Logout",
    unit="1",
)


# Record Logout Initiated Function
def record_logout_initiated() -> None:
    """
    Record Successful Logout Initiation.
    """

    # Create Labels
    labels: dict[str, Any] = {}

    # Add Counter Value
    user_logout_initiated_total.add(1, labels)


# Record Tokens Revoked Function
def record_tokens_revoked(token_type: str) -> None:
    """
    Record Token Revocation During Logout.

    Args:
        token_type (str): Token Type Revoked.
    """

    # Create Labels
    labels: dict[str, Any] = {"token_type": token_type}

    # Add Counter Value
    user_logout_tokens_revoked_total.add(1, labels)


# Exports
__all__: list[str] = [
    "record_logout_initiated",
    "record_tokens_revoked",
    "user_logout_initiated_total",
    "user_logout_tokens_revoked_total",
]
