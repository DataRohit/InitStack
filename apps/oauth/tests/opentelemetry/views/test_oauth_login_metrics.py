# Standard Library Imports
from typing import Any
from unittest.mock import patch

# Local Imports
import apps.oauth.opentelemetry.views.oauth_login_metrics as metrics_mod


# Helper: Assert Counter Add Called With Correct Args
def _assert_add_called_once_with(counter_attr: str) -> None:
    """
    Assert .add Called Once With (1, {}) On The Given Counter Attribute.
    """

    # Patch Target Counter Attribute's add
    with patch.object(getattr(metrics_mod, counter_attr), "add") as add_mock:
        # Map Attr To Recorder
        recorder_map: dict[str, Any] = {
            "oauth_login_initiated_total": metrics_mod.record_oauth_login_initiated,
            "oauth_login_redirect_uri_built_total": metrics_mod.record_redirect_uri_built,
            "oauth_login_backend_loaded_total": metrics_mod.record_backend_loaded,
            "oauth_login_auth_url_generated_total": metrics_mod.record_auth_url_generated,
        }

        # Invoke Recorder
        recorder_map[counter_attr]()

        # Assert
        add_mock.assert_called_once_with(1, {})


# Test: OAuth Login Initiated Counter
def test_record_oauth_login_initiated_increments_counter_once() -> None:
    """
    Recording OAuth Login Initiated Should Add 1 With Empty Labels.
    """

    # Assert
    _assert_add_called_once_with("oauth_login_initiated_total")


# Test: Redirect URI Built Counter
def test_record_redirect_uri_built_increments_counter_once() -> None:
    """
    Recording Redirect URI Built Should Add 1 With Empty Labels.
    """

    # Assert
    _assert_add_called_once_with("oauth_login_redirect_uri_built_total")


# Test: Backend Loaded Counter
def test_record_backend_loaded_increments_counter_once() -> None:
    """
    Recording Backend Loaded Should Add 1 With Empty Labels.
    """

    # Assert
    _assert_add_called_once_with("oauth_login_backend_loaded_total")


# Test: Auth URL Generated Counter
def test_record_auth_url_generated_increments_counter_once() -> None:
    """
    Recording Auth URL Generated Should Add 1 With Empty Labels.
    """

    # Assert
    _assert_add_called_once_with("oauth_login_auth_url_generated_total")
