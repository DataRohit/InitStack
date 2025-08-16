# Standard Library Imports
from typing import Any
from typing import ClassVar

# Third Party Imports
from django.contrib.auth import get_user_model
from django.core.validators import EmailValidator
from django.core.validators import MaxLengthValidator
from django.core.validators import MinLengthValidator
from django.core.validators import RegexValidator
from django.utils.translation import gettext_lazy as _
from drf_spectacular.utils import OpenApiExample
from drf_spectacular.utils import extend_schema_serializer
from rest_framework import serializers
from rest_framework import status

# Local Imports
from apps.common.serializers.generic_response_serializer import GenericResponseSerializer
from apps.users.serializers.base_serializer import UserDetailSerializer

# Get User Model
User = get_user_model()


# User Register Payload Serializer Class
@extend_schema_serializer(
    examples=[
        OpenApiExample(
            name="User Register Payload Example",
            value={
                "username": "johndoe",
                "email": "johndoe@example.com",
                "first_name": "John",
                "last_name": "Doe",
                "password": "SecurePassword@123",
                "re_password": "SecurePassword@123",
            },
            summary="User Register Payload Example",
            description="User Register Payload Example",
            request_only=True,
            status_codes=[status.HTTP_201_CREATED],
        ),
    ],
)
class UserRegisterPayloadSerializer(serializers.ModelSerializer):
    """
    User Registration Payload Serializer For Creating New User Accounts.

    Attributes:
        re_password (serializers.CharField): Password Confirmation Field.

    Methods:
        validate(attrs: dict[str, Any]) -> dict[str, Any]: Validate Password Match.
        create(validated_data: dict[str, Any]) -> User: Create New User Account.
    """

    # Username Field
    username: serializers.CharField = serializers.CharField(
        help_text=_("Enter A Valid Username"),
        label=_("Username"),
        required=True,
        allow_null=False,
        validators=[
            RegexValidator(
                regex=r"^[A-Za-z0-9]+$",
                message=_("Username Must Contain Only Alphanumeric Characters With No Spaces"),
                code="invalid_username",
            ),
            MaxLengthValidator(
                limit_value=60,
                message=_("Username Must Not Exceed 60 Characters"),
            ),
        ],
        error_messages={
            "required": _("Username Is Required"),
            "null": _("Username Cannot Be Null"),
            "invalid_username": _("Username Must Contain Only Alphanumeric Characters With No Spaces"),
            "max_length": _("Username Must Not Exceed 60 Characters"),
        },
    )

    # Email Field
    email: serializers.CharField = serializers.CharField(
        help_text=_("Enter A Valid Email Address"),
        label=_("Email"),
        required=True,
        allow_null=False,
        validators=[
            EmailValidator(
                message=_("Invalid Email Address"),
                code="invalid_email",
            ),
        ],
        error_messages={
            "required": _("Email Is Required"),
            "null": _("Email Cannot Be Null"),
            "invalid_email": _("Invalid Email Address"),
        },
    )

    # First Name Field
    first_name: serializers.CharField = serializers.CharField(
        help_text=_("Enter A Valid First Name"),
        label=_("First Name"),
        required=True,
        allow_null=False,
        validators=[
            RegexValidator(
                regex=r"^[A-Za-z]+$",
                message=_("First Name Must Contain Only Letters With No Spaces"),
                code="invalid_first_name",
            ),
            MaxLengthValidator(
                limit_value=60,
                message=_("First Name Must Not Exceed 60 Characters"),
            ),
        ],
        error_messages={
            "required": _("First Name Is Required"),
            "null": _("First Name Cannot Be Null"),
            "invalid_first_name": _("First Name Must Contain Only Letters With No Spaces"),
            "max_length": _("First Name Must Not Exceed 60 Characters"),
        },
    )

    # Last Name Field
    last_name: serializers.CharField = serializers.CharField(
        help_text=_("Enter A Valid Last Name"),
        label=_("Last Name"),
        required=True,
        allow_null=False,
        validators=[
            RegexValidator(
                regex=r"^[A-Za-z]+$",
                message=_("Last Name Must Contain Only Letters With No Spaces"),
                code="invalid_last_name",
            ),
            MaxLengthValidator(
                limit_value=60,
                message=_("Last Name Must Not Exceed 60 Characters"),
            ),
        ],
        error_messages={
            "required": _("Last Name Is Required"),
            "null": _("Last Name Cannot Be Null"),
            "invalid_last_name": _("Last Name Must Contain Only Letters With No Spaces"),
            "max_length": _("Last Name Must Not Exceed 60 Characters"),
        },
    )

    # Password Field
    password: serializers.CharField = serializers.CharField(
        style={"input_type": "password"},
        write_only=True,
        help_text=_("Enter A Valid Password"),
        label=_("Password"),
        required=True,
        allow_null=False,
        validators=[
            RegexValidator(
                regex=r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$",
                message=_(
                    "Password Must Contain At Least One Uppercase Letter, One Lowercase Letter, One Digit, and One Special Character",  # noqa: E501
                ),
                code="invalid_password",
            ),
            MinLengthValidator(
                limit_value=8,
                message=_("Password Must Contain At Least 8 Characters"),
            ),
            MaxLengthValidator(
                limit_value=60,
                message=_("Password Must Not Exceed 60 Characters"),
            ),
        ],
        error_messages={
            "required": _("Password Is Required"),
            "null": _("Password Cannot Be Null"),
            "min_length": _("Password Must Contain At Least 8 Characters"),
            "max_length": _("Password Must Not Exceed 60 Characters"),
            "invalid_password": _(
                "Password Must Contain At Least One Uppercase Letter, One Lowercase Letter, One Digit, and One Special Character",  # noqa: E501
            ),
        },
    )

    # Password Confirmation Field
    re_password: serializers.CharField = serializers.CharField(
        style={"input_type": "password"},
        write_only=True,
        help_text=_("Confirm Password"),
        label=_("Password Confirmation"),
        required=True,
        allow_null=False,
        error_messages={
            "required": _("Password Confirmation Is Required"),
            "null": _("Password Confirmation Cannot Be Null"),
        },
    )

    # Meta Class
    class Meta:
        """
        Meta Class For UserRegisterSerializer.

        Attributes:
            model (ClassVar[type]): User Model Class.
            fields (ClassVar[list[str]]): Fields To Include In Serializer.
            extra_kwargs (ClassVar[dict[str, dict[str, Any]]]): Additional Field Options.
        """

        # Model
        model: ClassVar[type] = User

        # Fields
        fields: ClassVar[list[str]] = [
            "username",
            "email",
            "first_name",
            "last_name",
            "password",
            "re_password",
        ]

    # Validate Method
    def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:
        """
        Validate Password Match Between Password And Confirmation.

        Args:
            attrs (dict[str, Any]): Dictionary Of Field Values.

        Returns:
            dict[str, Any]: Validated Data Dictionary.

        Raises:
            serializers.ValidationError: If Passwords Do Not Match.
        """

        # Check If Username Already Exists
        if User.objects.filter(username=attrs["username"]).exists():
            # Raise Validation Error
            raise serializers.ValidationError(
                {"username": _("Username Already Exists")},
                code=status.HTTP_400_BAD_REQUEST,
            ) from None

        # Check If Email Already Exists
        if User.objects.filter(email=attrs["email"]).exists():
            # Raise Validation Error
            raise serializers.ValidationError(
                {"email": _("Email Already Exists")},
                code=status.HTTP_400_BAD_REQUEST,
            ) from None

        # Check Password Match
        if attrs["password"] != attrs["re_password"]:
            # Raise Validation Error
            raise serializers.ValidationError(
                {"password": _("Passwords Do Not Match")},
                code=status.HTTP_400_BAD_REQUEST,
            ) from None

        # Return Validated Data
        return attrs

    # Create Method
    def create(self, validated_data: dict[str, Any]) -> User:
        """
        Create New User Account With Validated Data.

        Args:
            validated_data (dict[str, Any]): Validated Form Data.

        Returns:
            User: Newly Created User Instance.
        """

        # Remove Confirmation Password
        validated_data.pop("re_password")

        # Create User Account
        return User.objects.create_user(**validated_data, is_active=False, is_staff=False, is_superuser=False)


