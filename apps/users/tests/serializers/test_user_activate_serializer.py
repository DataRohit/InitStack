# ruff: noqa: PLR2004

# Local Imports
from apps.users.serializers.user_activate_serializer import UserActivateResponseSerializer
from apps.users.serializers.user_activate_serializer import UserActivateUnauthorizedErrorResponseSerializer


# Test Valid Activate Response Serializer
def test_user_activate_response_serializer_with_valid_payload_is_valid() -> None:
    """
    Verify Serializer Accepts Valid Activate Response Payload.
    """

    # Inputs
    payload: dict[str, object] = {
        "status_code": 200,
        "user": {
            "id": "123e4567-e89b-12d3-a456-426614174000",
            "username": "johndoe",
            "email": "johndoe@example.com",
            "first_name": "John",
            "last_name": "Doe",
            "full_name": "John Doe",
            "is_active": True,
            "is_staff": False,
            "is_superuser": False,
            "date_joined": "2025-08-16T19:04:06.602446+05:30",
            "last_login": None,
        },
    }

    # Create Serializer
    serializer: UserActivateResponseSerializer = UserActivateResponseSerializer(data=payload)

    # Validate
    assert serializer.is_valid(), serializer.errors

    # Assert Nested Data
    assert serializer.validated_data["status_code"] == 200
    assert serializer.validated_data["user"]["username"] == "johndoe"


# Test Missing User Field
def test_user_activate_response_serializer_missing_user_is_invalid() -> None:
    """
    Verify Missing User Field Raises Error Message.
    """

    # Inputs
    payload: dict[str, object] = {
        "status_code": 200,
        # "user" missing
    }

    # Create Serializer
    serializer: UserActivateResponseSerializer = UserActivateResponseSerializer(data=payload)

    # Validate
    assert not serializer.is_valid()

    # Assert Error Message
    assert "user" in serializer.errors
    assert str(serializer.errors["user"][0]) == "User Details Is Required"


# Test Null User Field
def test_user_activate_response_serializer_null_user_is_invalid() -> None:
    """
    Verify Null User Field Raises Error Message.
    """

    # Inputs
    payload: dict[str, object] = {
        "status_code": 200,
        "user": None,
    }

    # Create Serializer
    serializer: UserActivateResponseSerializer = UserActivateResponseSerializer(data=payload)

    # Validate
    assert not serializer.is_valid()

    # Assert Error Message
    assert "user" in serializer.errors
    assert str(serializer.errors["user"][0]) == "User Details Cannot Be Null"


# Test Missing Status Code
def test_user_activate_response_serializer_missing_status_code_is_invalid() -> None:
    """
    Verify Missing Status Code Raises Error Message.
    """

    # Inputs
    payload: dict[str, object] = {
        # "status_code" missing
        "user": {
            "id": "123e4567-e89b-12d3-a456-426614174000",
            "username": "johndoe",
            "email": "johndoe@example.com",
            "first_name": "John",
            "last_name": "Doe",
            "full_name": "John Doe",
            "is_active": True,
            "is_staff": False,
            "is_superuser": False,
            "date_joined": "2025-08-16T19:04:06.602446+05:30",
            "last_login": None,
        },
    }

    # Create Serializer
    serializer: UserActivateResponseSerializer = UserActivateResponseSerializer(data=payload)

    # Validate
    assert not serializer.is_valid()

    # Assert Error Message
    assert "status_code" in serializer.errors
    assert str(serializer.errors["status_code"][0]) == "Status Code Is Required"


# Test Unauthorized Error Response Defaults
def test_user_activate_unauthorized_error_response_default_error_and_valid() -> None:
    """
    Verify Unauthorized Error Serializer Defaults Error And Validates.
    """

    # Inputs
    payload: dict[str, object] = {
        "status_code": 401,
        # no "error" provided
    }

    # Create Serializer
    serializer: UserActivateUnauthorizedErrorResponseSerializer = UserActivateUnauthorizedErrorResponseSerializer(
        data=payload,
    )

    # Validate
    assert serializer.is_valid(), serializer.errors

    # Assert Defaults
    assert serializer.validated_data["status_code"] == 401
    assert serializer.validated_data["error"] == "Unauthorized"


# Test Unauthorized Error Response Missing Status Code
def test_user_activate_unauthorized_error_response_missing_status_code_is_invalid() -> None:
    """
    Verify Missing Status Code Raises Error Message For Unauthorized Error Serializer.
    """

    # Inputs
    payload: dict[str, object] = {
        # "status_code" missing
    }

    # Create Serializer
    serializer: UserActivateUnauthorizedErrorResponseSerializer = UserActivateUnauthorizedErrorResponseSerializer(
        data=payload,
    )

    # Validate
    assert not serializer.is_valid()

    # Assert Error Message
    assert "status_code" in serializer.errors
    assert str(serializer.errors["status_code"][0]) == "Status Code Is Required"
