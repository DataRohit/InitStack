# ruff: noqa: PLR2004

# Standard Library Imports
from typing import Any

# Local Imports
from apps.users.serializers.user_username_change_serializer import (
    UserUsernameChangeConfirmBadRequestErrorResponseSerialzier,
)
from apps.users.serializers.user_username_change_serializer import UserUsernameChangeConfirmResponseSerializer
from apps.users.serializers.user_username_change_serializer import (
    UserUsernameChangeConfirmUnauthorizedErrorResponseSerializer,
)
from apps.users.serializers.user_username_change_serializer import UserUsernameChangePayloadSerializer
from apps.users.serializers.user_username_change_serializer import UserUsernameChangeRequestAcceptedResponseSerializer
from apps.users.serializers.user_username_change_serializer import (
    UserUsernameChangeRequestUnauthorizedErrorResponseSerializer,
)


# Payload — Valid
def test_username_change_payload_valid_when_usernames_match() -> None:
    """
    Verify Payload Serializer Validates When Usernames Match.
    """

    # Inputs
    payload: dict[str, str] = {
        "username": "johnnew",
        "re_username": "johnnew",
    }

    # Create Serializer
    serializer: UserUsernameChangePayloadSerializer = UserUsernameChangePayloadSerializer(data=payload)

    # Validate
    assert serializer.is_valid(), serializer.errors

    # Assert Values
    assert serializer.validated_data["username"] == payload["username"]
    assert serializer.validated_data["re_username"] == payload["re_username"]


# Payload — Mismatch
def test_username_change_payload_username_mismatch_is_invalid() -> None:
    """
    Verify Payload Serializer Rejects When Usernames Do Not Match.
    """

    # Inputs
    payload: dict[str, str] = {
        "username": "johnnew",
        "re_username": "john",
    }

    # Create Serializer
    serializer: UserUsernameChangePayloadSerializer = UserUsernameChangePayloadSerializer(data=payload)

    # Validate
    assert not serializer.is_valid()

    # Assert Error Message
    assert "username" in serializer.errors
    assert str(serializer.errors["username"][0]) == "Usernames Do Not Match"


# Payload — Required/Null/Blank
def test_username_change_payload_required_null_blank_errors() -> None:
    """
    Verify Required, Null, And Blank Error Messages For Payload.
    """

    # Missing All
    serializer_missing: UserUsernameChangePayloadSerializer = UserUsernameChangePayloadSerializer(data={})
    assert not serializer_missing.is_valid()
    assert str(serializer_missing.errors["username"][0]) == "Username Is Required"
    assert str(serializer_missing.errors["re_username"][0]) == "Username Confirmation Is Required"

    # Null Values
    serializer_null: UserUsernameChangePayloadSerializer = UserUsernameChangePayloadSerializer(
        data={"username": None, "re_username": None},
    )
    assert not serializer_null.is_valid()
    assert str(serializer_null.errors["username"][0]) == "Username Cannot Be Null"
    assert str(serializer_null.errors["re_username"][0]) == "Username Confirmation Cannot Be Null"

    # Blank Values
    serializer_blank: UserUsernameChangePayloadSerializer = UserUsernameChangePayloadSerializer(
        data={"username": "", "re_username": ""},
    )
    assert not serializer_blank.is_valid()
    assert str(serializer_blank.errors["username"][0]) == "Username Cannot Be Blank"
    assert str(serializer_blank.errors["re_username"][0]) == "Username Confirmation Cannot Be Blank"


# Request Accepted — Defaults And Valid
def test_username_change_request_accepted_defaults_and_valid() -> None:
    """
    Verify Request Accepted Serializer Defaults Message And Validates.
    """

    # Inputs
    payload: dict[str, Any] = {
        "status_code": 202,
        # no "message" provided
    }

    # Create Serializer
    serializer: UserUsernameChangeRequestAcceptedResponseSerializer = (
        UserUsernameChangeRequestAcceptedResponseSerializer(data=payload)
    )

    # Validate
    assert serializer.is_valid(), serializer.errors

    # Assert Defaults
    assert serializer.validated_data["status_code"] == 202
    assert serializer.validated_data["message"] == "Username Change Request Sent Successfully"


# Request Accepted — Missing Status Code
def test_username_change_request_accepted_missing_status_code_is_invalid() -> None:
    """
    Verify Missing Status Code Raises Error Message For Request Accepted Serializer.
    """

    # Inputs
    payload: dict[str, Any] = {}

    # Create Serializer
    serializer: UserUsernameChangeRequestAcceptedResponseSerializer = (
        UserUsernameChangeRequestAcceptedResponseSerializer(data=payload)
    )

    # Validate
    assert not serializer.is_valid()

    # Assert Error Message
    assert str(serializer.errors["status_code"][0]) == "Status Code Is Required"


