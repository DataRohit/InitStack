# Third Party Imports
from django.utils.translation import gettext_lazy as _
from drf_spectacular.utils import OpenApiExample
from drf_spectacular.utils import extend_schema_serializer
from rest_framework import serializers
from rest_framework import status

# Local Imports
from apps.common.serializers.generic_response_serializer import GenericResponseSerializer

# OAuth Auth URL Text
OAUTH_AUTH_URL_TEXT: str = "OAuth Auth URL"

# OAuth Auth URL Label
OAUTH_AUTH_URL_LABEL: str = _(OAUTH_AUTH_URL_TEXT)


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
            help_text=OAUTH_AUTH_URL_LABEL,
            label=OAUTH_AUTH_URL_LABEL,
            required=True,
            allow_null=False,
            error_messages={
                "required": _("OAuth Auth URL Is Required"),
                "null": _("OAuth Auth URL Cannot Be Null"),
            },
        )

    # Data Field
    data: OAuthAuthURLSerializer = OAuthAuthURLSerializer(
        help_text=OAUTH_AUTH_URL_LABEL,
        label=OAUTH_AUTH_URL_LABEL,
        required=True,
        allow_null=False,
        error_messages={
            "required": _("OAuth Auth URL Is Required"),
            "null": _("OAuth Auth URL Cannot Be Null"),
        },
    )


# Exports
__all__: list[str] = ["OAuthLoginResponseSerializer"]
