# Standard Library Imports
import json
from types import SimpleNamespace
from typing import Any

# Third Party Imports
import pytest

# Local Imports
from apps.common.renderers.generic_json_renderer import GenericJSONRenderer


# Test Generic JSON Renderer Behavior
def test_render_raises_without_response_in_context() -> None:
    """
    Test Renderer Raises When Response Missing In Context.
    """

    # Create Renderer
    renderer: GenericJSONRenderer = GenericJSONRenderer()

    # Assert Raises ValueError
    with pytest.raises(ValueError) as exc:  # noqa: PT011
        # Call Render
        renderer.render(data={"a": 1}, renderer_context={})

    # Assert Message Contains Keyword
    assert "Response Object" in str(exc.value)


# Test 204 Status Returns Empty Bytes
def test_render_returns_empty_on_204() -> None:
    """
    Test 204 Status Returns Empty Bytes.
    """

    # Create Renderer
    renderer: GenericJSONRenderer = GenericJSONRenderer()

    # Build Context With 204 Status
    response: Any = SimpleNamespace(status_code=204)
    context: dict[str, Any] = {"response": response, "view": SimpleNamespace()}

    # Render Response
    output: bytes = renderer.render(data={}, renderer_context=context)

    # Assert Empty Bytes
    assert output == b""


# Test Context None Falls Back To Empty Dict
def test_render_sets_default_context_when_none() -> None:
    """
    Test Renderer Uses Empty Context When None.
    """

    # Create Renderer
    renderer: GenericJSONRenderer = GenericJSONRenderer()

    # Assert Raises ValueError Due To Missing Response
    with pytest.raises(ValueError) as exc:  # noqa: PT011
        # Call Render With None Context
        renderer.render(data={}, renderer_context=None)

    # Assert Message Contains Keyword
    assert "Response Object" in str(exc.value)


# Test Message Key Produces Message Payload
def test_render_message_path() -> None:
    """
    Test Message Key Produces Message Payload.
    """

    # Create Renderer
    renderer: GenericJSONRenderer = GenericJSONRenderer()

    # Build Context
    response: Any = SimpleNamespace(status_code=200)
    context: dict[str, Any] = {"response": response, "view": SimpleNamespace()}

    # Render Message Payload
    output: bytes = renderer.render(data={"message": "Hello"}, renderer_context=context)

    # Assert JSON Content
    payload: dict[str, Any] = json.loads(output.decode("utf-8"))
    assert payload == {"status_code": 200, "message": "Hello"}


# Test Error Key Produces Error Payload
def test_render_error_path() -> None:
    """
    Test Error Key Produces Error Payload.
    """

    # Create Renderer
    renderer: GenericJSONRenderer = GenericJSONRenderer()

    # Build Context
    response: Any = SimpleNamespace(status_code=400)
    context: dict[str, Any] = {"response": response, "view": SimpleNamespace()}

    # Render Error Payload
    error_obj: dict[str, Any] = {"detail": "Bad Request"}
    output: bytes = renderer.render(data={"error": error_obj}, renderer_context=context)

    # Assert JSON Content
    payload: dict[str, Any] = json.loads(output.decode("utf-8"))
    assert payload == {"status_code": 400, "error": error_obj}


# Test Errors Key Produces Errors Payload
def test_render_errors_path() -> None:
    """
    Test Errors Key Produces Errors Payload.
    """

    # Create Renderer
    renderer: GenericJSONRenderer = GenericJSONRenderer()

    # Build Context
    response: Any = SimpleNamespace(status_code=422)
    context: dict[str, Any] = {"response": response, "view": SimpleNamespace()}

    # Render Errors Payload
    errors_obj: dict[str, Any] = {"field": ["Invalid Value"]}
    output: bytes = renderer.render(data={"errors": errors_obj}, renderer_context=context)

    # Assert JSON Content
    payload: dict[str, Any] = json.loads(output.decode("utf-8"))
    assert payload == {"status_code": 422, "errors": errors_obj}


# Test Default Path Uses "object" Label
def test_render_default_uses_default_label() -> None:
    """
    Test Default Path Uses "object" Label.
    """

    # Create Renderer
    renderer: GenericJSONRenderer = GenericJSONRenderer()

    # Build Context
    response: Any = SimpleNamespace(status_code=201)
    context: dict[str, Any] = {"response": response, "view": SimpleNamespace()}

    # Render Default Payload
    data_obj: dict[str, Any] = {"id": 1, "name": "Item"}
    output: bytes = renderer.render(data=data_obj, renderer_context=context)

    # Assert JSON Content
    payload: dict[str, Any] = json.loads(output.decode("utf-8"))
    assert payload == {"status_code": 201, "object": data_obj}


# Test Default Path Uses View's Object Label
def test_render_default_uses_custom_label_from_view() -> None:
    """
    Test Default Path Uses View's Object Label.
    """

    # Create Renderer
    renderer: GenericJSONRenderer = GenericJSONRenderer()

    # Build Context With Custom View Label
    response: Any = SimpleNamespace(status_code=200)
    view: Any = SimpleNamespace(object_label="item")
    context: dict[str, Any] = {"response": response, "view": view}

    # Render Default Payload
    data_obj: dict[str, Any] = {"id": 2}
    output: bytes = renderer.render(data=data_obj, renderer_context=context)

    # Assert JSON Content
    payload: dict[str, Any] = json.loads(output.decode("utf-8"))
    assert payload == {"status_code": 200, "item": data_obj}
