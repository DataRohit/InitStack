# Standard Library Imports
from typing import ClassVar

# Third Party Imports
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from drf_spectacular.utils import OpenApiExample
from drf_spectacular.utils import extend_schema_serializer
from rest_framework import serializers
from rest_framework import status

# Get User Model
User = get_user_model()


# User Detail Serializer Class
@extend_schema_serializer(
    examples=[
        OpenApiExample(
            name="User Detail Example",
            value={
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "username": "john_doe",
                "email": "john.doe@example.com",
                "first_name": "John",
                "last_name": "Doe",
                "is_active": True,
                "is_staff": False,
                "is_superuser": False,
                "date_joined": "2025-08-16T19:04:06.602446+05:30",
                "last_login": "2025-08-16T19:04:08.602446+05:30",
            },
            summary="User Detail Example",
            description="User Detail Example",
            response_only=True,
            status_codes=[status.HTTP_200_OK],
        ),
    ],
)
class UserDetailSerializer(serializers.ModelSerializer):
    """
    User Detail Serializer For Representing User Information.

    Attributes:
        id (serializers.UUIDField): User ID Field.
        username (serializers.CharField): User Username Field.
        email (serializers.EmailField): User Email Field.
        first_name (serializers.CharField): User First Name Field.
        last_name (serializers.CharField): User Last Name Field.
        is_active (serializers.BooleanField): User Active Status Field.
        is_staff (serializers.BooleanField): User Staff Status Field.
        is_superuser (serializers.BooleanField): User Superuser Status Field.
        date_joined (serializers.DateTimeField): User Date Joined Field.
        last_login (serializers.DateTimeField): User Last Login Field.
    """

    # ID Field
    id: serializers.UUIDField = serializers.UUIDField(
        help_text=_("User ID"),
        label=_("User ID"),
        required=True,
        allow_null=False,
        error_messages={
            "required": _("User ID Is Required"),
            "null": _("User ID Cannot Be Null"),
        },
    )

    # Username Field
    username: serializers.CharField = serializers.CharField(
        help_text=_("User Username"),
        label=_("Username"),
        required=True,
        allow_null=False,
        error_messages={
            "required": _("User Username Is Required"),
            "null": _("User Username Cannot Be Null"),
        },
    )

    # Email Field
    email: serializers.EmailField = serializers.EmailField(
        help_text=_("User Email"),
        label=_("Email"),
        required=True,
        allow_null=False,
        error_messages={
            "required": _("User Email Is Required"),
            "null": _("User Email Cannot Be Null"),
        },
    )

    # First Name Field
    first_name: serializers.CharField = serializers.CharField(
        help_text=_("User First Name"),
        label=_("First Name"),
        required=True,
        allow_null=False,
        error_messages={
            "required": _("User First Name Is Required"),
            "null": _("User First Name Cannot Be Null"),
        },
    )

    # Last Name Field
    last_name: serializers.CharField = serializers.CharField(
        help_text=_("User Last Name"),
        label=_("Last Name"),
        required=True,
        allow_null=False,
        error_messages={
            "required": _("User Last Name Is Required"),
            "null": _("User Last Name Cannot Be Null"),
        },
    )

    # Is Active Field
    is_active: serializers.BooleanField = serializers.BooleanField(
        help_text=_("User Active Status"),
        label=_("Active"),
        required=True,
        allow_null=False,
        error_messages={
            "required": _("User Active Status Is Required"),
            "null": _("User Active Status Cannot Be Null"),
        },
    )

    # Is Staff Field
    is_staff: serializers.BooleanField = serializers.BooleanField(
        help_text=_("User Staff Status"),
        label=_("Staff"),
        required=True,
        allow_null=False,
        error_messages={
            "required": _("User Staff Status Is Required"),
            "null": _("User Staff Status Cannot Be Null"),
        },
    )

    # Is Superuser Field
    is_superuser: serializers.BooleanField = serializers.BooleanField(
        help_text=_("User Superuser Status"),
        label=_("Superuser"),
        required=True,
        allow_null=False,
        error_messages={
            "required": _("User Superuser Status Is Required"),
            "null": _("User Superuser Status Cannot Be Null"),
        },
    )

    # Date Joined Field
    date_joined: serializers.DateTimeField = serializers.DateTimeField(
        help_text=_("User Date Joined"),
        label=_("Date Joined"),
        required=True,
        allow_null=False,
        error_messages={
            "required": _("User Date Joined Is Required"),
            "null": _("User Date Joined Cannot Be Null"),
        },
    )

    # Last Login Field
    last_login: serializers.DateTimeField = serializers.DateTimeField(
        help_text=_("User Last Login"),
        label=_("Last Login"),
        required=False,
        allow_null=False,
        error_messages={
            "null": _("User Last Login Cannot Be Null"),
        },
    )

    # Meta Class
    class Meta:
        """
        Meta Class For User Detail Serializer.

        Attributes:
            model (ClassVar[User]): User Model Class.
            fields (ClassVar[list[str]]): Fields To Include In Serialization.
        """

        # Set Model
        model: ClassVar[User] = User

        # Set Fields
        fields: ClassVar[list[str]] = [
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "full_name",
            "is_active",
            "is_staff",
            "is_superuser",
            "date_joined",
            "last_login",
        ]


# Exports
__all__: list[str] = ["UserDetailSerializer"]
