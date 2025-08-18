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
from apps.common.serializers import Generic500ResponseSerializer
from apps.users.models import User
from apps.users.serializers import UserDetailSerializer
from apps.users.serializers import UserUsernameChangeConfirmBadRequestErrorResponseSerialzier
from apps.users.serializers import UserUsernameChangeConfirmResponseSerializer
from apps.users.serializers import UserUsernameChangeConfirmUnauthorizedErrorResponseSerializer
from apps.users.serializers import UserUsernameChangePayloadSerializer

# Logger
logger = logging.getLogger(__name__)

# Get User Model
User: User = get_user_model()


# User Username Change Confirm View Class
class UserUsernameChangeConfirmView(APIView):
    """
    User Username Change Confirm API View Class.

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
    object_label: ClassVar[str] = "user_username_change_confirm"

    # Put Method For Username Change Confirmation
    @extend_schema(
        operation_id="User Username Change Confirm",
        request=UserUsernameChangePayloadSerializer,
        responses={
            status.HTTP_200_OK: UserUsernameChangeConfirmResponseSerializer,
            status.HTTP_400_BAD_REQUEST: UserUsernameChangeConfirmBadRequestErrorResponseSerialzier,
            status.HTTP_401_UNAUTHORIZED: UserUsernameChangeConfirmUnauthorizedErrorResponseSerializer,
            status.HTTP_500_INTERNAL_SERVER_ERROR: Generic500ResponseSerializer,
        },
        description="Confirm Username Change Using Token And Update Username",
        summary="Confirm Username Change",
        tags=["User"],
    )
    def put(self, request: Request, token: str) -> Response:
        """
        Process Username Change Confirmation.

        Args:
            request (Request): HTTP Request Object.
            token (str): Username Change Token From URL.

        Returns:
            Response: HTTP Response With Updated User Data Or Error Messages.

        Raises:
            Exception: For Any Unexpected Errors During Username Change Confirmation.
        """

        try:
            # Get Token Cache
            token_cache: BaseCache = caches["token_cache"]

            try:
                # Decode Token
                payload: dict[str, Any] = jwt.decode(
                    jwt=token,
                    key=settings.CHANGE_USERNAME_TOKEN_SECRET,
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
                    data={"error": "Invalid Username Change Token"},
                    status=status.HTTP_401_UNAUTHORIZED,
                )

            # Get User ID
            user_id: str = payload.get("sub")

            # Get Cached Token
            cached_token: str | None = token_cache.get(f"change_username_token_{user_id}")

            # If Token Does Not Match
            if not cached_token or cached_token != token:
                # Return Unauthorized Response
                return Response(
                    data={"error": "Invalid Or Expired Username Change Token"},
                    status=status.HTTP_401_UNAUTHORIZED,
                )

            # Validate Username Payload From Query Params
            payload_data: dict[str, str] = {
                "username": request.data.get("username"),
                "re_username": request.data.get("re_username"),
            }

            # Initialize Payload Serializer
            serializer: UserUsernameChangePayloadSerializer = UserUsernameChangePayloadSerializer(data=payload_data)

            # If Data Is Invalid
            if not serializer.is_valid():
                # Return Validation Error Response
                return Response(
                    data={"errors": serializer.errors},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Extract New Username
            new_username: str = serializer.validated_data.get("username")

            # Check Username Availability
            exists: bool = User.objects.filter(username__iexact=new_username).exists()

            # If Username Already Exists
            if exists:
                # Return Bad Request Response
                return Response(
                    data={"errors": {"username": ["Username Already Exists"]}},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Get User
            user: User = User.objects.get(id=user_id)

            # Store Old Username
            old_username: str = user.username

            # Update Username
            user.username = new_username
            user.save(update_fields=["username"])

            # Revoke Change Username Token
            token_cache.delete(f"change_username_token_{user_id}")

            # Revoke Access & Refresh Tokens
            token_cache.delete(f"access_token_{user_id}")
            token_cache.delete(f"refresh_token_{user_id}")

            # Deactivate User
            user.is_active = False
            user.save(update_fields=["is_active"])

            # Get Current Time
            now_dt: datetime.datetime = datetime.datetime.now(tz=datetime.UTC)

            # Generate Reactivation Token
            reactivation_token: str = jwt.encode(
                payload={
                    "sub": str(user.id),
                    "iss": slugify(settings.PROJECT_NAME),
                    "aud": slugify(settings.PROJECT_NAME),
                    "iat": now_dt,
                    "exp": now_dt + datetime.timedelta(seconds=settings.ACTIVATION_TOKEN_EXPIRY),
                },
                key=settings.REACTIVATION_TOKEN_SECRET,
                algorithm="HS256",
            )

            # Cache Reactivation Token
            token_cache.set(
                key=f"reactivation_token_{user.id}",
                value=reactivation_token,
                timeout=settings.REACTIVATION_TOKEN_EXPIRY,
            )

            # Get Current Site
            current_site: Site = Site.objects.get_current()

            # Determine Protocol (HTTP/HTTPS)
            protocol: str = "https" if request.is_secure() else "http"

            # Generate Reactivation Link
            reactivation_link: str = (
                f"{protocol}://{current_site.domain}/api/users/reactivate/confirm/{reactivation_token}/"
            )

            # Load Success Email Template
            success_email_template: str = render_to_string(
                template_name="users/user_username_change_success_email.html",
                context={
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                    "old_username": old_username,
                    "new_username": new_username,
                    "current_year": now_dt.year,
                    "project_name": settings.PROJECT_NAME,
                },
            )

            # Send Success Email
            send_mail(
                subject=f"Your {settings.PROJECT_NAME} Username Was Updated",
                message="",
                html_message=success_email_template,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
            )

            # Load Reactivation Email Template
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

            # Send Reactivation Email
            send_mail(
                subject=f"Re-Activate Your {settings.PROJECT_NAME} Account",
                message="",
                html_message=reactivation_email_template,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
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
__all__: list[str] = ["UserUsernameChangeConfirmView"]
