# Standard Library Imports
from unittest.mock import MagicMock
from unittest.mock import patch

# Local Imports
from apps.common.health_checks.elasticsearch_health_check import ElasticsearchHealthCheck


# Test Elasticsearch Health Check Class
class TestElasticsearchHealthCheck:
    """
    Test Elasticsearch Health Check Class.
    """

    # Test Identifier Method
    def test_identifier(self, elasticsearch_health_check: ElasticsearchHealthCheck) -> None:
        """
        Test Identifier Method Returns Correct Class Name.

        Args:
            elasticsearch_health_check (ElasticsearchHealthCheck): Elasticsearch Health Check Instance.
        """

        # Assert Identifier Returns Class Name
        assert elasticsearch_health_check.identifier() == "ElasticsearchHealthCheck"

    # Test Check Status With No URL Configured
    def test_check_status_no_url(
        self,
        elasticsearch_health_check: ElasticsearchHealthCheck,
        mock_elasticsearch_settings_empty,
    ) -> None:
        """
        Test Check Status Method When No URL Is Configured.

        Args:
            elasticsearch_health_check (ElasticsearchHealthCheck): Elasticsearch Health Check Instance.
            mock_elasticsearch_settings_empty: Mock Empty Elasticsearch Settings.
        """

        # Run Check Status
        elasticsearch_health_check.check_status()

        # Assert Error Was Added
        assert len(elasticsearch_health_check.errors) == 1
        assert "ELASTICSEARCH_URL Not Configured" in str(elasticsearch_health_check.errors[0])

    # Test Check Status With Valid URL And Successful Ping
    @patch("apps.common.health_checks.elasticsearch_health_check.Elasticsearch")
    def test_check_status_success(
        self,
        mock_es_class: MagicMock,
        elasticsearch_health_check: ElasticsearchHealthCheck,
        mock_elasticsearch_settings,
    ) -> None:
        """
        Test Check Status Method With Valid URL And Successful Ping.

        Args:
            mock_es_class (MagicMock): Mock Elasticsearch Class.
            elasticsearch_health_check (ElasticsearchHealthCheck): Elasticsearch Health Check Instance.
            mock_elasticsearch_settings: Mock Elasticsearch Settings.
        """

        # Configure Mock
        mock_es_instance = MagicMock()
        mock_es_instance.ping.return_value = True
        mock_es_class.return_value = mock_es_instance

        # Run Check Status
        elasticsearch_health_check.check_status()

        # Assert No Errors Were Added
        assert len(elasticsearch_health_check.errors) == 0

        # Assert Elasticsearch Was Created With Correct Parameters
        mock_es_class.assert_called_once()
        call_kwargs = mock_es_class.call_args.kwargs

        # Check Hosts Configuration
        assert "hosts" in call_kwargs
        assert len(call_kwargs["hosts"]) == 1
        assert call_kwargs["hosts"][0]["host"] == "localhost"
        assert call_kwargs["hosts"][0]["port"] == 9200  # noqa: PLR2004
        assert call_kwargs["hosts"][0]["scheme"] == "http"

        # Check Auth Configuration
        assert "http_auth" in call_kwargs
        assert call_kwargs["http_auth"] == ("user", "pass")

        # Check Verify Certs
        assert "verify_certs" in call_kwargs
        assert call_kwargs["verify_certs"] is True

    # Test Check Status With Valid URL But Failed Ping
    @patch("apps.common.health_checks.elasticsearch_health_check.Elasticsearch")
    def test_check_status_failed_ping(
        self,
        mock_es_class: MagicMock,
        elasticsearch_health_check: ElasticsearchHealthCheck,
        mock_elasticsearch_settings,
    ) -> None:
        """
        Test Check Status Method With Valid URL But Failed Ping.

        Args:
            mock_es_class (MagicMock): Mock Elasticsearch Class.
            elasticsearch_health_check (ElasticsearchHealthCheck): Elasticsearch Health Check Instance.
            mock_elasticsearch_settings: Mock Elasticsearch Settings.
        """

        # Configure Mock
        mock_es_instance = MagicMock()
        mock_es_instance.ping.return_value = False
        mock_es_class.return_value = mock_es_instance

        # Run Check Status
        elasticsearch_health_check.check_status()

        # Assert Error Was Added
        assert len(elasticsearch_health_check.errors) == 1
        assert "Elasticsearch Cluster Is Not Responding" in str(elasticsearch_health_check.errors[0])

    # Test Check Status With Exception During Ping
    @patch("apps.common.health_checks.elasticsearch_health_check.Elasticsearch")
    def test_check_status_exception(
        self,
        mock_es_class: MagicMock,
        elasticsearch_health_check: ElasticsearchHealthCheck,
        mock_elasticsearch_settings,
    ) -> None:
        """
        Test Check Status Method With Exception During Ping.

        Args:
            mock_es_class (MagicMock): Mock Elasticsearch Class.
            elasticsearch_health_check (ElasticsearchHealthCheck): Elasticsearch Health Check Instance.
            mock_elasticsearch_settings: Mock Elasticsearch Settings.
        """

        # Configure Mock
        mock_es_instance = MagicMock()
        mock_es_instance.ping.side_effect = Exception("Connection Error")
        mock_es_class.return_value = mock_es_instance

        # Run Check Status
        elasticsearch_health_check.check_status()

        # Assert Error Was Added
        assert len(elasticsearch_health_check.errors) == 1
        assert "Connection Error" in str(elasticsearch_health_check.errors[0])

    # Test Check Status With Different URL Scheme
    @patch("apps.common.health_checks.elasticsearch_health_check.Elasticsearch")
    def test_check_status_different_scheme(
        self,
        mock_es_class: MagicMock,
        elasticsearch_health_check: ElasticsearchHealthCheck,
        monkeypatch,
    ) -> None:
        """
        Test Check Status Method With Different URL Scheme.

        Args:
            mock_es_class (MagicMock): Mock Elasticsearch Class.
            elasticsearch_health_check (ElasticsearchHealthCheck): Elasticsearch Health Check Instance.
            monkeypatch: Pytest Monkeypatch Fixture.
        """

        # Set Elasticsearch URL With HTTPS Scheme
        monkeypatch.setattr("django.conf.settings.ELASTICSEARCH_URL", "https://localhost:9200")

        # Configure Mock
        mock_es_instance = MagicMock()
        mock_es_instance.ping.return_value = True
        mock_es_class.return_value = mock_es_instance

        # Run Check Status
        elasticsearch_health_check.check_status()

        # Assert No Errors Were Added
        assert len(elasticsearch_health_check.errors) == 0

        # Assert Elasticsearch Was Created With Correct Parameters
        mock_es_class.assert_called_once()
        call_kwargs = mock_es_class.call_args.kwargs

        # Check Scheme Is HTTPS
        assert call_kwargs["hosts"][0]["scheme"] == "https"

    # Test Check Status With No Auth In URL
    @patch("apps.common.health_checks.elasticsearch_health_check.Elasticsearch")
    def test_check_status_no_auth(
        self,
        mock_es_class: MagicMock,
        elasticsearch_health_check: ElasticsearchHealthCheck,
        monkeypatch,
    ) -> None:
        """
        Test Check Status Method With No Auth In URL.

        Args:
            mock_es_class (MagicMock): Mock Elasticsearch Class.
            elasticsearch_health_check (ElasticsearchHealthCheck): Elasticsearch Health Check Instance.
            monkeypatch: Pytest Monkeypatch Fixture.
        """

        # Set Elasticsearch URL Without Auth
        monkeypatch.setattr("django.conf.settings.ELASTICSEARCH_URL", "http://localhost:9200")

        # Configure Mock
        mock_es_instance = MagicMock()
        mock_es_instance.ping.return_value = True
        mock_es_class.return_value = mock_es_instance

        # Run Check Status
        elasticsearch_health_check.check_status()

        # Assert No Errors Were Added
        assert len(elasticsearch_health_check.errors) == 0

        # Assert Elasticsearch Was Created With Correct Parameters
        mock_es_class.assert_called_once()
        call_kwargs = mock_es_class.call_args.kwargs

        # Check Auth Is None
        assert call_kwargs["http_auth"] is None

    # Test Critical Service Attribute
    def test_critical_service_attribute(self, elasticsearch_health_check: ElasticsearchHealthCheck) -> None:
        """
        Test Critical Service Attribute Is Set Correctly.

        Args:
            elasticsearch_health_check (ElasticsearchHealthCheck): Elasticsearch Health Check Instance.
        """

        # Assert Critical Service Is True
        assert elasticsearch_health_check.critical_service is True
