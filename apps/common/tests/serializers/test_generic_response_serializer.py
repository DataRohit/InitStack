# Third Party Imports
from rest_framework import serializers
from rest_framework import status

# Local Imports
from apps.common.serializers.generic_response_serializer import Generic202ResponseSerializer
from apps.common.serializers.generic_response_serializer import Generic500ResponseSerializer
from apps.common.serializers.generic_response_serializer import GenericResponseSerializer


# Test Generic Response Serializer
def test_valid_payload() -> None:
    """
    Test Valid Status Code Passes Validation.
    """

    # Build Serializer
    serializer: GenericResponseSerializer = GenericResponseSerializer(data={"status_code": status.HTTP_200_OK})

    # Validate And Assert
    assert serializer.is_valid() is True
    assert serializer.validated_data["status_code"] == status.HTTP_200_OK


# Test Missing Status Code Fails With Required Message
def test_missing_status_code() -> None:
    """
    Test Missing Status Code Fails With Required Message.
    """

    # Build Serializer
    serializer: GenericResponseSerializer = GenericResponseSerializer(data={})

    # Validate And Assert
    assert serializer.is_valid() is False
    errors: dict[str, list[str]] = {k: [str(v) for v in vals] for k, vals in serializer.errors.items()}
    assert errors["status_code"][0] == "Status Code Is Required"


# Test Null Status Code Fails With Null Message
def test_null_status_code() -> None:
    """
    Test Null Status Code Fails With Null Message.
    """

    # Build Serializer
    serializer: GenericResponseSerializer = GenericResponseSerializer(data={"status_code": None})

    # Validate And Assert
    assert serializer.is_valid() is False
    errors: dict[str, list[str]] = {k: [str(v) for v in vals] for k, vals in serializer.errors.items()}
    assert errors["status_code"][0] == "Status Code Cannot Be Null"


# Test Generic 500 Response Serializer Default Error Message
def test_default_error_message() -> None:
    """
    Test Default Error Message Is Applied.
    """

    # Build Serializer
    serializer: Generic500ResponseSerializer = Generic500ResponseSerializer(
        data={"status_code": status.HTTP_500_INTERNAL_SERVER_ERROR},
    )

    # Validate And Assert
    assert serializer.is_valid() is True
    data: dict[str, serializers.Field] = serializer.data
    assert data["status_code"] == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert data["error"] == "Internal Server Error"


# Test Generic 500 Response Serializer Custom Error Message
def test_custom_error_message() -> None:
    """
    Test Custom Error Message Overrides Default.
    """

    # Build Serializer
    serializer: Generic500ResponseSerializer = Generic500ResponseSerializer(
        data={
            "status_code": status.HTTP_500_INTERNAL_SERVER_ERROR,
            "error": "Boom",
        },
    )

    # Validate And Assert
    assert serializer.is_valid() is True
    data: dict[str, serializers.Field] = serializer.data
    assert data["error"] == "Boom"


# Test Generic 202 Response Serializer Default Message
def test_default_message() -> None:
    """
    Test Default Message Is Applied.
    """

    # Build Serializer
    serializer: Generic202ResponseSerializer = Generic202ResponseSerializer(
        data={"status_code": status.HTTP_202_ACCEPTED},
    )

    # Validate And Assert
    assert serializer.is_valid() is True
    data: dict[str, serializers.Field] = serializer.data
    assert data["status_code"] == status.HTTP_202_ACCEPTED
    assert data["message"] == "Accepted"


# Test Generic 202 Response Serializer Custom Message
def test_custom_message() -> None:
    """
    Test Custom Message Overrides Default.
    """

    # Build Serializer
    serializer: Generic202ResponseSerializer = Generic202ResponseSerializer(
        data={
            "status_code": status.HTTP_202_ACCEPTED,
            "message": "All Good",
        },
    )

    # Validate And Assert
    assert serializer.is_valid() is True
    data: dict[str, serializers.Field] = serializer.data
    assert data["message"] == "All Good"
