# ruff: noqa: S105

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
from apps.users.views.user_reactivate_confirm_view import UserReactivateConfirmView

# If Type Checking
if TYPE_CHECKING:
    # Third Party Imports
    from rest_framework.request import Request

# Get User Model
User = get_user_model()

# Enable Django DB Access For All Tests In This Module
pytestmark = pytest.mark.django_db


# 401 Invalid Token Test
def test_user_reactivate_confirm_invalid_token_returns_401() -> None:
    """
    Invalid Reactivation Token Should Yield 401.
    """

    # Request
    factory: APIRequestFactory = APIRequestFactory()
    request: Request = factory.get("/api/users/reactivate/confirm/bad/")

    # Patch Decode To Raise InvalidTokenError
    with (
        patch(
            "apps.users.views.user_reactivate_confirm_view.jwt.decode",
            side_effect=__import__("jwt").InvalidTokenError,
        ),
        patch("apps.users.views.user_reactivate_confirm_view.record_token_validation") as rec_token,
        patch("apps.users.views.user_reactivate_confirm_view.record_http_request") as rec_http,
        patch("apps.users.views.user_reactivate_confirm_view.record_user_action") as rec_action,
    ):
        response = UserReactivateConfirmView.as_view()(request, token="bad")

    # Assert
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.data == {"error": "Invalid Reactivation Token"}
    rec_token.assert_called_with(token_type="reactivation", success=False)
    rec_http.assert_called()
    rec_action.assert_called()


# 401 Token Cache Mismatch Test
def test_user_reactivate_confirm_token_cache_mismatch_returns_401() -> None:
    """
    When Cached Token Is Missing Or Different, Return 401.
    """

    # Request
    factory: APIRequestFactory = APIRequestFactory()
    token: str = "react.jwt"
    request: Request = factory.get(f"/api/users/reactivate/confirm/{token}/")

    # Cache Mock With No Token
    token_cache: MagicMock = MagicMock()
    token_cache.get.return_value = None
    cache_mapping: dict[str, MagicMock] = {"token_cache": token_cache}

    # Patch Dependencies
    with (
        patch("apps.users.views.user_reactivate_confirm_view.jwt.decode", return_value={"sub": "1"}),
        patch("apps.users.views.user_reactivate_confirm_view.caches", cache_mapping),
        patch("apps.users.views.user_reactivate_confirm_view.record_token_validation") as rec_token,
        patch("apps.users.views.user_reactivate_confirm_view.record_token_cache_mismatch") as rec_mismatch,
        patch("apps.users.views.user_reactivate_confirm_view.record_cache_operation") as rec_cache,
        patch("apps.users.views.user_reactivate_confirm_view.record_http_request") as rec_http,
        patch("apps.users.views.user_reactivate_confirm_view.record_user_action") as rec_action,
    ):
        response = UserReactivateConfirmView.as_view()(request, token=token)

    # Assert
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.data == {"error": "Invalid Or Expired Reactivation Token"}
    rec_token.assert_called_with(token_type="reactivation", success=True)
    rec_mismatch.assert_called()
    rec_cache.assert_called()
    rec_http.assert_called()
    rec_action.assert_called()


