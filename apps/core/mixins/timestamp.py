"""
Timestamp mixin for Django models.

Provides automatic created_at and updated_at fields.
"""
from django.db import models


class TimestampMixin(models.Model):
    """
    Abstract model mixin that provides automatic timestamp fields.

    Fields:
        created_at: Automatically set when the object is created.
        updated_at: Automatically updated when the object is saved.
    """

    created_at = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
        help_text='Timestamp when the record was created.',
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text='Timestamp when the record was last updated.',
    )

    class Meta:
        abstract = True
        ordering = ['-created_at']
