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


# User Email Change Payload Serializer Class
@extend_schema_serializer(
    examples=[
        OpenApiExample(
            name="User Email Change Payload Example",
            value={
                "email": "newemail@example.com",
                "re_email": "newemail@example.com",
            },
            summary="User Email Change Payload Example",
            description="User Email Change Request Payload Example",
            request_only=True,
            status_codes=[status.HTTP_200_OK],
        ),
    ],
)
class UserEmailChangePayloadSerializer(serializers.Serializer):
    """
    User Email Change Payload Serializer For Updating Email.

    Attributes:
        email (serializers.EmailField): New Email Field.
        re_email (serializers.EmailField): Email Confirmation Field.

    Methods:
        validate(attrs: dict[str, str]) -> dict[str, str]: Validate Matching Emails.
    """

    # Email Field
    email: serializers.EmailField = serializers.EmailField(
        help_text=_("Enter A Valid Email"),
        label=_("Email"),
        required=True,
        allow_null=False,
        error_messages={
            "required": _("Email Is Required"),
            "null": _("Email Cannot Be Null"),
            "blank": _("Email Cannot Be Blank"),
            "invalid": _("Enter A Valid Email Address"),
        },
    )

    # Re-Email Field
    re_email: serializers.EmailField = serializers.EmailField(
        help_text=_("Confirm Email"),
        label=_("Email Confirmation"),
        required=True,
        allow_null=False,
        error_messages={
            "required": _("Email Confirmation Is Required"),
            "null": _("Email Confirmation Cannot Be Null"),
            "blank": _("Email Confirmation Cannot Be Blank"),
            "invalid": _("Enter A Valid Email Address"),
        },
    )

    # Validate Method
    def validate(self, attrs: dict[str, str]) -> dict[str, str]:
        """
        Validate Email Match Between Email And Confirmation.

        Args:
            attrs (dict[str, str]): Dictionary Of Field Values.

        Returns:
            dict[str, str]: Validated Data Dictionary.

        Raises:
            serializers.ValidationError: If Emails Do Not Match.
        """

        # Check Matching Emails
        if attrs.get("email") != attrs.get("re_email"):
            # Raise Validation Error
            raise serializers.ValidationError(
                {"email": _("Emails Do Not Match")},
                code="email_mismatch",
            ) from None

        # Return Validated Data
        return attrs


