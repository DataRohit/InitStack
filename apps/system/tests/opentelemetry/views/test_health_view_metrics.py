# Standard Library Imports
from types import SimpleNamespace
from unittest.mock import MagicMock
from unittest.mock import patch

# Local Imports
import apps.system.opentelemetry.views.health_view_metrics as hv_metrics


# Test CPU Observation Success
def test_observe_cpu_percent_success() -> None:
    """
    Observe CPU Percent Returns Single Observation On Success.
    """

    # Patch Dependencies
    with (
        patch.object(hv_metrics.psutil, "cpu_percent", return_value=12.3),
        patch.object(hv_metrics, "Observation") as observation_mock,
    ):
        # Type Hint
        observation_mock: MagicMock

        # Configure Observation Return
        observation_mock.side_effect = lambda v: ("OBS", v)

        # Call Callback
        observations = hv_metrics._observe_cpu_percent(options=MagicMock())

    # Assert Observation
    assert observations == [("OBS", 12.3)]
    observation_mock.assert_called_once_with(12.3)


# Test CPU Observation Error
def test_observe_cpu_percent_error() -> None:
    """
    Observe CPU Percent Returns Empty List On Psutil Error.
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

    # Patch Dependencies
    with (
        patch.object(hv_metrics.psutil, "cpu_percent", side_effect=_PE("boom")),
        patch.object(hv_metrics, "logger") as logger,
    ):
        # Type Hint
        logger: MagicMock

        # Call Callback
        observations = hv_metrics._observe_cpu_percent(options=MagicMock())

    # Assert Empty And Logged
    assert observations == []
    logger.exception.assert_called()


# Test Memory Observation Success
def test_observe_memory_percent_success() -> None:
    """
    Observe Memory Percent Returns Single Observation On Success.
    """

    # Build Virtual Memory Mock
    vmem = SimpleNamespace(percent=77.7)

    # Patch Dependencies
    with (
        patch.object(hv_metrics.psutil, "virtual_memory", return_value=vmem),
        patch.object(hv_metrics, "Observation") as observation_mock,
    ):
        # Type Hint
        observation_mock: MagicMock

        # Configure Observation Return
        observation_mock.side_effect = lambda v: ("OBS", v)

        # Call Callback
        observations = hv_metrics._observe_memory_percent(options=MagicMock())

    # Assert Observation
    assert observations == [("OBS", 77.7)]
    observation_mock.assert_called_once_with(77.7)


# Test Memory Observation Error
def test_observe_memory_percent_error() -> None:
    """
    Observe Memory Percent Returns Empty List On Psutil Error.
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

    # Patch Dependencies
    with (
        patch.object(hv_metrics.psutil, "virtual_memory", side_effect=_PE("boom")),
        patch.object(hv_metrics, "logger") as logger,
    ):
        # Type Hint
        logger: MagicMock

        # Call Callback
        observations = hv_metrics._observe_memory_percent(options=MagicMock())

    # Assert Empty And Logged
    assert observations == []
    logger.exception.assert_called()


# Test Disk Observation Success
def test_observe_disk_percent_success() -> None:
    """
    Observe Disk Percent Returns Single Observation On Success.
    """

    # Build Disk Usage Mock
    dusage = SimpleNamespace(percent=55.5)

    # Patch Dependencies
    with (
        patch.object(hv_metrics.psutil, "disk_usage", return_value=dusage),
        patch.object(hv_metrics, "Observation") as observation_mock,
    ):
        # Type Hint
        observation_mock: MagicMock

        # Configure Observation Return
        observation_mock.side_effect = lambda v: ("OBS", v)

        # Call Callback
        observations = hv_metrics._observe_disk_percent(options=MagicMock())

    # Assert Observation
    assert observations == [("OBS", 55.5)]
    observation_mock.assert_called_once_with(55.5)


# Test Disk Observation Error
def test_observe_disk_percent_error() -> None:
    """
    Observe Disk Percent Returns Empty List On Psutil Error.
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

    # Patch Dependencies
    with (
        patch.object(hv_metrics.psutil, "disk_usage", side_effect=_PE("boom")),
        patch.object(hv_metrics, "logger") as logger,
    ):
        # Type Hint
        logger: MagicMock

        # Call Callback
        observations = hv_metrics._observe_disk_percent(options=MagicMock())

    # Assert Empty And Logged
    assert observations == []
    logger.exception.assert_called()
