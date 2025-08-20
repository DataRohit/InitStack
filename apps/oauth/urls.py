# Standard Library Imports
from django.urls import path
from django.urls.resolvers import URLPattern
from django.urls.resolvers import URLResolver

# Local Imports
from apps.oauth.views import OAuthCallbackView
from apps.oauth.views import OAuthLoginView

# Set The App Name
app_name: str = "oauth"

# URL Patterns
urlpatterns: list[URLResolver | URLPattern] = [
    path(
        "<str:backend_name>/login/",
        OAuthLoginView.as_view(),
        name="oauth_login",
    ),
    path(
        "<str:backend_name>/callback/",
        OAuthCallbackView.as_view(),
        name="oauth_callback",
    ),
]
