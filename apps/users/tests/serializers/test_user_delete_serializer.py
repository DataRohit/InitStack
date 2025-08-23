# ruff: noqa: PLR2004

# Local Imports
from apps.users.serializers.user_delete_serializer import UserDeleteConfirmUnauthorizedErrorResponseSerializer
from apps.users.serializers.user_delete_serializer import UserDeleteRequestAcceptedResponseSerializer
from apps.users.serializers.user_delete_serializer import UserDeleteRequestUnauthorizedErrorResponseSerializer


# Test Request Accepted Defaults
def test_user_delete_request_accepted_default_message_and_valid() -> None:
    """
    Verify Request Accepted Serializer Defaults Message And Validates.
    """

    # Inputs
    payload: dict[str, object] = {
        "status_code": 202,
        # no "message" provided
    }

    # Create Serializer
    serializer: UserDeleteRequestAcceptedResponseSerializer = UserDeleteRequestAcceptedResponseSerializer(
        data=payload,
    )

    # Validate
    assert serializer.is_valid(), serializer.errors

    # Assert Defaults
    assert serializer.validated_data["status_code"] == 202
    assert (
        serializer.validated_data["message"]
        == "Account Deletion Request Sent Successfully"
    )


# Test Request Accepted Missing Status Code
def test_user_delete_request_accepted_missing_status_code_is_invalid() -> None:
    """
    Verify Missing Status Code Raises Error Message For Request Accepted Serializer.
    """

    # Inputs
    payload: dict[str, object] = {
        # "status_code" missing
    }

    # Create Serializer
    serializer: UserDeleteRequestAcceptedResponseSerializer = UserDeleteRequestAcceptedResponseSerializer(
        data=payload,
    )

    # Validate
    assert not serializer.is_valid()

    # Assert Error Message
    assert "status_code" in serializer.errors
    assert str(serializer.errors["status_code"][0]) == "Status Code Is Required"


# Test Request Unauthorized Defaults
def test_user_delete_request_unauthorized_default_error_and_valid() -> None:
    """
    Verify Request Unauthorized Error Serializer Defaults Error And Validates.
    """

    # Inputs
    payload: dict[str, object] = {
        "status_code": 401,
        # no "error" provided
    }

    # Create Serializer
    serializer: UserDeleteRequestUnauthorizedErrorResponseSerializer = (
        UserDeleteRequestUnauthorizedErrorResponseSerializer(
            data=payload,
        )
    )

    # Validate
    assert serializer.is_valid(), serializer.errors

    # Assert Defaults
    assert serializer.validated_data["status_code"] == 401
    assert serializer.validated_data["error"] == "Unauthorized"


# Test Request Unauthorized Missing Status Code
def test_user_delete_request_unauthorized_missing_status_code_is_invalid() -> None:
    """
    Verify Missing Status Code Raises Error Message For Request Unauthorized Error Serializer.
    """

    # Inputs
    payload: dict[str, object] = {
        # "status_code" missing
    }

    # Create Serializer
    serializer: UserDeleteRequestUnauthorizedErrorResponseSerializer = (
        UserDeleteRequestUnauthorizedErrorResponseSerializer(
            data=payload,
        )
    )

    # Validate
    assert not serializer.is_valid()

    # Assert Error Message
    assert "status_code" in serializer.errors
    assert str(serializer.errors["status_code"][0]) == "Status Code Is Required"


# Test Confirm Unauthorized Defaults
def test_user_delete_confirm_unauthorized_default_error_and_valid() -> None:
    """
    Verify Confirm Unauthorized Error Serializer Defaults Error And Validates.
    """

    # Inputs
    payload: dict[str, object] = {
        "status_code": 401,
        # no "error" provided
    }

    # Create Serializer
    serializer: UserDeleteConfirmUnauthorizedErrorResponseSerializer = (
        UserDeleteConfirmUnauthorizedErrorResponseSerializer(
            data=payload,
        )
    )

    # Validate
    assert serializer.is_valid(), serializer.errors

    # Assert Defaults
    assert serializer.validated_data["status_code"] == 401
    assert serializer.validated_data["error"] == "Unauthorized"


# Test Confirm Unauthorized Missing Status Code
def test_user_delete_confirm_unauthorized_missing_status_code_is_invalid() -> None:
    """
    Verify Missing Status Code Raises Error Message For Confirm Unauthorized Error Serializer.
    """

    # Inputs
    payload: dict[str, object] = {
        # "status_code" missing
    }

    # Create Serializer
    serializer: UserDeleteConfirmUnauthorizedErrorResponseSerializer = (
        UserDeleteConfirmUnauthorizedErrorResponseSerializer(
            data=payload,
        )
    )

    # Validate
    assert not serializer.is_valid()

    # Assert Error Message
    assert "status_code" in serializer.errors
    assert str(serializer.errors["status_code"][0]) == "Status Code Is Required"
