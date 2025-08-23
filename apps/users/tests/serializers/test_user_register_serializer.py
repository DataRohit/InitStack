# ruff: noqa: PLR2004

# Standard Library Imports
from typing import Any

# Third Party Imports
import pytest
from django.contrib.auth import get_user_model

# Local Imports
from apps.users.serializers.user_register_serializer import UserCreateBadRequestErrorResponseSerializer
from apps.users.serializers.user_register_serializer import UserRegisterPayloadSerializer
from apps.users.serializers.user_register_serializer import UserRegisterResponseSerializer

# Get User Model
User = get_user_model()

# Enable Django DB Access For All Tests In This Module
pytestmark = pytest.mark.django_db


# Valid Payload Test
def test_user_register_payload_serializer_valid() -> None:
    """
    Verify Payload Serializer Is Valid For Correct Input.
    """

    # Inputs
    payload: dict[str, Any] = {
        "username": "johndoe",
        "email": "johndoe@example.com",
        "first_name": "John",
        "last_name": "Doe",
        "password": "SecurePassword@123",
        "re_password": "SecurePassword@123",
    }

    # Create Serializer
    serializer: UserRegisterPayloadSerializer = UserRegisterPayloadSerializer(data=payload)

    # Validate
    assert serializer.is_valid(), serializer.errors

    # Assert Values
    assert serializer.validated_data["username"] == payload["username"]
    assert serializer.validated_data["email"] == payload["email"]


# Password Mismatch Test
def test_user_register_payload_serializer_password_mismatch() -> None:
    """
    Verify Error When Password And Confirmation Do Not Match.
    """

    # Inputs
    payload: dict[str, Any] = {
        "username": "johndoe",
        "email": "johndoe@example.com",
        "first_name": "John",
        "last_name": "Doe",
        "password": "SecurePassword@123",
        "re_password": "SecurePassword@124",
    }

    # Create Serializer
    serializer: UserRegisterPayloadSerializer = UserRegisterPayloadSerializer(data=payload)

    # Validate
    assert not serializer.is_valid()

    # Assert Error Message On Password
    assert "password" in serializer.errors
    assert str(serializer.errors["password"][0]) == "Passwords Do Not Match"


# Required Fields Test
def test_user_register_payload_serializer_missing_required_fields() -> None:
    """
    Verify Required Field Errors When All Fields Missing.
    """

    # Inputs
    payload: dict[str, Any] = {}

    # Create Serializer
    serializer: UserRegisterPayloadSerializer = UserRegisterPayloadSerializer(data=payload)

    # Validate
    assert not serializer.is_valid()

    # Assert Required Messages
    assert str(serializer.errors["username"][0]) == "Username Is Required"
    assert str(serializer.errors["email"][0]) == "Email Is Required"
    assert str(serializer.errors["first_name"][0]) == "First Name Is Required"
    assert str(serializer.errors["last_name"][0]) == "Last Name Is Required"
    assert str(serializer.errors["password"][0]) == "Password Is Required"
    assert str(serializer.errors["re_password"][0]) == "Password Confirmation Is Required"


