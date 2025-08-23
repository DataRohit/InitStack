# Standard Library Imports
from typing import Any
from unittest.mock import patch

# Local Imports
import apps.oauth.opentelemetry.views.oauth_callback_metrics as metrics_mod


# Helper: Assert Counter Add Called With Correct Args
def _assert_add_called_once_with(counter_attr: str) -> None:
    """
    Assert .add Called Once With (1, {}) On The Given Counter Attribute.
    """

    # Patch Target Counter Attribute's add
    with patch.object(getattr(metrics_mod, counter_attr), "add") as add_mock:
        # Map Attr To Recorder
        recorder_map: dict[str, Any] = {
            "oauth_callback_received_total": metrics_mod.record_callback_received,
            "oauth_callback_backend_loaded_total": metrics_mod.record_callback_backend_loaded,
            "oauth_callback_complete_success_total": metrics_mod.record_callback_complete_success,
            "oauth_callback_complete_failure_total": metrics_mod.record_callback_complete_failure,
            "oauth_callback_access_token_generated_total": metrics_mod.record_callback_access_token_generated,
            "oauth_callback_access_token_reused_total": metrics_mod.record_callback_access_token_reused,
            "oauth_callback_refresh_token_generated_total": metrics_mod.record_callback_refresh_token_generated,
            "oauth_callback_refresh_token_reused_total": metrics_mod.record_callback_refresh_token_reused,
        }

        # Invoke Recorder
        recorder_map[counter_attr]()

        # Assert
        add_mock.assert_called_once_with(1, {})


# Test: Callback Received Counter
def test_record_callback_received_increments_counter_once() -> None:
    """
    Recording Callback Received Should Add 1 With Empty Labels.
    """

    # Assert
    _assert_add_called_once_with("oauth_callback_received_total")


# Test: Backend Loaded Counter
def test_record_callback_backend_loaded_increments_counter_once() -> None:
    """
    Recording Backend Loaded Should Add 1 With Empty Labels.
    """

    # Assert
    _assert_add_called_once_with("oauth_callback_backend_loaded_total")


# Test: Callback Complete Success Counter
def test_record_callback_complete_success_increments_counter_once() -> None:
    """
    Recording Callback Complete Success Should Add 1 With Empty Labels.
    """

    # Assert
    _assert_add_called_once_with("oauth_callback_complete_success_total")


# Test: Callback Complete Failure Counter
def test_record_callback_complete_failure_increments_counter_once() -> None:
    """
    Recording Callback Complete Failure Should Add 1 With Empty Labels.
    """

    # Assert
    _assert_add_called_once_with("oauth_callback_complete_failure_total")


# Test: Access Token Generated Counter
def test_record_callback_access_token_generated_increments_counter_once() -> None:
    """
    Recording Access Token Generated Should Add 1 With Empty Labels.
    """

    # Assert
    _assert_add_called_once_with("oauth_callback_access_token_generated_total")


# Test: Access Token Reused Counter
def test_record_callback_access_token_reused_increments_counter_once() -> None:
    """
    Recording Access Token Reused Should Add 1 With Empty Labels.
    """

    # Assert
    _assert_add_called_once_with("oauth_callback_access_token_reused_total")


# Test: Refresh Token Generated Counter
def test_record_callback_refresh_token_generated_increments_counter_once() -> None:
    """
    Recording Refresh Token Generated Should Add 1 With Empty Labels.
    """

    # Assert
    _assert_add_called_once_with("oauth_callback_refresh_token_generated_total")


# Test: Refresh Token Reused Counter
def test_record_callback_refresh_token_reused_increments_counter_once() -> None:
    """
    Recording Refresh Token Reused Should Add 1 With Empty Labels.
    """

    # Assert
    _assert_add_called_once_with("oauth_callback_refresh_token_reused_total")
