# Standard Library Imports
from typing import ClassVar

# Third Party Imports
from drf_spectacular.utils import OpenApiExample
from drf_spectacular.utils import extend_schema_serializer
from rest_framework import serializers
from rest_framework import status


# System Memory Serializer
class SystemMemorySerializer(serializers.Serializer):
    """
    System Memory Information Model

    Attributes:
        total (int): Total Physical Memory In Bytes
        available (int): Available Memory In Bytes
        percent (float): Percentage Of Memory In Use
        used (int): Used Memory In Bytes
        free (int): Free Memory In Bytes
    """

    # Total Memory Bytes
    total: serializers.IntegerField = serializers.IntegerField(
        required=True,
        help_text="Total Physical Memory In Bytes",
        min_value=0,
    )

    # Available Memory Bytes
    available: serializers.IntegerField = serializers.IntegerField(
        required=True,
        help_text="Available Memory In Bytes",
        min_value=0,
    )

    # Percent Used
    percent: serializers.FloatField = serializers.FloatField(
        required=True,
        help_text="Percentage Of Memory In Use",
        min_value=0.0,
        max_value=100.0,
    )

    # Used Memory Bytes
    used: serializers.IntegerField = serializers.IntegerField(
        required=True,
        help_text="Used Memory In Bytes",
        min_value=0,
    )

    # Free Memory Bytes
    free: serializers.IntegerField = serializers.IntegerField(
        required=True,
        help_text="Free Memory In Bytes",
        min_value=0,
    )

    # Meta Class
    class Meta:
        """
        Meta Class For System Memory Serializer.

        Attributes:
            ref_name (ClassVar[str]): Reference Name For The Serializer.
        """

        # Set Reference Name
        ref_name: ClassVar[str] = "SystemMemory"


# System Disk Serializer
class SystemDiskSerializer(serializers.Serializer):
    """
    System Disk Usage Information Model

    Attributes:
        total (int): Total Disk Space In Bytes
        used (int): Used Disk Space In Bytes
        free (int): Free Disk Space In Bytes
        percent (float): Percentage Of Disk Space Used
    """

    # Total Disk Bytes
    total: serializers.IntegerField = serializers.IntegerField(
        required=True,
        help_text="Total Disk Space In Bytes",
        min_value=0,
    )

    # Used Disk Bytes
    used: serializers.IntegerField = serializers.IntegerField(
        required=True,
        help_text="Used Disk Space In Bytes",
        min_value=0,
    )

    # Free Disk Bytes
    free: serializers.IntegerField = serializers.IntegerField(
        required=True,
        help_text="Free Disk Space In Bytes",
        min_value=0,
    )

    # Percent Used
    percent: serializers.FloatField = serializers.FloatField(
        required=True,
        help_text="Percentage Of Disk Space Used",
        min_value=0.0,
        max_value=100.0,
    )

    # Meta Class
    class Meta:
        """
        Meta Class For System Disk Serializer.

        Attributes:
            ref_name (ClassVar[str]): Reference Name For The Serializer.
        """

        # Set Reference Name
        ref_name: ClassVar[str] = "SystemDisk"


# System Info Serializer
class SystemInfoSerializer(serializers.Serializer):
    """
    System Information Model

    Attributes:
        hostname (str): System Hostname
        cpu_percent (float): Current CPU Usage Percentage
        memory (SystemMemorySerializer): Memory Usage Information
        disk (SystemDiskSerializer): Disk Usage Information
    """

    # Hostname Value
    hostname: serializers.CharField = serializers.CharField(
        required=True,
        help_text="System Hostname",
        max_length=255,
        allow_blank=False,
    )

    # CPU Percent
    cpu_percent: serializers.FloatField = serializers.FloatField(
        required=True,
        help_text="Current CPU Usage Percentage",
        min_value=0.0,
        max_value=100.0,
    )

    # Memory Section
    memory: SystemMemorySerializer = SystemMemorySerializer(
        required=True,
        help_text="Memory Usage Information",
    )

    # Disk Section
    disk: SystemDiskSerializer = SystemDiskSerializer(
        required=True,
        help_text="Disk Usage Information",
    )

    # Meta Class
    class Meta:
        """
        Meta Class For System Info Serializer.

        Attributes:
            ref_name (ClassVar[str]): Reference Name For The Serializer.
        """

        # Set Reference Name
        ref_name: ClassVar[str] = "SystemInfo"


