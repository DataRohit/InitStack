# Standard Library Imports
from typing import TYPE_CHECKING
from unittest.mock import MagicMock
from unittest.mock import patch

# Third Party Imports
import pytest
from django.contrib.auth import get_user_model
from django.contrib.sites.models import Site
from rest_framework import status
from rest_framework.test import APIRequestFactory

# Local Imports
from apps.users.views.user_register_view import UserRegisterView

# If Type Checking
if TYPE_CHECKING:
    # Third Party Imports
    from rest_framework.request import Request

# Get User Model
User = get_user_model()

# Enable Django DB Access For All Tests In This Module
pytestmark = pytest.mark.django_db


# 400 Invalid Payload Test
def test_user_register_invalid_payload_returns_400() -> None:
    """
    Empty Payload Should Yield 400 With Errors.
    """

    # Request
    factory: APIRequestFactory = APIRequestFactory()
    request: Request = factory.post("/api/users/register/", data={}, format="json")

    # Patch Metrics
    with (
        patch("apps.users.views.user_register_view.record_http_request") as rec_http,
        patch("apps.users.views.user_register_view.record_user_action") as rec_action,
    ):
        response = UserRegisterView.as_view()(request)

    # Assert
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "errors" in response.data
    rec_http.assert_not_called()
    rec_action.assert_not_called()


# 400 Username Exists Test
def test_user_register_username_exists_returns_400() -> None:
    """
    Existing Username Should Yield 400 With Error.
    """

    # Existing User
    User.objects.create_user(
        username="takenuser",
        email="taken@example.com",
        first_name="Taken",
        last_name="User",
        password="SecurePassword@123",
        is_active=False,
    )

    # Request
    factory: APIRequestFactory = APIRequestFactory()
    request: Request = factory.post(
        "/api/users/register/",
        data={
            "username": "takenuser",
            "email": "new@example.com",
            "first_name": "New",
            "last_name": "User",
            "password": "SecurePassword@123",
            "re_password": "SecurePassword@123",
        },
        format="json",
    )

    # Execute
    response = UserRegisterView.as_view()(request)

    # Assert
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.data == {"errors": {"username": ["Username Already Exists"]}}


# 400 Email Exists Test
def test_user_register_email_exists_returns_400() -> None:
    """
    Existing Email Should Yield 400 With Error.
    """

    # Existing User
    User.objects.create_user(
        username="uniqueuser",
        email="exists@example.com",
        first_name="Exists",
        last_name="User",
        password="SecurePassword@123",
        is_active=False,
    )

    # Request
    factory: APIRequestFactory = APIRequestFactory()
    request: Request = factory.post(
        "/api/users/register/",
        data={
            "username": "anotheruser",
            "email": "exists@example.com",
            "first_name": "New",
            "last_name": "User",
            "password": "SecurePassword@123",
            "re_password": "SecurePassword@123",
        },
        format="json",
    )

    # Execute
    response = UserRegisterView.as_view()(request)

    # Assert
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.data == {"errors": {"email": ["Email Already Exists"]}}


# 201 Success Test
def test_user_register_success_returns_201_sends_email_and_records_metrics() -> None:
    """
    Valid Registration Should Return 201, Cache Token, Send Email, And Record Metrics.
    """

    # Request
    factory: APIRequestFactory = APIRequestFactory()
    request: Request = factory.post(
        "/api/users/register/",
        data={
            "username": "newuser",
            "email": "newuser@example.com",
            "first_name": "New",
            "last_name": "User",
            "password": "SecurePassword@123",
            "re_password": "SecurePassword@123",
        },
        format="json",
    )

    # Cache Mock
    token_cache: MagicMock = MagicMock()
    cache_mapping: dict[str, MagicMock] = {"token_cache": token_cache}

    # Site Mock
    site_mock: MagicMock = MagicMock(spec=Site)
    site_mock.domain = "example.com"

    # Patch Dependencies
    with (
        patch("apps.users.views.user_register_view.caches", cache_mapping),
        patch("apps.users.views.user_register_view.Site.objects.get_current", return_value=site_mock),
        patch("apps.users.views.user_register_view.send_mail") as send_mail_mock,
        patch("apps.users.views.user_register_view.record_cache_operation") as rec_cache,
        patch("apps.users.views.user_register_view.record_activation_token_generated") as rec_tok_gen,
        patch("apps.users.views.user_register_view.record_email_template_render_duration") as rec_tpl,
        patch("apps.users.views.user_register_view.record_email_sent") as rec_email,
        patch("apps.users.views.user_register_view.record_register_initiated") as rec_init,
        patch("apps.users.views.user_register_view.record_http_request") as rec_http,
        patch("apps.users.views.user_register_view.record_user_action") as rec_action,
    ):
        response = UserRegisterView.as_view()(request)

    # Assert
    assert response.status_code == status.HTTP_201_CREATED
    assert response.data["username"] == "newuser"
    assert response.data["email"] == "newuser@example.com"

    # Side Effects
    token_cache.set.assert_called_once()
    send_mail_mock.assert_called_once()

    # Metrics
    rec_cache.assert_called()
    rec_tok_gen.assert_called_once()
    rec_tpl.assert_called()
    rec_email.assert_called()
    rec_init.assert_called_once()
    rec_http.assert_called()
    rec_action.assert_called()


# 500 Internal Error Test
def test_user_register_internal_error_returns_500_records_metrics() -> None:
    """
    Unexpected Exception During Email Send Should Yield 500 And Record Metrics.
    """

    # Request
    factory: APIRequestFactory = APIRequestFactory()
    request: Request = factory.post(
        "/api/users/register/",
        data={
            "username": "boom",
            "email": "boom@example.com",
            "first_name": "Boom",
            "last_name": "User",
            "password": "SecurePassword@123",
            "re_password": "SecurePassword@123",
        },
        format="json",
    )

    # Cache Mock
    token_cache: MagicMock = MagicMock()
    cache_mapping: dict[str, MagicMock] = {"token_cache": token_cache}

    # Site Mock
    site_mock: MagicMock = MagicMock(spec=Site)
    site_mock.domain = "example.com"

    # Patch Dependencies And Force send_mail Error
    with (
        patch("apps.users.views.user_register_view.caches", cache_mapping),
        patch("apps.users.views.user_register_view.Site.objects.get_current", return_value=site_mock),
        patch("apps.users.views.user_register_view.send_mail", side_effect=Exception("boom")),
        patch("apps.users.views.user_register_view.record_api_error") as rec_api_error,
        patch("apps.users.views.user_register_view.record_http_request") as rec_http,
        patch("apps.users.views.user_register_view.record_user_action") as rec_action,
    ):
        response = UserRegisterView.as_view()(request)

    # Assert
    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert response.data == {"error": "Internal Server Error"}

    # Metrics
    rec_api_error.assert_called()
    rec_http.assert_called()
    rec_action.assert_called_with(action_type="register", success=False)
