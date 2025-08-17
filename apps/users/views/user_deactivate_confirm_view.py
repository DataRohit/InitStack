# Standard Library Imports
import datetime
import logging
from typing import Any
from typing import ClassVar

import jwt
from django.conf import settings
from django.contrib.auth import get_user_model

# Third Party Imports
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
from apps.users.serializers import UserDeactivateConfirmUnauthorizedErrorResponseSerializer
from apps.users.serializers import UserDeactivateResponseSerializer
from apps.users.serializers import UserDetailSerializer

# Logger
logger = logging.getLogger(__name__)

# Get User Model
User: User = get_user_model()


# User Deactivate Confirm View Class
class UserDeactivateConfirmView(APIView):
    """
    User Deactivate Confirm API View Class.

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
    object_label: ClassVar[str] = "user_deactivate_confirm"

    # Get Method For Deactivate Confirmation
    @extend_schema(
        operation_id="User Deactivate Confirm",
        request=None,
        responses={
            status.HTTP_200_OK: UserDeactivateResponseSerializer,
            status.HTTP_401_UNAUTHORIZED: UserDeactivateConfirmUnauthorizedErrorResponseSerializer,
            status.HTTP_500_INTERNAL_SERVER_ERROR: Generic500ResponseSerializer,
        },
        description="Confirm Account Deactivation Using Token",
        summary="Confirm Deactivation",
        tags=["User"],
    )
    def get(self, request: Request, token: str) -> Response:
        """
        Process Deactivation Confirmation.

        Args:
            request (Request): HTTP Request Object.
            token (str): Deactivation Token From URL.

        Returns:
            Response: HTTP Response With Success Or Error Message.

        Raises:
            Exception: For Any Unexpected Errors During Deactivation.
        """

        try:
            # Get Token Cache
            token_cache: BaseCache = caches["token_cache"]

            try:
                # Decode Token
                payload: dict[str, Any] = jwt.decode(
                    jwt=token,
                    key=settings.DEACTIVATION_TOKEN_SECRET,
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
                    data={"error": "Invalid Deactivation Token"},
                    status=status.HTTP_401_UNAUTHORIZED,
                )

            # Get User ID
            user_id: str = payload.get("sub")

            # Get Cached Token
            cached_token: str | None = token_cache.get(f"deactivation_token_{user_id}")

            # If Token Does Not Match
            if not cached_token or cached_token != token:
                # Return Unauthorized Response
                return Response(
                    data={"error": "Invalid Or Expired Deactivation Token"},
                    status=status.HTTP_401_UNAUTHORIZED,
                )

            # Get User
            user: User = User.objects.get(id=user_id)

            # Deactivate User
            user.is_active = False
            user.save(update_fields=["is_active"])

            # Revoke Deactivation Token
            token_cache.delete(f"deactivation_token_{user_id}")

            # Revoke Access & Refresh Tokens
            token_cache.delete(f"access_token_{user_id}")
            token_cache.delete(f"refresh_token_{user_id}")

            # Get Current Time
            now_dt: datetime.datetime = datetime.datetime.now(tz=datetime.UTC)

            # Get Current Site
            current_site: Site = Site.objects.get_current()

            # Determine Protocol (HTTP/HTTPS)
            protocol: str = "https" if request.is_secure() else "http"

            # Generate Reactivation Link
            reactivation_link: str = f"{protocol}://{current_site.domain}/api/users/reactivate/request/"

            # Load Deactivation Email Template
            deactivation_email_template: str = render_to_string(
                template_name="users/user_deactivate_success_email.html",
                context={
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                    "email": user.email,
                    "reactivation_link": reactivation_link,
                    "current_year": now_dt.year,
                    "project_name": settings.PROJECT_NAME,
                },
            )

            # Send Deactivation Email
            send_mail(
                subject=f"Your {settings.PROJECT_NAME} Account Has Been Deactivated",
                message="",
                html_message=deactivation_email_template,
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
__all__: list[str] = ["UserDeactivateConfirmView"]
