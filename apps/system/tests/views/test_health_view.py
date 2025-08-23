# Standard Library Imports
from typing import TYPE_CHECKING
from unittest.mock import MagicMock
from unittest.mock import patch

# Third Party Imports
from django.conf import settings
from rest_framework import status
from rest_framework.test import APIRequestFactory

# Local Imports
from apps.system.views.health_view import HealthCheckView

# If Type Checking
if TYPE_CHECKING:
    # Third Party Imports
    from rest_framework.response import Response


# Build Dummy Psutil Structs Function
def _vmem(total: int, available: int, percent: float, used: int, free: int) -> MagicMock:
    """
    Build Virtual Memory Mock Struct.

    Args:
        total (int): Total Bytes.
        available (int): Available Bytes.
        percent (float): Used Percent.
        used (int): Used Bytes.
        free (int): Free Bytes.

    Returns:
        MagicMock: Mocked Struct With Attributes Matching psutil.virtual_memory().
    """

    # Create Mock
    m: MagicMock = MagicMock()

    # Assign Attributes
    m.total = total
    m.available = available
    m.percent = percent
    m.used = used
    m.free = free

    # Return Mock
    return m


# Build Dummy Disk Usage Struct Function
def _disk(total: int, used: int, free: int, percent: float) -> MagicMock:
    """
    Build Disk Usage Mock Struct.

    Args:
        total (int): Total Bytes.
        used (int): Used Bytes.
        free (int): Free Bytes.
        percent (float): Used Percent.

    Returns:
        MagicMock: Mocked Struct With Attributes Matching psutil.disk_usage('/').
    """

    # Create Mock
    m: MagicMock = MagicMock()

    # Assign Attributes
    m.total = total
    m.used = used
    m.free = free
    m.percent = percent

    # Return Mock
    return m


# Test Healthy Metrics Return 200 With Healthy Status
def test_health_view_healthy() -> None:
    """
    Test Healthy Metrics Return 200 With Healthy Status.
    """

    # Patch Settings And Dependencies
    with (
        patch.object(settings, "PROJECT_NAME", "InitStack"),
        patch.object(settings, "PROJECT_VERSION", "1.2.3"),
        patch.object(settings, "SENTRY_ENVIRONMENT", "production"),
        patch("apps.system.views.health_view.health_check_requests_total") as mock_requests_total,
        patch("apps.system.views.health_view.health_check_errors_total") as mock_errors_total,
        patch("apps.system.views.health_view.health_check_duration_ms") as mock_duration_ms,
        patch("apps.system.views.health_view.psutil.virtual_memory", return_value=_vmem(100, 75, 25.0, 25, 75)),
        patch("apps.system.views.health_view.psutil.disk_usage", return_value=_disk(100, 50, 50, 50.0)),
        patch("apps.system.views.health_view.psutil.cpu_percent", return_value=15.5),
    ):
        # Build Request
        request = APIRequestFactory().get("/health")

        # Call View
        response: Response = HealthCheckView.as_view()(request)

    # Assert Status
    assert response.status_code == status.HTTP_200_OK
    data = response.data
    assert data["status"] == "healthy"
    assert data["app"] == "InitStack"
    assert data["version"] == "1.2.3"
    assert data["environment"] == "production"

    # Assert Metrics Called
    mock_requests_total.add.assert_called()
    mock_duration_ms.record.assert_called()
    mock_errors_total.add.assert_not_called()


# Test Degraded Metrics Return 503 With Degraded Status
def test_health_view_degraded() -> None:
    """
    Test Degraded Metrics Return 503 With Degraded Status.
    """

    # Patch Settings And Dependencies
    with (
        patch.object(settings, "PROJECT_NAME", "InitStack"),
        patch.object(settings, "PROJECT_VERSION", "1.2.3"),
        patch.object(settings, "SENTRY_ENVIRONMENT", "production"),
        patch("apps.system.views.health_view.health_check_requests_total") as mock_requests_total,
        patch("apps.system.views.health_view.health_check_errors_total") as mock_errors_total,
        patch("apps.system.views.health_view.health_check_duration_ms") as mock_duration_ms,
        patch("apps.system.views.health_view.psutil.virtual_memory", return_value=_vmem(100, 15, 85.0, 85, 15)),
        patch("apps.system.views.health_view.psutil.disk_usage", return_value=_disk(100, 50, 50, 50.0)),
        patch("apps.system.views.health_view.psutil.cpu_percent", return_value=85.5),
    ):
        # Build Request
        request = APIRequestFactory().get("/health")

        # Call View
        response: Response = HealthCheckView.as_view()(request)

    # Assert Status
    assert response.status_code == status.HTTP_503_SERVICE_UNAVAILABLE
    data = response.data
    assert data["status"] == "degraded"

    # Assert Metrics Called
    mock_requests_total.add.assert_called()
    mock_duration_ms.record.assert_called()
    mock_errors_total.add.assert_not_called()


