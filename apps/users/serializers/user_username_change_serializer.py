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


# User Username Change Payload Serializer Class
@extend_schema_serializer(
    examples=[
        OpenApiExample(
            name="User Username Change Payload Example",
            value={
                "username": "johnnew",
                "re_username": "johnnew",
            },
            summary="User Username Change Payload Example",
            description="User Username Change Request Payload Example",
            request_only=True,
            status_codes=[status.HTTP_200_OK],
        ),
    ],
)
class UserUsernameChangePayloadSerializer(serializers.Serializer):
    """
    User Username Change Payload Serializer For Updating Username.

    Attributes:
        username (serializers.CharField): New Username Field.
        re_username (serializers.CharField): Username Confirmation Field.

    Methods:
        validate(attrs: dict[str, str]) -> dict[str, str]: Validate Matching Usernames.
    """

    # Username Field
    username: serializers.CharField = serializers.CharField(
        help_text=_("Enter A Valid Username"),
        label=_("Username"),
        required=True,
        allow_null=False,
        error_messages={
            "required": _("Username Is Required"),
            "null": _("Username Cannot Be Null"),
            "blank": _("Username Cannot Be Blank"),
        },
    )

    # Re-Username Field
    re_username: serializers.CharField = serializers.CharField(
        help_text=_("Confirm Username"),
        label=_("Username Confirmation"),
        required=True,
        allow_null=False,
        error_messages={
            "required": _("Username Confirmation Is Required"),
            "null": _("Username Confirmation Cannot Be Null"),
            "blank": _("Username Confirmation Cannot Be Blank"),
        },
    )

    # Validate Method
    def validate(self, attrs: dict[str, str]) -> dict[str, str]:
        """
        Validate Username Match Between Username And Confirmation.

        Args:
            attrs (dict[str, str]): Dictionary Of Field Values.

        Returns:
            dict[str, str]: Validated Data Dictionary.

        Raises:
            serializers.ValidationError: If Usernames Do Not Match.
        """

        # Check Matching Usernames
        if attrs.get("username") != attrs.get("re_username"):
            # Raise Validation Error
            raise serializers.ValidationError(
                {"username": _("Usernames Do Not Match")},
                code="username_mismatch",
            ) from None

        # Return Validated Data
        return attrs


