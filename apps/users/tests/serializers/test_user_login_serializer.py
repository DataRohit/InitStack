# ruff: noqa: PLR2004

# Local Imports
from apps.users.serializers.user_login_serializer import UserLoginBadRequestErrorResponseSerializer
from apps.users.serializers.user_login_serializer import UserLoginPayloadSerializer
from apps.users.serializers.user_login_serializer import UserLoginResponseSerializer
from apps.users.serializers.user_login_serializer import UserLoginUnauthorizedErrorResponseSerializer


# Test Payload Serializer Valid
def test_user_login_payload_serializer_valid() -> None:
    """
    Verify Payload Serializer Validates With Identifier And Password.
    """

    # Inputs
    payload: dict[str, str] = {
        "identifier": "johndoe",
        "password": "SecurePassword@123",
    }

    # Create Serializer
    serializer: UserLoginPayloadSerializer = UserLoginPayloadSerializer(data=payload)

    # Validate
    assert serializer.is_valid(), serializer.errors

    # Assert Values
    assert serializer.validated_data["identifier"] == payload["identifier"]
    assert serializer.validated_data["password"] == payload["password"]


# Test Payload Required Field Errors
def test_user_login_payload_serializer_missing_required_fields() -> None:
    """
    Verify Required Field Errors When Identifier And Password Missing.
    """

    # Inputs
    payload: dict[str, str] = {}

    # Create Serializer
    serializer: UserLoginPayloadSerializer = UserLoginPayloadSerializer(data=payload)

    # Validate
    assert not serializer.is_valid()

    # Assert Error Messages
    assert str(serializer.errors["identifier"][0]) == "Identifier Is Required"
    assert str(serializer.errors["password"][0]) == "Password Is Required"


# Test Payload Null And Blank Errors
def test_user_login_payload_serializer_null_and_blank_errors() -> None:
    """
    Verify Null And Blank Error Messages For Identifier And Password.
    """

    # Inputs
    payload_null: dict[str, object] = {"identifier": None, "password": None}
    payload_blank: dict[str, str] = {"identifier": "", "password": ""}

    # Null Case
    serializer_null: UserLoginPayloadSerializer = UserLoginPayloadSerializer(data=payload_null)
    assert not serializer_null.is_valid()
    assert str(serializer_null.errors["identifier"][0]) == "Identifier Cannot Be Null"
    assert str(serializer_null.errors["password"][0]) == "Password Cannot Be Null"

    # Blank Case
    serializer_blank: UserLoginPayloadSerializer = UserLoginPayloadSerializer(data=payload_blank)
    assert not serializer_blank.is_valid()
    assert str(serializer_blank.errors["identifier"][0]) == "Identifier Cannot Be Blank"
    assert str(serializer_blank.errors["password"][0]) == "Password Cannot Be Blank"


