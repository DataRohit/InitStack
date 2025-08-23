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
from apps.users.views.user_delete_confirm_view import UserDeleteConfirmView

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


# Successful Deletion Test
def test_user_delete_confirm_view_success_returns_204() -> None:
    """
    Verify View Deletes User, Revokes Tokens, Sends Email, Returns 204.
    """

    # Create User
    user = User.objects.create_user(
        username="todelete",
        email="todelete@example.com",
        first_name="To",
        last_name="Delete",
        password="SecurePassword@123",
        is_active=True,
    )

    # Inputs
    token: str = "valid.deletion.token"
    payload: dict[str, Any] = {"sub": str(user.id)}

    # Build Request
    factory: APIRequestFactory = APIRequestFactory()
    request: Request = factory.get("/api/users/delete/confirm/<token>/")

    # Build Cache Mock With Matching Token
    token_cache: MagicMock = _build_token_cache_mock(expected_token=token)
    cache_mapping: dict[str, Any] = {"token_cache": token_cache}

    # Patch Dependencies
    with (
        patch.object(settings, "DELETION_TOKEN_SECRET", "secret"),
        patch.object(settings, "DEFAULT_FROM_EMAIL", "noreply@example.com"),
        patch.object(settings, "PROJECT_NAME", "InitStack"),
        patch("apps.users.views.user_delete_confirm_view.caches", cache_mapping),
        patch("apps.users.views.user_delete_confirm_view.jwt.decode", return_value=payload),
        patch("apps.users.views.user_delete_confirm_view.render_to_string", return_value="<html>ok</html>"),
        patch("apps.users.views.user_delete_confirm_view.send_mail") as mock_send_mail,
        patch("apps.users.views.user_delete_confirm_view.record_token_validation") as rec_token,
        patch("apps.users.views.user_delete_confirm_view.record_cache_operation") as rec_cache,
        patch("apps.users.views.user_delete_confirm_view.record_user_update") as rec_update,
        patch("apps.users.views.user_delete_confirm_view.record_user_action") as rec_action,
        patch("apps.users.views.user_delete_confirm_view.record_http_request") as rec_http,
        patch("apps.users.views.user_delete_confirm_view.record_email_sent") as rec_email,
        patch("apps.users.views.user_delete_confirm_view.record_deletion_performed") as rec_deleted,
        patch("apps.users.views.user_delete_confirm_view.record_tokens_revoked") as rec_revoked,
        patch("apps.users.views.user_delete_confirm_view.record_email_template_render_duration") as rec_template,
    ):
        # Call View
        response = UserDeleteConfirmView.as_view()(request, token=token)

    # Assert Response
    assert response.status_code == status.HTTP_204_NO_CONTENT

    # Assert Cache Delete Called For Tokens
    token_cache.delete.assert_any_call(f"deletion_token_{user.id}")
    token_cache.delete.assert_any_call(f"access_token_{user.id}")
    token_cache.delete.assert_any_call(f"refresh_token_{user.id}")

    # Assert Email And Metrics
    mock_send_mail.assert_called_once()
    rec_token.assert_called()
    rec_cache.assert_called()
    rec_update.assert_called()
    rec_action.assert_called()
    rec_http.assert_called()
    rec_email.assert_called()
    rec_deleted.assert_called_once()
    rec_revoked.assert_any_call(token_type="deletion")
    rec_revoked.assert_any_call(token_type="access")
    rec_revoked.assert_any_call(token_type="refresh")
    rec_template.assert_called()


# Invalid Token Test
def test_user_delete_confirm_view_invalid_token_returns_401() -> None:
    """
    Verify Invalid Token Returns 401 Unauthorized.
    """

    # Inputs
    token: str = "bad.token"

    # Build Request
    factory: APIRequestFactory = APIRequestFactory()
    request: Request = factory.get("/api/users/delete/confirm/<token>/")

    # Patch Dependencies
    with (
        patch.object(settings, "DELETION_TOKEN_SECRET", "secret"),
        patch.object(settings, "PROJECT_NAME", "InitStack"),
        patch("apps.users.views.user_delete_confirm_view.jwt.decode", side_effect=jwt.InvalidTokenError("bad")),
        patch("apps.users.views.user_delete_confirm_view.record_token_validation") as rec_token,
        patch("apps.users.views.user_delete_confirm_view.record_user_action") as rec_action,
        patch("apps.users.views.user_delete_confirm_view.record_http_request") as rec_http,
    ):
        # Call View
        response = UserDeleteConfirmView.as_view()(request, token=token)

    # Assert Response
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.data == {"error": "Invalid Deletion Token"}

    # Assert Metrics
    rec_token.assert_called()
    rec_action.assert_called()
    rec_http.assert_called()


