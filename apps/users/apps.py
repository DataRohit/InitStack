# Third Party imports
from celery import current_app as celery_app
from celery.schedules import timedelta
from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


# Users App Configuration Class
class UsersConfig(AppConfig):
    """
    Users App Configuration Class.

    Attributes:
        name (str): The Name Of The App.
        verbose_name (str): The Verbose Name Of The App.
    """

    # Attributes
    name: str = "apps.users"
    verbose_name: str = _("Users")

    # Ready Function
    def ready(self):
        """
        Ready Function To Configure Periodic Tasks.
        """

        # Local Imports
        from apps.users.tasks import delete_unactivated_users  # noqa: PLC0415

        # Configure Periodic Tasks
        celery_app.add_periodic_task(
            timedelta(seconds=30),
            delete_unactivated_users.s(),
            name="delete_unactivated_users_every_30s",
        )
