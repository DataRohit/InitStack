# Third Party Imports
from rest_framework import status

# Local Imports
from apps.oauth.serializers.oauth_login_serializer import OAuthLoginResponseSerializer


# OAuth Login Response Serializer: Valid Case
def test_oauth_login_response_serializer_valid() -> None:
    """
    Valid Payload Should Validate Successfully.
    """

    # Build Payload
    data = {
        "status_code": status.HTTP_200_OK,
        "data": {"auth_url": "https://example.com/api/users/oauth/google/callback/"},
    }

    # Initialize Serializer
    ser = OAuthLoginResponseSerializer(data=data)

    # Assert Validation
    assert ser.is_valid(), ser.errors

    # Assert Values
    assert ser.validated_data["status_code"] == status.HTTP_200_OK
    assert ser.validated_data["data"]["auth_url"].startswith("https://")


# OAuth Login Response Serializer: Missing Data Field
def test_oauth_login_response_serializer_missing_data() -> None:
    """
    Missing Data Should Fail Validation.
    """

    # Build Payload
    data = {"status_code": status.HTTP_200_OK}

    # Initialize Serializer
    ser = OAuthLoginResponseSerializer(data=data)

    # Assert Invalid
    assert not ser.is_valid()

    # Assert Error Key
    assert "data" in ser.errors


# OAuth Login Response Serializer: Null Data Not Allowed
def test_oauth_login_response_serializer_null_data() -> None:
    """
    Null Data Should Fail Validation.
    """

    # Build Payload
    data = {"status_code": status.HTTP_200_OK, "data": None}

    # Initialize Serializer
    ser = OAuthLoginResponseSerializer(data=data)

    # Assert Invalid
    assert not ser.is_valid()

    # Assert Error Key
    assert "data" in ser.errors


# OAuth Login Response Serializer: Missing Auth URL Field
def test_oauth_login_response_serializer_missing_auth_url() -> None:
    """
    Missing Auth URL Should Fail Validation.
    """

    # Build Payload
    data = {"status_code": status.HTTP_200_OK, "data": {}}

    # Initialize Serializer
    ser = OAuthLoginResponseSerializer(data=data)

    # Assert Invalid
    assert not ser.is_valid()

    # Assert Error Key
    assert "data" in ser.errors or "auth_url" in ser.errors.get("data", {})


# OAuth Login Response Serializer: Missing Status Code Field
def test_oauth_login_response_serializer_missing_status_code() -> None:
    """
    Missing Status Code Should Fail Validation.
    """

    # Build Payload
    data = {"data": {"auth_url": "https://example.com/oauth/google/callback/"}}

    # Initialize Serializer
    ser = OAuthLoginResponseSerializer(data=data)

    # Assert Invalid
    assert not ser.is_valid()

    # Assert Error Key
    assert "status_code" in ser.errors


# OAuth Login Response Serializer: Null Status Code Not Allowed
def test_oauth_login_response_serializer_null_status_code() -> None:
    """
    Null Status Code Should Fail Validation.
    """

    # Build Payload
    data = {"status_code": None, "data": {"auth_url": "https://example.com/oauth/google/callback/"}}

    # Initialize Serializer
    ser = OAuthLoginResponseSerializer(data=data)

    # Assert Invalid
    assert not ser.is_valid()

    # Assert Error Key
    assert "status_code" in ser.errors


# OAuth Login Response Serializer: Null Auth URL Not Allowed
def test_oauth_login_response_serializer_null_auth_url() -> None:
    """
    Null Auth URL Should Fail Validation.
    """

    # Build Payload
    data = {"status_code": status.HTTP_200_OK, "data": {"auth_url": None}}

    # Initialize Serializer
    ser = OAuthLoginResponseSerializer(data=data)

    # Assert Invalid
    assert not ser.is_valid()

    # Assert Error Key
    assert "data" in ser.errors or "auth_url" in ser.errors.get("data", {})


# OAuth Login Response Serializer: Blank Auth URL Not Allowed
def test_oauth_login_response_serializer_blank_auth_url() -> None:
    """
    Blank Auth URL Should Fail Validation.
    """

    # Build Payload
    data = {"status_code": status.HTTP_200_OK, "data": {"auth_url": ""}}

    # Initialize Serializer
    ser = OAuthLoginResponseSerializer(data=data)

    # Assert Invalid
    assert not ser.is_valid()

    # Assert Error Key
    assert "data" in ser.errors or "auth_url" in ser.errors.get("data", {})
