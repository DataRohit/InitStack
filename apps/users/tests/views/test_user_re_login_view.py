# ruff: noqa: S105

# Standard Library Imports
from typing import TYPE_CHECKING
from unittest.mock import MagicMock
from unittest.mock import patch

# Third Party Imports
import pytest
from django.conf import settings
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APIRequestFactory

# Local Imports
from apps.users.views.user_re_login_view import UserReLoginView

# If Type Checking
if TYPE_CHECKING:
    # Third Party Imports
    from rest_framework.request import Request

# Get User Model
User = get_user_model()

# Enable Django DB Access For All Tests In This Module
pytestmark = pytest.mark.django_db


# 400 Invalid Payload Test
def test_user_re_login_invalid_payload_returns_400() -> None:
    """
    Empty Payload Should Yield 400 With Errors.
    """

    # Request
    factory: APIRequestFactory = APIRequestFactory()
    request: Request = factory.post("/api/users/re-login/", data={}, format="json")

    # Patch Serializer And Metrics
    with (
        patch("apps.users.views.user_re_login_view.record_http_request") as rec_http,
        patch("apps.users.views.user_re_login_view.record_user_action") as rec_action,
    ):
        response = UserReLoginView.as_view()(request)

    # Assert
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "errors" in response.data
    rec_http.assert_called()
    rec_action.assert_called()


# 401 Missing Token Test (Post-Validation)
def test_user_re_login_missing_token_after_valid_serializer_returns_401() -> None:
    """
    Serializer Valid But Empty Refresh Token Should Yield 401 Invalid Token.
    """

    # Request
    factory: APIRequestFactory = APIRequestFactory()
    request: Request = factory.post(
        "/api/users/re-login/",
        data={"refresh_token": ""},
        format="json",
    )

    # Build Serializer Stub That Validates But Provides Empty Token
    class _StubSerializer:
        """
        Stub Serializer That Validates But Provides Empty Token.

        Attributes:
            data (dict[str, str]): Input Data.
            validated_data (dict[str, str]): Validated Data.
        """

        # Constructor
        def __init__(self, data: dict[str, str]) -> None:
            """
            Initialize Serializer With Empty Token.

            Args:
                data (dict[str, str]): Input Data.
            """

            # Instance Variables
            self.data = data
            self.validated_data = {"refresh_token": ""}

        # Methods
        def is_valid(self) -> bool:
            """
            Always Return True.

            Returns:
                bool: Always True.
            """

            # Return True
            return True

    # Patch Serializer And Metrics
    with (
        patch("apps.users.views.user_re_login_view.UserReLoginPayloadSerializer", _StubSerializer),
        patch("apps.users.views.user_re_login_view.record_http_request") as rec_http,
        patch("apps.users.views.user_re_login_view.record_user_action") as rec_action,
    ):
        response = UserReLoginView.as_view()(request)

    # Assert
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.data == {"error": "Invalid Token"}
    rec_http.assert_called()
    rec_action.assert_called()


# 401 Expired Token Test
def test_user_re_login_expired_token_returns_401() -> None:
    """
    Expired Refresh Token Should Yield 401 With Proper Error.
    """

    # Request
    factory: APIRequestFactory = APIRequestFactory()
    request: Request = factory.post(
        "/api/users/re-login/",
        data={"refresh_token": "ref.jwt"},
        format="json",
    )

    # Patch Decode To Raise Expired
    with (
        patch.object(settings, "PROJECT_NAME", "InitStack"),
        patch.object(settings, "REFRESH_TOKEN_SECRET", "rsec"),
        patch("apps.users.views.user_re_login_view.jwt.decode", side_effect=__import__("jwt").ExpiredSignatureError),
        patch("apps.users.views.user_re_login_view.record_token_validation") as rec_token,
        patch("apps.users.views.user_re_login_view.record_http_request") as rec_http,
        patch("apps.users.views.user_re_login_view.record_user_action") as rec_action,
    ):
        response = UserReLoginView.as_view()(request)

    # Assert
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.data == {"error": "Token Has Expired"}
    rec_token.assert_called_with(token_type="refresh", success=False)
    rec_http.assert_called()
    rec_action.assert_called()


