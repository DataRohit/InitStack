# Third Party Imports
from django.utils.translation import gettext_lazy as _
from drf_spectacular.utils import OpenApiExample
from drf_spectacular.utils import extend_schema_serializer
from rest_framework import serializers
from rest_framework import status

# Local Imports
from apps.common.serializers.generic_response_serializer import GenericResponseSerializer


# OAuthCallbackBadRequestErrorResponseSerialzier
@extend_schema_serializer(
    examples=[
        OpenApiExample(
            name="Authentication Failed Error Response Example",
            value={
                "status_code": status.HTTP_400_BAD_REQUEST,
                "error": "Authentication Failed",
            },
            summary="Authentication Failed Error Response Example",
            description="Authentication Failed Error Response Example",
            response_only=True,
            status_codes=[status.HTTP_400_BAD_REQUEST],
        ),
        OpenApiExample(
            name="User Not Found Error Response Example",
            value={
                "status_code": status.HTTP_400_BAD_REQUEST,
                "error": "User Not Found",
            },
            summary="User Not Found Error Response Example",
            description="User Not Found Error Response Example",
            response_only=True,
            status_codes=[status.HTTP_400_BAD_REQUEST],
        ),
    ],
)
class OAuthCallbackBadRequestErrorResponseSerialzier(GenericResponseSerializer):
    """
    OAuth Callback Bad Request Error Response Serializer For Standardized API Responses.

    Attributes:
        status_code (int): HTTP Status Code For The Response.
        error (str): Error Message For The Response.
    """

    # Error Field
    error: serializers.CharField = serializers.CharField(
        help_text=_("Error Message"),
        label=_("Error"),
        required=True,
        allow_null=False,
        error_messages={
            "required": _("Error Message Is Required"),
            "null": _("Error Message Cannot Be Null"),
        },
    )


# OAuth Callback Response Serializer Class
@extend_schema_serializer(
    examples=[
        OpenApiExample(
            name="OAuth Callback Response Example",
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
            summary="OAuth Callback Response Example",
            description="OAuth Callback Response Example",
            response_only=True,
            status_codes=[status.HTTP_200_OK],
        ),
    ],
)
class OAuthCallbackResponseSerializer(GenericResponseSerializer):
    """
    OAuth Callback Response Serializer For Standardized API Responses.

    Attributes:
        status_code (int): HTTP Status Code For The Response.
        user (OAuthCallbackUserDetailSerializer): User Details For The Response.
    """

    # User Detail Serializer
    class OAuthCallbackUserDetailSerializer(serializers.Serializer):
        """
        OAuth Callback User Detail Serializer Including Access And Refresh Tokens.

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
    user: OAuthCallbackUserDetailSerializer = OAuthCallbackUserDetailSerializer(
        help_text=_("User Details"),
        label=_("User Details"),
        required=True,
        allow_null=False,
        error_messages={
            "required": _("User Details Is Required"),
            "null": _("User Details Cannot Be Null"),
        },
    )


# OAuth Callback Unauthorized Error Response Serializer Class
@extend_schema_serializer(
    examples=[
        OpenApiExample(
            name="OAuth Unauthorized Error Response Example",
            value={
                "status_code": status.HTTP_401_UNAUTHORIZED,
                "error": "Unauthorized",
            },
            summary="OAuth Unauthorized Error Response Example",
            description="OAuth Unauthorized Error Response Example",
            response_only=True,
            status_codes=[status.HTTP_401_UNAUTHORIZED],
        ),
    ],
)
class OAuthCallbackUnauthorizedErrorResponseSerializer(GenericResponseSerializer):
    """
    OAuth Callback Unauthorized Error Response Serializer For Standardized API Responses.

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
    "OAuthCallbackBadRequestErrorResponseSerialzier",
    "OAuthCallbackResponseSerializer",
    "OAuthCallbackUnauthorizedErrorResponseSerializer",
]
