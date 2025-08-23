# ruff: noqa: PLR2004

# Local Imports
from apps.users.serializers.user_reactivate_serializer import UserReactivateBadRequestErrorResponseSerializer
from apps.users.serializers.user_reactivate_serializer import UserReactivateConfirmResponseSerializer
from apps.users.serializers.user_reactivate_serializer import UserReactivateConfirmUnauthorizedErrorResponseSerializer
from apps.users.serializers.user_reactivate_serializer import UserReactivatePayloadSerializer
from apps.users.serializers.user_reactivate_serializer import UserReactivateRequestAcceptedResponseSerializer


# Test Payload Serializer Valid
def test_user_reactivate_payload_serializer_valid_when_identifiers_match() -> None:
    """
    Verify Payload Serializer Validates When Identifiers Match.
    """

    # Inputs
    payload: dict[str, str] = {
        "identifier": "johndoe@example.com",
        "re_identifier": "johndoe@example.com",
    }

    # Create Serializer
    serializer: UserReactivatePayloadSerializer = UserReactivatePayloadSerializer(data=payload)

    # Validate
    assert serializer.is_valid(), serializer.errors

    # Assert Values
    assert serializer.validated_data["identifier"] == payload["identifier"]
    assert serializer.validated_data["re_identifier"] == payload["re_identifier"]


# Test Payload Serializer Identifier Mismatch
def test_user_reactivate_payload_serializer_identifier_mismatch_is_invalid() -> None:
    """
    Verify Payload Serializer Rejects When Identifiers Do Not Match.
    """

    # Inputs
    payload: dict[str, str] = {
        "identifier": "johndoe@example.com",
        "re_identifier": "john@example.com",
    }

    # Create Serializer
    serializer: UserReactivatePayloadSerializer = UserReactivatePayloadSerializer(data=payload)

    # Validate
    assert not serializer.is_valid()

    # Assert Error Message At Identifier Key
    assert "identifier" in serializer.errors
    assert str(serializer.errors["identifier"][0]) == "Identifiers Do Not Match"


# Test Payload Required Field Errors
def test_user_reactivate_payload_serializer_missing_required_fields() -> None:
    """
    Verify Required Field Errors When Identifier And Re Identifier Missing.
    """

    # Inputs
    payload: dict[str, str] = {}

    # Create Serializer
    serializer: UserReactivatePayloadSerializer = UserReactivatePayloadSerializer(data=payload)

    # Validate
    assert not serializer.is_valid()

    # Assert Error Messages
    assert str(serializer.errors["identifier"][0]) == "Identifier Is Required"
    assert str(serializer.errors["re_identifier"][0]) == "Identifier Confirmation Is Required"


# Test Payload Null And Blank Errors
def test_user_reactivate_payload_serializer_null_and_blank_errors() -> None:
    """
    Verify Null And Blank Error Messages For Identifier Fields.
    """

    # Inputs
    payload_null: dict[str, object] = {"identifier": None, "re_identifier": None}
    payload_blank: dict[str, str] = {"identifier": "", "re_identifier": ""}

    # Null Case
    serializer_null: UserReactivatePayloadSerializer = UserReactivatePayloadSerializer(data=payload_null)
    assert not serializer_null.is_valid()
    assert str(serializer_null.errors["identifier"][0]) == "Identifier Cannot Be Null"
    assert str(serializer_null.errors["re_identifier"][0]) == "Identifier Confirmation Cannot Be Null"

    # Blank Case
    serializer_blank: UserReactivatePayloadSerializer = UserReactivatePayloadSerializer(data=payload_blank)
    assert not serializer_blank.is_valid()
    assert str(serializer_blank.errors["identifier"][0]) == "Identifier Cannot Be Blank"
    assert str(serializer_blank.errors["re_identifier"][0]) == "Identifier Confirmation Cannot Be Blank"


# Test Request Accepted Defaults
def test_user_reactivate_request_accepted_default_message_and_valid() -> None:
    """
    Verify Request Accepted Serializer Defaults Message And Validates.
    """

    # Inputs
    payload: dict[str, object] = {
        "status_code": 202,
        # no "message" provided
    }

    # Create Serializer
    serializer: UserReactivateRequestAcceptedResponseSerializer = UserReactivateRequestAcceptedResponseSerializer(
        data=payload,
    )

    # Validate
    assert serializer.is_valid(), serializer.errors

    # Assert Defaults
    assert serializer.validated_data["status_code"] == 202
    assert serializer.validated_data["message"] == "Reactivation Request Sent Successfully"


# Test Request Accepted Missing Status Code
def test_user_reactivate_request_accepted_missing_status_code_is_invalid() -> None:
    """
    Verify Missing Status Code Raises Error Message For Request Accepted Serializer.
    """

    # Inputs
    payload: dict[str, object] = {
        # "status_code" missing
    }

    # Create Serializer
    serializer: UserReactivateRequestAcceptedResponseSerializer = UserReactivateRequestAcceptedResponseSerializer(
        data=payload,
    )

    # Validate
    assert not serializer.is_valid()

    # Assert Error Message
    assert "status_code" in serializer.errors
    assert str(serializer.errors["status_code"][0]) == "Status Code Is Required"


