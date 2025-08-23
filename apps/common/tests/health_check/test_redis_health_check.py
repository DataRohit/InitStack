# Standard Library Imports
from unittest.mock import MagicMock
from unittest.mock import patch

# Third Party Imports
import pytest
import redis
from health_check.exceptions import HealthCheckException

# Local Imports
from apps.common.health_checks.redis_health_check import RedisHealthCheck


# Redis Fixture
@pytest.fixture
def redis_health_check() -> RedisHealthCheck:
    """
    Create Redis Health Check Instance.

    Returns:
        RedisHealthCheck: Instance Of Redis Health Check.
    """

    # Return Instance
    return RedisHealthCheck()


# Test Redis Health Check Identifier
def test_identifier(redis_health_check: RedisHealthCheck) -> None:
    """
    Test Identifier Method Returns Correct Class Name.
    """

    # Assert Identifier Returns Class Name
    assert redis_health_check.identifier() == "RedisHealthCheck"


# Test Check Status With No Settings Configured
def test_check_status_no_settings(
    redis_health_check: RedisHealthCheck,
    monkeypatch,
) -> None:
    """
    Test Check Status Method When No Settings Are Configured.
    """

    # Set Empty Redis URL
    monkeypatch.delattr("django.conf.settings.REDIS_DEFAULT_URL", raising=False)

    # Run Check Status
    redis_health_check.check_status()

    # Assert Error Was Added
    assert len(redis_health_check.errors) == 1
    assert "REDIS_DEFAULT_URL Not Configured" in str(redis_health_check.errors[0])


# Test Check Status With Empty Redis URL
def test_check_status_empty_redis_url(
    redis_health_check: RedisHealthCheck,
    monkeypatch,
) -> None:
    """
    Test Check Status Method With Empty Redis URL.
    """

    # Set Empty Redis URL
    monkeypatch.setattr("django.conf.settings.REDIS_DEFAULT_URL", "")

    # Run Check Status
    redis_health_check.check_status()

    # Assert Error Was Added
    assert len(redis_health_check.errors) == 1
    assert "REDIS_DEFAULT_URL Not Configured" in str(redis_health_check.errors[0])


# Test Check Status With Valid Settings And Successful Ping
@patch("redis.Redis")
def test_check_status_success(
    mock_redis: MagicMock,
    redis_health_check: RedisHealthCheck,
    monkeypatch,
) -> None:
    """
    Test Check Status Method With Valid Settings And Successful Ping.
    """

    # Set Redis URL
    monkeypatch.setattr(
        "django.conf.settings.REDIS_DEFAULT_URL",
        "redis://:password@localhost:6379/0",
    )

    # Configure Mock Redis Client
    mock_redis_instance = MagicMock()
    mock_redis_instance.ping.return_value = True
    mock_redis.return_value = mock_redis_instance

    # Run Check Status
    redis_health_check.check_status()

    # Assert No Errors Were Added
    assert len(redis_health_check.errors) == 0

    # Assert Redis Client Was Created With Correct Parameters
    mock_redis.assert_called_once_with(
        host="localhost",
        port=6379,
        db=0,
        password="password",
        socket_timeout=3,
    )

    # Assert Ping Was Called
    mock_redis_instance.ping.assert_called_once()


# Test Check Status With Redis URL Without Port
@patch("redis.Redis")
def test_check_status_no_port(
    mock_redis: MagicMock,
    redis_health_check: RedisHealthCheck,
    monkeypatch,
) -> None:
    """
    Test Check Status Method With Redis URL Without Port.
    """

    # Set Redis URL Without Port
    monkeypatch.setattr(
        "django.conf.settings.REDIS_DEFAULT_URL",
        "redis://localhost/0",
    )

    # Configure Mock Redis Client
    mock_redis_instance = MagicMock()
    mock_redis_instance.ping.return_value = True
    mock_redis.return_value = mock_redis_instance

    # Run Check Status
    redis_health_check.check_status()

    # Assert No Errors Were Added
    assert len(redis_health_check.errors) == 0

    # Assert Redis Client Was Created With Default Port
    mock_redis.assert_called_once_with(
        host="localhost",
        port=6379,
        db=0,
        password=None,
        socket_timeout=3,
    )


