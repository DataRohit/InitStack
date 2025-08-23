# Third Party Imports
import pytest
from django.contrib.auth.forms import UserChangeForm as BaseUserChangeForm

# Local Imports
from apps.users.forms.user_change_form import UserChangeForm
from apps.users.models import User

# Enable Django DB Access For All Tests In This Module
pytestmark = pytest.mark.django_db


# User Form Data Fixture
@pytest.fixture
def user_form_data() -> dict[str, str]:
    """
    Create User Form Data For Testing.

    Returns:
        dict[str, str]: Dictionary With User Form Data.
    """

    # Return Form Data
    return {
        "first_name": "John",
        "last_name": "Doe",
        "username": "johndoe",
        "email": "john.doe@example.com",
    }


# Mixed Case Form Data Fixture
@pytest.fixture
def mixed_case_form_data() -> dict[str, str]:
    """
    Create Form Data With Mixed Case For Testing.

    Returns:
        dict[str, str]: Dictionary With Mixed Case Form Data.
    """

    # Return Form Data
    return {
        "first_name": "jOhN",
        "last_name": "dOe",
        "username": "JohnDoe",
        "email": "John.Doe@Example.COM",
    }


# User Change Form Fixture
@pytest.fixture
def user_change_form(user_form_data: dict[str, str]) -> UserChangeForm:
    """
    Create User Change Form Instance For Testing.

    Args:
        user_form_data (dict[str, str]): User Form Data.

    Returns:
        UserChangeForm: User Change Form Instance.
    """

    # Create Form
    return UserChangeForm(data=user_form_data)


# User Instance Fixture
@pytest.fixture
def user_instance() -> User:
    """
    Create User Instance For Testing.

    Returns:
        User: User Instance.
    """

    # Create & Return User
    return User.objects.create_user(
        first_name="Jane",
        last_name="Smith",
        username="janesmith",
        email="jane.smith@example.com",
        password="AnotherStr0ngP@ss",
    )


# User Change Form With Instance Fixture
@pytest.fixture
def user_change_form_with_instance(user_instance: User) -> UserChangeForm:
    """
    Create User Change Form With User Instance For Testing.

    Args:
        user_instance (User): User Instance.

    Returns:
        UserChangeForm: User Change Form Instance With User Instance.
    """

    # Create Form
    return UserChangeForm(instance=user_instance)


# Test Form Initialization
def test_form_initialization(user_change_form: UserChangeForm) -> None:
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
def test_meta_class_model() -> None:
    """
    Test Meta Class Model Is Set Correctly.
    """

    # Assert Model Is User
    assert UserChangeForm.Meta.model == User


# Test Meta Class Fields
def test_meta_class_fields() -> None:
    """
    Test Meta Class Fields Are Set Correctly.
    """

    # Expected Fields
    expected_fields = ["first_name", "last_name", "username", "email"]

    # Assert Fields Are Correct
    assert UserChangeForm.Meta.fields == expected_fields


# Test Form Validation With Valid Data
def test_form_validation_with_valid_data(user_change_form: UserChangeForm) -> None:
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
def test_clean_email_method(user_change_form: UserChangeForm) -> None:
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
def test_clean_email_method_with_mixed_case(mixed_case_form_data: dict[str, str]) -> None:
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
def test_clean_username_method(user_change_form: UserChangeForm) -> None:
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
def test_clean_username_method_with_mixed_case(mixed_case_form_data: dict[str, str]) -> None:
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
def test_clean_first_name_method(user_change_form: UserChangeForm) -> None:
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
def test_clean_first_name_method_with_mixed_case(mixed_case_form_data: dict[str, str]) -> None:
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
def test_clean_last_name_method(user_change_form: UserChangeForm) -> None:
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
def test_clean_last_name_method_with_mixed_case(mixed_case_form_data: dict[str, str]) -> None:
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
def test_form_with_existing_user_instance(user_change_form_with_instance: UserChangeForm) -> None:
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
def test_form_with_whitespace_in_fields(user_form_data: dict[str, str]) -> None:
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
def test_form_with_multi_word_names(user_form_data: dict[str, str]) -> None:
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
