# Standard Library Imports
import datetime
import logging
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
from rest_framework.permissions import AllowAny
from rest_framework.permissions import BasePermission
from rest_framework.renderers import JSONRenderer
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from slugify import slugify

# Local Imports
from apps.common.renderers import GenericJSONRenderer
from apps.common.serializers.generic_response_serializer import Generic500ResponseSerializer
from apps.users.models import User
from apps.users.serializers import UserActivateResponseSerializer
from apps.users.serializers import UserActivateUnauthorizedErrorResponseSerializer
from apps.users.serializers import UserDetailSerializer

# Logger
logger = logging.getLogger(__name__)

# Get User Model
User: ClassVar[User] = get_user_model()


# User Activate View Class
class UserActivateView(APIView):
    """
    User Account Activation API View Class.

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
    object_label: ClassVar[str] = "user_activation"

    # Get Method For User Activation
    @extend_schema(
        operation_id="User Activate",
        responses={
            status.HTTP_200_OK: UserActivateResponseSerializer,
            status.HTTP_401_UNAUTHORIZED: UserActivateUnauthorizedErrorResponseSerializer,
            status.HTTP_500_INTERNAL_SERVER_ERROR: Generic500ResponseSerializer,
        },
        description="Activate A User Account Using Token",
        summary="Activate A User Account",
        tags=["User"],
    )
    def get(self, request: Request, token: str) -> Response:
        """
        Process User Activation Request.

        Args:
            request (Request): HTTP Request Object.
            token (str): Activation Token From URL.

        Returns:
            Response: HTTP Response With User Data Or Error Messages.

        Raises:
            Exception: For Any Unexpected Errors During User Activation.
        """

        try:
            # Get Token Cache
            token_cache: BaseCache = caches["token_cache"]

            # Decode Token To Get User ID
            try:
                # Decode Token
                payload: dict[str, Any] = jwt.decode(
                    jwt=token,
                    key=settings.ACTIVATION_TOKEN_SECRET,
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

                # Get User ID
                user_id: str = payload.get("sub")

                # Get Cached Token
                cached_token: str | None = token_cache.get(f"activation_token_{user_id}")

                # If Token Does Not Match
                if not cached_token or cached_token != token:
                    # Return Unauthorized Response
                    return Response(
                        data={"error": "Invalid Or Expired Activation Token"},
                        status=status.HTTP_401_UNAUTHORIZED,
                    )

                # Remove Token From Cache
                token_cache.delete(f"activation_token_{user_id}")

                # Get User
                user: User = User.objects.get(id=user_id)

                # Activate User
                user.is_active = True
                user.save()

                # Get Current Time
                now_dt: datetime.datetime = datetime.datetime.now(tz=datetime.UTC)

                # Get Current Site
                current_site: Site = Site.objects.get_current()

                # Determine Protocol (HTTP/HTTPS)
                protocol: str = "https" if request.is_secure() else "http"

                # Generate Login Link
                login_link: str = f"{protocol}://{current_site.domain}/login/"

                # Load Welcome Email Template
                welcome_email_template: str = render_to_string(
                    template_name="users/user_activated_email.html",
                    context={
                        "first_name": user.first_name,
                        "last_name": user.last_name,
                        "username": user.username,
                        "email": user.email,
                        "login_link": login_link,
                        "current_year": now_dt.year,
                        "project_name": settings.PROJECT_NAME,
                    },
                )

                # Send Welcome Email
                send_mail(
                    subject=f"Welcome To {settings.PROJECT_NAME}",
                    message="",
                    html_message=welcome_email_template,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[user.email],
                )

                # Serialize User Data
                user_data: dict[str, Any] = UserDetailSerializer(user).data

                # Return Success Response
                return Response(
                    data=user_data,
                    status=status.HTTP_200_OK,
                )

            except jwt.InvalidTokenError:
                # Return Unauthorized Response
                return Response(
                    data={"error": "Invalid Activation Token"},
                    status=status.HTTP_401_UNAUTHORIZED,
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
__all__: list[str] = ["UserActivateView"]
