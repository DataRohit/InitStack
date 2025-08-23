# ruff: noqa: PLR2004

# Standard Library Imports
from typing import Any

# Local Imports
from apps.users.serializers.user_reset_password_serializer import (
    UserResetPasswordConfirmBadRequestErrorResponseSerializer,
)
from apps.users.serializers.user_reset_password_serializer import UserResetPasswordConfirmPayloadSerializer
from apps.users.serializers.user_reset_password_serializer import UserResetPasswordConfirmResponseSerializer
from apps.users.serializers.user_reset_password_serializer import (
    UserResetPasswordConfirmUnauthorizedErrorResponseSerializer,
)
from apps.users.serializers.user_reset_password_serializer import UserResetPasswordRequestAcceptedResponseSerializer
from apps.users.serializers.user_reset_password_serializer import (
    UserResetPasswordRequestBadRequestErrorResponseSerializer,
)
from apps.users.serializers.user_reset_password_serializer import UserResetPasswordRequestPayloadSerializer


# Request Payload — Valid
def test_reset_password_request_payload_valid_when_identifiers_match() -> None:
    """
    Verify Request Payload Serializer Validates When Identifiers Match.
    """

    # Inputs
    payload: dict[str, str] = {
        "identifier": "johndoe@example.com",
        "re_identifier": "johndoe@example.com",
    }

    # Create Serializer
    serializer: UserResetPasswordRequestPayloadSerializer = UserResetPasswordRequestPayloadSerializer(data=payload)

    # Validate
    assert serializer.is_valid(), serializer.errors

    # Assert Values
    assert serializer.validated_data["identifier"] == payload["identifier"]
    assert serializer.validated_data["re_identifier"] == payload["re_identifier"]


# Request Payload — Identifier Mismatch
def test_reset_password_request_payload_identifier_mismatch_is_invalid() -> None:
    """
    Verify Request Payload Serializer Rejects When Identifiers Do Not Match.
    """

    # Inputs
    payload: dict[str, str] = {
        "identifier": "johndoe@example.com",
        "re_identifier": "john@example.com",
    }

    # Create Serializer
    serializer: UserResetPasswordRequestPayloadSerializer = UserResetPasswordRequestPayloadSerializer(data=payload)

    # Validate
    assert not serializer.is_valid()

    # Assert Error Message
    assert "identifier" in serializer.errors
    assert str(serializer.errors["identifier"][0]) == "Identifiers Do Not Match"


# Request Payload — Required/Null/Blank
def test_reset_password_request_payload_required_null_blank_errors() -> None:
    """
    Verify Required, Null, And Blank Error Messages For Request Payload.
    """

    # Missing All
    serializer_missing: UserResetPasswordRequestPayloadSerializer = UserResetPasswordRequestPayloadSerializer(data={})
    assert not serializer_missing.is_valid()
    assert str(serializer_missing.errors["identifier"][0]) == "Identifier Is Required"
    assert str(serializer_missing.errors["re_identifier"][0]) == "Identifier Confirmation Is Required"

    # Null Values
    serializer_null: UserResetPasswordRequestPayloadSerializer = UserResetPasswordRequestPayloadSerializer(
        data={"identifier": None, "re_identifier": None},
    )
    assert not serializer_null.is_valid()
    assert str(serializer_null.errors["identifier"][0]) == "Identifier Cannot Be Null"
    assert str(serializer_null.errors["re_identifier"][0]) == "Identifier Confirmation Cannot Be Null"

    # Blank Values
    serializer_blank: UserResetPasswordRequestPayloadSerializer = UserResetPasswordRequestPayloadSerializer(
        data={"identifier": "", "re_identifier": ""},
    )
    assert not serializer_blank.is_valid()
    assert str(serializer_blank.errors["identifier"][0]) == "Identifier Cannot Be Blank"
    assert str(serializer_blank.errors["re_identifier"][0]) == "Identifier Confirmation Cannot Be Blank"


# Request Accepted Response — Defaults And Valid
def test_reset_password_request_accepted_defaults_and_valid() -> None:
    """
    Verify Request Accepted Serializer Defaults Message And Validates.
    """

    # Inputs
    payload: dict[str, Any] = {
        "status_code": 202,
        # no "message" provided
    }

    # Create Serializer
    serializer: UserResetPasswordRequestAcceptedResponseSerializer = UserResetPasswordRequestAcceptedResponseSerializer(
        data=payload,
    )

    # Validate
    assert serializer.is_valid(), serializer.errors

    # Assert Defaults
    assert serializer.validated_data["status_code"] == 202
    assert serializer.validated_data["message"] == "Password Reset Request Sent Successfully"


