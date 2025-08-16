# Third Party Imports
import pytest
from django.contrib.auth.forms import UserChangeForm as BaseUserChangeForm

# Local Imports
from apps.users.forms.user_change_form import UserChangeForm
from apps.users.models import User


# Test User Change Form Class
@pytest.mark.django_db
class TestUserChangeForm:
    """
    Test User Change Form Class.
    """

    # Test Form Initialization
    def test_form_initialization(self, user_change_form: UserChangeForm) -> None:
        """
        Test Form Initialization.

        Args:
            user_change_form (UserChangeForm): User Change Form Instance.
        """

        # Assert Form Is Instance Of UserChangeForm
        assert isinstance(user_change_form, UserChangeForm)

        # Assert Form Is Instance Of BaseUserChangeForm
        assert isinstance(user_change_form, BaseUserChangeForm)

    # Test Meta Class Model
    def test_meta_class_model(self) -> None:
        """
        Test Meta Class Model Is Set Correctly.
        """

        # Assert Model Is User
        assert UserChangeForm.Meta.model == User

    # Test Meta Class Fields
    def test_meta_class_fields(self) -> None:
        """
        Test Meta Class Fields Are Set Correctly.
        """

        # Expected Fields
        expected_fields = ["first_name", "last_name", "username", "email"]

        # Assert Fields Are Correct
        assert UserChangeForm.Meta.fields == expected_fields

    # Test Form Validation With Valid Data
    def test_form_validation_with_valid_data(self, user_change_form: UserChangeForm) -> None:
        """
        Test Form Validation With Valid Data.

        Args:
            user_change_form (UserChangeForm): User Change Form Instance.
        """

        # Assert Form Is Valid
        assert user_change_form.is_valid()

    # Test Form Validation With Invalid Data
    @pytest.mark.parametrize(
        ("field", "value", "error_message"),
        [
            ("email", "", "This field is required."),
            ("username", "", "This field is required."),
            ("first_name", "", "This field is required."),
            ("last_name", "", "This field is required."),
        ],
    )
    def test_form_validation_with_invalid_data(
        self,
        user_form_data: dict[str, str],
        field: str,
        value: str,
        error_message: str,
    ) -> None:
        """
        Test Form Validation With Invalid Data.

        Args:
            user_form_data (dict[str, str]): User Form Data.
            field (str): Field To Invalidate.
            value (str): Invalid Value.
            error_message (str): Expected Error Message.
        """

        # Update Form Data With Invalid Value
        user_form_data[field] = value

        # Create Form
        form = UserChangeForm(data=user_form_data)

        # Assert Form Is Not Valid
        assert not form.is_valid()

        # Assert Error Message
        assert error_message in form.errors[field]

    # Test Clean Email Method
    def test_clean_email_method(self, user_change_form: UserChangeForm) -> None:
        """
        Test Clean Email Method.

        Args:
            user_change_form (UserChangeForm): User Change Form Instance.
        """

        # Validate Form
        assert user_change_form.is_valid()

        # Get Cleaned Email
        cleaned_email = user_change_form.cleaned_data["email"]

        # Assert Email Is Lowercase
        assert cleaned_email == "john.doe@example.com"

    # Test Clean Email Method With Mixed Case
    def test_clean_email_method_with_mixed_case(self, mixed_case_form_data: dict[str, str]) -> None:
        """
        Test Clean Email Method With Mixed Case.

        Args:
            mixed_case_form_data (dict[str, str]): Mixed Case Form Data.
        """

        # Create Form
        form = UserChangeForm(data=mixed_case_form_data)

        # Validate Form
        assert form.is_valid()

        # Get Cleaned Email
        cleaned_email = form.cleaned_data["email"]

        # Assert Email Is Lowercase
        assert cleaned_email == "john.doe@example.com"

    # Test Clean Username Method
    def test_clean_username_method(self, user_change_form: UserChangeForm) -> None:
        """
        Test Clean Username Method.

        Args:
            user_change_form (UserChangeForm): User Change Form Instance.
        """

        # Validate Form
        assert user_change_form.is_valid()

        # Get Cleaned Username
        cleaned_username = user_change_form.cleaned_data["username"]

        # Assert Username Is Lowercase
        assert cleaned_username == "johndoe"

    # Test Clean Username Method With Mixed Case
    def test_clean_username_method_with_mixed_case(self, mixed_case_form_data: dict[str, str]) -> None:
        """
        Test Clean Username Method With Mixed Case.

        Args:
            mixed_case_form_data (dict[str, str]): Mixed Case Form Data.
        """

        # Create Form
        form = UserChangeForm(data=mixed_case_form_data)

        # Validate Form
        assert form.is_valid()

        # Get Cleaned Username
        cleaned_username = form.cleaned_data["username"]

        # Assert Username Is Lowercase
        assert cleaned_username == "johndoe"

    # Test Clean First Name Method
    def test_clean_first_name_method(self, user_change_form: UserChangeForm) -> None:
        """
        Test Clean First Name Method.

        Args:
            user_change_form (UserChangeForm): User Change Form Instance.
        """

        # Validate Form
        assert user_change_form.is_valid()

        # Get Cleaned First Name
        cleaned_first_name = user_change_form.cleaned_data["first_name"]

        # Assert First Name Is Title Case
        assert cleaned_first_name == "John"

    # Test Clean First Name Method With Mixed Case
    def test_clean_first_name_method_with_mixed_case(self, mixed_case_form_data: dict[str, str]) -> None:
        """
        Test Clean First Name Method With Mixed Case.

        Args:
            mixed_case_form_data (dict[str, str]): Mixed Case Form Data.
        """

        # Create Form
        form = UserChangeForm(data=mixed_case_form_data)

        # Validate Form
        assert form.is_valid()

        # Get Cleaned First Name
        cleaned_first_name = form.cleaned_data["first_name"]

        # Assert First Name Is Title Case
        assert cleaned_first_name == "John"

    # Test Clean Last Name Method
    def test_clean_last_name_method(self, user_change_form: UserChangeForm) -> None:
        """
        Test Clean Last Name Method.

        Args:
            user_change_form (UserChangeForm): User Change Form Instance.
        """

        # Validate Form
        assert user_change_form.is_valid()

        # Get Cleaned Last Name
        cleaned_last_name = user_change_form.cleaned_data["last_name"]

        # Assert Last Name Is Title Case
        assert cleaned_last_name == "Doe"

    # Test Clean Last Name Method With Mixed Case
    def test_clean_last_name_method_with_mixed_case(self, mixed_case_form_data: dict[str, str]) -> None:
        """
        Test Clean Last Name Method With Mixed Case.

        Args:
            mixed_case_form_data (dict[str, str]): Mixed Case Form Data.
        """

        # Create Form
        form = UserChangeForm(data=mixed_case_form_data)

        # Validate Form
        assert form.is_valid()

        # Get Cleaned Last Name
        cleaned_last_name = form.cleaned_data["last_name"]

        # Assert Last Name Is Title Case
        assert cleaned_last_name == "Doe"

    # Test Form With Existing User Instance
    def test_form_with_existing_user_instance(self, user_change_form_with_instance: UserChangeForm) -> None:
        """
        Test Form With Existing User Instance.

        Args:
            user_change_form_with_instance (UserChangeForm): User Change Form With Instance.
        """

        # Assert Form Has Instance
        assert user_change_form_with_instance.instance is not None

        # Assert Instance Username
        assert user_change_form_with_instance.instance.username == "janesmith"

    # Test Form With Whitespace In Fields
    def test_form_with_whitespace_in_fields(self, user_form_data: dict[str, str]) -> None:
        """
        Test Form With Whitespace In Fields.

        Args:
            user_form_data (dict[str, str]): User Form Data.
        """

        # Update Form Data With Whitespace
        user_form_data.update(
            {
                "first_name": "  John  ",
                "last_name": "  Doe  ",
                "username": "  johndoe  ",
                "email": "  john.doe@example.com  ",
            },
        )

        # Create Form
        form = UserChangeForm(data=user_form_data)

        # Validate Form
        assert form.is_valid()

        # Assert Whitespace Is Stripped
        assert form.cleaned_data["first_name"] == "John"
        assert form.cleaned_data["last_name"] == "Doe"
        assert form.cleaned_data["username"] == "johndoe"
        assert form.cleaned_data["email"] == "john.doe@example.com"

    # Test Form With Multi-word Names
    def test_form_with_multi_word_names(self, user_form_data: dict[str, str]) -> None:
        """
        Test Form With Multi-word Names Should Fail Validation.

        Args:
            user_form_data (dict[str, str]): User Form Data.
        """

        # Update Form Data With Multi-word Names
        user_form_data.update(
            {
                "first_name": "john michael",
                "last_name": "doe smith",
            },
        )

        # Create Form
        form = UserChangeForm(data=user_form_data)

        # Assert Form Is Not Valid (Multi-word Names Are Not Allowed)
        assert not form.is_valid()
