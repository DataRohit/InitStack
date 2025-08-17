# Standard Library Imports
import json
from typing import Any

# Third Party Imports
from django.utils.translation import gettext_lazy as _
from rest_framework.renderers import JSONRenderer


# Generic JSON Renderer Class
class GenericJSONRenderer(JSONRenderer):
    """
    Generic JSON Renderer For Standardizing API Responses.

    Attributes:
        charset (str): Character Encoding For The Rendered Content.
        object_label (str): Default Label For The Object In The Response.

    Methods:
        render() -> bytes: Render The Data Into JSON With Standardized Format.
    """

    # Character Encoding For Output
    charset: str = "utf-8"

    # Default Object Label For Response
    object_label: str = "object"

    # Render Method
    def render(
        self,
        data: dict[str, Any],
        accepted_media_type: str | None = None,
        renderer_context: dict[str, Any] | None = None,
    ) -> bytes:
        """
        Render The Data Into JSON With Standardized Format.

        Args:
            data (dict[str, Any]): The Data To Be Rendered, Typically From The Serializer.
            accepted_media_type (str | None): The Media Type Accepted By The Request.
            renderer_context (dict[str, Any] | None): Context Dictionary From The Renderer.

        Returns:
            bytes: JSON Encoded Response With Standardized Structure.

        Raises:
            ValueError: If Renderer Context Doesn't Contain A Response Object.
        """

        # If Renderer Context Is None
        if renderer_context is None:
            # Set Renderer Context To Empty Dict
            renderer_context = {}

        # Get View From Renderer Context
        view: Any = renderer_context.get("view")

        # Get Object Label From View Or Use Default
        object_label: str = getattr(view, "object_label", self.object_label)

        # Get Response Object From Renderer Context
        response: Any = renderer_context.get("response")

        # If Response Object Is Not Found
        if not response:
            # Raise A Validation Error
            raise ValueError(
                _("Renderer Context Does Not Contain A Response Object"),
            ) from None

        # Get Status Code From Response
        status_code: int = response.status_code

        # If Error In Data
        if "error" in data:
            # Return The Error Response
            return json.dumps(
                {
                    "status_code": status_code,
                    "error": data["error"],
                },
            ).encode(self.charset)

        # If Errors In Data
        if "errors" in data:
            # Return The Error Response
            return json.dumps(
                {
                    "status_code": status_code,
                    "errors": data["errors"],
                },
            ).encode(self.charset)

        # Return Standardized Response Format
        return json.dumps(
            {
                "status_code": status_code,
                object_label: data,
            },
        ).encode(self.charset)


# Exports
__all__: list[str] = ["GenericJSONRenderer"]
