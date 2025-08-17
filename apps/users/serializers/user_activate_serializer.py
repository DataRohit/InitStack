# Third Party Imports
from django.utils.translation import gettext_lazy as _
from drf_spectacular.utils import OpenApiExample
from drf_spectacular.utils import extend_schema_serializer
from rest_framework import serializers
from rest_framework import status

# Local Imports
from apps.common.serializers.generic_response_serializer import GenericResponseSerializer
from apps.users.serializers.base_serializer import UserDetailSerializer


# User Activate Response Serializer Class
@extend_schema_serializer(
    examples=[
        OpenApiExample(
            name="User Activate Response Example",
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
                    "last_login": None,
                },
            },
            summary="User Activate Response Example",
            description="User Activate Response Example",
            response_only=True,
            status_codes=[status.HTTP_200_OK],
        ),
    ],
)
class UserActivateResponseSerializer(GenericResponseSerializer):
    """
    User Activation Response Serializer For Standardized API Responses.

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


# User Activate Unauthorized Error Response Serializer Class
@extend_schema_serializer(
    examples=[
        OpenApiExample(
            name="Invalid Or Expired Activation Token",
            value={
                "status_code": status.HTTP_401_UNAUTHORIZED,
                "error": "Invalid Or Expired Activation Token",
            },
            summary="Invalid Or Expired Activation Token",
            description="Invalid Or Expired Activation Token Example",
            response_only=True,
            status_codes=[status.HTTP_401_UNAUTHORIZED],
        ),
        OpenApiExample(
            name="Invalid Activation Token",
            value={
                "status_code": status.HTTP_401_UNAUTHORIZED,
                "error": "Invalid Activation Token",
            },
            summary="Invalid Activation Token",
            description="Invalid Activation Token Example",
            response_only=True,
            status_codes=[status.HTTP_401_UNAUTHORIZED],
        ),
    ],
)
class UserActivateUnauthorizedErrorResponseSerializer(GenericResponseSerializer):
    """
    User Activate Unauthorized Error Response Serializer For Standardized API Responses.

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
    "UserActivateResponseSerializer",
    "UserActivateUnauthorizedErrorResponseSerializer",
]
