# Third Party Imports
import json

import pytest
from channels.testing import WebsocketCommunicator

# Local Imports
from config.asgi import application


# Test Ping Message
@pytest.mark.asyncio
async def test_websocket_ping_returns_pong() -> None:
    """
    Ensure Ping Message Returns Pong Response.
    """

    # Create Communicator
    communicator = WebsocketCommunicator(application, "/ws/chat/lobby/")

    # Connect Websocket
    connected, _ = await communicator.connect()

    # Assert Connected
    assert connected is True

    # Send Ping Message
    await communicator.send_to(text_data=json.dumps({"message": "ping!"}))

    # Receive Response
    response_text = await communicator.receive_from()

    # Assert Pong Response
    assert json.loads(response_text) == {"response": "pong!"}

    # Disconnect Websocket
    await communicator.disconnect()


# Test Non Ping Message
@pytest.mark.asyncio
async def test_websocket_other_message_returns_working() -> None:
    """
    Ensure Non Ping Message Returns Working Response.
    """

    # Create Communicator
    communicator = WebsocketCommunicator(application, "/ws/chat/room1/")

    # Connect Websocket
    connected, _ = await communicator.connect()

    # Assert Connected
    assert connected is True

    # Send Non Ping Message
    await communicator.send_to(text_data=json.dumps({"message": "hello"}))

    # Receive Response
    response_text = await communicator.receive_from()

    # Assert Working Response
    assert json.loads(response_text) == {"response": "working!"}

    # Disconnect Websocket
    await communicator.disconnect()


# Test Invalid Json Message
@pytest.mark.asyncio
async def test_websocket_invalid_json_returns_working() -> None:
    """
    Ensure Invalid Json Returns Working Response.
    """

    # Create Communicator
    communicator = WebsocketCommunicator(application, "/ws/chat/test/")

    # Connect Websocket
    connected, _ = await communicator.connect()

    # Assert Connected
    assert connected is True

    # Send Invalid Json
    await communicator.send_to(text_data="not-json")

    # Receive Response
    response_text = await communicator.receive_from()

    # Assert Working Response
    assert json.loads(response_text) == {"response": "working!"}

    # Disconnect Websocket
    await communicator.disconnect()
