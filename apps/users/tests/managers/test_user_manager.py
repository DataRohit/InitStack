# Standard Library Imports
import datetime
from typing import Any

# Third Party Imports
import pytest
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import check_password
from django.contrib.auth.models import UserManager as DjangoUserManager
from django.utils import timezone

# Local Imports
from apps.users.managers.user_manager import UserManager

# Get User Model
User = get_user_model()


# Test User Manager Class
@pytest.mark.django_db
class TestUserManager:
    """
    Test User Manager Class.
    """

    # Test Manager Initialization
    def test_manager_initialization(self, user_manager: UserManager) -> None:
        """
        Test Manager Initialization.

        Args:
            user_manager (UserManager): User Manager Instance.
        """

        # Assert Manager Is Instance Of UserManager
        assert isinstance(user_manager, UserManager)

        # Assert Manager Is Instance Of DjangoUserManager
        assert isinstance(user_manager, DjangoUserManager)

    # Test Create User Method
    def test_create_user_method(self, user_data: dict[str, Any]) -> None:
        """
        Test Create User Method.

        Args:
            user_data (dict[str, Any]): User Data.
        """

        # Create User
        user = User.objects.create_user(
            email=user_data["email"],
            password=user_data["password"],
            first_name=user_data["first_name"],
            last_name=user_data["last_name"],
            username=user_data["username"],
        )

        # Assert User Is Instance Of User
        assert isinstance(user, User)

        # Assert User Email
        assert user.email == user_data["email"]

        # Assert User First Name
        assert user.first_name == user_data["first_name"]

        # Assert User Last Name
        assert user.last_name == user_data["last_name"]

        # Assert User Username
        assert user.username == user_data["username"]

        # Assert User Password Is Hashed
        assert check_password(user_data["password"], user.password)

        # Assert User Is Not Staff
        assert not user.is_staff

        # Assert User Is Not Superuser
        assert not user.is_superuser

    # Test Create User Method With Minimal Data
    def test_create_user_method_with_minimal_data(self) -> None:
        """
        Test Create User Method With Minimal Data.
        """

        # Create User
        user = User.objects.create_user(
            email="minimal@example.com",
        )

        # Assert User Is Instance Of User
        assert isinstance(user, User)

        # Assert User Email
        assert user.email == "minimal@example.com"

        # Assert User Password Is Not Set
        assert not user.has_usable_password()

        # Assert User Is Not Staff
        assert not user.is_staff

        # Assert User Is Not Superuser
        assert not user.is_superuser

    # Test Create User Method With Empty Email
    def test_create_user_method_with_empty_email(self) -> None:
        """
        Test Create User Method With Empty Email.
        """

        # Assert ValueError Is Raised
        with pytest.raises(ValueError, match="Email Must Be Set"):
            # Create User
            User.objects.create_user(
                email="",
                password="password",
            )

    # Test Create User Method With None Email
    def test_create_user_method_with_none_email(self) -> None:
        """
        Test Create User Method With None Email.
        """

        # Assert ValueError Is Raised
        with pytest.raises(ValueError, match="Email Must Be Set"):
            # Create User
            User.objects.create_user(
                email=None,
                password="password",
            )

    # Test Create User Method With Custom Flags
    def test_create_user_method_with_custom_flags(self) -> None:
        """
        Test Create User Method With Custom Flags.
        """

        # Create User
        user = User.objects.create_user(
            email="custom@example.com",
            password="password",
            is_staff=True,
        )

        # Assert User Is Staff
        assert user.is_staff

        # Assert User Is Not Superuser
        assert not user.is_superuser

    # Test Create Superuser Method
    def test_create_superuser_method(self, superuser_data: dict[str, Any]) -> None:
        """
        Test Create Superuser Method.

        Args:
            superuser_data (dict[str, Any]): Superuser Data.
        """

        # Create Superuser
        superuser = User.objects.create_superuser(
            email=superuser_data["email"],
            password=superuser_data["password"],
            first_name=superuser_data["first_name"],
            last_name=superuser_data["last_name"],
            username=superuser_data["username"],
        )

        # Assert Superuser Is Instance Of User
        assert isinstance(superuser, User)

        # Assert Superuser Email
        assert superuser.email == superuser_data["email"]

        # Assert Superuser First Name
        assert superuser.first_name == superuser_data["first_name"]

        # Assert Superuser Last Name
        assert superuser.last_name == superuser_data["last_name"]

        # Assert Superuser Username
        assert superuser.username == superuser_data["username"]

        # Assert Superuser Password Is Hashed
        assert check_password(superuser_data["password"], superuser.password)

        # Assert Superuser Is Staff
        assert superuser.is_staff

        # Assert Superuser Is Superuser
        assert superuser.is_superuser

    # Test Create Superuser Method With Minimal Data
    def test_create_superuser_method_with_minimal_data(self) -> None:
        """
        Test Create Superuser Method With Minimal Data.
        """

        # Create Superuser
        superuser = User.objects.create_superuser(
            email="superminimal@example.com",
        )

        # Assert Superuser Is Instance Of User
        assert isinstance(superuser, User)

        # Assert Superuser Email
        assert superuser.email == "superminimal@example.com"

        # Assert Superuser Password Is Not Set
        assert not superuser.has_usable_password()

        # Assert Superuser Is Staff
        assert superuser.is_staff

        # Assert Superuser Is Superuser
        assert superuser.is_superuser

    # Test Create Superuser Method With Empty Email
    def test_create_superuser_method_with_empty_email(self) -> None:
        """
        Test Create Superuser Method With Empty Email.
        """

        # Assert ValueError Is Raised
        with pytest.raises(ValueError, match="Email Must Be Set"):
            # Create Superuser
            User.objects.create_superuser(
                email="",
                password="password",
            )

    # Test Create Superuser Method With None Email
    def test_create_superuser_method_with_none_email(self) -> None:
        """
        Test Create Superuser Method With None Email.
        """

        # Assert ValueError Is Raised
        with pytest.raises(ValueError, match="Email Must Be Set"):
            # Create Superuser
            User.objects.create_superuser(
                email=None,
                password="password",
            )

    # Test Create Superuser Method With Invalid Staff Flag
    def test_create_superuser_method_with_invalid_staff_flag(self) -> None:
        """
        Test Create Superuser Method With Invalid Staff Flag.
        """

        # Assert ValueError Is Raised
        with pytest.raises(ValueError, match="Invalid is_staff Flag"):
            # Create Superuser
            User.objects.create_superuser(
                email="invalid@example.com",
                password="password",
                is_staff=False,
            )

    # Test Create Superuser Method With Invalid Superuser Flag
    def test_create_superuser_method_with_invalid_superuser_flag(self) -> None:
        """
        Test Create Superuser Method With Invalid Superuser Flag.
        """

        # Assert ValueError Is Raised
        with pytest.raises(ValueError, match="Invalid is_superuser Flag"):
            # Create Superuser
            User.objects.create_superuser(
                email="invalid@example.com",
                password="password",
                is_superuser=False,
            )

    # Test Email Normalization
    def test_email_normalization(self) -> None:
        """
        Test Email Normalization.
        """

        # Create User With Mixed Case Email
        user = User.objects.create_user(
            email="MixedCase@Example.COM",
            password="password",
        )

        # Assert Email Is Normalized To Lowercase
        assert user.email == "mixedcase@example.com"

    # Test Create User With Extra Fields
    def test_create_user_with_extra_fields(self) -> None:
        """
        Test Create User With Extra Fields.
        """

        # Create User With Extra Fields
        user = User.objects.create_user(
            email="extra@example.com",
            password="password",
            is_active=False,
            date_joined=timezone.make_aware(datetime.datetime(2023, 1, 1)),
        )

        # Assert User Is Instance Of User
        assert isinstance(user, User)

        # Assert User Email
        assert user.email == "extra@example.com"

        # Assert User Is Not Active
        assert not user.is_active

    # Test Create Superuser With Extra Fields
    def test_create_superuser_with_extra_fields(self) -> None:
        """
        Test Create Superuser With Extra Fields.
        """

        # Create Superuser With Extra Fields
        superuser = User.objects.create_superuser(
            email="superextra@example.com",
            password="password",
            is_active=False,
            date_joined=timezone.make_aware(datetime.datetime(2023, 1, 1)),
        )

        # Assert Superuser Is Instance Of User
        assert isinstance(superuser, User)

        # Assert Superuser Email
        assert superuser.email == "superextra@example.com"

        # Assert Superuser Is Not Active
        assert not superuser.is_active

    # Test Create User With Different DB
    def test_create_user_with_different_db(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """
        Test Create User With Different DB.

        Args:
            monkeypatch (pytest.MonkeyPatch): Pytest MonkeyPatch Fixture.
        """

        # Mock Save Method To Track DB Used
        db_used = [None]

        # Original _create_user Method
        original_create_user = UserManager._create_user

        # Define Mock _create_user Method
        def mock_create_user(self, email: str, password: str | None, **extra_fields: dict[str, Any]) -> User:
            """
            Mock _create_user Method.

            Args:
                self: UserManager Instance.
                email (str): User Email Address.
                password (str | None): User Password.
                **extra_fields (dict[str, Any]): Additional Fields For User.

            Returns:
                User: Created User Instance.
            """

            # Check If Using Is In Extra Fields
            if "using" in extra_fields:
                # Store DB Used
                db_used[0] = extra_fields.pop("using")

            # Call Original _create_user Method
            return original_create_user(self, email, password, **extra_fields)

        # Apply Monkeypatch
        monkeypatch.setattr(UserManager, "_create_user", mock_create_user)

        # Create User With Different DB
        User.objects.create_user(
            email="dbtest@example.com",
            password="password",
            using="other_db",
        )

        # Assert DB Used
        assert db_used[0] == "other_db"
