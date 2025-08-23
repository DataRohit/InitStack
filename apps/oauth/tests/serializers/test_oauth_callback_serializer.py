# Third Party Imports
import pytest
from rest_framework import status

# Local Imports
from apps.oauth.serializers.oauth_callback_serializer import OAuthCallbackBadRequestErrorResponseSerialzier
from apps.oauth.serializers.oauth_callback_serializer import OAuthCallbackResponseSerializer
from apps.oauth.serializers.oauth_callback_serializer import OAuthCallbackUnauthorizedErrorResponseSerializer


# Bad Request Error Serializer: Valid Case
def test_oauth_callback_bad_request_error_response_serializer_valid() -> None:
    """
    Valid Payload Should Pass And Echo Values.
    """

    # Build Payload
    data = {"status_code": status.HTTP_400_BAD_REQUEST, "error": "Authentication Failed"}

    # Initialize Serializer
    ser = OAuthCallbackBadRequestErrorResponseSerialzier(data=data)

    # Assert Validation
    assert ser.is_valid(), ser.errors

    # Assert Values
    assert ser.validated_data["status_code"] == status.HTTP_400_BAD_REQUEST
    assert ser.validated_data["error"] == "Authentication Failed"


# Bad Request Error Serializer: Missing Error Field
def test_oauth_callback_bad_request_error_response_serializer_missing_error() -> None:
    """
    Missing Error Should Fail Validation.
    """

    # Build Payload
    data = {"status_code": status.HTTP_400_BAD_REQUEST}

    # Initialize Serializer
    ser = OAuthCallbackBadRequestErrorResponseSerialzier(data=data)

    # Assert Invalid
    assert not ser.is_valid()

    # Assert Error Key
    assert "error" in ser.errors


# Bad Request Error Serializer: Missing Status Code Field
def test_oauth_callback_bad_request_error_response_serializer_missing_status_code() -> None:
    """
    Missing Status Code Should Fail Validation.
    """

    # Build Payload
    data = {"error": "User Not Found"}

    # Initialize Serializer
    ser = OAuthCallbackBadRequestErrorResponseSerialzier(data=data)

    # Assert Invalid
    assert not ser.is_valid()

    # Assert Error Key
    assert "status_code" in ser.errors


# Bad Request Error Serializer: Null Error Not Allowed
def test_oauth_callback_bad_request_error_response_serializer_null_error() -> None:
    """
    Null Error Should Fail Validation.
    """

    # Build Payload
    data = {"status_code": status.HTTP_400_BAD_REQUEST, "error": None}

    # Initialize Serializer
    ser = OAuthCallbackBadRequestErrorResponseSerialzier(data=data)

    # Assert Invalid
    assert not ser.is_valid()

    # Assert Error Key
    assert "error" in ser.errors


# Callback Response Serializer: Valid Case With All Fields
def test_oauth_callback_response_serializer_valid_full_payload() -> None:
    """
    Full User Payload Should Validate Successfully.
    """

    # Build User Payload
    user_payload = {
        "id": "123e4567-e89b-12d3-a456-426614174000",
        "username": "johndoe",
        "email": "johndoe@example.com",
        "first_name": "John",
        "last_name": "Doe",
        "is_active": True,
        "is_staff": False,
        "is_superuser": False,
        "date_joined": "2025-08-16T19:04:06.602446+05:30",
        "last_login": "2025-08-16T19:10:06.602446+05:30",
        "access_token": "access",
        "refresh_token": "refresh",
    }

    # Build Payload
    data = {"status_code": status.HTTP_200_OK, "user": user_payload}

    # Initialize Serializer
    ser = OAuthCallbackResponseSerializer(data=data)

    # Assert Validation
    assert ser.is_valid(), ser.errors

    # Assert Values
    assert ser.validated_data["status_code"] == status.HTTP_200_OK
    assert ser.validated_data["user"]["username"] == "johndoe"


