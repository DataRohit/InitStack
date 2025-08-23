# ruff: noqa: S105

# Standard Library Imports
import datetime
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
from rest_framework.test import force_authenticate
from slugify import slugify

# Local Imports
from apps.users.views.user_username_change_request_view import UserUsernameChangeRequestView

# Get User Model
User = get_user_model()

# Enable Django DB Access For All Tests In This Module
pytestmark = pytest.mark.django_db


# Helper: Build Valid Change Username JWT
def _make_valid_change_username_token(user_id: str) -> str:
    """
    Create Valid Change Username JWT For Given User ID.
    """

    # Times
    now_dt: datetime.datetime = datetime.datetime.now(tz=datetime.UTC)
    exp_dt: datetime.datetime = now_dt + datetime.timedelta(seconds=settings.CHANGE_USERNAME_TOKEN_EXPIRY)

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
        key=settings.CHANGE_USERNAME_TOKEN_SECRET,
        algorithm="HS256",
    )

    # Return Token
    return token


# 401 Unauthorized Test
def test_username_change_request_unauthenticated_returns_401() -> None:
    """
    Unauthenticated Requests Should Return 401.
    """

    # Request
    factory: APIRequestFactory = APIRequestFactory()
    request = factory.get("/api/users/username/change/request/")

    # Execute (No Auth)
    response = UserUsernameChangeRequestView.as_view()(request)

    # Assert
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


# 202 Success With New Token Test
def test_username_change_request_success_new_token_returns_202_and_side_effects() -> None:
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

    # Request
    factory: APIRequestFactory = APIRequestFactory()
    request = factory.get("/api/users/username/change/request/")
    force_authenticate(request, user=user)

    # Execute With Patches
    with (
        patch("apps.users.views.user_username_change_request_view.caches", cache_mapping),
        patch("apps.users.views.user_username_change_request_view.Site.objects.get_current", return_value=site_mock),
        patch(
            "apps.users.views.user_username_change_request_view.render_to_string",
            return_value="<html></html>",
        ) as render_mock,
        patch("apps.users.views.user_username_change_request_view.send_mail") as send_mail_mock,
        patch("apps.users.views.user_username_change_request_view.record_cache_operation") as rec_cache,
        patch("apps.users.views.user_username_change_request_view.record_token_generated") as rec_tok_gen,
        patch("apps.users.views.user_username_change_request_view.record_email_template_render_duration") as rec_tpl,
        patch("apps.users.views.user_username_change_request_view.record_email_sent") as rec_email,
        patch(
            "apps.users.views.user_username_change_request_view.record_username_change_request_initiated",
        ) as rec_init,
        patch("apps.users.views.user_username_change_request_view.record_http_request") as rec_http,
        patch("apps.users.views.user_username_change_request_view.record_user_action") as rec_action,
    ):
        response = UserUsernameChangeRequestView.as_view()(request)

    # Assert
    assert response.status_code == status.HTTP_202_ACCEPTED
    assert response.data == {"message": "Username Change Request Sent Successfully"}

    # Side Effects
    token_cache.set.assert_called_once()
    render_mock.assert_called_once()
    send_mail_mock.assert_called_once()

    # Metrics
    rec_cache.assert_called()
    rec_tok_gen.assert_called_once()
    rec_tpl.assert_called()
    rec_email.assert_called_with(email_type="username_change_request", success=True)
    rec_init.assert_called_once()
    rec_http.assert_called()
    rec_action.assert_called_with(action_type="username_change_request", success=True)


# 202 Success With Reused Token Test
def test_username_change_request_success_reused_token_returns_202_and_side_effects() -> None:
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
    cached: str = _make_valid_change_username_token(str(user.id))

    # Cache Mock: Existing Valid Token
    token_cache: MagicMock = MagicMock()
    token_cache.get.return_value = cached
    cache_mapping: dict[str, MagicMock] = {"token_cache": token_cache}

    # Site Mock
    site_mock: MagicMock = MagicMock(spec=Site)
    site_mock.domain = "example.com"

    # Request
    factory: APIRequestFactory = APIRequestFactory()
    request = factory.get("/api/users/username/change/request/")
    force_authenticate(request, user=user)

    # Execute With Patches
    with (
        patch("apps.users.views.user_username_change_request_view.caches", cache_mapping),
        patch("apps.users.views.user_username_change_request_view.Site.objects.get_current", return_value=site_mock),
        patch(
            "apps.users.views.user_username_change_request_view.render_to_string",
            return_value="<html></html>",
        ) as render_mock,
        patch("apps.users.views.user_username_change_request_view.send_mail") as send_mail_mock,
        patch("apps.users.views.user_username_change_request_view.record_cache_operation") as rec_cache,
        patch("apps.users.views.user_username_change_request_view.record_token_reused") as rec_tok_reuse,
        patch("apps.users.views.user_username_change_request_view.record_email_template_render_duration") as rec_tpl,
        patch("apps.users.views.user_username_change_request_view.record_email_sent") as rec_email,
        patch(
            "apps.users.views.user_username_change_request_view.record_username_change_request_initiated",
        ) as rec_init,
        patch("apps.users.views.user_username_change_request_view.record_http_request") as rec_http,
        patch("apps.users.views.user_username_change_request_view.record_user_action") as rec_action,
    ):
        response = UserUsernameChangeRequestView.as_view()(request)

    # Assert
    assert response.status_code == status.HTTP_202_ACCEPTED
    assert response.data == {"message": "Username Change Request Sent Successfully"}

    # Side Effects
    token_cache.set.assert_not_called()
    render_mock.assert_called_once()
    send_mail_mock.assert_called_once()

    # Metrics
    rec_cache.assert_called()
    rec_tok_reuse.assert_called_once()
    rec_tpl.assert_called()
    rec_email.assert_called_with(email_type="username_change_request", success=True)
    rec_init.assert_called_once()
    rec_http.assert_called()
    rec_action.assert_called_with(action_type="username_change_request", success=True)


