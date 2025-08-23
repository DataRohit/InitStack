# ruff: noqa: S105, PLR2004

# Standard Library Imports
from typing import TYPE_CHECKING
from typing import Any
from unittest.mock import MagicMock
from unittest.mock import patch

# Third Party Imports
import pytest
from django.conf import settings
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APIRequestFactory

# Local Imports
from apps.users.views.user_login_view import UserLoginView

# If Type Checking
if TYPE_CHECKING:
    # Third Party Imports
    from rest_framework.request import Request

# Get User Model
User = get_user_model()

# Enable Django DB Access For All Tests In This Module
pytestmark = pytest.mark.django_db


# Build Token Cache Mock Function
def _build_token_cache_mock(access_value: str | None, refresh_value: str | None) -> MagicMock:
    """
    Build Token Cache Mock With Configurable Get Return For Access/Refresh Keys.

    Args:
        access_value (str | None): Access Token Value.
        refresh_value (str | None): Refresh Token Value.

    Returns:
        MagicMock: Cache Mock.
    """

    # Create Mock
    m: MagicMock = MagicMock()

    # Configure Get
    def _get(key: str) -> str | None:
        """
        Return Token Based On Key.

        Args:
            key (str): Cache Key.

        Returns:
            str | None: Token Value Or None.
        """

        # If Access Token Key
        if key.startswith("access_token_"):
            # Return Access Token
            return access_value

        # If Refresh Token Key
        if key.startswith("refresh_token_"):
            # Return Refresh Token
            return refresh_value

        # Return None
        return None

    m.get.side_effect = _get

    # Return Mock
    return m


# 400 Invalid Payload Test
def test_user_login_invalid_payload_returns_400() -> None:
    """
    Empty Payload Should Yield 400 With Errors.
    """

    # Request
    factory: APIRequestFactory = APIRequestFactory()
    request: Request = factory.post("/api/users/login/", data={}, format="json")

    # Patch Minimal Metrics
    with (
        patch("apps.users.views.user_login_view.record_http_request") as rec_http,
        patch("apps.users.views.user_login_view.record_user_action") as rec_action,
    ):
        response = UserLoginView.as_view()(request)

    # Assert
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "errors" in response.data
    rec_http.assert_called()
    rec_action.assert_called()


# 401 Social Auth Registered Test
def test_user_login_social_auth_registered_returns_401() -> None:
    """
    If UserSocialAuth Exists For Identifier, Return 401 With Proper Error.
    """

    # Request
    factory: APIRequestFactory = APIRequestFactory()
    request: Request = factory.post(
        "/api/users/login/",
        data={"identifier": "someone", "password": "x"},
        format="json",
    )

    # Patch Social Auth Get To Return Object
    with (
        patch("apps.users.views.user_login_view.UserSocialAuth.objects.get", return_value=MagicMock()),
        patch("apps.users.views.user_login_view.record_http_request") as rec_http,
        patch("apps.users.views.user_login_view.record_user_action") as rec_action,
    ):
        response = UserLoginView.as_view()(request)

    # Assert
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.data == {"error": "User Registered With Social Auth"}
    rec_http.assert_called()
    rec_action.assert_called()


# 401 User Does Not Exist Test
def test_user_login_user_not_found_returns_401() -> None:
    """
    If No Matching User, Return 401.
    """

    # Request
    factory: APIRequestFactory = APIRequestFactory()
    request: Request = factory.post(
        "/api/users/login/",
        data={"identifier": "nouser@example.com", "password": "pass"},
        format="json",
    )

    # Patch User Get To Raise DoesNotExist
    with (
        patch("apps.users.views.user_login_view.User.objects.get", side_effect=User.DoesNotExist),
        patch("apps.users.views.user_login_view.record_http_request") as rec_http,
        patch("apps.users.views.user_login_view.record_user_action") as rec_action,
    ):
        response = UserLoginView.as_view()(request)

    # Assert
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.data == {"error": "Invalid Username Or Password"}
    rec_http.assert_called()
    rec_action.assert_called()


# 401 Inactive User Test
def test_user_login_inactive_user_returns_401() -> None:
    """
    Inactive Users Should Not Be Able To Login.
    """

    # Create Inactive User
    user = User.objects.create_user(
        username="inactive",
        email="inactive@example.com",
        password="SecurePassword@123",
        is_active=False,
    )

    # Request
    factory: APIRequestFactory = APIRequestFactory()
    request: Request = factory.post(
        "/api/users/login/",
        data={"identifier": user.username, "password": "SecurePassword@123"},
        format="json",
    )

    # Patch Direct User Retrieval
    with (
        patch("apps.users.views.user_login_view.User.objects.get", return_value=user),
        patch("apps.users.views.user_login_view.record_http_request") as rec_http,
        patch("apps.users.views.user_login_view.record_user_action") as rec_action,
    ):
        response = UserLoginView.as_view()(request)

    # Assert
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.data == {"error": "User Is Not Active"}
    rec_http.assert_called()
    rec_action.assert_called()


