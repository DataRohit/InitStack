# Third Party Imports
from django.utils.translation import gettext_lazy as _
from drf_spectacular.utils import OpenApiExample
from drf_spectacular.utils import extend_schema_serializer
from rest_framework import serializers
from rest_framework import status

# Local Imports
from apps.common.serializers.generic_response_serializer import Generic202ResponseSerializer
from apps.common.serializers.generic_response_serializer import GenericResponseSerializer


# User Delete Request Accepted Response Serializer Class
@extend_schema_serializer(
    examples=[
        OpenApiExample(
            name="User Delete Request Accepted Response Example",
            value={
                "status_code": 202,
                "message": "Deletion Request Sent Successfully",
            },
            summary="User Delete Request Accepted Response Example",
            description="User Delete Request Accepted Response Example",
            response_only=True,
            status_codes=[status.HTTP_202_ACCEPTED],
        ),
    ],
)
class UserDeleteRequestAcceptedResponseSerializer(Generic202ResponseSerializer):
    """
    User Delete Request Accepted Response Serializer For Standardized API Responses.

    Attributes:
        status_code (int): HTTP Status Code For The Response.
        message (str): Message For The Response.
    """

    # Message Field
    message: serializers.CharField = serializers.CharField(
        help_text=_("Message For The Response"),
        label=_("Message"),
        default="Account Deletion Request Sent Successfully",
    )


# User Delete Request Unauthorized Error Response Serializer Class
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
    ],
)
class UserDeleteRequestUnauthorizedErrorResponseSerializer(GenericResponseSerializer):
    """
    User Delete Request Unauthorized Error Response Serializer For Standardized API Responses.

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


# User Delete Confirm Unauthorized Error Response Serializer Class
@extend_schema_serializer(
    examples=[
        OpenApiExample(
            name="Invalid Deletion Token",
            value={
                "status_code": status.HTTP_401_UNAUTHORIZED,
                "error": "Invalid Deletion Token",
            },
            summary="Invalid Deletion Token",
            description="Invalid Deletion Token Error Response",
            response_only=True,
            status_codes=[status.HTTP_401_UNAUTHORIZED],
        ),
        OpenApiExample(
            name="Invalid Or Expired Deletion Token",
            value={
                "status_code": status.HTTP_401_UNAUTHORIZED,
                "error": "Invalid Or Expired Deletion Token",
            },
            summary="Invalid Or Expired Deletion Token",
            description="Invalid Or Expired Deletion Token Error Response",
            response_only=True,
            status_codes=[status.HTTP_401_UNAUTHORIZED],
        ),
    ],
)
class UserDeleteConfirmUnauthorizedErrorResponseSerializer(GenericResponseSerializer):
    """
    User Delete Confirm Unauthorized Error Response Serializer For Standardized API Responses.

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
    "UserDeleteConfirmUnauthorizedErrorResponseSerializer",
    "UserDeleteRequestAcceptedResponseSerializer",
    "UserDeleteRequestUnauthorizedErrorResponseSerializer",
]