# 401 Invalid Token Test
def test_user_re_login_invalid_token_returns_401() -> None:
    """
    Invalid Refresh Token Should Yield 401.
    """

    # Request
    factory: APIRequestFactory = APIRequestFactory()
    request: Request = factory.post(
        "/api/users/re-login/",
        data={"refresh_token": "bad.jwt"},
        format="json",
    )

    # Patch Decode To Raise InvalidTokenError
    with (
        patch.object(settings, "PROJECT_NAME", "InitStack"),
        patch.object(settings, "REFRESH_TOKEN_SECRET", "rsec"),
        patch("apps.users.views.user_re_login_view.jwt.decode", side_effect=__import__("jwt").InvalidTokenError),
        patch("apps.users.views.user_re_login_view.record_token_validation") as rec_token,
        patch("apps.users.views.user_re_login_view.record_http_request") as rec_http,
        patch("apps.users.views.user_re_login_view.record_user_action") as rec_action,
    ):
        response = UserReLoginView.as_view()(request)

    # Assert
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.data == {"error": "Invalid Token"}
    rec_token.assert_called_with(token_type="refresh", success=False)
    rec_http.assert_called()
    rec_action.assert_called()


# 401 Token Revoked Test
def test_user_re_login_revoked_token_returns_401() -> None:
    """
    If Token Does Not Match Cached Value, Treat As Revoked And Return 401.
    """

    # Request
    factory: APIRequestFactory = APIRequestFactory()
    provided_token: str = "ref.jwt"
    request: Request = factory.post(
        "/api/users/re-login/",
        data={"refresh_token": provided_token},
        format="json",
    )

    # Cache Mock With Different Token
    token_cache: MagicMock = MagicMock()
    token_cache.get.return_value = "different"
    cache_mapping: dict[str, MagicMock] = {"token_cache": token_cache}

    # Patch Decode To Provide Sub, Cache Get To Mismatch
    with (
        patch.object(settings, "PROJECT_NAME", "InitStack"),
        patch.object(settings, "REFRESH_TOKEN_SECRET", "rsec"),
        patch("apps.users.views.user_re_login_view.caches", cache_mapping),
        patch("apps.users.views.user_re_login_view.jwt.decode", return_value={"sub": "1"}),
        patch("apps.users.views.user_re_login_view.record_token_validation") as rec_token,
        patch("apps.users.views.user_re_login_view.record_cache_operation") as rec_cache,
        patch("apps.users.views.user_re_login_view.record_http_request") as rec_http,
        patch("apps.users.views.user_re_login_view.record_user_action") as rec_action,
    ):
        response = UserReLoginView.as_view()(request)

    # Assert
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.data == {"error": "Token Has Been Revoked"}
    rec_token.assert_called_with(token_type="refresh", success=True)
    rec_cache.assert_called()
    rec_http.assert_called()
    rec_action.assert_called()


# 401 User Not Found Test
def test_user_re_login_user_not_found_returns_401() -> None:
    """
    If User ID From Token Does Not Exist, Return 401.
    """

    # Request
    factory: APIRequestFactory = APIRequestFactory()
    token: str = "ref.jwt"
    request: Request = factory.post(
        "/api/users/re-login/",
        data={"refresh_token": token},
        format="json",
    )

    # Cache Mock With Same Token
    token_cache: MagicMock = MagicMock()
    token_cache.get.return_value = token
    cache_mapping: dict[str, MagicMock] = {"token_cache": token_cache}

    # Patch Decode To Provide Sub, But User Lookup Fails
    with (
        patch.object(settings, "PROJECT_NAME", "InitStack"),
        patch.object(settings, "REFRESH_TOKEN_SECRET", "rsec"),
        patch("apps.users.views.user_re_login_view.caches", cache_mapping),
        patch("apps.users.views.user_re_login_view.jwt.decode", return_value={"sub": "9999"}),
        patch("apps.users.views.user_re_login_view.User.objects.get", side_effect=User.DoesNotExist),
        patch("apps.users.views.user_re_login_view.record_http_request") as rec_http,
        patch("apps.users.views.user_re_login_view.record_user_action") as rec_action,
    ):
        response = UserReLoginView.as_view()(request)

    # Assert
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.data == {"error": "User Not Found"}
    rec_http.assert_called()
    rec_action.assert_called()


