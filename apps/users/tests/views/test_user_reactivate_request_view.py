# Standard Library Imports
from typing import TYPE_CHECKING
from unittest.mock import MagicMock
from unittest.mock import patch

# Third Party Imports
import jwt
import pytest
from django.contrib.auth import get_user_model
from django.contrib.sites.models import Site
from rest_framework import status
from rest_framework.test import APIRequestFactory

# Local Imports
from apps.users.views.user_reactivate_request_view import UserReactivateRequestView

# If Type Checking
if TYPE_CHECKING:
    # Third Party Imports
    from rest_framework.request import Request

# Get User Model
User = get_user_model()

# Enable Django DB Access For All Tests In This Module
pytestmark = pytest.mark.django_db


# 400 Invalid Payload Test
def test_user_reactivate_request_invalid_payload_returns_400() -> None:
    """
    Empty Payload Should Yield 400 With Errors.
    """

    # Request
    factory: APIRequestFactory = APIRequestFactory()
    request: Request = factory.post("/api/users/reactivate/request/", data={}, format="json")

    # Patch Metrics
    with (
        patch("apps.users.views.user_reactivate_request_view.record_http_request") as rec_http,
        patch("apps.users.views.user_reactivate_request_view.record_user_action") as rec_action,
    ):
        response = UserReactivateRequestView.as_view()(request)

    # Assert
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "errors" in response.data
    rec_http.assert_not_called()
    rec_action.assert_not_called()


# 400 User Not Found Test
def test_user_reactivate_request_user_not_found_returns_400() -> None:
    """
    Unknown Identifier Should Yield 400 With Error.
    """

    # Request
    factory: APIRequestFactory = APIRequestFactory()
    request: Request = factory.post(
        "/api/users/reactivate/request/",
        data={"identifier": "nouser@example.com", "re_identifier": "nouser@example.com"},
        format="json",
    )

    # Patch Metrics
    with (
        patch("apps.users.views.user_reactivate_request_view.record_http_request") as rec_http,
        patch("apps.users.views.user_reactivate_request_view.record_user_action") as rec_action,
    ):
        response = UserReactivateRequestView.as_view()(request)

    # Assert
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.data == {"errors": {"identifier": ["No Account Found With This Identifier"]}}
    rec_http.assert_not_called()
    rec_action.assert_not_called()


# 400 Already Active Test
def test_user_reactivate_request_already_active_returns_400() -> None:
    """
    Active Account Should Yield 400 With Error.
    """

    # Create Active User
    user = User.objects.create_user(
        username="activeuser",
        email="activeuser@example.com",
        password="SecurePassword@123",
        is_active=True,
    )

    # Request
    factory: APIRequestFactory = APIRequestFactory()
    request: Request = factory.post(
        "/api/users/reactivate/request/",
        data={"identifier": user.email, "re_identifier": user.email},
        format="json",
    )

    # Patch Metrics
    with (
        patch("apps.users.views.user_reactivate_request_view.record_http_request") as rec_http,
        patch("apps.users.views.user_reactivate_request_view.record_user_action") as rec_action,
    ):
        response = UserReactivateRequestView.as_view()(request)

    # Assert
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.data == {"errors": {"identifier": ["Account Is Already Active"]}}
    rec_http.assert_not_called()
    rec_action.assert_not_called()


