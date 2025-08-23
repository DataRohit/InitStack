# Standard Library Imports
import smtplib
from unittest.mock import MagicMock
from unittest.mock import patch

# Third Party Imports
import pytest
from django.conf import settings

# Local Imports
from apps.common.health_checks.mailpit_health_check import MailpitSMTPHealthCheck


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


# Test Mailpit SMTP Health Check Identifier
def test_identifier(mailpit_health_check: MailpitSMTPHealthCheck) -> None:
    """
    Test Identifier Method Returns Correct Class Name.
    """

    # Assert Identifier Returns Class Name
    assert mailpit_health_check.identifier() == "MailpitSMTPHealthCheck"


# Test Check Status With No Settings Configured
def test_check_status_no_settings(
    mailpit_health_check: MailpitSMTPHealthCheck,
    mock_mailpit_settings_empty,
) -> None:
    """
    Test Check Status Method When No Settings Are Configured.
    """

    # Run Check Status
    mailpit_health_check.check_status()

    # Assert Error Was Added
    assert len(mailpit_health_check.errors) == 1
    assert "EMAIL_HOST or EMAIL_PORT Not Configured" in str(mailpit_health_check.errors[0])


# Test Check Status With Only Host Configured
def test_check_status_only_host(
    mailpit_health_check: MailpitSMTPHealthCheck,
    monkeypatch,
) -> None:
    """
    Test Check Status Method When Only Host Is Configured.
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
    mailpit_health_check: MailpitSMTPHealthCheck,
    monkeypatch,
) -> None:
    """
    Test Check Status Method When Only Port Is Configured.
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
    mock_smtp: MagicMock,
    mailpit_health_check: MailpitSMTPHealthCheck,
    mock_mailpit_settings,
) -> None:
    """
    Test Check Status Method With Valid Settings And Successful Connection.
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
    mock_smtp: MagicMock,
    mailpit_health_check: MailpitSMTPHealthCheck,
    mock_mailpit_settings,
) -> None:
    """
    Test Check Status Method With SMTP Exception.
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
    mock_smtp: MagicMock,
    mailpit_health_check: MailpitSMTPHealthCheck,
    mock_mailpit_settings,
) -> None:
    """
    Test Check Status Method With OS Error.
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
    mock_smtp: MagicMock,
    mailpit_health_check: MailpitSMTPHealthCheck,
    mock_mailpit_settings,
) -> None:
    """
    Test Check Status Method With NOOP Exception.
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
    mock_smtp: MagicMock,
    mailpit_health_check: MailpitSMTPHealthCheck,
    mock_mailpit_settings,
) -> None:
    """
    Test Check Status Method With Generic Exception.
    """

    # Configure Mock To Raise Exception
    mock_smtp.side_effect = Exception("Unexpected Error")

    # Run Check Status
    mailpit_health_check.check_status()

    # Assert Error Was Added
    assert len(mailpit_health_check.errors) == 1
    assert "Unexpected Error" in str(mailpit_health_check.errors[0])


# Test Critical Service Attribute
def test_critical_service_attribute(mailpit_health_check: MailpitSMTPHealthCheck) -> None:
    """
    Test Critical Service Attribute Is Set Correctly.
    """

    # Assert Critical Service Is True
    assert mailpit_health_check.critical_service is True
