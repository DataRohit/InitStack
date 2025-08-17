# Standard Library Imports
from typing import Any

import jwt
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractBaseUser

# Third Party Imports
from django.core.cache import BaseCache
from django.core.cache import caches
from rest_framework import authentication
from rest_framework import exceptions
from rest_framework.request import Request
from slugify import slugify

# Local Imports
from apps.users.models import User

# Get User Model
User: User = get_user_model()


# JWT Authentication Class
class JWTAuthentication(authentication.BaseAuthentication):
    """
    JSON Web Token Authentication Backend.
    """

    # Authenticate Request Method
    def authenticate(self, request: Request) -> tuple[AbstractBaseUser, str] | None:
        """
        Authenticate Request Using Bearer Token.

        Args:
            request (Request): DRF Request Instance.

        Returns:
            tuple[AbstractBaseUser, str] | None: Tuple Of User And Token If Authenticated, Otherwise None.

        Raises:
            exceptions.AuthenticationFailed: When Token Format Is Invalid.
        """

        # Get Authorization Header
        auth_header: list[bytes] = authentication.get_authorization_header(request).split()

        # If No Auth Header Or Not Bearer
        if not auth_header or auth_header[0].lower() != b"bearer":
            # Raise Missing Credentials
            raise exceptions.AuthenticationFailed({"error": "Authentication Credentials Were Not Provided"}) from None

        # If Header Parts Length Is Not 2
        if len(auth_header) != 2:  # noqa: PLR2004
            # Raise Invalid Authorization Header
            raise exceptions.AuthenticationFailed({"error": "Invalid Authorization Header"}) from None

        try:
            # Decode Token String
            token: str = auth_header[1].decode("utf-8")

        except UnicodeError:
            # Raise Invalid Token Format
            raise exceptions.AuthenticationFailed({"error": "Invalid Token Format"}) from None

        # Delegate To Credentials Check
        return self.authenticate_credentials(token)

    # Authenticate Credentials Method
    def authenticate_credentials(self, token: str) -> tuple[AbstractBaseUser, str]:
        """
        Validate Token And Return Authenticated User.

        Args:
            token (str): Encoded JWT Token.

        Returns:
            tuple[AbstractBaseUser, str]: Tuple Containing User And Original Token.

        Raises:
            exceptions.AuthenticationFailed: When Token Is Expired, Invalid, User Not Found, Or Disabled.
        """

        # If Token Is Invalid
        if not token:
            # Raise Invalid Token
            raise exceptions.AuthenticationFailed({"error": "Invalid Token"}) from None

        try:
            # Get Token Cache
            token_cache: BaseCache = caches["token_cache"]

            # Decode Token With Secret
            payload: dict[str, Any] = jwt.decode(
                jwt=token,
                key=settings.ACCESS_TOKEN_SECRET,
                algorithms=["HS256"],
                options={
                    "verify_signature": True,
                    "verify_exp": True,
                    "verify_aud": True,
                    "verify_iss": True,
                },
                audience=slugify(settings.PROJECT_NAME),
                issuer=slugify(settings.PROJECT_NAME),
            )

            # Get Cached Token
            cached_token: str | None = token_cache.get(f"access_token_{payload['sub']}")

            # If Token Does Not Match
            if not cached_token or cached_token != token:
                # Raise Token Revoked
                raise exceptions.AuthenticationFailed({"error": "Token Has Been Revoked"}) from None

        except jwt.ExpiredSignatureError:
            # Raise Token Expired
            raise exceptions.AuthenticationFailed({"error": "Token Has Expired"}) from None

        except jwt.InvalidTokenError:
            # Raise Invalid Token
            raise exceptions.AuthenticationFailed({"error": "Invalid Token"}) from None

        try:
            # Get User By ID
            user: User = User.objects.get(id=payload["sub"])

        except User.DoesNotExist:
            # Raise User Not Found
            raise exceptions.AuthenticationFailed({"error": "User Not Found"}) from None

        # If User Is Not Active
        if not getattr(user, "is_active", False):
            # Raise Disabled Account
            raise exceptions.AuthenticationFailed({"error": "User Account Is Disabled"}) from None

        # Return User And Token
        return (user, token)

    # Authenticate Header Method
    def authenticate_header(self, request: Request) -> str:
        """
        Return Authentication Scheme For 401 Responses.

        Args:
            request (Request): DRF Request Instance.

        Returns:
            str: Authentication Header Scheme.
        """

        # Return Bearer Scheme
        return "Bearer"


# Exports
__all__: list[str] = ["JWTAuthentication"]
