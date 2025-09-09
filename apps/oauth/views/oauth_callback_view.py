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
from apps.oauth.opentelemetry.views.oauth_callback_metrics import record_callback_access_token_generated
from apps.oauth.opentelemetry.views.oauth_callback_metrics import record_callback_access_token_reused
from apps.oauth.opentelemetry.views.oauth_callback_metrics import record_callback_backend_loaded
from apps.oauth.opentelemetry.views.oauth_callback_metrics import record_callback_complete_failure
from apps.oauth.opentelemetry.views.oauth_callback_metrics import record_callback_complete_success
from apps.oauth.opentelemetry.views.oauth_callback_metrics import record_callback_received
from apps.oauth.opentelemetry.views.oauth_callback_metrics import record_callback_refresh_token_generated
from apps.oauth.opentelemetry.views.oauth_callback_metrics import record_callback_refresh_token_reused
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

    # Validate JWT Token Function
    def _is_token_valid(self, token: str | None, secret: str, *, token_type: str) -> bool:
        """
        Validate JWT Token.

        Args:
            token (str | None): Jwt Token To Validate.
            secret (str): Secret Key For Token Validation.
            token_type (str): Token Type Label For Metrics.

        Returns:
            bool: True If Token Is Valid, False Otherwise.
        """

        # If Token Is Missing
        if not token:
            # Return False
            return False

        try:
            # Decode Token
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

            # Return False
            return False

        # Return True
        return True

    # Ensure Token Present Function
    def _ensure_token(  # noqa: PLR0913
        self,
        *,
        token_cache: BaseCache,
        cache_key: str,
        cached_token: str | None,
        secret: str,
        token_type: str,
        now_dt: datetime.datetime,
        expiry_seconds: int,
        with_metrics: bool,
    ) -> tuple[str, bool]:
        """
        Ensure Cached Token Is Valid Or Generate And Cache A New One.

        Args:
            token_cache (BaseCache): Token Cache Backend.
            cache_key (str): Cache Key For Token.
            cached_token (str | None): Existing Cached Token.
            secret (str): Jwt Secret For Token Type.
            token_type (str): Token Type Label.
            now_dt (datetime.datetime): Current Time.
            expiry_seconds (int): Expiry Seconds For Token.
            with_metrics (bool): Flag To Record Cache And Token Metrics.

        Returns:
            tuple[str, bool]: Tuple Of Token And Whether A New Token Was Generated.
        """

        # If Token Is Invalid
        if not self._is_token_valid(cached_token, secret, token_type=token_type):
            # Generate New Token
            payload: dict[str, Any] = {
                "sub": cache_key.rsplit("_", 1)[-1],
                "iss": slugify(settings.PROJECT_NAME),
                "aud": slugify(settings.PROJECT_NAME),
                "iat": now_dt,
                "exp": now_dt + datetime.timedelta(seconds=expiry_seconds),
            }

            # Encode New Token
            new_token: str = jwt.encode(
                payload=payload,
                key=secret,
                algorithm="HS256",
            )

            # Cache New Token
            token_cache.set(
                key=cache_key,
                value=new_token,
                timeout=expiry_seconds,
            )

            # If With Metrics
            if with_metrics:
                # Record Cache Set Operation
                record_cache_operation(operation="set", cache_type="token_cache", success=True)

                # If Token Type Is Access
                if token_type == "access":  # noqa: S105
                    # Record Access Token Generated
                    record_callback_access_token_generated()

                else:
                    # Record Refresh Token Generated
                    record_callback_refresh_token_generated()

            # Return New Token And True
            return new_token, True

        # If With Metrics
        if with_metrics:
            # If Token Type Is Access
            if token_type == "access":  # noqa: S105
                # Record Access Token Reused
                record_callback_access_token_reused()

            else:
                # Record Refresh Token Reused
                record_callback_refresh_token_reused()

        # Return Cached Token And False
        return cached_token or "", False

    # Handle Authenticated User Function
    def _handle_authenticated_user(
        self,
        *,
        request: Request,
        with_metrics: bool,
        start_time: float | None,
    ) -> Response:
        """
        Build Tokens, Update User, And Return Success Response.

        Args:
            request (Request): Http Request Object.
            with_metrics (bool): Flag To Record Additional Metrics.
            start_time (float | None): Start Time For Duration Metrics.

        Returns:
            Response: Http 200 Response With User And Tokens Or 400 If User Missing.
        """

        # Get User
        user = getattr(request, "user", None)

        # If User Is Not Authenticated
        if not (user and user.is_authenticated):
            # If With Metrics And Start Time Is Not None
            if with_metrics and start_time is not None:
                # Get Duration
                duration_400_user: float = time.perf_counter() - start_time

                # Record User Action
                record_user_action(action_type="oauth_callback", success=False)

                # Record HTTP Request
                record_http_request(
                    method=request.method,
                    endpoint=request.path,
                    status_code=int(status.HTTP_400_BAD_REQUEST),
                    duration=duration_400_user,
                )

            # Return Bad Request Response
            return Response(data={"error": "User Not Found"}, status=status.HTTP_400_BAD_REQUEST)

        # Get Token Cache
        token_cache: BaseCache = caches["token_cache"]

        # Get User ID String
        user_id_str: str = str(user.id)

        # Get Access Key
        access_key: str = f"access_token_{user_id_str}"

        # Get Refresh Key
        refresh_key: str = f"refresh_token_{user_id_str}"

        # Get Cached Access Token
        cached_access_token: str | None = token_cache.get(access_key)

        # Get Cached Refresh Token
        cached_refresh_token: str | None = token_cache.get(refresh_key)

        # If With Metrics
        if with_metrics:
            # Record Cache Operation
            record_cache_operation(operation="get", cache_type="token_cache", success=bool(cached_access_token))
            record_cache_operation(operation="get", cache_type="token_cache", success=bool(cached_refresh_token))

        # Get Current Time
        now_dt: datetime.datetime = datetime.datetime.now(tz=datetime.UTC)

        # Ensure Access Token
        access_token, _ = self._ensure_token(
            token_cache=token_cache,
            cache_key=access_key,
            cached_token=cached_access_token,
            secret=settings.ACCESS_TOKEN_SECRET,
            token_type="access",  # noqa: S106
            now_dt=now_dt,
            expiry_seconds=settings.ACCESS_TOKEN_EXPIRY,
            with_metrics=with_metrics,
        )

        # Ensure Refresh Token
        refresh_token, _ = self._ensure_token(
            token_cache=token_cache,
            cache_key=refresh_key,
            cached_token=cached_refresh_token,
            secret=settings.REFRESH_TOKEN_SECRET,
            token_type="refresh",  # noqa: S106
            now_dt=now_dt,
            expiry_seconds=settings.REFRESH_TOKEN_EXPIRY,
            with_metrics=with_metrics,
        )

        # Update User Last Login
        user.last_login = now_dt
        user.save(update_fields=["last_login"])

        # Serialize User Data
        user_data: dict[str, Any] = UserDetailSerializer(user).data

        # Attach Tokens
        user_data["access_token"] = access_token
        user_data["refresh_token"] = refresh_token

        # Record Callback Complete Success
        record_callback_complete_success()

        # If With Metrics And Start Time Is Not None
        if with_metrics and start_time is not None:
            # Get Duration
            duration_200: float = time.perf_counter() - start_time

            # Record User Action
            record_user_action(action_type="oauth_callback", success=True)

            # Record HTTP Request
            record_http_request(
                method=request.method,
                endpoint=request.path,
                status_code=int(status.HTTP_200_OK),
                duration=duration_200,
            )

        # Return Success Response
        return Response(data=user_data, status=status.HTTP_200_OK)

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
    def get(self, request: Request, backend_name: str) -> Response:
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

            # If Result Is A Redirect Response
            if isinstance(result, HttpResponseRedirect):
                # Handle Authenticated User
                return self._handle_authenticated_user(
                    request=request,
                    with_metrics=True,
                    start_time=start_time,
                )

            # If Result Is A Dict
            if isinstance(result, dict):
                # Handle Authenticated User
                return self._handle_authenticated_user(
                    request=request,
                    with_metrics=False,
                    start_time=None,
                )

            # Return Error Response
            # Get Duration
            duration_400: float = time.perf_counter() - start_time

            # Record User Action
            record_user_action(action_type="oauth_callback", success=False)

            # Record HTTP Request
            record_http_request(
                method=request.method,
                endpoint=request.path,
                status_code=int(status.HTTP_400_BAD_REQUEST),
                duration=duration_400,
            )

            # Return Error Response
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

            # Record HTTP Request
            record_http_request(
                method=request.method,
                endpoint=request.path,
                status_code=int(status.HTTP_500_INTERNAL_SERVER_ERROR),
                duration=duration_500,
            )

            # Record User Action
            record_user_action(action_type="oauth_callback", success=False)

            # Return Internal Server Error Response
            return Response(
                data={"error": "Internal Server Error"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
