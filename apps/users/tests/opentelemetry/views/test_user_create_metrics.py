# Standard Library Imports
from unittest.mock import MagicMock
from unittest.mock import patch

# Local Imports
import apps.users.opentelemetry.views.user_activate_metrics as ua_metrics
from apps.users.opentelemetry.views.user_activate_metrics import record_activation_completed
from apps.users.opentelemetry.views.user_activate_metrics import record_email_template_render_duration


# Test Activation Completed Recorder
def test_record_activation_completed_calls_counter() -> None:
    """
    Verify record_activation_completed Adds To Counter With Empty Labels.
    """

    # Patch Metric
    with patch.object(ua_metrics, "user_activate_completed_total") as completed_total:
        # Type Hint
        completed_total: MagicMock

        # Call Function
        record_activation_completed()

    # Assert Call
    completed_total.add.assert_called_once_with(1, {})


# Test Email Template Render Duration Recorder
def test_record_email_template_render_duration_calls_histogram() -> None:
    """
    Verify record_email_template_render_duration Records Histogram With Empty Labels.
    """

    # Inputs
    duration: float = 0.456

    # Patch Metric
    with patch.object(
        ua_metrics,
        "user_activate_email_template_render_duration",
    ) as render_hist:
        # Type Hint
        render_hist: MagicMock

        # Call Function
        record_email_template_render_duration(duration=duration)

    # Assert Call
    render_hist.record.assert_called_once_with(duration, {})