# User Regsiter Response Serializer Class
@extend_schema_serializer(
    examples=[
        OpenApiExample(
            name="User Register Response Example",
            value={
                "status_code": 201,
                "user": {
                    "id": "123e4567-e89b-12d3-a456-426614174000",
                    "username": "johndoe",
                    "email": "johndoe@example.com",
                    "first_name": "John",
                    "last_name": "Doe",
                    "is_active": False,
                    "is_staff": False,
                    "is_superuser": False,
                    "date_joined": "2025-08-16T19:04:06.602446+05:30",
                    "last_login": None,
                },
            },
            summary="User Register Response Example",
            description="User Register Response Example",
            response_only=True,
            status_codes=[status.HTTP_201_CREATED],
        ),
    ],
)
class UserRegisterResponseSerializer(GenericResponseSerializer):
    """
    User Registration Response Serializer For Standardized API Responses.

    Attributes:
        status_code (int): HTTP Status Code For The Response.
        user (UserDetailSerializer): User Details For The Response.
    """

    # User Field
    user: UserDetailSerializer = UserDetailSerializer(
        help_text=_("User Details"),
        label=_("User Details"),
        required=True,
        allow_null=False,
        error_messages={
            "required": _("User Details Is Required"),
            "null": _("User Details Cannot Be Null"),
        },
    )


