# ruff: noqa: PLR2004

# Standard Library Imports
from typing import TYPE_CHECKING

# Local Imports
from apps.system.serializers.health_serializer import HealthResponseSerializer

# If Type Checking
if TYPE_CHECKING:
    # Third Party Imports
    from rest_framework import serializers


# Test Health Response Serializer
def test_valid_payload() -> None:
    """
    Test Valid Payload Passes Validation.
    """

    # Build Payload
    payload: dict[str, serializers.Field] = {
        "status": "healthy",
        "app": "InitStack FastAPI Server",
        "version": "0.1.0",
        "environment": "production",
        "timestamp": "2025-08-23T03:38:00Z",
        "system": {
            "hostname": "host-1",
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
    }

    # Build Serializer
    serializer: HealthResponseSerializer = HealthResponseSerializer(data=payload)

    # Validate And Assert
    assert serializer.is_valid() is True
    data: dict[str, serializers.Field] = serializer.data
    assert data["status"] == "healthy"
    assert data["app"] == "InitStack FastAPI Server"
    assert data["version"] == "0.1.0"
    assert data["environment"] == "production"
    assert data["system"]["hostname"] == "host-1"
    assert data["system"]["cpu_percent"] == 15.5
    assert data["system"]["memory"]["percent"] == 25.0
    assert data["system"]["disk"]["percent"] == 50.0


# Test Missing Status Fails With Required Message
def test_missing_status() -> None:
    """
    Test Missing Status Fails With Required Message.
    """

    # Build Serializer
    serializer: HealthResponseSerializer = HealthResponseSerializer(data={})

    # Validate And Assert
    assert serializer.is_valid() is False
    errors: dict[str, list[str]] = {k: [str(v) for v in vals] for k, vals in serializer.errors.items()}
    assert errors["status"][0] == "Status Is Required"


# Test Invalid Status Choice Fails With Choices Message
def test_invalid_status_choice() -> None:
    """
    Test Invalid Status Choice Fails With Choices Message.
    """

    # Build Serializer
    serializer: HealthResponseSerializer = HealthResponseSerializer(data={"status": "ok"})

    # Validate And Assert
    assert serializer.is_valid() is False
    errors: dict[str, list[str]] = {k: [str(v) for v in vals] for k, vals in serializer.errors.items()}
    assert "valid choice" in errors["status"][0]


# Test Invalid Version Fails With Regex Message
def test_invalid_version_regex() -> None:
    """
    Test Invalid Version Fails With Regex Message.
    """

    # Build Serializer
    serializer: HealthResponseSerializer = HealthResponseSerializer(data={"version": "1.0"})

    # Validate And Assert
    assert serializer.is_valid() is False
    errors: dict[str, list[str]] = {k: [str(v) for v in vals] for k, vals in serializer.errors.items()}
    assert errors["version"][0] == "Version Must Follow The Pattern 'Major.Minor.Patch' (e.g., '1.0.0')"


# Test Invalid Environment Fails With Choices Message
def test_invalid_environment_choice() -> None:
    """
    Test Invalid Environment Fails With Choices Message.
    """

    # Build Serializer
    serializer: HealthResponseSerializer = HealthResponseSerializer(data={"environment": "prod"})

    # Validate And Assert
    assert serializer.is_valid() is False
    errors: dict[str, list[str]] = {k: [str(v) for v in vals] for k, vals in serializer.errors.items()}
    assert "valid choice" in errors["environment"][0]


# Test Missing Timestamp Fails With Required Message
def test_missing_timestamp() -> None:
    """
    Test Missing Timestamp Fails With Required Message.
    """

    # Build Serializer
    serializer: HealthResponseSerializer = HealthResponseSerializer(data={"status": "healthy"})

    # Validate And Assert
    assert serializer.is_valid() is False
    errors: dict[str, list[str]] = {k: [str(v) for v in vals] for k, vals in serializer.errors.items()}
    assert errors["timestamp"][0] == "Timestamp Is Required"


# Test Missing System Fails With Required Message
def test_missing_system() -> None:
    """
    Test Missing System Fails With Required Message.
    """

    # Build Serializer
    serializer: HealthResponseSerializer = HealthResponseSerializer(
        data={
            "status": "healthy",
            "app": "InitStack",
            "version": "1.2.3",
            "environment": "development",
            "timestamp": "2025-08-23T03:38:00Z",
        },
    )

    # Validate And Assert
    assert serializer.is_valid() is False
    errors: dict[str, list[str]] = {k: [str(v) for v in vals] for k, vals in serializer.errors.items()}
    assert errors["system"][0] == "System Information Is Required"


# Test Blank Hostname Fails With Blank Message
def test_hostname_blank() -> None:
    """
    Test Blank Hostname Fails With Blank Message.
    """

    # Build Payload
    payload: dict[str, serializers.Field] = {
        "status": "healthy",
        "app": "InitStack",
        "version": "1.2.3",
        "environment": "development",
        "timestamp": "2025-08-23T03:38:00Z",
        "system": {
            "hostname": "",
            "cpu_percent": 10.0,
            "memory": {"total": 1, "available": 1, "percent": 1.0, "used": 0, "free": 1},
            "disk": {"total": 1, "used": 0, "free": 1, "percent": 1.0},
        },
    }

    # Build Serializer
    serializer: HealthResponseSerializer = HealthResponseSerializer(data=payload)

    # Validate And Assert
    assert serializer.is_valid() is False
    errors: dict[str, list[str]] = serializer.errors["system"]
    errors = {k: [str(v) for v in vals] for k, vals in errors.items()}
    assert errors["hostname"][0] == "Hostname Cannot Be Blank"


# Test CPU Percent Greater Than Max Fails
def test_cpu_percent_exceeds_max() -> None:
    """
    Test CPU Percent Greater Than Max Fails.
    """

    # Build Payload
    payload: dict[str, serializers.Field] = {
        "status": "degraded",
        "app": "InitStack",
        "version": "1.2.3",
        "environment": "staging",
        "timestamp": "2025-08-23T03:38:00Z",
        "system": {
            "hostname": "host-1",
            "cpu_percent": 120.0,
            "memory": {"total": 1, "available": 1, "percent": 1.0, "used": 0, "free": 1},
            "disk": {"total": 1, "used": 0, "free": 1, "percent": 1.0},
        },
    }

    # Build Serializer
    serializer: HealthResponseSerializer = HealthResponseSerializer(data=payload)

    # Validate And Assert
    assert serializer.is_valid() is False
    sys_errors: dict[str, list[str]] = serializer.errors["system"]
    sys_errors = {k: [str(v) for v in vals] for k, vals in sys_errors.items()}
    assert sys_errors["cpu_percent"][0] == "CPU Percent Must Be Less Than Or Equal To 100"


# Test Memory Field Constraints Failures
def test_memory_constraints() -> None:
    """
    Test Memory Field Constraints Failures.
    """

    # Build Payload
    payload: dict[str, serializers.Field] = {
        "status": "unhealthy",
        "app": "InitStack",
        "version": "1.2.3",
        "environment": "production",
        "timestamp": "2025-08-23T03:38:00Z",
        "system": {
            "hostname": "host-1",
            "cpu_percent": 10.0,
            "memory": {"total": -1, "available": 1, "percent": 150.0, "used": 0, "free": 1},
            "disk": {"total": 1, "used": 0, "free": 1, "percent": 1.0},
        },
    }

    # Build Serializer
    serializer: HealthResponseSerializer = HealthResponseSerializer(data=payload)

    # Validate And Assert
    assert serializer.is_valid() is False
    sys_errors: dict[str, list[str]] = serializer.errors["system"]
    mem_errors: dict[str, list[str]] = sys_errors["memory"]
    mem_errors = {k: [str(v) for v in vals] for k, vals in mem_errors.items()}
    assert mem_errors["total"][0] == "Total Memory Must Be Greater Than Or Equal To 0"
    assert mem_errors["percent"][0] == "Percent Used Must Be Less Than Or Equal To 100"


# Test Disk Field Constraints Failures
def test_disk_constraints() -> None:
    """
    Test Disk Field Constraints Failures.
    """

    # Build Payload
    payload: dict[str, serializers.Field] = {
        "status": "unhealthy",
        "app": "InitStack",
        "version": "1.2.3",
        "environment": "staging",
        "timestamp": "2025-08-23T03:38:00Z",
        "system": {
            "hostname": "host-1",
            "cpu_percent": 10.0,
            "memory": {"total": 1, "available": 1, "percent": 1.0, "used": 0, "free": 1},
            "disk": {"total": -1, "used": 0, "free": 1, "percent": 150.0},
        },
    }

    # Build Serializer
    serializer: HealthResponseSerializer = HealthResponseSerializer(data=payload)

    # Validate And Assert
    assert serializer.is_valid() is False
    sys_errors: dict[str, list[str]] = serializer.errors["system"]
    disk_errors: dict[str, list[str]] = sys_errors["disk"]
    disk_errors = {k: [str(v) for v in vals] for k, vals in disk_errors.items()}
    assert disk_errors["total"][0] == "Total Disk Must Be Greater Than Or Equal To 0"
    assert disk_errors["percent"][0] == "Percent Used Must Be Less Than Or Equal To 100"
