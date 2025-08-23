# Local Imports
from apps.users.serializers.base_serializer import UserDetailSerializer


# Test Valid Serialization
def test_user_detail_serializer_with_valid_data_is_valid() -> None:
    """
    Verify Serializer Accepts Complete Valid Payload.
    """

    # Inputs
    data: dict[str, object] = {
        "id": "123e4567-e89b-12d3-a456-426614174000",
        "username": "john_doe",
        "email": "john.doe@example.com",
        "first_name": "John",
        "last_name": "Doe",
        "full_name": "John Doe",
        "is_active": True,
        "is_staff": False,
        "is_superuser": False,
        "date_joined": "2025-08-16T19:04:06.602446+05:30",
        "last_login": "2025-08-16T19:04:08.602446+05:30",
    }

    # Create Serializer
    serializer: UserDetailSerializer = UserDetailSerializer(data=data)

    # Validate
    assert serializer.is_valid(), serializer.errors

    # Assert Representation
    assert serializer.validated_data["username"] == data["username"]
    assert serializer.validated_data["email"] == data["email"]


# Test Missing Required Field
def test_user_detail_serializer_missing_email_is_invalid() -> None:
    """
    Verify Missing Required Email Raises Error Message.
    """

    # Inputs
    data: dict[str, object] = {
        "id": "123e4567-e89b-12d3-a456-426614174000",
        "username": "john_doe",
        # "email" missing
        "first_name": "John",
        "last_name": "Doe",
        "full_name": "John Doe",
        "is_active": True,
        "is_staff": False,
        "is_superuser": False,
        "date_joined": "2025-08-16T19:04:06.602446+05:30",
        "last_login": "2025-08-16T19:04:08.602446+05:30",
    }

    # Create Serializer
    serializer: UserDetailSerializer = UserDetailSerializer(data=data)

    # Validate
    assert not serializer.is_valid()

    # Assert Error Message
    assert "email" in serializer.errors
    assert str(serializer.errors["email"][0]) == "User Email Is Required"


# Test Nullable Field Allows Null
def test_user_detail_serializer_last_login_null_is_valid() -> None:
    """
    Verify Optional Last Login Accepts Null.
    """

    # Inputs
    data: dict[str, object] = {
        "id": "123e4567-e89b-12d3-a456-426614174000",
        "username": "john_doe",
        "email": "john.doe@example.com",
        "first_name": "John",
        "last_name": "Doe",
        "full_name": "John Doe",
        "is_active": True,
        "is_staff": False,
        "is_superuser": False,
        "date_joined": "2025-08-16T19:04:06.602446+05:30",
        "last_login": None,
    }

    # Create Serializer
    serializer: UserDetailSerializer = UserDetailSerializer(data=data)

    # Validate
    assert serializer.is_valid(), serializer.errors

    # Assert Null Preserved
    assert serializer.validated_data["last_login"] is None


# Test Null For Non-Nullable Field
def test_user_detail_serializer_first_name_null_is_invalid() -> None:
    """
    Verify Non-Nullable First Name Rejects Null With Message.
    """

    # Inputs
    data: dict[str, object] = {
        "id": "123e4567-e89b-12d3-a456-426614174000",
        "username": "john_doe",
        "email": "john.doe@example.com",
        "first_name": None,
        "last_name": "Doe",
        "full_name": "John Doe",
        "is_active": True,
        "is_staff": False,
        "is_superuser": False,
        "date_joined": "2025-08-16T19:04:06.602446+05:30",
        "last_login": None,
    }

    # Create Serializer
    serializer: UserDetailSerializer = UserDetailSerializer(data=data)

    # Validate
    assert not serializer.is_valid()

    # Assert Error Message
    assert "first_name" in serializer.errors
    assert str(serializer.errors["first_name"][0]) == "User First Name Cannot Be Null"


# Test Invalid UUID
def test_user_detail_serializer_invalid_uuid_is_invalid() -> None:
    """
    Verify Invalid UUID For Id Raises Error.
    """

    # Inputs
    data: dict[str, object] = {
        "id": "not-a-uuid",
        "username": "john_doe",
        "email": "john.doe@example.com",
        "first_name": "John",
        "last_name": "Doe",
        "full_name": "John Doe",
        "is_active": True,
        "is_staff": False,
        "is_superuser": False,
        "date_joined": "2025-08-16T19:04:06.602446+05:30",
        "last_login": None,
    }

    # Create Serializer
    serializer: UserDetailSerializer = UserDetailSerializer(data=data)

    # Validate
    assert not serializer.is_valid()

    # Assert Error Present
    assert "id" in serializer.errors
