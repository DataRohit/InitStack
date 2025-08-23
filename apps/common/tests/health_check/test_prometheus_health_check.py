# Standard Library Imports
from unittest.mock import MagicMock
from unittest.mock import patch

# Third Party Imports
import pytest
import requests
from health_check.exceptions import HealthCheckException

# Local Imports
from apps.common.health_checks.prometheus_health_check import PrometheusHealthCheck


# Prometheus Fixture
@pytest.fixture
def prometheus_health_check() -> PrometheusHealthCheck:
    """
    Create Prometheus Health Check Instance.

    Returns:
        PrometheusHealthCheck: Instance Of Prometheus Health Check.
    """

    # Return Instance
    return PrometheusHealthCheck()


# Test Prometheus Health Check Identifier
def test_identifier(prometheus_health_check: PrometheusHealthCheck) -> None:
    """
    Test Identifier Method Returns Correct Class Name.
    """

    # Assert Identifier Returns Class Name
    assert prometheus_health_check.identifier() == "PrometheusHealthCheck"


# Test Check Status With No Settings Configured
def test_check_status_no_settings(
    prometheus_health_check: PrometheusHealthCheck,
    monkeypatch,
) -> None:
    """
    Test Check Status Method When No Settings Are Configured.
    """

    # Set Empty Prometheus URL
    monkeypatch.setattr("django.conf.settings.PROMETHEUS_URL", "")

    # Run Check Status
    prometheus_health_check.check_status()

    # Assert Error Was Added
    assert len(prometheus_health_check.errors) == 1
    assert "PROMETHEUS_URL Not Configured" in str(prometheus_health_check.errors[0])


# Test Check Status With Valid Settings And Successful Response
@patch("requests.get")
def test_check_status_success(
    mock_get: MagicMock,
    prometheus_health_check: PrometheusHealthCheck,
    monkeypatch,
) -> None:
    """
    Test Check Status Method With Valid Settings And Successful Response.
    """

    # Set Prometheus URL
    monkeypatch.setattr("django.conf.settings.PROMETHEUS_URL", "http://prometheus:9090")

    # Configure Mock Response
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_get.return_value = mock_response

    # Run Check Status
    prometheus_health_check.check_status()

    # Assert No Errors Were Added
    assert len(prometheus_health_check.errors) == 0

    # Assert Request Was Made With Correct Parameters
    mock_get.assert_called_once_with(url="http://prometheus:9090/-/healthy", timeout=3)


# Test Check Status With URL Trailing Slash
@patch("requests.get")
def test_check_status_url_trailing_slash(
    mock_get: MagicMock,
    prometheus_health_check: PrometheusHealthCheck,
    monkeypatch,
) -> None:
    """
    Test Check Status Method With URL Having Trailing Slash.
    """

    # Set Prometheus URL With Trailing Slash
    monkeypatch.setattr("django.conf.settings.PROMETHEUS_URL", "http://prometheus:9090/")

    # Configure Mock Response
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_get.return_value = mock_response

    # Run Check Status
    prometheus_health_check.check_status()

    # Assert No Errors Were Added
    assert len(prometheus_health_check.errors) == 0

    # Assert Request Was Made With Correct Parameters (Trailing Slash Removed)
    mock_get.assert_called_once_with(url="http://prometheus:9090/-/healthy", timeout=3)


# Test Check Status With Non-200 Response
@patch("requests.get")
def test_check_status_non_200_response(
    mock_get: MagicMock,
    prometheus_health_check: PrometheusHealthCheck,
    monkeypatch,
) -> None:
    """
    Test Check Status Method With Non-200 Response.
    """

    # Set Prometheus URL
    monkeypatch.setattr("django.conf.settings.PROMETHEUS_URL", "http://prometheus:9090")

    # Configure Mock Response
    mock_response = MagicMock()
    mock_response.status_code = 500
    mock_get.return_value = mock_response

    # Run Check Status
    prometheus_health_check.check_status()

    # Assert Error Was Added
    assert len(prometheus_health_check.errors) == 1
    assert "Prometheus Returned Unexpected Status: 500" in str(prometheus_health_check.errors[0])


# Test Check Status With Request Exception
@patch("requests.get")
def test_check_status_request_exception(
    mock_get: MagicMock,
    prometheus_health_check: PrometheusHealthCheck,
    monkeypatch,
) -> None:
    """
    Test Check Status Method With Request Exception.
    """

    # Set Prometheus URL
    monkeypatch.setattr("django.conf.settings.PROMETHEUS_URL", "http://prometheus:9090")

    # Configure Mock To Raise Exception
    mock_get.side_effect = requests.RequestException("Connection Error")

    # Run Check Status
    prometheus_health_check.check_status()

    # Assert Error Was Added
    assert len(prometheus_health_check.errors) == 1
    assert "Connection Error" in str(prometheus_health_check.errors[0])
    assert isinstance(prometheus_health_check.errors[0], HealthCheckException)


# Test Check Status With Timeout Exception
@patch("requests.get")
def test_check_status_timeout_exception(
    mock_get: MagicMock,
    prometheus_health_check: PrometheusHealthCheck,
    monkeypatch,
) -> None:
    """
    Test Check Status Method With Timeout Exception.
    """

    # Set Prometheus URL
    monkeypatch.setattr("django.conf.settings.PROMETHEUS_URL", "http://prometheus:9090")

    # Configure Mock To Raise Exception
    mock_get.side_effect = requests.Timeout("Request Timed Out")

    # Run Check Status
    prometheus_health_check.check_status()

    # Assert Error Was Added
    assert len(prometheus_health_check.errors) == 1
    assert "Request Timed Out" in str(prometheus_health_check.errors[0])
    assert isinstance(prometheus_health_check.errors[0], HealthCheckException)


# Test Check Status With Generic Exception
@patch("requests.get")
def test_check_status_generic_exception(
    mock_get: MagicMock,
    prometheus_health_check: PrometheusHealthCheck,
    monkeypatch,
) -> None:
    """
    Test Check Status Method With Generic Exception.
    """

    # Set Prometheus URL
    monkeypatch.setattr("django.conf.settings.PROMETHEUS_URL", "http://prometheus:9090")

    # Configure Mock To Raise Exception
    mock_get.side_effect = Exception("Unexpected Error")

    # Run Check Status
    prometheus_health_check.check_status()

    # Assert Error Was Added
    assert len(prometheus_health_check.errors) == 1
    assert "Unexpected Error" in str(prometheus_health_check.errors[0])
    assert isinstance(prometheus_health_check.errors[0], HealthCheckException)


# Test Critical Service Attribute
def test_critical_service_attribute(prometheus_health_check: PrometheusHealthCheck) -> None:
    """
    Test Critical Service Attribute Is Set Correctly.
    """

    # Assert Critical Service Is True
    assert prometheus_health_check.critical_service is True
