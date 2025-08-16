# Standard Library Imports
import smtplib

# Third Party Imports
from django.conf import settings
from health_check.backends import BaseHealthCheckBackend
from health_check.exceptions import HealthCheckException


# Mailpit SMTP Health Check Class
class MailpitSMTPHealthCheck(BaseHealthCheckBackend):
    """
    Mailpit SMTP Health Check Class.

    Attributes:
        critical_service (bool): Whether The Service Is Critical.

    Methods:
        check_status() -> None: Check Status Function To Check The Health Of The Mailpit SMTP Service.
        identifier() -> str: Identifier Function To Return The Name Of The Health Check.
    """

    # Attributes
    critical_service: bool = True

    # Check Status Method
    def check_status(self) -> None:
        """
        Check Status Function To Check The Health Of The Mailpit SMTP Service.

        Raises:
            HealthCheckException: If The Mailpit SMTP Service Is Not Responding.
        """

        try:
            # Get The Email Host And Port From Settings
            host: str = getattr(settings, "EMAIL_HOST", None)
            port: int = getattr(settings, "EMAIL_PORT", None)

            # If The Email Host Or Port Is Not Configured
            if not host or not port:
                # Set The Error Message
                error_message: str = "EMAIL_HOST or EMAIL_PORT Not Configured"

                # Raise The HealthCheckException
                raise HealthCheckException(error_message)

            # Try Connecting To Mailpit's SMTP Server
            with smtplib.SMTP(host=host, port=port, timeout=3) as server:
                # Lightweight Check Without Sending Email
                server.noop()

        # Catch SMTP Or OS Exceptions
        except (smtplib.SMTPException, OSError) as e:
            # Create Health Check Exception With Original Error Message
            error = HealthCheckException(str(e))

            # Add The Error To The HealthCheck
            self.add_error(error)

        # Catch Any Exception
        except Exception as e:
            # Create Health Check Exception With Original Error Message
            error = HealthCheckException(str(e))

            # Add The Error To The HealthCheck
            self.add_error(error)

    # Identifier Function
    def identifier(self) -> str:
        """
        Identifier Function To Return The Name Of The Health Check.

        Returns:
            str: The Name Of The Health Check.
        """

        # Return The Class Name
        return self.__class__.__name__
