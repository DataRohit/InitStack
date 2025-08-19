# ruff: noqa: PLR0915, S106

# Standard Library Imports
import datetime
import logging
import time
from typing import Any
from typing import ClassVar

# Third Party Imports
import jwt
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.cache import BaseCache
from django.core.cache import caches
from django.db.models import Q
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
from apps.common.opentelemetry.base import record_api_error
from apps.common.opentelemetry.base import record_cache_operation
from apps.common.opentelemetry.base import record_http_request
from apps.common.opentelemetry.base import record_token_validation
from apps.common.opentelemetry.base import record_user_action
from apps.common.renderers import GenericJSONRenderer
from apps.common.serializers import Generic500ResponseSerializer
from apps.users.models import User
from apps.users.opentelemetry.views.user_login_metrics import record_access_token_generated
from apps.users.opentelemetry.views.user_login_metrics import record_access_token_reused
from apps.users.opentelemetry.views.user_login_metrics import record_login_initiated
from apps.users.opentelemetry.views.user_login_metrics import record_refresh_token_generated
from apps.users.opentelemetry.views.user_login_metrics import record_refresh_token_reused
from apps.users.serializers import UserDetailSerializer
from apps.users.serializers import UserLoginBadRequestErrorResponseSerializer
from apps.users.serializers import UserLoginPayloadSerializer
from apps.users.serializers import UserLoginResponseSerializer
from apps.users.serializers import UserLoginUnauthorizedErrorResponseSerializer

# Logger
logger = logging.getLogger(__name__)

# Get User Model
User: User = get_user_model()


