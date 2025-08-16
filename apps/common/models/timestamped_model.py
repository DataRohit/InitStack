# Standard Library Imports
import uuid
from typing import ClassVar

# Third Party Imports
from django.db import models
from django.utils.translation import gettext_lazy as _


# Time Stamped Model Class
class TimeStampedModel(models.Model):
    """
    Abstract Base Model With Timestamp Fields.

    Attributes:
        id (UUIDField): Primary Key And Unique Identifier.
        created_at (DateTimeField): Timestamp When The Instance Was Created.
        updated_at (DateTimeField): Timestamp When The Instance Was Last Updated.
    """

    # UUID Field For Unique Identification And Primary Key
    id: models.UUIDField = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        unique=True,
        blank=False,
        null=False,
        db_index=True,
    )

    # Timestamp When The Instance Was Created
    created_at: models.DateTimeField = models.DateTimeField(
        verbose_name=_("Created At"),
        auto_now_add=True,
        blank=False,
        null=False,
        db_index=True,
    )

    # Timestamp When The Instance Was Last Updated
    updated_at: models.DateTimeField = models.DateTimeField(
        verbose_name=_("Updated At"),
        auto_now=True,
        blank=False,
        null=False,
        db_index=True,
    )

    # Meta Class
    class Meta:
        """
        Meta Class For TimeStampedModel Configuration.

        Attributes:
            abstract (bool): Marks This As An Abstract Model.
        """

        # Mark As Abstract Model
        abstract: ClassVar[bool] = True


# Exports
__all__: list[str] = ["TimeStampedModel"]