# User Username Change Confirm Bad Request Error Response Serializer Class
@extend_schema_serializer(
    examples=[
        OpenApiExample(
            name="Missing Required Fields",
            value={
                "status_code": status.HTTP_400_BAD_REQUEST,
                "errors": {
                    "username": ["Username Is Required"],
                    "re_username": ["Username Confirmation Is Required"],
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
                    "re_username": ["Username Confirmation Cannot Be Null"],
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
                    "username": ["Username Cannot Be Blank"],
                    "re_username": ["Username Confirmation Cannot Be Blank"],
                },
            },
            summary="Blank Field Values",
            description="Error Response When Fields Are Provided As Blank",
            response_only=True,
            status_codes=[status.HTTP_400_BAD_REQUEST],
        ),
        OpenApiExample(
            name="Username Mismatch",
            value={
                "status_code": status.HTTP_400_BAD_REQUEST,
                "errors": {
                    "username": ["Usernames Do Not Match"],
                },
            },
            summary="Username Mismatch",
            description="Error Response When Username And Confirmation Do Not Match",
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
    ],
)
class UserUsernameChangeConfirmBadRequestErrorResponseSerialzier(GenericResponseSerializer):
    """
    User Username Change Confirm Bad Request Error Response Serializer For Standardized API Responses.

    Attributes:
        status_code (int): HTTP Status Code For The Response.
        errors (UserUsernameChangeErrorsDetailSerializer): Error Details For The Response.
    """

    # Error Detail Serializer
    class UserUsernameChangeErrorsDetailSerializer(serializers.Serializer):
        """
        User Username Change Error Detail Serializer For Standardized API Responses.

        Attributes:
            username (list[str]): List Of Errors Related To The Username Field.
            re_username (list[str]): List Of Errors Related To The Username Confirmation Field.
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

        # Re-Username Field
        re_username: serializers.ListField = serializers.ListField(
            help_text=_("Errors Related To The Username Confirmation Field"),
            label=_("Username Confirmation Errors"),
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
    errors: UserUsernameChangeErrorsDetailSerializer = UserUsernameChangeErrorsDetailSerializer(
        help_text=_("Object Containing Validation Errors"),
        label=_("Errors"),
        required=False,
        allow_null=True,
        default=None,
    )


# User Username Change Request Accepted Response Serializer Class
@extend_schema_serializer(
    examples=[
        OpenApiExample(
            name="User Username Change Request Accepted Response Example",
            value={
                "status_code": 202,
                "message": "Username Change Request Sent Successfully",
            },
            summary="User Username Change Request Accepted Response Example",
            description="User Username Change Request Accepted Response Example",
            response_only=True,
            status_codes=[status.HTTP_202_ACCEPTED],
        ),
    ],
)
class UserUsernameChangeRequestAcceptedResponseSerializer(Generic202ResponseSerializer):
    """
    User Username Change Request Accepted Response Serializer For Standardized API Responses.

    Attributes:
        status_code (int): HTTP Status Code For The Response.
        message (str): Message For The Response.
    """

    # Message Field
    message: serializers.CharField = serializers.CharField(
        help_text=_("Message For The Response"),
        label=_("Message"),
        default="Username Change Request Sent Successfully",
    )


# User Username Change Confirm Response Serializer Class
@extend_schema_serializer(
    examples=[
        OpenApiExample(
            name="User Username Change Confirm Response Example",
            value={
                "status_code": 200,
                "user": {
                    "id": "123e4567-e89b-12d3-a456-426614174000",
                    "username": "johnnew",
                    "email": "johndoe@example.com",
                    "first_name": "John",
                    "last_name": "Doe",
                    "is_active": True,
                    "is_staff": False,
                    "is_superuser": False,
                    "date_joined": "2025-08-16T19:04:06.602446+05:30",
                    "last_login": "2025-08-16T19:10:06.602446+05:30",
                },
            },
            summary="User Username Change Confirm Response Example",
            description="User Username Change Confirm Response Example",
            response_only=True,
            status_codes=[status.HTTP_200_OK],
        ),
    ],
)
class UserUsernameChangeConfirmResponseSerializer(GenericResponseSerializer):
    """
    User Username Change Confirm Response Serializer For Standardized API Responses.

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


# User Username Change Request Unauthorized Error Response Serializer Class
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
class UserUsernameChangeRequestUnauthorizedErrorResponseSerializer(GenericResponseSerializer):
    """
    User UsernameChange Request Unauthorized Error Response Serializer For Standardized API Responses.

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


# User Username Change Confirm Unauthorized Error Response Serializer Class
@extend_schema_serializer(
    examples=[
        OpenApiExample(
            name="Invalid Username Change Token",
            value={
                "status_code": status.HTTP_401_UNAUTHORIZED,
                "error": "Invalid Username Change Token",
            },
            summary="Invalid Username Change Token",
            description="Invalid Username Change Token Error Response",
            response_only=True,
            status_codes=[status.HTTP_401_UNAUTHORIZED],
        ),
        OpenApiExample(
            name="Invalid Or Expired Username Change Token",
            value={
                "status_code": status.HTTP_401_UNAUTHORIZED,
                "error": "Invalid Or Expired Username Change Token",
            },
            summary="Invalid Or Expired Username Change Token",
            description="Invalid Or Expired Username Change Token Error Response",
            response_only=True,
            status_codes=[status.HTTP_401_UNAUTHORIZED],
        ),
    ],
)
class UserUsernameChangeConfirmUnauthorizedErrorResponseSerializer(GenericResponseSerializer):
    """
    User UsernameChange Confirm Unauthorized Error Response Serializer For Standardized API Responses.

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
    "UserUsernameChangeConfirmBadRequestErrorResponseSerialzier",
    "UserUsernameChangeConfirmResponseSerializer",
    "UserUsernameChangeConfirmUnauthorizedErrorResponseSerializer",
    "UserUsernameChangePayloadSerializer",
    "UserUsernameChangeRequestAcceptedResponseSerializer",
    "UserUsernameChangeRequestUnauthorizedErrorResponseSerializer",
]
