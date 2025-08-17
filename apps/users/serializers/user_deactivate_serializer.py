# Third Party Imports
from django.utils.translation import gettext_lazy as _
from drf_spectacular.utils import OpenApiExample
from drf_spectacular.utils import extend_schema_serializer
from rest_framework import serializers
from rest_framework import status

# Local Imports
from apps.common.serializers.generic_response_serializer import Generic202ResponseSerializer
from apps.common.serializers.generic_response_serializer import GenericResponseSerializer
from apps.users.serializers.base_serializer import UserDetailSerializer


# User Deactivate Accepted Response Serializer Class
@extend_schema_serializer(
    examples=[
        OpenApiExample(
            name="User Deactivate Accepted Response Example",
            value={
                "status_code": 202,
                "message": "Deactivation Request Sent Successfully",
            },
            summary="User Deactivate Accepted Response Example",
            description="User Deactivate Accepted Response Example",
            response_only=True,
            status_codes=[status.HTTP_202_ACCEPTED],
        ),
    ],
)
class UserDeactivateAcceptedResponseSerializer(Generic202ResponseSerializer):
    """
    User Deactivate Accepted Response Serializer For Standardized API Responses.

    Attributes:
        status_code (int): HTTP Status Code For The Response.
        message (str): Message For The Response.
    """

    # Message Field
    message: serializers.CharField = serializers.CharField(
        help_text=_("Message For The Response"),
        label=_("Message"),
        default="Account Deactivation Request Sent Successfully",
    )


# User Deactivate Response Serializer Class
@extend_schema_serializer(
    examples=[
        OpenApiExample(
            name="User Deactivate Response Example",
            value={
                "status_code": 200,
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
                    "last_login": "2025-08-16T19:10:06.602446+05:30",
                },
            },
            summary="User Deactivate Response Example",
            description="User Deactivate Response Example",
            response_only=True,
            status_codes=[status.HTTP_200_OK],
        ),
    ],
)
class UserDeactivateResponseSerializer(GenericResponseSerializer):
    """
    User Deactivate Response Serializer For Standardized API Responses.

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


# User Deactivate Unauthorized Error Response Serializer Class
@extend_schema_serializer(
    examples=[
        OpenApiExample(
            name="Invalid Token Format",
            value={
                "status_code": status.HTTP_401_UNAUTHORIZED,
                "error": "Invalid Token Format",
            },
            summary="Invalid Token Format",
            description="Invalid Token Format Error Response",
            response_only=True,
            status_codes=[status.HTTP_401_UNAUTHORIZED],
        ),
        OpenApiExample(
            name="Token Has Expired",
            value={
                "status_code": status.HTTP_401_UNAUTHORIZED,
                "error": "Token Has Expired",
            },
            summary="Token Has Expired",
            description="Token Has Expired Error Response",
            response_only=True,
            status_codes=[status.HTTP_401_UNAUTHORIZED],
        ),
        OpenApiExample(
            name="Invalid Token",
            value={
                "status_code": status.HTTP_401_UNAUTHORIZED,
                "error": "Invalid Token",
            },
            summary="Invalid Token",
            description="Invalid Token Error Response",
            response_only=True,
            status_codes=[status.HTTP_401_UNAUTHORIZED],
        ),
        OpenApiExample(
            name="Token Has Been Revoked",
            value={
                "status_code": status.HTTP_401_UNAUTHORIZED,
                "error": "Token Has Been Revoked",
            },
            summary="Token Has Been Revoked",
            description="Token Has Been Revoked Error Response",
            response_only=True,
            status_codes=[status.HTTP_401_UNAUTHORIZED],
        ),
        OpenApiExample(
            name="User Not Found",
            value={
                "status_code": status.HTTP_401_UNAUTHORIZED,
                "error": "User Not Found",
            },
            summary="User Not Found",
            description="User Not Found Error Response",
            response_only=True,
            status_codes=[status.HTTP_401_UNAUTHORIZED],
        ),
        OpenApiExample(
            name="User Account Is Disabled",
            value={
                "status_code": status.HTTP_401_UNAUTHORIZED,
                "error": "User Account Is Disabled",
            },
            summary="User Account Is Disabled",
            description="User Account Is Disabled Error Response",
            response_only=True,
            status_codes=[status.HTTP_401_UNAUTHORIZED],
        ),
        OpenApiExample(
            name="Invalid Deactivation Token",
            value={
                "status_code": status.HTTP_401_UNAUTHORIZED,
                "error": "Invalid Deactivation Token",
            },
            summary="Invalid Deactivation Token",
            description="Invalid Deactivation Token Error Response",
            response_only=True,
            status_codes=[status.HTTP_401_UNAUTHORIZED],
        ),
    ],
)
class UserDeactivateUnauthorizedErrorResponseSerializer(GenericResponseSerializer):
    """
    User Deactivate Unauthorized Error Response Serializer For Standardized API Responses.

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
    "UserDeactivateAcceptedResponseSerializer",
    "UserDeactivateResponseSerializer",
    "UserDeactivateUnauthorizedErrorResponseSerializer",
]