# Null And Blank Test
def test_user_register_payload_serializer_null_and_blank_errors() -> None:
    """
    Verify Null And Blank Error Messages For All Fields.
    """

    # Inputs
    payload_null: dict[str, Any] = {
        "username": None,
        "email": None,
        "first_name": None,
        "last_name": None,
        "password": None,
        "re_password": None,
    }
    payload_blank: dict[str, Any] = {
        "username": "",
        "email": "",
        "first_name": "",
        "last_name": "",
        "password": "",
        "re_password": "",
    }

    # Null Case
    serializer_null: UserRegisterPayloadSerializer = UserRegisterPayloadSerializer(data=payload_null)
    assert not serializer_null.is_valid()
    assert str(serializer_null.errors["username"][0]) == "Username Cannot Be Null"
    assert str(serializer_null.errors["email"][0]) == "Email Cannot Be Null"
    assert str(serializer_null.errors["first_name"][0]) == "First Name Cannot Be Null"
    assert str(serializer_null.errors["last_name"][0]) == "Last Name Cannot Be Null"
    assert str(serializer_null.errors["password"][0]) == "Password Cannot Be Null"
    assert str(serializer_null.errors["re_password"][0]) == "Password Confirmation Cannot Be Null"

    # Blank Case
    serializer_blank: UserRegisterPayloadSerializer = UserRegisterPayloadSerializer(data=payload_blank)
    assert not serializer_blank.is_valid()
    assert str(serializer_blank.errors["username"][0]) == "Username Cannot Be Blank"
    assert str(serializer_blank.errors["email"][0]) == "Email Cannot Be Blank"
    assert str(serializer_blank.errors["first_name"][0]) == "First Name Cannot Be Blank"
    assert str(serializer_blank.errors["last_name"][0]) == "Last Name Cannot Be Blank"
    assert str(serializer_blank.errors["password"][0]) == "Password Cannot Be Blank"
    assert str(serializer_blank.errors["re_password"][0]) == "Password Confirmation Cannot Be Blank"


# Username Format And Length Test
def test_user_register_payload_serializer_username_format_and_length_errors() -> None:
    """
    Verify Username Regex And Max Length Errors.
    """

    # Inputs
    payload_invalid: dict[str, Any] = {
        "username": "john doe",  # has space
        "email": "john@example.com",
        "first_name": "John",
        "last_name": "Doe",
        "password": "SecurePassword@123",
        "re_password": "SecurePassword@123",
    }

    payload_too_long: dict[str, Any] = {
        "username": "a" * 61,
        "email": "john@example.com",
        "first_name": "John",
        "last_name": "Doe",
        "password": "SecurePassword@123",
        "re_password": "SecurePassword@123",
    }

    # Invalid Username Format
    serializer_invalid: UserRegisterPayloadSerializer = UserRegisterPayloadSerializer(data=payload_invalid)
    assert not serializer_invalid.is_valid()
    assert (
        str(serializer_invalid.errors["username"][0])
        == "Username Must Contain Only Alphanumeric Characters With No Spaces"
    )

    # Username Too Long
    serializer_long: UserRegisterPayloadSerializer = UserRegisterPayloadSerializer(data=payload_too_long)
    assert not serializer_long.is_valid()
    assert str(serializer_long.errors["username"][0]) == "Username Must Not Exceed 60 Characters"


# Email Format Test
def test_user_register_payload_serializer_email_invalid_format() -> None:
    """
    Verify Invalid Email Format Error Message.
    """

    # Inputs
    payload: dict[str, Any] = {
        "username": "johndoe",
        "email": "invalid-email",
        "first_name": "John",
        "last_name": "Doe",
        "password": "SecurePassword@123",
        "re_password": "SecurePassword@123",
    }

    # Create Serializer
    serializer: UserRegisterPayloadSerializer = UserRegisterPayloadSerializer(data=payload)

    # Validate
    assert not serializer.is_valid()

    # Assert Error Message
    assert str(serializer.errors["email"][0]) == "Invalid Email Address"


# Name Fields Format And Length Test
def test_user_register_payload_serializer_name_fields_format_and_length() -> None:
    """
    Verify First And Last Name Regex And Max Length Errors.
    """

    # Inputs
    payload_invalid: dict[str, Any] = {
        "username": "johndoe",
        "email": "john@example.com",
        "first_name": "John1",
        "last_name": "Doe2",
        "password": "SecurePassword@123",
        "re_password": "SecurePassword@123",
    }

    payload_too_long: dict[str, Any] = {
        "username": "johndoe",
        "email": "john@example.com",
        "first_name": "J" * 61,
        "last_name": "D" * 61,
        "password": "SecurePassword@123",
        "re_password": "SecurePassword@123",
    }

    # Invalid Name Formats
    serializer_invalid: UserRegisterPayloadSerializer = UserRegisterPayloadSerializer(data=payload_invalid)
    assert not serializer_invalid.is_valid()
    assert str(serializer_invalid.errors["first_name"][0]) == "First Name Must Contain Only Letters With No Spaces"
    assert str(serializer_invalid.errors["last_name"][0]) == "Last Name Must Contain Only Letters With No Spaces"

    # Name Too Long
    serializer_long: UserRegisterPayloadSerializer = UserRegisterPayloadSerializer(data=payload_too_long)
    assert not serializer_long.is_valid()
    assert str(serializer_long.errors["first_name"][0]) == "First Name Must Not Exceed 60 Characters"
    assert str(serializer_long.errors["last_name"][0]) == "Last Name Must Not Exceed 60 Characters"


