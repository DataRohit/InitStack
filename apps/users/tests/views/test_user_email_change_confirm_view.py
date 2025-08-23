# ruff: noqa: S105, PLR2004

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
from apps.users.views.user_email_change_confirm_view import UserEmailChangeConfirmView

# If Type Checking
if TYPE_CHECKING:
    # Third Party Imports
    from rest_framework.request import Request

# Get User Model
User = get_user_model()

# Enable Django DB Access For All Tests In This Module
pytestmark = pytest.mark.django_db


# Build Token Cache Mock Function
def _build_token_cache_mock(get_value: str | None) -> MagicMock:
    """
    Build Token Cache Mock With Configurable Get Return.

    Args:
        get_value (str | None): Return Value For get().

    Returns:
        MagicMock: Cache Mock.
    """

    # Create Mock
    m: MagicMock = MagicMock()

    # Configure Get
    m.get.return_value = get_value

    # Return Mock
    return m


# Success Path Test
def test_user_email_change_confirm_success_updates_email_revokes_tokens_sends_emails_returns_200() -> None:
    """
    Verify Success Path Updates Email, Revokes Tokens, Sends Two Emails, And Returns 200 With User Data.
    """

    # Existing Users
    user = User.objects.create_user(
        username="changeok",
        email="old@example.com",
        first_name="User",
        last_name="Ok",
        password="SecurePassword@123",
        is_active=True,
    )

    # Inputs
    token: str = "valid.token"
    payload: dict[str, Any] = {"sub": str(user.id)}
    new_email: str = "new@example.com"

    # Request
    factory: APIRequestFactory = APIRequestFactory()
    request: Request = factory.put(
        f"/api/users/change-email/confirm/{token}/",
        {"email": new_email, "re_email": new_email},
        format="json",
    )

    # Cache Mock With Matching Token
    token_cache: MagicMock = _build_token_cache_mock(get_value=token)
    cache_mapping: dict[str, Any] = {"token_cache": token_cache}

    # Patch Dependencies
    with (
        patch.object(settings, "CHANGE_EMAIL_TOKEN_SECRET", "secret"),
        patch.object(settings, "REACTIVATION_TOKEN_SECRET", "rsec"),
        patch.object(settings, "REACTIVATION_TOKEN_EXPIRY", 3600),
        patch.object(settings, "DEFAULT_FROM_EMAIL", "noreply@example.com"),
        patch.object(settings, "PROJECT_NAME", "InitStack"),
        patch("apps.users.views.user_email_change_confirm_view.caches", cache_mapping),
        patch("apps.users.views.user_email_change_confirm_view.jwt.decode", return_value=payload),
        patch(
            "apps.users.views.user_email_change_confirm_view.jwt.encode",
            return_value="react.token",
        ) as mock_jwt_encode,
        patch("apps.users.views.user_email_change_confirm_view.Site.objects.get_current") as mock_get_current,
        patch(
            "apps.users.views.user_email_change_confirm_view.render_to_string",
            side_effect=["<html>success</html>", "<html>react</html>"],
        ) as mock_render,
        patch("apps.users.views.user_email_change_confirm_view.send_mail") as mock_send_mail,
        patch("apps.users.views.user_email_change_confirm_view.record_token_validation") as rec_token,
        patch("apps.users.views.user_email_change_confirm_view.record_cache_operation") as rec_cache,
        patch("apps.users.views.user_email_change_confirm_view.record_user_update") as rec_update,
        patch("apps.users.views.user_email_change_confirm_view.record_email_sent") as rec_email,
        patch("apps.users.views.user_email_change_confirm_view.record_email_change_performed") as rec_performed,
        patch("apps.users.views.user_email_change_confirm_view.record_tokens_revoked") as rec_revoked,
        patch("apps.users.views.user_email_change_confirm_view.record_http_request") as rec_http,
        patch("apps.users.views.user_email_change_confirm_view.record_user_action") as rec_action,
        patch("apps.users.views.user_email_change_confirm_view.record_success_email_template_render_duration"),
        patch("apps.users.views.user_email_change_confirm_view.record_reactivation_email_template_render_duration"),
    ):
        # Site
        site_mock: MagicMock = MagicMock()
        site_mock.domain = "example.com"
        mock_get_current.return_value = site_mock

        # Call View
        response = UserEmailChangeConfirmView.as_view()(request, token=token)

    # Response
    assert response.status_code == status.HTTP_200_OK
    assert "user" in response.data

    # Side Effects
    user.refresh_from_db()
    assert user.email == new_email
    assert user.is_active is False
    mock_jwt_encode.assert_called_once()
    assert token_cache.delete.call_count == 3
    assert token_cache.set.call_count == 1
    assert mock_render.call_count == 2
    assert mock_send_mail.call_count == 2

    # Metrics
    rec_token.assert_called()
    rec_cache.assert_called()
    rec_update.assert_called()
    rec_email.assert_called()
    rec_performed.assert_called_once()
    rec_revoked.assert_called()
    rec_http.assert_called()
    rec_action.assert_called()


