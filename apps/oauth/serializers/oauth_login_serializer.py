# Third Party Imports
from django.utils.translation import gettext_lazy as _
from drf_spectacular.utils import OpenApiExample
from drf_spectacular.utils import extend_schema_serializer
from rest_framework import serializers
from rest_framework import status

# Local Imports
from apps.common.serializers.generic_response_serializer import GenericResponseSerializer


# OAuth Login Response Serializer Class
@extend_schema_serializer(
    examples=[
        OpenApiExample(
            name="OAuth Login Response Example",
            value={
                "status_code": status.HTTP_200_OK,
                "data": {
                    "auth_url": "https://example.com/api/users/oauth/<provider>/callback/",
                },
            },
            summary="OAuth Login Response Example",
            description="OAuth Login Response Example",
            response_only=True,
            status_codes=[status.HTTP_200_OK],
        ),
    ],
)
class OAuthLoginResponseSerializer(GenericResponseSerializer):
    """
    OAuth Login Response Serializer For Standardized API Responses.

    Attributes:
        status_code (int): HTTP Status Code For The Response.
        data (OAuthAuthURLSerializer): OAuth Auth URL For The Response.
    """

    # OAuth Auth URL Serializer
    class OAuthAuthURLSerializer(serializers.Serializer):
        """
        OAuth Auth URL Serializer For Standardized API Responses.

        Attributes:
            auth_url (str): OAuth Auth URL For The Response.
        """

        # Auth URL Field
        auth_url: serializers.CharField = serializers.CharField(
            help_text=_("OAuth Auth URL"),
            label=_("OAuth Auth URL"),
            required=True,
            allow_null=False,
            error_messages={
                "required": _("OAuth Auth URL Is Required"),
                "null": _("OAuth Auth URL Cannot Be Null"),
            },
        )

    # Data Field
    data: OAuthAuthURLSerializer = OAuthAuthURLSerializer(
        help_text=_("OAuth Auth URL"),
        label=_("OAuth Auth URL"),
        required=True,
        allow_null=False,
        error_messages={
            "required": _("OAuth Auth URL Is Required"),
            "null": _("OAuth Auth URL Cannot Be Null"),
        },
    )