# Callback Response Serializer: Missing User Field
def test_oauth_callback_response_serializer_missing_user() -> None:
    """
    Missing User Object Should Fail Validation.
    """

    # Build Payload
    data = {"status_code": status.HTTP_200_OK}

    # Initialize Serializer
    ser = OAuthCallbackResponseSerializer(data=data)

    # Assert Invalid
    assert not ser.is_valid()

    # Assert Error Key
    assert "user" in ser.errors


# Callback Response Serializer: Missing Required User Fields
@pytest.mark.parametrize(
    "missing_field",
    [
        "id",
        "username",
        "email",
        "first_name",
        "last_name",
        "is_active",
        "is_staff",
        "is_superuser",
        "date_joined",
        "access_token",
        "refresh_token",
    ],
)
def test_oauth_callback_response_serializer_missing_user_fields(missing_field: str) -> None:
    """
    Each Missing Required Field Should Fail Validation.
    """

    # Build User Payload
    user_payload = {
        "id": "123e4567-e89b-12d3-a456-426614174000",
        "username": "johndoe",
        "email": "johndoe@example.com",
        "first_name": "John",
        "last_name": "Doe",
        "is_active": True,
        "is_staff": False,
        "is_superuser": False,
        "date_joined": "2025-08-16T19:04:06.602446+05:30",
        "last_login": "2025-08-16T19:10:06.602446+05:30",
        "access_token": "access",
        "refresh_token": "refresh",
    }

    # Remove Field
    user_payload.pop(missing_field, None)

    # Build Payload
    data = {"status_code": status.HTTP_200_OK, "user": user_payload}

    # Initialize Serializer
    ser = OAuthCallbackResponseSerializer(data=data)

    # Assert Invalid
    assert not ser.is_valid()

    # Assert Error Key
    assert "user" in ser.errors or missing_field in ser.errors.get("user", {})


# Callback Response Serializer: Last Login Optional
def test_oauth_callback_response_serializer_allows_missing_last_login() -> None:
    """
    Missing Last Login Should Still Validate.
    """

    # Build User Payload
    user_payload = {
        "id": "123e4567-e89b-12d3-a456-426614174000",
        "username": "johndoe",
        "email": "johndoe@example.com",
        "first_name": "John",
        "last_name": "Doe",
        "is_active": True,
        "is_staff": False,
        "is_superuser": False,
        "date_joined": "2025-08-16T19:04:06.602446+05:30",
        "access_token": "access",
        "refresh_token": "refresh",
    }

    # Build Payload
    data = {"status_code": status.HTTP_200_OK, "user": user_payload}

    # Initialize Serializer
    ser = OAuthCallbackResponseSerializer(data=data)

    # Assert Validation
    assert ser.is_valid(), ser.errors


# Callback Unauthorized Error Serializer: Default Error Message
def test_oauth_callback_unauthorized_error_response_serializer_default_error() -> None:
    """
    Default Error Should Be "Unauthorized".
    """

    # Build Payload
    data = {"status_code": status.HTTP_401_UNAUTHORIZED}

    # Initialize Serializer
    ser = OAuthCallbackUnauthorizedErrorResponseSerializer(data=data)

    # Assert Validation
    assert ser.is_valid(), ser.errors

    # Assert Values
    assert ser.validated_data["status_code"] == status.HTTP_401_UNAUTHORIZED
    assert ser.validated_data["error"] == "Unauthorized"


# Callback Unauthorized Error Serializer: Custom Error Message
def test_oauth_callback_unauthorized_error_response_serializer_custom_error() -> None:
    """
    Custom Error Should Override Default.
    """

    # Build Payload
    data = {"status_code": status.HTTP_401_UNAUTHORIZED, "error": "Token Invalid"}

    # Initialize Serializer
    ser = OAuthCallbackUnauthorizedErrorResponseSerializer(data=data)

    # Assert Validation
    assert ser.is_valid(), ser.errors

    # Assert Values
    assert ser.validated_data["error"] == "Token Invalid"
