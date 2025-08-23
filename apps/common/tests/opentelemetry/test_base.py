# Standard Library Imports
from typing import Any
from unittest.mock import MagicMock
from unittest.mock import patch

# Local Imports
from apps.common.opentelemetry import base as otel_base
from apps.common.opentelemetry.base import record_api_error
from apps.common.opentelemetry.base import record_cache_operation
from apps.common.opentelemetry.base import record_email_sent
from apps.common.opentelemetry.base import record_http_request
from apps.common.opentelemetry.base import record_token_validation
from apps.common.opentelemetry.base import record_user_action
from apps.common.opentelemetry.base import record_user_update


# Test HTTP Request Recording Function
def test_record_http_request_calls_counters() -> None:
    """
    Verify record_http_request Adds To Counter And Records Histogram.
    """

    # Build Inputs
    method: str = "GET"
    endpoint: str = "/api/test"
    status_code: int = 200
    duration: float = 0.123

    # Build Expected Labels
    expected_labels: dict[str, Any] = {
        "method": method,
        "endpoint": endpoint,
        "status_code": status_code,
    }

    # Patch Metrics
    with (
        patch.object(otel_base, "http_requests_total") as http_requests_total,
        patch.object(otel_base, "http_request_duration") as http_request_duration,
    ):
        # Type Hint
        http_requests_total: MagicMock
        http_request_duration: MagicMock

        # Call Function
        record_http_request(method=method, endpoint=endpoint, status_code=status_code, duration=duration)

    # Assert Calls
    http_requests_total.add.assert_called_once_with(1, expected_labels)
    http_request_duration.record.assert_called_once_with(duration, expected_labels)


# Test API Error Recording Function
def test_record_api_error_calls_counter() -> None:
    """
    Verify record_api_error Adds To Errors Counter.
    """

    # Build Inputs
    endpoint: str = "/api/test"
    error_type: str = "InternalServerError"

    # Build Expected Labels
    expected_labels: dict[str, Any] = {
        "endpoint": endpoint,
        "error_type": error_type,
    }

    # Patch Metrics
    with patch.object(otel_base, "api_errors_total") as api_errors_total:
        # Type Hint
        api_errors_total: MagicMock

        # Call Function
        record_api_error(endpoint=endpoint, error_type=error_type)

    # Assert Calls
    api_errors_total.add.assert_called_once_with(1, expected_labels)


# Test User Action Recording Function
def test_record_user_action_calls_counter() -> None:
    """
    Verify record_user_action Adds To User Actions Counter.
    """

    # Build Inputs
    action_type: str = "login"
    success: bool = True

    # Build Expected Labels
    expected_labels: dict[str, Any] = {
        "action_type": action_type,
        "success": success,
    }

    # Patch Metrics
    with patch.object(otel_base, "user_actions_total") as user_actions_total:
        # Type Hint
        user_actions_total: MagicMock

        # Call Function
        record_user_action(action_type=action_type, success=success)

    # Assert Calls
    user_actions_total.add.assert_called_once_with(1, expected_labels)


# Test Token Validation Recording Function
def test_record_token_validation_calls_counter() -> None:
    """
    Verify record_token_validation Adds To Token Validations Counter.
    """

    # Build Inputs
    token_type: str = "activation"  # noqa: S105
    success: bool = False

    # Build Expected Labels
    expected_labels: dict[str, Any] = {
        "token_type": token_type,
        "success": success,
    }

    # Patch Metrics
    with patch.object(otel_base, "token_validations_total") as token_validations_total:
        # Type Hint
        token_validations_total: MagicMock

        # Call Function
        record_token_validation(token_type=token_type, success=success)

    # Assert Calls
    token_validations_total.add.assert_called_once_with(1, expected_labels)


# Test Email Sent Recording Function
def test_record_email_sent_calls_counter() -> None:
    """
    Verify record_email_sent Adds To Emails Sent Counter.
    """

    # Build Inputs
    email_type: str = "activation"
    success: bool = True

    # Build Expected Labels
    expected_labels: dict[str, Any] = {
        "email_type": email_type,
        "success": success,
    }

    # Patch Metrics
    with patch.object(otel_base, "emails_sent_total") as emails_sent_total:
        # Type Hint
        emails_sent_total: MagicMock

        # Call Function
        record_email_sent(email_type=email_type, success=success)

    # Assert Calls
    emails_sent_total.add.assert_called_once_with(1, expected_labels)


# Test Cache Operation Recording Function
def test_record_cache_operation_calls_counter() -> None:
    """
    Verify record_cache_operation Adds To Cache Operations Counter.
    """

    # Build Inputs
    operation: str = "set"
    cache_type: str = "token_cache"
    success: bool = True

    # Build Expected Labels
    expected_labels: dict[str, Any] = {
        "operation": operation,
        "cache_type": cache_type,
        "success": success,
    }

    # Patch Metrics
    with patch.object(otel_base, "cache_operations_total") as cache_operations_total:
        # Type Hint
        cache_operations_total: MagicMock

        # Call Function
        record_cache_operation(operation=operation, cache_type=cache_type, success=success)

    # Assert Calls
    cache_operations_total.add.assert_called_once_with(1, expected_labels)


# Test User Update Recording Function
def test_record_user_update_calls_counter() -> None:
    """
    Verify record_user_update Adds To User Updates Counter.
    """

    # Build Inputs
    update_type: str = "activate"
    success: bool = False

    # Build Expected Labels
    expected_labels: dict[str, Any] = {
        "update_type": update_type,
        "success": success,
    }

    # Patch Metrics
    with patch.object(otel_base, "user_updates_total") as user_updates_total:
        # Type Hint
        user_updates_total: MagicMock

        # Call Function
        record_user_update(update_type=update_type, success=success)

    # Assert Calls
    user_updates_total.add.assert_called_once_with(1, expected_labels)