# User Email Change Bad Request Error Response Serializer Class
@extend_schema_serializer(
    examples=[
        OpenApiExample(
            name="Missing Required Fields",
            value={
                "status_code": status.HTTP_400_BAD_REQUEST,
                "errors": {
                    "email": ["Email Is Required"],
                    "re_email": ["Email Confirmation Is Required"],
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
                    "email": ["Email Cannot Be Null"],
                    "re_email": ["Email Confirmation Cannot Be Null"],
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
                    "email": ["Email Cannot Be Blank"],
                    "re_email": ["Email Confirmation Cannot Be Blank"],
                },
            },
            summary="Blank Field Values",
            description="Error Response When Fields Are Provided As Blank",
            response_only=True,
            status_codes=[status.HTTP_400_BAD_REQUEST],
        ),
        OpenApiExample(
            name="Email Mismatch",
            value={
                "status_code": status.HTTP_400_BAD_REQUEST,
                "errors": {
                    "email": ["Emails Do Not Match"],
                },
            },
            summary="Email Mismatch",
            description="Error Response When Email And Confirmation Do Not Match",
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
            description="Error Response When Email Is Already Taken",
            response_only=True,
            status_codes=[status.HTTP_400_BAD_REQUEST],
        ),
        OpenApiExample(
            name="Invalid Email Format",
            value={
                "status_code": status.HTTP_400_BAD_REQUEST,
                "errors": {
                    "email": ["Enter A Valid Email Address"],
                    "re_email": ["Enter A Valid Email Address"],
                },
            },
            summary="Invalid Email Format",
            description="Error Response When Email Format Is Invalid",
            response_only=True,
            status_codes=[status.HTTP_400_BAD_REQUEST],
        ),
    ],
)
class UserEmailChangeBadRequestErrorResponseSerializer(GenericResponseSerializer):
    """
    User Email Change Bad Request Error Response Serializer For Standardized API Responses.

    Attributes:
        status_code (int): HTTP Status Code For The Response.
        errors (UserEmailChangeErrorsDetailSerializer): Error Details For The Response.
    """

    # Error Detail Serializer
    class UserEmailChangeErrorsDetailSerializer(serializers.Serializer):
        """
        User Email Change Error Detail Serializer For Standardized API Responses.

        Attributes:
            email (list[str]): List Of Errors Related To The Email Field.
            re_email (list[str]): List Of Errors Related To The Email Confirmation Field.
            non_field_errors (list[str]): List Of Non-Field Specific Errors.
        """

        # Email Field
        email: serializers.ListField = serializers.ListField(
            help_text=_("Errors Related To The Email Field"),
            label=_("Email Errors"),
            required=False,
            allow_null=True,
            child=serializers.CharField(),
        )

        # Re-Email Field
        re_email: serializers.ListField = serializers.ListField(
            help_text=_("Errors Related To The Email Confirmation Field"),
            label=_("Email Confirmation Errors"),
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
    errors: UserEmailChangeErrorsDetailSerializer = UserEmailChangeErrorsDetailSerializer(
        help_text=_("Object Containing Validation Errors"),
        label=_("Errors"),
        required=False,
        allow_null=True,
        default=None,
    )


# User Email Change Accepted Response Serializer Class
@extend_schema_serializer(
    examples=[
        OpenApiExample(
            name="User Email Change Accepted Response Example",
            value={
                "status_code": 202,
                "message": "Email Change Request Sent Successfully",
            },
            summary="User Email Change Accepted Response Example",
            description="User Email Change Accepted Response Example",
            response_only=True,
            status_codes=[status.HTTP_202_ACCEPTED],
        ),
    ],
)
class UserEmailChangeAcceptedResponseSerializer(Generic202ResponseSerializer):
    """
    User Email Change Accepted Response Serializer For Standardized API Responses.

    Attributes:
        status_code (int): HTTP Status Code For The Response.
    """

    # Message Field
    message: serializers.CharField = serializers.CharField(
        help_text=_("Message For The Response"),
        label=_("Message"),
        default="Email Change Request Sent Successfully",
    )


# User Email Change Response Serializer Class
@extend_schema_serializer(
    examples=[
        OpenApiExample(
            name="User Email Change Response Example",
            value={
                "status_code": 200,
                "user": {
                    "id": "123e4567-e89b-12d3-a456-426614174000",
                    "username": "johnnew",
                    "email": "newemail@example.com",
                    "first_name": "John",
                    "last_name": "Doe",
                    "is_active": True,
                    "is_staff": False,
                    "is_superuser": False,
                    "date_joined": "2025-08-16T19:04:06.602446+05:30",
                    "last_login": "2025-08-16T19:10:06.602446+05:30",
                },
            },
            summary="User Email Change Response Example",
            description="User Email Change Response Example",
            response_only=True,
            status_codes=[status.HTTP_200_OK],
        ),
    ],
)
class UserEmailChangeResponseSerializer(GenericResponseSerializer):
    """
    User Email Change Response Serializer For Standardized API Responses.

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


# User Email Change Unauthorized Error Response Serializer Class
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
            name="Invalid Email Change Token",
            value={
                "status_code": status.HTTP_401_UNAUTHORIZED,
                "error": "Invalid Email Change Token",
            },
            summary="Invalid Email Change Token",
            description="Invalid Email Change Token Error Response",
            response_only=True,
            status_codes=[status.HTTP_401_UNAUTHORIZED],
        ),
        OpenApiExample(
            name="Invalid Or Expired Email Change Token",
            value={
                "status_code": status.HTTP_401_UNAUTHORIZED,
                "error": "Invalid Or Expired Email Change Token",
            },
            summary="Invalid Or Expired Email Change Token",
            description="Invalid Or Expired Email Change Token Error Response",
            response_only=True,
            status_codes=[status.HTTP_401_UNAUTHORIZED],
        ),
    ],
)
class UserEmailUnauthorizedErrorResponseSerializer(GenericResponseSerializer):
    """
    User Email Change Unauthorized Error Response Serializer For Standardized API Responses.

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
    "UserEmailChangeAcceptedResponseSerializer",
    "UserEmailChangeBadRequestErrorResponseSerializer",
    "UserEmailChangePayloadSerializer",
    "UserEmailChangeResponseSerializer",
    "UserEmailUnauthorizedErrorResponseSerializer",
]
