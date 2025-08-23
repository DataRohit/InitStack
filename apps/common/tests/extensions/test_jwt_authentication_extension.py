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


# Test Class Attributes
def test_class_attributes(jwt_authentication_extension: JWTAuthenticationExtension) -> None:
    """
    Test Class Attributes Are Set Correctly.
    """

    # Assert Target Class Is Set Correctly
    assert (
        jwt_authentication_extension.target_class == "apps.common.authentication.jwt_authentication.JWTAuthentication"
    )

    # Assert Name Is Set Correctly
    assert jwt_authentication_extension.name == "jwtAuth"


# Test Get Security Definition Method
def test_get_security_definition(
    jwt_authentication_extension: JWTAuthenticationExtension,
    mock_auto_schema: MagicMock,
) -> None:
    """
    Test Get Security Definition Method Returns Correct Schema.
    """

    # Get Security Definition
    security_definition: dict[str, str] = jwt_authentication_extension.get_security_definition(mock_auto_schema)

    # Assert Each Key-Value Pair Individually To Ensure Line Coverage
    assert security_definition["type"] == "http"
    assert security_definition["scheme"] == "bearer"
    assert security_definition["bearerFormat"] == "JWT"
    assert security_definition["description"] == "Enter JWT Access Token"

    # Assert Complete Dictionary
    assert security_definition == {
        "type": "http",
        "scheme": "bearer",
        "bearerFormat": "JWT",
        "description": "Enter JWT Access Token",
    }


# Test Inheritance From OpenApiAuthenticationExtension
def test_inheritance(jwt_authentication_extension: JWTAuthenticationExtension) -> None:
    """
    Test JWT Authentication Extension Inherits From OpenApiAuthenticationExtension.
    """

    # Assert Instance Is OpenApiAuthenticationExtension
    assert isinstance(jwt_authentication_extension, OpenApiAuthenticationExtension)


# Test Auto Schema Parameter Is Not Used
def test_auto_schema_parameter_not_used(
    jwt_authentication_extension: JWTAuthenticationExtension,
    mock_auto_schema: MagicMock,
) -> None:
    """
    Test Auto Schema Parameter Is Not Used In Get Security Definition Method.
    """

    # Call Get Security Definition
    jwt_authentication_extension.get_security_definition(mock_auto_schema)

    # Assert Auto Schema Was Not Used
    assert not mock_auto_schema.method_calls


# Test Security Definition Keys
def test_security_definition_keys(
    jwt_authentication_extension: JWTAuthenticationExtension,
    mock_auto_schema: MagicMock,
) -> None:
    """
    Test Security Definition Contains All Required Keys.
    """

    # Get Security Definition
    security_definition: dict[str, str] = jwt_authentication_extension.get_security_definition(mock_auto_schema)

    # Assert All Required Keys Are Present
    required_keys: list[str] = ["type", "scheme", "bearerFormat", "description"]
    for key in required_keys:
        assert key in security_definition


# Test Security Definition Values Types
def test_security_definition_value_types(
    jwt_authentication_extension: JWTAuthenticationExtension,
    mock_auto_schema: MagicMock,
) -> None:
    """
    Test Security Definition Values Are All Strings.
    """

    # Get Security Definition
    security_definition: dict[str, str] = jwt_authentication_extension.get_security_definition(mock_auto_schema)

    # Assert All Values Are Strings
    for value in security_definition.values():
        assert isinstance(value, str)


# Test Security Definition Is Immutable
def test_security_definition_immutability(
    jwt_authentication_extension: JWTAuthenticationExtension,
    mock_auto_schema: MagicMock,
) -> None:
    """
    Test Security Definition Is Immutable Between Calls.
    """

    # Get Security Definition Twice
    first_definition: dict[str, str] = jwt_authentication_extension.get_security_definition(mock_auto_schema)
    second_definition: dict[str, str] = jwt_authentication_extension.get_security_definition(mock_auto_schema)

    # Assert Definitions Are Equal But Not The Same Object
    assert first_definition == second_definition
    assert first_definition is not second_definition


# Test Dictionary Return Value Coverage
def test_dictionary_return_value(
    jwt_authentication_extension: JWTAuthenticationExtension,
    mock_auto_schema: MagicMock,
) -> None:
    """
    Test Dictionary Return Value Coverage.
    """

    # Get Security Definition
    security_definition: dict[str, str] = jwt_authentication_extension.get_security_definition(mock_auto_schema)

    # Create Expected Dictionary
    expected_dict = {
        "type": "http",
        "scheme": "bearer",
        "bearerFormat": "JWT",
        "description": "Enter JWT Access Token",
    }

    # Assert Dictionary Keys Match
    assert set(security_definition.keys()) == set(expected_dict.keys())

    # Assert Each Key-Value Pair Individually To Ensure Line Coverage
    assert security_definition["type"] == expected_dict["type"]
    assert security_definition["scheme"] == expected_dict["scheme"]
    assert security_definition["bearerFormat"] == expected_dict["bearerFormat"]
    assert security_definition["description"] == expected_dict["description"]