# Request Accepted Response — Missing Status Code
def test_reset_password_request_accepted_missing_status_code_is_invalid() -> None:
    """
    Verify Missing Status Code Raises Error Message For Request Accepted Serializer.
    """

    # Inputs
    payload: dict[str, Any] = {}

    # Create Serializer
    serializer: UserResetPasswordRequestAcceptedResponseSerializer = UserResetPasswordRequestAcceptedResponseSerializer(
        data=payload,
    )

    # Validate
    assert not serializer.is_valid()

    # Assert Error Message
    assert str(serializer.errors["status_code"][0]) == "Status Code Is Required"


# Confirm Payload — Valid
def test_reset_password_confirm_payload_valid() -> None:
    """
    Verify Confirm Payload Serializer Accepts Valid Passwords.
    """

    # Inputs
    payload: dict[str, str] = {
        "password": "SecurePassword@123",
        "re_password": "SecurePassword@123",
    }

    # Create Serializer
    serializer: UserResetPasswordConfirmPayloadSerializer = UserResetPasswordConfirmPayloadSerializer(data=payload)

    # Validate
    assert serializer.is_valid(), serializer.errors

    # Assert Values
    assert serializer.validated_data["password"] == payload["password"]


# Confirm Payload — Password Mismatch
def test_reset_password_confirm_payload_password_mismatch() -> None:
    """
    Verify Error When Password And Confirmation Do Not Match.
    """

    # Inputs
    payload: dict[str, str] = {
        "password": "SecurePassword@123",
        "re_password": "SecurePassword@124",
    }

    # Create Serializer
    serializer: UserResetPasswordConfirmPayloadSerializer = UserResetPasswordConfirmPayloadSerializer(data=payload)

    # Validate
    assert not serializer.is_valid()

    # Assert Error
    assert "password" in serializer.errors
    assert str(serializer.errors["password"][0]) == "Passwords Do Not Match"


# Confirm Payload — Required/Null/Blank
def test_reset_password_confirm_payload_required_null_blank_and_rules() -> None:
    """
    Verify Required/Null/Blank Errors And Password Rules.
    """

    # Missing All
    serializer_missing: UserResetPasswordConfirmPayloadSerializer = UserResetPasswordConfirmPayloadSerializer(data={})
    assert not serializer_missing.is_valid()
    assert str(serializer_missing.errors["password"][0]) == "Password Is Required"
    assert str(serializer_missing.errors["re_password"][0]) == "Password Confirmation Is Required"

    # Null Values
    serializer_null: UserResetPasswordConfirmPayloadSerializer = UserResetPasswordConfirmPayloadSerializer(
        data={"password": None, "re_password": None},
    )
    assert not serializer_null.is_valid()
    assert str(serializer_null.errors["password"][0]) == "Password Cannot Be Null"
    assert str(serializer_null.errors["re_password"][0]) == "Password Confirmation Cannot Be Null"

    # Blank Values
    serializer_blank: UserResetPasswordConfirmPayloadSerializer = UserResetPasswordConfirmPayloadSerializer(
        data={"password": "", "re_password": ""},
    )
    assert not serializer_blank.is_valid()
    assert str(serializer_blank.errors["password"][0]) == "Password Cannot Be Blank"
    assert str(serializer_blank.errors["re_password"][0]) == "Password Confirmation Cannot Be Blank"

    # Too Short
    serializer_short: UserResetPasswordConfirmPayloadSerializer = UserResetPasswordConfirmPayloadSerializer(
        data={"password": "Ab1@", "re_password": "Ab1@"},
    )
    assert not serializer_short.is_valid()
    assert (
        str(serializer_short.errors["password"][0])
        == "Password Must Contain At Least One Uppercase Letter, One Lowercase Letter, One Digit, and One Special Character"  # noqa: E501
    )

    # Too Long
    long_pwd: str = ("A" * 61) + "b1@"
    serializer_long: UserResetPasswordConfirmPayloadSerializer = UserResetPasswordConfirmPayloadSerializer(
        data={"password": long_pwd, "re_password": long_pwd},
    )
    assert not serializer_long.is_valid()
    assert str(serializer_long.errors["password"][0]) == "Password Must Not Exceed 60 Characters"

    # Missing Complexity
    serializer_complexity: UserResetPasswordConfirmPayloadSerializer = UserResetPasswordConfirmPayloadSerializer(
        data={"password": "abcdefgh", "re_password": "abcdefgh"},
    )
    assert not serializer_complexity.is_valid()
    assert (
        str(serializer_complexity.errors["password"][0])
        == "Password Must Contain At Least One Uppercase Letter, One Lowercase Letter, One Digit, and One Special Character"  # noqa: E501
    )