# User Login View Class
class UserLoginView(APIView):
    """
    User Login API View Class.

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
    object_label: ClassVar[str] = "user_login"

    # Post Method For User Login
    @extend_schema(
        operation_id="User Login",
        request=UserLoginPayloadSerializer,
        responses={
            status.HTTP_200_OK: UserLoginResponseSerializer,
            status.HTTP_400_BAD_REQUEST: UserLoginBadRequestErrorResponseSerializer,
            status.HTTP_401_UNAUTHORIZED: UserLoginUnauthorizedErrorResponseSerializer,
            status.HTTP_500_INTERNAL_SERVER_ERROR: Generic500ResponseSerializer,
        },
        description="Authenticate A User With Username/Email And Password And Return Tokens",
        summary="User Login",
        tags=["User"],
    )
    def post(self, request: Request) -> Response:  # noqa: C901
        """
        Process User Login Request.

        Args:
            request (Request): HTTP Request Object Containing Login Data.

        Returns:
            Response: HTTP Response With User Data And Tokens Or Error Messages.

        Raises:
            Exception: For Any Unexpected Errors During User Login.
        """

        # Start Request Timer
        start_time: float = time.perf_counter()

        try:
            # Get Token Cache
            token_cache: BaseCache = caches["token_cache"]

            # Validate Request Data
            serializer: UserLoginPayloadSerializer = UserLoginPayloadSerializer(data=request.data)

            # If Data Is Invalid
            if not serializer.is_valid():
                # Record HTTP Request Metrics For 400
                duration_400: float = time.perf_counter() - start_time
                record_user_action(action_type="login", success=False)
                record_http_request(
                    method=request.method,
                    endpoint=request.path,
                    status_code=int(status.HTTP_400_BAD_REQUEST),
                    duration=duration_400,
                )

                # Return Validation Error Response
                return Response(
                    data={"errors": serializer.errors},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Get Identifier
            identifier: str = serializer.validated_data.get("identifier").strip()

            # Get Password
            password: str = serializer.validated_data.get("password")

            # Build User Query
            user_query: Q = Q(username__iexact=identifier) | Q(email__iexact=identifier)

            try:
                # Get User
                user: User = User.objects.get(user_query)

            except User.DoesNotExist:
                # Record HTTP Request Metrics For 401
                duration_401: float = time.perf_counter() - start_time
                record_user_action(action_type="login", success=False)
                record_http_request(
                    method=request.method,
                    endpoint=request.path,
                    status_code=int(status.HTTP_401_UNAUTHORIZED),
                    duration=duration_401,
                )

                # Return Unauthorized Response
                return Response(
                    data={"error": "Invalid Username Or Password"},
                    status=status.HTTP_401_UNAUTHORIZED,
                )

            # If User Is Not Active
            if not user.is_active:
                # Record HTTP Request Metrics For 401
                duration_401_inactive: float = time.perf_counter() - start_time
                record_user_action(action_type="login", success=False)
                record_http_request(
                    method=request.method,
                    endpoint=request.path,
                    status_code=int(status.HTTP_401_UNAUTHORIZED),
                    duration=duration_401_inactive,
                )

                # Return Unauthorized Response
                return Response(
                    data={"error": "User Is Not Active"},
                    status=status.HTTP_401_UNAUTHORIZED,
                )

            # If Password Is Invalid
            if not user.check_password(password):
                # Record HTTP Request Metrics For 401
                duration_401_badpass: float = time.perf_counter() - start_time
                record_user_action(action_type="login", success=False)
                record_http_request(
                    method=request.method,
                    endpoint=request.path,
                    status_code=int(status.HTTP_401_UNAUTHORIZED),
                    duration=duration_401_badpass,
                )

                # Return Unauthorized Response
                return Response(
                    data={"error": "Invalid Username Or Password"},
                    status=status.HTTP_401_UNAUTHORIZED,
                )

            # Build User ID String
            user_id_str: str = str(user.id)

            # Build Cache Keys
            access_key: str = f"access_token_{user_id_str}"
            refresh_key: str = f"refresh_token_{user_id_str}"

            # Get Cached Tokens
            cached_access_token: str | None = token_cache.get(access_key)
            cached_refresh_token: str | None = token_cache.get(refresh_key)

            # Record Cache Get Operations
            record_cache_operation(operation="get", cache_type="token_cache", success=bool(cached_access_token))
            record_cache_operation(operation="get", cache_type="token_cache", success=bool(cached_refresh_token))

            # Get Current Time
            now_dt: datetime.datetime = datetime.datetime.now(tz=datetime.UTC)

            # Helper To Validate Token
            def _is_token_valid(token: str | None, secret: str, *, token_type: str) -> bool:
                """
                Validate A JWT Token.

                Args:
                    token (str | None): JWT Token To Validate.
                    secret (str): Secret Key For Token Validation.

                Returns:
                    bool: True If Token Is Valid, False Otherwise.
                """

                # If Token Is Missing
                if not token:
                    # Return False
                    return False

                try:
                    # Try To Validate Token
                    jwt.decode(
                        jwt=token,
                        key=secret,
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

                    # Record Token Validation Success
                    record_token_validation(token_type=token_type, success=True)

                except jwt.InvalidTokenError:
                    # Record Token Validation Failure
                    record_token_validation(token_type=token_type, success=False)

                    # Return False If Token Is Invalid
                    return False

                # Return True If Token Is Valid
                return True

            # If Access Token Is Invalid
            if not _is_token_valid(cached_access_token, settings.ACCESS_TOKEN_SECRET, token_type="access"):
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

                # Record Cache Set Operation
                record_cache_operation(operation="set", cache_type="token_cache", success=True)

                # Update Cached Access Token
                cached_access_token = new_access_token

                # Record Access Token Generated
                record_access_token_generated()

            # If Refresh Token Is Invalid
            if not _is_token_valid(cached_refresh_token, settings.REFRESH_TOKEN_SECRET, token_type="refresh"):
                # Build Refresh Token Payload
                refresh_payload: dict[str, Any] = {
                    "sub": user_id_str,
                    "iss": slugify(settings.PROJECT_NAME),
                    "aud": slugify(settings.PROJECT_NAME),
                    "iat": now_dt,
                    "exp": now_dt + datetime.timedelta(seconds=settings.REFRESH_TOKEN_EXPIRY),
                }

                # Generate New Refresh Token
                new_refresh_token: str = jwt.encode(
                    payload=refresh_payload,
                    key=settings.REFRESH_TOKEN_SECRET,
                    algorithm="HS256",
                )

                # Cache New Refresh Token
                token_cache.set(refresh_key, new_refresh_token, timeout=settings.REFRESH_TOKEN_EXPIRY)

                # Record Cache Set Operation
                record_cache_operation(operation="set", cache_type="token_cache", success=True)

                # Update Cached Refresh Token
                cached_refresh_token = new_refresh_token

                # Record Refresh Token Generated
                record_refresh_token_generated()

            else:
                # Record Refresh Token Reused
                record_refresh_token_reused()

            # If Access Token Was Valid And Reused
            if _is_token_valid(cached_access_token, settings.ACCESS_TOKEN_SECRET, token_type="access"):
                # Record Access Token Reused
                record_access_token_reused()

            # Update Last Login
            user.last_login = now_dt
            user.save(update_fields=["last_login"])

            # Serialize User Data
            user_data: dict[str, Any] = UserDetailSerializer(user).data

            # Attach Tokens
            user_data["access_token"] = cached_access_token
            user_data["refresh_token"] = cached_refresh_token

            # Record User Action Success And HTTP Metrics For 200
            duration_200: float = time.perf_counter() - start_time
            record_user_action(action_type="login", success=True)
            record_http_request(
                method=request.method,
                endpoint=request.path,
                status_code=int(status.HTTP_200_OK),
                duration=duration_200,
            )

            # Record Login Initiated
            record_login_initiated()

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

            # Record API Error
            record_api_error(endpoint=request.path, error_type=e.__class__.__name__)

            # Record HTTP Request Metrics
            duration_500: float = time.perf_counter() - start_time
            record_http_request(
                method=request.method,
                endpoint=request.path,
                status_code=int(status.HTTP_500_INTERNAL_SERVER_ERROR),
                duration=duration_500,
            )

            # Record User Action Failure
            record_user_action(action_type="login", success=False)

            # Return Error Response
            return Response(
                data={"error": "Internal Server Error"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


# Exports
__all__: list[str] = ["UserLoginView"]
