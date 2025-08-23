# ruff: noqa: PLR2004

# Local Imports
from apps.users.serializers.user_deactivate_serializer import UserDeactivateConfirmResponseSerializer
from apps.users.serializers.user_deactivate_serializer import UserDeactivateConfirmUnauthorizedErrorResponseSerializer
from apps.users.serializers.user_deactivate_serializer import UserDeactivateRequestAcceptedResponseSerializer
from apps.users.serializers.user_deactivate_serializer import UserDeactivateRequestUnauthorizedErrorResponseSerializer


# Test Request Accepted Defaults
def test_user_deactivate_request_accepted_default_message_and_valid() -> None:
    """
    Verify Request Accepted Serializer Defaults Message And Validates.
    """

    # Inputs
    payload: dict[str, object] = {
        "status_code": 202,
        # no "message" provided
    }

    # Create Serializer
    serializer: UserDeactivateRequestAcceptedResponseSerializer = UserDeactivateRequestAcceptedResponseSerializer(
        data=payload,
    )

    # Validate
    assert serializer.is_valid(), serializer.errors

    # Assert Defaults
    assert serializer.validated_data["status_code"] == 202
    assert (
        serializer.validated_data["message"]
        == "Account Deactivation Request Sent Successfully"
    )


# Test Request Accepted Missing Status Code
def test_user_deactivate_request_accepted_missing_status_code_is_invalid() -> None:
    """
    Verify Missing Status Code Raises Error Message For Request Accepted Serializer.
    """

    # Inputs
    payload: dict[str, object] = {
        # "status_code" missing
    }

    # Create Serializer
    serializer: UserDeactivateRequestAcceptedResponseSerializer = UserDeactivateRequestAcceptedResponseSerializer(
        data=payload,
    )

    # Validate
    assert not serializer.is_valid()

    # Assert Error Message
    assert "status_code" in serializer.errors
    assert str(serializer.errors["status_code"][0]) == "Status Code Is Required"


# Test Confirm Response Valid
def test_user_deactivate_confirm_response_valid_payload_is_valid() -> None:
    """
    Verify Confirm Response Serializer Accepts Valid Payload.
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
            "is_active": False,
            "is_staff": False,
            "is_superuser": False,
            "date_joined": "2025-08-16T19:04:06.602446+05:30",
            "last_login": "2025-08-16T19:10:06.602446+05:30",
        },
    }

    # Create Serializer
    serializer: UserDeactivateConfirmResponseSerializer = UserDeactivateConfirmResponseSerializer(
        data=payload,
    )

    # Validate
    assert serializer.is_valid(), serializer.errors

    # Assert Nested Data
    assert serializer.validated_data["status_code"] == 200
    assert serializer.validated_data["user"]["username"] == "johndoe"


# Test Confirm Response Missing User
def test_user_deactivate_confirm_response_missing_user_is_invalid() -> None:
    """
    Verify Missing User Field Raises Error Message.
    """

    # Inputs
    payload: dict[str, object] = {
        "status_code": 200,
        # "user" missing
    }

    # Create Serializer
    serializer: UserDeactivateConfirmResponseSerializer = UserDeactivateConfirmResponseSerializer(
        data=payload,
    )

    # Validate
    assert not serializer.is_valid()

    # Assert Error Message
    assert "user" in serializer.errors
    assert str(serializer.errors["user"][0]) == "User Details Is Required"


# Test Confirm Response Null User
def test_user_deactivate_confirm_response_null_user_is_invalid() -> None:
    """
    Verify Null User Field Raises Error Message.
    """

    # Inputs
    payload: dict[str, object] = {
        "status_code": 200,
        "user": None,
    }

    # Create Serializer
    serializer: UserDeactivateConfirmResponseSerializer = UserDeactivateConfirmResponseSerializer(
        data=payload,
    )

    # Validate
    assert not serializer.is_valid()

    # Assert Error Message
    assert "user" in serializer.errors
    assert str(serializer.errors["user"][0]) == "User Details Cannot Be Null"


# Test Request Unauthorized Defaults
def test_user_deactivate_request_unauthorized_default_error_and_valid() -> None:
    """
    Verify Request Unauthorized Error Serializer Defaults Error And Validates.
    """

    # Inputs
    payload: dict[str, object] = {
        "status_code": 401,
        # no "error" provided
    }

    # Create Serializer
    serializer: UserDeactivateRequestUnauthorizedErrorResponseSerializer = (
        UserDeactivateRequestUnauthorizedErrorResponseSerializer(
            data=payload,
        )
    )

    # Validate
    assert serializer.is_valid(), serializer.errors

    # Assert Defaults
    assert serializer.validated_data["status_code"] == 401
    assert serializer.validated_data["error"] == "Unauthorized"


# Test Request Unauthorized Missing Status Code
def test_user_deactivate_request_unauthorized_missing_status_code_is_invalid() -> None:
    """
    Verify Missing Status Code Raises Error Message For Request Unauthorized Error Serializer.
    """

    # Inputs
    payload: dict[str, object] = {
        # "status_code" missing
    }

    # Create Serializer
    serializer: UserDeactivateRequestUnauthorizedErrorResponseSerializer = (
        UserDeactivateRequestUnauthorizedErrorResponseSerializer(
            data=payload,
        )
    )

    # Validate
    assert not serializer.is_valid()

    # Assert Error Message
    assert "status_code" in serializer.errors
    assert str(serializer.errors["status_code"][0]) == "Status Code Is Required"


# Test Confirm Unauthorized Defaults
def test_user_deactivate_confirm_unauthorized_default_error_and_valid() -> None:
    """
    Verify Confirm Unauthorized Error Serializer Defaults Error And Validates.
    """

    # Inputs
    payload: dict[str, object] = {
        "status_code": 401,
        # no "error" provided
    }

    # Create Serializer
    serializer: UserDeactivateConfirmUnauthorizedErrorResponseSerializer = (
        UserDeactivateConfirmUnauthorizedErrorResponseSerializer(
            data=payload,
        )
    )

    # Validate
    assert serializer.is_valid(), serializer.errors

    # Assert Defaults
    assert serializer.validated_data["status_code"] == 401
    assert serializer.validated_data["error"] == "Unauthorized"


# Test Confirm Unauthorized Missing Status Code
def test_user_deactivate_confirm_unauthorized_missing_status_code_is_invalid() -> None:
    """
    Verify Missing Status Code Raises Error Message For Confirm Unauthorized Error Serializer.
    """

    # Inputs
    payload: dict[str, object] = {
        # "status_code" missing
    }

    # Create Serializer
    serializer: UserDeactivateConfirmUnauthorizedErrorResponseSerializer = (
        UserDeactivateConfirmUnauthorizedErrorResponseSerializer(
            data=payload,
        )
    )

    # Validate
    assert not serializer.is_valid()

    # Assert Error Message
    assert "status_code" in serializer.errors
    assert str(serializer.errors["status_code"][0]) == "Status Code Is Required"
