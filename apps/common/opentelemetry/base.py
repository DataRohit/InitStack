# Standard Library Imports
from typing import Any

# Third Party Imports
from opentelemetry import metrics
from opentelemetry.metrics import Counter
from opentelemetry.metrics import Histogram

# Local Imports
from config.opentelemetry import get_meter

# Get Global Meter Instance
meter: metrics.Meter = get_meter()


# HTTP Requests Counter
# Tracks The Total Number of HTTP Requests Processed by the API Views.
# Labels: Method (e.g., 'GET', 'POST'), Endpoint (e.g., '/api/users/activate'), Status Code (e.g., 200, 401)
http_requests_total: Counter = meter.create_counter(
    name="http.requests.total",
    description="Total Number of HTTP Requests",
    unit="1",
)


# HTTP Request Duration Histogram
# Measures The Duration of HTTP Requests in Seconds.
# Labels: Method, Endpoint, Status Code
http_request_duration: Histogram = meter.create_histogram(
    name="http.request.duration",
    description="Duration of HTTP Requests",
    unit="s",
)


# API Errors Counter
# Counts The Number of Errors (Exceptions) Occurring in API Views.
# Labels: Endpoint, Error Type (e.g., 'ValidationError', 'InternalServerError')
api_errors_total: Counter = meter.create_counter(
    name="api.errors.total",
    description="Total Number of API Errors",
    unit="1",
)


# User Actions Counter
# Tracks The Total Number of User-Related Actions Across Views (e.g., Login, Register, Activate).
# Labels: Action Type (e.g., 'login', 'register', 'activate', 'deactivate'), Success (true/false)
user_actions_total: Counter = meter.create_counter(
    name="user.actions.total",
    description="Total Number of User Actions",
    unit="1",
)


# Token Validations Counter
# Counts The Number of Token Validation Attempts in Views (e.g., JWT Decode for Activation, Reset Password).
# Labels: Token Type (e.g., 'activation', 'reset_password', 'refresh'), Success (true/false)
token_validations_total: Counter = meter.create_counter(
    name="token.validations.total",
    description="Total Number of Token Validations",
    unit="1",
)


# Emails Sent Counter
# Tracks The Number of Emails Sent from Views (e.g., Activation, Reset Password Emails).
# Labels: Email Type (e.g., 'activation', 'reset_password', 'welcome'), Success (true/false)
emails_sent_total: Counter = meter.create_counter(
    name="emails.sent.total",
    description="Total Number of Emails Sent",
    unit="1",
)


# Cache Operations Counter
# Counts The Number of Cache Operations (get/set/delete) Used in Views for Tokens.
# Labels: Operation (get, set, delete), Cache Type (e.g., 'token_cache'), Success (true/false)
cache_operations_total: Counter = meter.create_counter(
    name="cache.operations.total",
    description="Total Number of Cache Operations",
    unit="1",
)


# User Updates Counter
# Tracks The Number of User Model Updates (e.g., Activate, Deactivate, Change Email/Username).
# Labels: Update Type (e.g., 'activate', 'deactivate', 'email_change'), Success (true/false)
user_updates_total: Counter = meter.create_counter(
    name="user.updates.total",
    description="Total Number of User Updates",
    unit="1",
)


# Function to Record HTTP Request Metrics
def record_http_request(method: str, endpoint: str, status_code: int, duration: float) -> None:
    """
    Record Metrics for an HTTP Request.

    Args:
        method (str): HTTP Method (e.g., 'GET', 'POST').
        endpoint (str): API Endpoint Path.
        status_code (int): HTTP Response Status Code.
        duration (float): Request processing duration in seconds.
    """

    # Create Labels
    labels: dict[str, Any] = {
        "method": method,
        "endpoint": endpoint,
        "status_code": status_code,
    }

    # Record HTTP Requests Total
    http_requests_total.add(1, labels)

    # Record HTTP Request Duration
    http_request_duration.record(duration, labels)


# Function to Record API Error
def record_api_error(endpoint: str, error_type: str) -> None:
    """
    Record an API Error Occurrence.

    Args:
        endpoint (str): API Endpoint Path.
        error_type (str): Type of Error (e.g., 'ValidationError').
    """

    # Create Labels
    labels: dict[str, Any] = {
        "endpoint": endpoint,
        "error_type": error_type,
    }

    # Record API Errors Total
    api_errors_total.add(1, labels)


# Function to Record User Action
def record_user_action(action_type: str, *, success: bool) -> None:
    """
    Record a User Action.

    Args:
        action_type (str): Type of User Action (e.g., 'login').
        success (bool): Whether the Action was Successful.
    """

    # Create Labels
    labels: dict[str, Any] = {
        "action_type": action_type,
        "success": success,
    }

    # Record User Actions Total
    user_actions_total.add(1, labels)


# Function to Record Token Validation
def record_token_validation(token_type: str, *, success: bool) -> None:
    """
    Record a Token Validation Attempt.

    Args:
        token_type (str): Type of Token (e.g., 'activation').
        success (bool): Whether the Validation was Successful.
    """

    # Create Labels
    labels: dict[str, Any] = {
        "token_type": token_type,
        "success": success,
    }

    # Record Token Validations Total
    token_validations_total.add(1, labels)


# Function to Record Email Sent
def record_email_sent(email_type: str, *, success: bool) -> None:
    """
    Record an Email Sending Attempt.

    Args:
        email_type (str): Type of Email (e.g., 'activation').
        success (bool): Whether the Email was Sent Successfully.
    """

    # Create Labels
    labels: dict[str, Any] = {
        "email_type": email_type,
        "success": success,
    }

    # Record Emails Sent Total
    emails_sent_total.add(1, labels)


# Function to Record Cache Operation
def record_cache_operation(operation: str, cache_type: str, *, success: bool) -> None:
    """
    Record a Cache Operation.

    Args:
        operation (str): Cache Operation (e.g., 'get', 'set').
        cache_type (str): Type of Cache (e.g., 'token_cache').
        success (bool): Whether the Operation was Successful.
    """

    # Create Labels
    labels: dict[str, Any] = {
        "operation": operation,
        "cache_type": cache_type,
        "success": success,
    }

    # Record Cache Operations Total
    cache_operations_total.add(1, labels)


# Function to Record User Update
def record_user_update(update_type: str, *, success: bool) -> None:
    """
    Record a User Update Operation.

    Args:
        update_type (str): Type of Update (e.g., 'activate').
        success (bool): Whether the Update was Successful.
    """

    # Create Labels
    labels: dict[str, Any] = {
        "update_type": update_type,
        "success": success,
    }

    # Record User Updates Total
    user_updates_total.add(1, labels)


# Exports
__all__: list[str] = [
    "api_errors_total",
    "cache_operations_total",
    "emails_sent_total",
    "http_request_duration",
    "http_requests_total",
    "record_api_error",
    "record_cache_operation",
    "record_email_sent",
    "record_http_request",
    "record_token_validation",
    "record_user_action",
    "record_user_update",
    "token_validations_total",
    "user_actions_total",
    "user_updates_total",
]
