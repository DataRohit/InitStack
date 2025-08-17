# Third Party Imports
from django.utils.translation import gettext_lazy as _
from drf_spectacular.utils import OpenApiExample
from drf_spectacular.utils import extend_schema_serializer
from rest_framework import serializers
from rest_framework import status

# Local Imports
from apps.common.serializers.generic_response_serializer import GenericResponseSerializer


# User Re-Login Payload Serializer Class
@extend_schema_serializer(
    examples=[
        OpenApiExample(
            name="User Re-Login Payload Example",
            value={
                "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
            },
            summary="User Re-Login Payload Example",
            description="User Re-Login Request Payload Example With Refresh Token",
            request_only=True,
            status_codes=[status.HTTP_200_OK],
        ),
    ],
)
class UserReLoginPayloadSerializer(serializers.Serializer):
    """
    User Re-Login Payload Serializer With Refresh Token Only.

    Attributes:
        refresh_token (serializers.CharField): JWT Refresh Token (Write Only).
    """

    # Refresh Token Field
    refresh_token: serializers.CharField = serializers.CharField(
        style={"input_type": "password"},
        write_only=True,
        help_text=(_("Enter Refresh Token")),
        label=_("Refresh Token"),
        required=True,
        allow_null=False,
        error_messages={
            "required": _("Refresh Token Is Required"),
            "null": _("Refresh Token Cannot Be Null"),
            "blank": _("Refresh Token Cannot Be Blank"),
        },
    )


# User Re-Login Bad Request Error Response Serializer Class
@extend_schema_serializer(
    examples=[
        OpenApiExample(
            name="Missing Required Fields",
            value={
                "status_code": status.HTTP_400_BAD_REQUEST,
                "errors": {
                    "refresh_token": ["Refresh Token Is Required"],
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
                    "refresh_token": ["Refresh Token Cannot Be Null"],
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
                    "refresh_token": ["Refresh Token Cannot Be Blank"],
                },
            },
            summary="Blank Field Values",
            description="Error Response When Fields Are Provided As Blank",
            response_only=True,
            status_codes=[status.HTTP_400_BAD_REQUEST],
        ),
    ],
)
class UserReLoginBadRequestErrorResponseSerializer(GenericResponseSerializer):
    """
    User Re-Login Bad Request Error Response Serializer For Standardized API Responses.

    Attributes:
        status_code (int): HTTP Status Code For The Response.
        error (str): Error Message For The Response.
    """

    # Error Field
    error: serializers.CharField = serializers.CharField(
        help_text=_("Error Message For The Response"),
        label=_("Error Message"),
        default="Bad Request",
    )


# User Re-Login Unauthorized Error Response Serializer Class
@extend_schema_serializer(
    examples=[
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
class UserReLoginUnauthorizedErrorResponseSerializer(GenericResponseSerializer):
    """
    User Re-Login Unauthorized Error Response Serializer For Standardized API Responses.

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
    "UserReLoginBadRequestErrorResponseSerializer",
    "UserReLoginPayloadSerializer",
    "UserReLoginUnauthorizedErrorResponseSerializer",
]