# 401 Invalid Password Test
def test_user_login_invalid_password_returns_401() -> None:
    """
    Wrong Password Should Yield 401.
    """

    # Create Active User
    user = User.objects.create_user(
        username="badpass",
        email="badpass@example.com",
        password="CorrectPassword@123",
        is_active=True,
    )

    # Request
    factory: APIRequestFactory = APIRequestFactory()
    request: Request = factory.post(
        "/api/users/login/",
        data={"identifier": user.username, "password": "WrongPassword"},
        format="json",
    )

    # Patch User Retrieval
    with (
        patch("apps.users.views.user_login_view.User.objects.get", return_value=user),
        patch("apps.users.views.user_login_view.record_http_request") as rec_http,
        patch("apps.users.views.user_login_view.record_user_action") as rec_action,
    ):
        response = UserLoginView.as_view()(request)

    # Assert
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.data == {"error": "Invalid Username Or Password"}
    rec_http.assert_called()
    rec_action.assert_called()


# 200 Success With New Tokens Test
def test_user_login_success_generates_both_tokens_returns_200() -> None:
    """
    If No Cached Tokens, Generate Both And Return 200 With Tokens.
    """

    # Create Active User
    user = User.objects.create_user(
        username="logingen",
        email="logingen@example.com",
        password="SecurePassword@123",
        is_active=True,
    )

    # Request
    factory: APIRequestFactory = APIRequestFactory()
    request: Request = factory.post(
        "/api/users/login/",
        data={"identifier": user.username, "password": "SecurePassword@123"},
        format="json",
    )

    # Cache Missing Tokens
    token_cache: MagicMock = _build_token_cache_mock(access_value=None, refresh_value=None)
    cache_mapping: dict[str, Any] = {"token_cache": token_cache}

    # Patch Dependencies
    with (
        patch.object(settings, "PROJECT_NAME", "InitStack"),
        patch.object(settings, "ACCESS_TOKEN_SECRET", "asec"),
        patch.object(settings, "REFRESH_TOKEN_SECRET", "rsec"),
        patch.object(settings, "ACCESS_TOKEN_EXPIRY", 3600),
        patch.object(settings, "REFRESH_TOKEN_EXPIRY", 7200),
        patch("apps.users.views.user_login_view.caches", cache_mapping),
        patch("apps.users.views.user_login_view.User.objects.get", return_value=user),
        patch("apps.users.views.user_login_view.jwt.encode", side_effect=["acc.t", "ref.t"]) as mock_jwt_encode,
        patch("apps.users.views.user_login_view.record_token_validation"),
        patch("apps.users.views.user_login_view.record_cache_operation") as rec_cache,
        patch("apps.users.views.user_login_view.record_http_request") as rec_http,
        patch("apps.users.views.user_login_view.record_user_action") as rec_action,
        patch("apps.users.views.user_login_view.record_access_token_generated") as rec_acc_gen,
        patch("apps.users.views.user_login_view.record_refresh_token_generated") as rec_ref_gen,
        patch("apps.users.views.user_login_view.record_login_initiated") as rec_login,
    ):
        response = UserLoginView.as_view()(request)

    # Assert
    assert response.status_code == status.HTTP_200_OK
    assert response.data["access_token"] == "acc.t"
    assert response.data["refresh_token"] == "ref.t"

    # Side Effects
    assert token_cache.set.call_count == 2
    assert mock_jwt_encode.call_count == 2

    # Metrics
    rec_cache.assert_called()
    rec_http.assert_called()
    rec_action.assert_called()
    rec_acc_gen.assert_called_once()
    rec_ref_gen.assert_called_once()
    rec_login.assert_called_once()


