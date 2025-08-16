# Standard Library Imports
from typing import Any
from typing import ClassVar

# Third Party Imports
from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _

# Local Imports
from apps.users.forms import UserChangeForm
from apps.users.forms import UserCreationForm
from apps.users.models import User

# Get User Model
User: ClassVar[User] = get_user_model()


# User Admin Class
@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """
    Custom User Admin Class For User Model.

    Attributes:
        form (ClassVar[UserChangeForm]): Form For Changing User.
        add_form (ClassVar[UserCreationForm]): Form For Creating User.
        list_display (ClassVar[list[str]]): Fields To Display In Admin List View.
        list_display_links (ClassVar[list[str]]): Fields That Link To Change View.
        search_fields (ClassVar[list[str]]): Fields That Can Be Searched.
        ordering (ClassVar[list[str]]): Default Ordering For Admin List View.
        readonly_fields (ClassVar[list[str]]): Fields That Cannot Be Modified.
        fieldsets (ClassVar[tuple]): Field Configuration For Change View.
        add_fieldsets (ClassVar[tuple]): Field Configuration For Add View.
    """

    # Form For Changing User
    form: ClassVar[UserChangeForm] = UserChangeForm

    # Form For Creating User
    add_form: ClassVar[UserCreationForm] = UserCreationForm

    # Fields To Display In Admin List View
    list_display: ClassVar[list[str]] = [
        "id",
        "email",
        "first_name",
        "last_name",
        "username",
        "is_active",
        "is_superuser",
    ]

    # Fields That Link To Change View
    list_display_links: ClassVar[list[str]] = ["id", "email", "username"]

    # Fields That Can Be Searched
    search_fields: ClassVar[list[str]] = ["email", "first_name", "last_name"]

    # Default Ordering For Admin List View
    ordering: ClassVar[list[str]] = ["id"]

    # Fields That Cannot Be Modified
    readonly_fields: ClassVar[list[str]] = ["id", "last_login", "date_joined"]

    # Field Configuration For Change View
    fieldsets: ClassVar[tuple[tuple[str, dict[str, Any]], ...]] = (
        ("User ID", {"fields": ("id",)}),
        (_("Login Credentials"), {"fields": ("email", "password")}),
        (
            _("Personal info"),
            {
                "fields": (
                    "first_name",
                    "last_name",
                    "username",
                ),
            },
        ),
        (
            _("Permissions and Groups"),
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                ),
            },
        ),
        (_("Important Dates"), {"fields": ("last_login", "date_joined")}),
    )

    # Field Configuration For Add View
    add_fieldsets: ClassVar[tuple[tuple[str | None, dict[str, Any]], ...]] = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "username",
                    "email",
                    "first_name",
                    "last_name",
                    "password1",
                    "password2",
                ),
            },
        ),
    )


# Exports
__all__: list[str] = ["UserAdmin"]
