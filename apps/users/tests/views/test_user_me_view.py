# Standard Library Imports
from typing import TYPE_CHECKING
from unittest.mock import patch

# Third Party Imports
import pytest
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APIRequestFactory
from rest_framework.test import force_authenticate

# Local Imports
from apps.users.views.user_me_view import UserMeView

# If Type Checking
if TYPE_CHECKING:
    # Third Party Imports
    from rest_framework.request import Request

# Get User Model
User = get_user_model()

# Enable Django DB Access For All Tests In This Module
pytestmark = pytest.mark.django_db


# 200 Success Path Test
def test_user_me_success_returns_200_with_user() -> None:
    """
    Authenticated Request Should Return 200 With User Payload.
    """

    # User
    user = User.objects.create_user(
        username="meok",
        email="meok@example.com",
        password="SecurePassword@123",
        is_active=True,
    )

    # Request
    factory: APIRequestFactory = APIRequestFactory()
    request: Request = factory.get("/api/users/me/")
    force_authenticate(request, user=user)

    # Patch Metrics
    with (
        patch("apps.users.views.user_me_view.record_http_request") as rec_http,
        patch("apps.users.views.user_me_view.record_user_action") as rec_action,
        patch("apps.users.views.user_me_view.record_me_retrieved") as rec_me,
    ):
        response = UserMeView.as_view()(request)

    # Assert
    assert response.status_code == status.HTTP_200_OK
    assert "user" in response.data

    # Metrics
    rec_http.assert_called()
    rec_action.assert_called()
    rec_me.assert_called_once()


# 500 Error Path Test
def test_user_me_error_returns_500() -> None:
    """
    Unexpected Exception Should Return 500 And Record Metrics.
    """

    # User
    user = User.objects.create_user(
        username="meerr",
        email="meerr@example.com",
        password="SecurePassword@123",
        is_active=True,
    )

    # Request
    factory: APIRequestFactory = APIRequestFactory()
    request: Request = factory.get("/api/users/me/")
    force_authenticate(request, user=user)

    # Patch Serializer To Raise
    with (
        patch("apps.users.views.user_me_view.UserDetailSerializer", side_effect=Exception("boom")),
        patch("apps.users.views.user_me_view.record_api_error") as rec_api_error,
        patch("apps.users.views.user_me_view.record_http_request") as rec_http,
        patch("apps.users.views.user_me_view.record_user_action") as rec_action,
    ):
        response = UserMeView.as_view()(request)

    # Assert
    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert response.data == {"error": "Internal Server Error"}

    # Metrics
    rec_api_error.assert_called()
    rec_http.assert_called()
    rec_action.assert_called()
