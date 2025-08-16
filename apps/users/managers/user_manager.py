# Standard Library Imports
from typing import TYPE_CHECKING
from typing import Any

# Third Party Imports
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import UserManager as DjangoUserManager

# If Type Checking
if TYPE_CHECKING:
    # Local Imports
    from apps.users.models import User


# User Manager Class
class UserManager(DjangoUserManager["User"]):
    """
    Custom User Manager Class For User Model.

    Attributes:
        create_user() -> User: Create And Save A Regular User With The Given Email And Password.
        create_superuser() -> User: Create And Save A Superuser With The Given Email And Password.
    """

    # Create User Base Method
    def _create_user(
        self,
        email: str,
        password: str | None,
        **extra_fields: dict[str, Any],
    ) -> "User":
        """
        Create And Save A User With The Given Email And Password.

        Args:
            email (str): User Email Address.
            password (str | None): User Password.
            **extra_fields (dict[str, Any]): Additional Fields For User.

        Returns:
            User: Created User Instance.

        Raises:
            ValueError: If Email Is Not Provided.
        """
        # Check Email Provided
        if not email:
            # Set Error Message
            error_message: str = "Email Must Be Set"

            # Raise ValueError
            raise ValueError(error_message) from None

        # Normalize Email
        email = self.normalize_email(email)

        # Create User Instance
        user = self.model(email=email, **extra_fields)

        # Set Password
        user.password = make_password(password)

        # Save User
        user.save(using=self._db)

        # Return User
        return user

    # Create Regular User Method
    def create_user(
        self,
        email: str,
        password: str | None = None,
        **extra_fields: dict[str, Any],
    ) -> "User":
        """
        Create And Save A Regular User With The Given Email And Password.

        Args:
            email (str): User Email Address.
            password (str | None, optional): User Password. Defaults to None.
            **extra_fields (dict[str, Any]): Additional Fields For User.

        Returns:
            User: Created User Instance.
        """
        # Set Default User Flags
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)

        # Create User
        return self._create_user(email, password, **extra_fields)

    # Create Superuser Method
    def create_superuser(
        self,
        email: str,
        password: str | None = None,
        **extra_fields: dict[str, Any],
    ) -> "User":
        """
        Create And Save A Superuser With The Given Email And Password.

        Args:
            email (str): User Email Address.
            password (str | None, optional): User Password. Defaults to None.
            **extra_fields (dict[str, Any]): Additional Fields For User.

        Returns:
            User: Created Superuser Instance.

        Raises:
            ValueError: If is_staff Or is_superuser Is Not True.
        """

        # Set Default Superuser Flags
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        # Check Staff Flag
        if extra_fields.get("is_staff") is not True:
            # Set Error Message
            error_message: str = "Invalid is_staff Flag"

            # Raise ValueError
            raise ValueError(error_message) from None

        # Check Superuser Flag
        if extra_fields.get("is_superuser") is not True:
            # Set Error Message
            error_message: str = "Invalid is_superuser Flag"

            # Raise ValueError
            raise ValueError(error_message) from None

        # Create Superuser
        return self._create_user(email, password, **extra_fields)


# Exports
__all__: list[str] = ["UserManager"]
