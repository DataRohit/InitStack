# Standard Library Imports
from unittest.mock import MagicMock
from unittest.mock import patch

# Local Imports
import apps.users.opentelemetry.views.user_username_change_confirm_metrics as uucc_metrics
from apps.users.opentelemetry.views.user_username_change_confirm_metrics import record_email_template_render_duration
from apps.users.opentelemetry.views.user_username_change_confirm_metrics import record_token_cache_mismatch
from apps.users.opentelemetry.views.user_username_change_confirm_metrics import record_tokens_revoked
from apps.users.opentelemetry.views.user_username_change_confirm_metrics import record_username_change_performed


# Test Token Cache Mismatch Recorder
def test_record_token_cache_mismatch_calls_counter() -> None:
    """
    Verify record_token_cache_mismatch Adds To Counter With Empty Labels.
    """

    # Patch Metric
    with patch.object(
        uucc_metrics,
        "user_username_change_confirm_token_cache_mismatch_total",
    ) as mismatch_total:
        # Type Hint
        mismatch_total: MagicMock

        # Call Function
        record_token_cache_mismatch()

    # Assert Call
    mismatch_total.add.assert_called_once_with(1, {})


# Test Username Change Performed Recorder
def test_record_username_change_performed_calls_counter() -> None:
    """
    Verify record_username_change_performed Adds To Counter With Empty Labels.
    """

    # Patch Metric
    with patch.object(
        uucc_metrics,
        "user_username_change_confirm_performed_total",
    ) as performed_total:
        # Type Hint
        performed_total: MagicMock

        # Call Function
        record_username_change_performed()

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
        uucc_metrics,
        "user_username_change_confirm_tokens_revoked_total",
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
    duration: float = 1.222

    # Patch Metric
    with patch.object(
        uucc_metrics,
        "user_username_change_confirm_email_template_render_duration",
    ) as render_hist:
        # Type Hint
        render_hist: MagicMock

        # Call Function
        record_email_template_render_duration(duration=duration)

    # Assert Call
    render_hist.record.assert_called_once_with(duration, {})
