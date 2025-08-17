# Standard Library Imports
from django.urls import path
from django.urls.resolvers import URLPattern
from django.urls.resolvers import URLResolver

# Local Imports
from apps.users.views.user_activate_view import UserActivateView
from apps.users.views.user_register_view import UserRegisterView

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
]
