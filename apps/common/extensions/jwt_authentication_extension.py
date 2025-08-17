# Third Party Imports
from drf_spectacular.extensions import OpenApiAuthenticationExtension


# JWT Authentication Extension Class
class JWTAuthenticationExtension(OpenApiAuthenticationExtension):
    """
    JWT Authentication OpenAPI Extension Class.

    Attributes:
        target_class (str): Dotted Path To Target Authentication Class.
        name (str): Name For The Security Scheme.
    """

    # Target Authentication Class
    target_class: str = "apps.common.authentication.jwt_authentication.JWTAuthentication"

    # Security Scheme Name
    name: str = "jwtAuth"

    # Get Security Definition Method
    def get_security_definition(self, auto_schema: object) -> dict[str, str]:
        """
        Return Security Scheme Definition For OpenAPI.

        Args:
            auto_schema (object): Auto Schema Instance Provided By DRF Spectacular.

        Returns:
            dict[str, str]: Security Scheme Definition For JWT Bearer Tokens.
        """

        # Return Bearer JWT Security Definition
        return {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
            "description": "Enter JWT Access Token",
        }


# Exports
__all__: list[str] = ["JWTAuthenticationExtension"]
