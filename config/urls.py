# Third Party Imports
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.urls import include
from django.urls import path
from django.urls.resolvers import URLPattern
from django.urls.resolvers import URLResolver
from drf_spectacular.views import SpectacularAPIView
from drf_spectacular.views import SpectacularRedocView
from drf_spectacular.views import SpectacularSwaggerView

# Admin & Media URLs
urlpatterns: list[URLPattern | URLResolver] = [
    path(
        route=settings.ADMIN_URL,
        view=admin.site.urls,
    ),
    *static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT),
]

# If Debug
if settings.DEBUG:
    # Static Files URLs
    urlpatterns += staticfiles_urlpatterns()

# Swagger URLs
urlpatterns += [
    path(
        route="api/swagger/schema/",
        view=SpectacularAPIView.as_view(),
        name="api-schema",
    ),
    path(
        route="api/swagger/ui/",
        view=SpectacularSwaggerView.as_view(url_name="api-schema"),
        name="api-swagger",
    ),
    path(
        route="api/swagger/redoc/",
        view=SpectacularRedocView.as_view(url_name="api-schema"),
        name="api-redoc",
    ),
]

# If Debug
if settings.DEBUG:
    # Health Check URLs
    urlpatterns += [
        path(
            route="health/",
            view=include("health_check.urls"),
        ),
    ]

    # Silk URLs
    urlpatterns += [
        path(
            route="silk/",
            view=include("silk.urls", namespace="silk"),
        ),
    ]

# App URLs
urlpatterns += [
    path(
        route="api/users/",
        view=include("apps.users.urls", namespace="users"),
    ),
]
