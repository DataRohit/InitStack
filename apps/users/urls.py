# Standard Library Imports
from django.urls import path
from django.urls.resolvers import URLPattern
from django.urls.resolvers import URLResolver

# Local Imports
from apps.users.views import UserActivateView
from apps.users.views import UserDeactivateConfirmView
from apps.users.views import UserDeactivateRequestView
from apps.users.views import UserDeleteConfirmView
from apps.users.views import UserDeleteRequestView
from apps.users.views import UserEmailChangeConfirmView
from apps.users.views import UserEmailChangeRequestView
from apps.users.views import UserLoginView
from apps.users.views import UserRegisterView
from apps.users.views import UserUsernameChangeConfirmView
from apps.users.views import UserUsernameChangeRequestView

# Set The App Name
app_name: str = "users"

# URL Patterns
urlpatterns: list[URLResolver | URLPattern] = [
    path(
        route="register/",
        view=UserRegisterView.as_view(),
        name="register",
    ),
    path(
        route="activate/<str:token>/",
        view=UserActivateView.as_view(),
        name="activate",
    ),
    path(
        route="login/",
        view=UserLoginView.as_view(),
        name="login",
    ),
    path(
        route="change-username/request/",
        view=UserUsernameChangeRequestView.as_view(),
        name="change_username_request",
    ),
    path(
        route="change-username/confirm/<str:token>/",
        view=UserUsernameChangeConfirmView.as_view(),
        name="change_username_confirm",
    ),
    path(
        route="change-email/request/",
        view=UserEmailChangeRequestView.as_view(),
        name="change_email_request",
    ),
    path(
        route="change-email/confirm/<str:token>/",
        view=UserEmailChangeConfirmView.as_view(),
        name="change_email_confirm",
    ),
    path(
        route="deactivate/request/",
        view=UserDeactivateRequestView.as_view(),
        name="deactivate_request",
    ),
    path(
        route="deactivate/confirm/<str:token>/",
        view=UserDeactivateConfirmView.as_view(),
        name="deactivate_confirm",
    ),
    path(
        route="delete/request/",
        view=UserDeleteRequestView.as_view(),
        name="delete_request",
    ),
    path(
        route="delete/confirm/<str:token>/",
        view=UserDeleteConfirmView.as_view(),
        name="delete_confirm",
    ),
]