# Invalid Token Test
def test_user_email_change_confirm_invalid_token_returns_401() -> None:
    """
    Verify Invalid JWT Returns 401 With Error And Records Metrics.
    """

    # Inputs
    token: str = "bad.token"

    # Request
    factory: APIRequestFactory = APIRequestFactory()
    request: Request = factory.put(
        f"/api/users/change-email/confirm/{token}/",
        {"email": "n@e.com", "re_email": "n@e.com"},
        format="json",
    )

    # Cache Mock Irrelevant
    cache_mapping: dict[str, Any] = {"token_cache": MagicMock()}

    # Patch
    with (
        patch.object(settings, "CHANGE_EMAIL_TOKEN_SECRET", "secret"),
        patch.object(settings, "DEFAULT_FROM_EMAIL", "noreply@example.com"),
        patch.object(settings, "PROJECT_NAME", "InitStack"),
        patch("apps.users.views.user_email_change_confirm_view.caches", cache_mapping),
        patch(
            "apps.users.views.user_email_change_confirm_view.jwt.decode",
            side_effect=jwt.InvalidTokenError("bad"),
        ),
        patch("apps.users.views.user_email_change_confirm_view.record_token_validation") as rec_token,
        patch("apps.users.views.user_email_change_confirm_view.record_http_request") as rec_http,
        patch("apps.users.views.user_email_change_confirm_view.record_user_action") as rec_action,
    ):
        response = UserEmailChangeConfirmView.as_view()(request, token=token)

    # Response
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.data == {"error": "Invalid Email Change Token"}

    # Metrics
    rec_token.assert_called()
    rec_http.assert_called()
    rec_action.assert_called()


# Token Cache Mismatch Test
def test_user_email_change_confirm_token_cache_mismatch_returns_401() -> None:
    """
    Verify Cache Miss Or Mismatch Returns 401.
    """

    # User
    user = User.objects.create_user(
        username="changemismatch",
        email="change.mismatch@example.com",
        first_name="User",
        last_name="Mis",
        password="SecurePassword@123",
        is_active=True,
    )

    # Inputs
    token: str = "valid.token"
    payload: dict[str, Any] = {"sub": str(user.id)}

    # Request
    factory: APIRequestFactory = APIRequestFactory()
    request: Request = factory.put(
        f"/api/users/change-email/confirm/{token}/",
        {"email": "a@b.com", "re_email": "a@b.com"},
        format="json",
    )

    # Cache With Different Token -> Mismatch
    token_cache: MagicMock = _build_token_cache_mock(get_value="different.token")
    cache_mapping: dict[str, Any] = {"token_cache": token_cache}

    # Patch
    with (
        patch.object(settings, "CHANGE_EMAIL_TOKEN_SECRET", "secret"),
        patch.object(settings, "DEFAULT_FROM_EMAIL", "noreply@example.com"),
        patch.object(settings, "PROJECT_NAME", "InitStack"),
        patch("apps.users.views.user_email_change_confirm_view.caches", cache_mapping),
        patch("apps.users.views.user_email_change_confirm_view.jwt.decode", return_value=payload),
        patch("apps.users.views.user_email_change_confirm_view.record_token_validation") as rec_token,
        patch("apps.users.views.user_email_change_confirm_view.record_cache_operation") as rec_cache,
        patch("apps.users.views.user_email_change_confirm_view.record_token_cache_mismatch") as rec_mismatch,
        patch("apps.users.views.user_email_change_confirm_view.record_http_request") as rec_http,
        patch("apps.users.views.user_email_change_confirm_view.record_user_action") as rec_action,
    ):
        response = UserEmailChangeConfirmView.as_view()(request, token=token)

    # Response
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.data == {"error": "Invalid Or Expired Email Change Token"}

    # Metrics
    rec_token.assert_called()
    rec_cache.assert_called()
    rec_mismatch.assert_called_once()
    rec_http.assert_called()
    rec_action.assert_called()