# Test Unhealthy Metrics Return 503 With Unhealthy Status
def test_health_view_unhealthy() -> None:
    """
    Test Unhealthy Metrics Return 503 With Unhealthy Status.
    """

    # Patch Settings And Dependencies
    with (
        patch.object(settings, "PROJECT_NAME", "InitStack"),
        patch.object(settings, "PROJECT_VERSION", "1.2.3"),
        patch.object(settings, "SENTRY_ENVIRONMENT", "production"),
        patch("apps.system.views.health_view.health_check_requests_total"),
        patch("apps.system.views.health_view.health_check_errors_total") as mock_errors_total,
        patch("apps.system.views.health_view.health_check_duration_ms") as mock_duration_ms,
        patch("apps.system.views.health_view.psutil.virtual_memory", return_value=_vmem(100, 5, 95.0, 95, 5)),
        patch("apps.system.views.health_view.psutil.disk_usage", return_value=_disk(100, 98, 2, 98.0)),
        patch("apps.system.views.health_view.psutil.cpu_percent", return_value=95.5),
    ):
        # Build Request
        request = APIRequestFactory().get("/health")

        # Call View
        response: Response = HealthCheckView.as_view()(request)

    # Assert Status
    assert response.status_code == status.HTTP_503_SERVICE_UNAVAILABLE
    data = response.data
    assert data["status"] == "unhealthy"

    # Assert Metrics Called
    mock_duration_ms.record.assert_called()
    mock_errors_total.add.assert_not_called()


# Test Unexpected Exception Returns 500
def test_health_view_unexpected_error() -> None:
    """
    Test Unexpected Exception Returns 500.
    """

    # Patch Settings And Dependencies
    with (
        patch.object(settings, "PROJECT_NAME", "InitStack"),
        patch.object(settings, "PROJECT_VERSION", "1.2.3"),
        patch.object(settings, "SENTRY_ENVIRONMENT", "production"),
        patch("apps.system.views.health_view.health_check_requests_total") as mock_requests_total,
        patch("apps.system.views.health_view.health_check_errors_total") as mock_errors_total,
        patch("apps.system.views.health_view.health_check_duration_ms") as mock_duration_ms,
        patch("apps.system.views.health_view.psutil.virtual_memory", side_effect=Exception("boom")),
    ):
        # Build Request
        request = APIRequestFactory().get("/health")

        # Call View
        response: Response = HealthCheckView.as_view()(request)

    # Assert Status
    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert response.data == {"error": "Internal Server Error"}

    # Assert Metrics Called
    mock_requests_total.add.assert_called()
    mock_duration_ms.record.assert_called()
    mock_errors_total.add.assert_called()


# Test Psutil.Error Path Returns 500
def test_health_view_psutil_error() -> None:
    """
    Test Psutil.Error Path Returns 500.
    """

    try:
        # Type To Import
        import psutil as _ps  # noqa: PLC0415

    except Exception:
        # Mock Type
        _ps = MagicMock()

    # Build Psutil Error
    class _PE(_ps.Error):
        # Ignore
        pass

    # Patch Settings And Dependencies
    with (
        patch.object(settings, "PROJECT_NAME", "InitStack"),
        patch.object(settings, "PROJECT_VERSION", "1.2.3"),
        patch.object(settings, "SENTRY_ENVIRONMENT", "production"),
        patch("apps.system.views.health_view.health_check_requests_total"),
        patch("apps.system.views.health_view.health_check_errors_total"),
        patch("apps.system.views.health_view.health_check_duration_ms"),
        patch("apps.system.views.health_view.psutil.virtual_memory", side_effect=_PE("psutil error")),
    ):
        # Build Request
        request = APIRequestFactory().get("/health")

        # Call View
        response: Response = HealthCheckView.as_view()(request)

    # Assert Status
    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert response.data == {"error": "Internal Server Error"}
