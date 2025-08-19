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
from django.contrib.sites.models import Site
from django.core.cache import BaseCache
from django.core.cache import caches
from django.core.mail import send_mail
from django.template.loader import render_to_string
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.authentication import BaseAuthentication
from rest_framework.permissions import BasePermission
from rest_framework.permissions import IsAuthenticated
from rest_framework.renderers import JSONRenderer
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from slugify import slugify

# Local Imports
from apps.common.authentication import JWTAuthentication
from apps.common.opentelemetry.base import record_api_error
from apps.common.opentelemetry.base import record_cache_operation
from apps.common.opentelemetry.base import record_email_sent
from apps.common.opentelemetry.base import record_http_request
from apps.common.opentelemetry.base import record_token_validation
from apps.common.opentelemetry.base import record_user_action
from apps.common.renderers import GenericJSONRenderer
from apps.common.serializers import Generic500ResponseSerializer
from apps.users.models import User
from apps.users.opentelemetry.views.user_username_change_request_metrics import record_email_template_render_duration
from apps.users.opentelemetry.views.user_username_change_request_metrics import record_token_generated
from apps.users.opentelemetry.views.user_username_change_request_metrics import record_token_reused
from apps.users.opentelemetry.views.user_username_change_request_metrics import record_username_change_request_initiated
from apps.users.serializers import UserUsernameChangeRequestAcceptedResponseSerializer
from apps.users.serializers import UserUsernameChangeRequestUnauthorizedErrorResponseSerializer

# Logger
logger: logging.Logger = logging.getLogger(__name__)

# Get User Model
User: User = get_user_model()