# 202 Success With Invalid Cached Token Test
def test_username_change_request_invalid_cached_token_triggers_regeneration_and_succeeds() -> None:
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

    # Request
    factory: APIRequestFactory = APIRequestFactory()
    request = factory.get("/api/users/username/change/request/")
    force_authenticate(request, user=user)

    # Execute With Patches (jwt.decode Raises InvalidTokenError)
    with (
        patch("apps.users.views.user_username_change_request_view.caches", cache_mapping),
        patch("apps.users.views.user_username_change_request_view.Site.objects.get_current", return_value=site_mock),
        patch(
            "apps.users.views.user_username_change_request_view.render_to_string",
            return_value="<html></html>",
        ) as render_mock,
        patch("apps.users.views.user_username_change_request_view.send_mail") as send_mail_mock,
        patch("apps.users.views.user_username_change_request_view.jwt.decode", side_effect=jwt.InvalidTokenError()),
        patch("apps.users.views.user_username_change_request_view.record_cache_operation") as rec_cache,
        patch("apps.users.views.user_username_change_request_view.record_token_generated") as rec_tok_gen,
        patch("apps.users.views.user_username_change_request_view.record_token_reused") as rec_tok_reused,
        patch("apps.users.views.user_username_change_request_view.record_token_validation") as rec_tok_val,
        patch("apps.users.views.user_username_change_request_view.record_email_template_render_duration") as rec_tpl,
        patch("apps.users.views.user_username_change_request_view.record_email_sent") as rec_email,
        patch(
            "apps.users.views.user_username_change_request_view.record_username_change_request_initiated",
        ) as rec_init,
        patch("apps.users.views.user_username_change_request_view.record_http_request") as rec_http,
        patch("apps.users.views.user_username_change_request_view.record_user_action") as rec_action,
    ):
        response = UserUsernameChangeRequestView.as_view()(request)

    # Assert Response
    assert response.status_code == status.HTTP_202_ACCEPTED
    assert response.data == {"message": "Username Change Request Sent Successfully"}

    # Ensure Regeneration Path (set called, token_generated recorded, token_reused not called)
    token_cache.set.assert_called_once()
    rec_tok_gen.assert_called_once()
    rec_tok_reused.assert_not_called()

    # Email And Template
    render_mock.assert_called_once()
    send_mail_mock.assert_called_once()

    # Metrics
    rec_cache.assert_called()
    rec_tok_val.assert_called_with(token_type="username_change", success=False)
    rec_tpl.assert_called()
    rec_email.assert_called_with(email_type="username_change_request", success=True)
    rec_init.assert_called_once()
    rec_http.assert_called()
    rec_action.assert_called_with(action_type="username_change_request", success=True)


# 500 Email Failure Test
def test_username_change_request_email_failure_returns_500_and_records_metrics() -> None:
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

    # Request
    factory: APIRequestFactory = APIRequestFactory()
    request = factory.get("/api/users/username/change/request/")
    force_authenticate(request, user=user)

    # Execute With send_mail Error
    with (
        patch("apps.users.views.user_username_change_request_view.caches", cache_mapping),
        patch("apps.users.views.user_username_change_request_view.Site.objects.get_current", return_value=site_mock),
        patch("apps.users.views.user_username_change_request_view.render_to_string", return_value="<html></html>"),
        patch("apps.users.views.user_username_change_request_view.send_mail", side_effect=Exception("boom")),
        patch("apps.users.views.user_username_change_request_view.record_email_sent") as rec_email,
        patch("apps.users.views.user_username_change_request_view.record_api_error") as rec_api_error,
        patch("apps.users.views.user_username_change_request_view.record_http_request") as rec_http,
        patch("apps.users.views.user_username_change_request_view.record_user_action") as rec_action,
    ):
        response = UserUsernameChangeRequestView.as_view()(request)

    # Assert
    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert response.data == {"error": "Internal Server Error"}
    rec_email.assert_called_with(email_type="username_change_request", success=False)
    rec_api_error.assert_called()
    rec_http.assert_called()
    rec_action.assert_called_with(action_type="username_change_request", success=False)
