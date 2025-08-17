# Standard Library Imports
from collections.abc import Generator
from typing import Any

# Third Party Imports
import pytest
from django.contrib.auth import get_user_model
from django.contrib.auth.models import UserManager as DjangoUserManager
from django.test import RequestFactory

# Local Imports
from apps.users.managers.user_manager import UserManager
from apps.users.models import User

# Get User Model
User: User = get_user_model()


# User Manager Fixture
@pytest.fixture
def user_manager() -> UserManager:
    """
    Create User Manager Instance For Testing.

    Returns:
        UserManager: User Manager Instance.
    """

    # Return User Manager
    return UserManager()


# Django User Manager Fixture
@pytest.fixture
def django_user_manager() -> DjangoUserManager:
    """
    Create Django User Manager Instance For Testing.

    Returns:
        DjangoUserManager: Django User Manager Instance.
    """

    # Return Django User Manager
    return DjangoUserManager()


# User Data Fixture
@pytest.fixture
def user_data() -> dict[str, Any]:
    """
    Create User Data For Testing.

    Returns:
        dict[str, Any]: Dictionary With User Data.
    """

    # Return User Data
    return {
        "first_name": "John",
        "last_name": "Doe",
        "username": "johndoe",
        "email": "john.doe@example.com",
        "password": "StrongP@ssw0rd",
    }


# Superuser Data Fixture
@pytest.fixture
def superuser_data() -> dict[str, Any]:
    """
    Create Superuser Data For Testing.

    Returns:
        dict[str, Any]: Dictionary With Superuser Data.
    """

    # Return Superuser Data
    return {
        "first_name": "Admin",
        "last_name": "User",
        "username": "adminuser",
        "email": "admin@example.com",
        "password": "AdminP@ssw0rd",
        "is_staff": True,
        "is_superuser": True,
    }


# User Instance Fixture
@pytest.fixture
def user_instance(user_data: dict[str, Any]) -> User:
    """
    Create User Instance For Testing.

    Args:
        user_data (dict[str, Any]): User Data.

    Returns:
        User: User Instance.
    """

    # Create & Return User
    return User.objects.create_user(
        first_name=user_data["first_name"],
        last_name=user_data["last_name"],
        username=user_data["username"],
        email=user_data["email"],
        password=user_data["password"],
    )


# Superuser Instance Fixture
@pytest.fixture
def superuser_instance(superuser_data: dict[str, Any]) -> User:
    """
    Create Superuser Instance For Testing.

    Args:
        superuser_data (dict[str, Any]): Superuser Data.

    Returns:
        User: Superuser Instance.
    """

    # Create & Return Superuser
    return User.objects.create_superuser(
        first_name=superuser_data["first_name"],
        last_name=superuser_data["last_name"],
        username=superuser_data["username"],
        email=superuser_data["email"],
        password=superuser_data["password"],
    )


# Request Factory Fixture
@pytest.fixture
def request_factory() -> RequestFactory:
    """
    Create Request Factory For Testing.

    Returns:
        RequestFactory: Django Request Factory Instance.
    """

    # Return Request Factory
    return RequestFactory()


# DB Cleanup Fixture
@pytest.fixture(autouse=True)
def cleanup_db(db: Any) -> Generator[None]:
    """
    Clean Up Database After Each Test.

    Args:
        db (Any): Database Fixture.

    Yields:
        Generator[None]: Generator For Test Execution.
    """

    # Setup Before Test
    yield

    # Cleanup After Test
    User.objects.all().delete()
