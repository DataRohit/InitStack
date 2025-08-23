# ruff: noqa: S105

# Third Party Imports
import datetime

import jwt
import pytest
from django.conf import settings as django_settings
from django.http import HttpResponseRedirect
from django.test import RequestFactory
from rest_framework import status
from slugify import slugify

# Local Imports
import apps.oauth.views.oauth_callback_view as callback_module
from apps.oauth.views.oauth_callback_view import OAuthCallbackView


# Fake Cache Adapter
class _FakeCache:
    """
    Simple In-Memory Cache For Tests.
    """

    # Init Store
    def __init__(self) -> None:
        """
        Initialize Cache Store.
        """

        # Store Dict
        self._store: dict[str, str] = {}

    # Get Value
    def get(self, key: str) -> str | None:
        """
        Get Value From Store.

        Args:
            key (str): Key To Get Value For.

        Returns:
            str | None: Value For Key If Found, Otherwise None.
        """

        # Return Value
        return self._store.get(key)

    # Set Value
    def set(self, key: str, value: str, timeout: int | None = None) -> None:
        """
        Set Value In Store.

        Args:
            key (str): Key To Set Value For.
            value (str): Value To Set.
            timeout (int | None, optional): Timeout For Value. Defaults to None.
        """

        # Set Value
        self._store[key] = value


# Base Patches Fixture
@pytest.fixture(autouse=True)
def _patch_metrics_and_cache(monkeypatch: pytest.MonkeyPatch) -> None:
    """
    Patch Metrics And Cache Dependencies.
    """

    # Patch Metrics No-Ops
    monkeypatch.setattr(callback_module, "record_callback_received", lambda: None)
    monkeypatch.setattr(callback_module, "record_callback_backend_loaded", lambda: None)
    monkeypatch.setattr(callback_module, "record_callback_complete_success", lambda: None)
    monkeypatch.setattr(callback_module, "record_callback_complete_failure", lambda: None)
    monkeypatch.setattr(callback_module, "record_cache_operation", lambda **kwargs: None)
    monkeypatch.setattr(callback_module, "record_user_action", lambda **kwargs: None)
    monkeypatch.setattr(callback_module, "record_http_request", lambda **kwargs: None)
    monkeypatch.setattr(callback_module, "record_token_validation", lambda **kwargs: None)
    monkeypatch.setattr(callback_module, "record_api_error", lambda **kwargs: None)

    # Patch Token Cache
    fake_cache = _FakeCache()
    monkeypatch.setattr(callback_module, "caches", {"token_cache": fake_cache})


# Patch Site Fixture
@pytest.fixture
def _patch_site(monkeypatch: pytest.MonkeyPatch) -> None:
    """
    Patch Current Site Domain.
    """

    # Fake Site Object
    class _Site:
        """
        Site Object.
        """

        # Domain Attr
        domain: str = "example.com"

        # Objects Manager
        class objects:  # noqa: N801
            """
            Site Objects Manager.
            """

            # Get Current Site
            @staticmethod
            def get_current() -> "_Site":
                """
                Get Current Site.

                Returns:
                    _Site: Current Site Object.
                """
                # Return Site
                return _Site()

    # Apply Patch
    monkeypatch.setattr(callback_module, "Site", _Site)


# Patch Serializers Fixture
@pytest.fixture
def _patch_user_serializer(monkeypatch: pytest.MonkeyPatch) -> None:
    """
    Patch UserDetailSerializer To Return Minimal Data.
    """

    # Fake Serializer
    class _FakeUserSerializer:
        """
        Fake User Serializer.
        """

        # Init With User
        def __init__(self, user: object) -> None:
            """
            Initialize Serializer With User Data.

            Args:
                user (object): User Object To Serialize.
            """

            # Data Attr
            self.data: dict[str, object] = {
                "id": "user-1",
                "username": "john",
                "email": "john@example.com",
                "first_name": "John",
                "last_name": "Doe",
                "is_active": True,
                "is_staff": False,
                "is_superuser": False,
                "date_joined": "2024-01-01T00:00:00Z",
                "last_login": "2024-01-01T00:00:00Z",
            }

    # Apply Patch
    monkeypatch.setattr(callback_module, "UserDetailSerializer", _FakeUserSerializer)


