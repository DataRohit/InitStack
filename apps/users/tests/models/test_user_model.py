# Standard Library Imports
import datetime
import time
import uuid
from typing import TYPE_CHECKING
from typing import Any

# Third Party Imports
import pytest
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.utils import timezone

# Local Imports
from apps.users.models import User

# If Type Checking
if TYPE_CHECKING:
    # Third Party Imports
    from django.db import models

# Get User Model
User: User = get_user_model()

# Enable Django DB Access For All Tests In This Module
pytestmark = pytest.mark.django_db


# Test User Model Fields
def test_user_model_fields() -> None:
    """
    Test User Model Fields.
    """

    # Get User Model Fields
    fields: dict[str, models.Field] = User._meta.fields

    # Get Field Names
    field_names: list[str] = [field.name for field in fields]

    # Assert Required Fields Exist
    assert "id" in field_names
    assert "username" in field_names
    assert "email" in field_names
    assert "first_name" in field_names
    assert "last_name" in field_names
    assert "password" in field_names
    assert "created_at" in field_names
    assert "updated_at" in field_names


# Test User Model Meta
def test_user_model_meta() -> None:
    """
    Test User Model Meta.
    """

    # Get User Model Meta
    meta = User._meta

    # Assert Meta Attributes
    assert meta.verbose_name == "User"
    assert meta.verbose_name_plural == "Users"
    assert meta.ordering == ["-date_joined"]
    assert meta.db_table == "users_user"


# Test User Model Authentication Fields
def test_user_model_authentication_fields() -> None:
    """
    Test User Model Authentication Fields.
    """

    # Assert Authentication Fields
    assert User.EMAIL_FIELD == "email"
    assert User.USERNAME_FIELD == "email"
    assert "username" in User.REQUIRED_FIELDS
    assert "first_name" in User.REQUIRED_FIELDS
    assert "last_name" in User.REQUIRED_FIELDS


# Test User Creation
def test_user_creation(user_factory: dict[str, Any]) -> None:
    """
    Test User Creation.

    Args:
        user_factory (dict[str, Any]): User Factory Dictionary.
    """

    # Wait For A Second
    time.sleep(1)

    # Create User
    user: User = User.objects.create_user(**user_factory)

    # Assert User Is Created
    assert user.username == user_factory["username"]
    assert user.email == user_factory["email"]
    assert user.first_name == user_factory["first_name"]
    assert user.last_name == user_factory["last_name"]
    assert user.check_password(user_factory["password"])


# Test Superuser Creation
def test_superuser_creation(superuser_factory: dict[str, Any]) -> None:
    """
    Test Superuser Creation.

    Args:
        superuser_factory (dict[str, Any]): Superuser Factory Dictionary.
    """

    # Create Superuser
    superuser: User = User.objects.create_superuser(**superuser_factory)

    # Assert Superuser Is Created
    assert superuser.username == superuser_factory["username"]
    assert superuser.email == superuser_factory["email"]
    assert superuser.first_name == superuser_factory["first_name"]
    assert superuser.last_name == superuser_factory["last_name"]
    assert superuser.check_password(superuser_factory["password"])
    assert superuser.is_staff
    assert superuser.is_superuser


# Test Full Name Property
def test_full_name_property(user_instance: User) -> None:
    """
    Test Full Name Property.

    Args:
        user_instance (User): User Instance.
    """

    # Assert Full Name
    assert user_instance.full_name == "Test User"


# Test Full Name Property With Spaces
def test_full_name_property_with_spaces() -> None:
    """
    Test Full Name Property With Spaces.
    """

    # Create User With Spaces In Names
    user: User = User.objects.create_user(
        username="spacesuser",
        email="spaces@example.com",
        first_name="  Test  ",
        last_name="  User  ",
        password="TestPass123!",
    )

    # Assert Full Name Is Stripped
    assert user.full_name == "Test User"


# Test Username Validation
def test_username_validation() -> None:
    """
    Test Username Validation.
    """

    # Create User With Invalid Username
    user: User = User.objects.create_user(
        username="invalid username",
        email="invalid@example.com",
        first_name="Invalid",
        last_name="User",
        password="InvalidPass123!",
    )
    with pytest.raises(ValidationError):
        user.full_clean()

    # Create User With Long Username
    user = User.objects.create_user(
        username="a" * 61,
        email="long@example.com",
        first_name="Long",
        last_name="User",
        password="LongPass123!",
    )
    with pytest.raises(ValidationError):
        user.full_clean()


# Test Email Validation
def test_email_validation() -> None:
    """
    Test Email Validation.
    """

    # Create User With Invalid Email
    user: User = User.objects.create_user(
        username="invalidemail",
        email="invalid",
        first_name="Invalid",
        last_name="Email",
        password="InvalidPass123!",
    )
    with pytest.raises(ValidationError):
        user.full_clean()


