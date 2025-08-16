# Standard Library Imports
from typing import ClassVar

# Third Party Imports
import pytest
from django.contrib.auth import get_user_model
from django.test import RequestFactory

# Local Imports
from apps.users.forms.user_change_form import UserChangeForm
from apps.users.forms.user_creation_form import UserCreationForm
from apps.users.models import User

# Get User Model
User: ClassVar[User] = get_user_model()


# User Form Data Fixture
@pytest.fixture
def user_form_data() -> dict[str, str]:
    """
    Create User Form Data For Testing.

    Returns:
        dict[str, str]: Dictionary With User Form Data.
    """

    # Return Form Data
    return {
        "first_name": "John",
        "last_name": "Doe",
        "username": "johndoe",
        "email": "john.doe@example.com",
    }


# User Creation Form Data Fixture
@pytest.fixture
def user_creation_form_data(user_form_data: dict[str, str]) -> dict[str, str]:
    """
    Create User Creation Form Data For Testing.

    Args:
        user_form_data (dict[str, str]): Base User Form Data.

    Returns:
        dict[str, str]: Dictionary With User Creation Form Data.
    """

    # Add Password Fields
    user_form_data.update(
        {
            "password1": "StrongP@ssw0rd",
            "password2": "StrongP@ssw0rd",
        },
    )

    # Return Form Data
    return user_form_data


# User Change Form Fixture
@pytest.fixture
def user_change_form(user_form_data: dict[str, str]) -> UserChangeForm:
    """
    Create User Change Form Instance For Testing.

    Args:
        user_form_data (dict[str, str]): User Form Data.

    Returns:
        UserChangeForm: User Change Form Instance.
    """

    # Create Form
    return UserChangeForm(data=user_form_data)


# User Creation Form Fixture
@pytest.fixture
def user_creation_form(user_creation_form_data: dict[str, str]) -> UserCreationForm:
    """
    Create User Creation Form Instance For Testing.

    Args:
        user_creation_form_data (dict[str, str]): User Creation Form Data.

    Returns:
        UserCreationForm: User Creation Form Instance.
    """

    # Create Form
    return UserCreationForm(data=user_creation_form_data)


# User Instance Fixture
@pytest.fixture
def user_instance() -> User:
    """
    Create User Instance For Testing.

    Returns:
        User: User Instance.
    """

    # Create & Return User
    return User.objects.create_user(
        first_name="Jane",
        last_name="Smith",
        username="janesmith",
        email="jane.smith@example.com",
        password="AnotherStr0ngP@ss",
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


# User Change Form With Instance Fixture
@pytest.fixture
def user_change_form_with_instance(user_instance: User) -> UserChangeForm:
    """
    Create User Change Form With User Instance For Testing.

    Args:
        user_instance (User): User Instance.

    Returns:
        UserChangeForm: User Change Form Instance With User Instance.
    """

    # Create Form
    return UserChangeForm(instance=user_instance)


# Mixed Case Form Data Fixture
@pytest.fixture
def mixed_case_form_data() -> dict[str, str]:
    """
    Create Form Data With Mixed Case For Testing.

    Returns:
        dict[str, str]: Dictionary With Mixed Case Form Data.
    """

    # Return Form Data
    return {
        "first_name": "jOhN",
        "last_name": "dOe",
        "username": "JohnDoe",
        "email": "John.Doe@Example.COM",
    }
