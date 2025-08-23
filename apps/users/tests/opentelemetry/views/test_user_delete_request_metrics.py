# Standard Library Imports
from unittest.mock import MagicMock
from unittest.mock import patch

# Local Imports
import apps.users.opentelemetry.views.user_delete_request_metrics as udr_metrics
from apps.users.opentelemetry.views.user_delete_request_metrics import record_delete_request_initiated
from apps.users.opentelemetry.views.user_delete_request_metrics import record_email_template_render_duration
from apps.users.opentelemetry.views.user_delete_request_metrics import record_token_generated
from apps.users.opentelemetry.views.user_delete_request_metrics import record_token_reused


# Test Token Reused Recorder
def test_record_token_reused_calls_counter() -> None:
    """
    Verify record_token_reused Adds To Counter With Empty Labels.
    """

    # Patch Metric
    with patch.object(
        udr_metrics,
        "user_delete_request_token_reused_total",
    ) as reused_total:
        # Type Hint
        reused_total: MagicMock

        # Call Function
        record_token_reused()

    # Assert Call
    reused_total.add.assert_called_once_with(1, {})


# Test Token Generated Recorder
def test_record_token_generated_calls_counter() -> None:
    """
    Verify record_token_generated Adds To Counter With Empty Labels.
    """

    # Patch Metric
    with patch.object(
        udr_metrics,
        "user_delete_request_token_generated_total",
    ) as generated_total:
        # Type Hint
        generated_total: MagicMock

        # Call Function
        record_token_generated()

    # Assert Call
    generated_total.add.assert_called_once_with(1, {})


# Test Delete Request Initiated Recorder
def test_record_delete_request_initiated_calls_counter() -> None:
    """
    Verify record_delete_request_initiated Adds To Counter With Empty Labels.
    """

    # Patch Metric
    with patch.object(
        udr_metrics,
        "user_delete_request_initiated_total",
    ) as initiated_total:
        # Type Hint
        initiated_total: MagicMock

        # Call Function
        record_delete_request_initiated()

    # Assert Call
    initiated_total.add.assert_called_once_with(1, {})


# Test Email Template Render Duration Recorder
def test_record_email_template_render_duration_calls_histogram() -> None:
    """
    Verify record_email_template_render_duration Records Histogram With Empty Labels.
    """

    # Inputs
    duration: float = 1.234

    # Patch Metric
    with patch.object(
        udr_metrics,
        "user_delete_request_email_template_render_duration",
    ) as render_hist:
        # Type Hint
        render_hist: MagicMock

        # Call Function
        record_email_template_render_duration(duration=duration)

    # Assert Call
    render_hist.record.assert_called_once_with(duration, {})
