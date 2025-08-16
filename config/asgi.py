# Standard Library Imports
import os
import sys
from pathlib import Path

# Third Party Imports
from django.core.asgi import get_asgi_application
from django.core.handlers.asgi import ASGIHandler
from sentry_sdk.integrations.asgi import SentryAsgiMiddleware

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

# Configure OpenTelemetry Before ASGI App Initialization
configure_opentelemetry()

# Get The ASGI Application
application: ASGIHandler = SentryAsgiMiddleware(app=get_asgi_application())

# Exports
__all__: list[str] = ["application"]
