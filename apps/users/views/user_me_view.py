# Standard Library Imports
import logging
from typing import Any
from typing import ClassVar

# Third Party Imports
from django.contrib.auth import get_user_model
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
from apps.common.authentication.jwt_authentication import JWTAuthentication
from apps.common.renderers import GenericJSONRenderer
from apps.common.serializers.generic_response_serializer import Generic500ResponseSerializer
from apps.users.models import User
from apps.users.serializers import UserDetailSerializer
from apps.users.serializers import UserMeResponseSerializer
from apps.users.serializers import UserMeUnauthorizedErrorResponseSerializer

# Logger
logger = logging.getLogger(__name__)

# Get User Model
User: User = get_user_model()


# User Me View Class
class UserMeView(APIView):
    """
    User Me API View Class.

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
    object_label: ClassVar[str] = "user"

    # Get Method For User Me
    @extend_schema(
        operation_id="User Me",
        request=None,
        responses={
            status.HTTP_200_OK: UserMeResponseSerializer,
            status.HTTP_401_UNAUTHORIZED: UserMeUnauthorizedErrorResponseSerializer,
            status.HTTP_500_INTERNAL_SERVER_ERROR: Generic500ResponseSerializer,
        },
        description="Retrieve Current Authenticated User Information",
        summary="Get Current User",
        tags=["User"],
    )
    def get(self, request: Request) -> Response:
        """
        Retrieve Current Authenticated User Information.

        Args:
            request (Request): HTTP Request Object.

        Returns:
            Response: HTTP Response With User Data.

        Raises:
            Exception: For Any Unexpected Errors During User Data Retrieval.
        """

        try:
            # Get Current User
            user: User = request.user

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
__all__: list[str] = ["UserMeView"]
