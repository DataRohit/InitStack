# Third Party Imports
from django.utils.translation import gettext_lazy as _
from drf_spectacular.utils import OpenApiExample
from drf_spectacular.utils import extend_schema_serializer
from rest_framework import serializers
from rest_framework import status

# Local Imports
from apps.common.serializers.generic_response_serializer import GenericResponseSerializer


# User Login Payload Serializer Class
@extend_schema_serializer(
    examples=[
        OpenApiExample(
            name="User Login Payload Example (Username)",
            value={
                "identifier": "johndoe",
                "password": "SecurePassword@123",
            },
            summary="User Login Payload Example (Username)",
            description="User Login Request Payload Example (Username)",
            request_only=True,
            status_codes=[status.HTTP_200_OK],
        ),
        OpenApiExample(
            name="User Login Payload Example (Email)",
            value={
                "identifier": "johndoe@example.com",
                "password": "SecurePassword@123",
            },
            summary="User Login Payload Example (Email)",
            description="User Login Request Payload Example (Email)",
            request_only=True,
            status_codes=[status.HTTP_200_OK],
        ),
    ],
)
class UserLoginPayloadSerializer(serializers.Serializer):
    """
    User Login Payload Serializer For Authenticating Users.

    Attributes:
        identifier (serializers.CharField): Username Or Email Identifier.
        password (serializers.CharField): User Password (Write Only).
    """

    # Identifier Field
    identifier: serializers.CharField = serializers.CharField(
        help_text=_("Enter Username Or Email"),
        label=_("Identifier"),
        required=True,
        allow_null=False,
        error_messages={
            "required": _("Identifier Is Required"),
            "null": _("Identifier Cannot Be Null"),
            "blank": _("Identifier Cannot Be Blank"),
        },
    )

    # Password Field
    password: serializers.CharField = serializers.CharField(
        style={"input_type": "password"},
        write_only=True,
        help_text=_("Enter Password"),
        label=_("Password"),
        required=True,
        allow_null=False,
        error_messages={
            "required": _("Password Is Required"),
            "null": _("Password Cannot Be Null"),
            "blank": _("Password Cannot Be Blank"),
        },
    )


