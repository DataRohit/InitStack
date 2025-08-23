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
from rest_framework.test import force_authenticate

# Local Imports
from apps.users.views.user_deactivate_request_view import UserDeactivateRequestView

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


# Generate Token And Send Email Test
def test_user_deactivate_request_view_generates_token_and_sends_email_returns_202() -> None:
    """
    Verify When No Valid Token Exists, A New Token Is Generated, Cached, Email Sent, 202 Returned.
    """

    # Create User
    user = User.objects.create_user(
        username="reqgen",
        email="reqgen@example.com",
        first_name="Req",
        last_name="Gen",
        password="SecurePassword@123",
        is_active=True,
    )

    # Inputs
    new_token: str = "new.deactivation.token"

    # Build Request
    factory: APIRequestFactory = APIRequestFactory()
    request: Request = factory.get("/api/users/deactivate/request/")
    force_authenticate(request, user=user)

    # Build Cache Mock With No Token
    token_cache: MagicMock = _build_token_cache_mock(get_value=None)
    cache_mapping: dict[str, Any] = {"token_cache": token_cache}

    # Patch Dependencies
    with (
        patch.object(settings, "DEACTIVATION_TOKEN_SECRET", "secret"),
        patch.object(settings, "DEACTIVATION_TOKEN_EXPIRY", 3600),
        patch.object(settings, "DEFAULT_FROM_EMAIL", "noreply@example.com"),
        patch.object(settings, "PROJECT_NAME", "InitStack"),
        patch("apps.users.views.user_deactivate_request_view.caches", cache_mapping),
        patch("apps.users.views.user_deactivate_request_view.jwt.encode", return_value=new_token) as mock_jwt_encode,
        patch("apps.users.views.user_deactivate_request_view.Site.objects.get_current") as mock_get_current,
        patch(
            "apps.users.views.user_deactivate_request_view.render_to_string",
            return_value="<html>ok</html>",
        ) as mock_render,
        patch("apps.users.views.user_deactivate_request_view.send_mail") as mock_send_mail,
        patch("apps.users.views.user_deactivate_request_view.record_token_validation"),
        patch("apps.users.views.user_deactivate_request_view.record_cache_operation") as rec_cache,
        patch("apps.users.views.user_deactivate_request_view.record_user_action") as rec_action,
        patch("apps.users.views.user_deactivate_request_view.record_http_request"),
        patch("apps.users.views.user_deactivate_request_view.record_email_sent"),
        patch("apps.users.views.user_deactivate_request_view.record_deactivate_request_initiated"),
        patch("apps.users.views.user_deactivate_request_view.record_token_generated"),
        patch("apps.users.views.user_deactivate_request_view.record_email_template_render_duration"),
    ):
        # Configure Site
        site_mock: MagicMock = MagicMock()
        site_mock.domain = "example.com"
        mock_get_current.return_value = site_mock

        # Call View
        response = UserDeactivateRequestView.as_view()(request)

    # Assert Response
    assert response.status_code == status.HTTP_202_ACCEPTED
    assert response.data == {"message": "Deactivation Request Sent Successfully"}

    # Assert Token Generated, Cached, And Email Sent
    mock_jwt_encode.assert_called_once()
    token_cache.set.assert_called_once()
    mock_render.assert_called_once()
    mock_send_mail.assert_called_once()

    # Assert Metrics
    rec_cache.assert_called()
    rec_action.assert_called()