# Password Rules Test
def test_user_register_payload_serializer_password_rules() -> None:
    """
    Verify Password Min Length, Max Length, And Complexity Errors.
    """

    # Inputs
    payload_too_short: dict[str, Any] = {
        "username": "johndoe",
        "email": "john@example.com",
        "first_name": "John",
        "last_name": "Doe",
        "password": "Ab1@",
        "re_password": "Ab1@",
    }

    payload_too_long: dict[str, Any] = {
        "username": "johndoe",
        "email": "john@example.com",
        "first_name": "John",
        "last_name": "Doe",
        "password": "A" * 61 + "b1@",
        "re_password": "A" * 61 + "b1@",
    }

    payload_no_complexity: dict[str, Any] = {
        "username": "johndoe",
        "email": "john@example.com",
        "first_name": "John",
        "last_name": "Doe",
        "password": "abcdefgh",  # lacks uppercase, digit, special
        "re_password": "abcdefgh",
    }

    # Too Short
    serializer_short: UserRegisterPayloadSerializer = UserRegisterPayloadSerializer(data=payload_too_short)
    assert not serializer_short.is_valid()
    assert (
        str(serializer_short.errors["password"][0])
        == "Password Must Contain At Least One Uppercase Letter, One Lowercase Letter, One Digit, and One Special Character"  # noqa: E501
    )

    # Too Long
    serializer_long: UserRegisterPayloadSerializer = UserRegisterPayloadSerializer(data=payload_too_long)
    assert not serializer_long.is_valid()
    assert str(serializer_long.errors["password"][0]) == "Password Must Not Exceed 60 Characters"

    # Lacking Complexity
    serializer_complexity: UserRegisterPayloadSerializer = UserRegisterPayloadSerializer(data=payload_no_complexity)
    assert not serializer_complexity.is_valid()
    assert (
        str(serializer_complexity.errors["password"][0])
        == "Password Must Contain At Least One Uppercase Letter, One Lowercase Letter, One Digit, and One Special Character"  # noqa: E501
    )


# Username Already Exists Test
@pytest.mark.django_db
def test_user_register_payload_serializer_username_already_exists() -> None:
    """
    Verify Username Already Exists Validation.
    """

    # Setup
    User.objects.create_user(
        username="johndoe",
        email="existing@example.com",
        first_name="Ex",
        last_name="Isting",
        password="SecurePassword@123",
        is_active=True,
    )

    # Inputs
    payload: dict[str, Any] = {
        "username": "johndoe",
        "email": "new@example.com",
        "first_name": "John",
        "last_name": "Doe",
        "password": "SecurePassword@123",
        "re_password": "SecurePassword@123",
    }

    # Create Serializer
    serializer: UserRegisterPayloadSerializer = UserRegisterPayloadSerializer(data=payload)

    # Validate
    assert not serializer.is_valid()

    # Assert Error
    assert "username" in serializer.errors
    assert str(serializer.errors["username"][0]) == "Username Already Exists"


