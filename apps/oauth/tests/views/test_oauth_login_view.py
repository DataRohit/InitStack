# Third Party Imports
import pytest
from django.test import RequestFactory
from rest_framework import status

# Local Imports
import apps.oauth.views.oauth_login_view as login_module
from apps.oauth.views.oauth_login_view import OAuthLoginView


# Base Patches Fixture
@pytest.fixture(autouse=True)
def _patch_metrics(monkeypatch: pytest.MonkeyPatch) -> None:
    """
    Patch Metrics Dependencies.
    """

    # Patch Metrics No-Ops
    monkeypatch.setattr(login_module, "record_oauth_login_initiated", lambda: None)
    monkeypatch.setattr(login_module, "record_redirect_uri_built", lambda: None)
    monkeypatch.setattr(login_module, "record_backend_loaded", lambda: None)
    monkeypatch.setattr(login_module, "record_auth_url_generated", lambda: None)
    monkeypatch.setattr(login_module, "record_user_action", lambda **kwargs: None)
    monkeypatch.setattr(login_module, "record_http_request", lambda **kwargs: None)
    monkeypatch.setattr(login_module, "record_api_error", lambda **kwargs: None)


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
    monkeypatch.setattr(login_module, "Site", _Site)


# Patch OAuth Backend Fixture
@pytest.fixture
def _patch_oauth(monkeypatch: pytest.MonkeyPatch) -> None:
    """
    Patch OAuth Strategy And Backend Loaders.
    """

    # Load Strategy
    monkeypatch.setattr(login_module, "load_strategy", lambda request: object())

    # Fake Backend With Auth URL
    class _Backend:
        """
        Fake OAuth Backend.
        """

        # Return Auth URL
        def auth_url(self) -> str:
            """
            Build Auth URL.

            Returns:
                str: Authorization URL.
            """

            # Return URL
            return "https://provider.example.com/auth"

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
        return _Backend()

    # Apply Patch
    monkeypatch.setattr(login_module, "load_backend", _load_backend)


# Helper To Build Request
def _build_request(path: str) -> object:
    """
    Build DRF-Compatible Request.
    """

    # Build Request
    req = RequestFactory().get(path)

    # Add Security Flag
    req.is_secure = lambda: False  # type: ignore[method-assign]

    # Return Request
    return req


# OAuth Login View: Success Returns Auth URL
@pytest.mark.django_db
@pytest.mark.usefixtures("_patch_site", "_patch_oauth")
def test_oauth_login_view_success() -> None:
    """
    Successful Login Should Return 200 With Auth URL.
    """

    # Build Request
    request = _build_request("/api/users/oauth/google-oauth2/login/")

    # Call View
    response = OAuthLoginView.as_view()(request, backend_name="google-oauth2")

    # Assert Status
    assert response.status_code == status.HTTP_200_OK

    # Assert Auth URL Key
    assert response.data.get("auth_url") == "https://provider.example.com/auth"


# OAuth Login View: Exception Returns 500
@pytest.mark.django_db
@pytest.mark.usefixtures("_patch_site")
def test_oauth_login_view_exception_returns_500(monkeypatch: pytest.MonkeyPatch) -> None:
    """
    Exception Should Return 500.
    """

    # Load Strategy
    monkeypatch.setattr(login_module, "load_strategy", lambda request: object())

    # Load Backend That Raises
    def _raise_backend(*args, **kwargs) -> object:
        """
        Raise While Loading Backend.

        Returns:
            object: Unused.
        """

        # Set Error Message
        error_message: str = "boom"

        # Raise Error
        raise RuntimeError(error_message)

    # Apply Patch
    monkeypatch.setattr(login_module, "load_backend", _raise_backend)

    # Build Request
    request = _build_request("/api/users/oauth/google-oauth2/login/")

    # Call View
    response = OAuthLoginView.as_view()(request, backend_name="google-oauth2")

    # Assert Status
    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR

    # Assert Error Key
    assert response.data.get("error") == "Internal Server Error"