# Test First Name Validation
def test_first_name_validation() -> None:
    """
    Test First Name Validation.
    """

    # Create User With Invalid First Name
    user: User = User.objects.create_user(
        username="invalidfirstname",
        email="firstname@example.com",
        first_name="Invalid123",
        last_name="User",
        password="InvalidPass123!",
    )
    with pytest.raises(ValidationError):
        user.full_clean()

    # Create User With Long First Name
    user = User.objects.create_user(
        username="longfirstname",
        email="longfirst@example.com",
        first_name="A" * 61,
        last_name="User",
        password="LongPass123!",
    )
    with pytest.raises(ValidationError):
        user.full_clean()


# Test Last Name Validation
def test_last_name_validation() -> None:
    """
    Test Last Name Validation.
    """

    # Create User With Invalid Last Name
    user: User = User.objects.create_user(
        username="invalidlastname",
        email="lastname@example.com",
        first_name="Invalid",
        last_name="User123",
        password="InvalidPass123!",
    )
    with pytest.raises(ValidationError):
        user.full_clean()

    # Create User With Long Last Name
    user = User.objects.create_user(
        username="longlastname",
        email="longlast@example.com",
        first_name="User",
        last_name="A" * 61,
        password="LongPass123!",
    )
    with pytest.raises(ValidationError):
        user.full_clean()


# Test Case Formatting
def test_case_formatting() -> None:
    """
    Test Case Formatting.
    """

    # Create User With Mixed Case
    user: User = User.objects.create_user(
        username="MixedCase",
        email="MixedCase@example.com",
        first_name="miXed",
        last_name="caSe",
        password="MixedCase123!",
    )

    # Assert Case Formatting
    assert user.username == "mixedcase"
    assert user.email == "mixedcase@example.com"
    assert user.first_name == "Mixed"
    assert user.last_name == "Case"


# Test Whitespace Stripping
def test_whitespace_stripping() -> None:
    """
    Test Whitespace Stripping.
    """

    # Create User With Whitespace
    user: User = User.objects.create_user(
        username="  whitespace  ",
        email="  whitespace@example.com  ",
        first_name="  Whitespace  ",
        last_name="  Test  ",
        password="Whitespace123!",
    )

    # Assert Whitespace Stripping
    assert user.username == "whitespace"
    assert user.email == "whitespace@example.com"
    assert user.first_name == "Whitespace"
    assert user.last_name == "Test"


# Test Extra Fields
def test_extra_fields() -> None:
    """
    Test Extra Fields.
    """

    # Create User With Extra Fields
    user: User = User.objects.create_user(
        username="extrafields",
        email="extra@example.com",
        first_name="Extra",
        last_name="Fields",
        password="ExtraFields123!",
        is_active=False,
        date_joined=timezone.make_aware(datetime.datetime(2023, 1, 1)),
    )

    # Assert Extra Fields
    assert not user.is_active
    assert user.date_joined == timezone.make_aware(
        datetime.datetime(2023, 1, 1),
    )


# Test Superuser Extra Fields
def test_superuser_extra_fields() -> None:
    """
    Test Superuser Extra Fields.
    """

    # Create Superuser With Extra Fields
    superuser: User = User.objects.create_superuser(
        username="superextra",
        email="superextra@example.com",
        first_name="Super",
        last_name="Extra",
        password="SuperExtra123!",
        is_active=False,
        date_joined=timezone.make_aware(datetime.datetime(2023, 1, 1)),
    )

    # Assert Extra Fields
    assert not superuser.is_active
    assert superuser.date_joined == timezone.make_aware(
        datetime.datetime(2023, 1, 1),
    )
    assert superuser.is_staff
    assert superuser.is_superuser


# Test UUID Primary Key
def test_uuid_primary_key(user_instance: User) -> None:
    """
    Test UUID Primary Key.

    Args:
        user_instance (User): User Instance.
    """

    # Assert UUID Primary Key
    assert user_instance.id is not None
    assert isinstance(user_instance.id, uuid.UUID)


# Test Timestamp Fields
def test_timestamp_fields(user_instance: User) -> None:
    """
    Test Timestamp Fields.

    Args:
        user_instance (User): User Instance.
    """

    # Assert Timestamp Fields
    assert user_instance.created_at is not None
    assert user_instance.updated_at is not None
    assert isinstance(user_instance.created_at, datetime.datetime)
    assert isinstance(user_instance.updated_at, datetime.datetime)


# Test Updated At Field Updates
def test_updated_at_field_updates(user_instance: User) -> None:
    """
    Test Updated At Field Updates.

    Args:
        user_instance (User): User Instance.
    """

    # Get Initial Updated At
    initial_updated_at = user_instance.updated_at

    # Update User
    user_instance.first_name = "Updated"
    user_instance.save()

    # Refresh From Database
    user_instance.refresh_from_db()

    # Assert Updated At Is Updated
    assert user_instance.updated_at > initial_updated_at


# Test User String Representation
def test_user_string_representation(user_instance: User) -> None:
    """
    Test User String Representation.

    Args:
        user_instance (User): User Instance.
    """

    # Assert String Representation
    assert str(user_instance) == user_instance.email
