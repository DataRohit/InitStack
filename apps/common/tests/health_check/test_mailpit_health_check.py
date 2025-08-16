# Standard Library Imports
import smtplib
from unittest.mock import MagicMock
from unittest.mock import patch

# Local Imports
from apps.common.health_checks.mailpit_health_check import MailpitSMTPHealthCheck


# Test Mailpit SMTP Health Check Class
class TestMailpitSMTPHealthCheck:
    """
    Test Mailpit SMTP Health Check Class.
    """

    # Test Identifier Method
    def test_identifier(self, mailpit_health_check: MailpitSMTPHealthCheck) -> None:
        """
        Test Identifier Method Returns Correct Class Name.

        Args:
            mailpit_health_check (MailpitSMTPHealthCheck): Mailpit Health Check Instance.
        """

        # Assert Identifier Returns Class Name
        assert mailpit_health_check.identifier() == "MailpitSMTPHealthCheck"

    # Test Check Status With No Settings Configured
    def test_check_status_no_settings(
        self,
        mailpit_health_check: MailpitSMTPHealthCheck,
        mock_mailpit_settings_empty,
    ) -> None:
        """
        Test Check Status Method When No Settings Are Configured.

        Args:
            mailpit_health_check (MailpitSMTPHealthCheck): Mailpit Health Check Instance.
            mock_mailpit_settings_empty: Mock Empty Mailpit Settings.
        """

        # Run Check Status
        mailpit_health_check.check_status()

        # Assert Error Was Added
        assert len(mailpit_health_check.errors) == 1
        assert "EMAIL_HOST or EMAIL_PORT Not Configured" in str(mailpit_health_check.errors[0])

    # Test Check Status With Only Host Configured
    def test_check_status_only_host(
        self,
        mailpit_health_check: MailpitSMTPHealthCheck,
        monkeypatch,
    ) -> None:
        """
        Test Check Status Method When Only Host Is Configured.

        Args:
            mailpit_health_check (MailpitSMTPHealthCheck): Mailpit Health Check Instance.
            monkeypatch: Pytest Monkeypatch Fixture.
        """

        # Set Only Host Setting
        monkeypatch.setattr("django.conf.settings.EMAIL_HOST", "localhost")
        monkeypatch.setattr("django.conf.settings.EMAIL_PORT", None)

        # Run Check Status
        mailpit_health_check.check_status()

        # Assert Error Was Added
        assert len(mailpit_health_check.errors) == 1
        assert "EMAIL_HOST or EMAIL_PORT Not Configured" in str(mailpit_health_check.errors[0])

    # Test Check Status With Only Port Configured
    def test_check_status_only_port(
        self,
        mailpit_health_check: MailpitSMTPHealthCheck,
        monkeypatch,
    ) -> None:
        """
        Test Check Status Method When Only Port Is Configured.

        Args:
            mailpit_health_check (MailpitSMTPHealthCheck): Mailpit Health Check Instance.
            monkeypatch: Pytest Monkeypatch Fixture.
        """

        # Set Only Port Setting
        monkeypatch.setattr("django.conf.settings.EMAIL_HOST", "")
        monkeypatch.setattr("django.conf.settings.EMAIL_PORT", 1025)

        # Run Check Status
        mailpit_health_check.check_status()

        # Assert Error Was Added
        assert len(mailpit_health_check.errors) == 1
        assert "EMAIL_HOST or EMAIL_PORT Not Configured" in str(mailpit_health_check.errors[0])

    # Test Check Status With Valid Settings And Successful Connection
    @patch("smtplib.SMTP")
    def test_check_status_success(
        self,
        mock_smtp: MagicMock,
        mailpit_health_check: MailpitSMTPHealthCheck,
        mock_mailpit_settings,
    ) -> None:
        """
        Test Check Status Method With Valid Settings And Successful Connection.

        Args:
            mock_smtp (MagicMock): Mock SMTP Class.
            mailpit_health_check (MailpitSMTPHealthCheck): Mailpit Health Check Instance.
            mock_mailpit_settings: Mock Mailpit Settings.
        """

        # Configure Mock
        mock_smtp_instance = MagicMock()
        mock_smtp_instance.__enter__.return_value = mock_smtp_instance
        mock_smtp.return_value = mock_smtp_instance

        # Run Check Status
        mailpit_health_check.check_status()

        # Assert No Errors Were Added
        assert len(mailpit_health_check.errors) == 0

        # Assert SMTP Was Created With Correct Parameters
        mock_smtp.assert_called_once_with(host="localhost", port=1025, timeout=3)

        # Assert NOOP Was Called
        mock_smtp_instance.noop.assert_called_once()

    # Test Check Status With SMTP Exception
    @patch("smtplib.SMTP")
    def test_check_status_smtp_exception(
        self,
        mock_smtp: MagicMock,
        mailpit_health_check: MailpitSMTPHealthCheck,
        mock_mailpit_settings,
    ) -> None:
        """
        Test Check Status Method With SMTP Exception.

        Args:
            mock_smtp (MagicMock): Mock SMTP Class.
            mailpit_health_check (MailpitSMTPHealthCheck): Mailpit Health Check Instance.
            mock_mailpit_settings: Mock Mailpit Settings.
        """

        # Configure Mock To Raise Exception
        mock_smtp.side_effect = smtplib.SMTPException("SMTP Connection Error")

        # Run Check Status
        mailpit_health_check.check_status()

        # Assert Error Was Added
        assert len(mailpit_health_check.errors) == 1
        assert "SMTP Connection Error" in str(mailpit_health_check.errors[0])

    # Test Check Status With OS Error
    @patch("smtplib.SMTP")
    def test_check_status_os_error(
        self,
        mock_smtp: MagicMock,
        mailpit_health_check: MailpitSMTPHealthCheck,
        mock_mailpit_settings,
    ) -> None:
        """
        Test Check Status Method With OS Error.

        Args:
            mock_smtp (MagicMock): Mock SMTP Class.
            mailpit_health_check (MailpitSMTPHealthCheck): Mailpit Health Check Instance.
            mock_mailpit_settings: Mock Mailpit Settings.
        """

        # Configure Mock To Raise Exception
        mock_smtp.side_effect = OSError("Connection Refused")

        # Run Check Status
        mailpit_health_check.check_status()

        # Assert Error Was Added
        assert len(mailpit_health_check.errors) == 1
        assert "Connection Refused" in str(mailpit_health_check.errors[0])

    # Test Check Status With NOOP Exception
    @patch("smtplib.SMTP")
    def test_check_status_noop_exception(
        self,
        mock_smtp: MagicMock,
        mailpit_health_check: MailpitSMTPHealthCheck,
        mock_mailpit_settings,
    ) -> None:
        """
        Test Check Status Method With NOOP Exception.

        Args:
            mock_smtp (MagicMock): Mock SMTP Class.
            mailpit_health_check (MailpitSMTPHealthCheck): Mailpit Health Check Instance.
            mock_mailpit_settings: Mock Mailpit Settings.
        """

        # Configure Mock
        mock_smtp_instance = MagicMock()
        mock_smtp_instance.__enter__.return_value = mock_smtp_instance
        mock_smtp_instance.noop.side_effect = smtplib.SMTPException("NOOP Command Failed")
        mock_smtp.return_value = mock_smtp_instance

        # Run Check Status
        mailpit_health_check.check_status()

        # Assert Error Was Added
        assert len(mailpit_health_check.errors) == 1
        assert "NOOP Command Failed" in str(mailpit_health_check.errors[0])

    # Test Check Status With Generic Exception
    @patch("smtplib.SMTP")
    def test_check_status_generic_exception(
        self,
        mock_smtp: MagicMock,
        mailpit_health_check: MailpitSMTPHealthCheck,
        mock_mailpit_settings,
    ) -> None:
        """
        Test Check Status Method With Generic Exception.

        Args:
            mock_smtp (MagicMock): Mock SMTP Class.
            mailpit_health_check (MailpitSMTPHealthCheck): Mailpit Health Check Instance.
            mock_mailpit_settings: Mock Mailpit Settings.
        """

        # Configure Mock To Raise Exception
        mock_smtp.side_effect = Exception("Unexpected Error")

        # Run Check Status
        mailpit_health_check.check_status()

        # Assert Error Was Added
        assert len(mailpit_health_check.errors) == 1
        assert "Unexpected Error" in str(mailpit_health_check.errors[0])

    # Test Critical Service Attribute
    def test_critical_service_attribute(self, mailpit_health_check: MailpitSMTPHealthCheck) -> None:
        """
        Test Critical Service Attribute Is Set Correctly.

        Args:
            mailpit_health_check (MailpitSMTPHealthCheck): Mailpit Health Check Instance.
        """

        # Assert Critical Service Is True
        assert mailpit_health_check.critical_service is True
