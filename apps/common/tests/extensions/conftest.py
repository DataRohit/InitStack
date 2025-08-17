# Standard Library Imports
from unittest.mock import MagicMock

# Third Party Imports
import pytest
from drf_spectacular.extensions import OpenApiAuthenticationExtension

# Local Imports
from apps.common.extensions.jwt_authentication_extension import JWTAuthenticationExtension


# JWT Authentication Extension Fixture
@pytest.fixture
def jwt_authentication_extension() -> JWTAuthenticationExtension:
    """
    Create JWT Authentication Extension Instance.

    Returns:
        JWTAuthenticationExtension: Instance Of JWT Authentication Extension.
    """

    # Create Instance With Target Parameter
    instance = JWTAuthenticationExtension.__new__(JWTAuthenticationExtension)

    # Set Attributes Manually
    instance.target_class = "apps.common.authentication.jwt_authentication.JWTAuthentication"
    instance.name = "jwtAuth"

    # Return Instance
    return instance


# Mock Auto Schema Fixture
@pytest.fixture
def mock_auto_schema() -> MagicMock:
    """
    Create Mock Auto Schema Instance.

    Returns:
        MagicMock: Mock Auto Schema Instance.
    """

    # Create & Return Mock Auto Schema
    return MagicMock()


# Base Authentication Extension Fixture
@pytest.fixture
def base_authentication_extension() -> OpenApiAuthenticationExtension:
    """
    Create Base Authentication Extension Instance.

    Returns:
        OpenApiAuthenticationExtension: Instance Of Base Authentication Extension.
    """

    # Mock Target Class
    target_class = "test.authentication.TestAuthentication"

    # Return Instance With Target Parameter
    return OpenApiAuthenticationExtension(target=target_class)
