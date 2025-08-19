# Standard Library Imports
from typing import Any

# Third Party Imports
from opentelemetry import metrics
from opentelemetry.metrics import Counter

# Local Imports
from config.opentelemetry import get_meter

# Get Meter Instance
meter: metrics.Meter = get_meter()


# Me Retrieved Counter
user_me_retrieved_total: Counter = meter.create_counter(
    name="user.me.retrieved.total",
    description="Total Number Of Successful User Me Retrievals",
    unit="1",
)


# Record Me Retrieved Function
def record_me_retrieved() -> None:
    """
    Record Successful Retrieval Of Current User Info.
    """

    # Create Labels
    labels: dict[str, Any] = {}

    # Add Counter Value
    user_me_retrieved_total.add(1, labels)


# Exports
__all__: list[str] = [
    "record_me_retrieved",
    "user_me_retrieved_total",
]