# 401 User Disabled Test
def test_user_re_login_user_disabled_returns_401() -> None:
    """
    If User Is Disabled, Return 401.
    """

    # Create Disabled User
    user = User.objects.create_user(
        username="disabled",
        email="disabled@example.com",
        password="SecurePassword@123",
        is_active=False,
    )

    # Request
    factory: APIRequestFactory = APIRequestFactory()
    token: str = "ref.jwt"
    request: Request = factory.post(
        "/api/users/re-login/",
        data={"refresh_token": token},
        format="json",
    )

    # Cache Mock With Same Token
    token_cache: MagicMock = MagicMock()
    token_cache.get.return_value = token
    cache_mapping: dict[str, MagicMock] = {"token_cache": token_cache}

    # Patch Decode To Provide Sub, User Lookup Returns Disabled User
    with (
        patch.object(settings, "PROJECT_NAME", "InitStack"),
        patch.object(settings, "REFRESH_TOKEN_SECRET", "rsec"),
        patch("apps.users.views.user_re_login_view.caches", cache_mapping),
        patch("apps.users.views.user_re_login_view.jwt.decode", return_value={"sub": str(user.id)}),
        patch("apps.users.views.user_re_login_view.User.objects.get", return_value=user),
        patch("apps.users.views.user_re_login_view.record_http_request") as rec_http,
        patch("apps.users.views.user_re_login_view.record_user_action") as rec_action,
    ):
        response = UserReLoginView.as_view()(request)

    # Assert
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.data == {"error": "User Account Is Disabled"}
    rec_http.assert_called()
    rec_action.assert_called()


# 200 Success Path Test
def test_user_re_login_success_returns_200_with_new_access() -> None:
    """
    Valid Refresh Token Matching Cache Should Issue New Access Token And Return 200.
    """

    # Create Active User
    user = User.objects.create_user(
        username="reloginok",
        email="reloginok@example.com",
        password="SecurePassword@123",
        is_active=True,
    )

    # Request
    factory: APIRequestFactory = APIRequestFactory()
    refresh_token: str = "ref.jwt"
    request: Request = factory.post(
        "/api/users/re-login/",
        data={"refresh_token": refresh_token},
        format="json",
    )

    # Cache Mock With Same Token
    token_cache: MagicMock = MagicMock()
    token_cache.get.return_value = refresh_token
    cache_mapping: dict[str, MagicMock] = {"token_cache": token_cache}

    # Patch Dependencies
    with (
        patch.object(settings, "PROJECT_NAME", "InitStack"),
        patch.object(settings, "ACCESS_TOKEN_SECRET", "asec"),
        patch.object(settings, "REFRESH_TOKEN_SECRET", "rsec"),
        patch.object(settings, "ACCESS_TOKEN_EXPIRY", 3600),
        patch("apps.users.views.user_re_login_view.caches", cache_mapping),
        patch("apps.users.views.user_re_login_view.jwt.decode", return_value={"sub": str(user.id)}),
        patch("apps.users.views.user_re_login_view.jwt.encode", return_value="acc.new"),
        patch("apps.users.views.user_re_login_view.User.objects.get", return_value=user),
        patch("apps.users.views.user_re_login_view.record_token_validation") as rec_token,
        patch("apps.users.views.user_re_login_view.record_cache_operation") as rec_cache,
        patch("apps.users.views.user_re_login_view.record_user_update") as rec_update,
        patch("apps.users.views.user_re_login_view.record_http_request") as rec_http,
        patch("apps.users.views.user_re_login_view.record_user_action") as rec_action,
        patch("apps.users.views.user_re_login_view.record_access_token_generated") as rec_acc_gen,
        patch("apps.users.views.user_re_login_view.record_re_login_initiated") as rec_re_login,
    ):
        response = UserReLoginView.as_view()(request)

    # Assert
    assert response.status_code == status.HTTP_200_OK
    assert response.data["access_token"] == "acc.new"
    assert response.data["refresh_token"] == refresh_token

    # Side Effects
    token_cache.set.assert_called_once()

    # Metrics
    rec_token.assert_called_with(token_type="refresh", success=True)
    rec_cache.assert_called()
    rec_update.assert_called_once()
    rec_http.assert_called()
    rec_action.assert_called()
    rec_acc_gen.assert_called_once()
    rec_re_login.assert_called_once()


# 500 Internal Error Test
def test_user_re_login_internal_error_returns_500() -> None:
    """
    Unexpected Exception Should Yield 500 And Record Metrics.
    """

    # Request
    factory: APIRequestFactory = APIRequestFactory()
    request: Request = factory.post(
        "/api/users/re-login/",
        data={"refresh_token": "tok"},
        format="json",
    )

    # Force Exception During Validation To Hit Global Exception Handler
    with (
        patch(
            "apps.users.views.user_re_login_view.UserReLoginPayloadSerializer.is_valid",
            side_effect=Exception("boom"),
        ),
        patch("apps.users.views.user_re_login_view.record_api_error") as rec_api_error,
        patch("apps.users.views.user_re_login_view.record_http_request") as rec_http,
        patch("apps.users.views.user_re_login_view.record_user_action") as rec_action,
    ):
        response = UserReLoginView.as_view()(request)

    # Assert
    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert response.data == {"error": "Internal Server Error"}

    # Metrics
    rec_api_error.assert_called()
    rec_http.assert_called()
    rec_action.assert_called()
