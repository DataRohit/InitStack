# Third Party Imports
import pytest
from channels.testing import WebsocketCommunicator

# Local Imports
from config.asgi import application


# Test Route Accepts Connection
@pytest.mark.asyncio
async def test_chat_route_accepts_websocket_connection() -> None:
    """
    Ensure Route Accepts Websocket Connection.
    """

    # Create Communicator
    communicator = WebsocketCommunicator(application, "/ws/chat/lobby/")

    # Connect Websocket
    connected, _ = await communicator.connect()

    # Assert Connected
    assert connected is True

    # Disconnect Websocket
    await communicator.disconnect()
