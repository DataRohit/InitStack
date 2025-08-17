# Third Party Imports
from django.core.validators import MaxLengthValidator
from django.core.validators import MinLengthValidator
from django.core.validators import RegexValidator
from django.utils.translation import gettext_lazy as _
from drf_spectacular.utils import OpenApiExample
from drf_spectacular.utils import extend_schema_serializer
from rest_framework import serializers
from rest_framework import status

# Local Imports
from apps.common.serializers.generic_response_serializer import GenericResponseSerializer


# User Reset Password Payload Serializer Class
@extend_schema_serializer(
    examples=[
        OpenApiExample(
            name="User Reset Password Payload Example",
            value={
                "identifier": "johndoe@example.com",
                "re_identifier": "johndoe@example.com",
            },
            summary="User Reset Password Payload Example",
            description="User Reset Password Request Payload Example",
            request_only=True,
            status_codes=[status.HTTP_200_OK],
        ),
    ],
)
class UserResetPasswordRequestPayloadSerializer(serializers.Serializer):
    """
    User Reset Password Request Payload Serializer For Resetting User Passwords.

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


# User Reset Password Accepted Response Serializer Class
@extend_schema_serializer(
    examples=[
        OpenApiExample(
            name="User Reset Password Accepted Response Example",
            value={
                "status_code": 202,
                "message": "Password Reset Request Sent Successfully",
            },
            summary="User Reset Password Accepted Response Example",
            description="User Reset Password Accepted Response Example",
            response_only=True,
            status_codes=[status.HTTP_202_ACCEPTED],
        ),
    ],
)
class UserResetPasswordRequestAcceptedResponseSerializer(GenericResponseSerializer):
    """
    User Reset Password Request Accepted Response Serializer For Standardized API Responses.

    Attributes:
        status_code (int): HTTP Status Code For The Response.
        message (str): Success Message For The Response.
    """

    # Message Field
    message: serializers.CharField = serializers.CharField(
        help_text=_("Success Message For The Response"),
        label=_("Message"),
        default="Password Reset Request Sent Successfully",
    )


# User Reset Password Confirm Payload Serializer Class
@extend_schema_serializer(
    examples=[
        OpenApiExample(
            name="User Reset Password Confirm Payload Example",
            value={
                "password": "SecurePassword@123",
                "re_password": "SecurePassword@123",
            },
            summary="User Reset Password Confirm Payload Example",
            description="User Reset Password Confirm Payload Example",
            request_only=True,
            status_codes=[status.HTTP_200_OK],
        ),
    ],
)
class UserResetPasswordConfirmPayloadSerializer(serializers.Serializer):
    """
    User Reset Password Confirm Payload Serializer For Confirming Password Reset.

    Attributes:
        password (serializers.CharField): New Password Field.
        re_password (serializers.CharField): Password Confirmation Field.
    """

    # Password Field
    password: serializers.CharField = serializers.CharField(
        style={"input_type": "password"},
        write_only=True,
        help_text=_("Enter A Valid Password"),
        label=_("Password"),
        required=True,
        allow_null=False,
        validators=[
            RegexValidator(
                regex=r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$",
                message=_(
                    "Password Must Contain At Least One Uppercase Letter, One Lowercase Letter, One Digit, and One Special Character",  # noqa: E501
                ),
                code="invalid_password",
            ),
            MinLengthValidator(
                limit_value=8,
                message=_("Password Must Contain At Least 8 Characters"),
            ),
            MaxLengthValidator(
                limit_value=60,
                message=_("Password Must Not Exceed 60 Characters"),
            ),
        ],
        error_messages={
            "required": _("Password Is Required"),
            "null": _("Password Cannot Be Null"),
            "blank": _("Password Cannot Be Blank"),
            "min_length": _("Password Must Contain At Least 8 Characters"),
            "max_length": _("Password Must Not Exceed 60 Characters"),
            "invalid_password": _(
                "Password Must Contain At Least One Uppercase Letter, One Lowercase Letter, One Digit, and One Special Character",  # noqa: E501
            ),
        },
    )

    # Password Confirmation Field
    re_password: serializers.CharField = serializers.CharField(
        style={"input_type": "password"},
        write_only=True,
        help_text=_("Confirm Password"),
        label=_("Password Confirmation"),
        required=True,
        allow_null=False,
        error_messages={
            "required": _("Password Confirmation Is Required"),
            "null": _("Password Confirmation Cannot Be Null"),
            "blank": _("Password Confirmation Cannot Be Blank"),
        },
    )

    # Validate Method
    def validate(self, attrs: dict[str, str]) -> dict[str, str]:
        """
        Validate Password Match Between Password And Confirmation.

        Args:
            attrs (dict[str, str]): Dictionary Of Field Values.

        Returns:
            dict[str, str]: Validated Data Dictionary.

        Raises:
            serializers.ValidationError: If Passwords Do Not Match.
        """

        # If Passwords Do Not Match
        if attrs.get("password") != attrs.get("re_password"):
            # Raise Validation Error
            raise serializers.ValidationError(
                {"password": _("Passwords Do Not Match")},
                code="password_mismatch",
            ) from None

        # Return Validated Data
        return attrs


# User Reset Password Confirm Response Serializer Class
@extend_schema_serializer(
    examples=[
        OpenApiExample(
            name="User Reset Password Confirm Response Example",
            value={
                "status_code": 200,
                "message": "Password Reset Completed Successfully",
            },
            summary="User Reset Password Confirm Response Example",
            description="User Reset Password Confirm Response Example",
            response_only=True,
            status_codes=[status.HTTP_200_OK],
        ),
    ],
)
class UserResetPasswordConfirmResponseSerializer(GenericResponseSerializer):
    """
    User Reset Password Confirm Response Serializer For Standardized API Responses.

    Attributes:
        status_code (int): HTTP Status Code For The Response.
        message (str): Success Message For The Response.
    """

    # Message Field
    message: serializers.CharField = serializers.CharField(
        help_text=_("Success Message For The Response"),
        label=_("Message"),
        default="Password Reset Completed Successfully",
    )


# User Reset Password Bad Request Error Response Serializer Class
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
    ],
)
class UserResetPasswordRequestBadRequestErrorResponseSerializer(GenericResponseSerializer):
    """
    User Reset Password Request Bad Request Error Response Serializer For Standardized API Responses.

    Attributes:
        status_code (int): HTTP Status Code For The Response.
        errors (UserResetPasswordErrorsDetailSerializer): Error Details For The Response.
    """

    # Error Detail Serializer
    class UserResetPasswordErrorsDetailSerializer(serializers.Serializer):
        """
        User Reset Password Error Detail Serializer For Standardized API Responses.

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
    errors: UserResetPasswordErrorsDetailSerializer = UserResetPasswordErrorsDetailSerializer(
        help_text=_("Object Containing Validation Errors"),
        label=_("Errors"),
        required=False,
        allow_null=True,
        default=None,
    )


