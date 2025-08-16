# Standard Library Imports
from django.urls import path

# Local Imports
from apps.users.views.user_register_view import UserRegisterView

# Set The App Name
app_name: str = "users"

# URL Patterns
urlpatterns: list[path] = [
    path(
        route="register/",
        view=UserRegisterView.as_view(),
        name="register",
    ),
]
