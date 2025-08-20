# Standard Library Imports
import datetime
import logging
import time
from typing import Any
from typing import ClassVar

# Third Party Imports
import jwt
from django.conf import settings
from django.contrib.auth import login
from django.contrib.sites.models import Site
from django.core.cache import BaseCache
from django.core.cache import caches
from django.http import HttpResponseRedirect
from drf_spectacular.utils import OpenApiParameter
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
from social_core.actions import do_complete
from social_django.utils import load_backend
from social_django.utils import load_strategy

# Local Imports
from apps.common.opentelemetry.base import record_api_error
from apps.common.opentelemetry.base import record_cache_operation
from apps.common.opentelemetry.base import record_http_request
from apps.common.opentelemetry.base import record_token_validation
from apps.common.opentelemetry.base import record_user_action
from apps.common.renderers import GenericJSONRenderer
from apps.common.serializers import Generic500ResponseSerializer
from apps.oauth.opentelemetry.oauth_callback_metrics import record_callback_access_token_generated
from apps.oauth.opentelemetry.oauth_callback_metrics import record_callback_access_token_reused
from apps.oauth.opentelemetry.oauth_callback_metrics import record_callback_backend_loaded
from apps.oauth.opentelemetry.oauth_callback_metrics import record_callback_complete_failure
from apps.oauth.opentelemetry.oauth_callback_metrics import record_callback_complete_success
from apps.oauth.opentelemetry.oauth_callback_metrics import record_callback_received
from apps.oauth.opentelemetry.oauth_callback_metrics import record_callback_refresh_token_generated
from apps.oauth.opentelemetry.oauth_callback_metrics import record_callback_refresh_token_reused
from apps.oauth.serializers import OAuthCallbackBadRequestErrorResponseSerialzier
from apps.oauth.serializers import OAuthCallbackResponseSerializer
from apps.oauth.serializers import OAuthCallbackUnauthorizedErrorResponseSerializer
from apps.users.serializers import UserDetailSerializer

# Logger
logger: logging.Logger = logging.getLogger(__name__)


