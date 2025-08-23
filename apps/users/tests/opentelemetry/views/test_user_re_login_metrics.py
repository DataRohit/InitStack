# Standard Library Imports
from unittest.mock import MagicMock
from unittest.mock import patch

# Local Imports
import apps.users.opentelemetry.views.user_re_login_metrics as url_metrics
from apps.users.opentelemetry.views.user_re_login_metrics import record_access_token_generated
from apps.users.opentelemetry.views.user_re_login_metrics import record_re_login_initiated


# Test Re-Login Initiated Recorder
def test_record_re_login_initiated_calls_counter() -> None:
    """
    Verify record_re_login_initiated Adds To Counter With Empty Labels.
    """

    # Patch Metric
    with patch.object(
        url_metrics,
        "user_re_login_initiated_total",
    ) as initiated_total:
        # Type Hint
        initiated_total: MagicMock

        # Call Function
        record_re_login_initiated()

    # Assert Call
    initiated_total.add.assert_called_once_with(1, {})


# Test Access Token Generated Recorder
def test_record_access_token_generated_calls_counter() -> None:
    """
    Verify record_access_token_generated Adds To Counter With Empty Labels.
    """

    # Patch Metric
    with patch.object(
        url_metrics,
        "user_re_login_access_token_generated_total",
    ) as at_generated_total:
        # Type Hint
        at_generated_total: MagicMock

        # Call Function
        record_access_token_generated()

    # Assert Call
    at_generated_total.add.assert_called_once_with(1, {})
