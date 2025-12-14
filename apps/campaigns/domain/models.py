"""
Campaign domain models.

This module contains the core entities for the campaigns domain.
"""
import uuid
from decimal import Decimal

from django.core.validators import MinValueValidator
from django.db import models

from apps.core.mixins import TimestampMixin


class CampaignStatus(models.TextChoices):
    """
    Status choices for campaigns.

    States:
        PENDING: Campaign created locally, not yet synced with Amazon
        PROCESSING: Campaign sent to Amazon, awaiting confirmation
        ACTIVE: Campaign is live on Amazon
        FAILED: Campaign sync failed
    """

    PENDING = 'PENDING', 'Pending'
    PROCESSING = 'PROCESSING', 'Processing'
    ACTIVE = 'ACTIVE', 'Active'
    FAILED = 'FAILED', 'Failed'


class Campaign(TimestampMixin):
    """
    Campaign model representing an Amazon Ads campaign.

    This model stores campaign information locally and tracks
    synchronization status with the external Amazon Ads API.
    """

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        help_text='Unique identifier for the campaign.',
    )
    name = models.CharField(
        max_length=255,
        help_text='Name of the campaign.',
    )
    budget = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        help_text='Campaign budget in USD.',
    )
    keywords = models.JSONField(
        default=list,
        help_text='List of keywords for the campaign.',
    )
    status = models.CharField(
        max_length=20,
        choices=CampaignStatus.choices,
        default=CampaignStatus.PENDING,
        db_index=True,
        help_text='Current status of the campaign.',
    )
    external_id = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        db_index=True,
        help_text='External ID from Amazon Ads API.',
    )
    error_message = models.TextField(
        null=True,
        blank=True,
        help_text='Error message if campaign sync failed.',
    )
    retry_count = models.PositiveIntegerField(
        default=0,
        help_text='Number of sync retry attempts.',
    )
    synced_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text='Timestamp of last successful sync with Amazon.',
    )

    class Meta:
        db_table = 'campaigns'
        ordering = ['-created_at']
        verbose_name = 'Campaign'
        verbose_name_plural = 'Campaigns'
        indexes = [
            models.Index(fields=['status', 'created_at']),
            models.Index(fields=['external_id']),
        ]

    def __str__(self):
        return f'{self.name} ({self.status})'

    def __repr__(self):
        return f'<Campaign(id={self.id}, name="{self.name}", status={self.status})>'

    @property
    def has_external_id(self) -> bool:
        """Check if the campaign has been synced with Amazon."""
        return bool(self.external_id)

    @property
    def is_synced(self) -> bool:
        """Check if the campaign is successfully synced and active."""
        return self.status == CampaignStatus.ACTIVE and self.has_external_id

    @property
    def can_retry(self) -> bool:
        """Check if the campaign can be retried for sync."""
        return self.status == CampaignStatus.FAILED and self.retry_count < 3

    def mark_as_processing(self, external_id: str) -> None:
        """
        Mark the campaign as processing with the external ID.

        Args:
            external_id: The ID received from Amazon Ads API.
        """
        self.external_id = external_id
        self.status = CampaignStatus.PROCESSING
        self.error_message = None
        self.save(update_fields=['external_id', 'status', 'error_message', 'updated_at'])

    def mark_as_active(self) -> None:
        """Mark the campaign as active."""
        from django.utils import timezone
        self.status = CampaignStatus.ACTIVE
        self.synced_at = timezone.now()
        self.save(update_fields=['status', 'synced_at', 'updated_at'])

    def mark_as_failed(self, error_message: str) -> None:
        """
        Mark the campaign as failed.

        Args:
            error_message: Description of the failure.
        """
        self.status = CampaignStatus.FAILED
        self.error_message = error_message
        self.retry_count += 1
        self.save(update_fields=['status', 'error_message', 'retry_count', 'updated_at'])
