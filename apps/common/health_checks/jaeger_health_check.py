# Third Party Imports
import requests
from django.conf import settings
from health_check.backends import BaseHealthCheckBackend
from health_check.exceptions import HealthCheckException


# Jaeger Health Check Class
class JaegerHealthCheck(BaseHealthCheckBackend):
    """
    Jaeger Query API Health Check Class.

    Attributes:
        critical_service (bool): Whether The Service Is Critical.

    Methods:
        check_status() -> None: Check Status Function To Verify Jaeger Query API Is Reachable And Healthy.
        identifier() -> str: Identifier Function To Return The Name Of The Health Check.
    """

    # Attributes
    critical_service: bool = True

    # Check Status Method
    def check_status(self) -> None:
        """
        Check Status Function To Verify Jaeger Query API Is Reachable And Healthy.

        Raises:
            HealthCheckException: If The Jaeger Query API Is Not Responding As Expected.
        """

        try:
            # Get The Jaeger Query URL From Settings
            jaeger_url: str = settings.JAEGER_QUERY_URL

            # If The Jaeger Query URL Is Not Configured
            if not jaeger_url:
                # Set The Error Message
                error_message: str = "JAEGER_QUERY_URL Not Configured"

                # Raise The HealthCheckException
                raise HealthCheckException(error_message)

            # Build The Services Endpoint
            endpoint: str = f"{jaeger_url.rstrip('/')}/api/services"

            # Make The Request To Jaeger Query API
            response: requests.Response = requests.get(url=endpoint, timeout=3)

            # If The Response Status Code Is Not 200
            if response.status_code != 200:  # noqa: PLR2004
                # Set The Error Message
                error_message: str = f"Jaeger Returned Unexpected Status: {response.status_code}"

                # Raise The HealthCheckException
                raise HealthCheckException(error_message)

            # Parse The JSON Response
            data: dict[str, object] = response.json()

            # If The Response JSON Does Not Contain The Expected 'data' Key
            if "data" not in data:
                # Set The Error Message
                error_message: str = "Jaeger API Response Missing 'data'"

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
