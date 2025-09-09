# Standard Library Imports
from collections.abc import Awaitable
from collections.abc import Callable
from typing import Any


# Websocket Application Function
async def websocket_application(
    scope: dict[str, Any],
    receive: Callable[[], Awaitable[dict[str, Any]]],
    send: Callable[[dict[str, Any]], Awaitable[None]],
) -> None:
    """
    Handle WebSocket Connections And Messages.

    Args:
        scope (dict[str, Any]): The ASGI Scope dictionary.
        receive (Callable[[], Awaitable[dict[str, Any]]]): The ASGI Receive Callable.
        send (Callable[[dict[str, Any]], Awaitable[None]]): The ASGI Send Callable.

    Returns:
        None
    """

    # Loop Forever
    while True:
        # Get Event
        event: dict[str, Any] = await receive()

        # If Websocket Connect
        if event["type"] == "websocket.connect":
            # Accept Connection
            await send({"type": "websocket.accept"})

        # If Websocket Disconnect
        if event["type"] == "websocket.disconnect":
            # Break Loop
            break

        # If Websocket Receive
        if event["type"] == "websocket.receive":
            # If Event Text Is Ping
            if event["text"] == "ping":
                # Send Pong
                await send({"type": "websocket.send", "text": "pong!"})


# Exports
__all__: list[str] = ["websocket_application"]
