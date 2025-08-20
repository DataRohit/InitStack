# Standard Library Imports
from typing import Any

# Third Party Imports
from opentelemetry import metrics
from opentelemetry.metrics import Counter

# Local Imports
from config.opentelemetry import get_meter

# Get Meter Instance
meter: metrics.Meter = get_meter()


# OAuth Login Initiated Counter
oauth_login_initiated_total: Counter = meter.create_counter(
    name="oauth.login.initiated.total",
    description="Total Number Of OAuth Login Requests Initiated",
    unit="1",
)


# Redirect URI Built Counter
oauth_login_redirect_uri_built_total: Counter = meter.create_counter(
    name="oauth.login.redirect_uri.built.total",
    description="Total Number Of Redirect URIs Built For OAuth Login",
    unit="1",
)


# Backend Loaded Counter
oauth_login_backend_loaded_total: Counter = meter.create_counter(
    name="oauth.login.backend.loaded.total",
    description="Total Number Of OAuth Backends Loaded",
    unit="1",
)


# Auth URL Generated Counter
oauth_login_auth_url_generated_total: Counter = meter.create_counter(
    name="oauth.login.auth_url.generated.total",
    description="Total Number Of OAuth Authorization URLs Generated",
    unit="1",
)


# Record OAuth Login Initiated Function
def record_oauth_login_initiated() -> None:
    """
    Record OAuth Login Initiation.
    """

    # Create Labels
    labels: dict[str, Any] = {}

    # Add Counter Value
    oauth_login_initiated_total.add(1, labels)


# Record Redirect URI Built Function
def record_redirect_uri_built() -> None:
    """
    Record Redirect URI Built.
    """

    # Create Labels
    labels: dict[str, Any] = {}

    # Add Counter Value
    oauth_login_redirect_uri_built_total.add(1, labels)


# Record Backend Loaded Function
def record_backend_loaded() -> None:
    """
    Record OAuth Backend Loaded.
    """

    # Create Labels
    labels: dict[str, Any] = {}

    # Add Counter Value
    oauth_login_backend_loaded_total.add(1, labels)


# Record Auth URL Generated Function
def record_auth_url_generated() -> None:
    """
    Record OAuth Authorization URL Generated.
    """

    # Create Labels
    labels: dict[str, Any] = {}

    # Add Counter Value
    oauth_login_auth_url_generated_total.add(1, labels)


# Exports
__all__: list[str] = [
    "oauth_login_auth_url_generated_total",
    "oauth_login_backend_loaded_total",
    "oauth_login_initiated_total",
    "oauth_login_redirect_uri_built_total",
    "record_auth_url_generated",
    "record_backend_loaded",
    "record_oauth_login_initiated",
    "record_redirect_uri_built",
]
