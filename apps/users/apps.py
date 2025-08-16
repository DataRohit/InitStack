# Third Party imports
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