# Confirm Response — Valid
def test_username_change_confirm_response_valid() -> None:
    """
    Verify Confirm Response Serializer Accepts Valid Nested User Details.
    """

    # Inputs
    payload: dict[str, Any] = {
        "status_code": 200,
        "user": {
            "id": "123e4567-e89b-12d3-a456-426614174000",
            "username": "johnnew",
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
    serializer: UserUsernameChangeConfirmResponseSerializer = UserUsernameChangeConfirmResponseSerializer(
        data=payload,
    )

    # Validate
    assert serializer.is_valid(), serializer.errors

    # Assert Nested Data
    assert serializer.validated_data["status_code"] == 200
    assert serializer.validated_data["user"]["username"] == "johnnew"


# Confirm Response — Missing Or Null User
def test_username_change_confirm_response_missing_or_null_user_is_invalid() -> None:
    """
    Verify Missing And Null User Field Raises Error Message.
    """

    # Missing User
    serializer_missing: UserUsernameChangeConfirmResponseSerializer = UserUsernameChangeConfirmResponseSerializer(
        data={"status_code": 200},
    )
    assert not serializer_missing.is_valid()
    assert str(serializer_missing.errors["user"][0]) == "User Details Is Required"

    # Null User
    serializer_null: UserUsernameChangeConfirmResponseSerializer = UserUsernameChangeConfirmResponseSerializer(
        data={"status_code": 200, "user": None},
    )
    assert not serializer_null.is_valid()
    assert str(serializer_null.errors["user"][0]) == "User Details Cannot Be Null"


# Bad Request Error — Optional Errors Field
def test_username_change_confirm_bad_request_errors_optional_and_valid() -> None:
    """
    Verify Confirm Bad Request Error Serializer Allows Optional Errors Field And Validates.
    """

    # Inputs
    payload_no_errors: dict[str, Any] = {
        "status_code": 400,
        # no "errors" provided (should default to None)
    }

    payload_with_errors: dict[str, Any] = {
        "status_code": 400,
        "errors": {
            "username": ["Username Is Required"],
            "re_username": ["Username Confirmation Cannot Be Blank"],
            "non_field_errors": ["General Error"],
        },
    }

    # Create Serializers
    serializer_no_errors: UserUsernameChangeConfirmBadRequestErrorResponseSerialzier = (
        UserUsernameChangeConfirmBadRequestErrorResponseSerialzier(data=payload_no_errors)
    )
    serializer_with_errors: UserUsernameChangeConfirmBadRequestErrorResponseSerialzier = (
        UserUsernameChangeConfirmBadRequestErrorResponseSerialzier(data=payload_with_errors)
    )

    # Validate
    assert serializer_no_errors.is_valid(), serializer_no_errors.errors
    assert serializer_with_errors.is_valid(), serializer_with_errors.errors

    # Assert Defaults And Data
    assert serializer_no_errors.validated_data["status_code"] == 400
    assert serializer_no_errors.validated_data["errors"] is None
    assert serializer_with_errors.validated_data["errors"]["username"] == ["Username Is Required"]


# Unauthorized Error — Request Flow
def test_username_change_request_unauthorized_defaults_and_missing_status_code() -> None:
    """
    Verify Request Unauthorized Error Serializer Defaults Error And Status Code Requirement.
    """

    # Valid With Defaults
    serializer_valid: UserUsernameChangeRequestUnauthorizedErrorResponseSerializer = (
        UserUsernameChangeRequestUnauthorizedErrorResponseSerializer(
            data={"status_code": 401},
        )
    )
    assert serializer_valid.is_valid(), serializer_valid.errors
    assert serializer_valid.validated_data["status_code"] == 401
    assert serializer_valid.validated_data["error"] == "Unauthorized"

    # Missing Status Code Invalid
    serializer_missing: UserUsernameChangeRequestUnauthorizedErrorResponseSerializer = (
        UserUsernameChangeRequestUnauthorizedErrorResponseSerializer(
            data={},
        )
    )
    assert not serializer_missing.is_valid()
    assert str(serializer_missing.errors["status_code"][0]) == "Status Code Is Required"


# Unauthorized Error — Confirm Flow
def test_username_change_confirm_unauthorized_defaults_and_missing_status_code() -> None:
    """
    Verify Confirm Unauthorized Error Serializer Defaults Error And Status Code Requirement.
    """

    # Valid With Defaults
    serializer_valid: UserUsernameChangeConfirmUnauthorizedErrorResponseSerializer = (
        UserUsernameChangeConfirmUnauthorizedErrorResponseSerializer(
            data={"status_code": 401},
        )
    )
    assert serializer_valid.is_valid(), serializer_valid.errors
    assert serializer_valid.validated_data["status_code"] == 401
    assert serializer_valid.validated_data["error"] == "Unauthorized"

    # Missing Status Code Invalid
    serializer_missing: UserUsernameChangeConfirmUnauthorizedErrorResponseSerializer = (
        UserUsernameChangeConfirmUnauthorizedErrorResponseSerializer(
            data={},
        )
    )
    assert not serializer_missing.is_valid()
    assert str(serializer_missing.errors["status_code"][0]) == "Status Code Is Required"
