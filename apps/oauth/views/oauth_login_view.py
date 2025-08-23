# Standard Library Imports
import logging
import time
from typing import Any
from typing import ClassVar

# Third Party Imports
from django.contrib.sites.models import Site
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
from social_django.utils import load_backend
from social_django.utils import load_strategy

# Local Imports
from apps.common.opentelemetry.base import record_api_error
from apps.common.opentelemetry.base import record_http_request
from apps.common.opentelemetry.base import record_user_action
from apps.common.renderers import GenericJSONRenderer
from apps.common.serializers import Generic500ResponseSerializer
from apps.oauth.opentelemetry.views.oauth_login_metrics import record_auth_url_generated
from apps.oauth.opentelemetry.views.oauth_login_metrics import record_backend_loaded
from apps.oauth.opentelemetry.views.oauth_login_metrics import record_oauth_login_initiated
from apps.oauth.opentelemetry.views.oauth_login_metrics import record_redirect_uri_built
from apps.oauth.serializers import OAuthLoginResponseSerializer

# Logger
logger: logging.Logger = logging.getLogger(__name__)


# OAuth Login View Class
class OAuthLoginView(APIView):
    """
    OAuth Login API View Class.

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
    object_label: ClassVar[str] = "data"

    # Get Method For OAuth Login
    @extend_schema(
        operation_id="OAuth Login",
        request=None,
        parameters=[
            OpenApiParameter(
                name="backend_name",
                description="OAuth Backend Name",
                required=True,
                location=OpenApiParameter.PATH,
                type=str,
                enum=["google-oauth2", "github"],
            ),
        ],
        responses={
            status.HTTP_200_OK: OAuthLoginResponseSerializer,
            status.HTTP_500_INTERNAL_SERVER_ERROR: Generic500ResponseSerializer,
        },
        description="Login Using OAuth",
        summary="OAuth Login",
        tags=["OAuth"],
    )
    def get(self, request: Request, backend_name: str) -> Response:
        """
        Process OAuth Login Request.

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
            # Record OAuth Login Initiated
            record_oauth_login_initiated()

            # Load Strategy
            strategy: Any = load_strategy(request)

            # Get Current Site
            current_site: Site = Site.objects.get_current()

            # Determine Protocol (HTTP/HTTPS)
            protocol: str = "https" if request.is_secure() else "http"

            # Generate Redirect URL
            redirect_uri: str = f"{protocol}://{current_site.domain}/api/users/oauth/{backend_name}/callback/"

            # Record Redirect URI Built
            record_redirect_uri_built()

            # Load Backend
            backend = load_backend(
                strategy=strategy,
                name=backend_name,
                redirect_uri=redirect_uri,
            )

            # Record Backend Loaded
            record_backend_loaded()

            # Get Auth URL
            auth_url: str = backend.auth_url()

            # Record Auth URL Generated
            record_auth_url_generated()

            # Return Auth URL
            duration_200: float = time.perf_counter() - start_time
            record_user_action(action_type="oauth_login", success=True)
            record_http_request(
                method=request.method,
                endpoint=request.path,
                status_code=int(status.HTTP_200_OK),
                duration=duration_200,
            )

            return Response(
                data={"auth_url": auth_url},
                status=status.HTTP_200_OK,
            )

        except Exception as e:
            # Create Log Message
            log_message: str = f"OAuth Login Failed: {e!s}"

            # Log Exception
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
            record_user_action(action_type="oauth_login", success=False)

            # Return Internal Server Error Response
            return Response(
                data={"error": "Internal Server Error"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
