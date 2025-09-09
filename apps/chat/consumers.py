# Standard Library Imports
import json
from typing import Any

# Third Party Imports
from channels.generic.websocket import AsyncWebsocketConsumer


# Chat Consumer Class
class ChatConsumer(AsyncWebsocketConsumer):
    """
    Async Chat Consumer.
    """

    # On Connect
    async def connect(self) -> None:
        """
        Connect To The Chat Consumer.
        """

        # Accept Connection
        await self.accept()

    # On Disconnect
    async def disconnect(self, close_code: int) -> None:
        """
        Disconnect From The Chat Consumer.

        Args:
            close_code (int): The Close Code.
        """

    # On Receive Message
    async def receive(self, text_data: str | None = None, bytes_data: bytes | None = None) -> None:
        """
        Receive Message From The Chat Consumer.

        Args:
            text_data (str | None): The Text Data.
            bytes_data (bytes | None): The Bytes Data.
        """

        # Default Payload
        payload: dict[str, Any] = {"response": "working!"}

        # If Text Data Present
        if text_data is not None:
            try:
                # Parse JSON
                data: dict[str, Any] = json.loads(text_data)

            except json.JSONDecodeError:
                # Set Data To Empty Dictionary
                data = {}

            # Get Message
            message: str | None = data.get("message") if isinstance(data, dict) else None

            # If Message Is Ping
            if message == "ping!":
                # Set Pong Response
                payload = {"response": "pong!"}

        # Send JSON Response
        await self.send(text_data=json.dumps(payload))


# Exports
__all__: list[str] = ["ChatConsumer"]