# Patch OAuth Backend Fixture
@pytest.fixture
def _patch_oauth(monkeypatch: pytest.MonkeyPatch) -> None:
    """
    Patch OAuth Strategy And Backend Loaders.
    """

    # Load Strategy
    monkeypatch.setattr(callback_module, "load_strategy", lambda request: object())

    # Load Backend
    def _load_backend(strategy: object, name: str, redirect_uri: str) -> object:
        """
        Load OAuth Backend.

        Args:
            strategy (object): OAuth Strategy Object.
            name (str): Backend Name.
            redirect_uri (str): Redirect URI.

        Returns:
            object: OAuth Backend Object.
        """

        # Return Backend
        return object()

    # Apply Patch
    monkeypatch.setattr(callback_module, "load_backend", _load_backend)


# Helper To Build Request
def _build_request(path: str, *, authenticated: bool) -> object:
    """
    Build DRF-Compatible Request.
    """

    # Build Request
    req = RequestFactory().get(path)

    # Add Security Flag
    req.is_secure = lambda: False  # type: ignore[method-assign]

    # Fake User Object
    class _User:
        """
        Fake User Object.
        """

        # Init Auth State
        def __init__(self, *, is_authenticated: bool) -> None:
            """
            Initialize User Object.

            Args:
                is_authenticated (bool): Authentication State.
            """

            # Auth Flag
            self.is_authenticated: bool = is_authenticated

            # Id Value
            self.id: int = 1

            # Last Login
            self.last_login = None

        # Save No-Op
        def save(self, update_fields: list[str] | None = None) -> None:
            """
            Save User Object.

            Args:
                update_fields (list[str] | None, optional): Fields to update. Defaults to None.
            """

    # Attach User
    req.user = _User(is_authenticated=authenticated)

    # Return Request
    return req


# OAuth Callback View: Redirect Result With Authenticated User
@pytest.mark.django_db
@pytest.mark.usefixtures("_patch_site", "_patch_user_serializer", "_patch_oauth")
def test_oauth_callback_view_redirect_authenticated_success(
    monkeypatch: pytest.MonkeyPatch,
    settings: django_settings,
) -> None:
    """
    Redirect With Authenticated User Should Return 200 With Tokens.
    """

    # Patch Settings
    settings.ACCESS_TOKEN_SECRET = "access-secret"
    settings.REFRESH_TOKEN_SECRET = "refresh-secret"
    settings.ACCESS_TOKEN_EXPIRY = 3600
    settings.REFRESH_TOKEN_EXPIRY = 7200
    settings.PROJECT_NAME = "InitStack"

    # Patch do_complete
    monkeypatch.setattr(callback_module, "do_complete", lambda **kwargs: HttpResponseRedirect("/"))

    # Build Request
    request = _build_request("/api/users/oauth/google/callback/", authenticated=True)

    # Call View
    response = OAuthCallbackView().get(request, backend_name="google")

    # Assert Status
    assert response.status_code == status.HTTP_200_OK

    # Assert Tokens Present
    assert "access_token" in response.data
    assert "refresh_token" in response.data


