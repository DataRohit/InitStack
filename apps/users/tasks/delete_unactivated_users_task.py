# Standard Library Imports
import datetime
import logging
from typing import TYPE_CHECKING

# Third Party Imports
from celery import shared_task
from django.utils import timezone

# Local Imports
from apps.users.models.user_model import User

# If Type Checking
if TYPE_CHECKING:
    # Third Party Imports
    from django.db.models import QuerySet


# Logger Instance
logger: logging.Logger = logging.getLogger(__name__)


# Delete Unactivated Users Task
@shared_task(name="users.delete_unactivated_users")
def delete_unactivated_users() -> int:
    """
    Delete Unactivated Users Older Than 30 Minutes With No Login

    Args:
        None

    Returns:
        int: Number Of Deleted User Records

    Raises:
        Exception: For Any Unexpected Errors During Deletion
    """

    # Compute Cutoff Time
    cutoff: datetime.datetime = timezone.now() - datetime.timedelta(minutes=30)

    # Build Deletion Queryset
    qs: QuerySet[User] = User.objects.filter(
        last_login__isnull=True,
        date_joined__lt=cutoff,
        is_active=False,
    )

    # Execute Delete
    deleted_total_and_breakdown: tuple[int, dict[str, int]] = qs.delete()
    deleted_count: int = deleted_total_and_breakdown[0]

    # Log Deletion Result
    logger.info("Deleted %s Unactivated Users Older Than 30 Minutes", deleted_count)

    # Return Deleted Count
    return deleted_count


# Exports
__all__: list[str] = ["delete_unactivated_users"]
