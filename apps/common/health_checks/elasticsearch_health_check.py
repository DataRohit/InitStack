# Standard Library Imports
from urllib.parse import ParseResult
from urllib.parse import urlparse

# Third Party Imports
from django.conf import settings
from elasticsearch import Elasticsearch
from health_check.backends import BaseHealthCheckBackend
from health_check.exceptions import HealthCheckException


# Elasticsearch Health Check Class
class ElasticsearchHealthCheck(BaseHealthCheckBackend):
    """
    Elasticsearch Health Check Class.

    Attributes:
        critical_service (bool): Whether The Service Is Critical.

    Methods:
        check_status() -> None: Check Status Function To Check The Health Of The Elasticsearch Service.
        identifier() -> str: Identifier Function To Return The Name Of The Health Check.
    """

    # Attributes
    critical_service: bool = True

    # Check Status Method
    def check_status(self) -> None:
        """
        Check Status Function To Check The Health Of The Elasticsearch Service.

        Raises:
            HealthCheckException: If The Elasticsearch Service Is Not Responding.
        """

        try:
            # Get The Elasticsearch URL From Settings
            es_url: str = settings.ELASTICSEARCH_URL

            # If The Elasticsearch URL Is Not Configured
            if not es_url:
                # Set The Error Message
                error_message: str = "ELASTICSEARCH_URL Not Configured"

                # Raise The HealthCheckException
                raise HealthCheckException(error_message)

            # Parse The Elasticsearch URL
            parsed_url: ParseResult = urlparse(url=es_url)

            # Create An Elasticsearch Client
            es = Elasticsearch(
                hosts=[
                    {
                        "host": parsed_url.hostname,
                        "port": parsed_url.port,
                        "scheme": parsed_url.scheme if parsed_url.scheme != "elasticsearch" else "http",
                    },
                ],
                http_auth=(parsed_url.username, parsed_url.password)
                if parsed_url.username and parsed_url.password
                else None,
                verify_certs=True,
            )

            # If The Elasticsearch Cluster Is Not Responding
            if not es.ping():
                # Set The Error Message
                error_message: str = "Elasticsearch Cluster Is Not Responding"

                # Raise The HealthCheckException
                raise HealthCheckException(error_message)

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
