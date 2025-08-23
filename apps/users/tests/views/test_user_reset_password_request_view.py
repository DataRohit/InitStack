# ruff: noqa: S105

# Standard Library Imports
import datetime
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
from apps.users.views.user_reset_password_request_view import UserResetPasswordRequestView

# If Type Checking
if TYPE_CHECKING:
    # Third Party Imports
    from rest_framework.request import Request

# Get User Model
User = get_user_model()

# Enable Django DB Access For All Tests In This Module
pytestmark = pytest.mark.django_db


# Helper: Build Valid JWT
def _make_valid_reset_token(user_id: str) -> str:
    """
    Create Valid Reset Password JWT For Given User ID.
    """

    # Times
    now_dt: datetime.datetime = datetime.datetime.now(tz=datetime.UTC)
    exp_dt: datetime.datetime = now_dt + datetime.timedelta(seconds=settings.RESET_PASSWORD_TOKEN_EXPIRY)

    # Payload
    payload: dict[str, object] = {
        "sub": user_id,
        "iss": slugify(settings.PROJECT_NAME),
        "aud": slugify(settings.PROJECT_NAME),
        "iat": now_dt,
        "exp": exp_dt,
    }

    # Encode
    token: str = jwt.encode(
        payload=payload,
        key=settings.RESET_PASSWORD_TOKEN_SECRET,
        algorithm="HS256",
    )

    # Return Token
    return token


# 202 Success With Invalid Cached Token Test
def test_reset_password_request_invalid_cached_token_triggers_regeneration_and_succeeds() -> None:
    """
    Invalid Cached Token Should Trigger Regeneration Path And Return 202.
    """

    # Create Active User
    user = User.objects.create_user(
        username="active_invalid",
        email="active_invalid@example.com",
        first_name="Ac",
        last_name="Tive",
        password="SecurePassword@123",
        is_active=True,
    )

    # Cache Mock: Return Invalid Token Placeholder
    invalid_token: str = "invalid.token.value"
    token_cache: MagicMock = MagicMock()
    token_cache.get.return_value = invalid_token
    cache_mapping: dict[str, MagicMock] = {"token_cache": token_cache}

    # Site Mock
    site_mock: MagicMock = MagicMock(spec=Site)
    site_mock.domain = "example.com"

    # Request Data
    data: dict[str, str] = {"identifier": user.email, "re_identifier": user.email}

    # Request
    factory: APIRequestFactory = APIRequestFactory()
    request: Request = factory.post("/api/users/reset-password/request/", data=data, format="json")

    # Execute With Patches (jwt.decode Raises InvalidTokenError)
    with (
        patch("apps.users.views.user_reset_password_request_view.caches", cache_mapping),
        patch("apps.users.views.user_reset_password_request_view.Site.objects.get_current", return_value=site_mock),
        patch(
            "apps.users.views.user_reset_password_request_view.render_to_string",
            return_value="<html></html>",
        ) as render_mock,
        patch("apps.users.views.user_reset_password_request_view.send_mail") as send_mail_mock,
        patch("apps.users.views.user_reset_password_request_view.jwt.decode", side_effect=jwt.InvalidTokenError()),
        patch("apps.users.views.user_reset_password_request_view.record_cache_operation") as rec_cache,
        patch("apps.users.views.user_reset_password_request_view.record_token_generated") as rec_tok_gen,
        patch("apps.users.views.user_reset_password_request_view.record_token_reused") as rec_tok_reused,
        patch("apps.users.views.user_reset_password_request_view.record_token_validation") as rec_tok_val,
        patch("apps.users.views.user_reset_password_request_view.record_email_template_render_duration") as rec_tpl,
        patch("apps.users.views.user_reset_password_request_view.record_email_sent") as rec_email,
        patch("apps.users.views.user_reset_password_request_view.record_reset_password_request_initiated") as rec_init,
        patch("apps.users.views.user_reset_password_request_view.record_http_request") as rec_http,
        patch("apps.users.views.user_reset_password_request_view.record_user_action") as rec_action,
    ):
        response = UserResetPasswordRequestView.as_view()(request)

    # Assert Response
    assert response.status_code == status.HTTP_202_ACCEPTED
    assert response.data == {
        "status_code": status.HTTP_202_ACCEPTED,
        "message": "Password Reset Request Sent Successfully",
    }

    # Ensure Regeneration Path (set called, token_generated recorded, token_reused not called)
    token_cache.set.assert_called_once()
    rec_tok_gen.assert_called_once()
    rec_tok_reused.assert_not_called()

    # Email And Template
    render_mock.assert_called_once()
    send_mail_mock.assert_called_once()

    # Metrics
    rec_cache.assert_called()
    rec_tok_val.assert_called_with(token_type="reset_password", success=False)
    rec_tpl.assert_called()
    rec_email.assert_called_with(email_type="reset_password_request", success=True)
    rec_init.assert_called_once()
    rec_http.assert_called()
    rec_action.assert_called_with(action_type="reset_password_request", success=True)


