# Standard Library Imports
from django.urls import path
from django.urls.resolvers import URLPattern
from django.urls.resolvers import URLResolver

# Local Imports
from apps.users.views import UserActivateView
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
]
