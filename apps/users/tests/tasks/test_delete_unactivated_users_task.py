# Standard Library Imports
import datetime
import logging
from typing import Any

# Third Party Imports
import pytest
from django.contrib.auth import get_user_model
from django.utils import timezone

from apps.users.models import User

# Local Imports
from apps.users.tasks.delete_unactivated_users_task import delete_unactivated_users

# Get User Model
User: User = get_user_model()


# Delete Unactivated Users Task Tests
@pytest.mark.django_db
class TestDeleteUnactivatedUsersTask:
    """
    Delete Unactivated Users Task Tests.
    """

    # Test Deletion Logic For Matching And Non-Matching Users
    def test_deletes_only_unactivated_users_older_than_30m_with_no_login(
        self,
        monkeypatch: pytest.MonkeyPatch,
        caplog: pytest.LogCaptureFixture,
    ) -> None:
        """
        Delete Only Users With No Login, Not Active, And Joined Before Cutoff.
        """

        # Set Fixed Now
        fixed_now: datetime.datetime = timezone.make_aware(datetime.datetime(2025, 8, 20, 3, 30, 0))

        # Patch Timezone Now
        monkeypatch.setattr(timezone, "now", lambda: fixed_now)

        # Build Cutoff
        cutoff: datetime.datetime = fixed_now - datetime.timedelta(minutes=30)

        # Create Deletable User 1
        deletable_1: User = User.objects.create_user(
            username="del1",
            email="del1@example.com",
            first_name="Del",
            last_name="One",
            password="TestPass123!",
            is_active=False,
            last_login=None,  # type: ignore[assignment]
            date_joined=fixed_now - datetime.timedelta(minutes=31),
        )

        # Create Deletable User 2
        deletable_2: User = User.objects.create_user(
            username="del2",
            email="del2@example.com",
            first_name="Del",
            last_name="Two",
            password="TestPass123!",
            is_active=False,
            last_login=None,  # type: ignore[assignment]
            date_joined=fixed_now - datetime.timedelta(hours=5),
        )

        # Create Non-Deletable Recent Join
        recent_join: User = User.objects.create_user(
            username="keep_recent",
            email="keep_recent@example.com",
            first_name="Keep",
            last_name="Recent",
            password="TestPass123!",
            is_active=False,
            last_login=None,  # type: ignore[assignment]
            date_joined=fixed_now - datetime.timedelta(minutes=15),
        )

        # Create Non-Deletable Has Login
        has_login: User = User.objects.create_user(
            username="keep_login",
            email="keep_login@example.com",
            first_name="Keep",
            last_name="Login",
            password="TestPass123!",
            is_active=False,
            last_login=fixed_now - datetime.timedelta(minutes=10),
            date_joined=fixed_now - datetime.timedelta(minutes=45),
        )

        # Create Non-Deletable Active
        is_active_user: User = User.objects.create_user(
            username="keep_active",
            email="keep_active@example.com",
            first_name="Keep",
            last_name="Active",
            password="TestPass123!",
            is_active=True,
            last_login=None,  # type: ignore[assignment]
            date_joined=fixed_now - datetime.timedelta(minutes=45),
        )

        # Create Boundary Exactly At 30 Minutes (Should Not Delete)
        boundary_user: User = User.objects.create_user(
            username="boundary",
            email="boundary@example.com",
            first_name="Boundary",
            last_name="Case",
            password="TestPass123!",
            is_active=False,
            last_login=None,  # type: ignore[assignment]
            date_joined=cutoff,
        )

        # Capture Logs
        caplog.set_level(logging.INFO)

        # Execute Task
        deleted_count: int = delete_unactivated_users()

        # Assert Return Value
        assert deleted_count == 2  # noqa: PLR2004

        # Assert Deletable Users Are Removed
        remaining_after_delete: int = User.objects.filter(id__in=[deletable_1.id, deletable_2.id]).count()
        assert remaining_after_delete == 0

        # Assert Non-Deletable Users Remain
        remaining_keep_ids: list[Any] = [
            recent_join.id,
            has_login.id,
            is_active_user.id,
            boundary_user.id,
        ]
        assert User.objects.filter(id__in=remaining_keep_ids).count() == 4  # noqa: PLR2004

        # Assert Log Message
        expected_log_snippet: str = "Deleted 2 Unactivated Users Older Than 30 Minutes"
        assert expected_log_snippet in caplog.text

    # Test Zero Deletion Case
    def test_returns_zero_when_no_matching_users_and_logs_info(
        self,
        monkeypatch: pytest.MonkeyPatch,
        caplog: pytest.LogCaptureFixture,
    ) -> None:
        """
        Return Zero When No Users Match The Deletion Criteria.
        """

        # Set Fixed Now
        fixed_now: datetime.datetime = timezone.make_aware(datetime.datetime(2025, 8, 20, 3, 45, 0))

        # Patch Timezone Now
        monkeypatch.setattr(timezone, "now", lambda: fixed_now)

        # Create Only Non-Matching Users
        keep_active: User = User.objects.create_user(
            username="keep_active2",
            email="keep_active2@example.com",
            first_name="Keep",
            last_name="Active2",
            password="TestPass123!",
            is_active=True,
            last_login=None,  # type: ignore[assignment]
            date_joined=fixed_now - datetime.timedelta(hours=1),
        )

        keep_has_login: User = User.objects.create_user(
            username="keep_login2",
            email="keep_login2@example.com",
            first_name="Keep",
            last_name="Login2",
            password="TestPass123!",
            is_active=False,
            last_login=fixed_now - datetime.timedelta(minutes=5),
            date_joined=fixed_now - datetime.timedelta(hours=1),
        )

        keep_recent: User = User.objects.create_user(
            username="keep_recent2",
            email="keep_recent2@example.com",
            first_name="Keep",
            last_name="Recent2",
            password="TestPass123!",
            is_active=False,
            last_login=None,  # type: ignore[assignment]
            date_joined=fixed_now - datetime.timedelta(minutes=10),
        )

        # Capture Logs
        caplog.set_level(logging.INFO)

        # Execute Task
        deleted_count: int = delete_unactivated_users()

        # Assert Return Value
        assert deleted_count == 0

        # Assert Users Still Exist
        assert User.objects.filter(id__in=[keep_active.id, keep_has_login.id, keep_recent.id]).count() == 3  # noqa: PLR2004

        # Assert Log Message Shows Zero
        expected_log_snippet: str = "Deleted 0 Unactivated Users Older Than 30 Minutes"
        assert expected_log_snippet in caplog.text


# Exports
__all__: list[str] = ["TestDeleteUnactivatedUsersTask"]