# 200 Success Test
def test_user_reactivate_confirm_success_returns_200() -> None:
    """
    Valid Token Matching Cache Should Reactivate User And Return 200.
    """

    # Create User
    user = User.objects.create_user(
        username="reactok",
        email="reactok@example.com",
        password="SecurePassword@123",
        is_active=False,
    )

    # Request
    factory: APIRequestFactory = APIRequestFactory()
    token: str = "react.jwt"
    request: Request = factory.get(f"/api/users/reactivate/confirm/{token}/")

    # Cache Mock With Same Token
    token_cache: MagicMock = MagicMock()
    token_cache.get.return_value = token
    cache_mapping: dict[str, MagicMock] = {"token_cache": token_cache}

    # Site Mock
    site_mock: MagicMock = MagicMock(spec=Site)
    site_mock.domain = "example.com"

    # Patch Dependencies
    with (
        patch("apps.users.views.user_reactivate_confirm_view.jwt.decode", return_value={"sub": str(user.id)}),
        patch("apps.users.views.user_reactivate_confirm_view.caches", cache_mapping),
        patch("apps.users.views.user_reactivate_confirm_view.Site.objects.get_current", return_value=site_mock),
        patch("apps.users.views.user_reactivate_confirm_view.send_mail") as send_mail_mock,
        patch("apps.users.views.user_reactivate_confirm_view.record_token_validation") as rec_token,
        patch("apps.users.views.user_reactivate_confirm_view.record_user_update") as rec_update,
        patch("apps.users.views.user_reactivate_confirm_view.record_reactivation_performed") as rec_performed,
        patch("apps.users.views.user_reactivate_confirm_view.record_cache_operation") as rec_cache,
        patch("apps.users.views.user_reactivate_confirm_view.record_tokens_revoked") as rec_revoked,
        patch("apps.users.views.user_reactivate_confirm_view.record_email_template_render_duration") as rec_tpl,
        patch("apps.users.views.user_reactivate_confirm_view.record_email_sent") as rec_email,
        patch("apps.users.views.user_reactivate_confirm_view.record_http_request") as rec_http,
        patch("apps.users.views.user_reactivate_confirm_view.record_user_action") as rec_action,
    ):
        response = UserReactivateConfirmView.as_view()(request, token=token)

    # Assert
    assert response.status_code == status.HTTP_200_OK
    assert "user" in response.data

    # Side Effects
    send_mail_mock.assert_called_once()
    token_cache.delete.assert_any_call(f"reactivation_token_{user.id}")
    token_cache.delete.assert_any_call(f"access_token_{user.id}")
    token_cache.delete.assert_any_call(f"refresh_token_{user.id}")

    # Metrics
    rec_token.assert_called_with(token_type="reactivation", success=True)
    rec_update.assert_called_once()
    rec_performed.assert_called_once()
    rec_cache.assert_called()
    rec_revoked.assert_called()
    rec_tpl.assert_called()
    rec_email.assert_called()
    rec_http.assert_called()
    rec_action.assert_called()


# 500 Internal Error Test
def test_user_reactivate_confirm_internal_error_returns_500() -> None:
    """
    Unexpected Exception During Email Send Should Yield 500 And Record Metrics.
    """

    # Create User
    user = User.objects.create_user(
        username="reacterr",
        email="reacterr@example.com",
        password="SecurePassword@123",
        is_active=False,
    )

    # Request
    factory: APIRequestFactory = APIRequestFactory()
    token: str = "react.jwt"
    request: Request = factory.get(f"/api/users/reactivate/confirm/{token}/")

    # Cache Mock With Same Token
    token_cache: MagicMock = MagicMock()
    token_cache.get.return_value = token
    cache_mapping: dict[str, MagicMock] = {"token_cache": token_cache}

    # Site Mock
    site_mock: MagicMock = MagicMock(spec=Site)
    site_mock.domain = "example.com"

    # Patch Dependencies And Force send_mail Error
    with (
        patch("apps.users.views.user_reactivate_confirm_view.jwt.decode", return_value={"sub": str(user.id)}),
        patch("apps.users.views.user_reactivate_confirm_view.caches", cache_mapping),
        patch("apps.users.views.user_reactivate_confirm_view.Site.objects.get_current", return_value=site_mock),
        patch("apps.users.views.user_reactivate_confirm_view.send_mail", side_effect=Exception("boom")),
        patch("apps.users.views.user_reactivate_confirm_view.record_api_error") as rec_api_error,
        patch("apps.users.views.user_reactivate_confirm_view.record_http_request") as rec_http,
    ):
        response = UserReactivateConfirmView.as_view()(request, token=token)

    # Assert
    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert response.data == {"error": "Internal Server Error"}

    # Metrics
    rec_api_error.assert_called()
    rec_http.assert_called()