# Invalid Cached Token Test
def test_user_deactivate_request_view_invalid_cached_token_generates_new_token_returns_202() -> None:
    """
    Verify When Cached Token Exists But Is Invalid, A New Token Is Generated, Cached, Email Sent, 202 Returned.
    """

    # Create User
    user = User.objects.create_user(
        username="reqinvalid",
        email="reqinvalid@example.com",
        first_name="Req",
        last_name="Invalid",
        password="SecurePassword@123",
        is_active=True,
    )

    # Inputs
    cached_token: str = "invalid.cached.token"
    new_token: str = "new.from.invalid.path"

    # Build Request
    factory: APIRequestFactory = APIRequestFactory()
    request: Request = factory.get("/api/users/deactivate/request/")
    force_authenticate(request, user=user)

    # Build Cache Mock With Invalid Token Present
    token_cache: MagicMock = _build_token_cache_mock(get_value=cached_token)
    cache_mapping: dict[str, Any] = {"token_cache": token_cache}

    # Patch Dependencies
    with (
        patch.object(settings, "DEACTIVATION_TOKEN_SECRET", "secret"),
        patch.object(settings, "DEACTIVATION_TOKEN_EXPIRY", 3600),
        patch.object(settings, "DEFAULT_FROM_EMAIL", "noreply@example.com"),
        patch.object(settings, "PROJECT_NAME", "InitStack"),
        patch("apps.users.views.user_deactivate_request_view.caches", cache_mapping),
        patch("apps.users.views.user_deactivate_request_view.jwt.decode", side_effect=jwt.InvalidTokenError("bad")),
        patch("apps.users.views.user_deactivate_request_view.jwt.encode", return_value=new_token) as mock_jwt_encode,
        patch("apps.users.views.user_deactivate_request_view.Site.objects.get_current") as mock_get_current,
        patch(
            "apps.users.views.user_deactivate_request_view.render_to_string",
            return_value="<html>ok</html>",
        ) as mock_render,
        patch("apps.users.views.user_deactivate_request_view.send_mail") as mock_send_mail,
        patch("apps.users.views.user_deactivate_request_view.record_token_validation") as rec_token,
        patch("apps.users.views.user_deactivate_request_view.record_cache_operation") as rec_cache,
        patch("apps.users.views.user_deactivate_request_view.record_user_action") as rec_action,
        patch("apps.users.views.user_deactivate_request_view.record_http_request") as rec_http,
        patch("apps.users.views.user_deactivate_request_view.record_email_sent") as rec_email,
        patch("apps.users.views.user_deactivate_request_view.record_deactivate_request_initiated") as rec_initiated,
        patch("apps.users.views.user_deactivate_request_view.record_token_generated") as rec_generated,
        patch("apps.users.views.user_deactivate_request_view.record_email_template_render_duration") as rec_template,
    ):
        # Configure Site
        site_mock: MagicMock = MagicMock()
        site_mock.domain = "example.com"
        mock_get_current.return_value = site_mock

        # Call View
        response = UserDeactivateRequestView.as_view()(request)

    # Assert Response
    assert response.status_code == status.HTTP_202_ACCEPTED
    assert response.data == {"message": "Deactivation Request Sent Successfully"}

    # Assert New Token Generated And Cached, And Email Sent
    mock_jwt_encode.assert_called_once()
    token_cache.set.assert_called_once()
    mock_render.assert_called_once()
    mock_send_mail.assert_called_once()

    # Assert Metrics Include Validation Failure And Generation Path
    rec_token.assert_called()
    rec_cache.assert_called()
    rec_action.assert_called()
    rec_http.assert_called()
    rec_email.assert_called()
    rec_initiated.assert_called_once()
    rec_generated.assert_called_once()
    rec_template.assert_called()
    rec_http.assert_called()
    rec_email.assert_called()
    rec_initiated.assert_called_once()
    rec_generated.assert_called_once()
    rec_template.assert_called()


# Reuse Valid Token Test
def test_user_deactivate_request_view_reuses_valid_token_returns_202() -> None:
    """
    Verify When Valid Token Exists, It Is Reused, Email Sent, 202 Returned.
    """

    # Create User
    user = User.objects.create_user(
        username="reqreuse",
        email="reqreuse@example.com",
        first_name="Req",
        last_name="Reuse",
        password="SecurePassword@123",
        is_active=True,
    )

    # Inputs
    cached_token: str = "valid.deactivation.token"

    # Build Request
    factory: APIRequestFactory = APIRequestFactory()
    request: Request = factory.get("/api/users/deactivate/request/")
    force_authenticate(request, user=user)

    # Build Cache Mock With Valid Token
    token_cache: MagicMock = _build_token_cache_mock(get_value=cached_token)
    cache_mapping: dict[str, Any] = {"token_cache": token_cache}

    # Patch Dependencies
    with (
        patch.object(settings, "DEACTIVATION_TOKEN_SECRET", "secret"),
        patch.object(settings, "DEACTIVATION_TOKEN_EXPIRY", 3600),
        patch.object(settings, "DEFAULT_FROM_EMAIL", "noreply@example.com"),
        patch.object(settings, "PROJECT_NAME", "InitStack"),
        patch("apps.users.views.user_deactivate_request_view.caches", cache_mapping),
        patch("apps.users.views.user_deactivate_request_view.jwt.decode", return_value={}),
        patch("apps.users.views.user_deactivate_request_view.Site.objects.get_current") as mock_get_current,
        patch(
            "apps.users.views.user_deactivate_request_view.render_to_string",
            return_value="<html>ok</html>",
        ) as mock_render,
        patch("apps.users.views.user_deactivate_request_view.send_mail") as mock_send_mail,
        patch("apps.users.views.user_deactivate_request_view.record_token_validation") as rec_token,
        patch("apps.users.views.user_deactivate_request_view.record_cache_operation") as rec_cache,
        patch("apps.users.views.user_deactivate_request_view.record_user_action") as rec_action,
        patch("apps.users.views.user_deactivate_request_view.record_http_request") as rec_http,
        patch("apps.users.views.user_deactivate_request_view.record_email_sent") as rec_email,
        patch("apps.users.views.user_deactivate_request_view.record_deactivate_request_initiated") as rec_initiated,
        patch("apps.users.views.user_deactivate_request_view.record_token_reused") as rec_reused,
        patch("apps.users.views.user_deactivate_request_view.record_email_template_render_duration") as rec_template,
    ):
        # Configure Site
        site_mock: MagicMock = MagicMock()
        site_mock.domain = "example.com"
        mock_get_current.return_value = site_mock

        # Call View
        response = UserDeactivateRequestView.as_view()(request)

    # Assert Response
    assert response.status_code == status.HTTP_202_ACCEPTED
    assert response.data == {"message": "Deactivation Request Sent Successfully"}

    # Assert Token Reused, No Cache Set, And Email Sent
    token_cache.set.assert_not_called()
    mock_render.assert_called_once()
    mock_send_mail.assert_called_once()

    # Assert Metrics
    rec_token.assert_called()
    rec_cache.assert_called()
    rec_action.assert_called()
    rec_http.assert_called()
    rec_email.assert_called()
    rec_initiated.assert_called_once()
    rec_reused.assert_called_once()
    rec_template.assert_called()


