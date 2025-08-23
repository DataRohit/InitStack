# ruff: noqa: S105

# Standard Library Imports
from typing import TYPE_CHECKING
from typing import Any
from unittest.mock import MagicMock
from unittest.mock import patch

# Third Party Imports
import jwt
import pytest
from django.conf import settings
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APIRequestFactory

# Local Imports
from apps.users.views.user_activate_view import UserActivateView

# If Type Checking
if TYPE_CHECKING:
    # Third Party Imports
    from rest_framework.request import Request

# Get User Model
User = get_user_model()

# Enable Django DB Access For All Tests In This Module
pytestmark = pytest.mark.django_db


# Build Token Cache Mock Function
def _build_token_cache_mock(expected_token: str | None) -> MagicMock:
    """
    Build Token Cache Mock.

    Args:
        expected_token (str | None): Token Value To Return For Get.

    Returns:
        MagicMock: Mocked Cache With Get/Delete.
    """

    # Create Mock
    token_cache: MagicMock = MagicMock()

    # Configure Get
    token_cache.get.return_value = expected_token

    # Return Mock
    return token_cache


# Successful Activation Test
def test_user_activate_view_success() -> None:
    """
    Verify View Activates User And Sends Email.
    """

    # Create Inactive User
    user = User.objects.create_user(
        username="activate_me",
        email="activate@example.com",
        first_name="Act",
        last_name="Ivate",
        password="SecurePassword@123",
        is_active=False,
    )

    # Inputs
    token: str = "valid.token.value"
    payload: dict[str, Any] = {"sub": str(user.id)}

    # Build Request
    factory: APIRequestFactory = APIRequestFactory()
    request: Request = factory.get("/api/users/activate/<token>/")

    # Build Cache Mapping
    token_cache: MagicMock = _build_token_cache_mock(expected_token=token)
    cache_mapping: dict[str, Any] = {"token_cache": token_cache}

    # Patch Dependencies
    with (
        patch.object(settings, "ACTIVATION_TOKEN_SECRET", "secret"),
        patch.object(settings, "DEFAULT_FROM_EMAIL", "noreply@example.com"),
        patch.object(settings, "PROJECT_NAME", "InitStack"),
        patch("apps.users.views.user_activate_view.caches", cache_mapping),
        patch("apps.users.views.user_activate_view.jwt.decode", return_value=payload),
        patch("apps.users.views.user_activate_view.Site.objects.get_current") as mock_get_current,
        patch("apps.users.views.user_activate_view.render_to_string", return_value="<html>ok</html>"),
        patch("apps.users.views.user_activate_view.send_mail") as mock_send_mail,
        patch("apps.users.views.user_activate_view.record_token_validation") as rec_token,
        patch("apps.users.views.user_activate_view.record_cache_operation") as rec_cache,
        patch("apps.users.views.user_activate_view.record_user_update") as rec_update,
        patch("apps.users.views.user_activate_view.record_user_action") as rec_action,
        patch("apps.users.views.user_activate_view.record_http_request") as rec_http,
        patch("apps.users.views.user_activate_view.record_email_sent"),
        patch("apps.users.views.user_activate_view.record_activation_completed"),
    ):
        # Configure Site
        site_mock: MagicMock = MagicMock()
        site_mock.domain = "example.com"
        mock_get_current.return_value = site_mock

        # Call View
        response = UserActivateView.as_view()(request, token=token)

    # Refresh User
    user.refresh_from_db()

    # Assert Response
    assert response.status_code == status.HTTP_200_OK
    assert response.data["id"] == str(user.id)
    assert user.is_active is True

    # Assert Cache Delete Called
    token_cache.delete.assert_called_once()

    # Assert Email Sent Metrics
    mock_send_mail.assert_called_once()
    rec_token.assert_called()
    rec_cache.assert_called()
    rec_update.assert_called()
    rec_action.assert_called()
    rec_http.assert_called()


