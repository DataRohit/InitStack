# Standard Library Imports
from unittest.mock import MagicMock
from unittest.mock import patch

# Local Imports
import apps.users.opentelemetry.views.user_logout_metrics as ulo_metrics
from apps.users.opentelemetry.views.user_logout_metrics import record_logout_initiated
from apps.users.opentelemetry.views.user_logout_metrics import record_tokens_revoked


# Test Logout Initiated Recorder
def test_record_logout_initiated_calls_counter() -> None:
    """
    Verify record_logout_initiated Adds To Counter With Empty Labels.
    """

    # Patch Metric
    with patch.object(
        ulo_metrics,
        "user_logout_initiated_total",
    ) as initiated_total:
        # Type Hint
        initiated_total: MagicMock

        # Call Function
        record_logout_initiated()

    # Assert Call
    initiated_total.add.assert_called_once_with(1, {})


# Test Tokens Revoked Recorder
def test_record_tokens_revoked_calls_counter() -> None:
    """
    Verify record_tokens_revoked Adds To Counter With Token Type Label.
    """

    # Input
    token_type: str = "access"  # noqa: S105

    # Patch Metric
    with patch.object(
        ulo_metrics,
        "user_logout_tokens_revoked_total",
    ) as revoked_total:
        # Type Hint
        revoked_total: MagicMock

        # Call Function
        record_tokens_revoked(token_type=token_type)

    # Assert Call
    revoked_total.add.assert_called_once_with(1, {"token_type": token_type})
