# ruff: noqa: PLR2004

# Standard Library Imports
from typing import TYPE_CHECKING
from unittest.mock import MagicMock
from unittest.mock import patch

# Third Party Imports
import pytest
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APIRequestFactory
from rest_framework.test import force_authenticate

# Local Imports
from apps.users.views.user_logout_view import UserLogoutView

# If Type Checking
if TYPE_CHECKING:
    # Third Party Imports
    from rest_framework.request import Request

# Get User Model
User = get_user_model()

# Enable Django DB Access For All Tests In This Module
pytestmark = pytest.mark.django_db


# Success Path Test
def test_user_logout_success_revokes_tokens_returns_204() -> None:
    """
    Verify Successful Logout Deletes Access And Refresh Tokens And Returns 204.
    """

    # User
    user = User.objects.create_user(
        username="logoutok",
        email="logoutok@example.com",
        password="SecurePassword@123",
        is_active=True,
    )

    # Request
    factory: APIRequestFactory = APIRequestFactory()
    request: Request = factory.get("/api/users/logout/")
    force_authenticate(request, user=user)

    # Cache Mock
    token_cache: MagicMock = MagicMock()
    cache_mapping: dict[str, MagicMock] = {"token_cache": token_cache}

    # Patch
    with (
        patch("apps.users.views.user_logout_view.caches", cache_mapping),
        patch("apps.users.views.user_logout_view.record_cache_operation") as rec_cache,
        patch("apps.users.views.user_logout_view.record_tokens_revoked") as rec_revoked,
        patch("apps.users.views.user_logout_view.record_http_request") as rec_http,
        patch("apps.users.views.user_logout_view.record_user_action") as rec_action,
        patch("apps.users.views.user_logout_view.record_logout_initiated") as rec_logout,
    ):
        response = UserLogoutView.as_view()(request)

    # Response
    assert response.status_code == status.HTTP_204_NO_CONTENT

    # Side Effects
    assert token_cache.delete.call_count == 2

    # Metrics
    rec_cache.assert_called()
    rec_revoked.assert_called()
    rec_http.assert_called()
    rec_action.assert_called()
    rec_logout.assert_called_once()


# Error Path Test
def test_user_logout_error_returns_500() -> None:
    """
    Verify Unexpected Error Yields 500 And Records Metrics.
    """

    # User
    user = User.objects.create_user(
        username="logouterr",
        email="logouterr@example.com",
        password="SecurePassword@123",
        is_active=True,
    )

    # Request
    factory: APIRequestFactory = APIRequestFactory()
    request: Request = factory.get("/api/users/logout/")
    force_authenticate(request, user=user)

    # Cache Mock That Raises On Delete
    token_cache: MagicMock = MagicMock()
    token_cache.delete.side_effect = Exception("boom")
    cache_mapping: dict[str, MagicMock] = {"token_cache": token_cache}

    # Patch
    with (
        patch("apps.users.views.user_logout_view.caches", cache_mapping),
        patch("apps.users.views.user_logout_view.record_api_error") as rec_api_error,
        patch("apps.users.views.user_logout_view.record_http_request") as rec_http,
        patch("apps.users.views.user_logout_view.record_user_action") as rec_action,
    ):
        response = UserLogoutView.as_view()(request)

    # Response
    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert response.data == {"error": "Internal Server Error"}

    # Metrics
    rec_api_error.assert_called()
    rec_http.assert_called()
    rec_action.assert_called()