# User Login Bad Request Error Response Serializer Class
@extend_schema_serializer(
    examples=[
        OpenApiExample(
            name="Missing Required Fields",
            value={
                "status_code": status.HTTP_400_BAD_REQUEST,
                "errors": {
                    "identifier": ["Identifier Is Required"],
                    "password": ["Password Is Required"],
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
                    "identifier": ["Identifier Cannot Be Null"],
                    "password": ["Password Cannot Be Null"],
                },
            },
            summary="Null Field Values",
            description="Error Response When Fields Are Provided As Null",
            response_only=True,
            status_codes=[status.HTTP_400_BAD_REQUEST],
        ),
        OpenApiExample(
            name="Blank Field Values",
            value={
                "status_code": status.HTTP_400_BAD_REQUEST,
                "errors": {
                    "identifier": ["Identifier Cannot Be Blank"],
                    "password": ["Password Cannot Be Blank"],
                },
            },
            summary="Blank Field Values",
            description="Error Response When Fields Are Provided As Blank",
            response_only=True,
            status_codes=[status.HTTP_400_BAD_REQUEST],
        ),
    ],
)
class UserLoginBadRequestErrorResponseSerializer(GenericResponseSerializer):
    """
    User Login Bad Request Error Response Serializer For Standardized API Responses.

    Attributes:
        status_code (int): HTTP Status Code For The Response.
        errors (UserLoginErrorsDetailSerializer): Error Details For The Response.
    """

    # Status Code Field
    status_code: serializers.IntegerField = serializers.IntegerField(
        help_text=_("HTTP Status Code Indicating A Bad Request"),
        label=_("Status Code"),
        default=status.HTTP_400_BAD_REQUEST,
    )

    # Error Detail Serializer
    class UserLoginErrorsDetailSerializer(serializers.Serializer):
        """
        User Login Error Detail Serializer For Standardized API Responses.

        Attributes:
            identifier (list[str]): List Of Errors Related To The Identifier Field.
            password (list[str]): List Of Errors Related To The Password Field.
            non_field_errors (list[str]): List Of Non-Field Specific Errors.
        """

        # Identifier Field
        identifier: serializers.ListField = serializers.ListField(
            help_text=_("Errors Related To The Identifier Field"),
            label=_("Identifier Errors"),
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

        # Non-Field Errors Field
        non_field_errors: serializers.ListField = serializers.ListField(
            help_text=_("Non-Field Specific Errors"),
            label=_("Non-Field Errors"),
            required=False,
            allow_null=True,
            child=serializers.CharField(),
        )

    # Errors Field
    errors: UserLoginErrorsDetailSerializer = UserLoginErrorsDetailSerializer(
        help_text=_("Object Containing Validation Errors"),
        label=_("Errors"),
        required=False,
        allow_null=True,
        default=None,
    )


# User Login Response Serializer Class
@extend_schema_serializer(
    examples=[
        OpenApiExample(
            name="User Login Response Example",
            value={
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
                    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                    "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                },
            },
            summary="User Login Response Example",
            description="User Login Response Example",
            response_only=True,
            status_codes=[status.HTTP_200_OK],
        ),
    ],
)
class UserLoginResponseSerializer(GenericResponseSerializer):
    """
    User Login Response Serializer For Standardized API Responses.

    Attributes:
        status_code (int): HTTP Status Code For The Response.
        user (UserLoginUserDetailSerializer): User Details For The Response.
    """

    # User Detail Serializer
    class UserLoginUserDetailSerializer(serializers.Serializer):
        """
        User Login User Detail Serializer Including Access And Refresh Tokens.

        Attributes:
            id (serializers.UUIDField): User ID Field.
            username (serializers.CharField): User Username Field.
            email (serializers.EmailField): User Email Field.
            first_name (serializers.CharField): User First Name Field.
            last_name (serializers.CharField): User Last Name Field.
            is_active (serializers.BooleanField): User Active Status Field.
            is_staff (serializers.BooleanField): User Staff Status Field.
            is_superuser (serializers.BooleanField): User Superuser Status Field.
            date_joined (serializers.DateTimeField): User Date Joined Field.
            last_login (serializers.DateTimeField): User Last Login Field.
            access_token (serializers.CharField): JWT Access Token Field.
            refresh_token (serializers.CharField): JWT Refresh Token Field.
        """

        # ID Field
        id: serializers.UUIDField = serializers.UUIDField(
            help_text=_("User ID"),
            label=_("User ID"),
            required=True,
            allow_null=False,
            error_messages={
                "required": _("User ID Is Required"),
                "null": _("User ID Cannot Be Null"),
            },
        )

        # Username Field
        username: serializers.CharField = serializers.CharField(
            help_text=_("User Username"),
            label=_("Username"),
            required=True,
            allow_null=False,
            error_messages={
                "required": _("User Username Is Required"),
                "null": _("User Username Cannot Be Null"),
            },
        )

        # Email Field
        email: serializers.EmailField = serializers.EmailField(
            help_text=_("User Email"),
            label=_("Email"),
            required=True,
            allow_null=False,
            error_messages={
                "required": _("User Email Is Required"),
                "null": _("User Email Cannot Be Null"),
            },
        )

        # First Name Field
        first_name: serializers.CharField = serializers.CharField(
            help_text=_("User First Name"),
            label=_("First Name"),
            required=True,
            allow_null=False,
            error_messages={
                "required": _("User First Name Is Required"),
                "null": _("User First Name Cannot Be Null"),
            },
        )

        # Last Name Field
        last_name: serializers.CharField = serializers.CharField(
            help_text=_("User Last Name"),
            label=_("Last Name"),
            required=True,
            allow_null=False,
            error_messages={
                "required": _("User Last Name Is Required"),
                "null": _("User Last Name Cannot Be Null"),
            },
        )

        # Is Active Field
        is_active: serializers.BooleanField = serializers.BooleanField(
            help_text=_("User Active Status"),
            label=_("Active"),
            required=True,
            allow_null=False,
            error_messages={
                "required": _("User Active Status Is Required"),
                "null": _("User Active Status Cannot Be Null"),
            },
        )

        # Is Staff Field
        is_staff: serializers.BooleanField = serializers.BooleanField(
            help_text=_("User Staff Status"),
            label=_("Staff"),
            required=True,
            allow_null=False,
            error_messages={
                "required": _("User Staff Status Is Required"),
                "null": _("User Staff Status Cannot Be Null"),
            },
        )

        # Is Superuser Field
        is_superuser: serializers.BooleanField = serializers.BooleanField(
            help_text=_("User Superuser Status"),
            label=_("Superuser"),
            required=True,
            allow_null=False,
            error_messages={
                "required": _("User Superuser Status Is Required"),
                "null": _("User Superuser Status Cannot Be Null"),
            },
        )

        # Date Joined Field
        date_joined: serializers.DateTimeField = serializers.DateTimeField(
            help_text=_("User Date Joined"),
            label=_("Date Joined"),
            required=True,
            allow_null=False,
            error_messages={
                "required": _("User Date Joined Is Required"),
                "null": _("User Date Joined Cannot Be Null"),
            },
        )

        # Last Login Field
        last_login: serializers.DateTimeField = serializers.DateTimeField(
            help_text=_("User Last Login"),
            label=_("Last Login"),
            required=False,
            allow_null=True,
        )

        # Access Token Field
        access_token: serializers.CharField = serializers.CharField(
            help_text=_("JWT Access Token"),
            label=_("Access Token"),
            required=True,
            allow_null=False,
            error_messages={
                "required": _("Access Token Is Required"),
                "null": _("Access Token Cannot Be Null"),
            },
        )

        # Refresh Token Field
        refresh_token: serializers.CharField = serializers.CharField(
            help_text=_("JWT Refresh Token"),
            label=_("Refresh Token"),
            required=True,
            allow_null=False,
            error_messages={
                "required": _("Refresh Token Is Required"),
                "null": _("Refresh Token Cannot Be Null"),
            },
        )

    # User Field
    user: UserLoginUserDetailSerializer = UserLoginUserDetailSerializer(
        help_text=_("User Details"),
        label=_("User Details"),
        required=True,
        allow_null=False,
        error_messages={
            "required": _("User Details Is Required"),
            "null": _("User Details Cannot Be Null"),
        },
    )


# User Login Unauthorized Error Response Serializer Class
@extend_schema_serializer(
    examples=[
        OpenApiExample(
            name="Invalid Username Or Password",
            value={
                "status_code": status.HTTP_401_UNAUTHORIZED,
                "error": "Invalid Username Or Password",
            },
            summary="Invalid Username Or Password",
            description="Invalid Username Or Password Error Response",
            response_only=True,
            status_codes=[status.HTTP_401_UNAUTHORIZED],
        ),
        OpenApiExample(
            name="User Is Not Active",
            value={
                "status_code": status.HTTP_401_UNAUTHORIZED,
                "error": "User Is Not Active",
            },
            summary="User Is Not Active",
            description="User Is Not Active Error Response",
            response_only=True,
            status_codes=[status.HTTP_401_UNAUTHORIZED],
        ),
    ],
)
class UserLoginUnauthorizedErrorResponseSerializer(GenericResponseSerializer):
    """
    User Login Unauthorized Error Response Serializer For Standardized API Responses.

    Attributes:
        status_code (int): HTTP Status Code For The Response.
        error (str): Error Message For The Response.
    """

    # Error Field
    error: serializers.CharField = serializers.CharField(
        help_text=_("Error Message For The Response"),
        label=_("Error Message"),
        default="Unauthorized",
    )


# Exports
__all__: list[str] = [
    "UserLoginBadRequestErrorResponseSerializer",
    "UserLoginPayloadSerializer",
    "UserLoginResponseSerializer",
    "UserLoginUnauthorizedErrorResponseSerializer",
]
