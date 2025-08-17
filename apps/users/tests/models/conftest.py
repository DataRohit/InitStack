# Standard Library Imports
from typing import Any

# Third Party Imports
import pytest
from django.contrib.auth import get_user_model
from django.test import RequestFactory

# Local Imports
from apps.users.models import User

# Get User Model
User: User = get_user_model()


# User Factory Fixture
@pytest.fixture
def user_factory() -> dict[str, Any]:
    """
    User Factory Fixture.

    Returns:
        dict[str, Any]: User Factory Dictionary.
    """

    # Return User Factory
    return {
        "username": "testuser",
        "email": "test@example.com",
        "first_name": "Test",
        "last_name": "User",
        "password": "TestPass123!",
    }


# User Instance Fixture
@pytest.fixture
def user_instance(user_factory: dict[str, Any]) -> User:
    """
    User Instance Fixture.

    Args:
        user_factory (dict[str, Any]): User Factory Dictionary.

    Returns:
        User: User Instance.
    """

    # Create User
    user: User = User.objects.create_user(**user_factory)

    # Return User
    return user


# Superuser Factory Fixture
@pytest.fixture
def superuser_factory() -> dict[str, Any]:
    """
    Superuser Factory Fixture.

    Returns:
        dict[str, Any]: Superuser Factory Dictionary.
    """

    # Return Superuser Factory
    return {
        "username": "testsuperuser",
        "email": "superuser@example.com",
        "first_name": "Super",
        "last_name": "User",
        "password": "SuperPass123!",
    }


# Superuser Instance Fixture
@pytest.fixture
def superuser_instance(superuser_factory: dict[str, Any]) -> User:
    """
    Superuser Instance Fixture.

    Args:
        superuser_factory (dict[str, Any]): Superuser Factory Dictionary.

    Returns:
        User: Superuser Instance.
    """

    # Create Superuser
    superuser: User = User.objects.create_superuser(**superuser_factory)

    # Return Superuser
    return superuser


# Request Factory Fixture
@pytest.fixture
def request_factory() -> RequestFactory:
    """
    Request Factory Fixture.

    Returns:
        RequestFactory: Django Request Factory.
    """

    # Return Request Factory
    return RequestFactory()


# Clean Up Database Fixture
@pytest.fixture(autouse=True)
def clean_up_database() -> None:
    """
    Clean Up Database Fixture.

    Returns:
        None
    """

    # Yield Control
    yield

    # Clean Up Users
    User.objects.all().delete()