# Payload Invalid Test
def test_user_email_change_confirm_invalid_payload_returns_400() -> None:
    """
    Verify Serializer Validation Errors Return 400.
    """

    # User
    user = User.objects.create_user(
        username="changebadpayload",
        email="change.badpayload@example.com",
        first_name="User",
        last_name="Bad",
        password="SecurePassword@123",
        is_active=True,
    )

    # Inputs
    token: str = "valid.token"
    payload: dict[str, Any] = {"sub": str(user.id)}

    # Request With Mismatched Emails
    factory: APIRequestFactory = APIRequestFactory()
    request: Request = factory.put(
        f"/api/users/change-email/confirm/{token}/",
        {"email": "new@example.com", "re_email": "other@example.com"},
        format="json",
    )

    # Cache With Matching Token
    token_cache: MagicMock = _build_token_cache_mock(get_value=token)
    cache_mapping: dict[str, Any] = {"token_cache": token_cache}

    # Patch
    with (
        patch.object(settings, "CHANGE_EMAIL_TOKEN_SECRET", "secret"),
        patch.object(settings, "DEFAULT_FROM_EMAIL", "noreply@example.com"),
        patch.object(settings, "PROJECT_NAME", "InitStack"),
        patch("apps.users.views.user_email_change_confirm_view.caches", cache_mapping),
        patch("apps.users.views.user_email_change_confirm_view.jwt.decode", return_value=payload),
    ):
        response = UserEmailChangeConfirmView.as_view()(request, token=token)

    # Response
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "errors" in response.data


# Email Already Exists Test
def test_user_email_change_confirm_email_already_exists_returns_400() -> None:
    """
    Verify When New Email Already Exists, Return 400.
    """

    # Users
    user = User.objects.create_user(
        username="changeexists1",
        email="exists1@example.com",
        password="SecurePassword@123",
        is_active=True,
    )
    User.objects.create_user(
        username="changeexists2",
        email="exists2@example.com",
        password="SecurePassword@123",
        is_active=True,
    )

    # Inputs
    token: str = "valid.token"
    payload: dict[str, Any] = {"sub": str(user.id)}
    new_email: str = "exists2@example.com"

    # Request
    factory: APIRequestFactory = APIRequestFactory()
    request: Request = factory.put(
        f"/api/users/change-email/confirm/{token}/",
        {"email": new_email, "re_email": new_email},
        format="json",
    )

    # Cache With Matching Token
    token_cache: MagicMock = _build_token_cache_mock(get_value=token)
    cache_mapping: dict[str, Any] = {"token_cache": token_cache}

    # Patch
    with (
        patch.object(settings, "CHANGE_EMAIL_TOKEN_SECRET", "secret"),
        patch.object(settings, "DEFAULT_FROM_EMAIL", "noreply@example.com"),
        patch.object(settings, "PROJECT_NAME", "InitStack"),
        patch("apps.users.views.user_email_change_confirm_view.caches", cache_mapping),
        patch("apps.users.views.user_email_change_confirm_view.jwt.decode", return_value=payload),
        patch("apps.users.views.user_email_change_confirm_view.record_http_request") as rec_http,
    ):
        response = UserEmailChangeConfirmView.as_view()(request, token=token)

    # Response
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.data == {"errors": {"email": ["Email Already Exists"]}}

    # Metrics
    rec_http.assert_called()