# OAuth Callback View: Redirect Result With Missing User
@pytest.mark.django_db
@pytest.mark.usefixtures("_patch_site", "_patch_oauth")
def test_oauth_callback_view_redirect_user_missing(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    Redirect With Anonymous User Should Return 400.
    """

    # Patch do_complete
    monkeypatch.setattr(callback_module, "do_complete", lambda **kwargs: HttpResponseRedirect("/"))

    # Build Request
    request = _build_request("/api/users/oauth/google/callback/", authenticated=False)

    # Call View
    response = OAuthCallbackView.as_view()(request, backend_name="google")

    # Assert Status
    assert response.status_code == status.HTTP_400_BAD_REQUEST

    # Assert Error Key
    assert response.data.get("error") == "User Not Found"


# OAuth Callback View: Dict Result With Authenticated User
@pytest.mark.django_db
@pytest.mark.usefixtures("_patch_site", "_patch_user_serializer", "_patch_oauth")
def test_oauth_callback_view_result_dict_authenticated_success(
    monkeypatch: pytest.MonkeyPatch,
    settings: django_settings,
) -> None:
    """
    Dict Result With Authenticated User Should Return 200 With Tokens.
    """

    # Patch Settings
    settings.ACCESS_TOKEN_SECRET = "access-secret"
    settings.REFRESH_TOKEN_SECRET = "refresh-secret"
    settings.ACCESS_TOKEN_EXPIRY = 3600
    settings.REFRESH_TOKEN_EXPIRY = 7200
    settings.PROJECT_NAME = "InitStack"

    # Patch do_complete
    monkeypatch.setattr(callback_module, "do_complete", lambda **kwargs: {})

    # Build Request
    request = _build_request("/api/users/oauth/google/callback/", authenticated=True)

    # Call View
    response = OAuthCallbackView().get(request, backend_name="google")

    # Assert Status
    assert response.status_code == status.HTTP_200_OK

    # Assert Tokens Present
    assert "access_token" in response.data
    assert "refresh_token" in response.data


# OAuth Callback View: Invalid Result Returns 400
@pytest.mark.django_db
@pytest.mark.usefixtures("_patch_site", "_patch_oauth")
def test_oauth_callback_view_invalid_result_returns_400(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    Invalid Result Should Return 400.
    """

    # Patch do_complete
    monkeypatch.setattr(callback_module, "do_complete", lambda **kwargs: None)

    # Build Request
    request = _build_request("/api/users/oauth/google/callback/", authenticated=False)

    # Call View
    response = OAuthCallbackView.as_view()(request, backend_name="google")

    # Assert Status
    assert response.status_code == status.HTTP_400_BAD_REQUEST

    # Assert Error Key
    assert response.data.get("error") == "Authentication Failed"


# OAuth Callback View: Dict Result With Missing User Returns 400
@pytest.mark.django_db
@pytest.mark.usefixtures("_patch_site", "_patch_oauth")
def test_oauth_callback_view_result_dict_user_missing(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    Dict Result With Anonymous User Should Return 400 User Not Found.
    """

    # Patch do_complete
    monkeypatch.setattr(callback_module, "do_complete", lambda **kwargs: {})

    # Build Request
    request = _build_request("/api/users/oauth/google/callback/", authenticated=False)

    # Call View
    response = OAuthCallbackView.as_view()(request, backend_name="google")

    # Assert Status
    assert response.status_code == status.HTTP_400_BAD_REQUEST

    # Assert Error Key
    assert response.data.get("error") == "User Not Found"


# OAuth Callback View: Exception Returns 500
@pytest.mark.django_db
@pytest.mark.usefixtures("_patch_site", "_patch_oauth")
def test_oauth_callback_view_exception_returns_500(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    Exception Should Return 500.
    """

    # Patch do_complete To Raise
    def _raise(**kwargs):
        # Set Error Message
        error_message = "boom"

        # Raise Error
        raise RuntimeError(error_message)

    # Apply Patch
    monkeypatch.setattr(callback_module, "do_complete", _raise)

    # Build Request
    request = _build_request("/api/users/oauth/google/callback/", authenticated=False)

    # Call View
    response = OAuthCallbackView.as_view()(request, backend_name="google")

    # Assert Status
    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR

    # Assert Error Key
    assert response.data.get("error") == "Internal Server Error"


# OAuth Callback View: Redirect Reuses Valid Tokens With Authenticated User
@pytest.mark.django_db
@pytest.mark.usefixtures("_patch_site", "_patch_user_serializer", "_patch_oauth")
def test_oauth_callback_view_redirect_authenticated_reuse_tokens(
    monkeypatch: pytest.MonkeyPatch,
    settings: django_settings,
) -> None:
    """
    Redirect With Authenticated User Should Reuse Valid Tokens From Cache.
    """

    # Patch Settings
    settings.ACCESS_TOKEN_SECRET = "access-secret"
    settings.REFRESH_TOKEN_SECRET = "refresh-secret"
    settings.ACCESS_TOKEN_EXPIRY = 3600
    settings.REFRESH_TOKEN_EXPIRY = 7200
    settings.PROJECT_NAME = "InitStack"

    # Patch do_complete
    monkeypatch.setattr(callback_module, "do_complete", lambda **kwargs: HttpResponseRedirect("/"))

    # Build Request
    request = _build_request("/api/users/oauth/google/callback/", authenticated=True)

    # Prepare Valid Cached Tokens
    now_dt: datetime.datetime = datetime.datetime.now(tz=datetime.UTC)
    user_id_str: str = "1"
    access_payload: dict[str, object] = {
        "sub": user_id_str,
        "iss": slugify(settings.PROJECT_NAME),
        "aud": slugify(settings.PROJECT_NAME),
        "iat": now_dt,
        "exp": now_dt + datetime.timedelta(seconds=settings.ACCESS_TOKEN_EXPIRY),
    }
    refresh_payload: dict[str, object] = {
        "sub": user_id_str,
        "iss": slugify(settings.PROJECT_NAME),
        "aud": slugify(settings.PROJECT_NAME),
        "iat": now_dt,
        "exp": now_dt + datetime.timedelta(seconds=settings.REFRESH_TOKEN_EXPIRY),
    }
    cached_access_token: str = jwt.encode(access_payload, key=settings.ACCESS_TOKEN_SECRET, algorithm="HS256")
    cached_refresh_token: str = jwt.encode(refresh_payload, key=settings.REFRESH_TOKEN_SECRET, algorithm="HS256")

    # Seed Fake Cache
    token_cache = callback_module.caches["token_cache"]
    token_cache.set(f"access_token_{user_id_str}", cached_access_token, timeout=settings.ACCESS_TOKEN_EXPIRY)
    token_cache.set(f"refresh_token_{user_id_str}", cached_refresh_token, timeout=settings.REFRESH_TOKEN_EXPIRY)

    # Call View
    response = OAuthCallbackView().get(request, backend_name="google")

    # Assert Status
    assert response.status_code == status.HTTP_200_OK

    # Assert Tokens Were Reused
    assert response.data.get("access_token") == cached_access_token
    assert response.data.get("refresh_token") == cached_refresh_token


# OAuth Callback View: Redirect With Invalid Cached Tokens Generates New Ones
@pytest.mark.django_db
@pytest.mark.usefixtures("_patch_site", "_patch_user_serializer", "_patch_oauth")
def test_oauth_callback_view_redirect_authenticated_invalid_cached_tokens(
    monkeypatch: pytest.MonkeyPatch,
    settings: django_settings,
) -> None:
    """
    Redirect With Authenticated User And Invalid Cached Tokens Should Regenerate Tokens.
    """

    # Patch Settings
    settings.ACCESS_TOKEN_SECRET = "access-secret"
    settings.REFRESH_TOKEN_SECRET = "refresh-secret"
    settings.ACCESS_TOKEN_EXPIRY = 3600
    settings.REFRESH_TOKEN_EXPIRY = 7200
    settings.PROJECT_NAME = "InitStack"

    # Patch do_complete
    monkeypatch.setattr(callback_module, "do_complete", lambda **kwargs: HttpResponseRedirect("/"))

    # Build Request
    request = _build_request("/api/users/oauth/google/callback/", authenticated=True)

    # Seed Fake Cache With Invalid Tokens
    user_id_str: str = "1"
    token_cache = callback_module.caches["token_cache"]
    invalid_access: str = "invalid.access.token"
    invalid_refresh: str = "invalid.refresh.token"
    token_cache.set(f"access_token_{user_id_str}", invalid_access, timeout=settings.ACCESS_TOKEN_EXPIRY)
    token_cache.set(f"refresh_token_{user_id_str}", invalid_refresh, timeout=settings.REFRESH_TOKEN_EXPIRY)

    # Call View
    response = OAuthCallbackView().get(request, backend_name="google")

    # Assert Status
    assert response.status_code == status.HTTP_200_OK

    # Assert Tokens Were Regenerated (Not Equal To Invalid Ones)
    assert response.data.get("access_token") != invalid_access
    assert response.data.get("refresh_token") != invalid_refresh
