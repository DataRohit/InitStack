# Standard Library Imports
import os
import sys
from pathlib import Path

# Third Party Imports
from django.core.handlers.wsgi import WSGIHandler
from django.core.wsgi import get_wsgi_application
from sentry_sdk.integrations.wsgi import SentryWsgiMiddleware

# Local Imports
from config.opentelemetry import configure_opentelemetry

# Set The Project Base Directory
BASE_DIR: Path = Path(__file__).resolve(strict=True).parent.parent

# Append The Current Path To The Python Path
sys.path.append(str(BASE_DIR / "apps"))

# Set The Default Django Settings Module
os.environ.setdefault(
    key="DJANGO_SETTINGS_MODULE",
    value="config.settings",
)

# Configure OpenTelemetry Before WSGI App Initialization
configure_opentelemetry()

# Get The WSGI Application
application: WSGIHandler = SentryWsgiMiddleware(app=get_wsgi_application())

# Exports
__all__: list[str] = ["application"]
