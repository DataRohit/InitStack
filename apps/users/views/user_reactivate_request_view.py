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
from apps.users.opentelemetry.views.user_reactivate_request_metrics import record_email_template_render_duration
from apps.users.opentelemetry.views.user_reactivate_request_metrics import record_reactivate_request_initiated
from apps.users.opentelemetry.views.user_reactivate_request_metrics import record_token_generated
from apps.users.opentelemetry.views.user_reactivate_request_metrics import record_token_reused
from apps.users.serializers import UserReactivateBadRequestErrorResponseSerializer
from apps.users.serializers import UserReactivatePayloadSerializer
from apps.users.serializers import UserReactivateRequestAcceptedResponseSerializer

# Logger
logger = logging.getLogger(__name__)

# Get User Model
User: User = get_user_model()


# User Reactivate Request View Class
class UserReactivateRequestView(APIView):
    """
    User Reactivate Request API View Class.

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

    # Post Method For Reactivation Request
    @extend_schema(
        operation_id="User Reactivate Request",
        request=UserReactivatePayloadSerializer,
        responses={
            status.HTTP_202_ACCEPTED: UserReactivateRequestAcceptedResponseSerializer,
            status.HTTP_400_BAD_REQUEST: UserReactivateBadRequestErrorResponseSerializer,
            status.HTTP_500_INTERNAL_SERVER_ERROR: Generic500ResponseSerializer,
        },
        description="Initiate A Reactivation Request For A Deactivated User Account",
        summary="Request Account Reactivation",
        tags=["User"],
    )
    def post(self, request: Request) -> Response:
        """
        Process Reactivation Request For User Account.

        Args:
            request (Request): HTTP Request Object.

        Returns:
            Response: HTTP Response With Status.

        Raises:
            Exception: For Any Unexpected Errors During Reactivation Request.
        """

        # Start Request Timer
        start_time: float = time.perf_counter()

        try:
            # Get Token Cache
            token_cache: BaseCache = caches["token_cache"]

            # Get Current Time
            now_dt: datetime.datetime = datetime.datetime.now(tz=datetime.UTC)

            # Validate Input Data
            serializer: UserReactivatePayloadSerializer = UserReactivatePayloadSerializer(data=request.data)

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
                # Return Unauthorized Response
                return Response(
                    data={"errors": {"identifier": ["No Account Found With This Identifier"]}},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # If User Is Already Active
            if user.is_active:
                # Return Unauthorized Response
                return Response(
                    data={"errors": {"identifier": ["Account Is Already Active"]}},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Build User ID String
            user_id_str: str = str(user.id)

            # Build Cache Key
            cache_key: str = f"reactivation_token_{user_id_str}"

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
                    record_token_validation(token_type="reactivation", success=True)

                except jwt.InvalidTokenError:
                    # Record Token Validation Failure
                    record_token_validation(token_type="reactivation", success=False)

                    # Return False If Token Is Invalid
                    return False

                # Return True If Token Is Valid
                return True

            # If Token Is Invalid
            if not _is_token_valid(cached_token, settings.REACTIVATION_TOKEN_SECRET):
                # Build Token Payload
                token_payload: dict[str, Any] = {
                    "sub": user_id_str,
                    "iss": slugify(settings.PROJECT_NAME),
                    "aud": slugify(settings.PROJECT_NAME),
                    "iat": now_dt,
                    "exp": now_dt + datetime.timedelta(seconds=settings.REACTIVATION_TOKEN_EXPIRY),
                }

                # Generate New Token
                new_token: str = jwt.encode(
                    payload=token_payload,
                    key=settings.REACTIVATION_TOKEN_SECRET,
                    algorithm="HS256",
                )

                # Cache New Token
                token_cache.set(cache_key, new_token, timeout=settings.REACTIVATION_TOKEN_EXPIRY)

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

            # Generate Reactivation Link
            reactivation_link: str = f"{protocol}://{current_site.domain}/api/users/reactivate/confirm/{cached_token}/"

            # Load Reactivation Email Template
            template_start: float = time.perf_counter()
            reactivation_email_template: str = render_to_string(
                template_name="users/user_reactivate_request_email.html",
                context={
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                    "username": user.username,
                    "email": user.email,
                    "reactivation_link": reactivation_link,
                    "reactivation_link_expiry": now_dt + datetime.timedelta(seconds=settings.REACTIVATION_TOKEN_EXPIRY),
                    "current_year": now_dt.year,
                    "project_name": settings.PROJECT_NAME,
                },
            )
            template_duration: float = time.perf_counter() - template_start
            record_email_template_render_duration(duration=template_duration)

            try:
                # Send Reactivation Email
                send_mail(
                    subject=f"Reactivate Your {settings.PROJECT_NAME} Account",
                    message="",
                    html_message=reactivation_email_template,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[user.email],
                )

                # Record Email Sent Success
                record_email_sent(email_type="reactivation_request", success=True)

            except Exception:
                # Record Email Sent Failure
                record_email_sent(email_type="reactivation_request", success=False)

                # Raise Exception
                raise

            # Record Reactivate Request Initiated
            record_reactivate_request_initiated()

            # Record HTTP Request Metrics For 202
            duration_202: float = time.perf_counter() - start_time
            record_user_action(action_type="reactivate_request", success=True)
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
                    "message": "Reactivation Request Sent Successfully",
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
            record_user_action(action_type="reactivate_request", success=False)

            # Return Error Response
            return Response(
                data={
                    "status_code": status.HTTP_500_INTERNAL_SERVER_ERROR,
                    "error": "Internal Server Error",
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


# Exports
__all__: list[str] = ["UserReactivateRequestView"]
