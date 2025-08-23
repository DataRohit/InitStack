# Standard Library Imports
from unittest.mock import MagicMock
from unittest.mock import patch

# Third Party Imports
import pytest
import requests

# Local Imports
from apps.common.health_checks.jaeger_health_check import JaegerHealthCheck


# Jaeger Fixtures
@pytest.fixture
def jaeger_health_check() -> JaegerHealthCheck:
    """
    Create Jaeger Health Check Instance.

    Returns:
        JaegerHealthCheck: Instance Of Jaeger Health Check.
    """

    # Return Instance
    return JaegerHealthCheck()


@pytest.fixture
def mock_jaeger_settings(monkeypatch) -> None:
    """
    Mock Jaeger Settings.

    Args:
        monkeypatch: Pytest Monkeypatch Fixture.
    """

    # Set Jaeger URL
    monkeypatch.setattr("django.conf.settings.JAEGER_QUERY_URL", "http://localhost:16686")


@pytest.fixture
def mock_jaeger_settings_empty(monkeypatch) -> None:
    """
    Mock Empty Jaeger Settings.

    Args:
        monkeypatch: Pytest Monkeypatch Fixture.
    """

    # Set Empty Jaeger URL
    monkeypatch.setattr("django.conf.settings.JAEGER_QUERY_URL", "")


# Mock Response Fixtures
@pytest.fixture
def mock_response_success() -> MagicMock:
    """
    Mock Successful HTTP Response.

    Returns:
        MagicMock: Mock Response With 200 Status Code.
    """

    # Create Mock Response
    mock_response = MagicMock()

    # Configure Mock
    mock_response.status_code = 200
    mock_response.json.return_value = {"data": ["service1", "service2"]}

    # Return Mock
    return mock_response


@pytest.fixture
def mock_response_error() -> MagicMock:
    """
    Mock Error HTTP Response.

    Returns:
        MagicMock: Mock Response With Error Status Code.
    """

    # Create Mock Response
    mock_response = MagicMock()

    # Configure Mock
    mock_response.status_code = 500

    # Return Mock
    return mock_response


@pytest.fixture
def mock_response_invalid_json() -> MagicMock:
    """
    Mock HTTP Response With Invalid JSON.

    Returns:
        MagicMock: Mock Response With Invalid JSON Structure.
    """

    # Create Mock Response
    mock_response = MagicMock()

    # Configure Mock
    mock_response.status_code = 200
    mock_response.json.return_value = {"wrong_key": "value"}

    # Return Mock
    return mock_response


# Test Jaeger Health Check Identifier
def test_identifier(jaeger_health_check: JaegerHealthCheck) -> None:
    """
    Test Identifier Method Returns Correct Class Name.
    """

    # Assert Identifier Returns Class Name
    assert jaeger_health_check.identifier() == "JaegerHealthCheck"


# Test Check Status With No URL Configured
def test_check_status_no_url(
    jaeger_health_check: JaegerHealthCheck,
    mock_jaeger_settings_empty,
) -> None:
    """
    Test Check Status Method When No URL Is Configured.
    """

    # Run Check Status
    jaeger_health_check.check_status()

    # Assert Error Was Added
    assert len(jaeger_health_check.errors) == 1
    assert "JAEGER_QUERY_URL Not Configured" in str(jaeger_health_check.errors[0])


# Test Check Status With Valid URL And Successful Response
@patch("apps.common.health_checks.jaeger_health_check.requests.get")
def test_check_status_success(
    mock_requests_get: MagicMock,
    jaeger_health_check: JaegerHealthCheck,
    mock_jaeger_settings,
    mock_response_success,
) -> None:
    """
    Test Check Status Method With Valid URL And Successful Response.
    """

    # Configure Mock
    mock_requests_get.return_value = mock_response_success

    # Run Check Status
    jaeger_health_check.check_status()

    # Assert No Errors Were Added
    assert len(jaeger_health_check.errors) == 0

    # Assert Request Was Made With Correct Parameters
    mock_requests_get.assert_called_once_with(
        url="http://localhost:16686/api/services",
        timeout=3,
    )


