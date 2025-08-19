# Standard Library Imports
import datetime
import logging
import socket
import time
from typing import Any
from typing import ClassVar

# Third Party Imports
import psutil
from django.conf import settings
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.authentication import BaseAuthentication
from rest_framework.permissions import AllowAny
from rest_framework.permissions import BasePermission
from rest_framework.renderers import JSONRenderer
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

# Local Imports
from apps.common.renderers import GenericJSONRenderer
from apps.common.serializers import Generic500ResponseSerializer
from apps.system.opentelemetry.views.health_view_metrics import health_check_duration_ms
from apps.system.opentelemetry.views.health_view_metrics import health_check_errors_total
from apps.system.opentelemetry.views.health_view_metrics import health_check_requests_total
from apps.system.serializers import HealthResponseSerializer
from apps.system.serializers import SystemDiskSerializer
from apps.system.serializers import SystemInfoSerializer
from apps.system.serializers import SystemMemorySerializer

# Constants
DEGRADED_THRESHOLD: int = 80
UNHEALTHY_THRESHOLD: int = 90

# Initialize Logger
logger: logging.Logger = logging.getLogger(__name__)


# Health Check View Class
class HealthCheckView(APIView):
    """
    Health Check API View Class.

    Attributes:
        renderer_classes (ClassVar[list[JSONRenderer]]): List Of Response Renderers.
        authentication_classes (ClassVar[list[BaseAuthentication]]): List Of Authentication Classes.
        permission_classes (ClassVar[list[BasePermission]]): List Of Permission Classes.
        http_method_names (ClassVar[list[str]]): List Of Allowed HTTP Methods.
        object_label (ClassVar[str]): Label For The Object Being Processed.
    """

    # Attributes
    renderer_classes: ClassVar[list[JSONRenderer]] = [GenericJSONRenderer]
    authentication_classes: ClassVar[list[BaseAuthentication]] = []
    permission_classes: ClassVar[list[BasePermission]] = [AllowAny]
    http_method_names: ClassVar[list[str]] = ["get"]
    object_label: ClassVar[str] = "data"

    # Get Method For Health Check
    @extend_schema(
        operation_id="Health Check",
        request=None,
        responses={
            status.HTTP_200_OK: HealthResponseSerializer,
            status.HTTP_503_SERVICE_UNAVAILABLE: HealthResponseSerializer,
            status.HTTP_500_INTERNAL_SERVER_ERROR: Generic500ResponseSerializer,
        },
        description="Returns The Health Status of the API along with System Metrics",
        summary="Retrieve Health Status And System Metrics",
        tags=["Health Check"],
    )
    def get(self, request: Request) -> Response:
        """
        Process Health Check Request.

        Args:
            request (Request): HTTP Request Object.

        Returns:
            Response: HTTP Response With Health Status And System Metrics.

        Raises:
            Exception: For Any Unexpected Errors During Health Check.
        """

        # Start Duration Timer
        start_time: float = time.perf_counter()

        # Increment Requests Counter
        health_check_requests_total.add(
            1,
            attributes={
                "method": "GET",
                "endpoint": "health",
            },
        )

        try:
            # Get System Memory Usage
            memory_info: Any = psutil.virtual_memory()

            # Serialize System Memory Usage
            system_memory = SystemMemorySerializer(
                data={
                    "total": memory_info.total,
                    "available": memory_info.available,
                    "percent": memory_info.percent,
                    "used": memory_info.used,
                    "free": memory_info.free,
                },
            )

            # Validate System Memory Usage
            system_memory.is_valid(raise_exception=True)

            # Get Disk Usage
            disk_info: Any = psutil.disk_usage("/")

            # Serialize System Disk Usage
            system_disk = SystemDiskSerializer(
                data={
                    "total": disk_info.total,
                    "used": disk_info.used,
                    "free": disk_info.free,
                    "percent": disk_info.percent,
                },
            )

            # Validate System Disk Usage
            system_disk.is_valid(raise_exception=True)

            # Serialize System Information
            system_info = SystemInfoSerializer(
                data={
                    "hostname": socket.gethostname(),
                    "cpu_percent": psutil.cpu_percent(),
                    "memory": system_memory.validated_data,
                    "disk": system_disk.validated_data,
                },
            )

            # Validate System Information
            system_info.is_valid(raise_exception=True)

            # Serialize Health Response
            health_data = HealthResponseSerializer(
                data={
                    "status": "healthy",
                    "app": settings.PROJECT_NAME,
                    "version": settings.PROJECT_VERSION,
                    "environment": settings.SENTRY_ENVIRONMENT,
                    "timestamp": datetime.datetime.now(tz=datetime.UTC).isoformat(),
                    "system": system_info.validated_data,
                },
            )

            # Validate Health Response
            health_data.is_valid(raise_exception=True)

            # Get The Data
            health_data = health_data.data

            # Check For Unhealthy State
            if (
                health_data["system"]["memory"]["percent"] > UNHEALTHY_THRESHOLD
                or health_data["system"]["disk"]["percent"] > UNHEALTHY_THRESHOLD
                or health_data["system"]["cpu_percent"] > UNHEALTHY_THRESHOLD
            ):
                # Update Status To Unhealthy
                health_data["status"] = "unhealthy"

            # Check For Degraded State
            elif (
                health_data["system"]["memory"]["percent"] > DEGRADED_THRESHOLD
                or health_data["system"]["disk"]["percent"] > DEGRADED_THRESHOLD
                or health_data["system"]["cpu_percent"] > DEGRADED_THRESHOLD
            ):
                # Update Status To Degraded
                health_data["status"] = "degraded"

            # If Status Not Healthy
            if health_data["status"] != "healthy":
                # Calculate Duration Milliseconds
                duration_ms: float = (time.perf_counter() - start_time) * 1000.0

                # Record Duration Histogram
                health_check_duration_ms.record(
                    duration_ms,
                    attributes={
                        "method": "GET",
                        "endpoint": "health",
                        "status": "unhealthy",
                    },
                )

                # Return Unhealthy Response
                return Response(
                    data=health_data,
                    status=status.HTTP_503_SERVICE_UNAVAILABLE,
                )

            # Return Healthy Response
            # Calculate Duration Milliseconds
            duration_ms: float = (time.perf_counter() - start_time) * 1000.0

            # Record Duration Histogram
            health_check_duration_ms.record(
                duration_ms,
                attributes={
                    "method": "GET",
                    "endpoint": "health",
                    "status": "healthy",
                },
            )

            return Response(
                data=health_data,
                status=status.HTTP_200_OK,
            )

        except psutil.Error as e:
            # Set Error Message
            error_message: str = f"Health Check Failed - System Metrics Error: {e!s}"

            # Log Error
            logger.exception(
                error_message,
                extra={"error_type": "psutil", "error": str(e)},
            )

            # Increment Errors Counter
            health_check_errors_total.add(
                1,
                attributes={
                    "method": "GET",
                    "endpoint": "health",
                    "type": "psutil",
                },
            )

            # Calculate Duration Milliseconds
            duration_ms: float = (time.perf_counter() - start_time) * 1000.0

            # Record Duration Histogram
            health_check_duration_ms.record(
                duration_ms,
                attributes={
                    "method": "GET",
                    "endpoint": "health",
                    "status": "error",
                },
            )

            # Return Error Response
            return Response(
                data={"error": "Internal Server Error"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        except Exception as e:
            # Set Error Message
            error_message: str = f"Health Check Failed - Unexpected Error: {e!s}"

            # Log Error
            logger.exception(
                error_message,
                extra={"error_type": "unexpected", "error": str(e)},
            )

            # Increment Errors Counter
            health_check_errors_total.add(
                1,
                attributes={
                    "method": "GET",
                    "endpoint": "health",
                    "type": "unexpected",
                },
            )

            # Calculate Duration Milliseconds
            duration_ms: float = (time.perf_counter() - start_time) * 1000.0

            # Record Duration Histogram
            health_check_duration_ms.record(
                duration_ms,
                attributes={
                    "method": "GET",
                    "endpoint": "health",
                    "status": "error",
                },
            )

            # Return Error Response
            return Response(
                data={"error": "Internal Server Error"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


# Exports
__all__: list[str] = ["HealthCheckView"]
