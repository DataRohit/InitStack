# Standard Library Imports
from django.urls import path
from django.urls.resolvers import URLPattern
from django.urls.resolvers import URLResolver

# Local Imports
from apps.system.views import HealthCheckView

# Set The App Name
app_name: str = "system"

# URL Patterns
urlpatterns: list[URLResolver | URLPattern] = [
    path(
        route="health/",
        view=HealthCheckView.as_view(),
        name="health",
    ),
]
