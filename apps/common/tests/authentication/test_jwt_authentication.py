# Standard Library Imports
from types import SimpleNamespace
from typing import Any
from unittest.mock import MagicMock
from unittest.mock import patch

# Third Party Imports
import jwt
import pytest
from django.core.cache import BaseCache
from rest_framework import exceptions

# Local Imports
from apps.common.authentication.jwt_authentication import JWTAuthentication


# JWT Authentication Fixture
@pytest.fixture
def jwt_auth() -> JWTAuthentication:
    """
    Create JWTAuthentication Instance.
    """

    # Return Instance
    return JWTAuthentication()


# Mock Cache Fixture
@pytest.fixture
def mock_token_cache() -> MagicMock:
    """
    Create Mock Token Cache Backend.
    """

    # Create And Return Mock Cache
    return MagicMock(spec=BaseCache)


# Test JWTAuthentication Class
class TestJWTAuthentication:
    """
    Test JWTAuthentication Backend.
    """

    # Test Authenticate Raises On Missing Header
    @patch("apps.common.authentication.jwt_authentication.authentication.get_authorization_header", return_value=b"")
    def test_authenticate_missing_header(self, mock_get_auth: MagicMock, jwt_auth: JWTAuthentication) -> None:
        """
        Test Missing Authorization Header Raises Error.
        """

        # Create Dummy Request
        request: Any = SimpleNamespace()

        # Assert Raises Authentication Failed
        with pytest.raises(exceptions.AuthenticationFailed) as exc:
            # Call Authenticate
            jwt_auth.authenticate(request)

        # Assert Error Message
        assert exc.value.detail == {"error": "Authentication Credentials Were Not Provided"}

    # Test Authenticate Raises On Non Bearer Scheme
    @patch(
        "apps.common.authentication.jwt_authentication.authentication.get_authorization_header",
        return_value=b"Basic abc",
    )
    def test_authenticate_non_bearer(self, mock_get_auth: MagicMock, jwt_auth: JWTAuthentication) -> None:
        """
        Test Non Bearer Scheme Raises Error.
        """

        # Create Dummy Request
        request: Any = SimpleNamespace()

        # Assert Raises Authentication Failed
        with pytest.raises(exceptions.AuthenticationFailed) as exc:
            # Call Authenticate
            jwt_auth.authenticate(request)

        # Assert Error Message
        assert exc.value.detail == {"error": "Authentication Credentials Were Not Provided"}

    # Test Authenticate Raises On Invalid Header Parts
    @patch(
        "apps.common.authentication.jwt_authentication.authentication.get_authorization_header",
        return_value=b"Bearer a b",
    )
    def test_authenticate_invalid_parts(self, mock_get_auth: MagicMock, jwt_auth: JWTAuthentication) -> None:
        """
        Test Invalid Authorization Header Parts Raise Error.
        """

        # Create Dummy Request
        request: Any = SimpleNamespace()

        # Assert Raises Authentication Failed
        with pytest.raises(exceptions.AuthenticationFailed) as exc:
            # Call Authenticate
            jwt_auth.authenticate(request)

        # Assert Error Message
        assert exc.value.detail == {"error": "Invalid Authorization Header"}

    # Test Authenticate Raises On Unicode Error
    @patch(
        "apps.common.authentication.jwt_authentication.authentication.get_authorization_header",
        return_value=b"Bearer \xff\xfe",
    )
    def test_authenticate_unicode_error(self, mock_get_auth: MagicMock, jwt_auth: JWTAuthentication) -> None:
        """
        Test Unicode Error While Decoding Token Raises Error.
        """

        # Create Dummy Request
        request: Any = SimpleNamespace()

        # Assert Raises Authentication Failed
        with pytest.raises(exceptions.AuthenticationFailed) as exc:
            # Call Authenticate
            jwt_auth.authenticate(request)

        # Assert Error Message
        assert exc.value.detail == {"error": "Invalid Token Format"}

    # Test Authenticate Delegates To Authenticate Credentials
    @patch(
        "apps.common.authentication.jwt_authentication.authentication.get_authorization_header",
        return_value=b"Bearer token123",
    )
    def test_authenticate_delegates(self, mock_get_auth: MagicMock, jwt_auth: JWTAuthentication) -> None:
        """
        Test Authenticate Delegates To Authenticate Credentials.
        """

        # Patch Authenticate Credentials
        with patch.object(
            JWTAuthentication,
            "authenticate_credentials",
            return_value=(MagicMock(), "token123"),
        ) as mock_creds:
            # Call Authenticate
            result = jwt_auth.authenticate(SimpleNamespace())

        # Assert Result
        assert isinstance(result, tuple)
        assert result[1] == "token123"

        # Assert Delegate Called
        mock_creds.assert_called_once_with("token123")

    # Test Authenticate Credentials Raises On Empty Token
    def test_authenticate_credentials_empty_token(self, jwt_auth: JWTAuthentication) -> None:
        """
        Test Empty Token Raises Error.
        """

        # Assert Raises Authentication Failed
        with pytest.raises(exceptions.AuthenticationFailed) as exc:
            # Call Authenticate Credentials
            jwt_auth.authenticate_credentials("")

        # Assert Error Message
        assert exc.value.detail == {"error": "Invalid Token"}

    # Test Token Expired Error
    def test_authenticate_credentials_token_expired(
        self,
        jwt_auth: JWTAuthentication,
        mock_token_cache: MagicMock,
        monkeypatch,
    ) -> None:
        """
        Test Expired Token Raises Proper Error.
        """

        # Create Token
        token: str = "expired.token"  # noqa: S105

        # Patch Caches
        fake_caches: MagicMock = MagicMock()
        fake_caches.__getitem__.return_value = mock_token_cache
        monkeypatch.setattr("apps.common.authentication.jwt_authentication.caches", fake_caches)

        # Patch JWT Decode To Raise ExpiredSignatureError
        monkeypatch.setattr(
            "apps.common.authentication.jwt_authentication.jwt.decode",
            MagicMock(side_effect=jwt.ExpiredSignatureError()),
        )

        # Assert Raises
        with pytest.raises(exceptions.AuthenticationFailed) as exc:
            # Call Authenticate Credentials
            jwt_auth.authenticate_credentials(token)

        # Assert Message
        assert exc.value.detail == {"error": "Token Has Expired"}

    # Test Invalid Token Error
    def test_authenticate_credentials_invalid_token(
        self,
        jwt_auth: JWTAuthentication,
        mock_token_cache: MagicMock,
        monkeypatch,
    ) -> None:
        """
        Test Invalid Token Raises Proper Error.
        """

        # Create Token
        token: str = "bad.token"  # noqa: S105

        # Patch Caches
        fake_caches: MagicMock = MagicMock()
        fake_caches.__getitem__.return_value = mock_token_cache
        monkeypatch.setattr("apps.common.authentication.jwt_authentication.caches", fake_caches)

        # Patch JWT Decode To Raise InvalidTokenError
        monkeypatch.setattr(
            "apps.common.authentication.jwt_authentication.jwt.decode",
            MagicMock(side_effect=jwt.InvalidTokenError()),
        )

        # Assert Raises
        with pytest.raises(exceptions.AuthenticationFailed) as exc:
            # Call Authenticate Credentials
            jwt_auth.authenticate_credentials(token)

        # Assert Message
        assert exc.value.detail == {"error": "Invalid Token"}

    # Test Revoked Token When Cache Miss
    def test_authenticate_credentials_revoked_token_miss(
        self,
        jwt_auth: JWTAuthentication,
        mock_token_cache: MagicMock,
        monkeypatch,
    ) -> None:
        """
        Test Revoked Token When Cache Miss.
        """

        # Token And Payload
        token: str = "tok123"  # noqa: S105
        payload: dict[str, Any] = {"sub": "user-id-1"}

        # Patch Caches And JWT Decode
        fake_caches: MagicMock = MagicMock()
        fake_caches.__getitem__.return_value = mock_token_cache
        mock_token_cache.get.return_value = None
        monkeypatch.setattr("apps.common.authentication.jwt_authentication.caches", fake_caches)
        monkeypatch.setattr("apps.common.authentication.jwt_authentication.jwt.decode", MagicMock(return_value=payload))

        # Assert Raises
        with pytest.raises(exceptions.AuthenticationFailed) as exc:
            # Call Authenticate Credentials
            jwt_auth.authenticate_credentials(token)

        # Assert Message
        assert exc.value.detail == {"error": "Token Has Been Revoked"}

    # Test Revoked Token When Cache Mismatch
    def test_authenticate_credentials_revoked_token_mismatch(
        self,
        jwt_auth: JWTAuthentication,
        mock_token_cache: MagicMock,
        monkeypatch,
    ) -> None:
        """
        Test Revoked Token When Cache Mismatch.
        """

        # Token And Payload
        token: str = "tok123"  # noqa: S105
        payload: dict[str, Any] = {"sub": "user-id-1"}

        # Patch Caches And JWT Decode
        fake_caches: MagicMock = MagicMock()
        fake_caches.__getitem__.return_value = mock_token_cache
        mock_token_cache.get.return_value = "different"
        monkeypatch.setattr("apps.common.authentication.jwt_authentication.caches", fake_caches)
        monkeypatch.setattr("apps.common.authentication.jwt_authentication.jwt.decode", MagicMock(return_value=payload))

        # Assert Raises
        with pytest.raises(exceptions.AuthenticationFailed) as exc:
            # Call Authenticate Credentials
            jwt_auth.authenticate_credentials(token)

        # Assert Message
        assert exc.value.detail == {"error": "Token Has Been Revoked"}

    # Test User Not Found
    def test_authenticate_credentials_user_not_found(
        self,
        jwt_auth: JWTAuthentication,
        mock_token_cache: MagicMock,
        monkeypatch,
    ) -> None:
        """
        Test User Not Found Raises Error.
        """

        # Token And Payload
        token: str = "tok123"  # noqa: S105
        payload: dict[str, Any] = {"sub": "user-id-1"}

        # Patch Caches And JWT Decode
        fake_caches: MagicMock = MagicMock()
        fake_caches.__getitem__.return_value = mock_token_cache
        mock_token_cache.get.return_value = token
        monkeypatch.setattr("apps.common.authentication.jwt_authentication.caches", fake_caches)
        monkeypatch.setattr("apps.common.authentication.jwt_authentication.jwt.decode", MagicMock(return_value=payload))

        # Patch User Lookup To Raise DoesNotExist
        with (
            patch(
                "apps.common.authentication.jwt_authentication.User.objects.get",
                side_effect=Exception(),
            ),
            patch(
                "apps.common.authentication.jwt_authentication.User.DoesNotExist",
                new=Exception,
            ),
            pytest.raises(exceptions.AuthenticationFailed) as exc,
        ):
            # Call Authenticate Credentials
            jwt_auth.authenticate_credentials(token)

        # Assert Message
        assert exc.value.detail == {"error": "User Not Found"}

    # Test Inactive User
    def test_authenticate_credentials_inactive_user(
        self,
        jwt_auth: JWTAuthentication,
        mock_token_cache: MagicMock,
        monkeypatch,
    ) -> None:
        """
        Test Inactive User Raises Error.
        """

        # Token And Payload
        token: str = "tok123"  # noqa: S105
        payload: dict[str, Any] = {"sub": "user-id-1"}

        # Patch Caches And JWT Decode
        fake_caches: MagicMock = MagicMock()
        fake_caches.__getitem__.return_value = mock_token_cache
        mock_token_cache.get.return_value = token
        monkeypatch.setattr("apps.common.authentication.jwt_authentication.caches", fake_caches)
        monkeypatch.setattr("apps.common.authentication.jwt_authentication.jwt.decode", MagicMock(return_value=payload))

        # Patch User Lookup To Return Inactive User
        user_obj: Any = SimpleNamespace(is_active=False)

        # Assert Raises
        with (
            patch("apps.common.authentication.jwt_authentication.User.objects.get", return_value=user_obj),
            pytest.raises(exceptions.AuthenticationFailed) as exc,
        ):
            # Call Authenticate Credentials
            jwt_auth.authenticate_credentials(token)

        # Assert Message
        assert exc.value.detail == {"error": "User Account Is Disabled"}

    # Test Successful Authentication
    def test_authenticate_credentials_success(
        self,
        jwt_auth: JWTAuthentication,
        mock_token_cache: MagicMock,
        monkeypatch,
    ) -> None:
        """
        Test Successful Credentials Authentication.
        """

        # Token And Payload
        token: str = "tok123"  # noqa: S105
        payload: dict[str, Any] = {"sub": "user-id-1"}

        # Patch Caches And JWT Decode
        fake_caches: MagicMock = MagicMock()
        fake_caches.__getitem__.return_value = mock_token_cache
        mock_token_cache.get.return_value = token
        monkeypatch.setattr("apps.common.authentication.jwt_authentication.caches", fake_caches)
        monkeypatch.setattr("apps.common.authentication.jwt_authentication.jwt.decode", MagicMock(return_value=payload))

        # Patch User Lookup To Return Active User
        user_obj: Any = SimpleNamespace(is_active=True)

        # Assert Returns
        with patch("apps.common.authentication.jwt_authentication.User.objects.get", return_value=user_obj):
            # Call Authenticate Credentials
            user, returned_token = jwt_auth.authenticate_credentials(token)

        # Assert Values
        assert user is user_obj
        assert returned_token == token

    # Test Authenticate Header Value
    def test_authenticate_header(self, jwt_auth: JWTAuthentication) -> None:
        """
        Test Authenticate Header Returns Bearer Scheme.
        """

        # Create Dummy Request
        request: Any = SimpleNamespace()

        # Assert Header Value
        assert jwt_auth.authenticate_header(request) == "Bearer"