# 400 Invalid Payload Test
def test_reset_password_request_invalid_payload_returns_400() -> None:
    """
    Empty Payload Should Yield 400 With Serializer Errors And Status Code.
    """

    # Request
    factory: APIRequestFactory = APIRequestFactory()
    request: Request = factory.post("/api/users/reset-password/request/", data={}, format="json")

    # Execute
    response = UserResetPasswordRequestView.as_view()(request)

    # Assert
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.data.get("status_code") == status.HTTP_400_BAD_REQUEST
    assert "errors" in response.data


# 400 User Not Found Test
def test_reset_password_request_user_not_found_returns_400() -> None:
    """
    Non-Existing Identifier Should Yield 400 With Proper Error.
    """

    # Request Data
    data: dict[str, str] = {"identifier": "nouser@example.com", "re_identifier": "nouser@example.com"}

    # Request
    factory: APIRequestFactory = APIRequestFactory()
    request: Request = factory.post("/api/users/reset-password/request/", data=data, format="json")

    # Patch get To Raise DoesNotExist
    with patch("apps.users.views.user_reset_password_request_view.User.objects.get", side_effect=User.DoesNotExist):
        response = UserResetPasswordRequestView.as_view()(request)

    # Assert
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.data == {"errors": {"identifier": ["No Account Found With This Identifier"]}}


# 400 User Inactive Test
def test_reset_password_request_user_inactive_returns_400() -> None:
    """
    Inactive Account Should Yield 400 With Proper Error.
    """

    # Create Inactive User
    user = User.objects.create_user(
        username="inactive",
        email="inactive@example.com",
        first_name="In",
        last_name="Active",
        password="SecurePassword@123",
        is_active=False,
    )

    # Request Data
    data: dict[str, str] = {"identifier": user.email, "re_identifier": user.email}

    # Request
    factory: APIRequestFactory = APIRequestFactory()
    request: Request = factory.post("/api/users/reset-password/request/", data=data, format="json")

    # Execute
    response = UserResetPasswordRequestView.as_view()(request)

    # Assert
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.data == {"errors": {"identifier": ["Account Is Not Active"]}}


# 202 Success With New Token Test
def test_reset_password_request_success_new_token_returns_202_and_side_effects() -> None:
    """
    When No Valid Cached Token, Should Generate New Token, Cache It, Send Email, And Record Metrics.
    """

    # Create Active User
    user = User.objects.create_user(
        username="active1",
        email="active1@example.com",
        first_name="Ac",
        last_name="Tive",
        password="SecurePassword@123",
        is_active=True,
    )

    # Cache Mock: No Existing Token
    token_cache: MagicMock = MagicMock()
    token_cache.get.return_value = None
    cache_mapping: dict[str, MagicMock] = {"token_cache": token_cache}

    # Site Mock
    site_mock: MagicMock = MagicMock(spec=Site)
    site_mock.domain = "example.com"

    # Request Data
    data: dict[str, str] = {"identifier": user.email, "re_identifier": user.email}

    # Request
    factory: APIRequestFactory = APIRequestFactory()
    request: Request = factory.post("/api/users/reset-password/request/", data=data, format="json")

    # Execute With Patches
    with (
        patch("apps.users.views.user_reset_password_request_view.caches", cache_mapping),
        patch("apps.users.views.user_reset_password_request_view.Site.objects.get_current", return_value=site_mock),
        patch(
            "apps.users.views.user_reset_password_request_view.render_to_string",
            return_value="<html></html>",
        ) as render_mock,
        patch("apps.users.views.user_reset_password_request_view.send_mail") as send_mail_mock,
        patch("apps.users.views.user_reset_password_request_view.record_cache_operation") as rec_cache,
        patch("apps.users.views.user_reset_password_request_view.record_token_generated") as rec_tok_gen,
        patch("apps.users.views.user_reset_password_request_view.record_email_template_render_duration") as rec_tpl,
        patch("apps.users.views.user_reset_password_request_view.record_email_sent") as rec_email,
        patch("apps.users.views.user_reset_password_request_view.record_reset_password_request_initiated") as rec_init,
        patch("apps.users.views.user_reset_password_request_view.record_http_request") as rec_http,
        patch("apps.users.views.user_reset_password_request_view.record_user_action") as rec_action,
    ):
        response = UserResetPasswordRequestView.as_view()(request)

    # Assert
    assert response.status_code == status.HTTP_202_ACCEPTED
    assert response.data == {
        "status_code": status.HTTP_202_ACCEPTED,
        "message": "Password Reset Request Sent Successfully",
    }

    # Side Effects
    token_cache.set.assert_called_once()
    render_mock.assert_called_once()
    send_mail_mock.assert_called_once()

    # Metrics
    rec_cache.assert_called()
    rec_tok_gen.assert_called_once()
    rec_tpl.assert_called()
    rec_email.assert_called_with(email_type="reset_password_request", success=True)
    rec_init.assert_called_once()
    rec_http.assert_called()
    rec_action.assert_called_with(action_type="reset_password_request", success=True)


