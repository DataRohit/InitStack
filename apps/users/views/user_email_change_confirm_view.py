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
from apps.users.serializers import UserDetailSerializer
from apps.users.serializers import UserEmailChangeBadRequestErrorResponseSerializer
from apps.users.serializers import UserEmailChangePayloadSerializer
from apps.users.serializers import UserEmailChangeResponseSerializer
from apps.users.serializers import UserEmailUnauthorizedErrorResponseSerializer

# Logger
logger = logging.getLogger(__name__)

# Get User Model
User: User = get_user_model()


# User Email Change Confirm View Class
class UserEmailChangeConfirmView(APIView):
    """
    User Email Change Confirm API View Class.

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
    http_method_names: ClassVar[list[str]] = ["put"]
    object_label: ClassVar[str] = "user_email_change_confirm"

    # Put Method For Email Change Confirmation
    @extend_schema(
        operation_id="User Email Change Confirm",
        request=UserEmailChangePayloadSerializer,
        responses={
            status.HTTP_200_OK: UserEmailChangeResponseSerializer,
            status.HTTP_400_BAD_REQUEST: UserEmailChangeBadRequestErrorResponseSerializer,
            status.HTTP_401_UNAUTHORIZED: UserEmailUnauthorizedErrorResponseSerializer,
            status.HTTP_500_INTERNAL_SERVER_ERROR: Generic500ResponseSerializer,
        },
        description="Confirm Email Change Using Token And Update Email",
        summary="Confirm Email Change",
        tags=["User"],
    )
    def put(self, request: Request, token: str) -> Response:
        """
        Process Email Change Confirmation.

        Args:
            request (Request): HTTP Request Object.
            token (str): Email Change Token From URL.

        Returns:
            Response: HTTP Response With Updated User Data Or Error Messages.

        Raises:
            Exception: For Any Unexpected Errors During Email Change Confirmation.
        """

        try:
            # Get Token Cache
            token_cache: BaseCache = caches["token_cache"]

            try:
                payload: dict[str, Any] = jwt.decode(
                    jwt=token,
                    key=settings.CHANGE_EMAIL_TOKEN_SECRET,
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

            except jwt.InvalidTokenError:
                # Return Unauthorized Response
                return Response(
                    data={"error": "Invalid Email Change Token"},
                    status=status.HTTP_401_UNAUTHORIZED,
                )

            # Get User ID
            user_id: str = payload.get("sub")

            # Get Cached Token
            cached_token: str | None = token_cache.get(f"change_email_token_{user_id}")

            # If Token Does Not Match
            if not cached_token or cached_token != token:
                # Return Unauthorized Response
                return Response(
                    data={"error": "Invalid Or Expired Email Change Token"},
                    status=status.HTTP_401_UNAUTHORIZED,
                )

            # Validate Email Payload From Query Params
            payload_data: dict[str, str] = {
                "email": request.data.get("email"),
                "re_email": request.data.get("re_email"),
            }

            # Initialize Payload Serializer
            serializer: UserEmailChangePayloadSerializer = UserEmailChangePayloadSerializer(data=payload_data)

            # If Data Is Invalid
            if not serializer.is_valid():
                # Return Validation Error Response
                return Response(
                    data={"errors": serializer.errors},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Extract New Email
            new_email: str = serializer.validated_data.get("email")

            # Check Email Availability
            exists: bool = User.objects.filter(email__iexact=new_email).exists()

            # If Email Already Exists
            if exists:
                # Return Bad Request Response
                return Response(
                    data={"errors": {"email": ["Email Already Exists"]}},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Get User
            user: User = User.objects.get(id=user_id)

            # Store Old Email
            old_email: str = user.email

            # Update Email
            user.email = new_email
            user.save(update_fields=["email"])

            # Revoke Change Email Token
            token_cache.delete(f"change_email_token_{user_id}")

            # Revoke Access & Refresh Tokens
            token_cache.delete(f"access_token_{user_id}")
            token_cache.delete(f"refresh_token_{user_id}")

            # Deactivate User
            user.is_active = False
            user.save(update_fields=["is_active"])

            # Get Current Time
            now_dt: datetime.datetime = datetime.datetime.now(tz=datetime.UTC)

            # Get Current Site
            current_site: Site = Site.objects.get_current()

            # Determine Protocol (HTTP/HTTPS)
            protocol: str = "https" if request.is_secure() else "http"

            # Generate Activation Token
            activation_token: str = jwt.encode(
                payload={
                    "sub": str(user.id),
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
                key=f"activation_token_{user.id}",
                value=activation_token,
                timeout=settings.ACTIVATION_TOKEN_EXPIRY,
            )

            # Generate Activation Link
            activation_link: str = f"{protocol}://{current_site.domain}/api/users/activate/{activation_token}/"

            # Load Success Email Template
            success_email_template: str = render_to_string(
                template_name="users/user_email_change_success.html",
                context={
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                    "old_email": old_email,
                    "new_email": new_email,
                    "current_year": now_dt.year,
                    "project_name": settings.PROJECT_NAME,
                },
            )

            # Send Success Email To Old Email
            send_mail(
                subject=f"Your {settings.PROJECT_NAME} Email Was Updated",
                message="",
                html_message=success_email_template,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[old_email],
            )

            # Load Activation Email Template
            activation_email_template: str = render_to_string(
                template_name="users/user_registered_email.html",
                context={
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                    "email": new_email,
                    "activation_link": activation_link,
                    "current_year": now_dt.year,
                    "project_name": settings.PROJECT_NAME,
                },
            )

            # Send Activation Email To New Email
            send_mail(
                subject=f"Re-Activate Your {settings.PROJECT_NAME} Account",
                message="",
                html_message=activation_email_template,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[new_email],
            )

            # Serialize User Data
            user_data: dict[str, Any] = UserDetailSerializer(user).data

            # Return Success Response
            return Response(
                data={"user": user_data},
                status=status.HTTP_200_OK,
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
__all__: list[str] = ["UserEmailChangeConfirmView"]