# Test Check Status With Redis URL Without DB
@patch("redis.Redis")
def test_check_status_no_db(
    mock_redis: MagicMock,
    redis_health_check: RedisHealthCheck,
    monkeypatch,
) -> None:
    """
    Test Check Status Method With Redis URL Without DB.
    """

    # Set Redis URL Without DB
    monkeypatch.setattr(
        "django.conf.settings.REDIS_DEFAULT_URL",
        "redis://localhost:6379",
    )

    # Configure Mock Redis Client
    mock_redis_instance = MagicMock()
    mock_redis_instance.ping.return_value = True
    mock_redis.return_value = mock_redis_instance

    # Run Check Status
    redis_health_check.check_status()

    # Assert No Errors Were Added
    assert len(redis_health_check.errors) == 0

    # Assert Redis Client Was Created With Default DB
    mock_redis.assert_called_once_with(
        host="localhost",
        port=6379,
        db=0,
        password=None,
        socket_timeout=3,
    )


# Test Check Status With Failed Ping
@patch("redis.Redis")
def test_check_status_failed_ping(
    mock_redis: MagicMock,
    redis_health_check: RedisHealthCheck,
    monkeypatch,
) -> None:
    """
    Test Check Status Method With Failed Ping.
    """

    # Set Redis URL
    monkeypatch.setattr(
        "django.conf.settings.REDIS_DEFAULT_URL",
        "redis://localhost:6379/0",
    )

    # Configure Mock Redis Client
    mock_redis_instance = MagicMock()
    mock_redis_instance.ping.return_value = False
    mock_redis.return_value = mock_redis_instance

    # Run Check Status
    redis_health_check.check_status()

    # Assert Error Was Added
    assert len(redis_health_check.errors) == 1
    assert "Redis Did Not Respond To PING" in str(redis_health_check.errors[0])


# Test Check Status With Redis Error
@patch("redis.Redis")
def test_check_status_redis_error(
    mock_redis: MagicMock,
    redis_health_check: RedisHealthCheck,
    monkeypatch,
) -> None:
    """
    Test Check Status Method With Redis Error.
    """

    # Set Redis URL
    monkeypatch.setattr(
        "django.conf.settings.REDIS_DEFAULT_URL",
        "redis://localhost:6379/0",
    )

    # Configure Mock To Raise Exception
    mock_redis.side_effect = redis.RedisError("Connection Error")

    # Run Check Status
    redis_health_check.check_status()

    # Assert Error Was Added
    assert len(redis_health_check.errors) == 1
    assert "Connection Error" in str(redis_health_check.errors[0])
    assert isinstance(redis_health_check.errors[0], HealthCheckException)


# Test Check Status With Ping Exception
@patch("redis.Redis")
def test_check_status_ping_exception(
    mock_redis: MagicMock,
    redis_health_check: RedisHealthCheck,
    monkeypatch,
) -> None:
    """
    Test Check Status Method With Ping Exception.
    """

    # Set Redis URL
    monkeypatch.setattr(
        "django.conf.settings.REDIS_DEFAULT_URL",
        "redis://localhost:6379/0",
    )

    # Configure Mock Redis Client
    mock_redis_instance = MagicMock()
    mock_redis_instance.ping.side_effect = redis.RedisError("Ping Failed")
    mock_redis.return_value = mock_redis_instance

    # Run Check Status
    redis_health_check.check_status()

    # Assert Error Was Added
    assert len(redis_health_check.errors) == 1
    assert "Ping Failed" in str(redis_health_check.errors[0])
    assert isinstance(redis_health_check.errors[0], HealthCheckException)


# Test Check Status With Generic Exception
@patch("redis.Redis")
def test_check_status_generic_exception(
    mock_redis: MagicMock,
    redis_health_check: RedisHealthCheck,
    monkeypatch,
) -> None:
    """
    Test Check Status Method With Generic Exception.
    """

    # Set Redis URL
    monkeypatch.setattr(
        "django.conf.settings.REDIS_DEFAULT_URL",
        "redis://localhost:6379/0",
    )

    # Configure Mock To Raise Exception
    mock_redis.side_effect = Exception("Unexpected Error")

    # Run Check Status
    redis_health_check.check_status()

    # Assert Error Was Added
    assert len(redis_health_check.errors) == 1
    assert "Unexpected Error" in str(redis_health_check.errors[0])
    assert isinstance(redis_health_check.errors[0], HealthCheckException)


# Test Critical Service Attribute
def test_critical_service_attribute(redis_health_check: RedisHealthCheck) -> None:
    """
    Test Critical Service Attribute Is Set Correctly.
    """

    # Assert Critical Service Is True
    assert redis_health_check.critical_service is True
