# Third Party Imports
from django.urls import re_path

# Local Imports
from apps.chat.consumers import ChatConsumer

# Websocket URL Patterns
websocket_urlpatterns: list[re_path] = [
    re_path(r"^ws/chat/(?P<room_name>\w+)/$", ChatConsumer.as_asgi()),
]

# Exports
__all__: list[str] = ["websocket_urlpatterns"]