# 202 Success Test (New Token)
def test_user_reactivate_request_success_generates_new_token_returns_202() -> None:
    """
    Inactive Account Should Get New Reactivation Token And 202 Response.
    """

    # Create Inactive User
    user = User.objects.create_user(
        username="reactreq",
        email="reactreq@example.com",
        password="SecurePassword@123",
        is_active=False,
    )

    # Request
    factory: APIRequestFactory = APIRequestFactory()
    request: Request = factory.post(
        "/api/users/reactivate/request/",
        data={"identifier": user.email, "re_identifier": user.email},
        format="json",
    )

    # Cache Mock With No Token
    token_cache: MagicMock = MagicMock()
    token_cache.get.return_value = None
    cache_mapping: dict[str, MagicMock] = {"token_cache": token_cache}

    # Site Mock
    site_mock: MagicMock = MagicMock(spec=Site)
    site_mock.domain = "example.com"

    # Patch Dependencies
    with (
        patch("apps.users.views.user_reactivate_request_view.caches", cache_mapping),
        patch("apps.users.views.user_reactivate_request_view.Site.objects.get_current", return_value=site_mock),
        patch("apps.users.views.user_reactivate_request_view.send_mail") as send_mail_mock,
        patch("apps.users.views.user_reactivate_request_view.record_cache_operation") as rec_cache,
        patch("apps.users.views.user_reactivate_request_view.record_token_validation"),
        patch("apps.users.views.user_reactivate_request_view.record_token_generated") as rec_tok_gen,
        patch("apps.users.views.user_reactivate_request_view.record_email_template_render_duration") as rec_tpl,
        patch("apps.users.views.user_reactivate_request_view.record_email_sent") as rec_email,
        patch("apps.users.views.user_reactivate_request_view.record_reactivate_request_initiated") as rec_init,
        patch("apps.users.views.user_reactivate_request_view.record_http_request") as rec_http,
        patch("apps.users.views.user_reactivate_request_view.record_user_action") as rec_action,
    ):
        response = UserReactivateRequestView.as_view()(request)

    # Assert
    assert response.status_code == status.HTTP_202_ACCEPTED
    assert response.data["message"] == "Reactivation Request Sent Successfully"

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


# 202 Success Test (Reuse Token)
def test_user_reactivate_request_success_reuses_token_returns_202() -> None:
    """
    When Cached Token Is Valid, Reuse It And Return 202.
    """

    # Create Inactive User
    user = User.objects.create_user(
        username="reactreuse",
        email="reactreuse@example.com",
        password="SecurePassword@123",
        is_active=False,
    )

    # Request
    factory: APIRequestFactory = APIRequestFactory()
    request: Request = factory.post(
        "/api/users/reactivate/request/",
        data={"identifier": user.username, "re_identifier": user.username},
        format="json",
    )

    # Cache Mock With Existing Token
    cached: str = "tok.jwt"
    token_cache: MagicMock = MagicMock()
    token_cache.get.return_value = cached
    cache_mapping: dict[str, MagicMock] = {"token_cache": token_cache}

    # Site Mock
    site_mock: MagicMock = MagicMock(spec=Site)
    site_mock.domain = "example.com"

    # Patch Dependencies
    with (
        patch("apps.users.views.user_reactivate_request_view.caches", cache_mapping),
        patch("apps.users.views.user_reactivate_request_view.Site.objects.get_current", return_value=site_mock),
        patch("apps.users.views.user_reactivate_request_view.send_mail") as send_mail_mock,
        patch("apps.users.views.user_reactivate_request_view.jwt.decode", return_value={}),
        patch("apps.users.views.user_reactivate_request_view.record_cache_operation") as rec_cache,
        patch("apps.users.views.user_reactivate_request_view.record_token_validation") as rec_token,
        patch("apps.users.views.user_reactivate_request_view.record_token_reused") as rec_tok_reused,
        patch("apps.users.views.user_reactivate_request_view.record_email_template_render_duration") as rec_tpl,
        patch("apps.users.views.user_reactivate_request_view.record_email_sent") as rec_email,
        patch("apps.users.views.user_reactivate_request_view.record_reactivate_request_initiated") as rec_init,
        patch("apps.users.views.user_reactivate_request_view.record_http_request") as rec_http,
        patch("apps.users.views.user_reactivate_request_view.record_user_action") as rec_action,
    ):
        response = UserReactivateRequestView.as_view()(request)

    # Assert
    assert response.status_code == status.HTTP_202_ACCEPTED
    assert response.data["message"] == "Reactivation Request Sent Successfully"

    # Side Effects
    token_cache.set.assert_not_called()
    send_mail_mock.assert_called_once()

    # Metrics
    rec_cache.assert_called()
    rec_token.assert_called()
    rec_tok_reused.assert_called_once()
    rec_tpl.assert_called()
    rec_email.assert_called()
    rec_init.assert_called_once()
    rec_http.assert_called()
    rec_action.assert_called()


