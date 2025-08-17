# Standard Library Imports
from typing import ClassVar

# Third Party Imports
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserChangeForm as BaseUserChangeForm

# Local Imports
from apps.users.models import User

# Get User Model
User: User = get_user_model()


# User Change Form Class
class UserChangeForm(BaseUserChangeForm):
    """
    User Change Form Class For Updating Existing Users.
    """

    # Meta Class
    class Meta(BaseUserChangeForm.Meta):
        """
        Meta Class For User Change Form.

        Attributes:
            model (ClassVar[User]): User Model.
            fields (ClassVar[list[str]]): Form Fields.
        """

        # Set Model
        model: ClassVar[User] = User

        # Set Fields
        fields: ClassVar[list[str]] = ["first_name", "last_name", "username", "email"]

    # Clean Email Method
    def clean_email(self) -> str:
        """
        Clean Email Method To Format To Lowercase.

        Returns:
            str: Validated Email In Lowercase.
        """

        # Get Email From Cleaned Data
        email: str = self.cleaned_data["email"]

        # Convert Email To Lowercase & Return
        return email.lower().strip()

    # Clean Username Method
    def clean_username(self) -> str:
        """
        Clean Username Method To Format To Lowercase.

        Returns:
            str: Validated Username In Lowercase.
        """

        # Get Username From Cleaned Data
        username: str = self.cleaned_data["username"]

        # Convert Username To Lowercase & Return
        return username.lower().strip()

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
__all__: list[str] = ["UserChangeForm"]
