# Standard Library Imports
from typing import Any

# Third Party Imports
from django.contrib import admin

# Local Imports
from apps.users.admin.user_admin import UserAdmin
from apps.users.models import User


# Test Admin Registration
def test_user_admin_registered_with_site() -> None:
    """
    Ensure User Model Is Registered With UserAdmin.
    """

    # Get Registered Admin
    registered_admin = admin.site._registry.get(User)

    # Assert Registration
    assert registered_admin is not None
    assert registered_admin.__class__ is UserAdmin


# Test Admin List Configuration
def test_user_admin_list_configuration() -> None:
    """
    Validate List Display, Links, Search, And Ordering.
    """

    # Expected Values
    expected_list_display: list[str] = [
        "id",
        "email",
        "first_name",
        "last_name",
        "username",
        "is_active",
        "is_superuser",
    ]
    expected_list_display_links: list[str] = ["id", "email", "username"]
    expected_search_fields: list[str] = ["email", "first_name", "last_name"]
    expected_ordering: list[str] = ["id"]

    # Assert Values
    assert UserAdmin.list_display == expected_list_display
    assert UserAdmin.list_display_links == expected_list_display_links
    assert UserAdmin.search_fields == expected_search_fields
    assert UserAdmin.ordering == expected_ordering


# Test Admin Readonly Fields
def test_user_admin_readonly_fields() -> None:
    """
    Validate Readonly Fields.
    """

    # Expected Values
    expected_readonly_fields: list[str] = ["id", "last_login", "date_joined"]

    # Assert Values
    assert UserAdmin.readonly_fields == expected_readonly_fields


# Test Fieldsets Structure
def test_user_admin_fieldsets_structure() -> None:
    """
    Validate Fieldsets Titles And Fields.
    """

    # Build Titles
    titles: list[str] = [section[0] for section in UserAdmin.fieldsets]

    # Assert Titles
    assert titles == [
        "User ID",
        "Login Credentials",
        "Personal info",
        "Permissions and Groups",
        "Important Dates",
    ]

    # Extract Fields Per Section
    fields_by_title: dict[str, Any] = {title: cfg["fields"] for title, cfg in UserAdmin.fieldsets}

    # Assert Fields
    assert fields_by_title["User ID"] == ("id",)
    assert fields_by_title["Login Credentials"] == ("email", "password")
    assert fields_by_title["Personal info"] == ("first_name", "last_name", "username")
    assert fields_by_title["Permissions and Groups"] == (
        "is_active",
        "is_staff",
        "is_superuser",
        "groups",
        "user_permissions",
    )
    assert fields_by_title["Important Dates"] == ("last_login", "date_joined")


# Test Add Fieldsets Structure
def test_user_admin_add_fieldsets_structure() -> None:
    """
    Validate Add Fieldsets Titles And Fields.
    """

    # There Should Be A Single Section With None Title
    section = UserAdmin.add_fieldsets[0]
    title, cfg = section

    # Assert Title And Classes
    assert title is None
    assert "classes" in cfg
    assert cfg["classes"] == ("wide",)

    # Assert Fields
    assert cfg["fields"] == (
        "username",
        "email",
        "first_name",
        "last_name",
        "password1",
        "password2",
    )