# Email Send Failure Test
def test_user_deactivate_request_view_email_send_failure_returns_500() -> None:
    """
    Verify Email Send Exception Yields 500 And Records Metrics, Including User Action Failure.
    """

    # Create User
    user = User.objects.create_user(
        username="reqerr",
        email="reqerr@example.com",
        first_name="Req",
        last_name="Err",
        password="SecurePassword@123",
        is_active=True,
    )

    # Inputs
    cached_token: str = "valid.deactivation.token"

    # Build Request
    factory: APIRequestFactory = APIRequestFactory()
    request: Request = factory.get("/api/users/deactivate/request/")
    force_authenticate(request, user=user)

    # Build Cache Mock With Valid Token
    token_cache: MagicMock = _build_token_cache_mock(get_value=cached_token)
    cache_mapping: dict[str, Any] = {"token_cache": token_cache}

    # Patch Dependencies
    with (
        patch.object(settings, "DEACTIVATION_TOKEN_SECRET", "secret"),
        patch.object(settings, "DEACTIVATION_TOKEN_EXPIRY", 3600),
        patch.object(settings, "DEFAULT_FROM_EMAIL", "noreply@example.com"),
        patch.object(settings, "PROJECT_NAME", "InitStack"),
        patch("apps.users.views.user_deactivate_request_view.caches", cache_mapping),
        patch("apps.users.views.user_deactivate_request_view.jwt.decode", return_value={}),
        patch("apps.users.views.user_deactivate_request_view.Site.objects.get_current") as mock_get_current,
        patch("apps.users.views.user_deactivate_request_view.render_to_string", return_value="<html>ok</html>"),
        patch(
            "apps.users.views.user_deactivate_request_view.send_mail",
            side_effect=Exception("boom"),
        ) as mock_send_mail,
        patch("apps.users.views.user_deactivate_request_view.record_email_sent") as rec_email,
        patch("apps.users.views.user_deactivate_request_view.record_email_template_render_duration") as rec_template,
        patch("apps.users.views.user_deactivate_request_view.record_api_error") as rec_api_error,
        patch("apps.users.views.user_deactivate_request_view.record_http_request") as rec_http,
        patch("apps.users.views.user_deactivate_request_view.record_user_action") as rec_action,
    ):
        # Configure Site
        site_mock: MagicMock = MagicMock()
        site_mock.domain = "example.com"
        mock_get_current.return_value = site_mock

        # Call View
        response = UserDeactivateRequestView.as_view()(request)

    # Assert Response
    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert response.data == {"error": "Internal Server Error"}

    # Assert Email Attempted And Failure Recorded
    mock_send_mail.assert_called_once()
    rec_email.assert_called()
    rec_template.assert_called()

    # Assert Error Metrics Recorded (Includes User Action Failure In Outer Except)
    rec_api_error.assert_called()
    rec_http.assert_called()
    rec_action.assert_called()