# User Registration Error Response Serializer Class
@extend_schema_serializer(
    examples=[
        OpenApiExample(
            name="Missing Required Fields",
            value={
                "status_code": status.HTTP_400_BAD_REQUEST,
                "errors": {
                    "username": ["Username Is Required"],
                    "email": ["Email Is Required"],
                    "first_name": ["First Name Is Required"],
                    "last_name": ["Last Name Is Required"],
                    "password": ["Password Is Required"],
                    "re_password": ["Password Confirmation Is Required"],
                },
            },
            summary="Missing Required Fields",
            description="Error Response When Required Fields Are Missing",
            response_only=True,
            status_codes=[status.HTTP_400_BAD_REQUEST],
        ),
        OpenApiExample(
            name="Null Field Values",
            value={
                "status_code": status.HTTP_400_BAD_REQUEST,
                "errors": {
                    "username": ["Username Cannot Be Null"],
                    "email": ["Email Cannot Be Null"],
                    "first_name": ["First Name Cannot Be Null"],
                    "last_name": ["Last Name Cannot Be Null"],
                    "password": ["Password Cannot Be Null"],
                    "re_password": ["Password Confirmation Cannot Be Null"],
                },
            },
            summary="Null Field Values",
            description="Error Response When Fields Are Provided As Null",
            response_only=True,
            status_codes=[status.HTTP_400_BAD_REQUEST],
        ),
        OpenApiExample(
            name="Invalid Username Format",
            value={
                "status_code": status.HTTP_400_BAD_REQUEST,
                "errors": {
                    "username": [
                        "Username Must Contain Only Alphanumeric Characters With No Spaces",
                    ],
                },
            },
            summary="Invalid Username Format",
            description="Error Response When Username Format Is Invalid",
            response_only=True,
            status_codes=[status.HTTP_400_BAD_REQUEST],
        ),
        OpenApiExample(
            name="Username Max Length Exceeded",
            value={
                "status_code": status.HTTP_400_BAD_REQUEST,
                "errors": {
                    "username": ["Username Must Not Exceed 60 Characters"],
                },
            },
            summary="Username Max Length Exceeded",
            description="Error Response When Username Exceeds Maximum Length",
            response_only=True,
            status_codes=[status.HTTP_400_BAD_REQUEST],
        ),
        OpenApiExample(
            name="Username Already Exists",
            value={
                "status_code": status.HTTP_400_BAD_REQUEST,
                "errors": {
                    "username": ["Username Already Exists"],
                },
            },
            summary="Username Already Exists",
            description="Error Response When Username Already Exists",
            response_only=True,
            status_codes=[status.HTTP_400_BAD_REQUEST],
        ),
        OpenApiExample(
            name="Invalid Email Format",
            value={
                "status_code": status.HTTP_400_BAD_REQUEST,
                "errors": {
                    "email": ["Invalid Email Address"],
                },
            },
            summary="Invalid Email Format",
            description="Error Response When Email Format Is Invalid",
            response_only=True,
            status_codes=[status.HTTP_400_BAD_REQUEST],
        ),
        OpenApiExample(
            name="Email Already Exists",
            value={
                "status_code": status.HTTP_400_BAD_REQUEST,
                "errors": {
                    "email": ["Email Already Exists"],
                },
            },
            summary="Email Already Exists",
            description="Error Response When Email Already Exists",
            response_only=True,
            status_codes=[status.HTTP_400_BAD_REQUEST],
        ),
        OpenApiExample(
            name="Invalid Name Format",
            value={
                "status_code": status.HTTP_400_BAD_REQUEST,
                "errors": {
                    "first_name": ["First Name Must Contain Only Letters With No Spaces"],
                    "last_name": ["Last Name Must Contain Only Letters With No Spaces"],
                },
            },
            summary="Invalid Name Format",
            description="Error Response When Name Format Is Invalid",
            response_only=True,
            status_codes=[status.HTTP_400_BAD_REQUEST],
        ),
        OpenApiExample(
            name="Name Fields Max Length Exceeded",
            value={
                "status_code": status.HTTP_400_BAD_REQUEST,
                "errors": {
                    "first_name": ["First Name Must Not Exceed 60 Characters"],
                    "last_name": ["Last Name Must Not Exceed 60 Characters"],
                },
            },
            summary="Name Fields Max Length Exceeded",
            description="Error Response When Name Fields Exceed Maximum Length",
            response_only=True,
            status_codes=[status.HTTP_400_BAD_REQUEST],
        ),
        OpenApiExample(
            name="Password Min Length Error",
            value={
                "status_code": status.HTTP_400_BAD_REQUEST,
                "errors": {
                    "password": ["Password Must Contain At Least 8 Characters"],
                },
            },
            summary="Password Min Length Error",
            description="Error Response When Password Is Too Short",
            response_only=True,
            status_codes=[status.HTTP_400_BAD_REQUEST],
        ),
        OpenApiExample(
            name="Password Max Length Exceeded",
            value={
                "status_code": status.HTTP_400_BAD_REQUEST,
                "errors": {
                    "password": ["Password Must Not Exceed 60 Characters"],
                },
            },
            summary="Password Max Length Exceeded",
            description="Error Response When Password Exceeds Maximum Length",
            response_only=True,
            status_codes=[status.HTTP_400_BAD_REQUEST],
        ),
        OpenApiExample(
            name="Password Complexity Error",
            value={
                "status_code": status.HTTP_400_BAD_REQUEST,
                "errors": {
                    "password": [
                        "Password Must Contain At Least One Uppercase Letter, One Lowercase Letter, One Digit, and One Special Character",  # noqa: E501
                    ],
                },
            },
            summary="Password Complexity Error",
            description="Error Response When Password Doesn't Meet Complexity Requirements",
            response_only=True,
            status_codes=[status.HTTP_400_BAD_REQUEST],
        ),
        OpenApiExample(
            name="Multiple Password Validation Errors",
            value={
                "status_code": status.HTTP_400_BAD_REQUEST,
                "errors": {
                    "password": [
                        "Password Must Contain At Least 8 Characters",
                        "Password Must Contain At Least One Uppercase Letter, One Lowercase Letter, One Digit, and One Special Character",  # noqa: E501
                    ],
                },
            },
            summary="Multiple Password Validation Errors",
            description="Error Response When Password Has Multiple Validation Errors",
            response_only=True,
            status_codes=[status.HTTP_400_BAD_REQUEST],
        ),
        OpenApiExample(
            name="Password Mismatch",
            value={
                "status_code": status.HTTP_400_BAD_REQUEST,
                "errors": {
                    "password": ["Passwords Do Not Match"],
                },
            },
            summary="Password Mismatch",
            description="Error Response When Password And Confirmation Don't Match",
            response_only=True,
            status_codes=[status.HTTP_400_BAD_REQUEST],
        ),
        OpenApiExample(
            name="Username Already Exists",
            value={
                "status_code": status.HTTP_400_BAD_REQUEST,
                "errors": {
                    "username": ["Username Already Exists"],
                },
            },
            summary="Username Already Exists",
            description="Error Response When Username Is Already Taken",
            response_only=True,
            status_codes=[status.HTTP_400_BAD_REQUEST],
        ),
        OpenApiExample(
            name="Email Already Exists",
            value={
                "status_code": status.HTTP_400_BAD_REQUEST,
                "errors": {
                    "email": ["Email Already Exists"],
                },
            },
            summary="Email Already Exists",
            description="Error Response When Email Is Already Registered",
            response_only=True,
            status_codes=[status.HTTP_400_BAD_REQUEST],
        ),
        OpenApiExample(
            name="Multiple Field Validation Errors",
            value={
                "status_code": status.HTTP_400_BAD_REQUEST,
                "errors": {
                    "username": ["Username Must Contain Only Alphanumeric Characters With No Spaces"],
                    "email": ["Invalid Email Address"],
                    "first_name": ["First Name Must Contain Only Letters With No Spaces"],
                    "last_name": ["Last Name Must Contain Only Letters With No Spaces"],
                    "password": [
                        "Password Must Contain At Least One Uppercase Letter, One Lowercase Letter, One Digit, and One Special Character",  # noqa: E501
                    ],
                },
            },
            summary="Multiple Field Validation Errors",
            description="Error Response When Multiple Fields Have Validation Errors",
            response_only=True,
            status_codes=[status.HTTP_400_BAD_REQUEST],
        ),
    ],
)
class UserCreateErrorResponseSerializer(GenericResponseSerializer):
    """
    User Registration Error Response Serializer For Standardized API Responses.

    Attributes:
        status_code (int): HTTP Status Code For The Response.
        errors (UserCreateErrorsDetailSerializer): Error Details For The Response.
    """

    # Error Detail Serializer
    class UserCreateErrorsDetailSerializer(serializers.Serializer):
        """
        User Registration Error Detail Serializer For Standardized API Responses.

        Attributes:
            username (list[str]): List Of Errors Related To The Username Field.
            email (list[str]): List Of Errors Related To The Email Field.
            first_name (list[str]): List Of Errors Related To The First Name Field.
            last_name (list[str]): List Of Errors Related To The Last Name Field.
            password (list[str]): List Of Errors Related To The Password Field.
            re_password (list[str]): List Of Errors Related To The Password Confirmation Field.
            non_field_errors (list[str]): List Of Non-Field Specific Errors.
        """

        # Username Field
        username: serializers.ListField = serializers.ListField(
            help_text=_("Errors Related To The Username Field"),
            label=_("Username Errors"),
            required=False,
            allow_null=True,
            child=serializers.CharField(),
        )

        # Email Field
        email: serializers.ListField = serializers.ListField(
            help_text=_("Errors Related To The Email Field"),
            label=_("Email Errors"),
            required=False,
            allow_null=True,
            child=serializers.CharField(),
        )

        # First Name Field
        first_name: serializers.ListField = serializers.ListField(
            help_text=_("Errors Related To The First Name Field"),
            label=_("First Name Errors"),
            required=False,
            allow_null=True,
            child=serializers.CharField(),
        )

        # Last Name Field
        last_name: serializers.ListField = serializers.ListField(
            help_text=_("Errors Related To The Last Name Field"),
            label=_("Last Name Errors"),
            required=False,
            allow_null=True,
            child=serializers.CharField(),
        )

        # Password Field
        password: serializers.ListField = serializers.ListField(
            help_text=_("Errors Related To The Password Field"),
            label=_("Password Errors"),
            required=False,
            allow_null=True,
            child=serializers.CharField(),
        )

        # Re-Password Field
        re_password: serializers.ListField = serializers.ListField(
            help_text=_("Errors Related To The Password Confirmation Field"),
            label=_("Password Confirmation Errors"),
            required=False,
            allow_null=True,
            child=serializers.CharField(),
        )

        # Non-Field Errors Field
        non_field_errors: serializers.ListField = serializers.ListField(
            help_text=_("Non-Field Specific Errors"),
            label=_("Non-Field Errors"),
            required=False,
            allow_null=True,
            child=serializers.CharField(),
        )

    # Status Code Field
    status_code: serializers.IntegerField = serializers.IntegerField(
        help_text=_("HTTP Status Code Indicating A Bad Request"),
        label=_("Status Code"),
        default=status.HTTP_400_BAD_REQUEST,
    )

    # Errors Field
    errors: UserCreateErrorsDetailSerializer = UserCreateErrorsDetailSerializer(
        help_text=_("Object Containing Validation Errors"),
        label=_("Errors"),
        required=False,
        allow_null=True,
        default=None,
    )


# Exports
__all__: list[str] = [
    "UserCreateErrorResponseSerializer",
    "UserRegisterPayloadSerializer",
    "UserRegisterResponseSerializer",
]