# User Reset Password Confirm Bad Request Error Response Serializer Class
@extend_schema_serializer(
    examples=[
        OpenApiExample(
            name="Missing Required Fields",
            value={
                "status_code": status.HTTP_400_BAD_REQUEST,
                "errors": {
                    "password": ["Password Is Required"],
                    "re_password": ["Password Confirmation Is Required"],
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
                    "password": ["Password Cannot Be Null"],
                    "re_password": ["Password Confirmation Cannot Be Null"],
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
                    "password": ["Password Cannot Be Blank"],
                    "re_password": ["Password Confirmation Cannot Be Blank"],
                },
            },
            summary="Blank Field Values",
            description="Error Response When Fields Are Provided As Blank",
            response_only=True,
            status_codes=[status.HTTP_400_BAD_REQUEST],
        ),
        OpenApiExample(
            name="Password Mismatch",
            value={
                "status_code": status.HTTP_400_BAD_REQUEST,
                "errors": {
                    "password": ["Passwords Do Not Match"],
                },
            },
            summary="Password Mismatch",
            description="Error Response When Password And Confirmation Do Not Match",
            response_only=True,
            status_codes=[status.HTTP_400_BAD_REQUEST],
        ),
        OpenApiExample(
            name="Invalid Password Format",
            value={
                "status_code": status.HTTP_400_BAD_REQUEST,
                "errors": {
                    "password": [
                        "Password Must Contain At Least One Uppercase Letter, One Lowercase Letter, One Digit, and One Special Character",  # noqa: E501
                    ],
                },
            },
            summary="Invalid Password Format",
            description="Error Response When Password Format Is Invalid",
            response_only=True,
            status_codes=[status.HTTP_400_BAD_REQUEST],
        ),
        OpenApiExample(
            name="Password Too Short",
            value={
                "status_code": status.HTTP_400_BAD_REQUEST,
                "errors": {
                    "password": ["Password Must Contain At Least 8 Characters"],
                },
            },
            summary="Password Too Short",
            description="Error Response When Password Is Too Short",
            response_only=True,
            status_codes=[status.HTTP_400_BAD_REQUEST],
        ),
        OpenApiExample(
            name="Password Too Long",
            value={
                "status_code": status.HTTP_400_BAD_REQUEST,
                "errors": {
                    "password": ["Password Must Not Exceed 60 Characters"],
                },
            },
            summary="Password Too Long",
            description="Error Response When Password Is Too Long",
            response_only=True,
            status_codes=[status.HTTP_400_BAD_REQUEST],
        ),
    ],
)
class UserResetPasswordConfirmBadRequestErrorResponseSerializer(GenericResponseSerializer):
    """
    User Reset Password Confirm Bad Request Error Response Serializer For Standardized API Responses.

    Attributes:
        status_code (int): HTTP Status Code For The Response.
        errors (UserResetPasswordConfirmErrorsDetailSerializer): Error Details For The Response.
    """

    # Error Detail Serializer
    class UserResetPasswordConfirmErrorsDetailSerializer(serializers.Serializer):
        """
        User Reset Password Confirm Error Detail Serializer For Standardized API Responses.

        Attributes:
            password (list[str]): List Of Errors Related To The Password Field.
            re_password (list[str]): List Of Errors Related To The Password Confirmation Field.
            non_field_errors (list[str]): List Of Non-Field Specific Errors.
        """

        # Password Field
        password: serializers.ListField = serializers.ListField(
            help_text=_("Errors Related To The Password Field"),
            label=_("Password Errors"),
            required=False,
            allow_null=True,
            child=serializers.CharField(),
        )

        # Re-Password Field
        re_password: serializers.ListField = serializers.ListField(
            help_text=_("Errors Related To The Password Confirmation Field"),
            label=_("Password Confirmation Errors"),
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
    errors: UserResetPasswordConfirmErrorsDetailSerializer = UserResetPasswordConfirmErrorsDetailSerializer(
        help_text=_("Object Containing Validation Errors"),
        label=_("Errors"),
        required=False,
        allow_null=True,
        default=None,
    )


# User Reset Password Unauthorized Error Response Serializer Class
@extend_schema_serializer(
    examples=[
        OpenApiExample(
            name="Invalid Reset Token",
            value={
                "status_code": status.HTTP_401_UNAUTHORIZED,
                "error": "Invalid Password Reset Token",
            },
            summary="Invalid Reset Token",
            description="Invalid Password Reset Token Error Response",
            response_only=True,
            status_codes=[status.HTTP_401_UNAUTHORIZED],
        ),
        OpenApiExample(
            name="Invalid Or Expired Reset Token",
            value={
                "status_code": status.HTTP_401_UNAUTHORIZED,
                "error": "Invalid Or Expired Password Reset Token",
            },
            summary="Invalid Or Expired Reset Token",
            description="Invalid Or Expired Password Reset Token Error Response",
            response_only=True,
            status_codes=[status.HTTP_401_UNAUTHORIZED],
        ),
    ],
)
class UserResetPasswordConfirmUnauthorizedErrorResponseSerializer(GenericResponseSerializer):
    """
    User Reset Password Confirm Unauthorized Error Response Serializer For Standardized API Responses.

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
    "UserResetPasswordConfirmBadRequestErrorResponseSerializer",
    "UserResetPasswordConfirmPayloadSerializer",
    "UserResetPasswordConfirmResponseSerializer",
    "UserResetPasswordConfirmUnauthorizedErrorResponseSerializer",
    "UserResetPasswordRequestAcceptedResponseSerializer",
    "UserResetPasswordRequestBadRequestErrorResponseSerializer",
    "UserResetPasswordRequestPayloadSerializer",
    "UserResetPasswordRequestPayloadSerializer",
]
