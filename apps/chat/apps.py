# Third Party imports
from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


# Chat App Configuration Class
class ChatConfig(AppConfig):
    """
    Chat App Configuration Class.

    Attributes:
        name (str): The Name Of The App.
        verbose_name (str): The Verbose Name Of The App.
    """

    # Attributes
    name: str = "apps.chat"
    verbose_name: str = _("Chat")
