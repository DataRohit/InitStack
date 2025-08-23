# Third Party Imports
from django.db import models

# Local Imports
from apps.common.models.timestamped_model import TimeStampedModel


# Test TimeStampedModel Class
class TestTimeStampedModel:
    """
    Test TimeStampedModel Abstract Base Model.
    """

    # Test Model Is Abstract
    def test_model_is_abstract(self) -> None:
        """
        Test That The Model Meta Marks It As Abstract.
        """

        # Assert Abstract Meta
        assert getattr(TimeStampedModel._meta, "abstract", False) is True

    # Test ID Field Definition
    def test_id_field_definition(self) -> None:
        """
        Test ID Field Type And Options.
        """

        # Get Field
        field: models.Field = TimeStampedModel._meta.get_field("id")

        # Assert Type
        assert isinstance(field, models.UUIDField)

        # Assert Options
        assert field.primary_key is True
        assert field.editable is False
        assert field.unique is True
        assert field.blank is False
        assert field.null is False
        assert field.db_index is True
        assert callable(field.default)

    # Test Created At Field Definition
    def test_created_at_field_definition(self) -> None:
        """
        Test Created At Field Type, Options, And Verbose Name.
        """

        # Get Field
        field: models.Field = TimeStampedModel._meta.get_field("created_at")

        # Assert Type
        assert isinstance(field, models.DateTimeField)

        # Assert Options
        assert getattr(field, "auto_now_add", False) is True
        assert field.blank is True
        assert field.null is False
        assert field.db_index is True

        # Assert Verbose Name
        assert str(field.verbose_name) == "Created At"

    # Test Updated At Field Definition
    def test_updated_at_field_definition(self) -> None:
        """
        Test Updated At Field Type, Options, And Verbose Name.
        """

        # Get Field
        field: models.Field = TimeStampedModel._meta.get_field("updated_at")

        # Assert Type
        assert isinstance(field, models.DateTimeField)

        # Assert Options
        assert getattr(field, "auto_now", False) is True
        assert field.blank is True
        assert field.null is False
        assert field.db_index is True

        # Assert Verbose Name
        assert str(field.verbose_name) == "Updated At"