# Test Response Serializer Valid
def test_user_login_response_serializer_valid_payload() -> None:
    """
    Verify Response Serializer Accepts Valid Payload With Nested User.
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
            "is_active": True,
            "is_staff": False,
            "is_superuser": False,
            "date_joined": "2025-08-16T19:04:06.602446+05:30",
            "last_login": "2025-08-16T19:10:06.602446+05:30",
            "access_token": "access.token.value",
            "refresh_token": "refresh.token.value",
        },
    }

    # Create Serializer
    serializer: UserLoginResponseSerializer = UserLoginResponseSerializer(data=payload)

    # Validate
    assert serializer.is_valid(), serializer.errors

    # Assert Nested Data
    assert serializer.validated_data["status_code"] == 200
    assert serializer.validated_data["user"]["username"] == "johndoe"
    assert serializer.validated_data["user"]["access_token"] == "access.token.value"  # noqa: S105
    assert serializer.validated_data["user"]["refresh_token"] == "refresh.token.value"  # noqa: S105


# Test Response Missing User
def test_user_login_response_serializer_missing_user_is_invalid() -> None:
    """
    Verify Missing User Field Raises Error Message.
    """

    # Inputs
    payload: dict[str, object] = {
        "status_code": 200,
        # "user" missing
    }

    # Create Serializer
    serializer: UserLoginResponseSerializer = UserLoginResponseSerializer(data=payload)

    # Validate
    assert not serializer.is_valid()

    # Assert Error Message
    assert "user" in serializer.errors
    assert str(serializer.errors["user"][0]) == "User Details Is Required"


# Test Response Null User
def test_user_login_response_serializer_null_user_is_invalid() -> None:
    """
    Verify Null User Field Raises Error Message.
    """

    # Inputs
    payload: dict[str, object] = {
        "status_code": 200,
        "user": None,
    }

    # Create Serializer
    serializer: UserLoginResponseSerializer = UserLoginResponseSerializer(data=payload)

    # Validate
    assert not serializer.is_valid()

    # Assert Error Message
    assert "user" in serializer.errors
    assert str(serializer.errors["user"][0]) == "User Details Cannot Be Null"


# Test Unauthorized Defaults
def test_user_login_unauthorized_default_error_and_valid() -> None:
    """
    Verify Unauthorized Error Serializer Defaults Error And Validates.
    """

    # Inputs
    payload: dict[str, object] = {
        "status_code": 401,
        # no "error" provided
    }

    # Create Serializer
    serializer: UserLoginUnauthorizedErrorResponseSerializer = UserLoginUnauthorizedErrorResponseSerializer(
        data=payload,
    )

    # Validate
    assert serializer.is_valid(), serializer.errors

    # Assert Defaults
    assert serializer.validated_data["status_code"] == 401
    assert serializer.validated_data["error"] == "Unauthorized"


# Test Unauthorized Missing Status Code
def test_user_login_unauthorized_missing_status_code_is_invalid() -> None:
    """
    Verify Missing Status Code Raises Error Message For Unauthorized Error Serializer.
    """

    # Inputs
    payload: dict[str, object] = {
        # "status_code" missing
    }

    # Create Serializer
    serializer: UserLoginUnauthorizedErrorResponseSerializer = UserLoginUnauthorizedErrorResponseSerializer(
        data=payload,
    )

    # Validate
    assert not serializer.is_valid()

    # Assert Error Message
    assert "status_code" in serializer.errors
    assert str(serializer.errors["status_code"][0]) == "Status Code Is Required"


# Test Unauthorized Specific Error Message
def test_user_login_unauthorized_specific_error_message_is_valid() -> None:
    """
    Verify Unauthorized Error Serializer Accepts Specific Error Message.
    """

    # Inputs
    payload: dict[str, object] = {
        "status_code": 401,
        "error": "Invalid Username Or Password",
    }

    # Create Serializer
    serializer: UserLoginUnauthorizedErrorResponseSerializer = UserLoginUnauthorizedErrorResponseSerializer(
        data=payload,
    )

    # Validate
    assert serializer.is_valid(), serializer.errors

    # Assert Data
    assert serializer.validated_data["status_code"] == 401
    assert serializer.validated_data["error"] == "Invalid Username Or Password"


# Test Bad Request Errors Optional Field
def test_user_login_bad_request_errors_optional_and_valid() -> None:
    """
    Verify Bad Request Error Response Allows Optional Errors Field And Validates.
    """

    # Inputs
    payload_no_errors: dict[str, object] = {
        # status_code should default to 400 here
    }

    payload_with_errors: dict[str, object] = {
        "status_code": 400,
        "errors": {
            "identifier": ["Identifier Is Required"],
            "password": ["Password Cannot Be Blank"],
            "non_field_errors": ["General Error"],
        },
    }

    # Create Serializers
    serializer_no_errors: UserLoginBadRequestErrorResponseSerializer = UserLoginBadRequestErrorResponseSerializer(
        data=payload_no_errors,
    )
    serializer_with_errors: UserLoginBadRequestErrorResponseSerializer = UserLoginBadRequestErrorResponseSerializer(
        data=payload_with_errors,
    )

    # Validate
    assert serializer_no_errors.is_valid(), serializer_no_errors.errors
    assert serializer_with_errors.is_valid(), serializer_with_errors.errors

    # Assert Defaults And Data
    assert serializer_no_errors.validated_data["status_code"] == 400
    assert serializer_no_errors.validated_data["errors"] is None
    assert serializer_with_errors.validated_data["errors"]["identifier"] == ["Identifier Is Required"]
