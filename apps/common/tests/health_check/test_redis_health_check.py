# Standard Library Imports
from unittest.mock import MagicMock
from unittest.mock import patch

# Third Party Imports
import redis
from health_check.exceptions import HealthCheckException

# Local Imports
from apps.common.health_checks.redis_health_check import RedisHealthCheck


# Test Redis Health Check Class
class TestRedisHealthCheck:
    """
    Test Redis Health Check Class.
    """

    # Test Identifier Method
    def test_identifier(self, redis_health_check: RedisHealthCheck) -> None:
        """
        Test Identifier Method Returns Correct Class Name.

        Args:
            redis_health_check (RedisHealthCheck): Redis Health Check Instance.
        """

        # Assert Identifier Returns Class Name
        assert redis_health_check.identifier() == "RedisHealthCheck"

    # Test Check Status With No Settings Configured
    def test_check_status_no_settings(
        self,
        redis_health_check: RedisHealthCheck,
        monkeypatch,
    ) -> None:
        """
        Test Check Status Method When No Settings Are Configured.

        Args:
            redis_health_check (RedisHealthCheck): Redis Health Check Instance.
            monkeypatch: Pytest Monkeypatch Fixture.
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
        self,
        redis_health_check: RedisHealthCheck,
        monkeypatch,
    ) -> None:
        """
        Test Check Status Method With Empty Redis URL.

        Args:
            redis_health_check (RedisHealthCheck): Redis Health Check Instance.
            monkeypatch: Pytest Monkeypatch Fixture.
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
        self,
        mock_redis: MagicMock,
        redis_health_check: RedisHealthCheck,
        monkeypatch,
    ) -> None:
        """
        Test Check Status Method With Valid Settings And Successful Ping.

        Args:
            mock_redis (MagicMock): Mock Redis Class.
            redis_health_check (RedisHealthCheck): Redis Health Check Instance.
            monkeypatch: Pytest Monkeypatch Fixture.
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
        self,
        mock_redis: MagicMock,
        redis_health_check: RedisHealthCheck,
        monkeypatch,
    ) -> None:
        """
        Test Check Status Method With Redis URL Without Port.

        Args:
            mock_redis (MagicMock): Mock Redis Class.
            redis_health_check (RedisHealthCheck): Redis Health Check Instance.
            monkeypatch: Pytest Monkeypatch Fixture.
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
        self,
        mock_redis: MagicMock,
        redis_health_check: RedisHealthCheck,
        monkeypatch,
    ) -> None:
        """
        Test Check Status Method With Redis URL Without DB.

        Args:
            mock_redis (MagicMock): Mock Redis Class.
            redis_health_check (RedisHealthCheck): Redis Health Check Instance.
            monkeypatch: Pytest Monkeypatch Fixture.
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
        self,
        mock_redis: MagicMock,
        redis_health_check: RedisHealthCheck,
        monkeypatch,
    ) -> None:
        """
        Test Check Status Method With Failed Ping.

        Args:
            mock_redis (MagicMock): Mock Redis Class.
            redis_health_check (RedisHealthCheck): Redis Health Check Instance.
            monkeypatch: Pytest Monkeypatch Fixture.
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
        self,
        mock_redis: MagicMock,
        redis_health_check: RedisHealthCheck,
        monkeypatch,
    ) -> None:
        """
        Test Check Status Method With Redis Error.

        Args:
            mock_redis (MagicMock): Mock Redis Class.
            redis_health_check (RedisHealthCheck): Redis Health Check Instance.
            monkeypatch: Pytest Monkeypatch Fixture.
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
        self,
        mock_redis: MagicMock,
        redis_health_check: RedisHealthCheck,
        monkeypatch,
    ) -> None:
        """
        Test Check Status Method With Ping Exception.

        Args:
            mock_redis (MagicMock): Mock Redis Class.
            redis_health_check (RedisHealthCheck): Redis Health Check Instance.
            monkeypatch: Pytest Monkeypatch Fixture.
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
        self,
        mock_redis: MagicMock,
        redis_health_check: RedisHealthCheck,
        monkeypatch,
    ) -> None:
        """
        Test Check Status Method With Generic Exception.

        Args:
            mock_redis (MagicMock): Mock Redis Class.
            redis_health_check (RedisHealthCheck): Redis Health Check Instance.
            monkeypatch: Pytest Monkeypatch Fixture.
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
    def test_critical_service_attribute(self, redis_health_check: RedisHealthCheck) -> None:
        """
        Test Critical Service Attribute Is Set Correctly.

        Args:
            redis_health_check (RedisHealthCheck): Redis Health Check Instance.
        """

        # Assert Critical Service Is True
        assert redis_health_check.critical_service is True