# Token Mismatch Test
def test_user_delete_confirm_view_token_mismatch_returns_401() -> None:
    """
    Verify Cache Miss Or Mismatch Returns 401 Unauthorized.
    """

    # Create User
    user = User.objects.create_user(
        username="del_mismatch",
        email="del_mismatch@example.com",
        first_name="Del",
        last_name="Mismatch",
        password="SecurePassword@123",
        is_active=True,
    )

    # Inputs
    token: str = "some.token"
    payload: dict[str, Any] = {"sub": str(user.id)}

    # Build Request
    factory: APIRequestFactory = APIRequestFactory()
    request: Request = factory.get("/api/users/delete/confirm/<token>/")

    # Build Cache Mock With None To Simulate Miss
    token_cache: MagicMock = _build_token_cache_mock(expected_token=None)
    cache_mapping: dict[str, Any] = {"token_cache": token_cache}

    # Patch Dependencies
    with (
        patch.object(settings, "DELETION_TOKEN_SECRET", "secret"),
        patch.object(settings, "PROJECT_NAME", "InitStack"),
        patch("apps.users.views.user_delete_confirm_view.caches", cache_mapping),
        patch("apps.users.views.user_delete_confirm_view.jwt.decode", return_value=payload),
        patch("apps.users.views.user_delete_confirm_view.record_token_validation") as rec_token,
        patch("apps.users.views.user_delete_confirm_view.record_cache_operation") as rec_cache,
        patch("apps.users.views.user_delete_confirm_view.record_user_action") as rec_action,
        patch("apps.users.views.user_delete_confirm_view.record_http_request") as rec_http,
        patch("apps.users.views.user_delete_confirm_view.record_token_cache_mismatch") as rec_mismatch,
    ):
        # Call View
        response = UserDeleteConfirmView.as_view()(request, token=token)

    # Assert Response
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.data == {"error": "Invalid Or Expired Deletion Token"}

    # Assert Metrics
    rec_token.assert_called()
    rec_cache.assert_called()
    rec_action.assert_called()
    rec_http.assert_called()
    rec_mismatch.assert_called_once()


# Email Send Failure Test
def test_user_delete_confirm_view_email_send_failure_returns_500() -> None:
    """
    Verify Email Send Exception Yields 500 And Records Metrics.
    """

    # Create User
    user = User.objects.create_user(
        username="emailfaildel",
        email="emailfaildel@example.com",
        first_name="Email",
        last_name="FailDel",
        password="SecurePassword@123",
        is_active=True,
    )

    # Inputs
    token: str = "valid.deletion.token"
    payload: dict[str, Any] = {"sub": str(user.id)}

    # Build Request
    factory: APIRequestFactory = APIRequestFactory()
    request: Request = factory.get("/api/users/delete/confirm/<token>/")

    # Build Cache Mock With Matching Token
    token_cache: MagicMock = _build_token_cache_mock(expected_token=token)
    cache_mapping: dict[str, Any] = {"token_cache": token_cache}

    # Patch Dependencies
    with (
        patch.object(settings, "DELETION_TOKEN_SECRET", "secret"),
        patch.object(settings, "DEFAULT_FROM_EMAIL", "noreply@example.com"),
        patch.object(settings, "PROJECT_NAME", "InitStack"),
        patch("apps.users.views.user_delete_confirm_view.caches", cache_mapping),
        patch("apps.users.views.user_delete_confirm_view.jwt.decode", return_value=payload),
        patch("apps.users.views.user_delete_confirm_view.render_to_string", return_value="<html>ok</html>"),
        patch("apps.users.views.user_delete_confirm_view.send_mail", side_effect=Exception("boom")) as mock_send_mail,
        patch("apps.users.views.user_delete_confirm_view.record_email_sent") as rec_email,
        patch("apps.users.views.user_delete_confirm_view.record_email_template_render_duration") as rec_template,
        patch("apps.users.views.user_delete_confirm_view.record_api_error") as rec_api_error,
        patch("apps.users.views.user_delete_confirm_view.record_http_request") as rec_http,
        patch("apps.users.views.user_delete_confirm_view.record_user_action"),
        patch("apps.users.views.user_delete_confirm_view.record_user_update") as rec_update,
    ):
        # Call View
        response = UserDeleteConfirmView.as_view()(request, token=token)

    # Assert Response
    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert response.data == {"error": "Internal Server Error"}

    # Assert Email Attempted And Failure Recorded
    mock_send_mail.assert_called_once()
    rec_email.assert_called()
    rec_template.assert_called()

    # Assert Error Metrics Recorded (Outer Except Does Not Record User Action Here)
    rec_api_error.assert_called()
    rec_http.assert_called()
    rec_update.assert_called()