# Health Response Serializer
@extend_schema_serializer(
    examples=[
        OpenApiExample(
            name="System In Healthy State",
            summary="System In Healthy State",
            description="Complete Health Response When System Is Healthy",
            value={
                "status_code": 200,
                "data": {
                    "status": "healthy",
                    "app": "InitStack FastAPI Server",
                    "version": "0.1.0",
                    "environment": "production",
                    "timestamp": "2025-07-21T05:27:32.123456+00:00",
                    "system": {
                        "hostname": "a2f460aba47d",
                        "cpu_percent": 15.5,
                        "memory": {
                            "total": 17179869184,
                            "available": 12884901888,
                            "percent": 25.0,
                            "used": 4294967296,
                            "free": 12884901888,
                        },
                        "disk": {
                            "total": 107374182400,
                            "used": 53687091200,
                            "free": 53687091200,
                            "percent": 50.0,
                        },
                    },
                },
            },
            status_codes=[status.HTTP_200_OK],
        ),
        OpenApiExample(
            name="System In Degraded State",
            summary="System In Degraded State",
            description="Complete Health Response When System Resources Are High But Service Is Up",
            value={
                "status_code": 503,
                "data": {
                    "status": "degraded",
                    "app": "InitStack FastAPI Server",
                    "version": "0.1.0",
                    "environment": "production",
                    "timestamp": "2025-07-21T05:27:32.123456+00:00",
                    "system": {
                        "hostname": "a2f460aba47d",
                        "cpu_percent": 85.5,
                        "memory": {
                            "total": 17179869184,
                            "available": 4294967296,
                            "percent": 75.0,
                            "used": 12884901888,
                            "free": 4294967296,
                        },
                        "disk": {
                            "total": 107374182400,
                            "used": 91268055040,
                            "free": 16106127360,
                            "percent": 85.0,
                        },
                    },
                },
            },
            status_codes=[status.HTTP_503_SERVICE_UNAVAILABLE],
        ),
        OpenApiExample(
            name="System Unhealthy Due To CPU Usage Exceeds Threshold",
            summary="System Unhealthy Due To CPU Usage Exceeds Threshold",
            description="Unhealthy Health Response Due To CPU Overload",
            value={
                "status_code": 503,
                "data": {
                    "status": "unhealthy",
                    "app": "InitStack FastAPI Server",
                    "version": "0.1.0",
                    "environment": "production",
                    "timestamp": "2025-07-21T05:27:32.123456+00:00",
                    "system": {
                        "hostname": "a2f460aba47d",
                        "cpu_percent": 95.5,
                        "memory": {
                            "total": 17179869184,
                            "available": 1073741824,
                            "percent": 93.8,
                            "used": 16106127360,
                            "free": 1073741824,
                        },
                        "disk": {
                            "total": 107374182400,
                            "used": 105656195072,
                            "free": 1717987328,
                            "percent": 98.4,
                        },
                    },
                },
            },
            status_codes=[status.HTTP_503_SERVICE_UNAVAILABLE],
        ),
        OpenApiExample(
            name="System Unhealthy Due To Memory Usage Exceeds Threshold",
            summary="System Unhealthy Due To Memory Usage Exceeds Threshold",
            description="Unhealthy Health Response Due To Memory Overload",
            value={
                "status_code": 503,
                "data": {
                    "status": "unhealthy",
                    "app": "InitStack FastAPI Server",
                    "version": "0.1.0",
                    "environment": "production",
                    "timestamp": "2025-07-21T05:27:32.123456+00:00",
                    "system": {
                        "hostname": "a2f460aba47d",
                        "cpu_percent": 65.5,
                        "memory": {
                            "total": 17179869184,
                            "available": 1073741824,
                            "percent": 93.8,
                            "used": 16106127360,
                            "free": 1073741824,
                        },
                        "disk": {
                            "total": 107374182400,
                            "used": 53687091200,
                            "free": 53687091200,
                            "percent": 50.0,
                        },
                    },
                },
            },
            status_codes=[status.HTTP_503_SERVICE_UNAVAILABLE],
        ),
    ],
)
class HealthResponseSerializer(serializers.Serializer):
    """
    Health Response Model

    Attributes:
        status (str): Current Status Of The API
        app (str): Name Of The Application
        version (str): Current Version Of The API
        environment (str): Current Environment
        timestamp (str): ISO Format Timestamp Of The Health Check
        system (SystemInfoSerializer): System Information And Metrics
    """

    # Status Value
    status: serializers.ChoiceField = serializers.ChoiceField(
        choices=("healthy", "degraded", "unhealthy"),
        help_text="Current Status Of The API",
    )

    # Application Name
    app: serializers.CharField = serializers.CharField(
        required=True,
        help_text="Name Of The Application",
        max_length=255,
    )

    # Version Value
    version: serializers.RegexField = serializers.RegexField(
        regex=r"^\d+\.\d+\.\d+$",
        help_text="Current Version Of The API",
    )

    # Environment Name
    environment: serializers.ChoiceField = serializers.ChoiceField(
        choices=("development", "staging", "production"),
        help_text="Current Environment",
    )

    # Timestamp ISO-8601
    timestamp: serializers.DateTimeField = serializers.DateTimeField(
        required=True,
        help_text="ISO Format Timestamp Of The Health Check",
    )

    # System Section
    system: SystemInfoSerializer = SystemInfoSerializer(
        required=True,
        help_text="System Information And Metrics",
    )

    # Meta Class
    class Meta:
        """
        Meta Class For Health Response Serializer.

        Attributes:
            ref_name (ClassVar[str]): Reference Name For The Serializer.
        """

        # Set Reference Name
        ref_name: ClassVar[str] = "HealthResponse"


# Exports
__all__: list[str] = [
    "HealthResponseSerializer",
    "SystemDiskSerializer",
    "SystemInfoSerializer",
    "SystemMemorySerializer",
]
