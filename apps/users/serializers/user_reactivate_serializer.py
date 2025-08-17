# Third Party Imports
from django.utils.translation import gettext_lazy as _
from drf_spectacular.utils import OpenApiExample
from drf_spectacular.utils import extend_schema_serializer
from rest_framework import serializers
from rest_framework import status

# Local Imports
from apps.common.serializers.generic_response_serializer import GenericResponseSerializer
from apps.users.serializers.base_serializer import UserDetailSerializer


# User Reactivate Payload Serializer Class
@extend_schema_serializer(
    examples=[
        OpenApiExample(
            name="User Reactivate Payload Example",
            value={
                "identifier": "johndoe@example.com",
                "re_identifier": "johndoe@example.com",
            },
            summary="User Reactivate Payload Example",
            description="User Reactivate Request Payload Example",
            request_only=True,
            status_codes=[status.HTTP_200_OK],
        ),
    ],
)
class UserReactivatePayloadSerializer(serializers.Serializer):
    """
    User Reactivate Payload Serializer For Reactivating User Accounts.

    Attributes:
        identifier (serializers.CharField): Username Or Email Identifier.
        re_identifier (serializers.CharField): Identifier Confirmation Field.
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

    # Re-Identifier Field
    re_identifier: serializers.CharField = serializers.CharField(
        help_text=_("Confirm Identifier"),
        label=_("Identifier Confirmation"),
        required=True,
        allow_null=False,
        error_messages={
            "required": _("Identifier Confirmation Is Required"),
            "null": _("Identifier Confirmation Cannot Be Null"),
            "blank": _("Identifier Confirmation Cannot Be Blank"),
        },
    )

    # Validate Method
    def validate(self, attrs: dict[str, str]) -> dict[str, str]:
        """
        Validate Identifier Match Between Identifier And Confirmation.

        Args:
            attrs (dict[str, str]): Dictionary Of Field Values.

        Returns:
            dict[str, str]: Validated Data Dictionary.

        Raises:
            serializers.ValidationError: If Identifiers Do Not Match.
        """

        # Check Matching Identifiers
        if attrs.get("identifier") != attrs.get("re_identifier"):
            # Raise Validation Error
            raise serializers.ValidationError(
                {"identifier": _("Identifiers Do Not Match")},
                code="identifier_mismatch",
            ) from None

        # Return Validated Data
        return attrs


# User Reactivate Accepted Response Serializer Class
@extend_schema_serializer(
    examples=[
        OpenApiExample(
            name="User Reactivate Accepted Response Example",
            value={
                "status_code": 202,
                "message": "Reactivation Request Sent Successfully",
            },
            summary="User Reactivate Accepted Response Example",
            description="User Reactivate Accepted Response Example",
            response_only=True,
            status_codes=[status.HTTP_202_ACCEPTED],
        ),
    ],
)
class UserReactivateAcceptedResponseSerializer(GenericResponseSerializer):
    """
    User Reactivate Accepted Response Serializer For Standardized API Responses.

    Attributes:
        status_code (int): HTTP Status Code For The Response.
        message (str): Success Message For The Response.
    """

    # Message Field
    message: serializers.CharField = serializers.CharField(
        help_text=_("Success Message For The Response"),
        label=_("Message"),
        default="Reactivation Request Sent Successfully",
    )


# User Reactivate Success Response Serializer Class
@extend_schema_serializer(
    examples=[
        OpenApiExample(
            name="User Reactivate Success Response Example",
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
            summary="User Reactivate Success Response Example",
            description="User Reactivate Success Response Example",
            response_only=True,
            status_codes=[status.HTTP_200_OK],
        ),
        OpenApiExample(
            name="User Reactivate With Last Login Example",
            value={
                "status_code": 200,
                "user": {
                    "id": "123e4567-e89b-12d3-a456-426614174002",
                    "username": "johndoe",
                    "email": "johndoe@example.com",
                    "first_name": "John",
                    "last_name": "Doe",
                    "is_active": True,
                    "is_staff": False,
                    "is_superuser": False,
                    "date_joined": "2025-08-16T19:04:06.602446+05:30",
                    "last_login": "2025-08-17T15:40:00+05:30",
                },
            },
            summary="User Reactivate With Last Login",
            description="User Reactivate Success Response Example With Last Login Timestamp",
            response_only=True,
            status_codes=[status.HTTP_200_OK],
        ),
    ],
)
class UserReactivateSuccessResponseSerializer(GenericResponseSerializer):
    """
    User Reactivation Success Response Serializer For Standardized API Responses.

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


