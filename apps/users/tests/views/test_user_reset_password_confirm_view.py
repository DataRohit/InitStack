# ruff: noqa: PLR2004

# Standard Library Imports
from typing import TYPE_CHECKING
from unittest.mock import MagicMock
from unittest.mock import patch

# Third Party Imports
import jwt
import pytest
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.sites.models import Site
from rest_framework import status
from rest_framework.test import APIRequestFactory
from slugify import slugify

# Local Imports
from apps.users.views.user_reset_password_confirm_view import UserResetPasswordConfirmView

# If Type Checking
if TYPE_CHECKING:
    # Third Party Imports
    from rest_framework.request import Request

# Get User Model
User = get_user_model()

# Enable Django DB Access For All Tests In This Module
pytestmark = pytest.mark.django_db


# Helper: Build Valid JWT
def _make_valid_token(user_id: str) -> str:
    """
    Create Valid Reset Password JWT For Given User ID.
    """

    # Payload
    payload: dict[str, str] = {
        "sub": user_id,
        "iss": slugify(settings.PROJECT_NAME),
        "aud": slugify(settings.PROJECT_NAME),
    }

    # Encode
    token: str = jwt.encode(
        payload=payload,
        key=settings.RESET_PASSWORD_TOKEN_SECRET,
        algorithm="HS256",
    )

    # Return Token
    return token


# 401 Invalid Token Test
def test_reset_password_confirm_invalid_token_returns_401_and_records_metrics() -> None:
    """
    Invalid JWT Should Yield 401 With Error And Record Metrics.
    """

    # Request
    factory: APIRequestFactory = APIRequestFactory()
    request: Request = factory.post("/api/users/reset-password/confirm/bad/", data={}, format="json")

    # Execute With Patches
    with (
        patch("apps.users.views.user_reset_password_confirm_view.record_token_validation") as rec_tok_val,
        patch("apps.users.views.user_reset_password_confirm_view.record_user_action") as rec_action,
        patch("apps.users.views.user_reset_password_confirm_view.record_http_request") as rec_http,
    ):
        response = UserResetPasswordConfirmView.as_view()(request, token="invalid.token")

    # Assert
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.data == {"error": "Invalid Password Reset Token"}
    rec_tok_val.assert_called_with(token_type="reset_password", success=False)
    rec_action.assert_called_with(action_type="reset_password_confirm", success=False)
    rec_http.assert_called()


# 401 Cache Mismatch Test
def test_reset_password_confirm_cache_mismatch_returns_401_and_records_metrics() -> None:
    """
    Valid JWT But Cache Missing Or Different Should Yield 401.
    """

    # Create User
    user = User.objects.create_user(
        username="u1",
        email="u1@example.com",
        first_name="U",
        last_name="One",
        password="SecurePassword@123",
        is_active=True,
    )

    # Token
    token: str = _make_valid_token(str(user.id))

    # Cache Mock: Return None To Simulate Mismatch
    token_cache: MagicMock = MagicMock()
    token_cache.get.return_value = None
    cache_mapping: dict[str, MagicMock] = {"token_cache": token_cache}

    # Request
    factory: APIRequestFactory = APIRequestFactory()
    request: Request = factory.post("/api/users/reset-password/confirm/", data={}, format="json")

    # Execute With Patches
    with (
        patch("apps.users.views.user_reset_password_confirm_view.caches", cache_mapping),
        patch("apps.users.views.user_reset_password_confirm_view.record_token_cache_mismatch") as rec_mismatch,
        patch("apps.users.views.user_reset_password_confirm_view.record_cache_operation") as rec_cache,
        patch("apps.users.views.user_reset_password_confirm_view.record_user_action") as rec_action,
        patch("apps.users.views.user_reset_password_confirm_view.record_http_request") as rec_http,
        patch("apps.users.views.user_reset_password_confirm_view.record_token_validation") as rec_tok_val,
    ):
        response = UserResetPasswordConfirmView.as_view()(request, token=token)

    # Assert
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.data == {"error": "Invalid Or Expired Password Reset Token"}
    rec_mismatch.assert_called_once()
    rec_cache.assert_called_with(operation="get", cache_type="token_cache", success=False)
    rec_action.assert_called_with(action_type="reset_password_confirm", success=False)
    rec_http.assert_called()
    rec_tok_val.assert_called_with(token_type="reset_password", success=True)


# 400 Invalid Payload Test
def test_reset_password_confirm_invalid_payload_returns_400() -> None:
    """
    Empty Payload Should Yield 400 With Validation Errors.
    """

    # Create User
    user = User.objects.create_user(
        username="u2",
        email="u2@example.com",
        first_name="U",
        last_name="Two",
        password="SecurePassword@123",
        is_active=True,
    )

    # Token
    token: str = _make_valid_token(str(user.id))

    # Cache Mock: Return Same Token
    token_cache: MagicMock = MagicMock()
    token_cache.get.return_value = token
    cache_mapping: dict[str, MagicMock] = {"token_cache": token_cache}

    # Request
    factory: APIRequestFactory = APIRequestFactory()
    request: Request = factory.post("/api/users/reset-password/confirm/", data={}, format="json")

    # Execute
    with (
        patch("apps.users.views.user_reset_password_confirm_view.caches", cache_mapping),
        patch("apps.users.views.user_reset_password_confirm_view.record_http_request") as rec_http,
    ):
        response = UserResetPasswordConfirmView.as_view()(request, token=token)

    # Assert
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "errors" in response.data
    rec_http.assert_called()


