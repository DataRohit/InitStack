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
from django.db.models.query_utils import Q
from django.template.loader import render_to_string
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
from apps.common.opentelemetry.base import record_email_sent
from apps.common.opentelemetry.base import record_http_request
from apps.common.opentelemetry.base import record_token_validation
from apps.common.opentelemetry.base import record_user_action
from apps.common.renderers import GenericJSONRenderer
from apps.common.serializers import Generic500ResponseSerializer
from apps.users.models import User
from apps.users.opentelemetry.views.user_reset_password_request_metrics import record_email_template_render_duration
from apps.users.opentelemetry.views.user_reset_password_request_metrics import record_reset_password_request_initiated
from apps.users.opentelemetry.views.user_reset_password_request_metrics import record_token_generated
from apps.users.opentelemetry.views.user_reset_password_request_metrics import record_token_reused
from apps.users.serializers import UserResetPasswordRequestAcceptedResponseSerializer
from apps.users.serializers import UserResetPasswordRequestBadRequestErrorResponseSerializer
from apps.users.serializers import UserResetPasswordRequestPayloadSerializer

# Logger
logger = logging.getLogger(__name__)

# Get User Model
User: User = get_user_model()


# User Reset Password Request View Class
class UserResetPasswordRequestView(APIView):
    """
    User Reset Password Request API View Class.

    Attributes:
        renderer_classes (ClassVar[list[JSONRenderer]]): List Of Response Renderers.
        http_method_names (ClassVar[list[str]]): List Of Allowed HTTP Methods.
    """

    # Attributes
    renderer_classes: ClassVar[list[JSONRenderer]] = [GenericJSONRenderer]
    authentication_classes: ClassVar[list[BaseAuthentication]] = []
    permission_classes: ClassVar[list[BasePermission]] = [AllowAny]
    http_method_names: ClassVar[list[str]] = ["post"]
    object_label: ClassVar[str] = ""

    # Post Method For Reset Password Request
    @extend_schema(
        operation_id="User Reset Password Request",
        request=UserResetPasswordRequestPayloadSerializer,
        responses={
            status.HTTP_202_ACCEPTED: UserResetPasswordRequestAcceptedResponseSerializer,
            status.HTTP_400_BAD_REQUEST: UserResetPasswordRequestBadRequestErrorResponseSerializer,
            status.HTTP_500_INTERNAL_SERVER_ERROR: Generic500ResponseSerializer,
        },
        description="Initiate A Password Reset Request For A User Account",
        summary="Request Password Reset",
        tags=["User"],
    )
    def post(self, request: Request) -> Response:
        """
        Process Password Reset Request For User Account.

        Args:
            request (Request): HTTP Request Object.

        Returns:
            Response: HTTP Response With Status.

        Raises:
            Exception: For Any Unexpected Errors During Password Reset Request.
        """

        # Start Request Timer
        start_time: float = time.perf_counter()

        try:
            # Get Token Cache
            token_cache: BaseCache = caches["token_cache"]

            # Get Current Time
            now_dt: datetime.datetime = datetime.datetime.now(tz=datetime.UTC)

            # Validate Input Data
            serializer: UserResetPasswordRequestPayloadSerializer = UserResetPasswordRequestPayloadSerializer(
                data=request.data,
            )

            # Check Validation
            if not serializer.is_valid():
                # Return Error Response
                return Response(
                    data={
                        "status_code": status.HTTP_400_BAD_REQUEST,
                        "errors": serializer.errors,
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Get Validated Data
            validated_data: dict[str, Any] = serializer.validated_data

            # Get Identifier
            identifier: str = validated_data["identifier"]

            # Build User Query
            user_query: Q = Q(username__iexact=identifier) | Q(email__iexact=identifier)

            try:
                # Get User
                user: User = User.objects.get(user_query)

            except User.DoesNotExist:
                # Return Bad Request Response
                return Response(
                    data={"errors": {"identifier": ["No Account Found With This Identifier"]}},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # If User Not Active
            if not user.is_active:
                # Return Bad Request Response
                return Response(
                    data={"errors": {"identifier": ["Account Is Not Active"]}},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Build User ID String
            user_id_str: str = str(user.id)

            # Build Cache Key
            cache_key: str = f"reset_password_token_{user_id_str}"

            # Get Cached Token
            cached_token: str | None = token_cache.get(cache_key)

            # Record Cache Get Operation
            record_cache_operation(operation="get", cache_type="token_cache", success=bool(cached_token))

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
                    record_token_validation(token_type="reset_password", success=True)

                except jwt.InvalidTokenError:
                    # Record Token Validation Failure
                    record_token_validation(token_type="reset_password", success=False)

                    # Return False If Token Is Invalid
                    return False

                # Return True If Token Is Valid
                return True

            # If Token Is Invalid
            if not _is_token_valid(cached_token, settings.RESET_PASSWORD_TOKEN_SECRET):
                # Build Token Payload
                token_payload: dict[str, Any] = {
                    "sub": user_id_str,
                    "iss": slugify(settings.PROJECT_NAME),
                    "aud": slugify(settings.PROJECT_NAME),
                    "iat": now_dt,
                    "exp": now_dt + datetime.timedelta(seconds=settings.RESET_PASSWORD_TOKEN_EXPIRY),
                }

                # Generate New Token
                new_token: str = jwt.encode(
                    payload=token_payload,
                    key=settings.RESET_PASSWORD_TOKEN_SECRET,
                    algorithm="HS256",
                )

                # Cache New Token
                token_cache.set(cache_key, new_token, timeout=settings.RESET_PASSWORD_TOKEN_EXPIRY)

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

            # Generate Reset Password Link
            reset_password_link: str = (
                f"{protocol}://{current_site.domain}/api/users/reset-password/confirm/{cached_token}/"
            )

            # Load Reset Password Email Template
            template_start: float = time.perf_counter()
            reset_password_email_template: str = render_to_string(
                template_name="users/user_reset_password_request_email.html",
                context={
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                    "username": user.username,
                    "email": user.email,
                    "reset_password_link": reset_password_link,
                    "reset_password_link_expiry": now_dt
                    + datetime.timedelta(seconds=settings.RESET_PASSWORD_TOKEN_EXPIRY),
                    "current_year": now_dt.year,
                    "project_name": settings.PROJECT_NAME,
                },
            )
            template_duration: float = time.perf_counter() - template_start
            record_email_template_render_duration(duration=template_duration)

            try:
                # Send Reset Password Email
                send_mail(
                    subject=f"Reset Your {settings.PROJECT_NAME} Password",
                    message="",
                    html_message=reset_password_email_template,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[user.email],
                )

                # Record Email Sent Success
                record_email_sent(email_type="reset_password_request", success=True)

            except Exception:
                # Record Email Sent Failure
                record_email_sent(email_type="reset_password_request", success=False)

                # Raise Exception
                raise

            # Record Reset Password Request Initiated
            record_reset_password_request_initiated()

            # Record HTTP Request Metrics For 202
            duration_202: float = time.perf_counter() - start_time
            record_user_action(action_type="reset_password_request", success=True)
            record_http_request(
                method=request.method,
                endpoint=request.path,
                status_code=int(status.HTTP_202_ACCEPTED),
                duration=duration_202,
            )

            # Return Accepted Response
            return Response(
                data={
                    "status_code": status.HTTP_202_ACCEPTED,
                    "message": "Password Reset Request Sent Successfully",
                },
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
            record_user_action(action_type="reset_password_request", success=False)

            # Return Error Response
            return Response(
                data={
                    "status_code": status.HTTP_500_INTERNAL_SERVER_ERROR,
                    "error": "Internal Server Error",
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


# Exports
__all__: list[str] = ["UserResetPasswordRequestView"]
