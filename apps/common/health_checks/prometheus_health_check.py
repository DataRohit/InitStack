# Third Party Imports
import requests
from django.conf import settings
from health_check.backends import BaseHealthCheckBackend
from health_check.exceptions import HealthCheckException


# Prometheus Health Check Class
class PrometheusHealthCheck(BaseHealthCheckBackend):
    """
    Prometheus Server Health Check Class.

    Attributes:
        critical_service (bool): Whether The Service Is Critical.

    Methods:
        check_status() -> None: Check Status Function To Verify Prometheus Is Healthy.
        identifier() -> str: Identifier Function To Return The Name Of The Health Check.
    """

    # Attributes
    critical_service: bool = True

    # Check Status Method
    def check_status(self) -> None:
        """
        Check Status Function To Verify Prometheus Is Healthy.

        Raises:
            HealthCheckException: If The Prometheus Health Endpoint Is Not Healthy.
        """

        try:
            # Get The Prometheus URL From Settings
            prometheus_url: str = settings.PROMETHEUS_URL

            # If The Prometheus URL Is Not Configured
            if not prometheus_url:
                # Set The Error Message
                error_message: str = "PROMETHEUS_URL Not Configured"

                # Raise The HealthCheckException
                raise HealthCheckException(error_message)

            # Build The Health Endpoint
            endpoint: str = f"{prometheus_url.rstrip('/')}/-/healthy"

            # Make The Request To Prometheus Health Endpoint
            response: requests.Response = requests.get(url=endpoint, timeout=3)

            # If The Response Status Code Is Not 200
            if response.status_code != 200:  # noqa: PLR2004
                # Set The Error Message
                error_message: str = f"Prometheus Returned Unexpected Status: {response.status_code}"

                # Raise The HealthCheckException
                raise HealthCheckException(error_message)

        # Catch Request Exceptions
        except requests.RequestException as e:
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