# OAuth Callback View Class
class OAuthCallbackView(APIView):
    """
    OAuth Callback API View Class.

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
    http_method_names: ClassVar[list[str]] = ["get"]
    object_label: ClassVar[str] = "user"

    # Get Method For OAuth Callback
    @extend_schema(
        operation_id="OAuth Callback",
        request=None,
        parameters=[
            OpenApiParameter(
                name="backend_name",
                description="OAuth Backend Name",
                required=True,
                location=OpenApiParameter.PATH,
                type=str,
            ),
            OpenApiParameter(
                name="code",
                description="Authorization Code Returned By The OAuth Provider",
                required=False,
                location=OpenApiParameter.QUERY,
                type=str,
            ),
            OpenApiParameter(
                name="state",
                description="State Parameter Returned By The OAuth Provider For CSRF Protection",
                required=False,
                location=OpenApiParameter.QUERY,
                type=str,
            ),
            OpenApiParameter(
                name="error",
                description="Error Code If The Authorization Failed",
                required=False,
                location=OpenApiParameter.QUERY,
                type=str,
            ),
        ],
        responses={
            status.HTTP_200_OK: OAuthCallbackResponseSerializer,
            status.HTTP_400_BAD_REQUEST: OAuthCallbackBadRequestErrorResponseSerialzier,
            status.HTTP_401_UNAUTHORIZED: OAuthCallbackUnauthorizedErrorResponseSerializer,
            status.HTTP_500_INTERNAL_SERVER_ERROR: Generic500ResponseSerializer,
        },
        description="OAuth Callback",
        summary="OAuth Callback",
        tags=["OAuth"],
    )
    def get(self, request: Request, backend_name: str) -> Response:  # noqa: C901, PLR0915
        """
        Process OAuth Callback Request.

        Args:
            request (Request): HTTP Request Object.
            backend_name (str): OAuth Backend Name.

        Returns:
            Response: HTTP Response With OAuth Auth URL Or Error Messages.

        Raises:
            Exception: For Any Unexpected Errors During OAuth Login.
        """

        # Start Request Timer
        start_time: float = time.perf_counter()

        try:
            # Record Callback Received
            record_callback_received()

            # Load Strategy
            strategy: Any = load_strategy(request)

            # Get Current Site
            current_site: Site = Site.objects.get_current()

            # Determine Protocol (HTTP/HTTPS)
            protocol: str = "https" if request.is_secure() else "http"

            # Generate Redirect URL
            redirect_uri: str = f"{protocol}://{current_site.domain}/api/users/oauth/{backend_name}/callback/"

            # Load Backend
            backend: Any = load_backend(
                strategy=strategy,
                name=backend_name,
                redirect_uri=redirect_uri,
            )

            # Record Backend Loaded
            record_callback_backend_loaded()

            # Complete OAuth Flow
            result: Any = do_complete(
                backend=backend,
                login=lambda strat, user, social_user: login(request, user),
                user=(request.user.is_authenticated and request.user) or None,
            )

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

            # If Result Is A Redirect Response
            if isinstance(result, HttpResponseRedirect):
                # Get User
                user = getattr(request, "user", None)

                # If User Exists And User Is Authenticated
                if user and user.is_authenticated:
                    # Get Token Cache
                    token_cache: BaseCache = caches["token_cache"]

                    # Build User ID String
                    user_id_str: str = str(user.id)

                    # Build Cache Keys
                    access_key: str = f"access_token_{user_id_str}"
                    refresh_key: str = f"refresh_token_{user_id_str}"

                    # Get Cached Tokens
                    cached_access_token: str | None = token_cache.get(access_key)
                    cached_refresh_token: str | None = token_cache.get(refresh_key)

                    # Record Cache Get Operations
                    record_cache_operation(
                        operation="get",
                        cache_type="token_cache",
                        success=bool(cached_access_token),
                    )
                    record_cache_operation(
                        operation="get",
                        cache_type="token_cache",
                        success=bool(cached_refresh_token),
                    )

                    # Get Current Time
                    now_dt: datetime.datetime = datetime.datetime.now(tz=datetime.UTC)

                    # If Access Token Is Invalid
                    if not _is_token_valid(
                        cached_access_token,
                        settings.ACCESS_TOKEN_SECRET,
                        token_type="access",  # noqa: S106
                    ):
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
                        token_cache.set(
                            access_key,
                            new_access_token,
                            timeout=settings.ACCESS_TOKEN_EXPIRY,
                        )

                        # Record Cache Set Operation
                        record_cache_operation(
                            operation="set",
                            cache_type="token_cache",
                            success=True,
                        )

                        # Update Cached Access Token
                        cached_access_token = new_access_token

                        # Record Access Token Generated
                        record_callback_access_token_generated()

                    else:
                        # Record Access Token Reused
                        record_callback_access_token_reused()

                    # If Refresh Token Is Invalid
                    if not _is_token_valid(
                        cached_refresh_token,
                        settings.REFRESH_TOKEN_SECRET,
                        token_type="refresh",  # noqa: S106
                    ):
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
                        token_cache.set(
                            refresh_key,
                            new_refresh_token,
                            timeout=settings.REFRESH_TOKEN_EXPIRY,
                        )

                        # Record Cache Set Operation
                        record_cache_operation(
                            operation="set",
                            cache_type="token_cache",
                            success=True,
                        )

                        # Update Cached Refresh Token
                        cached_refresh_token = new_refresh_token

                        # Record Refresh Token Generated
                        record_callback_refresh_token_generated()

                    else:
                        # Record Refresh Token Reused
                        record_callback_refresh_token_reused()

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
                    record_user_action(action_type="oauth_callback", success=True)
                    record_http_request(
                        method=request.method,
                        endpoint=request.path,
                        status_code=int(status.HTTP_200_OK),
                        duration=duration_200,
                    )

                    # Record Callback Completion Success
                    record_callback_complete_success()

                    # Return Success Response
                    return Response(
                        data=user_data,
                        status=status.HTTP_200_OK,
                    )

                # Return Error Response
                duration_400_user: float = time.perf_counter() - start_time
                record_user_action(action_type="oauth_callback", success=False)
                record_http_request(
                    method=request.method,
                    endpoint=request.path,
                    status_code=int(status.HTTP_400_BAD_REQUEST),
                    duration=duration_400_user,
                )

                return Response(
                    data={"error": "User Not Found"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # If Result Is A Dict
            if isinstance(result, dict):
                # Get User
                user = getattr(request, "user", None)

                # If User Exists And User Is Authenticated
                if user and user.is_authenticated:
                    # Get Token Cache
                    token_cache: BaseCache = caches["token_cache"]

                    # Build User ID String
                    user_id_str: str = str(user.id)

                    # Build Cache Keys
                    access_key: str = f"access_token_{user_id_str}"
                    refresh_key: str = f"refresh_token_{user_id_str}"

                    # Get Cached Tokens
                    cached_access_token: str | None = token_cache.get(access_key)
                    cached_refresh_token: str | None = token_cache.get(refresh_key)

                    # Get Current Time
                    now_dt: datetime.datetime = datetime.datetime.now(tz=datetime.UTC)

                    # If Access Token Is Invalid
                    if not _is_token_valid(
                        cached_access_token,
                        settings.ACCESS_TOKEN_SECRET,
                        token_type="access",  # noqa: S106
                    ):
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
                        token_cache.set(
                            access_key,
                            new_access_token,
                            timeout=settings.ACCESS_TOKEN_EXPIRY,
                        )

                        # Update Cached Access Token
                        cached_access_token = new_access_token

                    # If Refresh Token Is Invalid
                    if not _is_token_valid(
                        cached_refresh_token,
                        settings.REFRESH_TOKEN_SECRET,
                        token_type="refresh",  # noqa: S106
                    ):
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
                        token_cache.set(
                            refresh_key,
                            new_refresh_token,
                            timeout=settings.REFRESH_TOKEN_EXPIRY,
                        )

                        # Update Cached Refresh Token
                        cached_refresh_token = new_refresh_token

                    # Update Last Login
                    user.last_login = now_dt
                    user.save(update_fields=["last_login"])

                    # Serialize User Data
                    user_data: dict[str, Any] = UserDetailSerializer(user).data

                    # Attach Tokens
                    user_data["access_token"] = cached_access_token
                    user_data["refresh_token"] = cached_refresh_token

                    # Record Callback Completion Success
                    record_callback_complete_success()

                    # Return Success Response
                    return Response(
                        data=user_data,
                        status=status.HTTP_200_OK,
                    )

                # Return Error Response
                return Response(
                    data={"error": "User Not Found"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Return Error Response
            duration_400: float = time.perf_counter() - start_time
            record_user_action(action_type="oauth_callback", success=False)
            record_http_request(
                method=request.method,
                endpoint=request.path,
                status_code=int(status.HTTP_400_BAD_REQUEST),
                duration=duration_400,
            )

            return Response(
                data={"error": "Authentication Failed"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        except Exception as e:
            # Create Log Message
            log_message: str = f"OAuth Callback Failed: {e!s}"

            # Log Exception
            logger.exception(log_message)

            # Record Callback Failure
            record_callback_complete_failure()

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
            record_user_action(action_type="oauth_callback", success=False)

            # Return Internal Server Error Response
            return Response(
                data={"error": "Internal Server Error"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
