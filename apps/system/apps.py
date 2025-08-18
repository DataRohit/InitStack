# Third Party imports
from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


# System App Configuration Class
class SystemConfig(AppConfig):
    """
    System App Configuration Class.

    Attributes:
        name (str): The Name Of The App.
        verbose_name (str): The Verbose Name Of The App.
    """

    # Attributes
    name: str = "apps.system"
    verbose_name: str = _("System")