# Confirm Response — Defaults And Valid
def test_reset_password_confirm_response_defaults_and_valid() -> None:
    """
    Verify Confirm Response Serializer Defaults Message And Validates.
    """

    # Inputs
    payload: dict[str, Any] = {
        "status_code": 200,
        # no "message" provided
    }

    # Create Serializer
    serializer: UserResetPasswordConfirmResponseSerializer = UserResetPasswordConfirmResponseSerializer(data=payload)

    # Validate
    assert serializer.is_valid(), serializer.errors

    # Assert Defaults
    assert serializer.validated_data["status_code"] == 200
    assert serializer.validated_data["message"] == "Password Reset Completed Successfully"


# Confirm Response — Missing Status Code
def test_reset_password_confirm_response_missing_status_code_is_invalid() -> None:
    """
    Verify Missing Status Code Raises Error Message For Confirm Response Serializer.
    """

    # Inputs
    payload: dict[str, Any] = {}

    # Create Serializer
    serializer: UserResetPasswordConfirmResponseSerializer = UserResetPasswordConfirmResponseSerializer(data=payload)

    # Validate
    assert not serializer.is_valid()

    # Assert Error Message
    assert str(serializer.errors["status_code"][0]) == "Status Code Is Required"


# Request Bad Request Error — Optional Errors Field
def test_reset_password_request_bad_request_errors_optional_and_valid() -> None:
    """
    Verify Request Bad Request Error Serializer Allows Optional Errors Field And Validates.
    """

    # Inputs
    payload_no_errors: dict[str, Any] = {
        "status_code": 400,
        # no "errors" provided (should default to None)
    }

    payload_with_errors: dict[str, Any] = {
        "status_code": 400,
        "errors": {
            "identifier": ["Identifier Is Required"],
            "re_identifier": ["Identifier Confirmation Cannot Be Blank"],
            "non_field_errors": ["General Error"],
        },
    }

    # Create Serializers
    serializer_no_errors: UserResetPasswordRequestBadRequestErrorResponseSerializer = (
        UserResetPasswordRequestBadRequestErrorResponseSerializer(data=payload_no_errors)
    )
    serializer_with_errors: UserResetPasswordRequestBadRequestErrorResponseSerializer = (
        UserResetPasswordRequestBadRequestErrorResponseSerializer(data=payload_with_errors)
    )

    # Validate
    assert serializer_no_errors.is_valid(), serializer_no_errors.errors
    assert serializer_with_errors.is_valid(), serializer_with_errors.errors

    # Assert Defaults And Data
    assert serializer_no_errors.validated_data["status_code"] == 400
    assert serializer_no_errors.validated_data["errors"] is None
    assert serializer_with_errors.validated_data["errors"]["identifier"] == ["Identifier Is Required"]


# Confirm Bad Request Error — Optional Errors Field
def test_reset_password_confirm_bad_request_errors_optional_and_valid() -> None:
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
            "password": [
                "Password Must Contain At Least One Uppercase Letter, One Lowercase Letter, One Digit, and One Special Character",  # noqa: E501
            ],
            "re_password": ["Password Confirmation Is Required"],
            "non_field_errors": ["General Error"],
        },
    }

    # Create Serializers
    serializer_no_errors: UserResetPasswordConfirmBadRequestErrorResponseSerializer = (
        UserResetPasswordConfirmBadRequestErrorResponseSerializer(data=payload_no_errors)
    )
    serializer_with_errors: UserResetPasswordConfirmBadRequestErrorResponseSerializer = (
        UserResetPasswordConfirmBadRequestErrorResponseSerializer(data=payload_with_errors)
    )

    # Validate
    assert serializer_no_errors.is_valid(), serializer_no_errors.errors
    assert serializer_with_errors.is_valid(), serializer_with_errors.errors

    # Assert Defaults And Data
    assert serializer_no_errors.validated_data["status_code"] == 400
    assert serializer_no_errors.validated_data["errors"] is None
    assert serializer_with_errors.validated_data["errors"]["re_password"] == ["Password Confirmation Is Required"]


# Confirm Unauthorized Error — Defaults And Missing Status Code
def test_reset_password_confirm_unauthorized_defaults_and_missing_status_code() -> None:
    """
    Verify Confirm Unauthorized Error Serializer Defaults Error And Status Code Requirement.
    """

    # Valid With Defaults
    serializer_valid: UserResetPasswordConfirmUnauthorizedErrorResponseSerializer = (
        UserResetPasswordConfirmUnauthorizedErrorResponseSerializer(
            data={"status_code": 401},
        )
    )
    assert serializer_valid.is_valid(), serializer_valid.errors
    assert serializer_valid.validated_data["status_code"] == 401
    assert serializer_valid.validated_data["error"] == "Unauthorized"

    # Missing Status Code Invalid
    serializer_missing: UserResetPasswordConfirmUnauthorizedErrorResponseSerializer = (
        UserResetPasswordConfirmUnauthorizedErrorResponseSerializer(
            data={},
        )
    )
    assert not serializer_missing.is_valid()
    assert str(serializer_missing.errors["status_code"][0]) == "Status Code Is Required"