# Test Check Status With Non-200 Response
@patch("apps.common.health_checks.jaeger_health_check.requests.get")
def test_check_status_non_200_response(
    mock_requests_get: MagicMock,
    jaeger_health_check: JaegerHealthCheck,
    mock_jaeger_settings,
    mock_response_error,
) -> None:
    """
    Test Check Status Method With Non-200 Response.
    """

    # Configure Mock
    mock_requests_get.return_value = mock_response_error

    # Run Check Status
    jaeger_health_check.check_status()

    # Assert Error Was Added
    assert len(jaeger_health_check.errors) == 1
    assert "Jaeger Returned Unexpected Status: 500" in str(jaeger_health_check.errors[0])


# Test Check Status With Missing Data Key In Response
@patch("apps.common.health_checks.jaeger_health_check.requests.get")
def test_check_status_missing_data_key(
    mock_requests_get: MagicMock,
    jaeger_health_check: JaegerHealthCheck,
    mock_jaeger_settings,
    mock_response_invalid_json,
) -> None:
    """
    Test Check Status Method With Missing Data Key In Response.
    """

    # Configure Mock
    mock_requests_get.return_value = mock_response_invalid_json

    # Run Check Status
    jaeger_health_check.check_status()

    # Assert Error Was Added
    assert len(jaeger_health_check.errors) == 1
    assert "Jaeger API Response Missing 'data'" in str(jaeger_health_check.errors[0])


# Test Check Status With Request Exception
@patch("apps.common.health_checks.jaeger_health_check.requests.get")
def test_check_status_request_exception(
    mock_requests_get: MagicMock,
    jaeger_health_check: JaegerHealthCheck,
    mock_jaeger_settings,
) -> None:
    """
    Test Check Status Method With Request Exception.
    """

    # Configure Mock To Raise Exception
    mock_requests_get.side_effect = requests.RequestException("Connection Error")

    # Run Check Status
    jaeger_health_check.check_status()

    # Assert Error Was Added
    assert len(jaeger_health_check.errors) == 1
    assert "Connection Error" in str(jaeger_health_check.errors[0])


# Test Check Status With Generic Exception
@patch("apps.common.health_checks.jaeger_health_check.requests.get")
def test_check_status_generic_exception(
    mock_requests_get: MagicMock,
    jaeger_health_check: JaegerHealthCheck,
    mock_jaeger_settings,
) -> None:
    """
    Test Check Status Method With Generic Exception.
    """

    # Configure Mock To Raise Exception
    mock_requests_get.side_effect = Exception("Unexpected Error")

    # Run Check Status
    jaeger_health_check.check_status()

    # Assert Error Was Added
    assert len(jaeger_health_check.errors) == 1
    assert "Unexpected Error" in str(jaeger_health_check.errors[0])


# Test URL Trailing Slash Handling
@patch("apps.common.health_checks.jaeger_health_check.requests.get")
def test_check_status_url_trailing_slash(
    mock_requests_get: MagicMock,
    jaeger_health_check: JaegerHealthCheck,
    mock_jaeger_settings,
    mock_response_success,
    monkeypatch,
) -> None:
    """
    Test Check Status Method With URL Having Trailing Slash.
    """

    # Set Jaeger URL With Trailing Slash
    monkeypatch.setattr("django.conf.settings.JAEGER_QUERY_URL", "http://localhost:16686/")

    # Configure Mock
    mock_requests_get.return_value = mock_response_success

    # Run Check Status
    jaeger_health_check.check_status()

    # Assert No Errors Were Added
    assert len(jaeger_health_check.errors) == 0

    # Assert Request Was Made With Correct URL (Trailing Slash Removed)
    mock_requests_get.assert_called_once_with(
        url="http://localhost:16686/api/services",
        timeout=3,
    )


# Test Critical Service Attribute
def test_critical_service_attribute(jaeger_health_check: JaegerHealthCheck) -> None:
    """
    Test Critical Service Attribute Is Set Correctly.
    """

    # Assert Critical Service Is True
    assert jaeger_health_check.critical_service is True
