# Third Party Imports
from django.utils.translation import gettext_lazy as _
from drf_spectacular.utils import OpenApiExample
from drf_spectacular.utils import extend_schema_serializer
from rest_framework import serializers
from rest_framework import status


# Generic Response Serializer Class
class GenericResponseSerializer(serializers.Serializer):
    """
    Generic Response Serializer For Standardized API Responses.

    Attributes:
        status_code (int): HTTP Status Code For The Response.
    """

    # Status Code Field
    status_code: serializers.IntegerField = serializers.IntegerField(
        help_text=_("Status Code"),
        label=_("Status Code"),
        required=True,
        allow_null=False,
        error_messages={
            "required": _("Status Code Is Required"),
            "null": _("Status Code Cannot Be Null"),
        },
    )


# Generic 500 Response Serializer Class
@extend_schema_serializer(
    examples=[
        OpenApiExample(
            name="Internal Server Error Example",
            value={
                "status_code": status.HTTP_500_INTERNAL_SERVER_ERROR,
                "error": "Internal Server Error",
            },
            summary="Internal Server Error Example",
            description="Internal Server Error Example",
            response_only=True,
            status_codes=[status.HTTP_500_INTERNAL_SERVER_ERROR],
        ),
    ],
)
class Generic500ResponseSerializer(GenericResponseSerializer):
    """
    Generic 500 Response Serializer For Standardized API Responses.

    Attributes:
        status_code (int): HTTP Status Code For The Response.
        error (str): Error Message For The Response.
    """

    # Error Field
    error: serializers.CharField = serializers.CharField(
        help_text=_("Error Message For The Response"),
        label=_("Error Message"),
        default="Internal Server Error",
    )


# Exports
__all__: list[str] = ["Generic500ResponseSerializer", "GenericResponseSerializer"]