# 500 Internal Error Test
def test_user_reactivate_request_internal_error_returns_500() -> None:
    """
    Unexpected Exception During Email Send Should Yield 500 And Record Metrics.
    """

    # Create Inactive User
    user = User.objects.create_user(
        username="reacterr",
        email="reacterr@example.com",
        password="SecurePassword@123",
        is_active=False,
    )

    # Request
    factory: APIRequestFactory = APIRequestFactory()
    request: Request = factory.post(
        "/api/users/reactivate/request/",
        data={"identifier": user.email, "re_identifier": user.email},
        format="json",
    )

    # Cache Mock With No Token
    token_cache: MagicMock = MagicMock()
    token_cache.get.return_value = None
    cache_mapping: dict[str, MagicMock] = {"token_cache": token_cache}

    # Site Mock
    site_mock: MagicMock = MagicMock(spec=Site)
    site_mock.domain = "example.com"

    # Patch Dependencies And Force send_mail Error
    with (
        patch("apps.users.views.user_reactivate_request_view.caches", cache_mapping),
        patch("apps.users.views.user_reactivate_request_view.Site.objects.get_current", return_value=site_mock),
        patch("apps.users.views.user_reactivate_request_view.send_mail", side_effect=Exception("boom")),
        patch("apps.users.views.user_reactivate_request_view.record_api_error") as rec_api_error,
        patch("apps.users.views.user_reactivate_request_view.record_http_request") as rec_http,
        patch("apps.users.views.user_reactivate_request_view.record_user_action") as rec_action,
    ):
        response = UserReactivateRequestView.as_view()(request)

    # Assert
    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert response.data == {"status_code": status.HTTP_500_INTERNAL_SERVER_ERROR, "error": "Internal Server Error"}

    # Metrics
    rec_api_error.assert_called()
    rec_http.assert_called()
    rec_action.assert_called_with(action_type="reactivate_request", success=False)


# 202 Success Test (Invalid Cached Token -> Generate New Token)
def test_user_reactivate_request_invalid_cached_token_generates_new_token_returns_202() -> None:
    """
    Invalid Cached Token Should Record Validation Failure And Generate New Token.
    """

    # Create Inactive User
    user = User.objects.create_user(
        username="reactinvalid",
        email="reactinvalid@example.com",
        password="SecurePassword@123",
        is_active=False,
    )

    # Request
    factory: APIRequestFactory = APIRequestFactory()
    request: Request = factory.post(
        "/api/users/reactivate/request/",
        data={"identifier": user.email, "re_identifier": user.email},
        format="json",
    )

    # Cache Mock With Invalid Token
    cached: str = "bad.jwt"
    token_cache: MagicMock = MagicMock()
    token_cache.get.return_value = cached
    cache_mapping: dict[str, MagicMock] = {"token_cache": token_cache}

    # Site Mock
    site_mock: MagicMock = MagicMock(spec=Site)
    site_mock.domain = "example.com"

    # Patch Dependencies With jwt.decode Raising InvalidTokenError
    with (
        patch("apps.users.views.user_reactivate_request_view.caches", cache_mapping),
        patch("apps.users.views.user_reactivate_request_view.Site.objects.get_current", return_value=site_mock),
        patch("apps.users.views.user_reactivate_request_view.send_mail") as send_mail_mock,
        patch("apps.users.views.user_reactivate_request_view.jwt.decode", side_effect=jwt.InvalidTokenError("invalid")),
        patch("apps.users.views.user_reactivate_request_view.record_cache_operation") as rec_cache,
        patch("apps.users.views.user_reactivate_request_view.record_token_validation") as rec_token,
        patch("apps.users.views.user_reactivate_request_view.record_token_generated") as rec_tok_gen,
        patch("apps.users.views.user_reactivate_request_view.record_email_template_render_duration") as rec_tpl,
        patch("apps.users.views.user_reactivate_request_view.record_email_sent") as rec_email,
        patch("apps.users.views.user_reactivate_request_view.record_reactivate_request_initiated") as rec_init,
        patch("apps.users.views.user_reactivate_request_view.record_http_request") as rec_http,
        patch("apps.users.views.user_reactivate_request_view.record_user_action") as rec_action,
    ):
        response = UserReactivateRequestView.as_view()(request)

    # Assert
    assert response.status_code == status.HTTP_202_ACCEPTED
    assert response.data["message"] == "Reactivation Request Sent Successfully"

    # Side Effects
    token_cache.set.assert_called_once()
    send_mail_mock.assert_called_once()

    # Metrics
    rec_cache.assert_called()
    rec_token.assert_called()
    rec_tok_gen.assert_called_once()
    rec_tpl.assert_called()
    rec_email.assert_called()
    rec_init.assert_called_once()
    rec_http.assert_called()
    rec_action.assert_called()