# 200 Success Reuse Access, Generate Refresh Test
def test_user_login_success_reuse_access_generate_refresh_returns_200() -> None:
    """
    If Access Valid And Refresh Invalid, Reuse Access And Generate Refresh.
    """

    # Create Active User
    user = User.objects.create_user(
        username="loginreuse",
        email="loginreuse@example.com",
        password="SecurePassword@123",
        is_active=True,
    )

    # Request
    factory: APIRequestFactory = APIRequestFactory()
    request: Request = factory.post(
        "/api/users/login/",
        data={"identifier": user.username, "password": "SecurePassword@123"},
        format="json",
    )

    # Cache With Valid Access And No Refresh
    token_cache: MagicMock = _build_token_cache_mock(access_value="acc.cached", refresh_value=None)
    cache_mapping: dict[str, Any] = {"token_cache": token_cache}

    # Patch Dependencies
    with (
        patch.object(settings, "PROJECT_NAME", "InitStack"),
        patch.object(settings, "ACCESS_TOKEN_SECRET", "asec"),
        patch.object(settings, "REFRESH_TOKEN_SECRET", "rsec"),
        patch.object(settings, "ACCESS_TOKEN_EXPIRY", 3600),
        patch.object(settings, "REFRESH_TOKEN_EXPIRY", 7200),
        patch("apps.users.views.user_login_view.caches", cache_mapping),
        patch("apps.users.views.user_login_view.User.objects.get", return_value=user),
        patch("apps.users.views.user_login_view.jwt.decode", return_value={}),
        patch("apps.users.views.user_login_view.jwt.encode", return_value="ref.new") as mock_jwt_encode,
        patch("apps.users.views.user_login_view.record_token_validation") as rec_token,
        patch("apps.users.views.user_login_view.record_cache_operation") as rec_cache,
        patch("apps.users.views.user_login_view.record_http_request") as rec_http,
        patch("apps.users.views.user_login_view.record_user_action") as rec_action,
        patch("apps.users.views.user_login_view.record_access_token_reused") as rec_acc_reused,
        patch("apps.users.views.user_login_view.record_refresh_token_generated") as rec_ref_gen,
        patch("apps.users.views.user_login_view.record_login_initiated") as rec_login,
    ):
        response = UserLoginView.as_view()(request)

    # Assert
    assert response.status_code == status.HTTP_200_OK
    assert response.data["access_token"] == "acc.cached"
    assert response.data["refresh_token"] == "ref.new"

    # Side Effects
    token_cache.set.assert_called_once()
    mock_jwt_encode.assert_called_once()

    # Metrics
    rec_token.assert_called()
    rec_cache.assert_called()
    rec_http.assert_called()
    rec_action.assert_called()
    rec_acc_reused.assert_called_once()
    rec_ref_gen.assert_called_once()
    rec_login.assert_called_once()


# 200 Success Reuse Both Tokens Test
def test_user_login_success_reuse_both_tokens_returns_200() -> None:
    """
    If Both Cached Tokens Are Valid, Reuse Both And Return 200.
    """

    # Create Active User
    user = User.objects.create_user(
        username="loginreuseboth",
        email="loginreuseboth@example.com",
        password="SecurePassword@123",
        is_active=True,
    )

    # Request
    factory: APIRequestFactory = APIRequestFactory()
    request: Request = factory.post(
        "/api/users/login/",
        data={"identifier": user.username, "password": "SecurePassword@123"},
        format="json",
    )

    # Cache With Valid Access And Refresh
    token_cache: MagicMock = _build_token_cache_mock(access_value="acc.ok", refresh_value="ref.ok")
    cache_mapping: dict[str, Any] = {"token_cache": token_cache}

    # Patch Dependencies
    with (
        patch.object(settings, "PROJECT_NAME", "InitStack"),
        patch.object(settings, "ACCESS_TOKEN_SECRET", "asec"),
        patch.object(settings, "REFRESH_TOKEN_SECRET", "rsec"),
        patch("apps.users.views.user_login_view.caches", cache_mapping),
        patch("apps.users.views.user_login_view.User.objects.get", return_value=user),
        patch("apps.users.views.user_login_view.jwt.decode", return_value={}),
        patch("apps.users.views.user_login_view.record_token_validation") as rec_token,
        patch("apps.users.views.user_login_view.record_cache_operation") as rec_cache,
        patch("apps.users.views.user_login_view.record_http_request") as rec_http,
        patch("apps.users.views.user_login_view.record_user_action") as rec_action,
        patch("apps.users.views.user_login_view.record_access_token_reused") as rec_acc_reused,
        patch("apps.users.views.user_login_view.record_refresh_token_reused") as rec_ref_reused,
        patch("apps.users.views.user_login_view.record_login_initiated") as rec_login,
    ):
        response = UserLoginView.as_view()(request)

    # Assert
    assert response.status_code == status.HTTP_200_OK
    assert response.data["access_token"] == "acc.ok"
    assert response.data["refresh_token"] == "ref.ok"

    # Side Effects
    token_cache.set.assert_not_called()

    # Metrics
    rec_token.assert_called()
    rec_cache.assert_called()
    rec_http.assert_called()
    rec_action.assert_called()
    rec_acc_reused.assert_called_once()
    rec_ref_reused.assert_called_once()
    rec_login.assert_called_once()


# 500 Internal Error Path Test
def test_user_login_internal_error_returns_500() -> None:
    """
    Unexpected Exception Should Trigger 500 Error Response And Metrics.
    """

    # Request With Valid-Looking Payload
    factory: APIRequestFactory = APIRequestFactory()
    request: Request = factory.post(
        "/api/users/login/",
        data={"identifier": "any", "password": "pwd"},
        format="json",
    )

    # Force Exception During User Lookup
    with (
        patch("apps.users.views.user_login_view.User.objects.get", side_effect=Exception("boom")),
        patch("apps.users.views.user_login_view.record_api_error") as rec_api_error,
        patch("apps.users.views.user_login_view.record_http_request") as rec_http,
        patch("apps.users.views.user_login_view.record_user_action") as rec_action,
    ):
        response = UserLoginView.as_view()(request)

    # Assert
    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert response.data == {"error": "Internal Server Error"}

    # Metrics
    rec_api_error.assert_called()
    rec_http.assert_called()
    rec_action.assert_called()