# Email Already Exists Test
@pytest.mark.django_db
def test_user_register_payload_serializer_email_already_exists() -> None:
    """
    Verify Email Already Exists Validation.
    """

    # Setup
    User.objects.create_user(
        username="existinguser",
        email="johndoe@example.com",
        first_name="Ex",
        last_name="Isting",
        password="SecurePassword@123",
        is_active=True,
    )

    # Inputs
    payload: dict[str, Any] = {
        "username": "newuser",
        "email": "johndoe@example.com",
        "first_name": "John",
        "last_name": "Doe",
        "password": "SecurePassword@123",
        "re_password": "SecurePassword@123",
    }

    # Create Serializer
    serializer: UserRegisterPayloadSerializer = UserRegisterPayloadSerializer(data=payload)

    # Validate
    assert not serializer.is_valid()

    # Assert Error
    assert "email" in serializer.errors
    assert str(serializer.errors["email"][0]) == "Email Already Exists"


# Response Serializer Valid Test
def test_user_register_response_serializer_valid() -> None:
    """
    Verify Response Serializer Accepts Valid Nested User Details.
    """

    # Inputs
    payload: dict[str, Any] = {
        "status_code": 201,
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
            "last_login": None,
        },
    }

    # Create Serializer
    serializer: UserRegisterResponseSerializer = UserRegisterResponseSerializer(data=payload)

    # Validate
    assert serializer.is_valid(), serializer.errors

    # Assert Nested Data
    assert serializer.validated_data["status_code"] == 201
    assert serializer.validated_data["user"]["username"] == "johndoe"


# Bad Request Error Serializer Tests
def test_user_create_bad_request_error_response_defaults_and_with_errors() -> None:
    """
    Verify Bad Request Error Serializer Defaults And Validates Provided Errors.
    """

    # Inputs
    payload_default: dict[str, Any] = {
        # defaults to 400 and errors=None
    }
    payload_with_errors: dict[str, Any] = {
        "status_code": 400,
        "errors": {
            "username": ["Username Is Required"],
            "email": ["Invalid Email Address"],
            "first_name": ["First Name Must Contain Only Letters With No Spaces"],
            "last_name": ["Last Name Must Contain Only Letters With No Spaces"],
            "password": [
                "Password Must Contain At Least One Uppercase Letter, One Lowercase Letter, One Digit, and One Special Character",  # noqa: E501
            ],
            "re_password": ["Password Confirmation Is Required"],
            "non_field_errors": ["General Error"],
        },
    }

    # Create Serializers
    serializer_default: UserCreateBadRequestErrorResponseSerializer = UserCreateBadRequestErrorResponseSerializer(
        data=payload_default,
    )
    serializer_with_errors: UserCreateBadRequestErrorResponseSerializer = UserCreateBadRequestErrorResponseSerializer(
        data=payload_with_errors,
    )

    # Validate
    assert serializer_default.is_valid(), serializer_default.errors
    assert serializer_with_errors.is_valid(), serializer_with_errors.errors

    # Assert Defaults
    assert serializer_default.validated_data["status_code"] == 400
    assert serializer_default.validated_data["errors"] is None

    # Assert Provided Errors
    assert serializer_with_errors.validated_data["errors"]["username"] == ["Username Is Required"]


# Create Method Test
def test_user_register_payload_serializer_create_persists_user_with_flags() -> None:
    """
    Verify Create() Persists User And Sets Flags To False.
    """

    # Inputs
    payload: dict[str, Any] = {
        "username": "newperson",
        "email": "newperson@example.com",
        "first_name": "New",
        "last_name": "Person",
        "password": "SecurePassword@123",
        "re_password": "SecurePassword@123",
    }

    # Create Serializer
    serializer: UserRegisterPayloadSerializer = UserRegisterPayloadSerializer(data=payload)

    # Validate
    assert serializer.is_valid(), serializer.errors

    # Save User
    user = serializer.save()

    # Assert User Fields And Flags
    assert user.username == payload["username"]
    assert user.email == payload["email"]
    assert user.first_name == payload["first_name"]
    assert user.last_name == payload["last_name"]
    assert user.is_active is False
    assert user.is_staff is False
    assert user.is_superuser is False
