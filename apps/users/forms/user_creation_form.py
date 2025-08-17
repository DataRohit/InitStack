# Standard Library Imports
from typing import ClassVar

# Third Party Imports
from django import forms
from django.contrib.auth import forms as admin_forms
from django.contrib.auth import get_user_model

# Local Imports
from apps.users.models import User

# Get User Model
User: ClassVar[User] = get_user_model()


# User Creation Form Class
class UserCreationForm(admin_forms.UserCreationForm):
    """
    User Creation Form Class For Creating New Users.

    Attributes:
        error_messages (ClassVar[dict[str, str]]): Error Messages For Form Validation.

    Methods:
        clean_email() -> str: Clean Email Method To Validate Email Uniqueness.
        clean_username() -> str: Clean Username Method To Validate Username Uniqueness.
    """

    # Meta Class
    class Meta(admin_forms.UserCreationForm.Meta):
        """
        Meta Class For User Creation Form.

        Attributes:
            model (ClassVar[User]): User Model.
            fields (ClassVar[list[str]]): Form Fields.
        """

        # Set Model
        model: ClassVar[User] = User

        # Set Fields
        fields: ClassVar[list[str]] = ["first_name", "last_name", "username", "email"]

    # Error Messages
    error_messages: ClassVar[dict[str, str]] = {
        "duplicate_username": "A User With That Username Already Exists",
        "duplicate_email": "A User With That Email Already Exists",
        "password_mismatch": "The Two Password Fields Didn't Match",
    }

    # Clean Email Method
    def clean_email(self) -> str:
        """
        Clean Email Method To Validate Email Uniqueness And Format To Lowercase.

        Returns:
            str: Validated Email In Lowercase.

        Raises:
            forms.ValidationError: If Email Already Exists.
        """

        # Get Email From Cleaned Data
        email: str = self.cleaned_data["email"]

        # Convert Email To Lowercase
        email = email.lower().strip()

        # If Email Already Exists
        if User.objects.filter(email=email).exists():
            # Raise Validation Error
            raise forms.ValidationError(
                self.error_messages["duplicate_email"],
            ) from None

        # Return Email
        return email

    # Clean Username Method
    def clean_username(self) -> str:
        """
        Clean Username Method To Validate Username Uniqueness And Format To Lowercase.

        Returns:
            str: Validated Username In Lowercase.

        Raises:
            forms.ValidationError: If Username Already Exists.
        """

        # Get Username From Cleaned Data
        username: str = self.cleaned_data["username"]

        # Convert Username To Lowercase
        username = username.lower().strip()

        # If Username Already Exists
        if User.objects.filter(username=username).exists():
            # Raise Validation Error
            raise forms.ValidationError(
                self.error_messages["duplicate_username"],
            ) from None

        # Return Username
        return username

    # Clean First Name Method
    def clean_first_name(self) -> str:
        """
        Clean First Name Method To Format To Title Case.

        Returns:
            str: Validated First Name In Title Case.
        """

        # Get First Name From Cleaned Data
        first_name: str = self.cleaned_data["first_name"]

        # Convert First Name To Title Case & Return
        return first_name.title().strip()

    # Clean Last Name Method
    def clean_last_name(self) -> str:
        """
        Clean Last Name Method To Format To Title Case.

        Returns:
            str: Validated Last Name In Title Case.
        """

        # Get Last Name From Cleaned Data
        last_name: str = self.cleaned_data["last_name"]

        # Convert Last Name To Title Case & Return
        return last_name.title().strip()


# Exports
__all__: list[str] = ["UserCreationForm"]
