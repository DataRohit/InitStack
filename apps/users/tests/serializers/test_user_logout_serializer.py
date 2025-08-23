# ruff: noqa: PLR2004

# Local Imports
from apps.users.serializers.user_logout_serializer import UserLogoutUnauthorizedErrorResponseSerializer


# Test Unauthorized Defaults
def test_user_logout_unauthorized_default_error_and_valid() -> None:
    """
    Verify Unauthorized Error Serializer Defaults Error And Validates.
    """

    # Inputs
    payload: dict[str, object] = {
        "status_code": 401,
        # no "error" provided
    }

    # Create Serializer
    serializer: UserLogoutUnauthorizedErrorResponseSerializer = UserLogoutUnauthorizedErrorResponseSerializer(
        data=payload,
    )

    # Validate
    assert serializer.is_valid(), serializer.errors

    # Assert Defaults
    assert serializer.validated_data["status_code"] == 401
    assert serializer.validated_data["error"] == "Unauthorized"


# Test Unauthorized Missing Status Code
def test_user_logout_unauthorized_missing_status_code_is_invalid() -> None:
    """
    Verify Missing Status Code Raises Error Message For Unauthorized Error Serializer.
    """

    # Inputs
    payload: dict[str, object] = {
        # "status_code" missing
    }

    # Create Serializer
    serializer: UserLogoutUnauthorizedErrorResponseSerializer = UserLogoutUnauthorizedErrorResponseSerializer(
        data=payload,
    )

    # Validate
    assert not serializer.is_valid()

    # Assert Error Message
    assert "status_code" in serializer.errors
    assert str(serializer.errors["status_code"][0]) == "Status Code Is Required"


# Test Unauthorized Specific Error Message
def test_user_logout_unauthorized_specific_error_message_is_valid() -> None:
    """
    Verify Unauthorized Error Serializer Accepts Specific Error Message.
    """

    # Inputs
    payload: dict[str, object] = {
        "status_code": 401,
        "error": "Token Has Expired",
    }

    # Create Serializer
    serializer: UserLogoutUnauthorizedErrorResponseSerializer = UserLogoutUnauthorizedErrorResponseSerializer(
        data=payload,
    )

    # Validate
    assert serializer.is_valid(), serializer.errors

    # Assert Data
    assert serializer.validated_data["status_code"] == 401
    assert serializer.validated_data["error"] == "Token Has Expired"