# User Reactivate Bad Request Error Response Serializer Class
@extend_schema_serializer(
    examples=[
        OpenApiExample(
            name="Missing Required Fields",
            value={
                "status_code": status.HTTP_400_BAD_REQUEST,
                "errors": {
                    "identifier": ["Identifier Is Required"],
                    "re_identifier": ["Identifier Confirmation Is Required"],
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
                    "re_identifier": ["Identifier Confirmation Cannot Be Null"],
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
                    "re_identifier": ["Identifier Confirmation Cannot Be Blank"],
                },
            },
            summary="Blank Field Values",
            description="Error Response When Fields Are Provided As Blank",
            response_only=True,
            status_codes=[status.HTTP_400_BAD_REQUEST],
        ),
        OpenApiExample(
            name="Identifier Mismatch",
            value={
                "status_code": status.HTTP_400_BAD_REQUEST,
                "errors": {
                    "identifier": ["Identifiers Do Not Match"],
                },
            },
            summary="Identifier Mismatch",
            description="Error Response When Identifier And Confirmation Do Not Match",
            response_only=True,
            status_codes=[status.HTTP_400_BAD_REQUEST],
        ),
        OpenApiExample(
            name="User Not Found",
            value={
                "status_code": status.HTTP_400_BAD_REQUEST,
                "errors": {
                    "identifier": ["No Account Found With This Identifier"],
                },
            },
            summary="User Not Found",
            description="Error Response When No Account Is Found With The Given Identifier",
            response_only=True,
            status_codes=[status.HTTP_400_BAD_REQUEST],
        ),
        OpenApiExample(
            name="User Already Active",
            value={
                "status_code": status.HTTP_400_BAD_REQUEST,
                "errors": {
                    "identifier": ["Account Is Already Active"],
                },
            },
            summary="User Already Active",
            description="Error Response When User Account Is Already Active",
            response_only=True,
            status_codes=[status.HTTP_400_BAD_REQUEST],
        ),
    ],
)
class UserReactivateBadRequestErrorResponseSerializer(GenericResponseSerializer):
    """
    User Reactivate Bad Request Error Response Serializer For Standardized API Responses.

    Attributes:
        status_code (int): HTTP Status Code For The Response.
        errors (UserReactivateErrorsDetailSerializer): Error Details For The Response.
    """

    # Error Detail Serializer
    class UserReactivateErrorsDetailSerializer(serializers.Serializer):
        """
        User Reactivate Error Detail Serializer For Standardized API Responses.

        Attributes:
            identifier (list[str]): List Of Errors Related To The Identifier Field.
            re_identifier (list[str]): List Of Errors Related To The Identifier Confirmation Field.
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

        # Re-Identifier Field
        re_identifier: serializers.ListField = serializers.ListField(
            help_text=_("Errors Related To The Identifier Confirmation Field"),
            label=_("Identifier Confirmation Errors"),
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
    errors: UserReactivateErrorsDetailSerializer = UserReactivateErrorsDetailSerializer(
        help_text=_("Object Containing Validation Errors"),
        label=_("Errors"),
        required=False,
        allow_null=True,
        default=None,
    )


# User Reactivate Unauthorized Error Response Serializer Class
@extend_schema_serializer(
    examples=[
        OpenApiExample(
            name="Invalid Reactivation Token",
            value={
                "status_code": status.HTTP_401_UNAUTHORIZED,
                "error": "Invalid Reactivation Token",
            },
            summary="Invalid Reactivation Token",
            description="Invalid Reactivation Token Error Response",
            response_only=True,
            status_codes=[status.HTTP_401_UNAUTHORIZED],
        ),
        OpenApiExample(
            name="Invalid Or Expired Reactivation Token",
            value={
                "status_code": status.HTTP_401_UNAUTHORIZED,
                "error": "Invalid Or Expired Reactivation Token",
            },
            summary="Invalid Or Expired Reactivation Token",
            description="Invalid Or Expired Reactivation Token Error Response",
            response_only=True,
            status_codes=[status.HTTP_401_UNAUTHORIZED],
        ),
    ],
)
class UserReactivateUnauthorizedErrorResponseSerializer(GenericResponseSerializer):
    """
    User Reactivate Unauthorized Error Response Serializer For Standardized API Responses.

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
    "UserReactivateAcceptedResponseSerializer",
    "UserReactivateBadRequestErrorResponseSerializer",
    "UserReactivatePayloadSerializer",
    "UserReactivateSuccessResponseSerializer",
    "UserReactivateUnauthorizedErrorResponseSerializer",
]