# Success Email Send Failure Test
def test_user_email_change_confirm_success_email_send_failure_returns_500() -> None:
    """
    Verify Failure While Sending Success Email Causes 500 And Records Error Metrics.
    """

    # User
    user = User.objects.create_user(
        username="changeerr1",
        email="old1@example.com",
        password="SecurePassword@123",
        is_active=True,
    )

    # Inputs
    token: str = "valid.token"
    payload: dict[str, Any] = {"sub": str(user.id)}
    new_email: str = "new1@example.com"

    # Request
    factory: APIRequestFactory = APIRequestFactory()
    request: Request = factory.put(
        f"/api/users/change-email/confirm/{token}/",
        {"email": new_email, "re_email": new_email},
        format="json",
    )

    # Cache With Matching Token
    token_cache: MagicMock = _build_token_cache_mock(get_value=token)
    cache_mapping: dict[str, Any] = {"token_cache": token_cache}

    # Patch
    with (
        patch.object(settings, "CHANGE_EMAIL_TOKEN_SECRET", "secret"),
        patch.object(settings, "REACTIVATION_TOKEN_SECRET", "rsec"),
        patch.object(settings, "REACTIVATION_TOKEN_EXPIRY", 3600),
        patch.object(settings, "DEFAULT_FROM_EMAIL", "noreply@example.com"),
        patch.object(settings, "PROJECT_NAME", "InitStack"),
        patch("apps.users.views.user_email_change_confirm_view.caches", cache_mapping),
        patch("apps.users.views.user_email_change_confirm_view.jwt.decode", return_value=payload),
        patch("apps.users.views.user_email_change_confirm_view.jwt.encode", return_value="react.token"),
        patch("apps.users.views.user_email_change_confirm_view.Site.objects.get_current") as mock_get_current,
        patch(
            "apps.users.views.user_email_change_confirm_view.render_to_string",
            side_effect=["<html>success</html>", "<html>react</html>"],
        ),
        patch(
            "apps.users.views.user_email_change_confirm_view.send_mail",
            side_effect=Exception("boom"),
        ) as mock_send_mail,
        patch("apps.users.views.user_email_change_confirm_view.record_email_sent") as rec_email,
        patch("apps.users.views.user_email_change_confirm_view.record_api_error") as rec_api_error,
        patch("apps.users.views.user_email_change_confirm_view.record_http_request") as rec_http,
    ):
        site_mock: MagicMock = MagicMock()
        site_mock.domain = "example.com"
        mock_get_current.return_value = site_mock

        # Call
        response = UserEmailChangeConfirmView.as_view()(request, token=token)

    # Response
    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert response.data == {"error": "Internal Server Error"}

    # Metrics
    mock_send_mail.assert_called_once()
    rec_email.assert_called()
    rec_api_error.assert_called()
    rec_http.assert_called()


# Reactivation Email Send Failure Test
def test_user_email_change_confirm_reactivation_email_send_failure_returns_500() -> None:
    """
    Verify Failure While Sending Reactivation Email Causes 500 And Records Error Metrics.
    """

    # User
    user = User.objects.create_user(
        username="changeerr2",
        email="old2@example.com",
        password="SecurePassword@123",
        is_active=True,
    )

    # Inputs
    token: str = "valid.token"
    payload: dict[str, Any] = {"sub": str(user.id)}
    new_email: str = "new2@example.com"

    # Request
    factory: APIRequestFactory = APIRequestFactory()
    request: Request = factory.put(
        f"/api/users/change-email/confirm/{token}/",
        {"email": new_email, "re_email": new_email},
        format="json",
    )

    # Cache With Matching Token
    token_cache: MagicMock = _build_token_cache_mock(get_value=token)
    cache_mapping: dict[str, Any] = {"token_cache": token_cache}

    # Patch
    with (
        patch.object(settings, "CHANGE_EMAIL_TOKEN_SECRET", "secret"),
        patch.object(settings, "REACTIVATION_TOKEN_SECRET", "rsec"),
        patch.object(settings, "REACTIVATION_TOKEN_EXPIRY", 3600),
        patch.object(settings, "DEFAULT_FROM_EMAIL", "noreply@example.com"),
        patch.object(settings, "PROJECT_NAME", "InitStack"),
        patch("apps.users.views.user_email_change_confirm_view.caches", cache_mapping),
        patch("apps.users.views.user_email_change_confirm_view.jwt.decode", return_value=payload),
        patch("apps.users.views.user_email_change_confirm_view.jwt.encode", return_value="react.token"),
        patch("apps.users.views.user_email_change_confirm_view.Site.objects.get_current") as mock_get_current,
        patch(
            "apps.users.views.user_email_change_confirm_view.render_to_string",
            side_effect=["<html>success</html>", "<html>react</html>"],
        ),
        patch(
            "apps.users.views.user_email_change_confirm_view.send_mail",
            side_effect=[None, Exception("boom")],
        ) as mock_send_mail,
        patch("apps.users.views.user_email_change_confirm_view.record_email_sent") as rec_email,
        patch("apps.users.views.user_email_change_confirm_view.record_api_error") as rec_api_error,
        patch("apps.users.views.user_email_change_confirm_view.record_http_request") as rec_http,
    ):
        site_mock: MagicMock = MagicMock()
        site_mock.domain = "example.com"
        mock_get_current.return_value = site_mock

        # Call
        response = UserEmailChangeConfirmView.as_view()(request, token=token)

    # Response
    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert response.data == {"error": "Internal Server Error"}

    # Metrics
    assert mock_send_mail.call_count == 2
    rec_email.assert_called()
    rec_api_error.assert_called()
    rec_http.assert_called()
