# Third Party imports
from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


# OAuth App Configuration Class
class OAuthConfig(AppConfig):
    """
    OAuth App Configuration Class.

    Attributes:
        name (str): The Name Of The App.
        verbose_name (str): The Verbose Name Of The App.
    """

    # Attributes
    name: str = "apps.oauth"
    verbose_name: str = _("OAuth")
