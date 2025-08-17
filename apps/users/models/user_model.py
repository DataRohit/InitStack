# Standard Library Imports
from typing import Any
from typing import ClassVar

# Third Party Imports
from django.contrib.auth.models import AbstractUser
from django.core.validators import EmailValidator
from django.core.validators import MaxLengthValidator
from django.core.validators import RegexValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

# Local Imports
from apps.common.models import TimeStampedModel
from apps.users.managers import UserManager


# User Model Class
class User(AbstractUser, TimeStampedModel):
    """
    Custom User Model Class That Extends Django's AbstractUser.

    Attributes:
        username (models.CharField): User's Username (Unique).
        email (models.CharField): User's Email Address (Unique).
        first_name (models.CharField): User's First Name.
        last_name (models.CharField): User's Last Name.

        EMAIL_FIELD (ClassVar[str]): Field Name For Email.
        USERNAME_FIELD (ClassVar[str]): Field Used For Authentication.
        REQUIRED_FIELDS (ClassVar[list[str]]): Required Fields For User Creation.

        objects (ClassVar[UserManager]): Custom User Manager.

    Methods:
        full_name() -> str: Returns User's Full Name.
    """

    # Username Field
    username: models.CharField = models.CharField(
        verbose_name=_("Username"),
        unique=True,
        db_index=True,
        blank=False,
        null=False,
        validators=[
            RegexValidator(
                regex=r"^[A-Za-z0-9]+$",
                message=_("Username Must Contain Only Alphanumeric Characters With No Spaces"),
                code="invalid_username",
            ),
            MaxLengthValidator(
                limit_value=60,
                message=_("Username Must Not Exceed 60 Characters"),
            ),
        ],
    )

    # Email Field
    email: models.CharField = models.CharField(
        verbose_name=_("Email Address"),
        unique=True,
        db_index=True,
        blank=False,
        null=False,
        validators=[
            EmailValidator(
                message=_("Invalid Email Address"),
                code="invalid_email",
            ),
        ],
    )

    # First Name Field
    first_name: models.CharField = models.CharField(
        verbose_name=_("First Name"),
        blank=False,
        null=False,
        validators=[
            RegexValidator(
                regex=r"^[A-Za-z]+$",
                message=_("First Name Must Contain Only Letters With No Spaces"),
                code="invalid_first_name",
            ),
            MaxLengthValidator(
                limit_value=60,
                message=_("First Name Must Not Exceed 60 Characters"),
            ),
        ],
    )

    # Last Name Field
    last_name: models.CharField = models.CharField(
        verbose_name=_("Last Name"),
        blank=False,
        null=False,
        validators=[
            RegexValidator(
                regex=r"^[A-Za-z]+$",
                message=_("Last Name Must Contain Only Letters With No Spaces"),
                code="invalid_last_name",
            ),
            MaxLengthValidator(
                limit_value=60,
                message=_("Last Name Must Not Exceed 60 Characters"),
            ),
        ],
    )

    # Password Field
    password: models.CharField = models.CharField(
        verbose_name=_("Password"),
        blank=False,
        null=False,
    )

    # Email Field Configuration
    EMAIL_FIELD: ClassVar[str] = "email"

    # Authentication Field Configuration
    USERNAME_FIELD: ClassVar[str] = "email"

    # Required Fields For User Creation
    REQUIRED_FIELDS: ClassVar[list[str]] = ["username", "first_name", "last_name"]

    # User Manager
    objects: ClassVar[UserManager] = UserManager()

    # Meta Class
    class Meta:
        """
        Meta Class For User Model.

        Attributes:
            verbose_name (ClassVar[str]): Singular Name For The Model.
            verbose_name_plural (ClassVar[str]): Plural Name For The Model.
            ordering (ClassVar[list[str]]): Default Ordering For The Model.
            db_table (ClassVar[str]): Database Table Name.
        """

        # Singular Name
        verbose_name: ClassVar[str] = _("User")

        # Plural Name
        verbose_name_plural: ClassVar[str] = _("Users")

        # Default Ordering
        ordering: ClassVar[list[str]] = ["-date_joined"]

        # Database Table
        db_table: ClassVar[str] = "users_user"

    # Full Name Property
    @property
    def full_name(self) -> str:
        """
        Get User's Full Name.

        Returns:
            str: Formatted Full Name.
        """

        # Format Full Name
        full_name: str = f"{self.first_name} {self.last_name}".title()

        # Return Stripped Name
        return full_name.strip()

    # Save Method Override
    def save(self, *args: Any, **kwargs: Any) -> None:
        """
        Override Save Method To Enforce Case Formatting Rules.

        Args:
            *args (Any): Variable Length Argument List.
            **kwargs (Any): Arbitrary Keyword Arguments.

        Returns:
            None
        """

        # If First Name Is Not Empty
        if self.first_name:
            # Apply Title Case
            self.first_name: str = self.first_name.title().strip()

        # If Last Name Is Not Empty
        if self.last_name:
            # Apply Title Case
            self.last_name: str = self.last_name.title().strip()

        # If Username Is Not Empty
        if self.username:
            # Apply Lowercase
            self.username: str = self.username.lower().strip()

        # If Email Is Not Empty
        if self.email:
            # Apply Lowercase
            self.email: str = self.email.lower().strip()

        # Call Parent Save Method
        super().save(*args, **kwargs)


# Exports
__all__: list[str] = ["User"]
