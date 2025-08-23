# Standard Library Imports
from unittest.mock import MagicMock
from unittest.mock import patch

# Local Imports
import apps.users.opentelemetry.views.user_reset_password_confirm_metrics as urpc_metrics
from apps.users.opentelemetry.views.user_reset_password_confirm_metrics import record_email_template_render_duration
from apps.users.opentelemetry.views.user_reset_password_confirm_metrics import record_password_reset_performed
from apps.users.opentelemetry.views.user_reset_password_confirm_metrics import record_token_cache_mismatch
from apps.users.opentelemetry.views.user_reset_password_confirm_metrics import record_tokens_revoked


# Test Token Cache Mismatch Recorder
def test_record_token_cache_mismatch_calls_counter() -> None:
    """
    Verify record_token_cache_mismatch Adds To Counter With Empty Labels.
    """

    # Patch Metric
    with patch.object(
        urpc_metrics,
        "user_reset_password_confirm_token_cache_mismatch_total",
    ) as mismatch_total:
        # Type Hint
        mismatch_total: MagicMock

        # Call Function
        record_token_cache_mismatch()

    # Assert Call
    mismatch_total.add.assert_called_once_with(1, {})


# Test Password Reset Performed Recorder
def test_record_password_reset_performed_calls_counter() -> None:
    """
    Verify record_password_reset_performed Adds To Counter With Empty Labels.
    """

    # Patch Metric
    with patch.object(
        urpc_metrics,
        "user_reset_password_confirm_performed_total",
    ) as performed_total:
        # Type Hint
        performed_total: MagicMock

        # Call Function
        record_password_reset_performed()

    # Assert Call
    performed_total.add.assert_called_once_with(1, {})


# Test Tokens Revoked Recorder
def test_record_tokens_revoked_calls_counter() -> None:
    """
    Verify record_tokens_revoked Adds To Counter With Token Type Label.
    """

    # Input
    token_type: str = "access"  # noqa: S105

    # Patch Metric
    with patch.object(
        urpc_metrics,
        "user_reset_password_confirm_tokens_revoked_total",
    ) as revoked_total:
        # Type Hint
        revoked_total: MagicMock

        # Call Function
        record_tokens_revoked(token_type=token_type)

    # Assert Call
    revoked_total.add.assert_called_once_with(1, {"token_type": token_type})


# Test Email Template Render Duration Recorder
def test_record_email_template_render_duration_calls_histogram() -> None:
    """
    Verify record_email_template_render_duration Records Histogram With Empty Labels.
    """

    # Inputs
    duration: float = 2.001

    # Patch Metric
    with patch.object(
        urpc_metrics,
        "user_reset_password_confirm_email_template_render_duration",
    ) as render_hist:
        # Type Hint
        render_hist: MagicMock

        # Call Function
        record_email_template_render_duration(duration=duration)

    # Assert Call
    render_hist.record.assert_called_once_with(duration, {})
