# Third Party Imports
import pytest
from django.contrib.auth import forms as admin_forms

# Local Imports
from apps.users.forms.user_creation_form import UserCreationForm
from apps.users.models import User


# Test User Creation Form Class
@pytest.mark.django_db
class TestUserCreationForm:
    """
    Test User Creation Form Class.
    """

    # Test Form Initialization
    def test_form_initialization(self, user_creation_form: UserCreationForm) -> None:
        """
        Test Form Initialization.

        Args:
            user_creation_form (UserCreationForm): User Creation Form Instance.
        """

        # Assert Form Is Instance Of UserCreationForm
        assert isinstance(user_creation_form, UserCreationForm)

        # Assert Form Is Instance Of BaseUserCreationForm
        assert isinstance(user_creation_form, admin_forms.UserCreationForm)

    # Test Meta Class Model
    def test_meta_class_model(self) -> None:
        """
        Test Meta Class Model Is Set Correctly.
        """

        # Assert Model Is User
        assert UserCreationForm.Meta.model == User

    # Test Meta Class Fields
    def test_meta_class_fields(self) -> None:
        """
        Test Meta Class Fields Are Set Correctly.
        """

        # Expected Fields
        expected_fields = ["first_name", "last_name", "username", "email"]

        # Assert Fields Are Correct
        assert UserCreationForm.Meta.fields == expected_fields

    # Test Error Messages
    def test_error_messages(self) -> None:
        """
        Test Error Messages Are Set Correctly.
        """

        # Expected Error Messages
        expected_error_messages = {
            "duplicate_username": "A User With That Username Already Exists",
            "duplicate_email": "A User With That Email Already Exists",
            "password_mismatch": "The Two Password Fields Didn't Match",
        }

        # Assert Error Messages Are Correct
        assert UserCreationForm.error_messages == expected_error_messages

    # Test Form Validation With Valid Data
    def test_form_validation_with_valid_data(self, user_creation_form: UserCreationForm) -> None:
        """
        Test Form Validation With Valid Data.

        Args:
            user_creation_form (UserCreationForm): User Creation Form Instance.
        """

        # Assert Form Is Valid
        assert user_creation_form.is_valid()

    # Test Form Validation With Invalid Data
    @pytest.mark.parametrize(
        ("field", "value", "error_message"),
        [
            ("email", "", "This field is required."),
            ("username", "", "This field is required."),
            ("first_name", "", "This field is required."),
            ("last_name", "", "This field is required."),
            ("password1", "", "This field is required."),
            ("password2", "", "This field is required."),
        ],
    )
    def test_form_validation_with_invalid_data(
        self,
        user_creation_form_data: dict[str, str],
        field: str,
        value: str,
        error_message: str,
    ) -> None:
        """
        Test Form Validation With Invalid Data.

        Args:
            user_creation_form_data (dict[str, str]): User Creation Form Data.
            field (str): Field To Invalidate.
            value (str): Invalid Value.
            error_message (str): Expected Error Message.
        """

        # Update Form Data With Invalid Value
        user_creation_form_data[field] = value

        # Create Form
        form = UserCreationForm(data=user_creation_form_data)

        # Assert Form Is Not Valid
        assert not form.is_valid()

        # Assert Error Message
        assert error_message in form.errors[field]

    # Test Password Mismatch
    def test_password_mismatch(self, user_creation_form_data: dict[str, str]) -> None:
        """
        Test Password Mismatch Validation.

        Args:
            user_creation_form_data (dict[str, str]): User Creation Form Data.
        """

        # Update Form Data With Mismatched Passwords
        user_creation_form_data["password2"] = "DifferentP@ssw0rd"

        # Create Form
        form = UserCreationForm(data=user_creation_form_data)

        # Assert Form Is Not Valid
        assert not form.is_valid()

        # Assert Error Message
        assert UserCreationForm.error_messages["password_mismatch"] in form.errors["password2"]

    # Test Clean Email Method
    def test_clean_email_method(self, user_creation_form: UserCreationForm) -> None:
        """
        Test Clean Email Method.

        Args:
            user_creation_form (UserCreationForm): User Creation Form Instance.
        """

        # Validate Form
        assert user_creation_form.is_valid()

        # Get Cleaned Email
        cleaned_email = user_creation_form.cleaned_data["email"]

        # Assert Email Is Lowercase
        assert cleaned_email == "john.doe@example.com"

    # Test Clean Email Method With Mixed Case
    def test_clean_email_method_with_mixed_case(self, mixed_case_form_data: dict[str, str]) -> None:
        """
        Test Clean Email Method With Mixed Case.

        Args:
            mixed_case_form_data (dict[str, str]): Mixed Case Form Data.
        """

        # Add Password Fields
        mixed_case_form_data.update(
            {
                "password1": "StrongP@ssw0rd",
                "password2": "StrongP@ssw0rd",
            },
        )

        # Create Form
        form = UserCreationForm(data=mixed_case_form_data)

        # Validate Form
        assert form.is_valid()

        # Get Cleaned Email
        cleaned_email = form.cleaned_data["email"]

        # Assert Email Is Lowercase
        assert cleaned_email == "john.doe@example.com"

    # Test Clean Username Method
    def test_clean_username_method(self, user_creation_form: UserCreationForm) -> None:
        """
        Test Clean Username Method.

        Args:
            user_creation_form (UserCreationForm): User Creation Form Instance.
        """

        # Validate Form
        assert user_creation_form.is_valid()

        # Get Cleaned Username
        cleaned_username = user_creation_form.cleaned_data["username"]

        # Assert Username Is Lowercase
        assert cleaned_username == "johndoe"

    # Test Clean Username Method With Mixed Case
    def test_clean_username_method_with_mixed_case(self, mixed_case_form_data: dict[str, str]) -> None:
        """
        Test Clean Username Method With Mixed Case.

        Args:
            mixed_case_form_data (dict[str, str]): Mixed Case Form Data.
        """

        # Add Password Fields
        mixed_case_form_data.update(
            {
                "password1": "StrongP@ssw0rd",
                "password2": "StrongP@ssw0rd",
            },
        )

        # Create Form
        form = UserCreationForm(data=mixed_case_form_data)

        # Validate Form
        assert form.is_valid()

        # Get Cleaned Username
        cleaned_username = form.cleaned_data["username"]

        # Assert Username Is Lowercase
        assert cleaned_username == "johndoe"

    # Test Clean First Name Method
    def test_clean_first_name_method(self, user_creation_form: UserCreationForm) -> None:
        """
        Test Clean First Name Method.

        Args:
            user_creation_form (UserCreationForm): User Creation Form Instance.
        """

        # Validate Form
        assert user_creation_form.is_valid()

        # Get Cleaned First Name
        cleaned_first_name = user_creation_form.cleaned_data["first_name"]

        # Assert First Name Is Title Case
        assert cleaned_first_name == "John"

    # Test Clean First Name Method With Mixed Case
    def test_clean_first_name_method_with_mixed_case(self, mixed_case_form_data: dict[str, str]) -> None:
        """
        Test Clean First Name Method With Mixed Case.

        Args:
            mixed_case_form_data (dict[str, str]): Mixed Case Form Data.
        """

        # Add Password Fields
        mixed_case_form_data.update(
            {
                "password1": "StrongP@ssw0rd",
                "password2": "StrongP@ssw0rd",
            },
        )

        # Create Form
        form = UserCreationForm(data=mixed_case_form_data)

        # Validate Form
        assert form.is_valid()

        # Get Cleaned First Name
        cleaned_first_name = form.cleaned_data["first_name"]

        # Assert First Name Is Title Case
        assert cleaned_first_name == "John"

    # Test Clean Last Name Method
    def test_clean_last_name_method(self, user_creation_form: UserCreationForm) -> None:
        """
        Test Clean Last Name Method.

        Args:
            user_creation_form (UserCreationForm): User Creation Form Instance.
        """

        # Validate Form
        assert user_creation_form.is_valid()

        # Get Cleaned Last Name
        cleaned_last_name = user_creation_form.cleaned_data["last_name"]

        # Assert Last Name Is Title Case
        assert cleaned_last_name == "Doe"

    # Test Clean Last Name Method With Mixed Case
    def test_clean_last_name_method_with_mixed_case(self, mixed_case_form_data: dict[str, str]) -> None:
        """
        Test Clean Last Name Method With Mixed Case.

        Args:
            mixed_case_form_data (dict[str, str]): Mixed Case Form Data.
        """

        # Add Password Fields
        mixed_case_form_data.update(
            {
                "password1": "StrongP@ssw0rd",
                "password2": "StrongP@ssw0rd",
            },
        )

        # Create Form
        form = UserCreationForm(data=mixed_case_form_data)

        # Validate Form
        assert form.is_valid()

        # Get Cleaned Last Name
        cleaned_last_name = form.cleaned_data["last_name"]

        # Assert Last Name Is Title Case
        assert cleaned_last_name == "Doe"

    # Test Form With Whitespace In Fields
    def test_form_with_whitespace_in_fields(self, user_creation_form_data: dict[str, str]) -> None:
        """
        Test Form With Whitespace In Fields.

        Args:
            user_creation_form_data (dict[str, str]): User Creation Form Data.
        """

        # Update Form Data With Whitespace
        user_creation_form_data.update(
            {
                "first_name": "  John  ",
                "last_name": "  Doe  ",
                "username": "  johndoe  ",
                "email": "  john.doe@example.com  ",
            },
        )

        # Create Form
        form = UserCreationForm(data=user_creation_form_data)

        # Validate Form
        assert form.is_valid()

        # Assert Whitespace Is Stripped
        assert form.cleaned_data["first_name"] == "John"
        assert form.cleaned_data["last_name"] == "Doe"
        assert form.cleaned_data["username"] == "johndoe"
        assert form.cleaned_data["email"] == "john.doe@example.com"

    # Test Form With Multi-word Names
    def test_form_with_multi_word_names(self, user_creation_form_data: dict[str, str]) -> None:
        """
        Test Form With Multi-word Names Should Fail Validation.

        Args:
            user_creation_form_data (dict[str, str]): User Creation Form Data.
        """

        # Update Form Data With Multi-word Names
        user_creation_form_data.update(
            {
                "first_name": "john michael",
                "last_name": "doe smith",
            },
        )

        # Create Form
        form = UserCreationForm(data=user_creation_form_data)

        # Assert Form Is Not Valid (Multi-word Names Are Not Allowed)
        assert not form.is_valid()

    # Test Duplicate Email Validation
    def test_duplicate_email_validation(self, user_instance: User, user_creation_form_data: dict[str, str]) -> None:
        """
        Test Duplicate Email Validation.

        Args:
            user_instance (User): Existing User Instance.
            user_creation_form_data (dict[str, str]): User Creation Form Data.
        """

        # Update Form Data With Existing Email
        user_creation_form_data["email"] = user_instance.email

        # Create Form
        form = UserCreationForm(data=user_creation_form_data)

        # Assert Form Is Not Valid
        assert not form.is_valid()

        # Assert Error Message
        assert UserCreationForm.error_messages["duplicate_email"] in form.errors["email"]

    # Test Duplicate Username Validation
    def test_duplicate_username_validation(self, user_instance: User, user_creation_form_data: dict[str, str]) -> None:
        """
        Test Duplicate Username Validation.

        Args:
            user_instance (User): Existing User Instance.
            user_creation_form_data (dict[str, str]): User Creation Form Data.
        """

        # Update Form Data With Existing Username
        user_creation_form_data["username"] = user_instance.username

        # Create Form
        form = UserCreationForm(data=user_creation_form_data)

        # Assert Form Is Not Valid
        assert not form.is_valid()

        # Assert Error Message
        assert UserCreationForm.error_messages["duplicate_username"] in form.errors["username"]

    # Test Case Insensitive Duplicate Email Validation
    def test_case_insensitive_duplicate_email_validation(
        self,
        user_instance: User,
        user_creation_form_data: dict[str, str],
    ) -> None:
        """
        Test Case Insensitive Duplicate Email Validation.

        Args:
            user_instance (User): Existing User Instance.
            user_creation_form_data (dict[str, str]): User Creation Form Data.
        """

        # Update Form Data With Existing Email In Different Case
        user_creation_form_data["email"] = user_instance.email.upper()

        # Create Form
        form = UserCreationForm(data=user_creation_form_data)

        # Assert Form Is Not Valid
        assert not form.is_valid()

        # Assert Error Message
        assert UserCreationForm.error_messages["duplicate_email"] in form.errors["email"]

    # Test Case Insensitive Duplicate Username Validation
    def test_case_insensitive_duplicate_username_validation(
        self,
        user_instance: User,
        user_creation_form_data: dict[str, str],
    ) -> None:
        """
        Test Case Insensitive Duplicate Username Validation.

        Args:
            user_instance (User): Existing User Instance.
            user_creation_form_data (dict[str, str]): User Creation Form Data.
        """

        # Update Form Data With Existing Username In Different Case
        user_creation_form_data["username"] = user_instance.username.upper()

        # Create Form
        form = UserCreationForm(data=user_creation_form_data)

        # Assert Form Is Not Valid
        assert not form.is_valid()

        # Assert Error Message
        assert UserCreationForm.error_messages["duplicate_username"] in form.errors["username"]
