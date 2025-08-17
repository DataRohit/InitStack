# Third Party Imports
from django.utils.translation import gettext_lazy as _
from drf_spectacular.utils import OpenApiExample
from drf_spectacular.utils import extend_schema_serializer
from rest_framework import serializers
from rest_framework import status

# Local Imports
from apps.common.serializers.generic_response_serializer import Generic202ResponseSerializer
from apps.common.serializers.generic_response_serializer import GenericResponseSerializer


# User Delete Accepted Response Serializer Class
@extend_schema_serializer(
    examples=[
        OpenApiExample(
            name="User Delete Accepted Response Example",
            value={
                "status_code": 202,
                "message": "Deletion Request Sent Successfully",
            },
            summary="User Delete Accepted Response Example",
            description="User Delete Accepted Response Example",
            response_only=True,
            status_codes=[status.HTTP_202_ACCEPTED],
        ),
    ],
)
class UserDeleteAcceptedResponseSerializer(Generic202ResponseSerializer):
    """
    User Delete Accepted Response Serializer For Standardized API Responses.

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


# User Delete Unauthorized Error Response Serializer Class
@extend_schema_serializer(
    examples=[
        OpenApiExample(
            name="User Delete Unauthorized Error Response Example",
            value={
                "status_code": 401,
                "message": "Invalid Or Expired Deletion Token",
            },
            summary="User Delete Unauthorized Error Response Example",
            description="User Delete Unauthorized Error Response Example",
            response_only=True,
            status_codes=[status.HTTP_401_UNAUTHORIZED],
        ),
    ],
)
class UserDeleteUnauthorizedErrorResponseSerializer(GenericResponseSerializer):
    """
    User Delete Unauthorized Error Response Serializer For Standardized API Responses.

    Attributes:
        status_code (int): HTTP Status Code For The Response.
        message (str): Message For The Response.
    """

    # Message Field
    message: serializers.CharField = serializers.CharField(
        help_text=_("Error Message For The Response"),
        label=_("Message"),
        default="Invalid Or Expired Deletion Token",
    )


# Exports
__all__: list[str] = [
    "UserDeleteAcceptedResponseSerializer",
    "UserDeleteUnauthorizedErrorResponseSerializer",
]
