# Standard Library Imports
from unittest.mock import MagicMock
from unittest.mock import patch

# Local Imports
import apps.users.opentelemetry.views.user_login_metrics as ul_metrics
from apps.users.opentelemetry.views.user_login_metrics import record_access_token_generated
from apps.users.opentelemetry.views.user_login_metrics import record_access_token_reused
from apps.users.opentelemetry.views.user_login_metrics import record_login_initiated
from apps.users.opentelemetry.views.user_login_metrics import record_refresh_token_generated
from apps.users.opentelemetry.views.user_login_metrics import record_refresh_token_reused


# Test Login Initiated Recorder
def test_record_login_initiated_calls_counter() -> None:
    """
    Verify record_login_initiated Adds To Counter With Empty Labels.
    """

    # Patch Metric
    with patch.object(
        ul_metrics,
        "user_login_initiated_total",
    ) as initiated_total:
        # Type Hint
        initiated_total: MagicMock

        # Call Function
        record_login_initiated()

    # Assert Call
    initiated_total.add.assert_called_once_with(1, {})


# Test Access Token Generated Recorder
def test_record_access_token_generated_calls_counter() -> None:
    """
    Verify record_access_token_generated Adds To Counter With Empty Labels.
    """

    # Patch Metric
    with patch.object(
        ul_metrics,
        "user_login_access_token_generated_total",
    ) as at_generated_total:
        # Type Hint
        at_generated_total: MagicMock

        # Call Function
        record_access_token_generated()

    # Assert Call
    at_generated_total.add.assert_called_once_with(1, {})


# Test Access Token Reused Recorder
def test_record_access_token_reused_calls_counter() -> None:
    """
    Verify record_access_token_reused Adds To Counter With Empty Labels.
    """

    # Patch Metric
    with patch.object(
        ul_metrics,
        "user_login_access_token_reused_total",
    ) as at_reused_total:
        # Type Hint
        at_reused_total: MagicMock

        # Call Function
        record_access_token_reused()

    # Assert Call
    at_reused_total.add.assert_called_once_with(1, {})


# Test Refresh Token Generated Recorder
def test_record_refresh_token_generated_calls_counter() -> None:
    """
    Verify record_refresh_token_generated Adds To Counter With Empty Labels.
    """

    # Patch Metric
    with patch.object(
        ul_metrics,
        "user_login_refresh_token_generated_total",
    ) as rt_generated_total:
        # Type Hint
        rt_generated_total: MagicMock

        # Call Function
        record_refresh_token_generated()

    # Assert Call
    rt_generated_total.add.assert_called_once_with(1, {})


# Test Refresh Token Reused Recorder
def test_record_refresh_token_reused_calls_counter() -> None:
    """
    Verify record_refresh_token_reused Adds To Counter With Empty Labels.
    """

    # Patch Metric
    with patch.object(
        ul_metrics,
        "user_login_refresh_token_reused_total",
    ) as rt_reused_total:
        # Type Hint
        rt_reused_total: MagicMock

        # Call Function
        record_refresh_token_reused()

    # Assert Call
    rt_reused_total.add.assert_called_once_with(1, {})
