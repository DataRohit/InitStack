# Standard Library Imports
from urllib.parse import urlparse

# Third Party Imports
import redis
from django.conf import settings
from health_check.backends import BaseHealthCheckBackend
from health_check.exceptions import HealthCheckException


# Redis Health Check Class
class RedisHealthCheck(BaseHealthCheckBackend):
    """
    Redis Health Check Class.

    Attributes:
        critical_service (bool): Whether The Service Is Critical.

    Methods:
        check_status() -> None: Check Status Function To Verify Redis Is Reachable And Healthy.
        identifier() -> str: Identifier Function To Return The Name Of The Health Check.
    """

    # Attributes
    critical_service: bool = True

    # Check Status Method
    def check_status(self) -> None:
        """
        Check Status Function To Verify Redis Is Reachable And Healthy.

        Raises:
            HealthCheckException: If The Redis Server Is Not Responding As Expected.
        """
        try:
            # Get The Redis URL From Settings
            redis_url: str = getattr(settings, "REDIS_DEFAULT_URL", None)

            # If The Redis URL Is Not Configured
            if not redis_url:
                # Set The Error Message
                error_message: str = "REDIS_DEFAULT_URL Not Configured"

                # Raise The HealthCheckException
                raise HealthCheckException(error_message)

            # Parse The Redis URL
            parsed = urlparse(redis_url)

            # Create Redis Client
            client: redis.Redis = redis.Redis(
                host=parsed.hostname,
                port=parsed.port or 6379,
                db=int(parsed.path.lstrip("/") or 0),
                password=parsed.password,
                socket_timeout=3,
            )

            # Check If Redis Responds To Ping
            if client.ping() is not True:
                # Set The Error Message
                error_message: str = "Redis Did Not Respond To PING"

                # Raise The HealthCheckException
                raise HealthCheckException(error_message)

        # Catch Redis Exceptions
        except redis.RedisError as e:
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
