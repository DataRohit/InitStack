# Standard Library Imports
from unittest.mock import MagicMock
from unittest.mock import patch

# Local Imports
import apps.users.opentelemetry.views.user_register_metrics as ur_metrics
from apps.users.opentelemetry.views.user_register_metrics import record_activation_token_generated
from apps.users.opentelemetry.views.user_register_metrics import record_email_template_render_duration
from apps.users.opentelemetry.views.user_register_metrics import record_register_initiated


# Test Register Initiated Recorder
def test_record_register_initiated_calls_counter() -> None:
    """
    Verify record_register_initiated Adds To Counter With Empty Labels.
    """

    # Patch Metric
    with patch.object(
        ur_metrics,
        "user_register_initiated_total",
    ) as initiated_total:
        # Type Hint
        initiated_total: MagicMock

        # Call Function
        record_register_initiated()

    # Assert Call
    initiated_total.add.assert_called_once_with(1, {})


# Test Activation Token Generated Recorder
def test_record_activation_token_generated_calls_counter() -> None:
    """
    Verify record_activation_token_generated Adds To Counter With Empty Labels.
    """

    # Patch Metric
    with patch.object(
        ur_metrics,
        "user_register_activation_token_generated_total",
    ) as at_generated_total:
        # Type Hint
        at_generated_total: MagicMock

        # Call Function
        record_activation_token_generated()

    # Assert Call
    at_generated_total.add.assert_called_once_with(1, {})


# Test Email Template Render Duration Recorder
def test_record_email_template_render_duration_calls_histogram() -> None:
    """
    Verify record_email_template_render_duration Records Histogram With Empty Labels.
    """

    # Inputs
    duration: float = 1.234

    # Patch Metric
    with patch.object(
        ur_metrics,
        "user_register_email_template_render_duration",
    ) as render_hist:
        # Type Hint
        render_hist: MagicMock

        # Call Function
        record_email_template_render_duration(duration=duration)

    # Assert Call
    render_hist.record.assert_called_once_with(duration, {})
