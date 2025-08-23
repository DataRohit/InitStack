# Standard Library Imports
from unittest.mock import MagicMock
from unittest.mock import patch

# Local Imports
import apps.users.opentelemetry.views.user_me_metrics as um_metrics
from apps.users.opentelemetry.views.user_me_metrics import record_me_retrieved


# Test Me Retrieved Recorder
def test_record_me_retrieved_calls_counter() -> None:
    """
    Verify record_me_retrieved Adds To Counter With Empty Labels.
    """

    # Patch Metric
    with patch.object(
        um_metrics,
        "user_me_retrieved_total",
    ) as me_total:
        # Type Hint
        me_total: MagicMock

        # Call Function
        record_me_retrieved()

    # Assert Call
    me_total.add.assert_called_once_with(1, {})