# 200 Success Test
def test_reset_password_confirm_success_returns_200_and_side_effects() -> None:
    """
    Valid Flow Should Update Password, Revoke Tokens, Send Email, And Record Metrics.
    """

    # Create User
    user = User.objects.create_user(
        username="u3",
        email="u3@example.com",
        first_name="U",
        last_name="Three",
        password="OldPassword@123",
        is_active=True,
    )

    # Token
    token: str = _make_valid_token(str(user.id))

    # Cache Mock: Token Present And Matches
    token_cache: MagicMock = MagicMock()
    token_cache.get.return_value = token
    cache_mapping: dict[str, MagicMock] = {"token_cache": token_cache}

    # Site Mock
    site_mock: MagicMock = MagicMock(spec=Site)
    site_mock.domain = "example.com"

    # Request
    factory: APIRequestFactory = APIRequestFactory()
    request: Request = factory.post(
        "/api/users/reset-password/confirm/",
        data={"password": "NewPassword@123", "re_password": "NewPassword@123"},
        format="json",
    )

    # Execute
    with (
        patch("apps.users.views.user_reset_password_confirm_view.caches", cache_mapping),
        patch("apps.users.views.user_reset_password_confirm_view.Site.objects.get_current", return_value=site_mock),
        patch(
            "apps.users.views.user_reset_password_confirm_view.render_to_string",
            return_value="<html></html>",
        ) as render_mock,
        patch("apps.users.views.user_reset_password_confirm_view.send_mail") as send_mail_mock,
        patch("apps.users.views.user_reset_password_confirm_view.record_cache_operation") as rec_cache,
        patch("apps.users.views.user_reset_password_confirm_view.record_tokens_revoked") as rec_tokens,
        patch("apps.users.views.user_reset_password_confirm_view.record_user_update") as rec_user_update,
        patch("apps.users.views.user_reset_password_confirm_view.record_password_reset_performed") as rec_reset_perf,
        patch("apps.users.views.user_reset_password_confirm_view.record_email_template_render_duration") as rec_tpl,
        patch("apps.users.views.user_reset_password_confirm_view.record_email_sent") as rec_email,
        patch("apps.users.views.user_reset_password_confirm_view.record_user_action") as rec_action,
        patch("apps.users.views.user_reset_password_confirm_view.record_http_request") as rec_http,
        patch("apps.users.views.user_reset_password_confirm_view.record_token_validation") as rec_tok_val,
    ):
        response = UserResetPasswordConfirmView.as_view()(request, token=token)

    # Assert Response
    assert response.status_code == status.HTTP_200_OK
    assert response.data == {"message": "Password Reset Completed Successfully"}

    # Password Updated
    user.refresh_from_db()
    assert user.check_password("NewPassword@123") is True

    # Cache Effects
    token_cache.delete.assert_any_call(f"reset_password_token_{user.id}")
    token_cache.delete.assert_any_call(f"access_token_{user.id}")
    token_cache.delete.assert_any_call(f"refresh_token_{user.id}")
    assert token_cache.delete.call_count >= 3

    # Email And Template
    render_mock.assert_called_once()
    send_mail_mock.assert_called_once()

    # Metrics
    rec_cache.assert_called()
    rec_tokens.assert_any_call(token_type="reset_password")
    rec_tokens.assert_any_call(token_type="access")
    rec_tokens.assert_any_call(token_type="refresh")
    rec_user_update.assert_called_with(update_type="password_reset", success=True)
    rec_reset_perf.assert_called_once()
    rec_tpl.assert_called()
    rec_email.assert_called_with(email_type="password_reset_success", success=True)
    rec_action.assert_called_with(action_type="reset_password_confirm", success=True)
    rec_http.assert_called()
    rec_tok_val.assert_called()


# 500 Email Failure Test
def test_reset_password_confirm_email_failure_returns_500_and_records_metrics() -> None:
    """
    Email Send Failure Should Yield 500 And Record API Error And Metrics.
    """

    # Create User
    user = User.objects.create_user(
        username="u4",
        email="u4@example.com",
        first_name="U",
        last_name="Four",
        password="OldPassword@123",
        is_active=True,
    )

    # Token
    token: str = _make_valid_token(str(user.id))

    # Cache Mock
    token_cache: MagicMock = MagicMock()
    token_cache.get.return_value = token
    cache_mapping: dict[str, MagicMock] = {"token_cache": token_cache}

    # Site Mock
    site_mock: MagicMock = MagicMock(spec=Site)
    site_mock.domain = "example.com"

    # Request
    factory: APIRequestFactory = APIRequestFactory()
    request: Request = factory.post(
        "/api/users/reset-password/confirm/",
        data={"password": "NewPassword@123", "re_password": "NewPassword@123"},
        format="json",
    )

    # Execute With send_mail Error
    with (
        patch("apps.users.views.user_reset_password_confirm_view.caches", cache_mapping),
        patch("apps.users.views.user_reset_password_confirm_view.Site.objects.get_current", return_value=site_mock),
        patch("apps.users.views.user_reset_password_confirm_view.render_to_string", return_value="<html></html>"),
        patch("apps.users.views.user_reset_password_confirm_view.send_mail", side_effect=Exception("boom")),
        patch("apps.users.views.user_reset_password_confirm_view.record_email_sent") as rec_email,
        patch("apps.users.views.user_reset_password_confirm_view.record_api_error") as rec_api_error,
        patch("apps.users.views.user_reset_password_confirm_view.record_http_request") as rec_http,
    ):
        response = UserResetPasswordConfirmView.as_view()(request, token=token)

    # Assert
    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert response.data == {"error": "Internal Server Error"}
    rec_email.assert_called_with(email_type="password_reset_success", success=False)
    rec_api_error.assert_called()
    rec_http.assert_called()
