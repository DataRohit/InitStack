# ruff: noqa: PLR2004

# Local Imports
from apps.users.serializers.user_re_login_serializer import UserReLoginBadRequestErrorResponseSerializer
from apps.users.serializers.user_re_login_serializer import UserReLoginPayloadSerializer
from apps.users.serializers.user_re_login_serializer import UserReLoginUnauthorizedErrorResponseSerializer


# Test Payload Serializer Valid
def test_user_re_login_payload_serializer_valid() -> None:
    """
    Verify Payload Serializer Validates With Refresh Token.
    """

    # Inputs
    payload: dict[str, str] = {
        "refresh_token": "refresh.token.value",
    }

    # Create Serializer
    serializer: UserReLoginPayloadSerializer = UserReLoginPayloadSerializer(data=payload)

    # Validate
    assert serializer.is_valid(), serializer.errors

    # Assert Values
    assert serializer.validated_data["refresh_token"] == payload["refresh_token"]


# Test Payload Required Field Errors
def test_user_re_login_payload_serializer_missing_required_fields() -> None:
    """
    Verify Required Field Errors When Refresh Token Missing.
    """

    # Inputs
    payload: dict[str, str] = {}

    # Create Serializer
    serializer: UserReLoginPayloadSerializer = UserReLoginPayloadSerializer(data=payload)

    # Validate
    assert not serializer.is_valid()

    # Assert Error Messages
    assert str(serializer.errors["refresh_token"][0]) == "Refresh Token Is Required"


# Test Payload Null And Blank Errors
def test_user_re_login_payload_serializer_null_and_blank_errors() -> None:
    """
    Verify Null And Blank Error Messages For Refresh Token.
    """

    # Inputs
    payload_null: dict[str, object] = {"refresh_token": None}
    payload_blank: dict[str, str] = {"refresh_token": ""}

    # Null Case
    serializer_null: UserReLoginPayloadSerializer = UserReLoginPayloadSerializer(data=payload_null)
    assert not serializer_null.is_valid()
    assert str(serializer_null.errors["refresh_token"][0]) == "Refresh Token Cannot Be Null"

    # Blank Case
    serializer_blank: UserReLoginPayloadSerializer = UserReLoginPayloadSerializer(data=payload_blank)
    assert not serializer_blank.is_valid()
    assert str(serializer_blank.errors["refresh_token"][0]) == "Refresh Token Cannot Be Blank"


# Test Bad Request Default Error And Valid
def test_user_re_login_bad_request_default_error_and_valid() -> None:
    """
    Verify Bad Request Error Serializer Defaults Error And Validates.
    """

    # Inputs
    payload: dict[str, object] = {
        "status_code": 400,
        # no "error" provided
    }

    # Create Serializer
    serializer: UserReLoginBadRequestErrorResponseSerializer = UserReLoginBadRequestErrorResponseSerializer(
        data=payload,
    )

    # Validate
    assert serializer.is_valid(), serializer.errors

    # Assert Defaults
    assert serializer.validated_data["status_code"] == 400
    assert serializer.validated_data["error"] == "Bad Request"


# Test Bad Request Missing Status Code
def test_user_re_login_bad_request_missing_status_code_is_invalid() -> None:
    """
    Verify Missing Status Code Raises Error Message For Bad Request Error Serializer.
    """

    # Inputs
    payload: dict[str, object] = {
        # "status_code" missing
    }

    # Create Serializer
    serializer: UserReLoginBadRequestErrorResponseSerializer = UserReLoginBadRequestErrorResponseSerializer(
        data=payload,
    )

    # Validate
    assert not serializer.is_valid()

    # Assert Error Message
    assert "status_code" in serializer.errors
    assert str(serializer.errors["status_code"][0]) == "Status Code Is Required"


# Test Bad Request Specific Error Message
def test_user_re_login_bad_request_specific_error_message_is_valid() -> None:
    """
    Verify Bad Request Error Serializer Accepts Specific Error Message.
    """

    # Inputs
    payload: dict[str, object] = {
        "status_code": 400,
        "error": "Invalid Payload",
    }

    # Create Serializer
    serializer: UserReLoginBadRequestErrorResponseSerializer = UserReLoginBadRequestErrorResponseSerializer(
        data=payload,
    )

    # Validate
    assert serializer.is_valid(), serializer.errors

    # Assert Data
    assert serializer.validated_data["status_code"] == 400
    assert serializer.validated_data["error"] == "Invalid Payload"


# Test Unauthorized Defaults
def test_user_re_login_unauthorized_default_error_and_valid() -> None:
    """
    Verify Unauthorized Error Serializer Defaults Error And Validates.
    """

    # Inputs
    payload: dict[str, object] = {
        "status_code": 401,
        # no "error" provided
    }

    # Create Serializer
    serializer: UserReLoginUnauthorizedErrorResponseSerializer = UserReLoginUnauthorizedErrorResponseSerializer(
        data=payload,
    )

    # Validate
    assert serializer.is_valid(), serializer.errors

    # Assert Defaults
    assert serializer.validated_data["status_code"] == 401
    assert serializer.validated_data["error"] == "Unauthorized"


# Test Unauthorized Missing Status Code
def test_user_re_login_unauthorized_missing_status_code_is_invalid() -> None:
    """
    Verify Missing Status Code Raises Error Message For Unauthorized Error Serializer.
    """

    # Inputs
    payload: dict[str, object] = {
        # "status_code" missing
    }

    # Create Serializer
    serializer: UserReLoginUnauthorizedErrorResponseSerializer = UserReLoginUnauthorizedErrorResponseSerializer(
        data=payload,
    )

    # Validate
    assert not serializer.is_valid()

    # Assert Error Message
    assert "status_code" in serializer.errors
    assert str(serializer.errors["status_code"][0]) == "Status Code Is Required"


# Test Unauthorized Specific Error Message
def test_user_re_login_unauthorized_specific_error_message_is_valid() -> None:
    """
    Verify Unauthorized Error Serializer Accepts Specific Error Message.
    """

    # Inputs
    payload: dict[str, object] = {
        "status_code": 401,
        "error": "Token Has Expired",
    }

    # Create Serializer
    serializer: UserReLoginUnauthorizedErrorResponseSerializer = UserReLoginUnauthorizedErrorResponseSerializer(
        data=payload,
    )

    # Validate
    assert serializer.is_valid(), serializer.errors

    # Assert Data
    assert serializer.validated_data["status_code"] == 401
    assert serializer.validated_data["error"] == "Token Has Expired"