# User Username Change Request View Class
class UserUsernameChangeRequestView(APIView):
    """
    User Username Change Request API View Class.

    Attributes:
        renderer_classes (ClassVar[list[JSONRenderer]]): List Of Response Renderers.
        authentication_classes (ClassVar[list[BaseAuthentication]]): List Of Authentication Classes.
        permission_classes (ClassVar[list[BasePermission]]): List Of Permission Classes.
        http_method_names (ClassVar[list[str]]): List Of Allowed HTTP Methods.
        object_label (ClassVar[str]): Label For The Object Being Processed.
    """

    # Attributes
    renderer_classes: ClassVar[list[JSONRenderer]] = [GenericJSONRenderer]
    authentication_classes: ClassVar[list[BaseAuthentication]] = [JWTAuthentication]
    permission_classes: ClassVar[list[BasePermission]] = [IsAuthenticated]
    http_method_names: ClassVar[list[str]] = ["get"]
    object_label: ClassVar[str] = ""

    # Get Method For Username Change Request
    @extend_schema(
        operation_id="User Username Change Request",
        request=None,
        responses={
            status.HTTP_202_ACCEPTED: UserUsernameChangeRequestAcceptedResponseSerializer,
            status.HTTP_401_UNAUTHORIZED: UserUsernameChangeRequestUnauthorizedErrorResponseSerializer,
            status.HTTP_500_INTERNAL_SERVER_ERROR: Generic500ResponseSerializer,
        },
        description="Initiate A Username Change Request For The Authenticated User",
        summary="Request Username Change",
        tags=["User"],
    )
    def get(self, request: Request) -> Response:
        """
        Process Username Change Request For Authenticated User.

        Args:
            request (Request): HTTP Request Object.

        Returns:
            Response: HTTP Response With User Data.

        Raises:
            Exception: For Any Unexpected Errors During Username Change Request.
        """

        # Start Request Timer
        start_time: float = time.perf_counter()

        try:
            # Get Token Cache
            token_cache: BaseCache = caches["token_cache"]

            # Get Current User
            user: User = request.user

            # Build User ID String
            user_id_str: str = str(user.id)

            # Build Cache Key
            cache_key: str = f"change_username_token_{user_id_str}"

            # Get Cached Token
            cached_token: str | None = token_cache.get(cache_key)

            # Record Cache Get Operation
            record_cache_operation(operation="get", cache_type="token_cache", success=bool(cached_token))

            # Get Current Time
            now_dt: datetime.datetime = datetime.datetime.now(tz=datetime.UTC)

            # Helper To Validate Token
            def _is_token_valid(token: str | None, secret: str) -> bool:
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
                    record_token_validation(token_type="username_change", success=True)

                except jwt.InvalidTokenError:
                    # Record Token Validation Failure
                    record_token_validation(token_type="username_change", success=False)

                    # Return False If Token Is Invalid
                    return False

                # Return True If Token Is Valid
                return True

            # If Token Is Invalid
            if not _is_token_valid(cached_token, settings.CHANGE_USERNAME_TOKEN_SECRET):
                # Build Token Payload
                token_payload: dict[str, Any] = {
                    "sub": user_id_str,
                    "iss": slugify(settings.PROJECT_NAME),
                    "aud": slugify(settings.PROJECT_NAME),
                    "iat": now_dt,
                    "exp": now_dt + datetime.timedelta(seconds=settings.CHANGE_USERNAME_TOKEN_EXPIRY),
                }

                # Generate New Token
                new_token: str = jwt.encode(
                    payload=token_payload,
                    key=settings.CHANGE_USERNAME_TOKEN_SECRET,
                    algorithm="HS256",
                )

                # Cache New Token
                token_cache.set(cache_key, new_token, timeout=settings.CHANGE_USERNAME_TOKEN_EXPIRY)

                # Record Cache Set Operation
                record_cache_operation(operation="set", cache_type="token_cache", success=True)

                # Update Cached Token
                cached_token = new_token

                # Record Token Generated
                record_token_generated()

            else:
                # Record Token Reused
                record_token_reused()

            # Get Current Site
            current_site: Site = Site.objects.get_current()

            # Determine Protocol (HTTP/HTTPS)
            protocol: str = "https" if request.is_secure() else "http"

            # Generate Username Change Link
            username_change_link: str = (
                f"{protocol}://{current_site.domain}/api/users/change-username/confirm/{cached_token}/"
            )

            # Load Username Change Email Template
            template_start: float = time.perf_counter()
            username_change_email_template: str = render_to_string(
                template_name="users/user_username_change_request_email.html",
                context={
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                    "username": user.username,
                    "email": user.email,
                    "username_change_link": username_change_link,
                    "username_change_link_expiry": now_dt
                    + datetime.timedelta(seconds=settings.CHANGE_USERNAME_TOKEN_EXPIRY),
                    "current_year": now_dt.year,
                    "project_name": settings.PROJECT_NAME,
                },
            )
            template_duration: float = time.perf_counter() - template_start
            record_email_template_render_duration(duration=template_duration)

            try:
                # Send Username Change Email
                send_mail(
                    subject=f"Change Your {settings.PROJECT_NAME} Username",
                    message="",
                    html_message=username_change_email_template,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[user.email],
                )

                # Record Email Sent Success
                record_email_sent(email_type="username_change_request", success=True)

            except Exception:
                # Record Email Sent Failure
                record_email_sent(email_type="username_change_request", success=False)

                # Raise Exception
                raise

            # Record Username Change Request Initiated
            record_username_change_request_initiated()

            # Record HTTP Request Metrics For 202
            duration_202: float = time.perf_counter() - start_time
            record_user_action(action_type="username_change_request", success=True)
            record_http_request(
                method=request.method,
                endpoint=request.path,
                status_code=int(status.HTTP_202_ACCEPTED),
                duration=duration_202,
            )

            # Return Accepted Response
            return Response(
                data={"message": "Username Change Request Sent Successfully"},
                status=status.HTTP_202_ACCEPTED,
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
            record_user_action(action_type="username_change_request", success=False)

            # Return Error Response
            return Response(
                data={"error": "Internal Server Error"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


# Exports
__all__: list[str] = ["UserUsernameChangeRequestView"]