# Test Confirm Response Valid
def test_user_reactivate_confirm_response_valid_payload_is_valid() -> None:
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
            "is_active": True,
            "is_staff": False,
            "is_superuser": False,
            "date_joined": "2025-08-16T19:04:06.602446+05:30",
            "last_login": None,
        },
    }

    # Create Serializer
    serializer: UserReactivateConfirmResponseSerializer = UserReactivateConfirmResponseSerializer(
        data=payload,
    )

    # Validate
    assert serializer.is_valid(), serializer.errors

    # Assert Nested Data
    assert serializer.validated_data["status_code"] == 200
    assert serializer.validated_data["user"]["username"] == "johndoe"


# Test Confirm Response Missing User
def test_user_reactivate_confirm_response_missing_user_is_invalid() -> None:
    """
    Verify Missing User Field Raises Error Message.
    """

    # Inputs
    payload: dict[str, object] = {
        "status_code": 200,
        # "user" missing
    }

    # Create Serializer
    serializer: UserReactivateConfirmResponseSerializer = UserReactivateConfirmResponseSerializer(
        data=payload,
    )

    # Validate
    assert not serializer.is_valid()

    # Assert Error Message
    assert "user" in serializer.errors
    assert str(serializer.errors["user"][0]) == "User Details Is Required"


# Test Confirm Response Null User
def test_user_reactivate_confirm_response_null_user_is_invalid() -> None:
    """
    Verify Null User Field Raises Error Message.
    """

    # Inputs
    payload: dict[str, object] = {
        "status_code": 200,
        "user": None,
    }

    # Create Serializer
    serializer: UserReactivateConfirmResponseSerializer = UserReactivateConfirmResponseSerializer(
        data=payload,
    )

    # Validate
    assert not serializer.is_valid()

    # Assert Error Message
    assert "user" in serializer.errors
    assert str(serializer.errors["user"][0]) == "User Details Cannot Be Null"


# Test Bad Request Errors Optional Field
def test_user_reactivate_bad_request_errors_optional_and_valid() -> None:
    """
    Verify Bad Request Error Response Allows Optional Errors Field And Validates.
    """

    # Inputs
    payload_no_errors: dict[str, object] = {
        "status_code": 400,
        # no "errors" provided (should default to None)
    }

    payload_with_errors: dict[str, object] = {
        "status_code": 400,
        "errors": {
            "identifier": ["Identifier Is Required"],
            "re_identifier": ["Identifier Confirmation Cannot Be Blank"],
            "non_field_errors": ["General Error"],
        },
    }

    # Create Serializers
    serializer_no_errors: UserReactivateBadRequestErrorResponseSerializer = (
        UserReactivateBadRequestErrorResponseSerializer(data=payload_no_errors)
    )
    serializer_with_errors: UserReactivateBadRequestErrorResponseSerializer = (
        UserReactivateBadRequestErrorResponseSerializer(data=payload_with_errors)
    )

    # Validate
    assert serializer_no_errors.is_valid(), serializer_no_errors.errors
    assert serializer_with_errors.is_valid(), serializer_with_errors.errors

    # Assert Defaults And Data
    assert serializer_no_errors.validated_data["status_code"] == 400
    assert serializer_no_errors.validated_data["errors"] is None
    assert serializer_with_errors.validated_data["errors"]["identifier"] == ["Identifier Is Required"]


# Test Confirm Unauthorized Defaults
def test_user_reactivate_confirm_unauthorized_default_error_and_valid() -> None:
    """
    Verify Confirm Unauthorized Error Serializer Defaults Error And Validates.
    """

    # Inputs
    payload: dict[str, object] = {
        "status_code": 401,
        # no "error" provided
    }

    # Create Serializer
    serializer: UserReactivateConfirmUnauthorizedErrorResponseSerializer = (
        UserReactivateConfirmUnauthorizedErrorResponseSerializer(
            data=payload,
        )
    )

    # Validate
    assert serializer.is_valid(), serializer.errors

    # Assert Defaults
    assert serializer.validated_data["status_code"] == 401
    assert serializer.validated_data["error"] == "Unauthorized"


# Test Confirm Unauthorized Missing Status Code
def test_user_reactivate_confirm_unauthorized_missing_status_code_is_invalid() -> None:
    """
    Verify Missing Status Code Raises Error Message For Confirm Unauthorized Error Serializer.
    """

    # Inputs
    payload: dict[str, object] = {
        # "status_code" missing
    }

    # Create Serializer
    serializer: UserReactivateConfirmUnauthorizedErrorResponseSerializer = (
        UserReactivateConfirmUnauthorizedErrorResponseSerializer(
            data=payload,
        )
    )

    # Validate
    assert not serializer.is_valid()

    # Assert Error Message
    assert "status_code" in serializer.errors
    assert str(serializer.errors["status_code"][0]) == "Status Code Is Required"
