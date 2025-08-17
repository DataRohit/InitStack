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
from apps.users.serializers import UserCreateBadRequestErrorResponseSerializer
from apps.users.serializers import UserDetailSerializer
from apps.users.serializers import UserRegisterPayloadSerializer
from apps.users.serializers import UserRegisterResponseSerializer

# Logger
logger = logging.getLogger(__name__)

# Get User Model
User: ClassVar[User] = get_user_model()


# User Register View Class
class UserRegisterView(APIView):
    """
    User Registration API View Class.

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
    object_label: ClassVar[str] = "user"

    # Post Method For User Registration
    @extend_schema(
        operation_id="User Register",
        request=UserRegisterPayloadSerializer,
        responses={
            status.HTTP_201_CREATED: UserRegisterResponseSerializer,
            status.HTTP_400_BAD_REQUEST: UserCreateBadRequestErrorResponseSerializer,
            status.HTTP_500_INTERNAL_SERVER_ERROR: Generic500ResponseSerializer,
        },
        description="Register A New User Account",
        summary="Register A New User Account",
        tags=["User"],
    )
    def post(self, request: Request) -> Response:
        """
        Process User Registration Request.

        Args:
            request (Request): HTTP Request Object Containing User Registration Data.

        Returns:
            Response: HTTP Response With User Data Or Error Messages.

        Raises:
            Exception: For Any Unexpected Errors During User Registration.
        """

        try:
            # Get Token Cache
            token_cache: BaseCache = caches["token_cache"]

            # Validate Request Data
            serializer: UserRegisterPayloadSerializer = UserRegisterPayloadSerializer(data=request.data)

            # If Data Is Valid
            if serializer.is_valid():
                # Create New User
                user: User = serializer.save()

                # Serializer User Data
                user_data: dict[str, Any] = UserDetailSerializer(user).data

                # Get Current Time
                now_dt: datetime.datetime = datetime.datetime.now(tz=datetime.UTC)

                # Generate Activation Token
                activation_token: str = jwt.encode(
                    payload={
                        "sub": str(user_data.get("id")),
                        "iss": slugify(settings.PROJECT_NAME),
                        "aud": slugify(settings.PROJECT_NAME),
                        "iat": now_dt,
                        "exp": now_dt + datetime.timedelta(seconds=settings.ACTIVATION_TOKEN_EXPIRY),
                    },
                    key=settings.ACTIVATION_TOKEN_SECRET,
                    algorithm="HS256",
                )

                # Cache Activation Token
                token_cache.set(
                    key=f"activation_token_{user_data.get('id')}",
                    value=activation_token,
                    timeout=settings.ACTIVATION_TOKEN_EXPIRY,
                )

                # Get Current Site
                current_site: Site = Site.objects.get_current()

                # Determine Protocol (HTTP/HTTPS)
                protocol: str = "https" if request.is_secure() else "http"

                # Generate Activation Link
                activation_link: str = f"{protocol}://{current_site.domain}/api/users/activate/{activation_token}/"

                # Load Activation Email Template
                activation_email_template: str = render_to_string(
                    template_name="users/user_registered_email.html",
                    context={
                        "first_name": user_data.get("first_name"),
                        "last_name": user_data.get("last_name"),
                        "username": user_data.get("username"),
                        "email": user_data.get("email"),
                        "activation_link": activation_link,
                        "activation_link_expiry": now_dt + datetime.timedelta(seconds=settings.ACTIVATION_TOKEN_EXPIRY),
                        "current_year": now_dt.year,
                        "project_name": settings.PROJECT_NAME,
                    },
                )

                # Send Activation Email
                send_mail(
                    subject=f"Activate Your {settings.PROJECT_NAME} Account",
                    message="",
                    html_message=activation_email_template,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[user_data.get("email")],
                )

                # Return Success Response
                return Response(
                    data=user_data,
                    status=status.HTTP_201_CREATED,
                )

            # Return Validation Error Response
            return Response(
                data={"errors": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
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
__all__: list[str] = ["UserRegisterView"]
