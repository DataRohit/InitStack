# Standard Library Imports
import logging
import time
from typing import ClassVar

# Third Party Imports
from django.contrib.auth import get_user_model
from django.core.cache import BaseCache
from django.core.cache import caches
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.authentication import BaseAuthentication
from rest_framework.permissions import BasePermission
from rest_framework.permissions import IsAuthenticated
from rest_framework.renderers import JSONRenderer
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

# Local Imports
from apps.common.authentication import JWTAuthentication
from apps.common.opentelemetry.base import record_api_error
from apps.common.opentelemetry.base import record_cache_operation
from apps.common.opentelemetry.base import record_http_request
from apps.common.opentelemetry.base import record_user_action
from apps.common.renderers import GenericJSONRenderer
from apps.common.serializers import Generic500ResponseSerializer
from apps.users.models import User
from apps.users.opentelemetry.views.user_logout_metrics import record_logout_initiated
from apps.users.opentelemetry.views.user_logout_metrics import record_tokens_revoked
from apps.users.serializers import UserLogoutUnauthorizedErrorResponseSerializer

# Logger
logger = logging.getLogger(__name__)

# Get User Model
User: User = get_user_model()


# User Logout View Class
class UserLogoutView(APIView):
    """
    User Logout API View Class.

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

    # Get Method For User Logout
    @extend_schema(
        operation_id="User Logout",
        request=None,
        responses={
            status.HTTP_204_NO_CONTENT: None,
            status.HTTP_401_UNAUTHORIZED: UserLogoutUnauthorizedErrorResponseSerializer,
            status.HTTP_500_INTERNAL_SERVER_ERROR: Generic500ResponseSerializer,
        },
        description="Log Out Current Authenticated User By Revoking Access And Refresh Tokens",
        summary="Logout User",
        tags=["User"],
    )
    def get(self, request: Request) -> Response:
        """
        Revoke Access And Refresh Tokens For Current User.

        Args:
            request (Request): HTTP Request Object.

        Returns:
            Response: HTTP Response With No Content On Success.

        Raises:
            Exception: For Any Unexpected Errors During Logout.
        """

        # Start Request Timer
        start_time: float = time.perf_counter()

        try:
            # Get Current User
            user: User = request.user

            # Get Token Cache
            token_cache: BaseCache = caches["token_cache"]

            # Delete Access Token
            token_cache.delete(f"access_token_{user.id}")
            record_cache_operation(operation="delete", cache_type="token_cache", success=True)
            record_tokens_revoked(token_type="access")  # noqa: S106

            # Delete Refresh Token
            token_cache.delete(f"refresh_token_{user.id}")
            record_cache_operation(operation="delete", cache_type="token_cache", success=True)
            record_tokens_revoked(token_type="refresh")  # noqa: S106

            # Record Success Metrics
            duration_204: float = time.perf_counter() - start_time
            record_user_action(action_type="logout", success=True)
            record_http_request(
                method=request.method,
                endpoint=request.path,
                status_code=int(status.HTTP_204_NO_CONTENT),
                duration=duration_204,
            )

            # Record Logout Initiated
            record_logout_initiated()

            # Return No Content Response
            return Response(status=status.HTTP_204_NO_CONTENT)

        except Exception as e:
            # Create Log Message
            log_message: str = f"Internal Server Error: {e!s}"

            # Log The Exception
            logger.exception(log_message)

            # Record API Error And HTTP Metrics
            record_api_error(endpoint=request.path, error_type=e.__class__.__name__)

            duration_500: float = time.perf_counter() - start_time
            record_http_request(
                method=request.method,
                endpoint=request.path,
                status_code=int(status.HTTP_500_INTERNAL_SERVER_ERROR),
                duration=duration_500,
            )

            # Record User Action Failure
            record_user_action(action_type="logout", success=False)

            # Return Error Response
            return Response(
                data={"error": "Internal Server Error"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


# Exports
__all__: list[str] = ["UserLogoutView"]
