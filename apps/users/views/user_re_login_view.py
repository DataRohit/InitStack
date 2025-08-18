# Standard Library Imports
import datetime
import logging
from typing import Any
from typing import ClassVar

# Third Party Imports
import jwt
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.cache import BaseCache
from django.core.cache import caches
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.authentication import BaseAuthentication
from rest_framework.permissions import AllowAny
from rest_framework.permissions import BasePermission
from rest_framework.renderers import JSONRenderer
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from slugify import slugify

# Local Imports
from apps.common.renderers import GenericJSONRenderer
from apps.common.serializers import Generic500ResponseSerializer
from apps.users.models import User
from apps.users.serializers import UserDetailSerializer
from apps.users.serializers import UserLoginResponseSerializer
from apps.users.serializers import UserReLoginBadRequestErrorResponseSerializer
from apps.users.serializers import UserReLoginPayloadSerializer
from apps.users.serializers import UserReLoginUnauthorizedErrorResponseSerializer

# Logger
logger = logging.getLogger(__name__)

# Get User Model
User: User = get_user_model()


# User Re-Login View Class
class UserReLoginView(APIView):
    """
    User Re-Login API View Class.

    Attributes:
        renderer_classes (ClassVar[list[JSONRenderer]]): List Of Response Renderers.
        authentication_classes (ClassVar[list[BaseAuthentication]]): List Of Authentication Classes.
        permission_classes (ClassVar[list[BasePermission]]): List Of Permission Classes.
        http_method_names (ClassVar[list[str]]): List Of Allowed HTTP Methods.
        object_label (ClassVar[str]): Label For The Object Being Processed.
    """

    # Attributes
    renderer_classes: ClassVar[list[JSONRenderer]] = [GenericJSONRenderer]
    authentication_classes: ClassVar[list[BaseAuthentication]] = []
    permission_classes: ClassVar[list[BasePermission]] = [AllowAny]
    http_method_names: ClassVar[list[str]] = ["post"]
    object_label: ClassVar[str] = "user_re_login"

    # Post Method For User Re-Login
    @extend_schema(
        operation_id="User Re-Login",
        request=UserReLoginPayloadSerializer,
        responses={
            status.HTTP_200_OK: UserLoginResponseSerializer,
            status.HTTP_400_BAD_REQUEST: UserReLoginBadRequestErrorResponseSerializer,
            status.HTTP_401_UNAUTHORIZED: UserReLoginUnauthorizedErrorResponseSerializer,
            status.HTTP_500_INTERNAL_SERVER_ERROR: Generic500ResponseSerializer,
        },
        description="Re-Authenticate Using Refresh Token And Return New Access Token",
        summary="User Re-Login",
        tags=["User"],
    )
    def post(self, request: Request) -> Response:  # noqa: PLR0911
        """
        Process User Re-Login Request Using Refresh Token.

        Args:
            request (Request): HTTP Request Object Containing Refresh Token.

        Returns:
            Response: HTTP Response With User Data And Tokens Or Error Messages.

        Raises:
            Exception: For Any Unexpected Errors During User Re-Login.
        """

        try:
            # Get Token Cache
            token_cache: BaseCache = caches["token_cache"]

            # Validate Request Data
            serializer: UserReLoginPayloadSerializer = UserReLoginPayloadSerializer(data=request.data)

            # If Data Is Invalid
            if not serializer.is_valid():
                # Return Validation Error Response
                return Response(
                    data={"errors": serializer.errors},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Get Refresh Token
            refresh_token: str = serializer.validated_data.get("refresh_token")

            # If Token Is Invalid
            if not refresh_token:
                # Return Unauthorized Response
                return Response(
                    data={"error": "Invalid Token"},
                    status=status.HTTP_401_UNAUTHORIZED,
                )

            try:
                # Decode Refresh Token
                payload: dict[str, Any] = jwt.decode(
                    jwt=refresh_token,
                    key=settings.REFRESH_TOKEN_SECRET,
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

            except jwt.ExpiredSignatureError:
                # Return Unauthorized Response (Expired)
                return Response(
                    data={"error": "Token Has Expired"},
                    status=status.HTTP_401_UNAUTHORIZED,
                )

            except jwt.InvalidTokenError:
                # Return Unauthorized Response (Invalid Token)
                return Response(
                    data={"error": "Invalid Token"},
                    status=status.HTTP_401_UNAUTHORIZED,
                )

            # Build User ID String
            user_id_str: str = str(payload["sub"])

            # Build Cache Keys
            access_key: str = f"access_token_{user_id_str}"
            refresh_key: str = f"refresh_token_{user_id_str}"

            # Get Cached Refresh Token
            cached_refresh_token: str | None = token_cache.get(refresh_key)

            # If Token Does Not Match Cached
            if not cached_refresh_token or cached_refresh_token != refresh_token:
                # Return Unauthorized Response (Revoked)
                return Response(
                    data={"error": "Token Has Been Revoked"},
                    status=status.HTTP_401_UNAUTHORIZED,
                )

            # Get Current Time
            now_dt: datetime.datetime = datetime.datetime.now(tz=datetime.UTC)

            # Build Access Token Payload
            access_payload: dict[str, Any] = {
                "sub": user_id_str,
                "iss": slugify(settings.PROJECT_NAME),
                "aud": slugify(settings.PROJECT_NAME),
                "iat": now_dt,
                "exp": now_dt + datetime.timedelta(seconds=settings.ACCESS_TOKEN_EXPIRY),
            }

            # Generate New Access Token
            new_access_token: str = jwt.encode(
                payload=access_payload,
                key=settings.ACCESS_TOKEN_SECRET,
                algorithm="HS256",
            )

            # Cache New Access Token
            token_cache.set(access_key, new_access_token, timeout=settings.ACCESS_TOKEN_EXPIRY)

            try:
                # Get User Instance
                user: User = User.objects.get(id=user_id_str)

            except User.DoesNotExist:
                # Return Unauthorized Response (User Not Found)
                return Response(
                    data={"error": "User Not Found"},
                    status=status.HTTP_401_UNAUTHORIZED,
                )

            # If User Is Not Active
            if not getattr(user, "is_active", False):
                # Return Unauthorized Response (Disabled)
                return Response(
                    data={"error": "User Account Is Disabled"},
                    status=status.HTTP_401_UNAUTHORIZED,
                )

            # Update Last Login
            user.last_login = now_dt
            user.save(update_fields=["last_login"])

            # Serialize User Data
            user_data: dict[str, Any] = UserDetailSerializer(user).data

            # Attach Tokens
            user_data["access_token"] = new_access_token
            user_data["refresh_token"] = refresh_token

            # Return Success Response
            return Response(
                data=user_data,
                status=status.HTTP_200_OK,
            )

        except Exception as e:
            # Create Log Message
            log_message: str = f"Internal Server Error: {e!s}"

            # Log The Exception
            logger.exception(log_message)

            # Return Error Response
            return Response(
                data={"error": "Internal Server Error"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


# Exports
__all__: list[str] = ["UserReLoginView"]