# 202 Success With Reused Token Test
def test_reset_password_request_success_reused_token_returns_202_and_side_effects() -> None:
    """
    When Valid Cached Token Exists, Should Reuse It And Not Set Cache Again.
    """

    # Create Active User
    user = User.objects.create_user(
        username="active2",
        email="active2@example.com",
        first_name="Ac",
        last_name="Tive",
        password="SecurePassword@123",
        is_active=True,
    )

    # Valid Cached Token
    cached: str = _make_valid_reset_token(str(user.id))

    # Cache Mock: Existing Valid Token
    token_cache: MagicMock = MagicMock()
    token_cache.get.return_value = cached
    cache_mapping: dict[str, MagicMock] = {"token_cache": token_cache}

    # Site Mock
    site_mock: MagicMock = MagicMock(spec=Site)
    site_mock.domain = "example.com"

    # Request Data
    data: dict[str, str] = {"identifier": user.email, "re_identifier": user.email}

    # Request
    factory: APIRequestFactory = APIRequestFactory()
    request: Request = factory.post("/api/users/reset-password/request/", data=data, format="json")

    # Execute With Patches
    with (
        patch("apps.users.views.user_reset_password_request_view.caches", cache_mapping),
        patch("apps.users.views.user_reset_password_request_view.Site.objects.get_current", return_value=site_mock),
        patch(
            "apps.users.views.user_reset_password_request_view.render_to_string",
            return_value="<html></html>",
        ) as render_mock,
        patch("apps.users.views.user_reset_password_request_view.send_mail") as send_mail_mock,
        patch("apps.users.views.user_reset_password_request_view.record_cache_operation") as rec_cache,
        patch("apps.users.views.user_reset_password_request_view.record_token_reused") as rec_tok_reuse,
        patch("apps.users.views.user_reset_password_request_view.record_email_template_render_duration") as rec_tpl,
        patch("apps.users.views.user_reset_password_request_view.record_email_sent") as rec_email,
        patch("apps.users.views.user_reset_password_request_view.record_reset_password_request_initiated") as rec_init,
        patch("apps.users.views.user_reset_password_request_view.record_http_request") as rec_http,
        patch("apps.users.views.user_reset_password_request_view.record_user_action") as rec_action,
    ):
        response = UserResetPasswordRequestView.as_view()(request)

    # Assert
    assert response.status_code == status.HTTP_202_ACCEPTED
    assert response.data == {
        "status_code": status.HTTP_202_ACCEPTED,
        "message": "Password Reset Request Sent Successfully",
    }

    # Side Effects
    token_cache.set.assert_not_called()
    render_mock.assert_called_once()
    send_mail_mock.assert_called_once()

    # Metrics
    rec_cache.assert_called()
    rec_tok_reuse.assert_called_once()
    rec_tpl.assert_called()
    rec_email.assert_called_with(email_type="reset_password_request", success=True)
    rec_init.assert_called_once()
    rec_http.assert_called()
    rec_action.assert_called_with(action_type="reset_password_request", success=True)


# 500 Email Failure Test
def test_reset_password_request_email_failure_returns_500_and_records_metrics() -> None:
    """
    Email Send Failure Should Yield 500 And Record API Error And Metrics.
    """

    # Create Active User
    user = User.objects.create_user(
        username="active3",
        email="active3@example.com",
        first_name="Ac",
        last_name="Tive",
        password="SecurePassword@123",
        is_active=True,
    )

    # Cache Mock: No Existing Token
    token_cache: MagicMock = MagicMock()
    token_cache.get.return_value = None
    cache_mapping: dict[str, MagicMock] = {"token_cache": token_cache}

    # Site Mock
    site_mock: MagicMock = MagicMock(spec=Site)
    site_mock.domain = "example.com"

    # Request Data
    data: dict[str, str] = {"identifier": user.email, "re_identifier": user.email}

    # Request
    factory: APIRequestFactory = APIRequestFactory()
    request: Request = factory.post("/api/users/reset-password/request/", data=data, format="json")

    # Execute With send_mail Error
    with (
        patch("apps.users.views.user_reset_password_request_view.caches", cache_mapping),
        patch("apps.users.views.user_reset_password_request_view.Site.objects.get_current", return_value=site_mock),
        patch("apps.users.views.user_reset_password_request_view.render_to_string", return_value="<html></html>"),
        patch("apps.users.views.user_reset_password_request_view.send_mail", side_effect=Exception("boom")),
        patch("apps.users.views.user_reset_password_request_view.record_email_sent") as rec_email,
        patch("apps.users.views.user_reset_password_request_view.record_api_error") as rec_api_error,
        patch("apps.users.views.user_reset_password_request_view.record_http_request") as rec_http,
        patch("apps.users.views.user_reset_password_request_view.record_user_action") as rec_action,
    ):
        response = UserResetPasswordRequestView.as_view()(request)

    # Assert
    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert response.data == {
        "status_code": status.HTTP_500_INTERNAL_SERVER_ERROR,
        "error": "Internal Server Error",
    }
    rec_email.assert_called_with(email_type="reset_password_request", success=False)
    rec_api_error.assert_called()
    rec_http.assert_called()
    rec_action.assert_called_with(action_type="reset_password_request", success=False)
