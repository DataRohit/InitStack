# Standard Library Imports
from unittest.mock import MagicMock

# Third Party Imports
import pytest
from django.conf import settings
from elasticsearch import Elasticsearch

# Local Imports
from apps.common.health_checks.elasticsearch_health_check import ElasticsearchHealthCheck
from apps.common.health_checks.jaeger_health_check import JaegerHealthCheck
from apps.common.health_checks.mailpit_health_check import MailpitSMTPHealthCheck
from apps.common.health_checks.prometheus_health_check import PrometheusHealthCheck
from apps.common.health_checks.redis_health_check import RedisHealthCheck


# Elasticsearch Fixtures
@pytest.fixture
def elasticsearch_health_check() -> ElasticsearchHealthCheck:
    """
    Create Elasticsearch Health Check Instance.

    Returns:
        ElasticsearchHealthCheck: Instance Of Elasticsearch Health Check.
    """

    # Return Instance
    return ElasticsearchHealthCheck()


@pytest.fixture
def mock_elasticsearch_settings(monkeypatch) -> None:
    """
    Mock Elasticsearch Settings.

    Args:
        monkeypatch: Pytest Monkeypatch Fixture.
    """

    # Set Elasticsearch URL
    monkeypatch.setattr(settings, "ELASTICSEARCH_URL", "elasticsearch://user:pass@localhost:9200")


@pytest.fixture
def mock_elasticsearch_settings_empty(monkeypatch) -> None:
    """
    Mock Empty Elasticsearch Settings.

    Args:
        monkeypatch: Pytest Monkeypatch Fixture.
    """

    # Set Empty Elasticsearch URL
    monkeypatch.setattr(settings, "ELASTICSEARCH_URL", "")


@pytest.fixture
def mock_elasticsearch_client() -> MagicMock:
    """
    Mock Elasticsearch Client.

    Returns:
        MagicMock: Mock Elasticsearch Client.
    """

    # Create Mock Client
    mock_client = MagicMock(spec=Elasticsearch)

    # Configure Mock
    mock_client.ping.return_value = True

    # Return Mock
    return mock_client


@pytest.fixture
def mock_elasticsearch_client_error() -> MagicMock:
    """
    Mock Elasticsearch Client With Error.

    Returns:
        MagicMock: Mock Elasticsearch Client That Raises Error.
    """

    # Create Mock Client
    mock_client = MagicMock(spec=Elasticsearch)

    # Configure Mock To Return False For Ping
    mock_client.ping.return_value = False

    # Return Mock
    return mock_client


@pytest.fixture
def mock_elasticsearch_exception() -> MagicMock:
    """
    Mock Elasticsearch Client That Raises Exception.

    Returns:
        MagicMock: Mock Elasticsearch Client That Raises Exception.
    """

    # Create Mock Client
    mock_client = MagicMock(spec=Elasticsearch)

    # Configure Mock To Raise Exception
    mock_client.ping.side_effect = Exception("Connection Error")

    # Return Mock
    return mock_client


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
    monkeypatch.setattr(settings, "JAEGER_QUERY_URL", "http://localhost:16686")


@pytest.fixture
def mock_jaeger_settings_empty(monkeypatch) -> None:
    """
    Mock Empty Jaeger Settings.

    Args:
        monkeypatch: Pytest Monkeypatch Fixture.
    """

    # Set Empty Jaeger URL
    monkeypatch.setattr(settings, "JAEGER_QUERY_URL", "")


# Mailpit Fixtures
@pytest.fixture
def mailpit_health_check() -> MailpitSMTPHealthCheck:
    """
    Create Mailpit Health Check Instance.

    Returns:
        MailpitSMTPHealthCheck: Instance Of Mailpit Health Check.
    """

    # Return Instance
    return MailpitSMTPHealthCheck()


@pytest.fixture
def mock_mailpit_settings(monkeypatch) -> None:
    """
    Mock Mailpit Settings.

    Args:
        monkeypatch: Pytest Monkeypatch Fixture.
    """

    # Set Mailpit Settings
    monkeypatch.setattr(settings, "EMAIL_HOST", "localhost")
    monkeypatch.setattr(settings, "EMAIL_PORT", 1025)


@pytest.fixture
def mock_mailpit_settings_empty(monkeypatch) -> None:
    """
    Mock Empty Mailpit Settings.

    Args:
        monkeypatch: Pytest Monkeypatch Fixture.
    """

    # Set Empty Mailpit Settings
    monkeypatch.setattr(settings, "EMAIL_HOST", "")
    monkeypatch.setattr(settings, "EMAIL_PORT", None)


# Prometheus Fixtures
@pytest.fixture
def prometheus_health_check() -> PrometheusHealthCheck:
    """
    Create Prometheus Health Check Instance.

    Returns:
        PrometheusHealthCheck: Instance Of Prometheus Health Check.
    """

    # Return Instance
    return PrometheusHealthCheck()


@pytest.fixture
def mock_prometheus_settings(monkeypatch) -> None:
    """
    Mock Prometheus Settings.

    Args:
        monkeypatch: Pytest Monkeypatch Fixture.
    """

    # Set Prometheus URL
    monkeypatch.setattr(settings, "PROMETHEUS_URL", "http://localhost:9090")


@pytest.fixture
def mock_prometheus_settings_empty(monkeypatch) -> None:
    """
    Mock Empty Prometheus Settings.

    Args:
        monkeypatch: Pytest Monkeypatch Fixture.
    """

    # Set Empty Prometheus URL
    monkeypatch.setattr(settings, "PROMETHEUS_URL", "")


# Redis Fixtures
@pytest.fixture
def redis_health_check() -> RedisHealthCheck:
    """
    Create Redis Health Check Instance.

    Returns:
        RedisHealthCheck: Instance Of Redis Health Check.
    """

    # Return Instance
    return RedisHealthCheck()


@pytest.fixture
def mock_redis_settings(monkeypatch) -> None:
    """
    Mock Redis Settings.

    Args:
        monkeypatch: Pytest Monkeypatch Fixture.
    """

    # Set Redis URL
    monkeypatch.setattr(settings, "REDIS_DEFAULT_URL", "redis://localhost:6379/0")


@pytest.fixture
def mock_redis_settings_empty(monkeypatch) -> None:
    """
    Mock Empty Redis Settings.

    Args:
        monkeypatch: Pytest Monkeypatch Fixture.
    """

    # Set Empty Redis URL
    monkeypatch.setattr(settings, "REDIS_DEFAULT_URL", "")


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