# Email Send Failure Test
def test_user_activate_view_email_send_failure_returns_500() -> None:
    """
    Verify Email Send Exception Yields 500 And Records Metrics.
    """

    # Create Inactive User
    user = User.objects.create_user(
        username="emailfail",
        email="emailfail@example.com",
        first_name="Email",
        last_name="Fail",
        password="SecurePassword@123",
        is_active=False,
    )

    # Inputs
    token: str = "valid.token.value"
    payload: dict[str, Any] = {"sub": str(user.id)}

    # Build Request
    factory: APIRequestFactory = APIRequestFactory()
    request = factory.get("/api/users/activate/<token>/")

    # Build Cache Mapping
    token_cache: MagicMock = _build_token_cache_mock(expected_token=token)
    cache_mapping: dict[str, Any] = {"token_cache": token_cache}

    # Patch Dependencies
    with (
        patch.object(settings, "ACTIVATION_TOKEN_SECRET", "secret"),
        patch.object(settings, "DEFAULT_FROM_EMAIL", "noreply@example.com"),
        patch.object(settings, "PROJECT_NAME", "InitStack"),
        patch("apps.users.views.user_activate_view.caches", cache_mapping),
        patch("apps.users.views.user_activate_view.jwt.decode", return_value=payload),
        patch("apps.users.views.user_activate_view.Site.objects.get_current") as mock_get_current,
        patch("apps.users.views.user_activate_view.render_to_string", return_value="<html>ok</html>"),
        patch("apps.users.views.user_activate_view.send_mail", side_effect=Exception("boom")) as mock_send_mail,
        patch("apps.users.views.user_activate_view.record_email_sent") as rec_email,
        patch("apps.users.views.user_activate_view.record_email_template_render_duration") as rec_template,
        patch("apps.users.views.user_activate_view.record_api_error") as rec_api_error,
        patch("apps.users.views.user_activate_view.record_http_request") as rec_http,
        patch("apps.users.views.user_activate_view.record_user_action") as rec_action,
        patch("apps.users.views.user_activate_view.record_user_update") as rec_update,
    ):
        # Configure Site
        site_mock: MagicMock = MagicMock()
        site_mock.domain = "example.com"
        mock_get_current.return_value = site_mock

        # Call View
        response = UserActivateView.as_view()(request, token=token)

    # Refresh User
    user.refresh_from_db()

    # Assert Response
    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert response.data == {"error": "Internal Server Error"}

    # Assert User Activated Before Email
    assert user.is_active is True

    # Assert Email Attempted And Failure Recorded
    mock_send_mail.assert_called_once()
    rec_email.assert_called()
    rec_template.assert_called()

    # Assert Error Metrics Recorded
    rec_api_error.assert_called()
    rec_http.assert_called()
    rec_action.assert_called()
    rec_update.assert_called()


# Invalid Token Test
def test_user_activate_view_invalid_token_returns_401() -> None:
    """
    Verify Invalid Token Returns 401 Unauthorized.
    """

    # Inputs
    token: str = "bad.token"

    # Build Request
    factory: APIRequestFactory = APIRequestFactory()
    request: Request = factory.get("/api/users/activate/<token>/")

    # Patch Dependencies
    with (
        patch.object(settings, "ACTIVATION_TOKEN_SECRET", "secret"),
        patch.object(settings, "PROJECT_NAME", "InitStack"),
        patch("apps.users.views.user_activate_view.jwt.decode", side_effect=jwt.InvalidTokenError("bad")),
        patch("apps.users.views.user_activate_view.record_token_validation") as rec_token,
        patch("apps.users.views.user_activate_view.record_user_action") as rec_action,
        patch("apps.users.views.user_activate_view.record_http_request") as rec_http,
    ):
        # Call View
        response = UserActivateView.as_view()(request, token=token)

    # Assert Response
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.data == {"error": "Invalid Activation Token"}

    # Assert Metrics
    rec_token.assert_called()
    rec_action.assert_called()
    rec_http.assert_called()


# Token Mismatch Test
def test_user_activate_view_token_mismatch_returns_401() -> None:
    """
    Verify Cache Miss Or Mismatch Returns 401 Unauthorized.
    """

    # Create Inactive User
    user = User.objects.create_user(
        username="mismatch_user",
        email="mismatch@example.com",
        first_name="Mis",
        last_name="Match",
        password="SecurePassword@123",
        is_active=False,
    )

    # Inputs
    token: str = "another.token"
    payload: dict[str, Any] = {"sub": str(user.id)}

    # Build Request
    factory: APIRequestFactory = APIRequestFactory()
    request: Request = factory.get("/api/users/activate/<token>/")

    # Build Cache Mapping With None
    token_cache: MagicMock = _build_token_cache_mock(expected_token=None)
    cache_mapping: dict[str, Any] = {"token_cache": token_cache}

    # Patch Dependencies
    with (
        patch.object(settings, "ACTIVATION_TOKEN_SECRET", "secret"),
        patch.object(settings, "PROJECT_NAME", "InitStack"),
        patch("apps.users.views.user_activate_view.caches", cache_mapping),
        patch("apps.users.views.user_activate_view.jwt.decode", return_value=payload),
        patch("apps.users.views.user_activate_view.record_token_validation") as rec_token,
        patch("apps.users.views.user_activate_view.record_cache_operation") as rec_cache,
        patch("apps.users.views.user_activate_view.record_user_action") as rec_action,
        patch("apps.users.views.user_activate_view.record_http_request") as rec_http,
    ):
        # Call View
        response = UserActivateView.as_view()(request, token=token)

    # Assert Response
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.data == {"error": "Invalid Or Expired Activation Token"}

    # Assert Metrics
    rec_token.assert_called()
    rec_cache.assert_called()
    rec_action.assert_called()
    rec_http.assert_called()
